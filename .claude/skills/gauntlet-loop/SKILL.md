---
name: gauntlet-loop
description: >
  Improvement-loop protocol for this repository. Each iteration picks ONE
  target, sets a named/fetchable/comparable quality bar, runs a builder and a
  separate harsh critic with fresh context, compares blind against the bar,
  and loops until ours wins — then enforces the repo gate before committing.
  Triggers on "/gauntlet-loop", "gauntlet loop", "run a gauntlet iteration",
  or when GAUNTLET.md points here for the iteration engine.
---

# Gauntlet Loop — v2 scheme

Technique: Matt Shumer's gauntlet loop (builder / harsh critic / blind
comparison against a real bar, loop until it wins). Packaging inspiration:
robonuggets/gauntlet-loop (CC BY 4.0). This file adapts both to this repo's
existing machinery (`scripts/gauntlet.ps1`, lens rotation, journal).

## The one-rule summary

Work is done when an independent critic — fresh context, labels stripped —
picks ours over a **real, named bar**. Never when it "looks good", never after
N rounds. The gate then decides whether it may ship.

## Per-iteration protocol

**0. Baseline.** `pwsh scripts/gauntlet.ps1` must PASS. Red gate = fixing it
is the iteration.

**1. Pick ONE target.** First applicable: open `BACKLOG.md` items unblocked by
external materials → else lens rotation from `GAUNTLET.md` (docs-truth,
test-gap, data-completeness, cli-ux, cross-platform, hygiene).

**2. Set the bar BEFORE building.** The bar must be:

- **Named** — a specific artifact that exists. Not "good tests".
- **Fetchable** — the critic can actually open/run/read both sides. In-repo
  artifacts are ideal bars because they are trivially fetchable.
- **Comparable** — you can strip labels, put A next to B, and pick a winner.

Repo-proven bar examples (use these forms):

| Target | Bar |
|---|---|
| Error-handling in a sub-tool | "CSV errors are handled exactly as thoroughly as `triz_evaluator._parse_csv`'s BOM/short-row/stderr tests in `tests/test_triz.py` (R3 block)" |
| Doc accuracy | "Every command in the README works verbatim, as verified for `triz.py` in the docs-truth iteration" |
| Test-suite rigor for module X | "Edge coverage matches the catalog tests: exact values, fixture presence, clean stderr — the R4 block standard" |
| README/outside-facing doc | "Structure and scannability of ripgrep's or fd's README" (fetch it first) |
| Data completeness | "scientific_effects.json carries N entries/families with the same field completeness as standard_solutions_76.json (87 complete entries)" |

Add the measurable half when one exists (test count, families covered, gate
time). Taste plus a number beats taste alone.

**3. Builder pass.** Implement the smallest correct change toward the bar.
Rules from `GAUNTLET.md` still bind: stdlib-only, behavior changes need
tests, ~≤300 changed lines, one concern.

**4. Critic pass — fresh context, mandatory.** The critic must NOT be the
builder's stream of thought. In priority order:

1. Spawn a true fresh-context process and hand it only the two artifacts:
   `claude -p`, `opencode run`, or `codex exec`, whichever exists.
2. Fallback: the Task/subagent tool with a prompt containing ONLY the two
   artifacts and the instruction below — no builder reasoning, no history.
3. Last resort (log it in the journal as `critic=weak`): self-critique with
   the artifacts re-read from disk, labels stripped, forced adversarial
   stance.

Critic instructions (verbatim job): *"Below are Artifact A and Artifact B and
the bar description. Labels are stripped; do not guess which is which. Pick
which one better meets the bar — binary, no scores. Then name the single
biggest remaining gap in the loser. Be harsh; praise is useless."*

Randomize/rotate A/B across rounds so position can't leak the answer.

**5. Resolve.**

- Critic picks **ours** → go to 6.
- Critic picks the **bar** → its single biggest gap becomes the builder's
  next input; repeat 3–4. No round cap. If two consecutive rounds produce no
  movement on the gap, the gap is out of scope for this iteration: shrink the
  claim (or the bar) explicitly, get a fresh pick, and record that decision.

**6. Ship through the gate.** `pwsh scripts/gauntlet.ps1` must PASS (zero
hard fails). Then:

```
git commit -m "gauntlet(<lens>): <what> — beat <bar> blind"
git push
```

Append to `.gauntlet/journal.log`: date, lens, bar, rounds, verdict
(`won blind` / `won shrunk`), critic mode (`fresh` / `subagent` / `weak`).

**7. Stop conditions.** Unchanged from `GAUNTLET.md`: same idea fails twice →
abandon and log why; nothing passes the "would a maintainer thank me?" test →
DONE. Plus: critic keeps rejecting after scope-shrink → abandon, the bar wins.

## Hard guardrails (never)

- The builder never grades its own work except in logged `critic=weak`
  fallback.
- Never weaken tests, edit data to silence assertions, add dependencies, or
  touch copyrighted material — `GAUNTLET.md` rules carry over verbatim.
- Master merges need explicit user approval; iterate on feature branches.
- A round that can't name its bar doesn't start.

## Running the whole loop

Feed an agent this line each cycle (Claude Code `/loop`, opencode scheduled
task, cron + `claude -p`, …):

> Read `.claude/skills/gauntlet-loop/SKILL.md` and `GAUNTLET.md`, then execute
> exactly one full iteration (protocol steps 0–7). Do not skip the critic.

Credit: gauntlet-loop technique by Matt Shumer (mshumer/Claude-of-Duty);
skill-packaging pattern by robonuggets/gauntlet-loop (CC BY 4.0). This
adaptation adds the enforcement gate, lens rotation, and journal.
