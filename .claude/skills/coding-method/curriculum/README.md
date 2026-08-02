# Curriculum — Lazy Ideality (7-step learning path)

How to *become* the method: the order in which to read the books so each builds
the capability the next one needs. Every step names the **capability it unlocks**
(which stage of the pipeline it powers), how to read it efficiently, and whether
the source book is available in `CodingBooks-md` (copyrighted material — never
commit it; convert it with `how-to-add-book.md`).

## Selection rule: step vs reference-only
Only 7 books get curriculum **steps**. The rest of the 14 distilled books stay
**reference-only** — they install a *filter or checklist consulted per task*
(red flags, debugging loop, ETC/DRY, trade-off matrix, seams), not a
load-bearing habit you must build in order. The rule: **a step installs a habit
the rest of the method builds on; a reference installs a checklist you reach for
when the habit is already there.** That is why Skiena gets a step but Levitin
(an interim substitute for it) stays a reference, and why CTM / Code Complete /
Google / Pragmatic / Underscore / Dooley / TAPL are references, not steps.

## The path
| # | Book | Capability unlocked | Status |
|---|---|---|---|
| 1 | **How to Design Programs** | the data-first discipline → stages 3–4 | ✅ in CodingBooks-md |
| 2 | **The Algorithm Design Manual** | strategy catalog + complexity → stage 4 | ❌ **da aggiungere** |
| 3 | **A Philosophy of Software Design** | design judgment → stages 3, 7 | ✅ |
| 4 | **Refactoring** | safe mechanical improvement → stages 6–7 | ❌ **da aggiungere** |
| 5 | **Working Effectively with Legacy Code** | change-any-code safety → stage 6 | ✅ |
| 6 | **SICP** | the reasoning engine → stages 3–5 | ✅ |
| 7 | **Fork finale** (FSWA / DDD / DDIA) | system-level judgment → stages 5, 8 | ✅ tutti e tre |

Missing books don't block you: steps 2 and 4 have interim substitutes from the
already-distilled cards.

---

## Step 1 — How to Design Programs (Felleisen et al.)
**Capability:** turning any problem statement into a correct program mechanically.
**Powering:** stage 4 (structure from data).
**Status:** ✅ available.
**Read:** the design recipe is the heart — ch 3, then 4–6 (data definitions),
8–9 (lists + natural recursion), 14–16 (abstraction from examples), 26
(generative recursion + termination), 32 (accumulator style). Copy the tabular
index-card summaries, not the prose. Skip the teachpack material, Intermezzos,
and most finger exercises.
**Why first:** it installs the data-first habit everything else builds on.

## Step 2 — The Algorithm Design Manual (Skiena)
**Capability:** pattern-matching a problem onto a reusable algorithm strategy.
**Powering:** stage 4 (algorithm strategy + complexity class).
**Status:** ❌ **da aggiungere** — the user adds the book to `CodingBooks-md`
(see `how-to-add-book.md`), then its distilled card gets merged into
`references/algorithm-strategies.md`.
**Interim substitute (start today):** the Levitin card (already distilled) —
read its ch 1–2 (the 6-step problem-solving plan + asymptotic notation) and the
strategy chapters 4 (decrease), 5 (divide), 6 (transform), 8 (DP). Note: the
converted Levitin file is the *solution manual*, so use it to see which problems
each strategy targets. Once Skiena lands, read its "war stories" for
real-problem recognition.

## Step 3 — A Philosophy of Software Design (Ousterhout)
**Capability:** design-quality judgment — recognizing and eliminating complexity.
**Powering:** stages 3 (deep modules) and 7 (red flags).
**Status:** ✅ available.
**Read:** ~190 pages in 2–3 sessions. Start with the two end-of-book summaries
(16 principles + 16 red flags) as a one-page checklist. Read carefully: ch 1–2
(complexity theory), 3 (strategic vs tactical), 4 (deep modules), 5 (info
hiding), 7–8, 10 (errors out of existence), 11 (design it twice), 15 (comments
first). Skim 6, 12–14, 16–18. Skip 19–21 first pass. The OCR is degraded — read
body text, ignore figure captions.

## Step 4 — Refactoring (Fowler)
**Capability:** safe mechanical improvement of existing code.
**Powering:** stages 6–7 (trimming/design-it-twice as low-risk steps).
**Status:** ❌ **da aggiungere** — then its catalog merges into
`references/red-flags.md` + `references/construction-checklist.md`.
**Interim substitute (start today):** Feathers covers the "change safely" half
(Legacy Code Change Algorithm, seams, sprout/wrap, characterization tests) and
Dooley covers the "when to refactor" half (refactor-triggers checklist).
Once added, read ch 1–4 as the core (mechanics + smell catalogue), then treat
the catalog chapters as a lookup by smell.

## Step 5 — Working Effectively with Legacy Code (Feathers)
**Capability:** making ANY code safe to change.
**Powering:** stage 6 — the safety layer of the lazy path.
**Status:** ✅ available.
**Read:** ch 2 (the master Change Algorithm — the map), 4 (the Seam Model — the
most important chapter), 3 (sensing/separation). Then 6 (sprout/wrap), 8, 11
(effect analysis), 12 (pinch points), 13 (characterization tests), 23 (safe
first incisions). Treat 9, 10, 14, 15, 19, 21, 25 as reference-by-problem.
A 20% read of ch 2+4+6+13+23 delivers ~90% of the method.

## Step 6 — SICP (Abelson & Sussman, JS edition)
**Capability:** precise mental models of computation — layered abstraction.
**Powering:** stages 3–5 (the reasoning engine).
**Status:** ✅ available.
**Read:** ch 1 fully (1.1.5 substitution model, 1.1.8 black-box abstraction, 1.2
process shapes, 1.3 higher-order functions — the load-bearing core; skim the
Newton/primality math). Ch 2: 2.1 data abstraction + wishful thinking, 2.2
closure + conventional interfaces. Ch 3: 3.1–3.2 (assignment, environment
model), 3.5 streams. Ch 4.1 (metacircular evaluator) is the philosophical peak.
Skip ch 5. Do the exercises — the method is in the doing.

## Step 7 — Final fork: FSWA (default) / DDD / DDIA
**Capability:** system-level architecture judgment — deciding "it depends" with
weighted evidence.
**Powering:** stages 5 and 8 (trade-offs, ADRs) — the counterweight to ponytail's
cheap default.
**Pick by system type:**
- **Default — Fundamentals of Software Architecture** (✅ available): you build
  a variety of systems. Read: ch 2 → 4–5 (characteristics + katas) → 8
  (component-based thinking) → 21 (ADRs) → 22 (risk storming) → 27 (Laws
  revisited); treat ch 10–19 "When to Use/Not Use" as decision-time lookup.
- **Fork A — Learning Domain-Driven Design** (✅ available): you build
  domain-heavy business software. Read: ch 1, 2, 3, 4 (integration), 6
  (tactical building blocks), 10 (decision tree — twice), 12 (EventStorming).
- **Fork B — Designing Data-Intensive Applications** (✅ available): you build
  data-heavy systems (databases, pipelines, analytics). Distilled into
  `references/data-systems.md` — the reference is the operational core; read the
  book for depth. Start with Part I (ch 1: the RSM frame + percentiles; ch 2:
  data-model choice; ch 3: storage engines; ch 4: encoding/evolution — skim),
  then Part II's load-bearing chapters (ch 5: replication + the three lag
  guarantees; ch 7: transactions and the isolation ladder; ch 9: linearizability
  vs causality + consensus-reducible problems), then Part III (ch 10: batch;
  ch 11: stream + CDC/event sourcing; skim ch 12). Read ch 6 (partitioning) and
  ch 8 (partial failure) when a specific system needs them — they're the "why",
  the reference gives the "what to do".

The fork is not permanent — the other two become reference files in the skill
regardless (`architecture-tradeoffs.md`, `domain-modeling.md`; DDIA →
`data-systems.md`).

## Health check
A small script-level check lists which of the 7 books are still missing and
what unblocks each:
`python .claude/skills/coding-method/scripts/method.py route "curriculum check"`
— but the authoritative list lives here. Remaining missing: Algorithm Design
Manual (step 2) and Refactoring (step 4), both with interim substitutes.
