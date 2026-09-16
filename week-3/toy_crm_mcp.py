"""Toy CRM MCP server (stdio) — Session 3 MCP stretch / lab.

Run:
  python toy_crm_mcp.py

Or point an MCP client / Cursor at this file with transport=stdio.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("toy-crm")

# In-memory "database" - swap for a real one later
TICKETS = {
    "T-101": {"customer": "Northwind Robotics", "status": "open", "owner": "aki"},
    "T-102": {"customer": "Harmony Apartments", "status": "closed", "owner": "manu"},
}


@mcp.tool()
def list_open_tickets() -> list[dict]:
    """Return every ticket whose status is 'open'. Use this before answering
    any question about current workload or backlog."""
    return [{"id": k, **v} for k, v in TICKETS.items() if v["status"] == "open"]


@mcp.tool()
def close_ticket(ticket_id: str, resolution: str) -> dict:
    """Mark a ticket closed with a one-line resolution note.
    Fails if the ticket_id does not exist - check with list_open_tickets first."""
    if ticket_id not in TICKETS:
        raise ValueError(f"No such ticket: {ticket_id}")
    TICKETS[ticket_id]["status"] = "closed"
    TICKETS[ticket_id]["resolution"] = resolution
    return TICKETS[ticket_id]


if __name__ == "__main__":
    mcp.run(transport="stdio")
