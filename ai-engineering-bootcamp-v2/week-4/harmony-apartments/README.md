# Week 4 sample pack: Harmony Apartments SMS leasing bot

Use this when you do not yet have enough traces from your own capstone/product.

## Files
- `harmony-apartments-knowledge-base.md` - ground truth the bot should use
- `harmony-apartments-traces.jsonl` - 20 traces (input, context, tools, output) for open coding
- `harmony-apartments-traces.csv` - same traces + empty columns for your notes (Builders-friendly)
- `harmony-apartments-answer-key.jsonl` - self-check ONLY after you finish your own notes

## How to use (Path A)
1. Skim the knowledge base.
2. Open-code all 20 traces (free-text notes, then binary pass/fail + failure label). Do not open the answer key yet.
3. Build a failure taxonomy (aim for 4+ specific categories).
4. Write checks / must-pass cases from your top failures.
5. Propose or implement one fix (prompt rule, assertion, or handoff). Show before/after on the sample set.
6. Optional: compare your labels to the answer key.

## Suggested failure labels you may discover
instruction/constraint miss, grounding/hallucination, formatting (markdown in SMS), missing handoff, tone mismatch, safety/injection, tool-output ignored
