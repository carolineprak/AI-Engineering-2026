"""Pytest — prove each check catches known failures with a one-line reason."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.checks import check_unauthorized_action, check_url_allowlist
from evals.load_traces import load_annotated_traces
from evals.suite import apply_output_fix, run_suite, summarize


@pytest.fixture(scope="module")
def by_id():
    return {t["trace_id"]: t for t in load_annotated_traces()}


def test_invalid_link_flags_ha006(by_id):
    result = check_url_allowlist(by_id["ha-006"])
    assert result.passed is False
    assert "bit.ly" in result.reason


def test_invalid_link_passes_clean_trace(by_id):
    result = check_url_allowlist(by_id["ha-009"])
    assert result.passed is True
    assert result.reason == ""


def test_unauthorized_action_flags_hold(by_id):
    result = check_unauthorized_action(by_id["ha-005"])
    assert result.passed is False
    assert "held" in result.reason.lower() or "confirmed" in result.reason.lower()


def test_unauthorized_action_flags_password(by_id):
    result = check_unauthorized_action(by_id["ha-008"])
    assert result.passed is False
    assert "password" in result.reason.lower()


def test_fix_clears_targeted_failures(by_id):
    """One Path A fix should clear invalid_link + unauthorized_action on known bad rows."""
    for tid in ("ha-005", "ha-006", "ha-008"):
        fixed = apply_output_fix(by_id[tid])
        assert check_url_allowlist(fixed).passed, tid
        assert check_unauthorized_action(fixed).passed, tid


def test_suite_metric_moves_after_fix():
    traces = load_annotated_traces()
    before = summarize(run_suite(traces))
    after = summarize(run_suite([apply_output_fix(t) for t in traces]))
    assert after["passed"] > before["passed"]
    assert after["by_check"]["invalid_link"]["failed"] == 0
    assert after["by_check"]["unauthorized_action"]["failed"] == 0
