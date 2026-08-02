# Software TRIZ

TRIZ for software architecture, performance, reliability, UX, and app problems.
The contradictions are real even though there are no atoms — latency vs cost,
flexibility vs simplicity, consistency vs availability.

## Translate the core concepts
| Engineering | Software |
|---|---|
| Component | Service, module, layer, data store, job, endpoint, UI element |
| Tool → Action → Object | Producer → operation → consumer/data |
| Harmful function | Coupling, latency, flakiness, tech debt, alert fatigue |
| Insufficient | Slow, under-tested, low coverage, missing validation |
| Excessive | Over-fetching, chatty APIs, notification spam, over-engineering |
| Resource | Cache, idle CPU, logs, existing fields, the platform/OS, the client device |

## Recurring software contradictions → principles
- **Latency vs cost** → [IP-10 Prior action] precompute/cache; [IP-19 Periodic] batch; [IP-2 Taking out] move work off the hot path.
- **Consistency vs availability** (CAP) → [IP-15 Dynamics] tunable consistency; [IP-13 Other way round] eventual + reconcile.
- **Flexibility vs simplicity** → [IP-1 Segmentation] plugins; [IP-6 Universality] one extension point; [IP-25 Self-service] config over code.
- **Coupling vs performance** → [IP-24 Intermediary] queue/broker; [IP-7 Nesting] bounded contexts.
- **Coverage vs speed of delivery** → [IP-16 Partial action] test the risky 20%; [IP-10] test fixtures prepared once.
- **Engagement vs annoyance** (notifications) → physical contradiction (present/absent) → separation in **time/condition** + [IP-15 Dynamics], [IP-23 Feedback].

## Software-specific moves
- **Trimming a service:** can the client, the DB, or the platform do the job
  (Rule C)? Can the need disappear entirely (Rule A — e.g., remove a sync step by
  making the source of truth singular)?
- **Self-service / self-X (IP-25):** self-healing retries, self-tuning autoscalers,
  self-validating schemas, self-logging via existing telemetry.
- **Resource-first:** before adding infra, inventory caches, logs, unused columns,
  client compute, and platform APIs (`resource-analysis.md`).
- **System Operator for architecture:** sub (libraries) / system (service) / super
  (platform & ecosystem) across past/present/future — catches "the platform now
  does this, delete our code" opportunities.

## IFR for software
The function executes with **zero added latency, zero new service, zero
maintenance** — i.e., it's already handled by data/compute you have. Push designs
toward fewer moving parts; every new service is denominator weight.

## Test/experiment bias
Software changes are cheap to make reversible: feature flags, canary, shadow
traffic, A/B. The stage-10 experiment should almost always be a flagged, metric-
gated rollout with an explicit success threshold and rollback trigger.

## Cross-link
For the coding-method skill's code-side bridge (8-stage pipeline, ponytail
ladder, red flags), see
`../coding-method/references/triz-for-code.md`.
