# domain-modeling

Domain-driven modeling: let the business domain drive design decisions instead
of technology fashion. Reach for it at the start of a system, feature, or
modernization to decide where engineering effort goes and to split one ambiguous
model into consistent, context-scoped models.

## When to use it
- Starting a new system or feature — decide how much engineering each part
  deserves *before* building anything.
- Two experts (or teams) use the same word for different things, or different
  words for the same thing — the "telephone game" signal that knowledge is being
  lost in translation.
- Integrating with a legacy, external, or third-party system whose model you
  cannot change.
- A model keeps producing ambiguity or contradictions the more you use it.
- Choosing a subdomain's business logic pattern, and its architecture + tests.
- Modernizing or refactoring legacy code — you want to *evolve* the model, not
  rewrite it.
- Route: `method-map.md` sends "system-level decision (architecture)" here
  (stages 1 → 3 → 5 → 8 + ADR).

## Core method

### 1. Type the subdomains [Subdomain typing]
Classify every area of the business before building. This is an **investment
filter**: effort concentrates on the core and is consciously withheld from
everything else — the same trim as TRIZ focusing on the main useful function.

| Type | Competitive value | Complexity | Build vs buy | Engineering investment |
|---|---|---|---|---|
| Core [Core subdomain] | Differentiator — why customers choose you | High: rules, invariants, algorithms | In-house, best engineers | Full method: tactical blocks, deep modeling |
| Generic [Generic subdomain] | Neutral — a solved problem | Hard but solvable off the shelf | Buy / adopt existing tooling | Integration only — an ACL at the edge |
| Supporting [Supporting subdomain] | Neutral — back-office CRUD/ETL | Simple | Rapid framework, cut corners | Minimum code |

### 2. Build the ubiquitous language [Ubiquitous language]
- One term, exactly one meaning; no jargon, no synonyms. Use it in code, tests,
  docs, and conversation.
- Cultivate it with domain experts — they are a resource; mining their tacit
  vocabulary is resource analysis, not overhead.
- When the same word carries two meanings, that is the signal to *split* (step
  3), never to compromise.

### 3. Split into bounded contexts [Bounded context]
A bounded context is the **consistency boundary of the language**: the model
inside stays internally consistent even where it contradicts a neighbor.

- Split when one model keeps producing ambiguity — marketing `Lead` vs sales
  `Lead` are two models, not one.
- Start **wide** around volatile core subdomains and decompose as knowledge
  grows; logical boundaries are cheaper to move than physical ones [Wide
  boundaries first].
- Draw the **context map** [Context map]: name each context, the type of each
  subdomain, and the integration pattern on each edge.

### 4. Integrate contexts without leaking [Anticorruption layer]
| Edge pattern | Direction | Rule |
|---|---|---|
| Anticorruption layer [Anticorruption layer] | inbound foreign model | translate between contexts so a legacy/third-party model cannot leak into yours |
| Open-host service + published language [Open-host service] [Published language] | outbound | expose your model via a fixed published language; others translate to it |
| Shared kernel | both ways | only for a genuinely shared, small core — trim it hard |
| Conformist | inbound | adopt the upstream model when you cannot influence it |

### 5. Tactical building blocks (the core-subdomain case)
| Block | Models | Rule |
|---|---|---|
| Value object [Value object] | an attribute of a thing | immutable, self-validating, encapsulates its own logic; kills primitive obsession |
| Entity [Entity] | identity over time | identity survives attribute changes; identity ≠ values |
| Aggregate [Aggregate] | transaction / consistency boundary | invariants enforced at the root; one aggregate per transaction |
| Domain service [Domain service] | logic that fits no single entity | stateless; orchestrates across entities/aggregates |
| Repository | persistence | collection-like interface the domain owns |
| Domain event | something that happened | input to other aggregates and policies, avoiding cross-aggregate coupling |

### 6. Business-logic pattern decision tree [Pattern ladder]
The pattern is the *smallest tool adequate to the logic* — YAGNI applied to
design. Pick a feature of the logic, get a pattern.

| Feature of the logic | Pattern |
|---|---|
| Money / audit / deep-analysis needs | Event-sourced domain model |
| Complex rules, invariants, algorithms | Domain model (tactical blocks) |
| Complex data structures, simple rules | Active record |
| Nothing demanding | Transaction script |

**Sanity check:** the chosen pattern should match the subdomain type you
assigned in step 1. A "supporting" subdomain with an event-sourced model is a
contradiction — resolve it, don't accept it.

### 7. Pair the architecture and the testing shape [Architecture pairing] [Testing shape]
| Pattern | Architecture | Test emphasis |
|---|---|---|
| Event sourcing | CQRS | — |
| Domain model | Ports & adapters | pyramid (unit-heavy) |
| Active record | Layered + application/service layer | diamond (integration-heavy) |
| Transaction script | Minimal three-layer | reversed pyramid (end-to-end) |

### 8. EventStorming the domain [EventStorming]
A facilitated workshop (whole team + experts, sticky notes) to co-discover the
domain and its boundaries. Ten steps, in order:
1. **Unstructured exploration** — everyone dumps candidate events freely.
2. **Timeline** — arrange them chronologically.
3. **Pain points** — annotate the timeline.
4. **Pivotal events** — mark the load-bearing ones.
5. **Commands** — what triggers each event.
6. **Policies** — reactive business logic (when X, then Y).
7. **Read models** — what actors need to see.
8. **External systems** — integration points.
9. **Aggregates** — group events into consistency boundaries.
10. **Bounded contexts** — draw the seams where the workshop split the model.

### 9. Evolve incrementally [Incremental evolution]
- Never big-rewrite; keep the system working throughout.
- Order of introduction: value objects first (cheapest, self-documenting),
  then aggregate boundaries, then richer patterns only if the domain demands.
- Hold an anticorruption layer in place for the whole migration so the legacy
  model cannot contaminate the new one.
- Re-type subdomains as the business shifts (core ↔ generic ↔ supporting) and
  move boundaries to follow.

### TRIZ mapping
| Software concept | TRIZ concept |
|---|---|
| Subdomain typing + pattern heuristics | Standard-solution tables — problem features select a solution, exactly how TRIZ maps contradiction types to principles |
| Bounded contexts | Segmentation (IP-1) / separation — split the conflict instead of compromising; a jack-of-all-trades model is the harmful compromise TRIZ forbids |
| Model = "just enough" [Model trimming] | IFR + trimming — keep only what the problem needs, omit the rest; the map is not the territory |
| Anticorruption layer | Taking out the disturbing part (IP-2) — isolate harmful coupling at a boundary instead of living with it |
| Generic subdomain → buy | Existing resource / cheap short-living solution (IP-27) — adopt, don't re-invent |
| Ubiquitous language + EventStorming | Resource analysis — mine the free resource of experts' tacit knowledge |
| Wide boundaries first | Leave reserve/dynamism — hedge against being wrong rather than committing to a rigid ideal |

### Ponytail reconciliation
- The pattern ladder **is** the ponytail ladder in design terms: start at
  transaction script (minimum code), escalate to active record → domain model →
  event-sourced only when the problem demands it.
- Generic subdomains = the "existing dep" rung (buy); supporting subdomains =
  minimum code, corners cut on purpose.
- Tension: domain modeling front-loads analysis (language, modeling,
  EventStorming) where ponytail says code-first. Reconciliation: **the code IS
  the model** — value
  objects make code self-documenting, collapsing explanation toward zero.
- Sell a pattern with logic, not authority [Logic over authority].
- Counter-signal to watch: money/audit domains genuinely escalate the ladder —
  the senior move is recognizing when the *problem*, not fashion, demands the
  heavy pattern.

## Worked example
A legacy monolith uses one shared `Customer` record, but marketing and sales
mean different things by `Lead`. The team plans a rewrite in a new framework —
technology fashion, not a domain need.

1. Reframe: this is a domain question, not a technology question. [Subdomain typing]
2. EventStorm with the experts → the two vocabularies collide around `Lead`.
   [EventStorming]
3. Split wide: a marketing context and a sales context, one term one meaning in
   each. [Wide boundaries first] [Ubiquitous language]
4. Type each area: sales-customer = core (differentiator), billing = generic
   (buy it), reporting = supporting (rapid CRUD). [Subdomain typing]
5. Draw an anticorruption layer between the new sales model and the legacy
   `Customer` table so the old model cannot leak in. [Anticorruption layer]
6. Pick patterns per context: sales = domain model (tactical blocks), reporting
   = transaction script, billing = ACL around the bought tool. [Pattern ladder]
7. Migrate incrementally — value objects first, the ACL held in place until the
   legacy model is gone. [Incremental evolution]

## How it feeds the pipeline
- **Stage 1 — Frame the task**: subdomain typing is the neutral restatement of
  what the business needs; it fixes investment before design. [Subdomain typing]
- **Stage 2 — Climb the ponytail ladder**: the pattern tree is the ladder
  (transaction script up to event sourcing); generic subdomains are the
  existing-dep rung, supporting subdomains the minimum-code rung.
- **Stage 3 — Sketch the IFR**: a model that is "just enough" is the IFR of the
  domain; the deep module's small interface parallels the encapsulated bounded
  context. [Model trimming] [Deep module]
- **Stage 4 — Structure from data**: EventStorming read models and value objects
  define the data shape before code. [EventStorming] [Value object]
- **Stage 5 — Resolve contradictions**: bounded contexts segment the "one
  language vs conflicting expert models" contradiction instead of compromising;
  the ACL takes out the harmful coupling. [Bounded context] [Anticorruption layer]
- **Stage 6 — Make the minimal safe change**: incremental evolution (value
  objects first, ACL during migration) is the legacy change algorithm at the
  domain level. [Incremental evolution]
- **Stage 7 — Review with red flags**: audit for model leakage across contexts,
  ambiguous terms, and pattern over-engineering (event sourcing without a
  money/audit driver). [Contradiction]
- **Stage 8 — Verify, record, ship**: the testing-shape heuristic picks the
  verification strategy; a context boundary is an ADR-lite decision.
  [Testing shape]

Cross-links — siblings: `method-map.md` (the router that sends system-level
decisions here), `architecture-tradeoffs.md` (boundaries + ADRs),
`deep-modules.md` (encapsulated complexity ↔ aggregates/contexts),
`rewrite-ladder.md`, `design-recipe.md` (data-first ↔ value objects),
`red-flags.md`. TRIZ: `software-triz.md`, `ideal-final-result.md`,
`trimming.md`, `resource-analysis.md`, `contradiction-analysis.md`,
`branches/fields/software` (under `triz-innovation/`).

## Source
Original operational synthesis from the domain-modeling literature.
