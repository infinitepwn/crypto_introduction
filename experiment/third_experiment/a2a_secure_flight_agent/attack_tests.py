from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from a2a.client import A2ACardResolver, Client, ClientConfig, ClientFactory, create_text_message_object
from a2a.types import TransportProtocol
from a2a.utils.message import get_message_text

from security import AliceSecurityContext, OfflineCA, b64d, b64e, load_or_create_demo_identities


async def send_once(client: Client, content: str, metadata: dict[str, Any]) -> dict[str, Any]:
    message = create_text_message_object(content=content)
    message.metadata = metadata
    last_text = "{}"
    async for response in client.send_message(message):
        task, _ = response
        if task.artifacts:
            last_text = get_message_text(task.artifacts[-1])
    return json.loads(last_text)


async def new_client() -> tuple[Client, AliceSecurityContext, httpx.AsyncClient]:
    ca, alice_identity, _flight_identity = load_or_create_demo_identities()
    alice = AliceSecurityContext(ca, alice_identity)
    httpx_client = httpx.AsyncClient()
    resolver = A2ACardResolver(httpx_client=httpx_client, base_url="http://localhost:10001")
    agent_card = await resolver.get_agent_card()
    config = ClientConfig(
        httpx_client=httpx_client,
        supported_transports=[TransportProtocol.jsonrpc, TransportProtocol.http_json],
        streaming=agent_card.capabilities.streaming,
    )
    return ClientFactory(config).create(agent_card), alice, httpx_client


async def secure_session(client: Client, alice: AliceSecurityContext) -> str:
    server_hello = await send_once(client, "secure handshake", alice.make_handshake_metadata())
    return alice.accept_server_hello(server_hello)


def passed_if_error(name: str, response: dict[str, Any], expected: str) -> dict[str, str]:
    error = response.get("error", "")
    ok = expected in error
    return {
        "test": name,
        "result": "PASS" if ok else "FAIL",
        "reason": error or json.dumps(response, ensure_ascii=False),
    }


async def test_replay_attack(client: Client, alice: AliceSecurityContext) -> dict[str, str]:
    session_id = await secure_session(client, alice)
    metadata = alice.make_booking_envelope(session_id, seq=1)
    first = await send_once(client, "normal request before replay", metadata)
    second = await send_once(client, "replayed request", metadata)
    result = passed_if_error("replay attack", second, "duplicated session sequence")
    if first.get("type") != "signed_audit_receipt":
        result["result"] = "FAIL"
        result["reason"] = "baseline request failed before replay"
    return result


async def test_authorization_escalation(client: Client, alice: AliceSecurityContext) -> dict[str, str]:
    session_id = await secure_session(client, alice)
    metadata = alice.make_booking_envelope(
        session_id,
        seq=1,
        tamper_authorization_after_sign=lambda auth: auth.update({"budget_cny": 50000}),
    )
    response = await send_once(client, "tampered authorization budget", metadata)
    return passed_if_error("authorization escalation", response, "InvalidSignature")


async def test_message_tampering(client: Client, alice: AliceSecurityContext) -> dict[str, str]:
    session_id = await secure_session(client, alice)

    def tamper_ciphertext(envelope: dict[str, Any]) -> None:
        raw = bytearray(b64d(envelope["ciphertext"]))
        raw[-1] ^= 1
        envelope["ciphertext"] = b64e(bytes(raw))

    metadata = alice.make_booking_envelope(
        session_id,
        seq=1,
        tamper_envelope_after_hmac=tamper_ciphertext,
    )
    response = await send_once(client, "tampered ciphertext", metadata)
    return passed_if_error("message tampering", response, "HMAC integrity check failed")


async def test_forged_identity(client: Client, alice: AliceSecurityContext) -> dict[str, str]:
    session_id = await secure_session(client, alice)
    rogue_ca = OfflineCA()
    forged_alice = rogue_ca.issue_agent("agent:alice", ["delegate", "audit"])
    metadata = alice.make_booking_envelope(
        session_id,
        seq=1,
        sign_identity=forged_alice,
        certificate=forged_alice.certificate,
    )
    response = await send_once(client, "forged identity", metadata)
    return passed_if_error("forged identity", response, "InvalidSignature")


async def main() -> None:
    client, alice, httpx_client = await new_client()
    try:
        tests = [
            test_replay_attack,
            test_authorization_escalation,
            test_message_tampering,
            test_forged_identity,
        ]
        for test in tests:
            result = await test(client, alice)
            print(f"- {result['test']}: {result['result']} ({result['reason']})")
    finally:
        await httpx_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
