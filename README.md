# AI Engineering 2026

Caroline Prak’s public fork of the AI Engineering Bootcamp work — cleaned into flat week folders.

**Live demo:** ask me for a demo link  
**Repo:** https://github.com/carolineprak/AI-Engineering-2026  

Private product work (Rainflowers, Understories) lives in separate private repos — not here.

## Layout

```text
AI-Engineering-2026/
├── week-1/   # FastAPI + RAG + durable memory (Render root)
├── week-2/   # RAG / vector DB lab
├── week-3/   # ADK Northwind agent + Streamlit
├── week-4/   # TRACE evals (Harmony)
├── week-5/   # Memory note → implemented in week-1
└── README.md
```

| Week | What | Start here |
|------|------|------------|
| 1 | Typed `/ask`, ingest, Qdrant RAG, SQLite memory | `week-1/README.md` |
| 2 | RAG / vector databases notebook lab | `week-2/` |
| 3 | Google ADK agent + `search_docs` + Streamlit | `week-3/` |
| 4 | TRACE taxonomy, checks, Streamlit suite | `week-4/README.md` |
| 5 | Durable memory Path A | `week-5/README.md` (code in `week-1/`) |

## Quick start (Week 1 API)

```bash
cd week-1
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add keys
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

- Health: http://127.0.0.1:8000/health → `{"status":"ok"}`
- Docs: http://127.0.0.1:8000/docs

## Render

Deploy root should be **`week-1`** (was previously `ai-engineering-bootcamp-v2/week-1`).  
Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`  
Health check path: `/health`

## Notes

- Secrets stay in `.env` (gitignored). Never commit keys.
- This fork is independent of the course upstream kit; no expectation to PR cleanup upstream.
