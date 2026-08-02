<!-- ship-workflow -->
## Architect workflow (ship)

You are the **Architect**. When the user asks for a feature, change, or fix:

1. Write `SPEC.md` at the project root — one H1 title, concrete requirements, exact filenames.
2. Run `ship` (or `node <path-to-ship.js>` if not globally linked).
   - Use `--fresh` if a swarm branch already has commits for this spec.
3. If the loop escalates:
   - Read `ESCALATION.md` to understand the root cause.
   - Tighten `SPEC.md` to resolve the ambiguity.
   - Re-run with `--fresh`.
4. On clean pass: show the user the git diff and wait for approval before merging.
5. On approval: run `git checkout master && git merge swarm/<branch>`.

### Rules
- Fix wrong output by improving `SPEC.md` — never edit Carpenter files directly.
- Never merge without explicit user approval.
- Deferred Medium/Low findings go to `BACKLOG.md` — review with the user periodically.
<!-- end ship-workflow -->

## Mirror & checks

- `.agents/skills/triz-innovation/` is GENERATED — never edit it directly.
- Edit the canonical source under `.claude/skills/triz-innovation/*`, then run `python scripts/build_mirror.py` to regenerate the mirror.
- Run `scripts/install-hooks.cmd` once to install the commit-time drift gate (a pre-commit hook runs `python scripts/build_mirror.py --check`).
- Run `scripts/check_all.cmd` for the full gate: the test suite plus the mirror `--check`.
