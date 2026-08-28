"""Load Harmony traces from CSV (comma or semicolon) or JSONL."""

from __future__ import annotations

import csv
import json
from pathlib import Path

PACK_DIR = Path(__file__).resolve().parent.parent / "harmony-apartments"
DEFAULT_CSV = PACK_DIR / "harmony-apartments-traces.csv"
DEFAULT_JSONL = PACK_DIR / "harmony-apartments-traces.jsonl"

TRACE_FIELDS = (
    "trace_id",
    "channel",
    "user_input",
    "retrieved_context",
    "tool_calls_json",
    "assistant_output",
    "your_open_coding_notes",
    "your_pass_fail",
    "your_failure_label",
)


def _delimiter_for(path: Path) -> str:
    head = path.read_text(encoding="utf-8-sig").splitlines()[0]
    return ";" if head.count(";") > head.count(",") else ","


def load_traces_csv(path: Path | None = None) -> list[dict]:
    csv_path = path or DEFAULT_CSV
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=_delimiter_for(csv_path)))
    return [r for r in rows if (r.get("trace_id") or "").startswith("ha-")]


def load_traces_jsonl(path: Path | None = None) -> list[dict]:
    jsonl_path = path or DEFAULT_JSONL
    traces: list[dict] = []
    with jsonl_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            traces.append(json.loads(line))
    return traces


def load_annotated_traces() -> list[dict]:
    """Prefer annotated CSV; fall back to pack JSONL."""
    if DEFAULT_CSV.exists():
        return load_traces_csv()
    return load_traces_jsonl()
