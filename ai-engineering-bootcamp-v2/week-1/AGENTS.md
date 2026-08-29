# Session 5 — memory write gate (above the compaction line)

When changing Northwind week-1 memory:

- Persist ONLY allowlisted keys: preferred_name, preferred_language, work_mode,
  last_policy_topic, role.
- Never store raw tool dumps, full chat transcripts, API keys, or passwords.
- Prefer short stable facts useful across sessions.
- Recall is keyed by `user_id`; a new chat/thread with the same user_id must
  still load SQLite memory without the user restating preferences.
