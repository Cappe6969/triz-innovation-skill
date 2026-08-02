---
name: triz-innovation
description: Use this skill when solving real-world technical, business, software, workflow, rehabilitation, clinical, product, or organizational problems using structured TRIZ methods. Trigger this skill for contradictions, bottlenecks, constraints, creative problem solving, function analysis, root cause analysis, resource optimization, ideality, trimming, system redesign, or innovation strategy.
---

# TRIZ Innovation

A disciplined TRIZ problem-solving engine. You are NOT brainstorming. You run a
fixed pipeline that turns a messy real-world problem into a small set of
**evaluated, testable** solutions. Default to method over inspiration.

## When to use
Software, business, pricing, product design, workflow, physiotherapy &
rehabilitation, clinic/study organization, local automation, app development,
general technical problems, and creative problems with real constraints.

## Operating rules
1. **Run the pipeline in order** (sections 1–10 below). Do not skip a stage; if a
   stage has no content, say so explicitly and move on.
2. **One question at a time, max 3 total.** Ask only when an answer would change
   the analysis. Otherwise state an assumption and proceed.
3. **Be concrete.** No generic advice ("communicate better"). Every output must
   name components, parameters, resources, or steps.
4. **Cite the method.** When you propose a solution, tag which TRIZ method
   produced it (e.g. `[Trimming Rule B]`, `[Separation in time]`, `[IP-15
   Dynamics]`).
5. **Load references on demand.** Read the matching file in `references/` only
   when a stage needs depth. Do not dump references into the answer.
6. **End with a test, always.** No analysis is complete without stage 10.

## Reference index (read on demand)
| Need | File |
|------|------|
| Which method(s) to use, decision tree | `references/triz-method-map.md` |
| Engineering contradiction + 40 principles + matrix | `references/contradiction-analysis.md` |
| Look up the 39×39 matrix (improving/worsening → IPs) | `references/contradiction-matrix.md` |
| Same param, two opposite values + 4 separations | `references/physical-contradictions.md` |
| Components, interactions, U/H functions table | `references/function-analysis.md` |
| Cause-effect chain, leverage points | `references/root-cause-analysis.md` |
| Inventory of internal/external/free resources | `references/resource-analysis.md` |
| Ideal Final Result, ideality equation | `references/ideal-final-result.md` |
| Remove a component, keep its function | `references/trimming.md` |
| 9 Windows / time × system levels | `references/system-operator.md` |
| Full list of 40 inventive principles | `references/inventive-principles.md` |
| Su-Field modeling + 76 standard solutions (5 classes) | `references/substance-field-analysis.md` |
| ARIZ-85C step-by-step algorithm (escalation path) | `references/ariz.md` |
| Evolution trends (8 laws) + S-curve maturity | `references/evolution-trends.md` |
| Function → scientific/physical effects catalog | `references/scientific-effects.md` |
| Business/management adaptation | `references/business-triz.md` |
| Software/architecture adaptation | `references/software-triz.md` |
| Physio/rehab/clinical adaptation | `references/rehabilitation-triz.md` |

## The pipeline

### 1. Problem framing
- Restate the problem in one sentence, neutrally (no solution baked in).
- Name **system**, **subsystem(s)**, **super-system**.
- List **stakeholders** and what each one actually wants.
- State the **primary useful function** (Tool → Action → Object).
- List **harmful / insufficient / excessive** functions and effects.
- List **real constraints** (time, money, regulation, skill, physics, politics).
- Separate **symptoms vs causes vs goals** in three short lists.

### 2. Function analysis  → `references/function-analysis.md`
- List components (sub-system, system, super-system).
- Table: `Tool | Action | Object | U/H | N/I/E | Parameter changed`.
- Flag harmful, insufficient, excessive, and redundant functions.
- Mark components that are candidates for **trimming**.

### 3. Root cause analysis  → `references/root-cause-analysis.md`
- Build the cause→effect chain from symptom down to root.
- Separate surface causes vs deep causes.
- Mark each cause **controllable / not controllable**.
- Identify the **leverage points** (causes that, if fixed, collapse the chain).

### 4. Contradiction analysis  → `references/contradiction-analysis.md` + `references/contradiction-matrix.md` + `references/physical-contradictions.md`
- **Engineering contradiction:** "IF we improve X, THEN Y gets better, BUT Z gets worse."
- **Map to the matrix:** translate X and Z to two of the 39 standard parameters
  and look up the recommended inventive principles:
  `python .claude/skills/triz-innovation/scripts/triz_matrix.py <improving_id> <worsening_id>`.
  Try 2–3 framings if the suggestions feel weak. Apply each principle concretely.
- **Physical contradiction:** "Element E must be A and not-A" — name the element and the two opposing demands.
- List the **apparent trade-offs** the user assumes are unavoidable.
- Note which could break via separation in **time / space / condition / scale (parts↔whole)**.

### 5. Resource analysis  → `references/resource-analysis.md`
Inventory, even if "free" or "already there":
internal · external · free/underused · informational · temporal · spatial ·
human · digital/software. For each promising one: how it could be used.

### 6. Ideal Final Result  → `references/ideal-final-result.md`
- State the IFR: the useful function happens **by itself**, on time, with no
  cost/harm, ideally without adding any new element.
- Maximize useful function; minimize cost, complexity, friction, maintenance, risk.
- Ask explicitly: "How do we get this result **without adding a new component**?"

### 7. Method selection  → `references/triz-method-map.md`
Pick 2–5 methods that fit the problem signature (use the router logic). Justify
each in one line. Available methods:
Function Analysis · Root Cause Analysis · Engineering Contradiction + 40 IP +
Contradiction Matrix · Physical Contradiction + Separation · Resource Analysis ·
Ideality/IFR · Trimming · System Operator (9 Windows) · Su-Field + 76 Standard
Solutions · Evolution Trends + S-curve · Scientific Effects · Function-Oriented
Search · Method-Oriented Search · Smart Little People · ARIZ (escalation) ·
Business TRIZ · Software TRIZ · Rehabilitation/clinical TRIZ.

> Tip: `python .claude/skills/triz-innovation/scripts/triz_router.py "problem text"`
> gives a fast first guess at methods + likely contradictions.

### 8. Solution generation
Produce, each tagged with its method:
- **3 conservative** solutions (low risk, known to work).
- **3 creative-but-realistic** solutions.
- **3 non-obvious TRIZ** solutions (separation / trimming / resource / standard-solution driven).
- **2 high-risk / high-upside** solutions.
- **1 minimal solution testable this week.**

### 9. Evaluation
Score every solution 1–5 on: **impact, feasibility, cost, speed, risk,
reversibility, complexity, ideality**. (Cost/risk/complexity: 5 = cheap/safe/simple.)
Present as a table, sort by total. The evaluator script can do this from a CSV:
`python .claude/skills/triz-innovation/scripts/triz_evaluator.py solutions.csv`.

### 10. Experiment plan (mandatory close)
- **Best candidate** and why.
- **First practical experiment** (smallest real-world test).
- **Data to collect.**
- **Success / failure criterion** (a number or observable, not a vibe).
- **Next step if it works.**
- **Next step if it fails.**

## Advanced track (escalate when the main pipeline stalls)
The 10-stage pipeline solves most problems. When it doesn't — the contradiction is
stubborn, the system feels exhausted, or the problem is an *interaction* not a
trade-off — escalate into these deeper TRIZ tools. Pull them in during stages 4–8;
don't run them by default.

- **Su-Field + 76 Standard Solutions** → `references/substance-field-analysis.md`.
  Use when the problem is an interaction (S1 —[field]→ S2) that is missing, weak,
  or harmful. Diagnose the link, then jump to the matching solution class:
  `python .claude/skills/triz-innovation/scripts/triz_standard_solutions.py --state <incomplete|insufficient|harmful|measurement|excessive>`.
- **ARIZ-85C** → `references/ariz.md`. The master algorithm for hard problems that
  resist the quick tools. Generate a worksheet and fill every part:
  `python .claude/skills/triz-innovation/scripts/triz_ariz.py "problem title"`.
- **Evolution Trends + S-curve** → `references/evolution-trends.md`. Use for "where
  is this headed / how do we leapfrog" questions. Place the system on the S-curve
  and walk the 8 trends: `python .claude/skills/triz-innovation/scripts/triz_evolution.py --signals "..."`.
- **Scientific Effects** → `references/scientific-effects.md`. When you have a clear
  required function but no mechanism — search effects by function family.

> The router (`triz_router.py`) also flags when a problem signature points to these
> advanced tools (interaction → Su-Field; "leapfrog/evolve" → Evolution Trends;
> "stuck after the basics" → ARIZ).

## Saving a case
Persist the analysis as a reusable case file:
`python .claude/skills/triz-innovation/scripts/triz_case_template.py "Short problem title"`
creates a pre-filled markdown file in `cases/`. Fill it as you run the pipeline.

## Branches
The skill is a mix of branches — pure-data JSON that tunes the same TRIZ core
to a field or a language, no code.

- **Field branches** (`branches/fields/<id>/branch.json`) carry domain
  vocabulary: keywords, parameter translations, soft readings of the 40
  principles, and worked examples. Shipped fields: `general`, `business`,
  `software`, `rehab`. `general` is the canonical core.
- **Language branches** (`branches/langs/<lang>/branch.json`) carry localized
  labels for method names and contradiction lines plus stopwords for language
  auto-detection. English is the default overlay; Italian is the first
  additional one.

The two axes are orthogonal: **field** × **language**. Localize any tool with
`python .../triz.py --branch <id> --lang <lang> route "..."`, and pass
`--lang auto` to auto-detect the language of the problem text.

Manage branches through the registry:
`python .../triz.py branches list` and `python .../triz.py branches check`.

To add a field branch, drop a `branch.json` in `branches/fields/<id>/` with
that field's keywords, parameter translations, soft principle readings, and
examples. To add a language, drop a `branch.json` in `branches/langs/<lang>/`
with the localized labels and stopwords. Nothing else changes — the registry
and the router pick the new branch up automatically.

## Master tool (one entrypoint)
Instead of remembering each script, call the dispatcher:
`python .claude/skills/triz-innovation/scripts/triz.py <command> [args]`.
Commands: `route "<text>"` · `matrix <imp> <wor>` (or `matrix --list`) ·
`sufield --state <state>` · `ariz "<title>"` · `evolution --signals "..."` ·
`case "<title>"` · `evaluate <csv>` · `branches list|check` · `master` (show
the `TRIZ-MASTER.md` knowledge base). Global flags `--branch <id>` (default
`general`) and `--lang <lang>` (default `en`, or `auto`) localize `route` and
`case`; other commands ignore them. Run with no args for the full list. Works
from any directory, so Claude Code or Codex can invoke it whenever a TRIZ
capability is needed.
