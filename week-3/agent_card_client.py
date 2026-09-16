"""
A2A client for the Triage Agent (deep-dive client sketch).

Maven's sample uses a2a-sdk 0.3 (`A2AClient.get_client_from_agent_card_url`).
This repo has a2a-sdk 1.1.x — same idea via ClientFactory.create_from_url.

Prereq: triage server running
  uvicorn agent_card:app --port 9000

Run:
  python agent_card_client.py
  python agent_card_client.py "Triage this ticket: invoice double-charged"
"""

from __future__ import annotations

import asyncio
import sys
import uuid

import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.helpers import get_message_text, new_text_message
from a2a.types import a2a_pb2

DEFAULT_TICKET = (
    "Triage this ticket: customer can't log in after password reset"
)
AGENT_CARD_URL = "http://localhost:9000"


async def ask_triage_agent(ticket_text: str) -> str:
    """Resolve the Agent Card at :9000 and send one triage message."""
    http_client = httpx.AsyncClient(timeout=30.0)
    factory = ClientFactory(ClientConfig(httpx_client=http_client))
    client = await factory.create_from_url(AGENT_CARD_URL)
    try:
        message = new_text_message(ticket_text, role=a2a_pb2.ROLE_USER)
        message.message_id = str(uuid.uuid4())
        request = a2a_pb2.SendMessageRequest(message=message)

        parts: list[str] = []
        async for event in client.send_message(request):
            if event.HasField("message"):
                text = get_message_text(event.message)
                if text:
                    parts.append(text)
        return "\n".join(parts) if parts else "(no text response)"
    finally:
        await client.close()
        await http_client.aclose()


async def _main() -> None:
    ticket = " ".join(sys.argv[1:]).strip() or DEFAULT_TICKET
    print(f"→ {AGENT_CARD_URL}")
    print(f"ticket: {ticket}\n")
    print(await ask_triage_agent(ticket))


if __name__ == "__main__":
    asyncio.run(_main())
