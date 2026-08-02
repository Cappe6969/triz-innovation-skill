# Method Map — the coding-method stage router

How the 8-stage **Lazy Ideality** pipeline decides what to do and which
reference file to load. Read this first — it is the index for the whole skill.
The pipeline merges three sources: **ponytail** (the lazy default), **TRIZ**
(the stuck-state engine), and the distilled methods of classic programming books
(the field-branch catalog of standard moves).

## The pipeline at a glance
| Stage | Name | Produces | Core tags |
|---|---|---|---|
| 1 | Frame the task | neutral restatement, function, constraints | [Function analysis], [Wicked vs tame] |
| 2 | Climb the ponytail ladder | build-or-reuse decision | [YAGNI], [Leanness], [Creative extension] |
| 3 | Sketch the Ideal Final Result | the target + the "almost-IFR" | [IFR], [Deep module], [Design it twice] |
| 4 | Structure from data | data def + signature + strategy | [Design recipe], [Computation model], [Strategy catalog] |
| 5 | Resolve contradictions | named contradiction + principle | [Contradiction], [Separation], [Trade-off matrix] |
| 6 | Make the minimal safe change | the diff, test-protected | [Legacy Change], [Seam], [Characterization test] |
| 7 | Review with red flags | the audit | [Red flag], [Trimming], [DRY] |
| 8 | Verify, record, ship | tests, ADR-lite, ≤3-line why | [Test as proof], [ADR], [≤3 lines] |

## Escalation table — which path, when
| Situation | Path | Load |
|---|---|---|
| Routine task, pattern known | Stages 1 → 2 → 6, skip the rest | `rewrite-ladder.md`, `ladder.py` |
| Genuine trade-off ("I need X but that breaks Y") | Stages 1 → 5 | `triz-for-code.md`, `architecture-tradeoffs.md` |
| Stuck after the basics | Stage 5 forced contradiction | `triz-for-code.md` + `triz_matrix.py` |
| Legacy/untested code that must not break | Stages 1 → 6, full Feathers | `legacy-change.md` |
| System-level decision (architecture) | Stages 1 → 3 → 5 → 8 + ADR | `architecture-tradeoffs.md`, `domain-modeling.md` |
| **Broken code / debugging** | Debugging loop (below) | `construction-checklist.md`, `pragmatic-etiquette.md` |
| Novel structure, design unclear | Full recipe, stages 1 → 7 | `design-recipe.md`, `deep-modules.md` |
| Data-heavy system decision | Stages 1 → 3 → 5 (data fork) | `data-systems.md` (FUTURE: DDIA) |

## The debugging path (broken code)
A bug report is a *different* problem shape from a design task — route it
explicitly, never straight to the ladder:

1. **Characterize before touching.** [Characterization test] on the failing
   behavior (`legacy-change.md`) — you can only change what you can observe.
2. **Run the 5-step debugging loop** (`construction-checklist.md`): reproduce →
   stabilize → locate (binary chop the input/process) → fix the *root cause*,
   not the symptom → add a regression test.
3. **Find the Box first** (`pragmatic-etiquette.md`): is the real constraint
   imagined? Does the bug even matter at this scale?
4. **Effect analysis** (`legacy-change.md`): before the fix, map what the change
   touches (pinch points) so the fix is provably local.
5. Close with the mandatory test + numeric criterion (stage 8) — a debug is not
   done until a test proves the failure is gone and stays gone.

## Intensity levels (ponytail-compatible)
- **lite** — stages 1–3 only: routine task, ladder + IFR + one-liner.
- **full** — all 8 stages: default for anything with a design decision.
- **ultra** — full + forced TRIZ contradiction escalation + a verification pass
  (`type-safety.md` progress/preservation-style proof or a substitution-model
  trace) + the trade-off matrix scored twice (once per hypothesis).

## Reference index
| Need | File |
|------|------|
| This router + escalation | `references/method-map.md` |
| HtDP design recipe (data-first discipline) | `references/design-recipe.md` |
| Computation-model ladder + declarative default | `references/computation-models.md` |
| Algorithm strategy catalog + complexity | `references/algorithm-strategies.md` |
| Deep modules + complexity model | `references/deep-modules.md` |
| Review checklist (red flags + construction) | `references/red-flags.md` |
| Construction craft + debugging loop | `references/construction-checklist.md` |
| Safe change on legacy code | `references/legacy-change.md` |
| Architecture trade-offs, ADRs, katas | `references/architecture-tradeoffs.md` |
| Domain modeling (DDD) | `references/domain-modeling.md` |
| Time/scale/tradeoffs engineering | `references/sustainable-engineering.md` |
| ETC/DRY/orthogonality mindset | `references/pragmatic-etiquette.md` |
| Rewrite ladder (plain → library → one line) | `references/rewrite-ladder.md` |
| Proof-pass / type-safety verification | `references/type-safety.md` |
| TRIZ ↔ code bridge | `references/triz-for-code.md` |
