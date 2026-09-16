"""Streamlit UI — run TRACE Path A checks and show pass/fail counts."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.load_traces import load_annotated_traces
from evals.suite import apply_output_fix, run_suite, summarize

st.set_page_config(page_title="Week 4 TRACE Evals", layout="wide")
st.title("Week 4 — TRACE eval suite")
st.caption("Harmony Apartments SMS bot · binary code checks · Path A")

traces = load_annotated_traces()
st.write(f"Loaded **{len(traces)}** annotated traces from the Harmony pack.")

col_a, col_b = st.columns(2)
with col_a:
    run_baseline = st.button("Run baseline suite", type="primary", use_container_width=True)
with col_b:
    run_fixed = st.button("Run after fix", use_container_width=True)

if "baseline" not in st.session_state and run_baseline:
    st.session_state.baseline = summarize(run_suite(traces))
if run_baseline:
    st.session_state.baseline = summarize(run_suite(traces))

if run_fixed:
    fixed = [apply_output_fix(t) for t in traces]
    st.session_state.after = summarize(run_suite(fixed))
    st.session_state.baseline = st.session_state.get("baseline") or summarize(run_suite(traces))


def _render_summary(title: str, summary: dict) -> None:
    st.subheader(title)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Checks run", summary["total_checks"])
    c2.metric("Passed", summary["passed"])
    c3.metric("Failed", summary["failed"])
    c4.metric("Pass rate", f"{summary['pass_rate']:.0%}")

    for check_id, stats in summary["by_check"].items():
        with st.expander(
            f"{check_id}: {stats['passed']}/{stats['total']} passed "
            f"({stats['pass_rate']:.0%})",
            expanded=bool(stats["failures"]),
        ):
            if not stats["failures"]:
                st.success("All traces passed this check.")
            else:
                for fail in stats["failures"]:
                    st.error(f"**{fail['trace_id']}** — {fail['reason']}")


if "baseline" in st.session_state:
    _render_summary("Baseline (raw assistant_output)", st.session_state.baseline)

if "after" in st.session_state:
    _render_summary("After fix (strip bad URLs / unauthorized actions)", st.session_state.after)
    if "baseline" in st.session_state:
        delta = st.session_state.after["passed"] - st.session_state.baseline["passed"]
        st.info(
            f"Metric move: **{delta:+d}** more passing check-results "
            f"({st.session_state.baseline['pass_rate']:.0%} → "
            f"{st.session_state.after['pass_rate']:.0%})."
        )

st.divider()
st.markdown(
    """
**Checks**
- `invalid_link` — URLs must be on the KB allowlist  
- `unauthorized_action` — no hold/book/confirm or password leaks  

**Taxonomy:** see `FAILURE_TAXONOMY.md`  
**CLI:** `python -m evals.suite` from `week-4/` · `pytest tests/`
"""
)
