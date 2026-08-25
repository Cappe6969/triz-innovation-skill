# GAUNTLET — continuous-improvement loop

The gauntlet is how this repo improves itself: **one bounded, verified,
pushed improvement per iteration**, forever or until nothing worth doing
remains. Two parts:

- `scripts/gauntlet.ps1` — the enforcement harness (runs everything, pass/fail)
- this file — the iteration contract an agent (or human) follows each cycle

**Iteration engine (v2):** each improvement is now driven through the
builder/critic/blind-bar protocol in
[`.claude/skills/gauntlet-loop/SKILL.md`](.claude/skills/gauntlet-loop/SKILL.md):
set a named, fetchable bar for the chosen lens target, build, then let a
fresh-context critic compare blind — ship only when ours wins. The protocol
below defines the rails (gate, commit format, journal, guardrails); the v2
skill defines how step 2–3 are executed.

## The iteration protocol (exactly one per run)

**0. Baseline.** Run `pwsh scripts/gauntlet.ps1`. It must PASS before any new
work. If it fails: fixing it *is* this iteration; commit the fix alone.

**1. Pick exactly ONE improvement.** First applicable source wins:

| Order | Source | Notes |
|---|---|---|
| 1 | `BACKLOG.md` Open items | only ones not blocked on external materials |
| 2 | Lens rotation (below) | alternate lenses across iterations |

**2. Implement the smallest correct change.**
- Stdlib-only Python. No new dependencies, ever.
- Behavior changes require tests; bug fixes require a regression test.
- Docs claims must be verified by actually running the documented command.
- Keep diffs small (~≤300 changed lines). One lens, one concern.

**3. Gate again.** `pwsh scripts/gauntlet.ps1` must PASS with zero hard fails.
Soft warnings should trend down over time; do not add new ones.

**4. Commit + push.**
```
gauntlet(<lens>): <one-line what>
```
Push to the current feature branch. Never push red; never force-push;
never rewrite history; master merges need explicit user approval.

**5. Journal.** Append to `.gauntlet/journal.log`:
`<iso-date> gauntlet(<lens>): <change> -> PASS`

**6. Stop conditions.**
- The same idea fails the gate twice → abandon it, log why, pick another.
- Nothing passes the "would a user/maintainer thank me for this?" test →
  declare DONE and stop. Do not pad.

## Improvement lenses (rotation)

1. **docs-truth** — run every command in README / SKILL.md /
   docs/usage-guide.md; fix drift between docs and reality.
2. **test-gap** — find untested edges in `scripts/*.py` (empty input,
   unicode, malformed CSV/JSON rows, unknown flags, missing files) and add
   focused unittests.
3. **data-completeness** — the catalogs are thin: the scientific-effects
   catalog spans only a handful of broad families, with some families much
   smaller than others; spot-check matrix/principles data against public
   TRIZ references; extend carefully with sourced, original phrasing.
4. **cli-ux** — inconsistent flags, error messages, or exit codes across
   sub-tools; align them with the dispatcher's conventions (`Error:` on
   stderr, non-zero exit, no tracebacks).
5. **cross-platform** — encoding edge cases (cp1252 vs utf-8), path
   handling, CI matrix cells (ubuntu/windows × py3.9/3.11/3.13).
6. **hygiene** — gitignore correctness, stray artifacts, marker scan,
   journal review, dependency-free claim still true.

## Hard guardrails (never)

- No third-party dependencies; no pip installs.
- Never delete or weaken tests to make the gate pass.
- Never edit data files just to silence a failing assertion without
  understanding why.
- No copyrighted text into `references/` (see `docs/source-map.md`).
- No scope creep beyond the chosen lens; one commit per iteration.
- Respect `.gitignore`: `Books/`, `CodingBooks*/`, secrets, `.gauntlet/`.

## Running it

```bash
# human / CI-style single sweep
pwsh scripts/gauntlet.ps1

# agent loop — opencode (/loop, adaptive):
#   prompt: "In triz-innovation-skill: read GAUNTLET.md and execute exactly
#            one iteration of the protocol. Stop at section 6 rules."

# agent loop — Claude Code (bash wrapper):
while true; do
  claude -p "Read GAUNTLET.md and execute exactly one iteration." \
    --allowedTools "Bash,Read,Edit,Write" || break
  sleep 60
done
```

The loop is healthy when the journal grows one line per run, the gate stays
green, and every commit is individually defensible.
