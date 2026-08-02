# sustainable-engineering

Time, scale, and tradeoffs as first-class design inputs: the discipline of
keeping code useful, changeable, and cheap across its whole life span and across
a team — programming integrated over time. Reach for it when code must survive,
be consumed by others, or be changed years from now. Source: *Software
Engineering at Google* (Winters, Manshreck, Wright).

## When to use it
- The code must live for years and be touched by people other than its author.
- You are designing or changing any shared interface, library, API, or data
  format that others consume.
- Before writing a new feature or utility — "should this exist at all?" is the
  first question.
- Setting up the process around code: review gates, CI coverage, testing
  strategy, branching policy.
- Deprecating or migrating something that many teams use.
- Refactoring or upgrading that touches thousands of references.
- A long-lived, business-critical system nobody dares modify anymore.

## Core method

### The three axes — time, scale, tradeoffs
Every coding decision is judged on all three; a solution that optimizes one and
ignores the others is incomplete.
| Axis | Question it forces | Decision rule |
|---|---|---|
| Time | How long must this code live? | Design for the expected life span: a throwaway script does not earn review; a decade-lived API earns extra design [Expected life span] |
| Scale | Does the per-change cost stay flat as the org grows? | Anything whose per-user cost grows with the org must be restructured before it is adopted [Time/scale/tradeoffs] |
| Tradeoffs | What data backs the cost/benefit claim? | Make tradeoffs explicit and evidence-informed; never accept an unstated compromise [Time/scale/tradeoffs] |

### The lifetime decision rule
Programming produces code; software engineering keeps code changeable. Before
writing, state the expected life span and the change velocity, then choose the
minimum process that survives that horizon [Program integrated over time].
Short-lived → write and ship. Long-lived → review, tests, ownership, deprecation
plan. Same decision, different input.

### Hyrum's Law — budget for observable behavior
Any behavior an interface exposes — documented or not — becomes part of its
implicit contract as soon as callers rely on it. Plan for that drift instead of
assuming the written API is the whole deal.
- Treat the documented contract as the floor, not the ceiling, of what you owe
  users [Hyrum's Law].
- Before changing a shared interface, inventory which behaviors are *actually*
  relied on (tests, callers, the data) — not just what you documented.
- Undocumented behavior is frozen the moment users depend on it; changing it
  costs a migration, not a commit [Hyrum's Law].

### Code is a liability — the default answer is no
- Every line is a future maintenance task; added code costs development,
  review, testing, and backward compatibility forever [Code is a liability].
- Search for existing code before writing new: a working abstraction you already
  own beats a new one [Find existing code first].
- Writing from scratch is the last resort, not the default [Code is a liability].

### Shift left / Beyoncé Rule
- Move defect detection as early as possible: static analysis → review →
  test-before-commit. The cost of a defect rises with the stage it escapes
  [Shift left].
- Only a check wired into CI is real: if the pipeline does not enforce it, it
  will silently stop running [Beyoncé Rule].

### Churn Rule — policies that scale
- The owner of a change does the migration work internally; never push it onto
  every downstream user [Churn Rule].
- Centralize the expertise: one expert team does the migration once and
  correctly, instead of every user doing it badly [Churn Rule].

### Small frequent changes to trunk
- Keep the largest atomic change small and land it continuously [Small frequent
  changes to trunk].
- Long-lived feature branches accumulate resync cost and merge pain; the cost of
  a change grows with its distance from the trunk [Small frequent changes to trunk].

### Large-Scale Changes (LSC)
When a change spans hundreds of thousands of references, split it:
1. Centralize the change in one expert team.
2. Write tooling that makes each step mechanical and repeatable.
3. Land the change in small, independently-tested increments — never one atomic
   mega-commit [Large-Scale Changes].
Use LSC for compiler upgrades, interface migrations, or org-wide renames.

### No Haunted Graveyards
- A system that is thoroughly tested can be changed arbitrarily; one that is not
  becomes untouchable [No Haunted Graveyards].
- Never let a component age into "risky to touch" — keep its tests current so
  the cost of changing it stays low [No Haunted Graveyards].

### Maintainable tests (DAMP, not DRY)
- Write small, clear, non-brittle tests; the suite must stay cheap so it keeps
  running [Maintainable tests].
- In tests, prefer DAMP (descriptive and meaningful phrases) over DRY: a test
  reads top-to-bottom like a story even if it repeats setup [DAMP not DRY].
- The tests are the safety net that makes every other change possible; they must
  never become an obstacle to change [Maintainable tests].

### Deprecation as a process
Deleting code is first-class engineering work, not a PR:
1. Ship a backward-compatible upgrade path first.
2. Write a real migration plan with owners and a timeline [Deprecation as a
   process].
3. Do the migration yourself — never issue deadlines to users [Churn Rule].
4. Only after the old path is unused, delete it [Deprecation as a process].

## Worked example
A shared `format_name(user)` helper in a common library is consumed by five
services. It must accept a new middle-name field — but callers pass a single
string today, and one caller concatenates two fields itself and expects the
helper to match.

1. [Hyrum's Law] Before touching it, grep all callers and read the tests: one
   service asserts the old concatenation order. That behavior is now part of the
   contract — budget for it.
2. [Shift left] Add a CI test for the new field before writing the change, so
   the intended behavior is pinned the moment it exists.
3. [Large-Scale Changes] Split the change: (a) add an optional `middle` argument
   with the old behavior as default; (b) update the services that pass it, each
   in its own small commit; (c) fix the one caller with the ordering quirk in
   its own change.
4. [Small frequent changes to trunk] Land each step separately; every commit
   keeps the suite green.
5. [Deprecation as a process] After every caller is migrated, remove the
   concatenation quirk — the one-step delete is safe because a test pins the new
   behavior.

Net: the interface changed, nobody was broken, and the delete at the end was a
one-liner because the migration happened in small, tested steps.

## How it feeds the pipeline
- **Stage 1 (Frame the task):** the time/scale/tradeoffs axes are the frame —
  name the expected life span and change velocity before anything else
  [Program integrated over time], [Expected life span].
- **Stage 2 (Climb the ponytail ladder):** code-is-a-liability and
  find-existing-code restate the ladder as policy; the ladder runs, then the
  lifetime rule decides how much care the survivor earns [Code is a liability],
  [Find existing code first]. See `rewrite-ladder.md`.
- **Stage 3 (Sketch the IFR):** sustainability is the IFR of the codebase — any
  future change is free; the almost-IFR is the minimum change that keeps the
  system changeable [Sustainability]. See
  `triz-innovation/references/ideal-final-result.md`.
- **Stage 5 (Resolve contradictions):** Hyrum's Law = [IP-22 Convert harm into
  benefit] (budget for the latent resource of observable behavior); LSC and
  small changes = [IP-1 Segmentation] (split the big change into small steps);
  the Churn Rule = [IP-24 Intermediary] (do the work where the expertise lives —
  move the code, not the users). See `triz-for-code.md` and
  `triz-innovation/references/software-triz.md`.
- **Stage 6 (Make the minimal safe change):** small frequent changes to trunk +
  No Haunted Graveyards (tested code can be changed) are the safety net that
  makes the minimal diff safe; shift-left = [IP-9 Preliminary anti-action] /
  [IP-11 Cushion in advance] [Small frequent changes to trunk], [No Haunted
  Graveyards], [Shift left]. See `legacy-change.md`.
- **Stage 7 (Review with red flags):** code review is the training ground for
  the red-flag catalogue (`red-flags.md`); maintainable tests (DAMP not DRY)
  keep the audit cheap [Maintainable tests], [DAMP not DRY].
- **Stage 8 (Verify, record, ship):** the Beyoncé Rule is test-as-proof made
  policy — if you relied on it, there is a CI test on it [Beyoncé Rule],
  [Test as proof]. See `method-map.md` for routing.

## Source
*Software Engineering at Google: Lessons Learned from Programming Over Time*,
edited by Titus Winters, Tom Manshreck, and Hyrum Wright (O'Reilly, 2020).
