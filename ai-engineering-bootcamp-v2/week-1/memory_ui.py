"""Session 5 — cross-session memory demo (Streamlit).

Proves durable recall without reusing in-memory chat history:
  1) Save preference for a user_id (POST /memory)
  2) "New session" clears local widgets, then GET /memory + optional /ask

Run (from week-1):
  streamlit run memory_ui.py
"""

from __future__ import annotations

import json
import os
import uuid

import httpx
import streamlit as st

DEFAULT_API_URL = (
    os.getenv("RAG_API_URL")
    or os.getenv("API_BASE_URL")
    or "https://ai-internship-bnrf.onrender.com"
).rstrip("/")


def call_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict | str]:
    try:
        response = httpx.request(method, url, json=payload, timeout=120.0)
    except httpx.HTTPError as exc:
        return 0, f"Request failed: {exc}"
    try:
        body: dict | str = response.json()
    except ValueError:
        body = response.text
    return response.status_code, body


st.set_page_config(page_title="Northwind Memory", layout="centered")
st.title("Northwind — durable memory")
st.caption(
    "Session 5 Path A: write a preference, start a **new session**, recall without restating it."
)

with st.sidebar:
    st.header("API")
    api_url = st.text_input("Base URL", value=DEFAULT_API_URL).rstrip("/")
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"demo-{uuid.uuid4().hex[:8]}"
    user_id = st.text_input("user_id", value=st.session_state.user_id)
    st.session_state.user_id = user_id.strip() or st.session_state.user_id
    st.caption("Same user_id + new session = cross-session recall.")
    if st.button("New session (clear local UI only)"):
        for key in list(st.session_state.keys()):
            if key.startswith("mem_") or key in {"saved_note", "recalled", "ask_result"}:
                del st.session_state[key]
        st.success("Local session cleared. user_id kept — memory stays in SQLite on the API.")
        st.rerun()

tab_write, tab_recall = st.tabs(["1) Write (Session A)", "2) Recall (Session B)"])

with tab_write:
    st.subheader("POST /memory")
    st.write("Persist a stable preference (write-gated keys only).")
    key = st.selectbox(
        "key",
        options=[
            "preferred_name",
            "preferred_language",
            "work_mode",
            "role",
            "last_policy_topic",
        ],
        key="mem_key",
    )
    value = st.text_input(
        "value",
        value="Caroline",
        key="mem_value",
        help="Example: preferred_name=Caroline, work_mode=remote",
    )
    if st.button("Save preference", type="primary", key="mem_save"):
        status, body = call_json(
            "POST",
            f"{api_url}/memory",
            {
                "user_id": st.session_state.user_id,
                "key": key,
                "value": value.strip(),
            },
        )
        st.write(f"HTTP {status}")
        if status == 200 and isinstance(body, dict):
            st.session_state.saved_note = body
            st.success(f"Saved `{body.get('key')}` for `{body.get('user_id')}`")
        else:
            st.error("Write failed (check write gate / API).")
        st.code(json.dumps(body, indent=2) if not isinstance(body, str) else body)

with tab_recall:
    st.subheader("Fresh session recall")
    st.write(
        "Click **New session** in the sidebar first (optional but clearer for the Loom). "
        "Then load memory — do **not** retype the preference."
    )
    if st.button("Load memory for this user_id", type="primary", key="mem_load"):
        status, body = call_json(
            "GET",
            f"{api_url}/memory/{st.session_state.user_id}",
        )
        st.write(f"HTTP {status}")
        if status == 200 and isinstance(body, dict):
            st.session_state.recalled = body.get("memories") or {}
            memories = st.session_state.recalled
            if memories:
                st.success("Recalled durable memory (survived new UI session / API process).")
                st.json(memories)
            else:
                st.warning("No memories yet for this user_id — save one in tab 1.")
        else:
            st.error("Recall failed")
            st.code(json.dumps(body, indent=2) if not isinstance(body, str) else body)

    st.divider()
    st.subheader("Optional: /ask with memory")
    q = st.text_input(
        "Question",
        value="What is the remote work policy?",
        key="mem_ask_q",
    )
    if st.button("Ask with user_id", key="mem_ask"):
        status, body = call_json(
            "POST",
            f"{api_url}/ask",
            {
                "question": q.strip(),
                "user_id": st.session_state.user_id,
                "top_k": 5,
            },
        )
        st.write(f"HTTP {status}")
        if status == 200 and isinstance(body, dict):
            st.markdown("**memory_used**")
            st.json(body.get("memory_used") or {})
            answer = (body.get("answer") or {}).get("answer")
            st.markdown("**answer**")
            st.write(answer)
            with st.expander("Full JSON"):
                st.code(json.dumps(body, indent=2), language="json")
        else:
            st.error("Ask failed")
            st.code(json.dumps(body, indent=2) if not isinstance(body, str) else body)
