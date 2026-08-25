# Contributing

Thanks for looking at this repo. It is primarily a personal project built with
a spec-driven ("ship") workflow, but focused issues and PRs are welcome.

## The full gate (must pass before any merge)

```bash
python -m unittest discover -s tests -p "test_*.py"
python .claude/skills/triz-innovation/scripts/triz.py branches check
python .claude/skills/triz-innovation/mcp/triz_mcp_server.py --self-test
```

Windows shortcut: `scripts/check_all.cmd`. CI (`.github/workflows/ci.yml`)
runs the same three steps on Ubuntu + Windows, Python 3.9 / 3.11 / 3.13.

## Ground rules

- **Stdlib only.** No third-party dependencies, no pip install. If your change
  needs one, propose it in an issue first.
- **Tests travel with behavior.** New script behavior needs unittest coverage;
  bug fixes need a regression test.
- **Data stays pure data.** Field/language branches are JSON only; the registry
  (`branches check`) validates them.
- **No copyrighted text.** `references/` content must remain original
  operational rewriting (see `.claude/skills/triz-innovation/docs/source-map.md`).
- Deferred findings go to `BACKLOG.md` rather than half-fixed.

## Workflow notes

Features here are specified in `SPEC.md` and built on short-lived branches,
merged only after review (see `CLAUDE.md`). External contributors can ignore
that machinery: keep PRs small, run the gate, describe what changed.
