# architecture-tradeoffs

System-level decision method: how to answer "it depends" with weighted evidence
instead of taste. Reach for it when two viable options both carry real
trade-offs — a shared library vs a shared service, sync vs async, a style
choice. Companion to the domain fork (`domain-modeling.md`) and the
time/scale/tradeoffs lens (`sustainable-engineering.md`).

## When to use it
- A choice between two viable options: queue vs topic, shared library vs shared
  service, sync vs async, REST vs messaging. Never "just pick".
- Before choosing a style or component structure — step zero of any system or
  feature design.
- Judging whether a decision is architecturally significant (every option carries
  significant trade-offs) vs a technical default you can leave alone.
- Before production and after a major refactor — the de-risk moment.
- Re-evaluating a past decision in a new context (scale, team, or budget changed).
- High-uncertainty decisions where more information is coming.

## Core method

### The Three Laws — the decision lens [Three Laws]
| Law | Meaning in code |
|---|---|
| 1. Everything is a trade-off | No silver bullet. If it seems free, keep looking; re-run the analysis per context, don't make sweeping semi-permanent calls. |
| 2. Why is more important than how | Record reasons, not mechanisms. A decision without its why is the Out of Context antipattern [Out of Context]. |
| 3. Decisions sit on a spectrum, not binaries | An architectural decision is one where EVERY option has significant trade-offs. No-binaries; extremes are rare. |

### Step zero: extract the characteristics [Characteristic extraction]
Translate business drivers into a small prioritized set of non-functional
requirements (this is the contract the whole design optimizes against).
| Business driver | Architectural characteristic |
|---|---|
| Cost / budget | Cost, elasticity, scalability |
| Time to market | Agility, deployability, testability |
| User satisfaction | Performance, availability, fault tolerance |
| Strategic position | Security, interoperability, evolvability |

Rules:
- Explicit characteristics come from requirements; implicit ones surface through
  katas and stories.
- Prioritize to a small set — typically 3 to start. You cannot satisfy ~100;
  unprioritized everything means nothing.
- Do this BEFORE style or component choice — it is step zero.

### Score candidates: the weighted trade-off matrix [Trade-off matrix]
1. List the factors that matter in THIS context (heterogeneous code, volatility,
   versioning, change risk, performance, fault tolerance, scalability).
2. Build a +/− matrix: each option scored per factor.
3. WEIGHT the criteria by the current context — do not count positives
   (programmers know the benefits of everything, trade-offs of nothing).
4. Weigh the negatives explicitly; a free lunch is a sign you mis-scored.
5. Re-run per context; a decision valid at 3 services may flip at 30.

### Train judgment: architecture katas [Architecture kata]
Scenario → identify explicit + implicit characteristics → produce a candidate
architecture with trade-off justifications. No answer key — every design has
trade-offs. The deliverable is the justification, not the diagram.

### Decompose with component-based thinking [Component buckets]
- Seed core components as "empty buckets" from major happy-path workflows (each
  step → component) or actor actions (customer / order-packer / system) — NOT
  from entities. Names like `XManager` / `XController` / `XHandler` signal the
  Entity Trap antipattern [Entity Trap].
- Assign user stories; write each component's role-and-responsibility statement.
  Conjunctive phrases ("and", "also", "in addition") signal too much
  responsibility → split [Role and responsibility].
- Analyze characteristics, then restructure iteratively. Never get the first cut
  perfect.
- This is manual trimming: pull out functions that don't belong until each
  component is single-purpose, and guard the trimmed structure with fitness
  functions.

### Record: architectural decision records [ADR]
One- to two-page markdown file per decision:
- Title, Status (Proposed / Accepted / Superseded)
- Context (forces + alternatives)
- Decision — "We will..." in affirmative voice
- Consequences (the trade-offs)
- Compliance (how it is enforced)
- Notes (metadata)

Rules: one file per decision; supersede-by-link history; a single system of
record — never the decision inside an email [Email-Driven Architecture]. This is
how "why beats how" survives to the next engineer [Why beats how].

### Govern: fitness functions [Fitness function]
Any automated mechanism that objectively assesses a characteristic: an
ArchUnit/NetArchTest test for cycles or layer violations, a metric, a chaos
experiment, a monitor. Rules:
- Wire into CI so governance guards the "important but not urgent" concerns
  automatically.
- Write one per governed decision (dependency direction, modularity, distance
  from the main sequence).
- For legacy, characterization tests play this role (`legacy-change.md`).

### De-risk: risk storming [Risk storming]
Three phases against a specific criterion/context:
1. Individually score each area on a risk matrix (impact × likelihood, 1–9) as
   green / yellow / red.
2. Consensus — reconcile disagreements. Unknown technologies are ALWAYS high
   risk (9).
3. Mitigation with the business stakeholders who hold the budget.

Repeat per major feature or iteration; surfaces risks one architect alone misses.

### Defer: last responsible moment [Last responsible moment]
Defer the decision until the cost of deferring exceeds the risk of deciding —
the intersection of the cost curve (rising with time) and the risk curve (falling
with information). Avoids both analysis paralysis and premature commitment.
≈ YAGNI applied to decisions.

### Stay broad: 20-minute rule + personal radar [20-minute rule] [Personal radar]
- 20 minutes each morning (before email) on one new topic → technical breadth.
- Maintain a personal radar: quadrants (tools / languages-frameworks /
  techniques / platforms), rings (Hold / Assess / Trial / Adopt).
- Breaks the memetic bubble; avoids the Frozen Caveman antipattern of reverting
  to pet tech [Frozen Caveman].

### TRIZ reconciliation
The First Law IS contradiction detection: "reuse is implemented via coupling" is
an engineering contradiction — improving one parameter degrades another. Where
the architecture frame settles for the least-worst compromise [Least worst], TRIZ goes one step
further and separates in time/space/part/condition to ELIMINATE it
(`triz-for-code.md`). Separation GENERATES candidates; the matrix VERIFIES the
residual. IFR is the generation north-star; this file is the evaluation
instrument [IFR]. The style catalog (microkernel, event-driven, pipeline)
is a softer analog of the 40 inventive principles; "it depends on environment,
budgets, skill set" is TRIZ resource analysis.

### Ponytail reconciliation
The default path stays the ladder — cheap, existing, one line. Escalate to this
file exactly when BOTH options carry significant trade-offs — the frame's own
definition of an architecturally significant decision. The Frozen Caveman
antipattern is the warning that the lazy default can rot into defaulting to pet
tech; the 20-minute rule is how a lazy senior dev knows the ladder's rungs exist.

## Worked example
Notifications on checkout: (A) synchronous HTTP call inside the order flow, vs
(B) publish to a queue, consume asynchronously. Factors weighted for THIS context
(3-service system, checkout latency is a core metric, no ops staff to watch a
broker):

| Factor (weight) | A sync call | B async queue |
|---|---|---|
| Checkout latency (5) | − blocks order on broker | + decouples |
| Fault tolerance (3) | − notification loss blocks order | + retry/backoff |
| Ops burden (4) | + nothing new to run | − broker to operate |
| Scalability (2) | − bursts queue up | + elastic |

Weighted, B's decoupling does not beat its ops burden on the current team. But
run TRIZ before settling [Separation in condition]: customer-facing confirmation
stays synchronous (they must see the result), marketing digests go to the queue.
Record the ADR [ADR] with the matrix and the re-evaluation trigger (a 4th
service, or someone owns the broker). Add a fitness function [Fitness function]:
"no notification producer may add a third transport" (ArchUnit).

## How it feeds the pipeline
Powers **stage 5 (Resolve contradictions)** — the verification instrument: after
TRIZ separation attempts, score the residual candidates with the weighted matrix;
the Three Laws decide what is even architecturally significant. Also feeds
**stage 8 (Verify, record, ship)** — ADR-lite records why-beats-how, fitness
functions are tests. Feeds **stage 1** (characteristics extraction is the frame),
**stage 2** (the deliberate-escalation trigger; last responsible moment ≈ YAGNI),
**stage 3** (IFR reconciliation: generation vs evaluation), **stage 4**
(component-based thinking = structure from data at system level), and **stage 7**
(risk storming + fitness-function governance as the audit). Cross-links:
`method-map.md` (system-level path), `triz-for-code.md` (contradiction/separation
engine), `domain-modeling.md` (domain fork — bounded contexts ≈ separation in
condition), `sustainable-engineering.md` (same evaluation lens at scale),
`red-flags.md` (design audit), `legacy-change.md` (characterization tests as
fitness functions). triz-innovation: `references/software-triz.md`,
`branches/fields/software`.

## Source
Original operational synthesis from the software-architecture literature.
