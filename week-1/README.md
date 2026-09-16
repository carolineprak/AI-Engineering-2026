# Week 1 — `/ask` Demo (5 stages)

Build a typed LLM endpoint step by step. Each stage is a standalone FastAPI app you can run and compare.

## Setup

```bash
cp .env.example .env          # OPENAI_API_KEY=sk-...
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Demo stages

| Stage | File | What you learn |
|-------|------|----------------|
| 1 | `serve_stage1.py` | Bare `/ask` — string answer + `tokens_used` |
| 2 | `serve_stage2.py` | Structured output via Pydantic + `completions.parse` |
| 3 | `serve_stage3.py` | Validation guardrail + retry (`force_bad` demo knob) |
| 4 | `serve_stage4.py` | Per-request `model` override + `latency_ms` |
| 5 | `serve_stage5.py` / `main.py` | Full system + `cost_usd` readout |

Run one stage at a time (only one server on port 8000):

```bash
uvicorn serve_stage1:app --host 127.0.0.1 --port 8000 --reload
# or the full system:
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Streamlit demo runner

Interactive UI for all five stages:

```bash
streamlit run demo_page.py
```

Open http://localhost:8501. Set **API base URL** to `http://127.0.0.1:8000` and start the matching stage server in another terminal.

## Test with curl

```bash
curl -s -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG in one sentence?"}'
```

Stage 5 example (model + cost):

```bash
curl -s -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is chunking?", "model": "gpt-4o-mini"}'
```

## Smoke-test all stages

Requires `.venv` and a valid `OPENAI_API_KEY`:

```bash
python test_all_stages.py
```

## Project layout

```
week-1/
├── main.py              # Full system (stages 1–5 + Session 5 memory)
├── memory_store.py      # SQLite durable memory + write gate
├── memory_ui.py         # Streamlit cross-session recall demo
├── AGENTS.md            # Write-gate rules (above compaction line)
├── serve_stage1.py … serve_stage5.py
├── demo_page.py         # Streamlit test UI
├── rag_ui.py            # Ingest + ask thin client
├── test_all_stages.py   # Automated stage smoke tests
├── requirements.txt
├── .env.example
└── .gitignore
```

## Session 5 — durable memory (Path A)

Northwind remembers a few **stable preferences** across sessions (not longer chat history).

### Five memory questions

| Question | Answer |
|----------|--------|
| **What do I keep?** | `preferred_name`, `preferred_language`, `work_mode`, `role`, `last_policy_topic` only |
| **When do I write?** | Explicit `POST /memory` when the user saves a preference (write gate rejects other keys) |
| **Where does it live?** | SQLite file (`data/memory.db` locally; set `MEMORY_DB_PATH` on Render if needed) |
| **How do I get it back?** | `GET /memory/{user_id}`; `/ask` with `user_id` injects memory into the prompt |
| **When do I forget?** | `DELETE /memory/{user_id}` (all) or `?key=` (one key). No auto-decay yet |

### Prove cross-session recall

```bash
# Terminal 1 — API
uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2 — UI
streamlit run memory_ui.py
```

1. Save `preferred_name=Caroline` for a `user_id`.
2. Click **New session** (clears local UI only).
3. **Load memory** — the preference returns without retyping.
4. Optional: **Ask with user_id** and confirm `memory_used` in the response.

### API quick check

```bash
curl -s -X POST http://127.0.0.1:8000/memory \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-1","key":"preferred_name","value":"Caroline"}'

curl -s http://127.0.0.1:8000/memory/demo-1
```
