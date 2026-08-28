# Week 4 TRACE — failure taxonomy (Harmony Apartments)

From open-coding 20 SMS leasing-bot traces (11 pass / 9 fail).

| Code | Definition | Example traces | Freq |
|------|------------|----------------|------|
| `grounding_policy_error` | Output contradicts the KB (pets, tours, breeds, limits) | ha-003, ha-004, ha-013, ha-019 | 4 |
| `unauthorized_action` | Bot books/holds a unit or shares credentials instead of handing off to office | ha-005, ha-008 | 2 |
| `incomplete_or_offtopic` | Misses the ask, incomplete inventory, or irrelevant reply | ha-001, ha-002 | 2 |
| `invalid_link` | URL outside the Harmony allowlist (or markdown link junk on SMS) | ha-006 | 1 |
| `tone_pressure` | Pushy sales pressure | ha-002 | 1 |

## Rank (frequency × impact)
1. `unauthorized_action` — highest impact  
2. `grounding_policy_error` — most frequent  
3. `incomplete_or_offtopic`  
4. `invalid_link`  
5. `tone_pressure`

## Path A code checks (this folder)
- **A — `invalid_link`:** every `http(s)` URL in `assistant_output` must be on the KB allowlist.  
- **B — `unauthorized_action`:** fail if the bot claims a hold/booking/confirmation or leaks a password/credential.
