from __future__ import annotations

import asyncio
import json

import httpx
from a2a.client import A2ACardResolver, Client, ClientConfig, ClientFactory, create_text_message_object
from a2a.types import TransportProtocol
from a2a.utils.message import get_message_text

from security import AliceSecurityContext, load_or_create_demo_identities


async def send_once(client: Client, content: str, metadata: dict) -> dict:
    message = create_text_message_object(content=content)
    message.metadata = metadata
    last_text = "{}"
    async for response in client.send_message(message):
        task, _ = response
        if task.artifacts:
            last_text = get_message_text(task.artifacts[-1])
    return json.loads(last_text)


async def main() -> None:
    ca, alice_identity, _flight_identity = load_or_create_demo_identities()
    alice = AliceSecurityContext(ca, alice_identity)

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url="http://localhost:10001")
        agent_card = await resolver.get_agent_card()
        config = ClientConfig(
            httpx_client=httpx_client,
            supported_transports=[TransportProtocol.jsonrpc, TransportProtocol.http_json],
            streaming=agent_card.capabilities.streaming,
        )
        client = ClientFactory(config).create(agent_card)

        server_hello = await send_once(client, "secure handshake", alice.make_handshake_metadata())
        session_id = alice.accept_server_hello(server_hello)
        receipt = await send_once(client, "secure booking request", alice.make_booking_envelope(session_id))
        print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
