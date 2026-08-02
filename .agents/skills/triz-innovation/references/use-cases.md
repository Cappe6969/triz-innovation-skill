# Use cases

> Worked examples showing each field branch in action — how `--branch <id>` tunes the same TRIZ core to an ultra-specific task in that field.

## Mechanical / hardware

**Problem:** The gearbox must transmit more torque, but the housing cannot grow
heavier or larger.

**Branch detection:** The router matched `torque`, `gearbox` from the
`Mechanical TRIZ` rule; the `--branch mechanical` filter isolates that rule and
skips the other domains.

**Route:** `python .agents/skills/triz-innovation/scripts/triz.py --branch mechanical route "The gearbox must transmit more torque, but the housing cannot grow heavier or larger."`
Live output — top methods: Engineering Contradiction + 40 Inventive Principles
(7), then Mechanical TRIZ (4). The "must ... but" trade-off is detected as a
contradiction (score 7); the mechanical keywords add the domain rule (2 keyword
hits × 2).

**Parameter translation:** `Force (Intensity)` → *torque / load / clamping
force*; `Weight of moving object` → *mass / moment of inertia of the moving
part*; `Stress or pressure` → *contact stress / preload*. Improving = 10 Force
(Intensity), worsening = 1 Weight of moving object.

**Solution via soft principles:**
- `IP-35` (Parameter Changes) — case-harden the gear teeth so each tooth
  carries more torque without adding mass.
- `IP-1` (Segmentation) — split the single heavy gear into a cluster of smaller
  meshing stages so the load spreads over more teeth.
- `IP-24` (Intermediary) — an oil-lubricated intermediate gear redistributes
  contact stress away from the weak zone.

**Result:** case-harden the teeth `[IP-35 Parameter Changes]` and split the
single stage into a cluster `[IP-1 Segmentation]` — torque up, mass unchanged.

## Data science / ML / AI

**Problem:** The model must be more accurate, but adding features makes training
too slow.

**Branch detection:** The router matched `model`, `features`, `training` from
the `Data Science TRIZ` rule; the `--branch datascience` filter isolates it.

**Route:** `python .agents/skills/triz-innovation/scripts/triz.py --branch datascience route "The model must be more accurate, but adding features makes training too slow."`
Live output — top methods: Engineering Contradiction + 40 Inventive Principles
(7), Physical Contradiction + Separation (6), then Data Science TRIZ (4), with
Resource Analysis, Ideality / IFR, and System Operator (9 Windows) suggested as
physical-contradiction companions. The text also reads as a physical
contradiction ("must be ... but"), which is why the separation route appears.

**Parameter translation:** `Measurement accuracy` → *model accuracy / F1 /
precision-recall*; `Speed` → *training time / inference latency / throughput*;
`Quantity of substance` → *dataset size / feature count*. Improving = 28
Measurement accuracy, worsening = 21 Power (compute).

**Solution via soft principles:**
- `IP-10` (Preliminary Action) — compute the new features *before* training as a
  background job and cache them in a feature store, so training never waits on
  feature engineering.
- `IP-2` (Taking out) — train the full model offline, then distill a smaller
  student model for the hot path.
- `IP-1` (Segmentation) — split into specialist sub-models (mixture of experts),
  each cheaper to train than the whole.

**Result:** cache pre-computed features `[IP-10 Preliminary Action]` and serve a
distilled student model `[IP-2 Taking out]` — accuracy up, training wall-clock
flat. The two demands (many features for accuracy, few for speed) separate in
time: train on the full feature set, serve the distilled model `[Separation in
time]`.

## Marketing / growth

**Problem:** The landing page must convert more visitors, but adding a
data-capture form hurts sign-ups.

**Branch detection:** The router matched `landing page` from the `Marketing TRIZ`
rule; the `--branch marketing` filter isolates it.

**Route:** `python .agents/skills/triz-innovation/scripts/triz.py --branch marketing route "The landing page must convert more visitors, but adding a data-capture form hurts sign-ups."`
Live output — top methods: Engineering Contradiction + 40 Inventive Principles
(7), then Marketing TRIZ (2). The conversion vs. friction trade-off reads as a
contradiction; the single `landing page` keyword hit adds the domain rule.

**Parameter translation:** `Speed` → *campaign launch time / growth velocity*;
`Loss of time` → *time wasted on low-intent leads*; `Difficulty of detecting and
measuring` → *attribution accuracy*. The form is the friction: improving
conversion (a marketing-specific goal) worsens data capture.

**Solution via soft principles:**
- `IP-2` (Taking out) — move the form off the critical path: progressive
  profiling, one optional field per visit instead of a full form.
- `IP-25` (Self-service) — social login / one-tap sign-up so the visitor
  self-registers; the profile completes itself.
- `IP-10` (Preliminary Action) — capture the data later: a nurtured follow-up
  email asks for the missing fields after the conversion moment.

**Result:** drop the full form for one optional field + social login
`[IP-2 Taking out]` `[IP-25 Self-service]` — conversion holds, data still
accumulates post-signup.

## Supply chain / logistics

**Problem:** Lead time must drop, but holding more safety stock raises inventory
cost.

**Branch detection:** The router matched `lead time`, `safety stock`, `stock`,
`inventory` from the `Supply Chain TRIZ` rule (4 hits); the `--branch
supplychain` filter isolates it.

**Route:** `python .agents/skills/triz-innovation/scripts/triz.py --branch supplychain route "Lead time must drop, but holding more safety stock raises inventory cost."`
Live output — top methods: Supply Chain TRIZ (8, 4 keyword hits × 2), then
Engineering Contradiction + 40 Inventive Principles (7), then Marketing TRIZ (2
— the word "lead" in "lead time" also matches the marketing `lead` keyword; an
expected overlap, see the branch note). Lead time vs. inventory is a classic
contradiction.

**Parameter translation:** `Speed` → *lead time / delivery speed / throughput*;
`Quantity of substance` → *inventory volume / order quantity / lot size*;
`Loss of time` → *idle time / waiting at the dock*. Improving = 9 Speed,
worsening = 26 Quantity of substance.

**Solution via soft principles:**
- `IP-24` (Intermediary) — a cross-docking hub: goods flow through the node
  without sitting in storage, so lead time drops without holding stock.
- `IP-2` (Taking out) — dual sourcing: take the slow supplier off the critical
  path instead of padding inventory for its variability.
- `IP-10` (Preliminary Action) — forecast-driven pre-staging: build the buffer
  *before* the peak in cheaper upstream capacity, not at the last mile.

**Result:** cross-dock the fast movers `[IP-24 Intermediary]` and pre-stage on
forecast `[IP-10 Preliminary Action]` — lead time down, inventory flat.
