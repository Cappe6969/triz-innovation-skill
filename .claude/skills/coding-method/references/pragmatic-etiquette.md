# pragmatic-etiquette

The Pragmatic Programmer mindset layer for coding-method: ETC, DRY,
orthogonality, tracer bullets, broken windows, design by contract, find the box,
and the debugging discipline (Hunt & Thomas). Not a technique catalog — a set of
judgment habits that decide **how big** a change should be (ponytail answers
this) and **which direction** it should take (this file answers that). Reach for
it when two minimal options tie, when code is rotting, or when a bug looks
impossible.

## When to use it
- Two candidate changes are equal in size — pick the one that leaves the system easiest to change.
- Rot spotted on review, in review itself, or before merge — fix or board up now.
- The same knowledge exists in two places (code, comments, config, two modules, two developers).
- A change you expect to ripple across components.
- Starting a feature with unknowns or risky integrations.
- Any bug, especially intermittent or "worked on my machine".
- A problem that feels impossible — the Gordian-knot moment.
- Writing or reviewing any module/API boundary.

## Core method

### ETC — the meta-rule [ETC]
Judge every design choice by a single question: **does this make the system
easier or harder to change?** Decoupling, single-responsibility, naming, config
— all reduce to ETC.
- At a decision fork, if unsure, make the chunk **replaceable**.
- When several minimal options are equal in size, pick the one that keeps the system easiest to change (a rule ponytail lacks).

### DRY — one source of truth [DRY]
Every piece of knowledge must have a **single, unambiguous, authoritative
representation** in the system. Duplication is of *knowledge*, not just code.
Four duplication sources to hunt:
| Source | Pattern | Fix |
|---|---|---|
| Imposed | Two tools force the same info (e.g., schema + API shape) | Generate one from the other |
| Inadvertent | Two things happen to look alike | Share only the truly-shared concept |
| Impatient | Copy-paste to save typing | Extract, don't duplicate |
| Interdeveloper | Two people wrote the same thing unaware | Cross-check ownership, one canonical home |
Also kill **doc duplication**: comments that repeat the code.

### Orthogonality [Orthogonality]
Design components so a change to one has **no ripple** on others.
- Don't split one piece of knowledge across multiple components.
- Audit coupling: if touching A forces touching B, they share a concept.
- Test at the component boundary; changes should need only the component's own tests.

### Tracer bullets [Tracer bullet]
Build the **thinnest end-to-end skeleton** that pierces every layer
(UI → logic → data) and makes one real call work; then flesh out in parallel.
- Tracer code is production-quality, just not feature-complete.
- Prefer over big-bang module-by-module builds; it surfaces integration risk early.

### Broken windows [Broken window]
Software rot spreads by psychology: one unrepaired bad design invites more.
- Fix each broken window **as soon as found** on review, during debugging, before merging.
- If you can't fix now, **board it up** [Board it up]: comment out, mark dead, dummy-data — don't leave it looking alive.
- *First, do no harm.* Fixing small rot now is a shorter-diff-tomorrow move (fights lazy-minimalism).

### Design by contract [Design by contract]
Define each module's **preconditions, postconditions, and invariants** at the
boundary; the caller and callee share responsibility.
- On violation, **crash early** [Crash early] — a loud, locatable failure is a resource.
- Combine with asserting invariants; **never swallow errors**.

### Programming deliberately [Deliberate programming]
Never rely on luck. Use only documented behavior; know *why* your code works.
- Don't keep spurious calls "because it works"; don't fix by coincidence (±1 patches and phantom patterns mask real flaws).
- If something works without a clear reason, investigate before proceeding.

### Find the box [Find the box]
Don't think outside the box — **find** it. Enumerate every avenue, categorize
**real vs imagined** constraints, prioritize the most restrictive first (cut the
longest piece first), and solve within the degrees of freedom you actually have.
- Use at the Gordian-knot moment and during requirements analysis.
- This is TRIZ's anti-inertia move: most "impossible" problems die by naming an imagined constraint.

### Debugging mindset [Binary chop]
Don't panic. Reproduce the bug first — a non-reproducible bug is a second bug.
- Don't assume fault; don't assume innocence. Locate by **bisecting** the data/code path, not by reading the whole file.
- Check the simple, obvious cause first.
- Fix the **root cause, not the symptom** [Root-cause fix] — then add a regression test so the fix stays fixed.

### Knowledge portfolio [Knowledge portfolio]
Great code, like great lawns, needs daily small care. Make many small
improvements continuously: learn new tools, invest in skill, practice
deliberately. Do it weekly, not just on projects.

## Worked example
Bug: a timezone-corrected report is off by one hour for some users, only on the
server, intermittently. Junior instinct: "works on my machine, it's fine."
- [Deliberate programming] Stop. Non-reproducible = haven't reproduced. Log the actual inputs at the boundary.
- [Binary chop] Bisect the date pipeline: format → parse → offset. Confirmed the offset constant is applied twice for users whose timezone string matches the server default — a `TZ` env dependency.
- [Find the box] The real constraint: two components both "know" the timezone (envelope + body). One is a phantom; the config layer is the box.
- [Root-cause fix] Delete the duplicate offset in the parser; keep the single authoritative envelope.
- [Design by contract] Add a precondition to the formatter: input must be timezone-normalized; assert it and crash early instead of producing a wrong date.
- [DRY] The timezone knowledge now lives in one place.
- Close with a regression test ([Binary chop] stays green) and re-run the review pass: no new [Broken window] left behind.

## How it feeds the pipeline
- **Stage 1 Frame the task** — [Find the box]: separate real from imagined constraints; name responsibility for the outcome.
- **Stage 2 Climb the ladder** — [Good-enough software] as YAGNI (know when to stop); [ETC] as the tiebreaker when equal-size options remain.
- **Stage 3 Sketch the IFR** — [ETC] is the ideal-final-result flavor: a system that adapts to change is the ideal target; aim the almost-IFR at changeability.
- **Stage 5 Resolve contradictions** — [Find the box] dissolves false contradictions; the real-vs-imagined constraint split is the anti-inertia frame.
- **Stage 6 Make the minimal safe change** — the debugging loop: [Binary chop], [Root-cause fix], [Crash early]; broken code routes here via `method-map.md`.
- **Stage 7 Review with red flags** — [DRY], [Orthogonality], [Broken window]/[Board it up], [Deliberate programming] audit; fix each broken window now.
- **Stage 8 Verify, record, ship** — regression test as proof; [Knowledge portfolio] as the continuous-improvement habit after ship.
Cross-links: sibling `construction-checklist.md` (debugging loop), `red-flags.md`
(DRY/orthogonality audit items), `legacy-change.md` (characterization before
fixing), `triz-for-code.md` (box = contradiction reframe); triz-innovation
`references/software-triz.md`, `references/root-cause-analysis.md`,
`references/contradiction-analysis.md`, `references/function-analysis.md`,
`branches/fields/software`.

## Source
The Pragmatic Programmer — Andrew Hunt & David Thomas (1999; 20th-anniversary ed. 2019).
