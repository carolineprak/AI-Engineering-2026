# Week 4 — TRACE Path A (Harmony Apartments)

## Layout
- `harmony-apartments/` — sample pack + your open-coded CSV
- `FAILURE_TAXONOMY.md` — categories from your notes
- `evals/` — loaders, checks, suite + one output fix
- `tests/test_assertions.py` — pytest (binary + one-line fail reason)
- `eval_ui.py` — Streamlit pass/fail UI

## Setup
```bash
cd ai-engineering-bootcamp-v2/week-4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
# CLI suite + before/after fix
python -m evals.suite

# Pytest
pytest -q

# Streamlit
streamlit run eval_ui.py
```

Do not open `harmony-apartments-answer-key.jsonl` until after open-coding (already done).
