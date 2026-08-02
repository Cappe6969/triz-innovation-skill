# Paired benchmark

Ten minimized fixtures compare a baseline coding prompt with the same prompt
plus `$triz-coding-method`. Five are public examples; five are anonymized
behavioral reductions of real commits. Fixture JSON embeds the starter files
and deterministic tests materialized into an isolated temporary directory.

Validate without model calls:

```text
python benchmarks/runner.py --dry-run
```

Run one paid/authenticated arm explicitly:

```text
python benchmarks/runner.py --execute --fixture closest-pair --arm treatment --results-dir benchmark-results/run-001
```

The runner uses Codex CLI 0.146.0, `gpt-5.6-luna`, low reasoning, an ephemeral
session, Python 3.11, and Node 24. It writes JSONL events, final answer, patch,
test outcome, production-line count, dependencies, and elapsed time. Reviewers
receive randomized A/B packets and must not see arm names.

Release gate: treatment tests 10/10, no regression relative to baseline, blind
treatment preference at least 7/10, median treatment production lines no
greater than baseline, and no unjustified dependency.
