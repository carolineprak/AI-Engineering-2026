"""Run the Path A eval suite over Harmony traces."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict

from evals.checks import ALL_CHECKS, CheckResult
from evals.load_traces import load_annotated_traces


def run_suite(traces: list[dict] | None = None) -> list[CheckResult]:
    rows = traces if traces is not None else load_annotated_traces()
    results: list[CheckResult] = []
    for trace in rows:
        for check in ALL_CHECKS:
            results.append(check(trace))
    return results


def summarize(results: list[CheckResult]) -> dict:
    by_check: dict[str, dict] = {}
    grouped: dict[str, list[CheckResult]] = defaultdict(list)
    for r in results:
        grouped[r.check_id].append(r)

    for check_id, items in grouped.items():
        failed = [i for i in items if not i.passed]
        by_check[check_id] = {
            "total": len(items),
            "passed": len(items) - len(failed),
            "failed": len(failed),
            "pass_rate": round((len(items) - len(failed)) / len(items), 3) if items else 0.0,
            "failures": [
                {"trace_id": f.trace_id, "reason": f.reason} for f in failed
            ],
        }

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    return {
        "total_checks": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total, 3) if total else 0.0,
        "by_check": by_check,
        "results": [asdict(r) for r in results],
    }


def apply_output_fix(trace: dict) -> dict:
    """
    One Path A fix: strip unauthorized holds/credentials and non-allowlist URLs,
    and append a safe office handoff when we removed a bad action.
    """
    import re

    from evals.checks import UNAUTHORIZED_RE, URL_ALLOWLIST, URL_RE

    fixed = dict(trace)
    text = fixed.get("assistant_output") or ""
    original = text

    def _url_sub(match: re.Match[str]) -> str:
        url = match.group(0).rstrip(".,);]")
        trailing = match.group(0)[len(url) :]
        if url in URL_ALLOWLIST:
            return match.group(0)
        return "(link removed — ask the office)" + trailing

    text = URL_RE.sub(_url_sub, text)
    if UNAUTHORIZED_RE.search(text):
        text = UNAUTHORIZED_RE.sub("[removed]", text)
        if "office" not in text.lower():
            text = (
                text.rstrip()
                + " I can't book units or share passwords over SMS — "
                "please contact the leasing office during office hours."
            )

    # Light SMS cleanup: drop markdown link syntax leftovers from bad outputs.
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 \2", text)
    text = text.replace("**", "")

    fixed["assistant_output"] = text
    fixed["_fix_applied"] = text != original
    return fixed


if __name__ == "__main__":
    baseline = summarize(run_suite())
    traces = load_annotated_traces()
    fixed_traces = [apply_output_fix(t) for t in traces]
    after = summarize(run_suite(fixed_traces))
    print("BASELINE", baseline["passed"], "/", baseline["total_checks"], baseline["pass_rate"])
    for cid, stats in baseline["by_check"].items():
        print(f"  {cid}: {stats['passed']}/{stats['total']} failed={stats['failures']}")
    print("AFTER_FIX", after["passed"], "/", after["total_checks"], after["pass_rate"])
    for cid, stats in after["by_check"].items():
        print(f"  {cid}: {stats['passed']}/{stats['total']} failed={stats['failures']}")
