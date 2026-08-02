# Curriculum — Lazy Ideality (7-step learning path)

How to *become* the method: the order in which to build the capabilities so each
one powers the next. Every step names the **capability it unlocks** (which stage
of the pipeline it powers), how to internalize it efficiently, and whether the
source material is available in the local (gitignored) `CodingBooks-md`
collection — copyrighted source, never commit it; convert it with
`how-to-add-book.md`.

## Selection rule: step vs reference-only
Only 7 capabilities get curriculum **steps**. The rest of the distilled catalog
stays **reference-only** — they install a *filter or checklist consulted per
task* (red flags, debugging loop, ETC/DRY, trade-off matrix, seams), not a
load-bearing habit you must build in order. The rule: **a step installs a habit
the rest of the method builds on; a reference installs a checklist you reach for
when the habit is already there.** That is why the algorithm-strategy catalog
gets a step but the computation-model card (an interim substitute for it) stays
a reference, and why the construction, engineering-culture, pragmatic, and
type-safety catalogs are references, not steps.

## The path
| # | Capability | Pipeline power | Status |
|---|---|---|---|
| 1 | Data-first design discipline | stages 3–4 | ✅ available |
| 2 | Algorithm strategy catalog + complexity | stage 4 | ❌ **da aggiungere** |
| 3 | Design judgment (complexity elimination) | stages 3, 7 | ✅ available |
| 4 | Safe mechanical refactoring | stages 6–7 | ❌ **da aggiungere** |
| 5 | Change-any-code safety | stage 6 | ✅ available |
| 6 | The reasoning engine (computation models) | stages 3–5 | ✅ available |
| 7 | Final fork: system-level architecture judgment | stages 5, 8 | ✅ available |

Missing steps don't block you: steps 2 and 4 have interim substitutes from the
already-distilled cards.

---

## Step 1 — Data-first design discipline
**Capability:** turning any problem statement into a correct program mechanically.
**Powering:** stage 4 (structure from data).
**Status:** ✅ available.
**Read:** the design recipe is the heart — data definitions, then lists + natural
recursion, abstraction from examples, generative recursion + termination,
accumulator style. Copy the tabular index-card summaries, not the prose. Skip
the environment-specific material and most finger exercises.
**Why first:** it installs the data-first habit everything else builds on.

## Step 2 — Algorithm strategy catalog + complexity
**Capability:** pattern-matching a problem onto a reusable algorithm strategy.
**Powering:** stage 4 (algorithm strategy + complexity class).
**Status:** ❌ **da aggiungere** — the source material needs to be added to the
local `CodingBooks-md` collection (see `how-to-add-book.md`), then its distilled
card gets merged into `references/algorithm-strategies.md`.
**Interim substitute (start today):** the strategy card (already distilled) —
read its problem-solving plan + asymptotic notation and the strategy chapters
(decrease, divide, transform, dynamic programming). Note: the converted source
file is the *solution manual*, so use it to see which problems each strategy
targets. Real-problem recognition comes from worked cases.

## Step 3 — Design judgment (complexity elimination)
**Capability:** design-quality judgment — recognizing and eliminating complexity.
**Powering:** stages 3 (deep modules) and 7 (red flags).
**Status:** ✅ available.
**Read:** a short core book in 2–3 sessions. Start with the end-of-book
summaries (the principles + the red flags) as a one-page checklist. Read
carefully: complexity theory, strategic vs tactical, deep modules, info hiding,
errors out of existence, design it twice, comments first. Skim the middle
chapters; skip the final ones first pass. The OCR is degraded — read body text,
ignore figure captions.

## Step 4 — Safe mechanical refactoring
**Capability:** safe mechanical improvement of existing code.
**Powering:** stages 6–7 (trimming/design-it-twice as low-risk steps).
**Status:** ❌ **da aggiungere** — then its catalog merges into
`references/red-flags.md` + `references/construction-checklist.md`.
**Interim substitute (start today):** the legacy-change card covers the "change
safely" half (change algorithm, seams, sprout/wrap, characterization tests) and
the construction card covers the "when to refactor" half (refactor-triggers
checklist). Once added, read the core (mechanics + smell catalogue) first, then
treat the catalog chapters as a lookup by smell.

## Step 5 — Change-any-code safety
**Capability:** making ANY code safe to change.
**Powering:** stage 6 — the safety layer of the lazy path.
**Status:** ✅ available.
**Read:** the master change algorithm (the map), the seam model (the most
important concept), sensing/separation. Then sprout/wrap, effect analysis, pinch
points, characterization tests, safe first incisions. Treat the rest as
reference-by-problem. A 20% read delivers ~90% of the method.

## Step 6 — The reasoning engine (computation models)
**Capability:** precise mental models of computation — layered abstraction.
**Powering:** stages 3–5 (the reasoning engine).
**Status:** ✅ available.
**Read:** the substitution model, black-box abstraction, process shapes,
higher-order functions — the load-bearing core; skim the mathematics. Then data
abstraction + wishful thinking, closure + conventional interfaces, assignment,
environment model, streams. The metacircular evaluator is the philosophical
peak. Do the exercises — the method is in the doing.

## Step 7 — Final fork: system-level architecture judgment
**Capability:** system-level architecture judgment — deciding "it depends" with
weighted evidence.
**Powering:** stages 5 and 8 (trade-offs, ADRs) — the counterweight to the cheap
default.
**Pick by system type:**
- **Default — general architecture** (✅ available): you build a variety of
  systems. Read: characteristics + katas → component-based thinking → ADRs →
  risk storming → laws revisited; treat the "When to Use/Not Use" chapter as a
  decision-time lookup.
- **Fork A — domain-heavy modeling** (✅ available): you build domain-heavy
  business software. Read: the domain-first chapters, integration, tactical
  building blocks, the decision tree — twice, EventStorming.
- **Fork B — data-heavy systems** (✅ available): you build data-heavy systems
  (databases, pipelines, analytics). Distilled into `references/data-systems.md`
  — the reference is the operational core; read the source for depth. Start with
  the composite-data-system frame (reliability + percentiles; data-model choice;
  storage engines; encoding/evolution — skim), then the load-bearing chapters
  (replication + the three lag guarantees; transactions and the isolation
  ladder; linearizability vs causality + consensus-reducible problems), then
  derived data (batch; stream + CDC/event sourcing; skim the rest). Read
  partitioning and partial failure when a specific system needs them — they're
  the "why", the reference gives the "what to do".

The fork is not permanent — the other two become reference files in the skill
regardless (`architecture-tradeoffs.md`, `domain-modeling.md`; data-systems →
`data-systems.md`).

## Health check
A small script-level check lists which steps are still missing and what unblocks
each:
`python .claude/skills/coding-method/scripts/method.py route "curriculum check"`
— but the authoritative list lives here. Remaining missing: the algorithm-
strategy catalog (step 2) and safe refactoring (step 4), both with interim
substitutes.
