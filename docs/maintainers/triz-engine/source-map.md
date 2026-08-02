# Source Map

Provenance for the internal engine of `triz-coding-method`. Everything in
`engine/references/` is
**original operational rewriting** — checklists, procedures, decision tables. No
long passages were copied from the books; the books were used as conceptual
cross-checks only.

## Upstream repository used
Structured TRIZ prompts (XML) by the ccTOPP / TRIZ-prompt-engineering project (MIT
licensed). Files consulted and what was distilled from each:

| Repo file/folder | Concept distilled → our reference |
|---|---|
| `technical_triz/function_analysis/function_analysis.xml` | Tool→Action→Object, U/H, N/I/E grading, magic-wand test → `function-analysis.md` |
| `business_triz/function_analysis/non-engineer_function_analysis.xml` | simplified function analysis for services → `function-analysis.md`, `business-triz.md` |
| `technical_triz/root_cause_analysis/root_cause_analysis.xml` | RCA step framework, physical-parameter Too-High/Too-Low → `root-cause-analysis.md` |
| `technical_triz/root_conflict_analysis/*` | RCA+ tying causes to contradictions → `root-cause-analysis.md` |
| `technical_triz/contradiction_solver_40_inventive_principles/` (matrix + 40IP CSVs) | engineering contradiction form, 39 params, matrix, 40 principles → `contradiction-analysis.md`, `inventive-principles.md` |
| `technical_triz/physical_contradictions/Physical Contradictions and Separation Principles Prompt.xml` | physical contradiction form + 4 separations → `physical-contradictions.md` |
| `technical_triz/resource_analysis/*` (+ Derivative Resources) | 6 resource types, derived resources → `resource-analysis.md` |
| `technical_triz/ideality/ideality.xml` | ideality strategies, MATCHEMIB fields, ideal-system framing → `ideal-final-result.md`, `resource-analysis.md` |
| `technical_triz/trimming_and_trimming_rules/trimming_rules.xml` | trimming rules A/B/C + guidelines 1–4 → `trimming.md` |
| `technical_triz/system_operator/system_operator.xml` | 9 Windows grid → `system-operator.md` |
| `technical_triz/smart_little_people/*` | SLP method → `triz-method-map.md` |
| `technical_triz/function_oriented_search/*` | FOS / cross-industry transfer → `triz-method-map.md` |
| `technical_triz/76_standard_solutions/*` | standard-solutions pattern catalog (referenced, not expanded) → `triz-method-map.md` |
| `business_triz/business_solutions_at_system_levels/*` | super/sub-system solution mining → `business-triz.md` |
| `business_triz/business_perception_mapping/*` | perception → conflict → contradiction → `business-triz.md` |

## Published sources (conceptual reference only)
The works listed in `docs/bibliography.md` were consulted as conceptual
cross-checks only — no source text was copied. They informed the skill across
five areas:
- function-analysis, ideality, and business-application framing; "separate the
  best from the rest" → evaluation stage
- project-pipeline best practices; "always end with an experiment"
- common mistakes and operating rules ("don't skip a stage",
  method-over-inspiration)
- MCP/LLM integration direction; LLM-assisted FOS/MOS framing
- a small remainder consulted as spot cross-checks only (lightly mined)

## Concepts extracted (turned into operational notes)
Function modeling (T/A/O, U/H, N/I/E) · cause-effect chains & leverage points ·
engineering vs physical contradictions · the 4 separation principles · 40
inventive principles (with soft/business/software readings) · 6+ resource types &
derived resources · ideality equation & IFR · trimming rules A/B/C · 9 Windows ·
FOS/MOS · domain adaptations (business, software, rehab, mechanical,
datascience, marketing, supplychain, energy, education, construction,
robotics) — shipped as pure-data field branches under `branches/fields/`, each
with parameter translations and soft principle readings;
`references/use-cases.md` holds their worked examples
(original content, not book-derived).

## Limits / not yet analyzed
- The runtime includes only the normalized contradiction-matrix CSV and the
  standard-solutions JSON required by the tested CLI; the larger prompt corpus
  is not bundled.
- **76 Standard Solutions** is available as structured engine data, not copied
  upstream prose.
- German-language sources were skimmed, not deeply mined.
- Upstream PDFs and spreadsheets were not parsed or retained.
- No book text was copied; if a future version wants verbatim definitions, check licensing per book first.
