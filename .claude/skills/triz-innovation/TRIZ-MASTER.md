# TRIZ Master Knowledge Base

> **Canonical source.** This document is the single, coherent body of TRIZ knowledge from which the `triz-innovation` skill (and future skills) are derived. Think of it as the textbook; the skill files are the quick-reference cards cut from it. Every method, checklist, principle, and procedure lives here first.

### Table of Contents

- [0. How to use this document](#0-how-to-use-this-document)
- [1. TRIZ foundations](#1-triz-foundations)
- [2. The problem-solving pipeline](#2-the-problem-solving-pipeline)
- [3. Function analysis](#3-function-analysis)
- [4. Root cause analysis](#4-root-cause-analysis)
- [5. Engineering contradictions, the 39 parameters & the contradiction matrix](#5-engineering-contradictions-the-39-parameters--the-contradiction-matrix)
- [6. The 40 inventive principles](#6-the-40-inventive-principles)
- [7. Physical contradictions & the 4 separation principles](#7-physical-contradictions--the-4-separation-principles)
- [8. Resource analysis](#8-resource-analysis)
- [9. Ideal Final Result & ideality](#9-ideal-final-result--ideality)
- [10. Trimming](#10-trimming)
- [11. System operator (9 Windows)](#11-system-operator-9-windows)
- [12. Substance-field analysis & the 76 standard solutions](#12-substance-field-analysis--the-76-standard-solutions)
- [13. ARIZ-85C](#13-ariz-85c)
- [14. Evolution trends & the S-curve](#14-evolution-trends--the-s-curve)
- [15. Scientific effects](#15-scientific-effects)
- [16. Function-Oriented Search & Method-Oriented Search](#16-function-oriented-search--method-oriented-search)
- [17. Smart Little People](#17-smart-little-people)
- [18. Business TRIZ](#18-business-triz)
- [19. Software TRIZ](#19-software-triz)
- [20. Rehabilitation & clinical TRIZ](#20-rehabilitation--clinical-triz)
- [21. Tooling](#21-tooling)
- [22. Derivation map](#22-derivation-map)
- [23. Provenance & sources](#23-provenance--sources)

---

## 0. How to use this document

This document is the **canonical TRIZ body of knowledge** for this repository. It consolidates all TRIZ methods, principles, parameters, patterns, and procedures into one organized reference. The `triz-innovation` skill and its supporting files are derived from this master — they are the condensed, operational quick-reference cards; this is the full textbook.

**How to read it:**
- **New to TRIZ:** Read sections 0–2 for orientation, then jump to any method section (3–20) as your problem dictates.
- **Running the skill:** The pipeline in section 2 is your execution order. Each pipeline stage points to the method section that backs it.
- **Looking up a specific tool:** Use the Table of Contents above. Every section is self-contained — read it, apply it, come back for the next.
- **Tracing provenance:** Section 22 (Derivation map) shows exactly which source files feed each section. Section 23 (Provenance) credits all sources.

The document is designed for **method over inspiration**. TRIZ is a disciplined problem-solving system, not brainstorming. Every method here has a defined procedure, a problem signature that tells you when to use it, and a concrete example.

---

## 1. TRIZ foundations

TRIZ (Teoriya Resheniya Izobretatelskikh Zadach — "Theory of Inventive Problem Solving") is a systematic innovation methodology developed by Genrich Altshuller and his colleagues, beginning in 1946. After analysing hundreds of thousands of patents, Altshuller discovered that:

1. **Problems and solutions repeat across industries and sciences.** The same fundamental contradiction appears in mechanical engineering, chemistry, software, and business. A solution that worked in one field can be adapted to another.
2. **Patterns of technical evolution repeat.** Systems do not evolve randomly; they follow predictable trends. Knowing where a system sits on those trends lets you predict its next move.
3. **Innovation uses scientific effects outside their original field.** Most breakthrough inventions apply a physical, chemical, or geometric effect that was already known — just not in that context.

### Method over inspiration

TRIZ replaces "have a bright idea" with a **repeatable process**. Instead of brainstorming randomly, you:
- Model the problem as functions and contradictions.
- Map those contradictions to standardized parameters.
- Look up which inventive principles resolved similar contradictions across millions of patents.
- Apply those principles to your specific system.

This is the opposite of "think harder." It is **structured knowledge reuse**.

### Ideality — the central idea

Every system evolves toward **higher ideality**: more useful function per unit of cost, harm, and complexity. The Ideal Final Result (IFR) is the theoretical endpoint where the function is delivered perfectly, by itself, with zero cost and zero harm — ideally without the system even existing as a separate thing.

```
                Σ Useful functions
Ideality  =  ───────────────────────────────
             Σ Costs  +  Σ Harms  +  Σ Complexity
```

All TRIZ tools push in this direction: raise the numerator (add useful function) while shrinking the denominator (cut cost, cut harm, cut complexity). The most TRIZ-like move is to do both at once — usually by trimming or by using an existing resource.

### Contradictions — the engine of invention

Altshuller's key insight: **breakthrough solutions resolve contradictions, they don't compromise between them.** A contradiction is a situation where improving one thing degrades another. There are two kinds:

- **Engineering (technical) contradiction:** Two different parameters conflict. "If we make the wall thicker (improving strength), the part gets heavier (worsening weight)." Resolved by the contradiction matrix and the 40 inventive principles.
- **Physical contradiction:** One element must have two opposite states. "The notification must be present (to drive adherence) and absent (to avoid annoyance)." Resolved by the four separation principles.

The difference matters: an engineering contradiction is between *two parameters*; a physical contradiction is *one parameter with two opposite required values*. Many engineering contradictions, when pushed to their extreme, reduce to a physical contradiction — and physical contradictions are often easier to solve.

### The TRIZ toolset (summary)

| Tool | What it does |
|------|-------------|
| Function Analysis | Models the system as Tool → Action → Object; finds what to fix, trim, or strengthen |
| Root Cause Analysis | Chains symptom → root; finds the leverage point where intervention pays most |
| Contradiction Matrix + 40 Principles | Resolves engineering trade-offs using historically validated principle shortlists |
| Separation Principles (4) | Resolves physical contradictions by separating opposite demands in time, space, condition, or scale |
| Resource Analysis | Inventories everything already present and free before adding anything new |
| Ideality / IFR | Defines the perfect outcome; works backward to find what must be true |
| Trimming | Removes a component while keeping its useful function, handed to something that remains |
| System Operator (9 Windows) | Fights tunnel vision by examining sub/system/super × past/present/future |
| Su-Field Analysis + 76 Standards | Models interactions as S1—[field]→S2; fixes missing, weak, or harmful interactions |
| ARIZ | The master algorithm for hard problems that resist the quick tools |
| Evolution Trends + S-Curve | Predicts where a system is headed; identifies the next leap |
| Scientific Effects | Searches function → proven physical/chemical/behavioral mechanisms |
| FOS / MOS | Finds solutions by searching across industries for the same function or the same method |
| Smart Little People | Models a problem with imaginary agents to escape psychological inertia |
| Domain adaptations | Business TRIZ, Software TRIZ, Rehabilitation/Clinical TRIZ — same tools, domain vocabulary |

---

## 2. The problem-solving pipeline

The TRIZ innovation skill runs a fixed 10-stage pipeline. Each stage feeds the next; skipping stages produces shallow solutions. The pipeline is designed so that a messy real-world problem enters at stage 1 and a set of evaluated, testable solutions exits at stage 10.

1. **Problem framing** — Restate the problem neutrally; name system, subsystem, super-system; list stakeholders, primary useful function, harmful/insufficient/excessive effects, real constraints; separate symptoms from causes from goals.
2. **Function analysis** — Model the system as Tool → Action → Object; grade every function Useful/Harmful and Normal/Insufficient/Excessive; flag trimming candidates.
3. **Root cause analysis** — Build the cause→effect chain from symptom to root; classify every cause (surface/deep, controllable/not, contradiction-behind-it); identify leverage points.
4. **Contradiction analysis** — State engineering contradictions (IF improve X, THEN Y better BUT Z worse); map to the 39 parameters and the matrix; state physical contradictions (element must be A and not-A); test all four separations.
5. **Resource analysis** — Inventory internal, external, free/underused, informational, temporal, spatial, human, and digital resources; star the 3–5 most relevant.
6. **Ideal Final Result** — State the IFR: the function happens by itself, on time, with no added cost/harm/component; ask "how do we get this without adding a new element?"
7. **Method selection** — Pick 2–5 TRIZ methods that fit the problem signature; justify each in one line. Use the decision table (section 16) or the router script for a fast first guess.
8. **Solution generation** — Produce 3 conservative, 3 creative-but-realistic, 3 non-obvious TRIZ, 2 high-risk/high-upside, and 1 minimal testable-this-week solution. Tag every solution with its method.
9. **Evaluation** — Score every solution 1–5 on impact, feasibility, cost, speed, risk, reversibility, complexity, ideality. (Cost/risk/complexity: 5 = cheap/safe/simple.) Present as a table sorted by total.
10. **Experiment plan** — Name the best candidate, the first practical experiment, the data to collect, the success/failure criterion (a number, not a vibe), and next steps for both outcomes.

### Advanced escalation track

When the main pipeline stalls — the contradiction is stubborn, the system feels exhausted, or the problem is an *interaction* not a trade-off — escalate into these deeper tools during stages 4–8:

- **Su-Field + 76 Standard Solutions** — for interaction problems (missing, weak, or harmful S1—[field]→S2 links).
- **ARIZ-85C** — the master algorithm; reformulates a stubborn problem until the core contradiction becomes resolvable.
- **Evolution Trends + S-curve** — for "where is this headed / how do we leapfrog" questions.
- **Scientific Effects** — when you have a clear required function but no mechanism.

The pipeline is designed to be run in order and in full. Skipping stages produces shallow solutions; the discipline of completing each stage before moving on is what separates TRIZ from brainstorming.

### Operating rules (from SKILL.md)

These rules govern how the skill executes the pipeline. They are the behavioral contract for any TRIZ session:

1. **Run the pipeline in order** (stages 1–10 above). Do not skip a stage; if a stage has no content, say so explicitly and move on.
2. **One question at a time, max 3 total.** Ask only when an answer would change the analysis. Otherwise state an assumption and proceed.
3. **Be concrete.** No generic advice ("communicate better"). Every output must name components, parameters, resources, or steps.
4. **Cite the method.** When you propose a solution, tag which TRIZ method produced it (e.g. `[Trimming Rule B]`, `[Separation in time]`, `[IP-15 Dynamics]`).
5. **Load references on demand.** Read the matching file in `references/` only when a stage needs depth. Do not dump references into the answer.
6. **End with a test, always.** No analysis is complete without stage 10.

### Saving a case

Persist the analysis as a reusable case file: `python .claude/skills/triz-innovation/scripts/triz_case_template.py "Short problem title"` creates a pre-filled markdown file in `cases/`. Fill it as you run the pipeline.

---

## 3. Function analysis

**When to use:** The problem is "what even is going on here?" — the system is complex, has many interacting parts, or the real issues are unclear. Also the mandatory prerequisite for trimming.

**Core idea:** Model the system as **functions**, not parts. A function is one component (the **tool**) performing an **action** that changes or holds a **parameter** of another component (the **object**). This exposes exactly what to fix, what to remove, and what to strengthen. The magic-wand test: if you delete the tool and the object changes, a function exists. If nothing changes, it's not a real function — drop it.

**Procedure:**
1. **Component analysis (3 levels):** List the super-system (things outside you interact with), the system (the thing being improved), and sub-systems (its internal parts).
2. **Build the function table:** For every interaction, fill: `Tool | Action | Object | U/H | N/I/E | Parameter changed/held`. U/H = Useful or Harmful. For useful functions: N = Normal, I = Insufficient, E = Excessive. Harmful functions get `---` for N/I/E. Identify the **main function** first — the one that changes the target object in the super-system (the reason the system exists).
3. **Read the table for opportunities:**
   - Harmful (H) functions → eliminate, block, or convert to useful (trimming / contradiction).
   - Insufficient (I) → strengthen the tool or add a resource.
   - Excessive (E) → throttle / make dynamic (often hides a contradiction).
   - Redundant functions (two tools doing the same job) → trim one.
   - Trimming candidates: any tool whose function could be done by the object itself or by another existing component.

**Example:** A reminder app — Tool: *push notification*, Action: *prompts*, Object: *patient*, U/H: U, N/I/E: I (adherence still low). Harmful twin: *push notification annoys patient* (H). Trimming candidate: the phone's calendar already nudges — could the calendar take over the prompt function?

**Output:** A filled function table + a 3-bullet summary: main function (and its N/I/E grade), the worst harmful function, and the top trimming candidate.

**Derives →** `references/function-analysis.md`

---

## 4. Root cause analysis

**When to use:** "Why does this keep happening?" — recurring failures, intermittent problems, or any situation where you suspect you're treating symptoms rather than the disease.

**Core idea:** Trace the symptom down to the **root cause(s)** so you fix the disease, not the fever. In TRIZ this feeds straight into contradiction analysis: the best place to break a chain is where a cause sits behind a contradiction. A **leverage point** is a controllable cause that, if removed, collapses the most downstream effects. Prefer leverage points that are upstream (kill many effects at once), controllable, and cheap to act on.

RCA+ (developed by Valeri Souchkov) extends classical RCA in two fundamental ways: (1) it identifies **contradiction causes** — causes that produce both a negative and a positive effect, so they cannot be simply eliminated; (2) it targets contradictions **closer to the problem** rather than drilling to the deepest root, which yields more ideal solutions. RCA+ classifies causes into four types: **N** (purely negative — eliminate it), **N+P** (negative + positive — a contradiction cause requiring inventive resolution), **NC** (non-changeable — beyond your control), and **P** (positive effect of an N+P cause). Every cause must be stated as a sentence (function, relative parameter value, change of property, or radical state change), never a single word. Causes combine via **AND** (all required together; removing any one eliminates the effect) or **OR** (each contributes independently).

**Procedure:**
1. **Anchor the symptom:** State the observable problem as a measurable effect. Classify it: negative effect (something happens that we don't want), insufficient effect (desired result not achieved with required performance), excessive effect (wastes too much of a costly resource), or ineffective control (control process too slow/inaccurate/unreliable).
2. **Build the cause–effect chain:** Repeatedly ask "What causes this effect to occur?" — not "Why?" Allow branching (a node can have multiple contributing causes). State every cause as a complete sentence (function; relative parameter value; change of property; radical state change) and mark it **factual** (verified by data/observation) or **assumptive** (hypothesis requiring verification). Apply the **"stop at first contradiction cause" rule**: stop a branch at an N+P cause, an NC cause, or an unchangeable requirement — do NOT drill deeper below an N+P cause; the deeper causes only explain why its positive effect exists, so hand it to contradiction analysis instead.
3. **Classify every cause:** Tag each node as N (purely negative), N+P (contradiction cause — has both a positive and negative effect), NC (non-changeable), or P (positive effect of N+P). Also tag surface vs deep, factual vs assumptive, and check AND vs OR relationships — in a specific known system causes are usually AND-related (all required; removing any one collapses the effect), while broad failure prevention across varied conditions tends to be OR-related (each contributes independently).
4. **Find leverage points:** Rank causes by *(reach × controllability ÷ cost)* and pick the top 1–2. Closer to the top is generally preferred; system-level causes are preferred over super-system causes (easier to change).
5. **Convert to a problem to solve:** For N-type causes → "How to eliminate/prevent [cause]?" For N+P causes → formulate as a technical contradiction ("How to ensure [cause] to enable [positive effect] but avoid [negative effect]?") and as a physical contradiction ("[Cause] should be present/high/strong to [positive effect] AND should be absent/low/weak to avoid [negative effect].").

**Example:** "Patients stop doing exercises after week 2." Why? → Reminders feel annoying. Why? → They fire at random times. Why? → We don't know the patient's active hours. Leverage point: the unknown active window — an N-type cause (purely negative; no positive effect from not knowing). Solvable problem: "How do we learn or infer the active window without asking?" If the patient's fixed schedule were an N+P cause (it keeps them consistent but also makes them rigid and miss flexible opportunities), that would be handed to contradiction analysis.

**RCA+ classification decision tree:** Does the cause also produce a positive/useful effect? → **N+P** — stop, document the positive effect, hand to contradiction analysis. Else can we eliminate or change it? → **N** — keep drilling deeper. Else (beyond control) → **NC** — stop, treat as a boundary condition. Tag N+P causes' beneficial side-effects as **P**.

**Pitfalls:** single-line chains (you've missed AND branches) · one-word causes ("pressure" is a parameter, not a cause) · blame-the-user terminal nodes · expanding below an N+P cause · accepting NC too early ("too expensive" is not "non-changeable").

**Derives →** `references/root-cause-analysis.md`

---

## 5. Engineering contradictions, the 39 parameters & the contradiction matrix

**When to use:** "Improving A makes B worse" — any trade-off or apparent either/or choice. This is the most common TRIZ entry point.

**Core idea:** An engineering (technical) contradiction is two parameters in conflict: improving one degrades the other. TRIZ resolves it without compromise by mapping the two parameters to standardized ones, looking up which inventive principles historically resolved that exact trade-off, and applying those principles to your specific system.

### The 39 engineering parameters

These are the standardized abstractions used to describe any engineering trade-off. Map your concrete "improving" and "worsening" factors to the closest standard parameter — an approximate match is expected and sufficient.

| # | Parameter | # | Parameter | # | Parameter |
|---|-----------|---|---|-----------|---|-----------|
| 1 | Weight of moving object | 14 | Strength | 27 | Reliability |
| 2 | Weight of stationary object | 15 | Duration of action of moving object | 28 | Measurement accuracy |
| 3 | Length of moving object | 16 | Duration of action of stationary object | 29 | Manufacturing precision |
| 4 | Length of stationary object | 17 | Temperature | 30 | Object-affected harmful factors |
| 5 | Area of moving object | 18 | Illumination intensity | 31 | Object-generated harmful factors |
| 6 | Area of stationary object | 19 | Use of energy by moving object | 32 | Ease of manufacture |
| 7 | Volume of moving object | 20 | Use of energy by stationary object | 33 | Ease of operation |
| 8 | Volume of stationary object | 21 | Power | 34 | Ease of repair |
| 9 | Speed | 22 | Loss of energy | 35 | Adaptability or Versatility |
| 10 | Force (Intensity) | 23 | Loss of substance | 36 | Device complexity |
| 11 | Stress or pressure | 24 | Loss of information | 37 | Difficulty of detection |
| 12 | Shape | 25 | Loss of time | 38 | Extent of automation |
| 13 | Stability of the object composition | 26 | Quantity of substance | 39 | Productivity |

### Using the contradiction matrix

**Procedure:**
1. **Frame the contradiction in plain language.** "If we increase wall thickness (improve strength), the part gets heavier (weight worsens)."
2. **Map to parameters.** Pick the closest match for what improves and what worsens. "Moving" vs "stationary" matters — choose by whether the element changes position during operation.
3. **Look up the cell.** Run `python .claude/skills/triz-innovation/scripts/triz_matrix.py <improving_id> <worsening_id>`. The matrix returns a shortlist of inventive principle numbers.
4. **Apply each principle concretely.** Read the principle in section 6; force a specific interpretation onto your system. Tag solutions `[IP-NN name]`.
5. **If results feel weak, re-map.** Try 2–3 different parameter framings of the same problem. Different framings yield different principle suggestions.

**Important caveats:**
- When improving and worsening are the same parameter, the matrix says "see physical contradiction" — switch to section 7.
- Empty cells: fall back to Resource Analysis + IFR.
- For business/software/clinical problems, translate: "weight" → overhead/payload, "speed" → latency/throughput, "reliability" → uptime/adherence, "force" → load/pressure on a team.

**Example:** Onboarding needs more validation (improve reliability) but each step adds signup friction (loss of time). Improving = 27 Reliability, worsening = 25 Loss of time. The matrix returns principles like 10 (Preliminary Action), 30 (Flexible Shells), 4 (Asymmetry) — run `python triz_matrix.py 27 25` for the live answer, which is authoritative. Interpretation: pre-verify identity in the background before the user arrives, so the visible flow stays short. Tag: `[IP-10 Preliminary Action]`.

**Derives →** `references/contradiction-analysis.md`, `references/contradiction-matrix.md`

---

## 6. The 40 inventive principles

**When to use:** After a contradiction is framed and the matrix (or your judgment) suggests which principles to try. Each principle is a solution *pattern* — you must translate it into a concrete change for your specific system.

**Core idea:** Altshuller extracted 40 recurring solution patterns from hundreds of thousands of patents. These are the "grammar" of invention — the same patterns appear across every field. Apply them by asking: "How would this principle manifest in my system?"

**Procedure:**
1. **Frame the contradiction** — as an engineering contradiction (§5) or a physical contradiction (§7).
2. **Get candidate principles** — look up the matrix cell (step 3 of §5) for engineering contradictions, or pull the matching separation principle for physical ones.
3. **Translate concretely** — read each candidate and force a specific interpretation: "How would this pattern manifest in my system?" Push every principle through the *soft* readings until it names a real change, not a slogan.
4. **If the shortlist feels weak** — walk the "most universally useful" list (1, 2, 3, 10, 13, 15, 25, 35) or re-map the parameters (§5) to a different framing.
5. **Tag every proposed change** `[IP-NN Name]`.

### Complete list of the 40 inventive principles

1. **Segmentation** — divide into independent parts. *Soft:* microservices, modular pricing, split a workout into micro-sessions.
2. **Taking out** — extract the troublesome/needed part only. *Soft:* move a feature out of the core; remove the nagging channel, keep the nudge.
3. **Local Quality** — make parts non-uniform, each optimal for its role. *Soft:* per-segment UX, per-patient-phase protocol.
4. **Asymmetry** — replace symmetry with asymmetry. *Soft:* asymmetric rate limits, tiered access.
5. **Merging** — combine parallel operations/objects. *Soft:* batch jobs, bundle services, combine intake + assessment.
6. **Universality** — one part does multiple functions. *Soft:* a single field serves logging + analytics; one session covers exercise + assessment.
7. **Nesting** — put one thing inside another. *Soft:* embedded widgets, progressive disclosure, plan-within-plan.
8. **Anti-weight** — offset a downside with an upside. *Soft:* pair an annoying-but-needed step with a reward.
9. **Preliminary Anti-action** — pre-empt a harmful effect before it happens. *Soft:* input validation up front; warm up before load.
10. **Preliminary Action** — do part of the work in advance. *Soft:* precompute/cache; pre-fill forms; pre-schedule reminders at the active hour.
11. **In-advance Cushioning** — prepare emergency backups. *Soft:* retries, fallbacks, safety-net flows, relapse plan.
12. **Equipotentiality** — remove the need to fight a constraint. *Soft:* remove a step rather than optimize it; meet the patient where they are.
13. **The Other Way Around** — invert the action. *Soft:* pull instead of push (user requests vs app nags); patient teaches the exercise back.
14. **Spheroidality and Curvature** — use curves/rolling instead of straight/linear. *Soft:* iterative loops instead of linear pipelines.
15. **Dynamization** — let it adapt/change over time/conditions. *Soft:* adaptive frequency, autoscaling, difficulty that adjusts to progress.
16. **Partial or Excessive Actions** — if 100% is hard, do a bit less or a bit more. *Soft:* MVP; deliberate over-provisioning; "good enough" dosing.
17. **Transition to Another Dimension** — move into a new axis/layer. *Soft:* 2D→3D, add an async layer, use space/time you weren't using.
18. **Mechanical Vibration** — use rhythm/pulses. *Soft:* periodic pings, spaced repetition, interval training.
19. **Periodic Action** — replace continuous with pulsed. *Soft:* digest emails instead of per-event; scheduled rather than constant reminders.
20. **Continuity of Useful Action** — eliminate idle time, keep it working. *Soft:* background sync, fill dead time in a workflow.
21. **Skipping** — do a harmful step very fast to limit damage. *Soft:* fast-path a risky operation; brief intense bursts.
22. **Blessing in Disguise** — turn a harm into a benefit. *Soft:* use the error signal as a feature; use annoyance data to throttle.
23. **Feedback** — introduce/strengthen feedback. *Soft:* progress bars, adherence dashboards, closed-loop control.
24. **Intermediary** — use a go-between/carrier. *Soft:* a broker/queue; a caregiver as the channel to the patient.
25. **Self-service** — the system serves itself / object does the work. *Soft:* self-healing, self-logging, patient self-monitoring. (Most ideal direction.)
26. **Copying** — use a cheap copy instead of the real/costly thing. *Soft:* simulations, mockups, video demo instead of live coaching.
27. **Cheap Short-living Objects** — replace an expensive durable thing with cheap disposables. *Soft:* ephemeral environments, disposable test data.
28. **Mechanics Substitution** — swap to fields (optical/acoustic/etc.) or other means. *Soft:* replace a manual mechanism with a sensor/signal.
29. **Pneumatics and Hydraulics** — use flexible/fluid media. *Soft:* elastic/buffered flows, flexible scheduling.
30. **Flexible Shells and Thin Films** — use thin flexible boundaries. *Soft:* lightweight wrappers, thin adapters, minimal UI overlays.
31. **Porous Materials** — add holes/permeability. *Soft:* selective filters, permeable permissions, optional steps.
32. **Color Changes** — change visibility/appearance/a property. *Soft:* color-coded states, highlight changes, status badges.
33. **Homogeneity** — make interacting things from the same material. *Soft:* consistent data formats, one stack, shared vocabulary with patient.
34. **Discarding and Recovering** — remove what's done; restore what's needed. *Soft:* garbage collection, sunset features, taper a therapy.
35. **Parameter Changes** — change state/concentration/flexibility/temperature. *Soft:* change a setting/threshold; change dose, intensity, cadence.
36. **Phase Transitions** — exploit changes of state. *Soft:* batch↔stream, sync↔async, sudden mode switches.
37. **Thermal Expansion** — use expansion/contraction with conditions. *Soft:* scale resources with load/season.
38. **Strong Oxidants** — intensify the active element. *Soft:* concentrate effort where it pays; enriched onboarding.
39. **Inert Atmosphere** — replace the environment with a calmer one. *Soft:* sandbox, quiet hours, distraction-free mode.
40. **Composite Materials** — combine different materials for the best of each. *Soft:* hybrid approaches, polyglot systems, blended care (in-person + app).

**Most universally useful when stuck:** 1, 2, 3, 10, 13, 15, 25, 35.

**Example:** A hospital needs to reduce infection rates (improving reliability) without adding cost (worsening device complexity). Apply IP-2 Taking out: move hand-sanitizer dispensers to the exact points where contamination happens (doorways, bedside) rather than mounting them everywhere. Apply IP-25 Self-service: make dispensers visible and easy to trigger so staff use them without thinking, making hygiene self-reinforcing. Tag: `[IP-2 Taking out]`, `[IP-25 Self-service]`.

**Derives →** `references/inventive-principles.md`

---

## 7. Physical contradictions & the 4 separation principles

**When to use:** "It must be X and also not-X" — the same element needs opposite states. This is the sharpest form of a problem and often the most solvable, because the four separation principles almost always crack it.

**Core idea:** A physical contradiction is one element requiring two opposite states at once. If you can separate those states in time, space, condition, or scale, both demands can be satisfied without compromise. Many engineering contradictions, when pushed to their extreme, reduce to a physical contradiction — and physical contradictions are often easier to resolve.

### The four separation principles

1. **Separation in TIME** — Element E is A at one time, not-A at another.  
   *Example:* A notification is present at the user's chosen workout window, absent otherwise. A bridge is rigid when loaded, flexible (expansion joints) with temperature.

2. **Separation in SPACE** — Element E is A in one place, not-A in another.  
   *Example:* A reminder is present on the practice screen, absent on the rest of the phone. Eyeglasses: different optical power in different zones (bifocals).

3. **Separation upon CONDITION** — Element E is A under one condition, not-A under another (state-dependent).  
   *Example:* Notify only when adherence dropped below target this week; silent otherwise. A sieve passes water but stops gravel — same hole, condition = particle size.

4. **Separation between PARTS and WHOLE (scale)** — The whole is A; a part is not-A (or vice versa).  
   *Example:* The program as a whole is "always present" (passive widget) while each push is rare. A bicycle chain is flexible as a whole, rigid in each link.

### Mapping to inventive principles

Each separation maps to a cluster of the 40 principles:
- **Time** → 9 (Preliminary Anti-action), 10 (Preliminary Action), 15 (Dynamization), 19 (Periodic Action), 21 (Skipping)
- **Space** → 1 (Segmentation), 2 (Taking out), 3 (Local Quality), 4 (Asymmetry), 7 (Nesting), 17 (Another Dimension)
- **Condition** → 32 (Color Changes), 35 (Parameter Changes), 36 (Phase Transitions), 31 (Porous Materials)
- **Parts/Whole** → 1 (Segmentation), 5 (Merging), 12 (Equipotentiality), 33 (Homogeneity), 40 (Composite Materials)

**Procedure:**
1. Find the single element that carries both demands. Name it precisely.
2. Write the two opposite states (A / not-A) and each one's goal.
3. Test all four separations; for each that fits, write a concrete mechanism.
4. Convert the best mechanism into a design change, tag it `[Separation in <axis>]`.

If you cannot reduce the problem to one element with opposite states, you likely have an engineering contradiction (two different parameters) instead — go to section 5.

**Example:** "The notification must be present (to drive adherence) and absent (to avoid annoyance)." Separation in time → fire only at the user's historically active hour. Separation on condition → nudge only when adherence dropped below target. Separation by scale → the app is always present as a passive widget; individual pushes are rare. Each yields a concrete design change.

**Derives →** `references/physical-contradictions.md`

---

## 8. Resource analysis

**When to use:** "We lack budget / people / tools / data" — any situation where the obvious solution requires something you don't have. Also the mandatory prerequisite for Ideality/IFR work.

**Core idea:** Before adding anything new, find what is **already present and underused**. The ideal solution uses resources you already have for free. Most "we need budget / people / a new tool" problems dissolve once the existing resource inventory is honest. A solution built from present resources is cheaper, faster, and more reversible — it scores high on ideality.

### Resource categories

| Type | Look for | Examples |
|------|----------|----------|
| **Internal (substance)** | parts, materials, data already in the system | logs, existing DB fields, sensors, unused screen space |
| **External (super-system)** | things in the environment | the phone's calendar, GPS, weather, the clinic's existing intake form |
| **Free / underused** | capacity that's idle or wasted | idle CPU, dead time in a workflow, a staff member's slack hours, waste heat |
| **Informational** | signals and data you could read | usage patterns, timestamps, error rates, patient self-reports |
| **Temporal** | moments and idle periods | time before/after an action, breaks, off-peak windows, the gap between sessions |
| **Spatial** | surfaces, volumes, positions, directions | margins of a UI, the back of a form, the lock screen, room layout |
| **Human** | attention, motivation, social ties | the patient's own goals, family, peer groups, the user's habit triggers |
| **Digital / software** | APIs, automations, existing tools | webhooks, cron, a spreadsheet, an LLM, push APIs, existing integrations |

### Resource fields (MATCHEMIB)

Physical/engineering resources also come as **fields**: **M**echanical, **A**coustic, **T**hermal, **CHEM**ical, **E**lectromagnetic, **I**ntermolecular, **B**iological. Useful for hardware/physical problems.

### Derived resources

You can transform a resource into a more useful one:
- Combine two weak resources (idle time + existing data → predicted active window).
- Change state (waste heat → energy; raw logs → a signal).
- Use a resource against itself (the annoyance signal becomes the throttle input).

**Procedure:**
1. Fill the checklist — at least one concrete item per row, or write "none."
2. Star the 3–5 resources most relevant to the problem.
3. For each starred resource, write one sentence: how it could replace a new component or strengthen an insufficient function.
4. Feed these into IFR (section 9) and solution generation.

**Example:** For a reminder app: internal = usage logs (time of day each user exercises); external = phone calendar (already nudges); temporal = the gap between sessions (could be used for a check-in); human = the patient's own motivation and habit triggers. Combined: use the logs + the gap → predicted active window → schedule reminders then.

**Derives →** `references/resource-analysis.md`

---

## 9. Ideal Final Result & ideality

**When to use:** "Reinvent / leapfrog this whole thing" — when you want the boldest possible solution direction, not incremental improvement. Also used in every evaluation (stage 9 of the pipeline) to measure how close each solution gets to ideal.

**Core idea:** The IFR is the north star: the useful function is delivered **perfectly, by itself, with zero cost and zero harm** — ideally without the system even existing as a separate thing. You won't reach it, but aiming there generates the boldest realistic moves. The gap between now and ideal *is* the contradiction to solve.

### The ideality equation

```
                Σ Useful functions
Ideality  =  ───────────────────────────────
             Σ Costs  +  Σ Harms  +  Σ Complexity
```

Raise ideality by any of: **add useful function · cut cost · cut harm · cut complexity**. The most TRIZ-like move is to raise the numerator while shrinking the denominator — usually by trimming or by using an existing resource.

### The four ideality strategies

1. **Eliminate harm** — remove or block each harmful function (notification annoyance, manual rework, side effects).
2. **Increase usefulness** — make the main function stronger / more frequent / more reliable.
3. **Hold or cut resources** — deliver the same with fewer parts, less cost, less maintenance.
4. **Add new useful function** — what else could this system do "for free" with what it already has?

### The IFR statement

Template: *The [function] happens by itself, exactly when needed, with no added cost, harm, or new component.*

### The key questions
- "How could we get this result **without adding any new element**?"
- "What if the **object did the function itself**?" (self-service / self-X) → often points straight at Trimming.
- "What if the function were already done **before the problem appears**?" (prior action).
- "What would the **ideal version with no cost** look like — and which 60% of that is actually achievable now?"

### Self-X (the ideal direction)

Push functions toward self-service: self-adjusting, self-correcting, self-monitoring, self-scheduling. The system uses its own resources to perform a function that previously needed an external tool or human effort.

**Procedure:**
1. Write the IFR statement using the template.
2. Run all four ideality strategies — list at least one concrete move per strategy.
3. Ask the four key questions; capture the answers as solution seeds.
4. Feed the IFR and seeds into solution generation (pipeline stage 8).
5. Use the ideality equation to score solutions in evaluation (pipeline stage 9).

**Example:** "The patient does the right exercise at the right intensity on their own, at the right time, with no reminder needed." Then work backwards: what would have to be true for that to happen? → The exercise must be tied to an existing habit (resource: daily routine). The intensity must auto-regulate (self-adjusting). The timing must feel internal, not external.

**Derives →** `references/ideal-final-result.md`

---

## 10. Trimming

**When to use:** "Too many parts / too costly / too complex" — when the function table (section 3) shows redundant, costly, or harmful-side-effect components. Always run function analysis first — you trim functions, not random parts.

**Core idea:** Trimming = **delete a component but keep its useful function**, by handing that function to something that remains. It's the most direct way to raise ideality: fewer parts, same value. The key question: "IF we remove [component], THEN [benefit: less cost/complexity/harm], BUT [its useful function is lost]. How do we keep [function] without [component]?"

### The three trimming rules

- **Rule A — the object disappears.** Trim the tool if the object of its useful function is itself removed or no longer needs the action. *(No dirty dishes → no dishwasher. No manual data entry → no validation step.)*

- **Rule B — the object does it itself.** Trim the tool if the **object performs the function on itself** (self-service). *(Self-cleaning surface; a form that validates as the user types; an exercise that auto-logs because the motion sensor already sees it.)*

- **Rule C — another component does it.** Trim the tool if **another existing component** can perform the function. Guidelines:
  1. Another component does the **same function on the same object**.
  2. On a **different object**.
  3. A **different function on the same object**.
  4. Another component has the **resources** to take it on.
  *(The phone's calendar already nudges — trim the app's separate reminder engine.)*

**Procedure:**
1. From the function table, pick the component to trim (favor costly/harmful/redundant).
2. Write the trimming key problem.
3. Try Rule A, then B, then C in order (A is the biggest win — the need vanishes).
4. For Rule C, scan the resource inventory (section 8) for a component that already has what's needed.
5. Verify the main function survives and no new harmful function appears.

**Trimming + contradiction:** Trimming often surfaces a contradiction ("if we remove it we lose X"). That's good — hand the residual "how do we keep X without it" to contradiction analysis (sections 5–7).

**Example:** A physio app has a separate reminder engine (costly, complexity). Rule A: does the patient still need reminders? Yes — the need hasn't vanished. Rule B: can the patient remind themselves? Possibly — tie exercises to an existing habit. Rule C: does something else already nudge? The phone's calendar and the clinician's weekly check-in both do. Trim the reminder engine; the calendar handles scheduling and the clinician reinforces at visits. Net: lower cost, lower complexity, same adherence function.

**Output:** For each trim: what's removed, which rule, who inherits the function, net effect on cost/complexity/harm, and any new contradiction created. Tag `[Trimming Rule A/B/C]`.

**Derives →** `references/trimming.md`

---

## 11. System operator (9 Windows)

**When to use:** The problem feels stuck or too narrow. You need to decide *where* to intervene (which level) before *how*. You're designing for the long term and want to avoid a soon-obsolete fix.

**Core idea:** A thinking lens that fights tunnel vision. You look at the problem across **three system levels × three time frames** = 9 windows. Solutions hide in the cells you'd normally ignore (the super-system in the past, the sub-system in the future).

### The 9-Window grid

| | **Past** | **Present** | **Future** |
|---|---|---|---|
| **Super-system** (context/environment) | what the context used to be | current environment & constraints | where the context is heading |
| **System** (the thing) | how the system was / its origin | the system as-is | the evolved/ideal system |
| **Sub-system** (parts) | former parts / inputs | current parts | future parts / capabilities |

**Procedure:**
1. Put your problem in the **center cell** (System / Present).
2. Fill the other 8 cells with short notes. Force yourself to write something in each — the empty ones you resist are usually where the insight is.
3. Read across rows and columns for moves:
   - **Past column** → a cause was planted earlier; can you act before the problem (prior action)?
   - **Future column** → where is this evolving anyway? Skate to the puck.
   - **Super-system row** → can the environment or a neighbor system do the job (Trimming Rule C, FOS)?
   - **Sub-system row** → can a part be given a new function, or removed?

**Trends for the future cells:** Systems tend to evolve toward more dynamic/adaptive, more segmented, more automated/self-service, more ideal (function with fewer resources), and better matched to the super-system. Use these to fill the Future column with direction, not guesswork.

**Example:**
- Super/Past: patients relied on the clinician's in-person reminders.
- Super/Future: wearables and calendars become the default reminder layer → the app may not need its own notifications at all.
- Sub/Future: on-device activity sensing detects exercises automatically → reminders become confirmations, not nags.
- System/Past: v1 sent fixed daily pushes → that's the origin of the annoyance.

**Output:** The filled 9-window grid + 2–3 candidate intervention points it revealed.

**Derives →** `references/system-operator.md`

---

## 12. Substance-field analysis & the 76 standard solutions

**When to use:** The problem is about an **interaction** — "the brush doesn't clean enough," "vibration damages the bearing," "the reminder annoys the user" — rather than a parameter trade-off. Use when the problem signature contains words like "interferes," "doesn't act on," "damages," "weak effect," "between," "contact."

**Core idea:** Su-Field analysis models interactions as the smallest working unit of a system: **two substances (S1, S2) interacting through a field (F)**. A useful function needs all three. When one is missing, weak, harmful, or excessive, the model tells you *which kind of fix* applies — and the **76 Standard Solutions** are the catalog of those fixes, grouped into 5 classes.

### The model
- **S1** = the object/product (acted upon). **S2** = the tool/substance acting on it.
- **F** = the field carrying the action: Mechanical, Acoustic, Thermal, Chemical, Electric, Magnetic, Electromagnetic, Gravitational — and in non-engineering domains: **Informational, Social/Behavioral, Economic** (the field is whatever *carries the influence* — money, attention, a notification, a rule).
- Draw it: `S1 —[F]→ S2`. Mark the link:
  - **Solid arrow** = adequate useful action
  - **Dashed/thin arrow** = insufficient action
  - **Wavy arrow** = harmful action

### The 5 diagnoses → which solution class

| Su-Field state | What you see | Go to class |
|---|---|---|
| **Incomplete** (S1 + S2 but no F, or a substance missing) | function doesn't happen at all | **Class 1** — complete the field |
| **Insufficient** | function happens but too weakly | **Class 1/2** — add/upgrade field |
| **Harmful** | an unwanted action accompanies the useful one | **Class 1** — block, neutralize, or add S3 |
| **Measurement/detection** problem | you can't sense or measure the state | **Class 4** — measurement standards |
| **Excessive / needs simplification** | works but too costly/complex | **Class 5 + Trimming** |

### The 5 standard-solution classes

**Class 1 — Build or destroy a Su-Field (13 solutions).** Complete an incomplete model; if a field is harmful, either *block* it, introduce a third substance S3 that absorbs the harm, or *redirect* the harmful field onto a sacrificial element. Core moves: add the missing substance/field; introduce S3 (often a modified version of S1 or S2, a void, a foam, an additive); switch to an externally-added or environmentally-available field.

**Class 2 — Develop / enhance the Su-Field (23 solutions).** Make a working model stronger or more controllable: chain Su-Fields (add another S–F stage), move to a **double or complex Su-Field**, increase **controllability** by upgrading the field (mechanical → electric → magnetic → electromagnetic, i.e., toward more easily controlled fields), **fragment** substances (solid → powder → liquid → gas → field), introduce **capillary/porous** structures, make the field or substance **dynamic/rhythmic** (pulse instead of constant), and match field frequency to the natural frequency of the object.

**Class 3 — Transition to super-system or micro-level (6 solutions).** Combine the system with others into a **bi-/poly-system**, or drop to the **micro-level** (act on molecules/fields rather than the whole part). "Solve it one level up or one level down."

**Class 4 — Detection & measurement (17 solutions).** If you must measure, first ask if you can **avoid measuring** (change the system so the measurement isn't needed). Else: measure a **copy**, measure two states and their **difference**, add an easily-detected **marker/additive**, exploit **resonance** or a field the object naturally emits, measure **derivatives** of a quantity instead of the quantity.

**Class 5 — Simplification & helpers / "how to apply 1–4" (17 solutions).** Introduce substances/fields the *cheap* way: use **voids, foams, inflatable or field-generated substances** instead of added matter; use **self-eliminating** substances (ice, evaporating, dissolving) that vanish after acting; obtain a field from the **environment** or from **phase transitions**; let the system **act on itself** (self-service). This class is where ideality lives.

**Procedure:**
1. Identify the function as an interaction → draw `S1 —[F]→ S2`.
2. Classify the link: complete / insufficient / harmful / measurement / excessive.
3. Jump to the class above; pick 1–3 candidate moves.
4. Translate each into a concrete change to *your* system. Tag `[SS Class N: description]`.
5. Hand the candidates to solution generation and evaluation.

**Example:** S1 = patient, S2 = exercise plan, F = reminder (informational field). The reminder is **harmful** (annoying). Class 1: add S3 (context — only fire when the patient is actually free). Class 5: self-service — tie to the patient's own routine so the external reminder isn't needed. Both yield concrete solution directions.

**Derives →** `references/substance-field-analysis.md`

---

## 13. ARIZ-85C

**When to use:** "Tried the quick tools, still stuck on a hard contradiction." ARIZ is the heavy artillery — a structured, sequential algorithm for problems that resist the matrix, separation, and trimming. Escalation only; don't start here.

**Core idea:** ARIZ (Algorithm for Inventive Problem Solving) reformulates a fuzzy problem step by step until the core contradiction and the solution become almost self-evident. It orchestrates the other TRIZ tools — physical contradiction + separation, resource analysis (OZ/OT/SFR), and Su-Field + standard solutions — into a disciplined worksheet. The output is always a **physical contradiction made resolvable** by a specific resource.

### The 9 parts of ARIZ-85C

1. **Problem & technical contradiction** — State the technical contradiction (TC) in both directions (TC-1: do A, gain X lose Y; TC-2: do not-A, keep Y lose X). Define the conflict pair (Tool & Object). Intensify the TC to extremes — extremes expose the real contradiction. Then **pick the TC that best preserves the main useful function** and state the *intensified* version (push the conflict to the extreme: "infinitely many", "zero", "instant").

2. **Resources** — Define the operating zone (OZ: exact space of conflict) and operating time (OT: exact time window — before/during/after). List substance-field resources (SFR): everything available inside or around the OZ/OT — substances, fields, space, time, the object itself, voids, by-products.

3. **IFR & physical contradiction** — State IFR-1: "The X-element, by itself, eliminates the harm during OT within OZ, while keeping the useful function and adding nothing." Intensify: the X-element must use only resources already in the OZ. State the physical contradiction (PC) at macro level (element in OZ must be P and not-P) and at micro level (particles/parts must produce P and not-P).

4. **Apply resources** — Apply the separation principles (time/space/condition/scale) to the PC. Apply the 76 standard solutions / Su-Field model to the conflict. Use Smart Little People modeling on the OZ if still stuck.

5. **Knowledge base** — Search scientific/physical effects that deliver the needed action with the available resources. Reuse known patterns/analogies (FOS): who else moves, heats, holds, separates, detects this cheaply elsewhere?

6. **Reformulate** — If no solution: was the right problem chosen? Switch to the other TC, widen the system (super-system) or narrow it (sub-system) and rerun. Check whether the problem disappears if a constraint is removed or a different component is selected as the conflict pair.

7. **Analyze the solution** — Does the concept introduce new harms or costs? Loop them back as new contradictions. How many resources did it consume? Fewer = more ideal.

8. **Maximize the solution** — Where else does this concept apply (other products, other parts of the system, the super-system)? Capture spin-off applications.

9. **Reflect on the process** — What reformulation unlocked it? Save the case so the move is reusable.

**Procedure:** Generate the worksheet with `python .claude/skills/triz-innovation/scripts/triz_ariz.py "problem title"` and fill every part in writing. ARIZ is a worksheet, not a chat — the discipline of writing each step is what produces the insight.

**Example:** A valve must open fast (for safety) and close slowly (to prevent water hammer). TC-1: fast open → safety but water hammer. TC-2: slow close → no hammer but unsafe. Conflict pair: valve plug + water. OZ: the valve seat. OT: the transition moment. SFR: the water itself, the pressure difference. IFR: the water itself prevents the hammer while allowing fast opening. PC: the water must be compressible (to absorb the shock) and incompressible (to transmit force). Separation in condition: introduce a small air pocket near the valve seat — water is incompressible, air is compressible; at the moment of closure, the air pocket absorbs the shock.

**Derives →** `references/ariz.md`

---

## 14. Evolution trends & the S-curve

**When to use:** "Where is this headed / how do we leapfrog this whole class?" — when you want to predict the next move or reinvent a mature system. Use in pipeline stages 6 (IFR) and 7 (method selection).

**Core idea:** TRIZ claims that technical (and many non-technical) systems evolve along **predictable trends**, not randomly. If you know where a system sits on these trends, you can **predict its next move and leapfrog competitors** instead of optimizing a dying design.

### The S-curve (system maturity)

Every system follows an S-shaped performance-vs-effort curve through 4 stages:

| Stage | Signs | What to do |
|---|---|---|
| **1. Infancy** | low performance, high cost, unreliable, few patents | invest if the IFR is compelling; expect rough edges |
| **2. Growth** | rapid improvement, investment pours in, patents rise | optimize hard, scale, capture market |
| **3. Maturity** | gains shrink, cost of each improvement rises, patent quantity peaks then falls while patent level drops (minor tweaks) | stop polishing — look for the **next S-curve** |
| **4. Decline** | performance plateaus, replaced by a new principle | jump to a new operating principle (new S-curve) |

**Diagnostic:** if you're spending more and more to gain less and less, and recent "innovations" are cosmetic, you're in late maturity — the leverage is in switching curves, not tuning this one.

### The 8 trends (laws) of evolution

1. **Increasing ideality** — More useful function per unit cost/harm; functions get delivered with fewer or no added components (toward IFR). The master trend.
2. **Non-uniform development of parts** — Sub-systems evolve at different rates; the slowest-evolving part becomes the bottleneck and the next contradiction. Find it.
3. **Increasing dynamism & controllability** — Rigid → jointed → flexible → fluid/field; manual → automatic → adaptive. Static things become tunable in real time.
4. **Increasing complexity then simplification (mono → bi → poly → trim)** — Systems add parts/functions (mono→bi→poly-system), then **trim** back to fewer parts carrying more functions. Know which half you're in.
5. **Matching & mismatching of parts** — Parts evolve from unmatched → matched → dynamically matched → deliberately mismatched to exploit a difference.
6. **Transition to the super-system & micro-level** — Mature systems merge into a bigger system or drop to act at the micro/field level (cf. Su-Field Class 3).
7. **Decreasing human involvement** — Functions migrate from human → tool → fully automatic/self-service. Each manual step is a future automation.
8. **Uneven flow / increasing field controllability** — Energy/substance/information conduction improves; fields shift toward more controllable ones (mechanical → electromagnetic), flows become smoother and lossless.

**Procedure:**
1. Place the system on the S-curve (which stage? evidence?).
2. Walk the 8 trends: for each, state where the system is now and the *next step* along that trend. Most systems are "behind" on 2–3 trends — those are the cheap wins.
3. Combine with System Operator (section 11): the "future" column of the 9 windows is exactly a trends forecast.
4. Convert forecasts into solutions, tagged `[Trend N: name]`.

**Example:**
- Trend 7 (less human involvement): manual → one-click → automatic on merge → self-healing rollback. Next: auto-deploy on green CI.
- Trend 3 (dynamism): one fixed pipeline → configurable per-service → adapts to change size. Next: risk-based pipeline.
- Trend 4 (mono→poly→trim): one script doing build+test+deploy → split stages → trim duplicated setup into a shared cached layer.

**Derives →** `references/evolution-trends.md`

---

## 15. Scientific effects

**When to use:** "I have the action but no mechanism" — you know what function you need (move, hold, heat, detect, separate) but don't know how to achieve it cheaply. Use inside ARIZ Part 5 and pipeline stage 8.

**Core idea:** The TRIZ "effects" approach flips the search: start from the **function** you need (verb + parameter), then pull the known **effects** (physical, chemical, geometric — and in other domains, behavioral/economic) that deliver it. This is how you find non-obvious mechanisms already proven elsewhere.

### Function families → effects (starter catalog)

**Move / transport a substance:** capillarity, osmosis, electro-/magneto-phoresis, gravity & siphon, thermal convection, pressure difference, ultrasonic streaming, diffusion. *(Non-engineering: incentives, defaults, social proof move behavior.)*

**Hold / fix / position:** magnetism, electrostatics, vacuum/suction, freezing (phase change to solid), surface tension, friction, interference/snap geometry, gyroscopic stiffening.

**Heat / cool a region:** Joule heating, induction, Peltier effect, evaporative cooling, exothermic reaction, microwave/dielectric heating, radiative cooling.

**Detect / measure:** resonance & natural frequency shift, thermal imaging, luminescence/fluorescent markers, change of color/phase indicators, capacitance change, Hall effect, Doppler shift, measuring a *derivative* or a *difference*.

**Change properties on demand:** phase transitions, shape-memory alloys/polymers, thixotropy (gel↔liquid under shear), magneto-/electro-rheological fluids, photochromism/thermochromism, piezoelectricity (force↔voltage).

**Generate force / motion:** thermal expansion, piezo actuation, magnetostriction, shape-memory, electrostatic/magnetic attraction, pressure/phase-change expansion, bimetallic bending.

**Separate / mix / purify:** centrifugation, electrophoresis, magnetic separation, distillation/phase change, filtration via porous/capillary media, flotation, adsorption.

### Cross-domain translation

The same move maps across domains: "use an environmental field for free" → software: use the OS/browser's existing events instead of polling; business: use existing customer behavior (defaults, habits) instead of new campaigns; rehab: use the patient's daily routine as the trigger (self-service field) instead of an added reminder. The discipline is identical: name the function, borrow a proven effect, check the resource is already there.

**Procedure:**
1. State the function as **action + object + condition**: "heat a small region without contact," "hold a part without a clamp," "measure level without a sensor inside the tank."
2. Pick the function family above and scan its effects.
3. For each candidate effect, ask: *do I have the resource it needs?* (cf. section 8). Keep the ones that use resources already present.
4. Tag the solution `[Effect: name]`.

**Example:** "Detect whether a patient did their exercises without a wearable." Function family: detect/measure. Candidate effects: measure a derivative (phone accelerometer data already exists as a resource); use resonance/difference (compare baseline daily movement to exercise-day movement). Both use resources already present — no new hardware.

**Derives →** `references/scientific-effects.md`

---

## 16. Function-Oriented Search & Method-Oriented Search

**When to use:** "Someone, somewhere already solved this" — you need to find existing solutions from other industries or domains. FOS when you know the function you need; MOS when you have a capability and need problems it can solve.

**Core idea:** Innovation by cross-industry analogy. Function-Oriented Search (FOS) starts from the **function** you need and finds industries/fields that already perform it well — then adapt their solution. Method-Oriented Search (MOS) works the other way: you have a **method or technology** and hunt for problems it can solve. Both leverage the TRIZ insight that the same functions appear across all domains.

### Function-Oriented Search (FOS)

**Procedure:**
1. Define the function in neutral, domain-free language: "remove heat from a small area quickly" (not "find a better CPU fan").
2. Generalize: what is the *leading industry* for this function? (Cooling → cryogenics, HVAC, aerospace thermal management.)
3. Search for how the leading industry solves it. Adapt their mechanism to your constraints.
4. Tag solutions `[FOS: industry → mechanism]`.

### Method-Oriented Search (MOS)

**Procedure:**
1. Describe your capability/method in functional terms: "We have a material that changes shape when heated."
2. Search for problems that need "shape change triggered by heat."
3. Filter for problems where your specific method has an advantage (cheaper, faster, safer).
4. Tag solutions `[MOS: method → problem domain]`.

**Example:** A clinic needs to reduce patient no-shows. FOS: generalize to "ensure a person arrives at a specific time." Leading industries: airlines (check-in reminders), restaurants (reservation confirmations), dentists (appointment cards). Adapt: the airline model of escalating reminders (72h, 24h, 2h before) plus a "check in now" button. Tag: `[FOS: airline check-in → appointment reminders]`.

### Method selection decision table

When you don't know which TRIZ tool to use, match the problem signature to the row and run those methods. Most real problems need **2–4** methods, not one. This table is the engine behind `triz_router.py`.

| If the problem looks like… | Start with | Then |
|---|---|---|
| "Improving A makes B worse" (a trade-off) | Engineering Contradiction + 40 IP | Physical Contradiction if it reduces to one element |
| "It must be X and also not-X" (same thing, opposite needs) | Physical Contradiction + Separation | Resource Analysis |
| "Too many parts / too costly / too complex" | Trimming | Function Analysis first, then Ideality |
| "Why does this keep happening?" / recurring failure | Root Cause Analysis | Contradiction at the root cause |
| "What even is going on here?" / unclear system | Function Analysis | System Operator |
| "We lack budget / people / data" | Resource Analysis | Ideality |
| "Reinvent / leapfrog this whole thing" | Ideal Final Result | System Operator + Function-Oriented Search |
| "Someone, somewhere already solved this" | Function-Oriented Search | 76 Standard Solutions |
| "Two things interact badly" (weak/harmful/missing action) | Su-Field + 76 Standard Solutions | Standard-solution class for the state |
| "Where is this headed / how to leapfrog this whole class" | Evolution Trends + S-curve | System Operator (future column) |
| "I have the action but no mechanism" | Scientific Effects | Resource Analysis |
| "Tried the quick tools, still stuck on a hard contradiction" | ARIZ (escalation) | Physical Contradiction + Su-Field + Resources |
| "Stuck, need a perspective shift" | Smart Little People | System Operator |
| Business / org / pricing / market | Business TRIZ | Contradiction + Resource + Ideality |
| Software / architecture / performance | Software TRIZ | Contradiction + Trimming |
| Physio / rehab / clinic / adherence | Rehabilitation TRIZ | Physical Contradiction + Resource + Ideality |

### Default fallback

If the problem signature is unclear, run: **Function Analysis → Root Cause → Contradiction → Resource → IFR**. That sequence works on almost anything.

### Router heuristics (keyword → method)

These are the keyword/intent cues used by `triz_router.py` to recommend methods. They are signals, not rules — a problem can hit several.

- **Engineering Contradiction:** "but", "trade-off", "at the cost of", "however", "increases … decreases", "more X means less Y".
- **Physical Contradiction:** "must be both", "present and absent", "fast and slow", "big and small", "on and off", "hot and cold".
- **Trimming:** "too many", "too complex", "expensive", "remove", "simplify", "redundant", "overhead", "bloated".
- **Root Cause Analysis:** "keeps happening", "recurring", "again", "fails", "root", "why", "intermittent".
- **Resource Analysis:** "no budget", "limited", "can't afford", "without adding", "scarce", "few people".
- **Ideality / IFR:** "ideal", "leapfrog", "rethink", "from scratch", "best possible".
- **Function Analysis:** "unclear", "complex system", "many parts", "interactions", "how it works".
- **System Operator:** "future", "evolve", "long term", "context", "bigger picture".
- **Su-Field + 76 Standard Solutions:** "interaction", "interferes", "doesn't act on", "damages", "weak effect", "too strong", "harmful", "contact", "between", "connect".
- **Evolution Trends + S-curve:** "leapfrog", "next generation", "where is this going", "mature", "plateau", "diminishing returns", "reinvent the category", "obsolete".
- **Scientific Effects:** "how do I", "mechanism", "without a", "is there a way to", "what effect", "achieve X without".
- **ARIZ:** "still stuck", "tried everything", "hard problem", "nothing works", "very hard contradiction", "deep dive".
- **Smart Little People:** "stuck", "no idea", "creative block".
- **Business TRIZ:** "pricing", "customer", "market", "revenue", "team", "process", "org", "workflow".
- **Software TRIZ:** "app", "code", "latency", "API", "database", "deploy", "architecture", "bug", "notification".
- **Rehabilitation TRIZ:** "patient", "exercise", "therapy", "rehab", "adherence", "clinic", "physio".
- **FOS:** "someone must have solved", "how do others", "is there a field that".
- **MOS:** "we have a technology", "where can we apply", "find problems for".

**Derives →** `references/triz-method-map.md`

---

## 17. Smart Little People

**When to use:** "Stuck, need a perspective shift" — when psychological inertia blocks you from seeing a solution. Use as a modeling technique inside ARIZ Part 4 or whenever you're creatively blocked. Also effective when a problem feels "too abstract" to visualize — the agents make it concrete.

**Core idea:** Model the problem with imaginary tiny agents ("smart little people") who can do exactly what you tell them. Place them at the conflict zone and instruct them to satisfy the contradictory demands — some agents deliver one requirement, others deliver the opposite. This externalizes the problem and bypasses the mental blocks that come from thinking about "the valve" or "the code" as monolithic objects. The method works because it forces you to specify **who does what, where, and when** — the answers often reveal the solution mechanism directly. It pairs naturally with the separation principles: time-separated agents, space-separated agents, condition-triggered agents, or scale-separated agents.

**Procedure:**
1. Identify the conflict zone (where the contradiction physically/functionally occurs).
2. Populate it with smart little people. Describe what each group does, where they stand, and what triggers them.
3. Instruct them to satisfy both demands simultaneously — e.g., "Group A holds the door open when fluid flows forward; Group B pushes the door shut the moment fluid tries to flow backward."
4. Vary the agent behavior: what if they worked in shifts (time)? What if they occupied different zones (space)? What if only some of them activate under a specific condition (condition)? What if a small team does something different from the whole crowd (scale)?
5. Translate the agent behavior back into a real mechanism. The "how" the agents achieve it often maps directly to a separation principle, a field, or a material property.

**Example:** A pipe must be open (for flow) and closed (to prevent backflow). Smart little people: Group A stands at the opening and lets fluid pass in one direction; the moment fluid tries to reverse, Group B (triggered by the backward pressure) swings a door shut. Translation: a check valve — a real mechanism that emerged from modeling the conflict with agents. For a software analogy (a login page must be secure and fast): Group A (security agents) check credentials thoroughly; Group B (speed agents) pre-warm the session while Group A works, so the user sees no delay. Translation: background authentication with optimistic UI.

Key router keywords (used by `triz_router.py`): Smart Little People — "stuck," "no idea," "creative block" (Italian: "bloccato," "nessuna idea," "blocco creativo").

**Derives →** `references/triz-method-map.md`

---

## 18. Business TRIZ

**When to use:** Business, pricing, org structure, workflow, process, or market problems. The problem signature includes words like "pricing," "customer," "market," "revenue," "team," "process," "org," "workflow."

**Core idea:** Same TRIZ machinery (functions, contradictions, resources, ideality) with non-engineering vocabulary. The tools don't change; the nouns do.

### Core concept translation

| Engineering | Business |
|---|---|
| Component | Role, team, process step, document, channel, asset |
| Tool → Action → Object | Who does what to whom (process → outcome → stakeholder) |
| Harmful function | Friction, cost, churn, rework, dissatisfaction |
| Insufficient function | Weak conversion, low adoption, underdelivery |
| Excessive | Over-processing, over-communication, waste |
| Resource | Existing customers, data, brand, idle capacity, staff time, channels |
| Super-system | Market, regulator, partners, competitors |

**Procedure:**
1. Translate the core concepts using the table above — map every business element to its TRIZ equivalent.
2. Identify the dominant contradiction pattern (price/volume, quality/speed, personalization/scale, growth/margin).
3. Resolve using the contradiction-specific principles below, then run the pricing playbook for pricing problems.
4. Check each candidate against the Ideality equation: raise value + revenue, cut cost to serve + risk + complexity.

### Common business contradictions

- **Price vs volume** — raise price, lose customers. Resolve by separation on **condition** (segment-based pricing), **time** (intro vs standard), **parts/whole** (free core + paid add-ons). [IP-3 Local Quality, IP-4 Asymmetry]
- **Quality vs speed** — [IP-10 Preliminary Action] templatize; [IP-1 Segmentation] tier the offering.
- **Personalization vs scale** — [IP-25 Self-service] customer configures; [IP-15 Dynamization] rules engine.
- **Growth vs margin** — Resource Analysis: monetize an existing underused asset before spending.

### Business-specific tools

- **Solutions at system levels** — generate 5–10 super-systems and sub-systems of your business, then mine each level for solutions and resources. Great for "rethink the model" problems.
- **Perception mapping** — map stakeholder perceptions and "leads-to" relationships to find conflict pairs, then translate each conflict into a TRIZ contradiction.
- **Non-engineer function analysis** — simplified U/H function table for services/processes.

### Ideality for business

Numerator = value delivered to customer + revenue. Denominator = cost to serve + risk + org complexity. Bias every move toward **self-service** and **using existing assets** — that's where margin and durability come from.

### Pricing playbook (mini)

1. **Function-analyze the offer:** what useful function does the customer actually pay for? Grade it N/I/E.
2. **Find the contradiction** — usually price↔adoption or simplicity↔revenue.
3. **Resolve by separation:** tiers (condition), trials (time), bundle/unbundle (parts↔whole), usage-based (dynamics).
4. **IFR check:** the customer gets the value *and pays in proportion to value received*, with no friction.
5. **Score variants** on impact/feasibility/risk/reversibility; pick the smallest reversible price test.

**Example:** A SaaS company wants to raise prices but fears churn. Contradiction: price vs volume. Separation on condition: segment by usage — heavy users pay more (value-based), light users keep a low tier. Separation on time: grandfather existing customers at current rates; new customers get new pricing. Separation by parts/whole: unbundle premium features into add-ons. Test the smallest reversible move first (e.g., a single add-on for new customers only).

**Derives →** `references/business-triz.md`

---

## 19. Software TRIZ

**When to use:** Software architecture, performance, reliability, UX, and app problems. The problem signature includes "app," "code," "latency," "API," "database," "deploy," "architecture," "bug," "notification."

**Core idea:** TRIZ for software — the contradictions are real even though there are no atoms (latency vs cost, flexibility vs simplicity, consistency vs availability). The same patterns apply; translate the nouns.

### Core concept translation

| Engineering | Software |
|---|---|
| Component | Service, module, layer, data store, job, endpoint, UI element |
| Tool → Action → Object | Producer → operation → consumer/data |
| Harmful function | Coupling, latency, flakiness, tech debt, alert fatigue |
| Insufficient | Slow, under-tested, low coverage, missing validation |
| Excessive | Over-fetching, chatty APIs, notification spam, over-engineering |
| Resource | Cache, idle CPU, logs, existing fields, the platform/OS, the client device |

**Procedure:**
1. Translate the core concepts using the table above — map every software element to its TRIZ equivalent.
2. Match your problem to the recurring contradiction patterns below; apply the suggested principles.
3. Run the software-specific moves checklist (trimming, self-service, resource-first, System Operator).
4. Evaluate against the IFR: does the solution add zero latency, zero new service, and zero maintenance? Push designs toward fewer moving parts.

### Recurring software contradictions → principles

- **Latency vs cost** → [IP-10 Preliminary Action] precompute/cache; [IP-19 Periodic Action] batch; [IP-2 Taking out] move work off the hot path.
- **Consistency vs availability (CAP)** → [IP-15 Dynamization] tunable consistency; [IP-13 The Other Way Around] eventual + reconcile.
- **Flexibility vs simplicity** → [IP-1 Segmentation] plugins; [IP-6 Universality] one extension point; [IP-25 Self-service] config over code.
- **Coupling vs performance** → [IP-24 Intermediary] queue/broker; [IP-7 Nesting] bounded contexts.
- **Coverage vs speed of delivery** → [IP-16 Partial or Excessive Actions] test the risky 20%; [IP-10] test fixtures prepared once.
- **Engagement vs annoyance (notifications)** → physical contradiction (present/absent) → separation in **time/condition** + [IP-15 Dynamization], [IP-23 Feedback].

### Software-specific moves

- **Trimming a service:** can the client, the DB, or the platform do the job (Rule C)? Can the need disappear entirely (Rule A — e.g., remove a sync step by making the source of truth singular)?
- **Self-service / self-X (IP-25):** self-healing retries, self-tuning autoscalers, self-validating schemas, self-logging via existing telemetry.
- **Resource-first:** before adding infra, inventory caches, logs, unused columns, client compute, and platform APIs.
- **System Operator for architecture:** sub (libraries) / system (service) / super (platform & ecosystem) across past/present/future — catches "the platform now does this, delete our code" opportunities.

### IFR for software

The function executes with **zero added latency, zero new service, zero maintenance** — i.e., it's already handled by data/compute you have. Push designs toward fewer moving parts; every new service is denominator weight.

### Test/experiment rollout guidance

Software changes are cheap to make reversible: **feature flags, canary deployments, shadow traffic, A/B testing**. The stage-10 experiment should almost always be a **flagged, metric-gated rollout** with an explicit success threshold and a **rollback trigger**. Never ship a software TRIZ solution without a way to instantly revert it. Pattern: *"Enable for 5% of users behind flag F, measure metric M for 7 days, success if M improves by ≥10% with no degradation in error rate. Roll back if error rate exceeds 0.1%."*

**Example:** A mobile app's notification system causes uninstalls (annoyance) while being the primary driver of retention. Physical contradiction: notifications must be present and absent. Separation in time: fire only during the user's historically active hours. Separation on condition: suppress when the user has already engaged today. Self-service: let users set their own notification budget ("nudge me at most 2× per day"). Tag: `[Separation in time + condition]`, `[IP-25 Self-service]`.

**Derives →** `references/software-triz.md`

---

## 20. Rehabilitation & clinical TRIZ

**When to use:** Physiotherapy, rehabilitation, adherence, and clinic/practice organization. The problem signature includes "patient," "exercise," "therapy," "rehab," "adherence," "clinic," "physio." Clinical guardrail: TRIZ generates *options*. Safety, dosage, contraindications, and diagnosis remain clinical decisions. Tag any solution touching patient safety as "requires clinician sign-off."

**Core idea:** The "system" is the therapy + patient + environment; the main useful function is **functional recovery**. TRIZ resolves the real trade-offs of clinical work — adherence vs annoyance, intensity vs safety, standardization vs personalization, throughput vs care quality — using the same tools with clinical vocabulary.

### Core concept translation

| Engineering | Rehab / clinic |
|---|---|
| Main useful function | Restore/strengthen function; reduce pain/disability |
| Tool → Action → Object | Exercise/clinician/device → loads/cues → patient tissue/behavior |
| Harmful function | Pain, fatigue, re-injury risk, annoyance, demotivation |
| Insufficient | Too little dose, poor adherence, weak carryover to daily life |
| Excessive | Overload, overtraining, over-reminding |
| Resource | Patient's own motivation, home objects, daily routine, family, wearable, idle waiting-room time |
| Super-system | Home, work, family, insurer, referring physician |

**Procedure:**
1. Translate the core concepts using the table above — map every clinical element to its TRIZ equivalent.
2. Identify the dominant contradiction (adherence/annoyance, intensity/safety, standardization/personalization, throughput/quality).
3. Resolve using the contradiction-specific patterns below, with the clinical guardrail: safety, dosage, contraindications, and diagnosis remain clinical decisions.
4. Inventory behavioral resources — the patient's own motivation, goals, habits, and social ties are the highest-leverage resources.
5. Score candidate solutions on impact (recovery), feasibility (clinically safe + doable at home), and ideality (low burden, self-sustaining). Always end with a measurable experiment.

### Signature contradictions and resolutions

- **Adherence vs annoyance (the reminder problem):** Physical contradiction — the prompt must be present and absent. Resolve by: separation in **time** (fire at the patient's real active window) [IP-10]; separation on **condition** (nudge only when adherence dropped) [IP-15]; trimming Rule B — let the patient set their own goal/check-in [IP-25]; resource — piggyback on an existing habit (after brushing teeth) [IP-10].
- **Intensity vs safety:** Separation on **condition** (auto-regulate by pain/RPE), [IP-15 Dynamization], [IP-23 Feedback]. Requires clinician thresholds.
- **Standardization vs personalization:** [IP-3 Local Quality] phase-based protocols; [IP-1 Segmentation] modular exercise blocks.
- **Clinic throughput vs care quality:** Function Analysis of the visit; trim non-value steps (Rule A/C); [IP-5 Merging] combine intake + assessment; [IP-25] patient self-intake before arrival.

### Behavioral resources

The patient's **own motivation, goals, identity, social ties, and daily routine** are free, powerful resources. IFR direction: the patient does the right exercise **by themselves at the right time because it's tied to something they already do/want** — minimal external prompting. This is self-service applied to behavior.

### IFR for rehab

Recovery happens **as a by-product of the patient's normal life**, with minimal clinic burden and minimal nagging. Score solutions on impact (recovery), feasibility (clinically safe + doable at home), and ideality (low burden, self-sustaining). Always end with a measurable experiment: a metric (adherence %, ROM, pain NRS, function score), a window, and a success threshold.

### Clinic/practice organization workflow

Treat the practice as a system: **function-analyze the patient journey** end-to-end — booking → intake → assessment → treatment → home program → follow-up. Find harmful, insufficient, and redundant steps; trim and resequence. Resource-analyze idle time (waiting room, between-session gaps) for education, self-assessment, or intake that can happen before the patient arrives. Common wins: combine intake + assessment into one step [IP-5 Merging]; let patients self-intake before arrival via a digital form [IP-25 Self-service]; trim non-value steps the clinician repeats each visit (Rule A/C); use the gap between sessions for automated check-ins (temporal resource). The IFR direction: the patient arrives pre-assessed, the clinician spends the whole visit on treatment, and the home program is already tied to the patient's daily routine before they leave.

**Example:** Post-surgical knee rehab — adherence drops at week 3. Function analysis: the exercise sheet (tool) instructs (action) the patient (object) — U, but Insufficient (patient forgets or loses motivation). Harmful: the clinician spends 15 min per visit re-explaining exercises. Root cause: the home program is disconnected from daily life. Resources: the patient walks to the kitchen every morning; the stairs are a built-in exercise surface. Solution: replace 2 of 5 sheet exercises with kitchen-counter and stair-based equivalents — the patient's environment becomes the tool (Trimming Rule B: the object does it itself). Tag: `[Trimming Rule B]`, `[Resource: daily routine]`.

**Derives →** `references/rehabilitation-triz.md`

---

## 21. Tooling

The `triz-innovation` skill includes helper scripts that automate lookups, generate worksheets, and evaluate solutions. All live under `.claude/skills/triz-innovation/scripts/`.

| Script | What it does |
|---|---|
| `triz_router.py` | Analyzes a problem description and recommends which TRIZ methods to use, plus likely contradiction types. Fast first guess: `python triz_router.py "problem text"` |
| `triz_matrix.py` | Looks up the contradiction matrix cell for a given improving × worsening parameter pair. Returns the recommended inventive principles: `python triz_matrix.py <improving_id> <worsening_id>` |
| `triz_standard_solutions.py` | Given a Su-Field state (`incomplete`, `insufficient`, `harmful`, `measurement`, `excessive`), recommends standard-solution classes and candidate moves: `python triz_standard_solutions.py --state harmful` |
| `triz_ariz.py` | Generates a structured ARIZ-85C worksheet for a given problem title. Fill every part in writing: `python triz_ariz.py "problem title"` |
| `triz_evolution.py` | Classifies S-curve stage from signals and suggests next-step evolution trends: `python triz_evolution.py --signals "gains shrinking, cost rising"` |
| `triz_case_template.py` | Creates a pre-filled markdown case file in `cases/` for persisting a TRIZ analysis: `python triz_case_template.py "Short problem title"` |
| `triz_evaluator.py` | Scores solutions from a CSV on impact, feasibility, cost, speed, risk, reversibility, complexity, and ideality. Returns a sorted table: `python triz_evaluator.py solutions.csv` |
| `triz.py` | Master dispatcher — one entrypoint for every sub-tool, works from any directory: `python triz.py route "problem"` |
| `triz_contradiction_network.py` | Builds/analyzes a contradiction network from parameter ids and finds conflicts: `python triz_contradiction_network.py --demo` |
| `triz_effects.py` | Searches the scientific-effects catalog by function or keyword: `python triz_effects.py --function "separate"` |
| `triz_branches.py` | Branch registry — lists field/language branches, resolves labels, checks schema: `python triz_branches.py list` |

---

## 22. Derivation map

This table maps every method section in the master document to the source file(s) it consolidates. Every referenced path exists on disk under `.claude/skills/triz-innovation/`.

| Master section | Derives skill file(s) |
|---|---|
| 2. The problem-solving pipeline | `SKILL.md` |
| 3. Function analysis | `references/function-analysis.md` |
| 4. Root cause analysis | `references/root-cause-analysis.md` |
| 5. Engineering contradictions, the 39 parameters & the contradiction matrix | `references/contradiction-analysis.md`, `references/contradiction-matrix.md` |
| 6. The 40 inventive principles | `references/inventive-principles.md` |
| 7. Physical contradictions & the 4 separation principles | `references/physical-contradictions.md` |
| 8. Resource analysis | `references/resource-analysis.md` |
| 9. Ideal Final Result & ideality | `references/ideal-final-result.md` |
| 10. Trimming | `references/trimming.md` |
| 11. System operator (9 Windows) | `references/system-operator.md` |
| 12. Substance-field analysis & the 76 standard solutions | `references/substance-field-analysis.md` |
| 13. ARIZ-85C | `references/ariz.md` |
| 14. Evolution trends & the S-curve | `references/evolution-trends.md` |
| 15. Scientific effects | `references/scientific-effects.md` |
| 16. Function-Oriented Search & Method-Oriented Search | `references/triz-method-map.md` |
| 17. Smart Little People | `references/triz-method-map.md` |
| 18. Business TRIZ | `references/business-triz.md` |
| 19. Software TRIZ | `references/software-triz.md` |
| 20. Rehabilitation & clinical TRIZ | `references/rehabilitation-triz.md` |

---

## 23. Provenance & sources

This document is an **original operational synthesis** — every section is written as instructional prose, checklists, decision tables, and worked examples, not as a transcription of source material. No long verbatim passages (25+ consecutive words) from any copyrighted source appear in this document.

### Primary sources

The 18 reference files in `.claude/skills/triz-innovation/references/` and the pipeline in `.claude/skills/triz-innovation/SKILL.md`. Each is an original operational rewrite — condensed, procedural, and designed for use during a TRIZ session. This master document consolidates and enriches them without altering their core concepts.

### Source material (conceptual reference only)

The source material in `Books/` (gitignored) informed the synthesis as
conceptual cross-checks only — no text was copied from it (mirrors
`docs/source-map.md`). The consulted material covered: practical framing of
function analysis, ideality, and business application; project-pipeline best
practices ("always end with an experiment"); common pitfalls and operating rules
("don't skip a stage", method-over-inspiration); and direction for future
MCP/LLM integration.

### Secondary enrichment

**`triz-prompt-engineering-main`** — A structured collection of TRIZ prompts in XML format, developed by the ccTOPP / TRIZ-prompt-engineering project and released under the **MIT License**. The following files were consulted for additional structure, checklists, and examples:

- `contradiction_solver_40_inventive_principles/40_Inventive_Principles_EN.md` — full 40 principles with engineering examples
- `76_standard_solutions/76_Standard_Solutions_EN.md` — complete 76 standard solutions catalog
- `root_conflict_analysis/root_conflict_analysis_knowledge.md` — RCA+ methodology (Souchkov approach), cause types (N, N+P, NC, P), contradiction formulation templates
- `root_conflict_analysis/root_conflict_analysis_method.md`, `tables.md`, `templates.md`, `examples.md` — RCA+ supporting materials
- `business_triz/` prompts — business domain adaptation patterns
- `technical_triz/function_analysis/`, `resource_analysis/`, `ideality/`, `trimming_and_trimming_rules/`, `system_operator/`, `physical_contradictions/`, `smart_little_people/`, `function_oriented_search/` — method-specific prompt structures
