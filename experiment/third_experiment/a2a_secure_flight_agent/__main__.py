from __future__ import annotations

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentExtension, AgentSkill

from agent_executor import SecureFlightAgentExecutor
from security import (
    SECURE_ENVELOPE_URI,
    SECURE_HANDSHAKE_URI,
    SECURE_PASSPORT_URI,
    FlightSecurityContext,
    load_or_create_demo_identities,
)


ca, alice_identity, flight_identity = load_or_create_demo_identities()


def build_agent_card() -> AgentCard:
    skill = AgentSkill(
        id="secure_flight_booking",
        name="Secure Flight Booking",
        description="Book flights only with signed Alice delegation and encrypted A2A envelopes.",
        tags=["flight", "booking", "secure-delegation"],
        examples=["预订 2026.06.08-2026.06.16 青岛—纽约往返机票，预算不超过10000元"],
    )
    return AgentCard(
        name="FlightAgent",
        description="A2A secure flight booking agent with CA certificate, signed delegation, anti-replay and audit receipt.",
        version="1.0.0",
        url="http://localhost:10001/",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(
            streaming=True,
            extensions=[
                AgentExtension(uri=SECURE_HANDSHAKE_URI, description="Signed X25519 handshake metadata."),
                AgentExtension(uri=SECURE_ENVELOPE_URI, description="AES-GCM/HMAC secure envelope metadata."),
                AgentExtension(uri=SECURE_PASSPORT_URI, description="Signed Alice delegation passport.", required=True),
            ],
        ),
        skills=[skill],
    )


if __name__ == "__main__":
    request_handler = DefaultRequestHandler(
        agent_executor=SecureFlightAgentExecutor(FlightSecurityContext(ca, flight_identity)),
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(agent_card=build_agent_card(), http_handler=request_handler)
    uvicorn.run(server.build(), host="0.0.0.0", port=10001)
