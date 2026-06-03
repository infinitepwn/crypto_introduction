from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


SECURE_PASSPORT_URI = "https://example.edu/a2a/extensions/secure-flight-passport/v1"
SECURE_HANDSHAKE_URI = "https://example.edu/a2a/extensions/secure-handshake/v1"
SECURE_ENVELOPE_URI = "https://example.edu/a2a/extensions/secure-envelope/v1"
ALLOWED_SKEW_SECONDS = 30


def b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(obj: Any) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


@dataclass
class AgentIdentity:
    agent_id: str
    permissions: list[str]
    signing_private: ed25519.Ed25519PrivateKey
    certificate: dict[str, Any]


class OfflineCA:
    def __init__(self, private_key: ed25519.Ed25519PrivateKey | None = None) -> None:
        self.private_key = private_key or ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def issue_agent(self, agent_id: str, permissions: list[str]) -> AgentIdentity:
        signing_private = ed25519.Ed25519PrivateKey.generate()
        signing_public = signing_private.public_key()
        public_key = signing_public.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        cert_body = {
            "agent_id": agent_id,
            "public_key": b64e(public_key),
            "permissions": permissions,
            "not_before": "2026-06-01T00:00:00+00:00",
            "not_after": "2026-12-31T23:59:59+00:00",
            "issuer": "TrustedOfflineCA",
        }
        certificate = {
            "body": cert_body,
            "ca_signature": b64e(self.private_key.sign(canon(cert_body))),
        }
        return AgentIdentity(agent_id, permissions, signing_private, certificate)

    def verify_certificate(self, certificate: dict[str, Any]) -> ed25519.Ed25519PublicKey:
        body = certificate["body"]
        self.public_key.verify(b64d(certificate["ca_signature"]), canon(body))
        current = datetime.now(timezone.utc)
        if current < datetime.fromisoformat(body["not_before"]):
            raise ValueError("certificate is not valid yet")
        if current > datetime.fromisoformat(body["not_after"]):
            raise ValueError("certificate is expired")
        return ed25519.Ed25519PublicKey.from_public_bytes(b64d(body["public_key"]))


def sign(identity: AgentIdentity, payload: Any) -> str:
    return b64e(identity.signing_private.sign(canon(payload)))


def verify_signature(public_key: ed25519.Ed25519PublicKey, signature: str, payload: Any) -> None:
    public_key.verify(b64d(signature), canon(payload))


def make_demo_identities() -> tuple[OfflineCA, AgentIdentity, AgentIdentity]:
    ca = OfflineCA()
    alice = ca.issue_agent("agent:alice", ["delegate", "audit"])
    flight = ca.issue_agent("agent:flight", ["flight.search", "flight.book"])
    return ca, alice, flight


def _private_to_b64(private_key: ed25519.Ed25519PrivateKey) -> str:
    return b64e(
        private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )


def _private_from_b64(value: str) -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.from_private_bytes(b64d(value))


def load_or_create_demo_identities(path: str = "trust_store.json") -> tuple[OfflineCA, AgentIdentity, AgentIdentity]:
    store_path = Path(path)
    if store_path.exists():
        data = json.loads(store_path.read_text())
        ca = OfflineCA(_private_from_b64(data["ca_private_key"]))
        alice = AgentIdentity(
            "agent:alice",
            ["delegate", "audit"],
            _private_from_b64(data["alice_private_key"]),
            data["alice_certificate"],
        )
        flight = AgentIdentity(
            "agent:flight",
            ["flight.search", "flight.book"],
            _private_from_b64(data["flight_private_key"]),
            data["flight_certificate"],
        )
        return ca, alice, flight

    ca, alice, flight = make_demo_identities()
    data = {
        "ca_private_key": _private_to_b64(ca.private_key),
        "alice_private_key": _private_to_b64(alice.signing_private),
        "alice_certificate": alice.certificate,
        "flight_private_key": _private_to_b64(flight.signing_private),
        "flight_certificate": flight.certificate,
    }
    store_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return ca, alice, flight


class ReplayWindow:
    def __init__(self) -> None:
        self.seen: set[tuple[str, int]] = set()

    def accept(self, session_id: str, seq: int, timestamp: str) -> None:
        message_time = datetime.fromisoformat(timestamp)
        if abs((datetime.now(timezone.utc) - message_time).total_seconds()) > ALLOWED_SKEW_SECONDS:
            raise ValueError("replay rejected: timestamp outside allowed window")
        key = (session_id, seq)
        if key in self.seen:
            raise ValueError("replay rejected: duplicated session sequence")
        self.seen.add(key)


class FlightSecurityContext:
    def __init__(self, ca: OfflineCA, identity: AgentIdentity) -> None:
        self.ca = ca
        self.identity = identity
        self.replay_window = ReplayWindow()
        self.session_keys: dict[str, dict[str, bytes]] = {}

    def accept_handshake(self, hello: dict[str, Any]) -> dict[str, Any]:
        alice_public = self.ca.verify_certificate(hello["certificate"])
        verify_signature(alice_public, hello["signature"], hello["body"])
        if hello["body"]["agent_id"] != hello["certificate"]["body"]["agent_id"]:
            raise ValueError("identity binding mismatch")

        flight_x = x25519.X25519PrivateKey.generate()
        alice_x_pub = x25519.X25519PublicKey.from_public_bytes(b64d(hello["body"]["x25519_public"]))
        shared_secret = flight_x.exchange(alice_x_pub)
        session_id = hello["body"]["session_id"]
        key_material = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=session_id.encode(),
            info=b"alice-flightagent-a2a-secure-session",
        ).derive(shared_secret)
        self.session_keys[session_id] = {"aes": key_material[:32], "hmac": key_material[32:]}

        body = {
            "session_id": session_id,
            "agent_id": self.identity.agent_id,
            "x25519_public": b64e(
                flight_x.public_key().public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            ),
            "timestamp": now_iso(),
        }
        return {"body": body, "certificate": self.identity.certificate, "signature": sign(self.identity, body)}

    def process_secure_envelope(self, envelope: dict[str, Any]) -> dict[str, Any]:
        session_id = envelope["session_id"]
        if session_id not in self.session_keys:
            raise ValueError("unknown secure session")
        keys = self.session_keys[session_id]
        self.replay_window.accept(session_id, envelope["seq"], envelope["timestamp"])
        mac_input = canon({k: v for k, v in envelope.items() if k != "hmac"})
        expected_mac = b64e(hmac.new(keys["hmac"], mac_input, hashlib.sha256).digest())
        if not hmac.compare_digest(envelope["hmac"], expected_mac):
            raise ValueError("message rejected: HMAC integrity check failed")

        plaintext = AESGCM(keys["aes"]).decrypt(
            b64d(envelope["nonce"]),
            b64d(envelope["ciphertext"]),
            canon(envelope["aad"]),
        )
        request = json.loads(plaintext)
        passport = request["metadata"][SECURE_PASSPORT_URI]
        auth = passport["state"]["authorization"]

        alice_public = self.ca.verify_certificate(passport["certificate"])
        verify_signature(alice_public, passport["signature"], auth)
        if auth["delegatee_agent_id"] != self.identity.agent_id:
            raise ValueError("authorization rejected: wrong delegatee")
        if auth["session_id"] != session_id or auth["nonce_used"]:
            raise ValueError("authorization rejected: invalid session or reused token")
        if auth["budget_cny"] > 10000:
            raise ValueError("authorization rejected: budget exceeds user limit")
        if not {"flight.search", "flight.book"}.issubset(auth["permissions"]):
            raise ValueError("authorization rejected: missing flight permission")

        order = {
            "order_id": "ORD-" + secrets.token_hex(4).upper(),
            "route": "Qingdao-New York round trip",
            "depart_date": "2026-06-08",
            "return_date": "2026-06-16",
            "passengers": 1,
            "price_cny": 9288,
            "currency": "CNY",
        }
        if order["price_cny"] > auth["budget_cny"]:
            raise ValueError("booking rejected: price exceeds authorization")

        receipt_body = {
            "session_id": session_id,
            "executed_at": now_iso(),
            "order": order,
            "actual_spend_cny": order["price_cny"],
            "authorization_digest": sha256_text(auth),
            "executor_agent_id": self.identity.agent_id,
        }
        return {
            "type": "signed_audit_receipt",
            "body": receipt_body,
            "signature": sign(self.identity, receipt_body),
            "certificate": self.identity.certificate,
        }


class AliceSecurityContext:
    def __init__(self, ca: OfflineCA, identity: AgentIdentity) -> None:
        self.ca = ca
        self.identity = identity
        self.pending_x25519: dict[str, x25519.X25519PrivateKey] = {}
        self.session_keys: dict[str, dict[str, bytes]] = {}

    def make_handshake_metadata(self) -> dict[str, Any]:
        session_id = "sess-" + uuid.uuid4().hex
        alice_x = x25519.X25519PrivateKey.generate()
        self.pending_x25519[session_id] = alice_x
        body = {
            "session_id": session_id,
            "agent_id": self.identity.agent_id,
            "x25519_public": b64e(
                alice_x.public_key().public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            ),
            "timestamp": now_iso(),
        }
        return {
            SECURE_HANDSHAKE_URI: {
                "body": body,
                "certificate": self.identity.certificate,
                "signature": sign(self.identity, body),
            }
        }

    def accept_server_hello(self, reply: dict[str, Any]) -> str:
        flight_public = self.ca.verify_certificate(reply["certificate"])
        verify_signature(flight_public, reply["signature"], reply["body"])
        session_id = reply["body"]["session_id"]
        alice_x = self.pending_x25519.pop(session_id)
        flight_x_pub = x25519.X25519PublicKey.from_public_bytes(b64d(reply["body"]["x25519_public"]))
        shared_secret = alice_x.exchange(flight_x_pub)
        key_material = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=session_id.encode(),
            info=b"alice-flightagent-a2a-secure-session",
        ).derive(shared_secret)
        self.session_keys[session_id] = {"aes": key_material[:32], "hmac": key_material[32:]}
        return session_id

    def make_booking_envelope(
        self,
        session_id: str,
        seq: int = 1,
        *,
        sign_identity: AgentIdentity | None = None,
        certificate: dict[str, Any] | None = None,
        tamper_authorization_after_sign: Any | None = None,
        tamper_envelope_after_hmac: Any | None = None,
    ) -> dict[str, Any]:
        auth = {
            "issuer_agent_id": self.identity.agent_id,
            "delegatee_agent_id": "agent:flight",
            "session_id": session_id,
            "budget_cny": 10000,
            "permissions": ["flight.search", "flight.book"],
            "valid_from": now_iso(),
            "valid_until": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
            "nonce": secrets.token_hex(16),
            "nonce_used": False,
            "itinerary": {
                "from": "Qingdao",
                "to": "New York",
                "depart_date": "2026-06-08",
                "return_date": "2026-06-16",
                "passengers": 1,
            },
        }
        signer = sign_identity or self.identity
        passport_certificate = certificate or self.identity.certificate
        passport_signature = sign(signer, auth)
        if tamper_authorization_after_sign:
            tamper_authorization_after_sign(auth)
        request = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": "预订青岛—纽约往返机票，总预算不超过10000元"}],
                }
            },
            "metadata": {
                SECURE_PASSPORT_URI: {
                    "clientId": self.identity.agent_id,
                    "sessionId": session_id,
                    "state": {"authorization": auth},
                    "certificate": passport_certificate,
                    "signature": passport_signature,
                }
            },
        }
        keys = self.session_keys[session_id]
        timestamp = now_iso()
        aad = {"session_id": session_id, "seq": seq, "timestamp": timestamp, "type": "booking_request"}
        nonce = secrets.token_bytes(12)
        ciphertext = AESGCM(keys["aes"]).encrypt(nonce, canon(request), canon(aad))
        envelope = {
            "session_id": session_id,
            "seq": seq,
            "timestamp": timestamp,
            "aad": aad,
            "nonce": b64e(nonce),
            "ciphertext": b64e(ciphertext),
        }
        envelope["hmac"] = b64e(hmac.new(keys["hmac"], canon(envelope), hashlib.sha256).digest())
        if tamper_envelope_after_hmac:
            tamper_envelope_after_hmac(envelope)
        return {SECURE_ENVELOPE_URI: envelope}
