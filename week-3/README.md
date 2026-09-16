# Week 3 — ADK Northwind agent

Google ADK multi-agent labs plus the **Northwind Path A** agent that calls the Week 1 RAG API.

## Path A (graded work)

| File | Role |
|------|------|
| `northwind_rag_agent.py` | ADK agent + `search_docs` tool |
| `northwind_streamlit.py` | Think → Act → Observe UI |

```bash
cd week-3
source .venv/bin/activate   # Python 3.12
# RAG_API_URL=https://ai-internship-bnrf.onrender.com
python northwind_rag_agent.py
streamlit run northwind_streamlit.py
```

Course demos (`demo1_routing.py`, MCP, A2A card) are optional stretch.

See also: toy CRM MCP (`toy_crm_mcp.py`) and `cursor-mcp.toy-crm.example.json`.
