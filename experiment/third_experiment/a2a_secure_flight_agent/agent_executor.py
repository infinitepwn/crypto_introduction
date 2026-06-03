from __future__ import annotations

import json
from typing import override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import TaskArtifactUpdateEvent, TaskState, TaskStatus, TaskStatusUpdateEvent
from a2a.utils import new_text_artifact

from security import SECURE_ENVELOPE_URI, SECURE_HANDSHAKE_URI, FlightSecurityContext


class SecureFlightAgentExecutor(AgentExecutor):
    def __init__(self, security: FlightSecurityContext) -> None:
        self.security = security

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        if not context.message:
            raise Exception("No A2A message provided")

        metadata = context.message.metadata or {}
        try:
            if SECURE_HANDSHAKE_URI in metadata:
                result = self.security.accept_handshake(metadata[SECURE_HANDSHAKE_URI])
            elif SECURE_ENVELOPE_URI in metadata:
                result = self.security.process_secure_envelope(metadata[SECURE_ENVELOPE_URI])
            else:
                raise ValueError("missing secure handshake or secure envelope metadata")

            artifact_text = json.dumps(result, ensure_ascii=False, sort_keys=True)
            final_state = TaskState.completed
        except Exception as exc:
            artifact_text = json.dumps(
                {"error": str(exc) or exc.__class__.__name__},
                ensure_ascii=False,
                sort_keys=True,
            )
            final_state = TaskState.failed

        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                context_id=context.context_id,  # type: ignore[arg-type]
                task_id=context.task_id,  # type: ignore[arg-type]
                artifact=new_text_artifact(name="secure_flight_result", text=artifact_text),
            )
        )
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                context_id=context.context_id,  # type: ignore[arg-type]
                task_id=context.task_id,  # type: ignore[arg-type]
                status=TaskStatus(state=final_state),
                final=True,
            )
        )

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")
