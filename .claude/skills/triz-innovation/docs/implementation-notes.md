# Implementation Notes

Design decisions and architecture for the `triz-innovation` skill. Read this
before extending it.

## Goals
- TRIZ as a **disciplined pipeline**, not creative brainstorming.
- Works across software, business, pricing, product, workflow, physio/rehab,
  clinic org, automation, and general technical/creative problems.
- Original operational synthesis from the source material — **no long book copies**.
- Local-first, testable; MCP/web deferred.

## Architecture
```
.claude/skills/triz-innovation/    # the single methodology folder
  SKILL.md            # core: operating rules + 10-stage pipeline + reference index
  TRIZ-MASTER.md      # the master knowledge base (24 sections)
  references/*.md     # 13 on-demand method notes (progressive disclosure)
  examples/*.md       # 4 fully-worked pipeline runs
  scripts/*.py        # stdlib MVP helpers
  mcp/                # stdlib MCP server
  docs/               # this file + usage-guide + source-map
cases/                # saved analyses (template + README + generated cases) — repo root
```

## Key decisions
1. **Progressive disclosure.** `SKILL.md` stays short and always loaded; deep
   method content lives in `references/` and is read only when a stage needs it.
   Keeps context cost low and routing fast.
2. **Single methodology folder, one source of truth.** The whole TRIZ
   methodology (skill + TRIZ-MASTER + docs + mcp) lives under
   `.claude/skills/triz-innovation/`. No mirror: any agent points at that folder.
3. **Contradiction matrix not embedded.** The full Altshuller matrix is large and
   already in the repo as CSVs; `contradiction-analysis.md` points to it on
   demand instead of bloating the skill.
4. **Scripts are heuristic MVPs, not engines.** The router uses transparent
   keyword/intent rules (easy to read and extend); the evaluator is a plain
   weighted-sum scorer; the case generator is a templater. No external deps so it
   runs anywhere Python 3.8+ exists.
5. **Architect/Carpenter split.** The knowledge content (SKILL.md, references,
   examples, docs) was authored directly by the Architect because LLM-synthesis
   of TRIZ method content needs domain accuracy. The three Python scripts were
   specified in `SPEC.md` and built/verified by the build loop with checkable
   acceptance criteria. (ADR-0011 pattern: don't delegate the parts the build
   engine is weak at.)

## Script contracts (so MCP wrapping is trivial later)
Keep each script's core logic in an importable function with a `__main__` guard:
- `triz_router.suggest_methods(problem: str) -> dict` (contradictions + ranked methods)
- `triz_case_template.create_case(title: str, cases_dir=...) -> Path`
- `triz_evaluator.score(rows: list[dict]) -> list[dict]` (+ a formatter)

## Extension points
- New method → `references/<topic>.md` + index row in `SKILL.md` + cues in
  `triz-method-map.md` + router keywords. Log it in `source-map.md`.
- New domain adaptation → another `*-triz.md` reference (mirror business/software/rehab).
- `references/standard-solutions.md` (76 standard solutions) is the most obvious
  next reference to add.

## Known limitations
- Router is keyword-based: it can misroute paraphrased problems; it's a *first
  guess*, the skill still reasons. Improve with more cues, not a model.
- Evaluator weights are equal by default; domain-specific weighting is a future option.
- No MCP server, no web UI, no GUI — intentionally out of scope for v1.
- Non-English (esp. German) sources only lightly mined — see `source-map.md`.
