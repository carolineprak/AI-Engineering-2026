"""
Standalone A2A Triage Agent (Agent Card demo).

Maven's sample uses a2a-sdk 0.3 (`A2AStarletteApplication`). This repo has
a2a-sdk 1.1.x, so the same card/skill/executor idea is wired with FastAPI routes.

Run: uvicorn agent_card:app --port 9000
Then open: http://localhost:9000/.well-known/agent-card.json
"""

from a2a.helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers.default_request_handler import LegacyRequestHandler
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.routes.fastapi_routes import add_a2a_routes_to_fastapi
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, a2a_pb2
from fastapi import FastAPI

SKILL = AgentSkill(
    id="triage-support-ticket",
    name="Triage a support ticket",
    description="Reads a support ticket and returns severity, owner, and next action.",
    tags=["support", "triage"],
    examples=["Triage this ticket: customer can't log in after password reset"],
)

CARD = AgentCard(
    name="Triage Agent",
    description="Specialist agent that triages inbound support tickets.",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
)
CARD.capabilities.CopyFrom(AgentCapabilities(streaming=True))
CARD.skills.append(SKILL)
CARD.supported_interfaces.append(
    a2a_pb2.AgentInterface(url="http://localhost:9000/", protocol_binding="JSONRPC")
)


class TriageExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        _ticket_text = context.get_user_input()
        # Stub triage — swap in an LLM / classifier / rules engine here.
        result = (
            "Severity: high. Owner: on-call. "
            "Reason: login is blocked for a paying customer."
        )
        await event_queue.enqueue_event(
            new_text_message(
                result,
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Cancellation not supported")


handler = LegacyRequestHandler(
    agent_executor=TriageExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=CARD,
)

app = FastAPI(title="Triage Agent")
add_a2a_routes_to_fastapi(
    app,
    agent_card_routes=create_agent_card_routes(CARD),
    jsonrpc_routes=create_jsonrpc_routes(handler, rpc_url="/"),
)

# Run with: uvicorn agent_card:app --port 9000
