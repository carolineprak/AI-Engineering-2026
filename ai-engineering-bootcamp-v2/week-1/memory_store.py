"""Durable user memory for Session 5 Path A (SQLite).

Write gate: only allowlisted preference/project keys are persisted.
Survives process restart (same machine / same disk volume).
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Stable facts worth remembering across Northwind sessions.
ALLOWED_KEYS = frozenset(
    {
        "preferred_name",
        "preferred_language",
        "work_mode",  # e.g. remote / hybrid / onsite
        "last_policy_topic",
        "role",  # e.g. engineer / manager
    }
)

_DEFAULT_DB = Path(__file__).resolve().parent / "data" / "memory.db"


def db_path() -> Path:
    override = (os.getenv("MEMORY_DB_PATH") or "").strip()
    return Path(override) if override else _DEFAULT_DB


def _connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            user_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (user_id, key)
        )
        """
    )
    conn.commit()
    return conn


def list_memory(user_id: str) -> dict[str, str]:
    uid = (user_id or "").strip()
    if not uid:
        return {}
    with _connect() as conn:
        rows = conn.execute(
            "SELECT key, value FROM memories WHERE user_id = ? ORDER BY key",
            (uid,),
        ).fetchall()
    return {str(r["key"]): str(r["value"]) for r in rows}


def get_memory(user_id: str, key: str) -> str | None:
    uid = (user_id or "").strip()
    k = (key or "").strip()
    if not uid or not k:
        return None
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM memories WHERE user_id = ? AND key = ?",
            (uid, k),
        ).fetchone()
    return None if row is None else str(row["value"])


def upsert_memory(user_id: str, key: str, value: str) -> dict:
    """Persist one fact if it passes the write gate. Raises ValueError on reject."""
    uid = (user_id or "").strip()
    k = (key or "").strip()
    v = (value or "").strip()
    if not uid:
        raise ValueError("user_id must not be empty")
    if k not in ALLOWED_KEYS:
        allowed = ", ".join(sorted(ALLOWED_KEYS))
        raise ValueError(f"Write gate rejected key '{k}'. Allowed: {allowed}")
    if not v:
        raise ValueError("value must not be empty")
    if len(v) > 500:
        raise ValueError("value must be at most 500 characters")

    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO memories (user_id, key, value, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (uid, k, v, now),
        )
        conn.commit()
    return {"user_id": uid, "key": k, "value": v, "updated_at": now, "status": "saved"}


def delete_memory(user_id: str, key: str | None = None) -> dict:
    """Forget one key, or all keys for a user if key is None."""
    uid = (user_id or "").strip()
    if not uid:
        raise ValueError("user_id must not be empty")
    with _connect() as conn:
        if key is None or not str(key).strip():
            conn.execute("DELETE FROM memories WHERE user_id = ?", (uid,))
            deleted = "all"
        else:
            k = str(key).strip()
            conn.execute(
                "DELETE FROM memories WHERE user_id = ? AND key = ?",
                (uid, k),
            )
            deleted = k
        conn.commit()
    return {"user_id": uid, "deleted": deleted, "status": "ok"}


def format_memory_block(memories: dict[str, str]) -> str:
    if not memories:
        return ""
    lines = [f"- {k}: {v}" for k, v in sorted(memories.items())]
    return "Known user memory (durable; do not invent beyond this):\n" + "\n".join(lines)
