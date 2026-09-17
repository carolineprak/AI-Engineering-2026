# Week 5 — durable memory (Path A)

Session 5 memory is implemented **on the Week 1 Northwind API**, not as a separate app.

## Where the code lives

| Piece | Path |
|-------|------|
| SQLite store + write gate | `../week-1/memory_store.py` |
| API: `POST/GET/DELETE /memory`, `/ask` + `user_id` | `../week-1/main.py` |
| Streamlit write → new session → recall | `../week-1/memory_ui.py` |
| Rules above the compaction line | `../week-1/AGENTS.md` |
| Five memory questions | `../week-1/README.md` (Session 5 section) |

## Prove it

```bash
cd ../week-1
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000
# other terminal:
streamlit run memory_ui.py
```

Live demo: ask me for a demo link (`/memory`, `/docs`, `/health`).
