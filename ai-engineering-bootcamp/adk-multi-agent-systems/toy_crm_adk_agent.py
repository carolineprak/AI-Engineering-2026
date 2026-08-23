"""
ADK agent + local toy-crm MCP server (Session 3 MCP stretch).

Launches toy_crm_mcp.py over stdio via ADK McpToolset — same pattern as Demo 2,
but no Supabase required.

Run:
  cd ai-engineering-bootcamp/adk-multi-agent-systems
  source .venv/bin/activate
  python toy_crm_adk_agent.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.genai import types
from mcp.client.stdio import StdioServerParameters

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
HERE = Path(__file__).resolve().parent
PYTHON = str(HERE / ".venv" / "bin" / "python")
SERVER = str(HERE / "toy_crm_mcp.py")

if not Path(PYTHON).exists():
    sys.exit(f"Missing venv python at {PYTHON}. Create .venv and pip install -e . first.")
if not Path(SERVER).exists():
    sys.exit(f"Missing MCP server script at {SERVER}")

toy_crm_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=PYTHON,
            args=[SERVER],
        ),
        timeout=30.0,
    ),
)

crm_agent = Agent(
    name="toy_crm_agent",
    model=MODEL,
    description="Handles support-ticket workload using the toy-crm MCP tools.",
    instruction=(
        "You are a support ops assistant for a tiny CRM.\n"
        "Always call list_open_tickets before answering workload/backlog questions.\n"
        "To close a ticket, call close_ticket with ticket_id and a short resolution.\n"
        "If a ticket id is missing, say so — do not invent tickets.\n"
        "Keep answers concise and mention ticket ids you used."
    ),
    tools=[toy_crm_mcp],
)


async def ask(agent: Agent, message: str) -> str:
    service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="toy_crm", session_service=service)
    session = await service.create_session(app_name="toy_crm", user_id="user1")
    content = types.Content(role="user", parts=[types.Part(text=message)])
    async for event in runner.run_async(
        user_id="user1", session_id=session.id, new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text or "(empty)"
    return "(no response)"


async def main() -> None:
    tests = [
        ("BACKLOG", "What open tickets do we have right now?"),
        (
            "CLOSE",
            "Close ticket T-101 with resolution: Confirmed fixed after redeploy.",
        ),
        ("BACKLOG_AFTER", "List open tickets again."),
    ]
    print(f"MODEL={MODEL}")
    print(f"MCP server={SERVER}")
    for label, query in tests:
        print(f"\n--- {label} ---")
        print(f"User: {query}\n")
        print(f"Agent: {await ask(crm_agent, query)}\n")


if __name__ == "__main__":
    asyncio.run(main())
