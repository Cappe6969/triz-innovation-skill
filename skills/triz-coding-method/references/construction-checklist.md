# construction-checklist

The construction-craft layer of the method: how to build and fix code so one
human mind only ever holds one part at a time, then prove it stays correct.
Merges the complexity-management rules (manage complexity, ADTs,
coupling/cohesion, hide secrets, leanness, defensive programming) with the
engineering-workflow rules (wicked problems, oscillating design, TDD, the
debugging loop, code review). Reach for it while writing, debugging, or auditing
any code; the broken-code path in `method-map.md` routes here.

## When to use it
- You're about to build a class/function and want the boundaries right the first time.
- A bug report arrives — run the 5-step debugging loop, not a guess.
- You're adding code and hear "it's easy, just add it" — run the [Leanness] gate.
- Code is untested or hard to change — write a failing test first, then make it pass.
- You're reviewing a diff — audit coupling/cohesion, hidden secrets, refactor triggers.
- The problem statement is fuzzy — decide [Wicked vs tame] before designing.

## Core method

### Complexity is the master filter
**[Manage complexity]** — every design and code decision is judged against one
criterion: *can the reader focus on this piece safely in isolation?* Keep
routines short, work at the highest abstraction, express code in problem-domain
terms. Minimize the essential complexity each part demands; stop accidental
complexity from proliferating. **[Intellectual toolbox]** — treat every
technique, pattern, and methodology as one tool among many, not a rule: pick per
problem and combine freely; the tool that "always applies" is a dogma.

### Translation table (Software ↔ TRIZ)
| Software concept | TRIZ concept |
|---|---|
| Leanness, "nothing more can be taken away" | Trimming + Ideal Final Result |
| Design trade-off ("X improves → Y degrades") | Engineering contradiction to dissolve, not balance |
| "Simplifying may mean more modules" | Contradiction resolved by decomposition (Segmentation) |
| Isolate the part likely to change | Separation: stable vs volatile; Dynamization / Taking out |
| Hide secrets behind a stable interface | Confine the varying parameter; one stable access point |
| Loose coupling | Segmentation — independent pieces held one at a time |
| Essential vs accidental complexity | Resource analysis: inherent vs self-inflicted |
| Fix the root cause, not the symptom | Eliminate the harmful function at its source (no patches) |
| Extract duplicated code (DRY) | Trimming: remove element, relocate its useful function |
| "Good enough" subset of features | Aim at the IFR, not completeness |
| Reuse a knapsack of patterns | Standard solutions + resource inventory |

### Frame before you build
**[Measure twice, cut once]** — problem definition, requirements, and shape
before construction; a wrong problem definition wastes everything downstream.
Scale the ceremony down on iterative work. **[Wicked vs tame]** triage first:

| | Wicked | Tame |
|---|---|---|
| Problem | ill-defined, requirements evolve as you solve | stable, objectively checkable |
| Stopping rule | none — iterate to "good enough" | known completion point |
| Approach | oscillate problem ↔ solution, prototype | solve directly with a known path |

**[Oscillating design]** — for non-trivial/wicked problems, abandon the
waterfall: swing between requirements analysis and solution modeling, converging
on good enough instead of a linear problem→solution pass.

### Give the shape (design heuristics)
- **[Abstract data type]** — model real-world objects; provide a complete,
  minimal, non-leaky interface; the caller sees one consistent concept and never
  the implementation.
- **[Isolate changes]** — during design, predict what will change (new output
  format, new data source) and confine each likely change to a single spot so it
  can't ripple through the system.
- **[Hide secrets]** — each class/module conceals the design decisions most
  likely to change behind a minimal stable interface; the rest of the system
  never depends on the hidden details.
- **[Loose coupling / high cohesion]** — keep interconnections few, small, and
  clear (low-to-medium fan-out); keep each module's internals strongly related
  (high fan-in for utility layers). Loose coupling is the cheapest insurance for
  integration and maintenance.
- **[Standard patterns]** — prefer named, standard, common solutions over exotic
  custom designs; standardization makes the whole system familiar to a first-time
  reader.
- **[Mental-model simulation]** — before writing code, build a mental model of
  the proposed solution, execute it on sample input, fix what comes out wrong,
  re-simulate, until samples produce correct output (design-as-debugging in your
  head).
- **[Defer decisions]** — don't force closure on the last 20% of a design;
  leave unresolved points until you have more information. When stuck on a
  design, switch medium (diagram → prose → prototype → brute force → walk away)
  rather than grinding.
- **[Design characteristics]** — judge any design against: fitness of purpose,
  separation of concerns, simplicity, ease of maintenance, loose coupling, high
  cohesion, extensibility, portability.

### Leanness — the "just add it" gate
**[Leanness]** — design with no extra parts. Before adding any feature or line,
ask: *what will we hurt by putting it in?* Extra code costs development, review,
testing, and backward-compatibility forever. This is the anti-YAGNI question —
the ladder rung that says "no" first.

### Build it
- **[Defensive programming]** — validate everything entering your code (args,
  files, params, nulls, zeros, out-of-range values) at external boundaries.
  Assertions for "should never happen" errors; exception/error handling for
  expected ones. Prefer recovery over exit; never fail silently.
- **[Test-first TDD]** — write a failing test first, stub the class/method,
  implement until it passes, then rerun the whole suite after every change so
  every fix becomes a regression test.
- **[Refactor triggers]** — while constructing or touching any code, refactor
  when you see: duplicated code (extract, DRY), a method longer than ~1 screen,
  weak cohesion, too many parameters, magic numbers (→ named constants),
  comments documenting hard code (rewrite the code), public instance variables
  (encapsulate), a middleman object, or code that doesn't return as soon as it
  knows the answer.

### Debug the loop
**[Debugging loop]** — never guess at the error location; never special-case a
symptom:

| Step | Move |
|---|---|
| 1 | Reproduce reliably |
| 2 | Shrink to the minimal failing input (halve the data) |
| 3 | Work backwards from the symptom — read code, print, or debugger |
| 4 | Fix the root cause, not the symptom — one error at a time |
| 5 | Rerun the original test **plus** the full regression suite |

### Review it
**[Code review]** — a static error-finding gate complementary to testing (it
finds static/logic errors tests can't). Formal inspection runs phases: planning →
overview → preparation → inspection → report → rework; or use a lightweight
agile peer review. Prefer reviewers trained on the red-flag catalogue
(`red-flags.md`) so review is pattern-matching, not opinion.

## Worked example
`Scoreboard.add(team, pts)` crashes on one data feed. Run the method:
- **Frame:** tame bug; root function = add points; constraint = must not crash
  on any feed. [Wicked vs tame]
- **Reproduce:** replay the feed — fails only when a team name has a leading
  space. [Debugging loop]
- **Shrink:** minimal input `" teamA", 5` reproduces. [Debugging loop]
- **Root cause:** `add()` assumes names parse cleanly; nothing at the boundary
  validated input. [Defensive programming]
- **Fix:** one `normalize()` at the API boundary, ADT internals untouched.
  [Hide secrets] [Abstract data type] [Defensive programming]
- **Test-first:** write failing tests (leading-space name, negative points)
  *before* the fix; fix; rerun the full suite. [Test-first TDD]
- **Audit:** `add()` is still short, single-purpose, low fan-out. [Loose
  coupling / high cohesion]

## How it feeds the pipeline
- **Stage 1 (Frame):** [Wicked vs tame] triage + [Measure twice, cut once]
  prerequisites set the task shape.
- **Stage 2 (Ladder):** [Leanness] is the "what will we hurt?" YAGNI gate — run
  it before every rung.
- **Stage 3 (IFR):** design heuristics — [Abstract data type], [Hide secrets],
  [Isolate changes] — push the module toward depth; [Defer decisions] stops
  premature structure.
- **Stage 5 (Contradictions):** design trade-offs are contradictions; before
  accepting a compromise, try to dissolve it (separate stable/volatile,
  decompose). Cross-ref `triz-for-code.md` / `architecture-tradeoffs.md`.
- **Stage 6 (Minimal safe change):** [Defensive programming], [Test-first TDD],
  and construction style protect the diff; the broken-code debugging path in
  `method-map.md` routes here.
- **Stage 7 (Review):** [Design characteristics] audit, [Loose coupling / high
  cohesion], [Hide secrets], [Refactor triggers], and [Code review] phases —
  the construction half of the audit (the red-flag half lives in `red-flags.md`).
- **Stage 8 (Verify):** the debugging loop's step 5 and the TDD suite rerun are
  the mandatory regression-test close.

Siblings: `method-map.md` (router + debugging path), `red-flags.md` (review
checklist), `deep-modules.md` (module depth), `legacy-change.md` (safe change on
untested code), `pragmatic-etiquette.md` (debugging mindset, ETC), `design-recipe.md`
(data-first build discipline), `triz-for-code.md` (TRIZ↔code bridge). TRIZ skill:
`references/software-triz.md`, `references/trimming.md`,
`branches/fields/software/branch.json`.

## Source
Original operational synthesis from the software-construction literature.
