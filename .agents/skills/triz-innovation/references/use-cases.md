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

## Energy / power

**Problem:** The inverter must deliver more peak power, but the bigger cooling
system no longer fits in the cabinet.

**Branch detection:** The router matched `inverter` from the `Energy TRIZ`
rule; the `--branch energy` filter isolates that rule and skips the other
domains.

**Route:** `python .agents/skills/triz-innovation/scripts/triz.py --branch energy route "The inverter must deliver more peak power, but the bigger cooling system no longer fits in the cabinet."`
Live output — top methods: Engineering Contradiction + 40 Inventive Principles
(7), then Energy TRIZ (2). The "must ... but" trade-off is detected as a
contradiction (score 7); the `inverter` keyword hit adds the domain rule (1
keyword hit × 2).

**Parameter translation:** `Power` → *rated / peak power output*; `Loss of
energy` → *conversion losses, heat, line losses*; `Temperature` → *junction
temperature of the power devices*. Improving = 21 Power, worsening = 17
Temperature.

**Solution via soft principles:**
- `IP-15` (Dynamization) — run the converter in a derated mode when the cabinet
  heat budget is exceeded, so full peak power returns as soon as the thermal
  mass cools.
- `IP-1` (Segmentation) — split the single large inverter into paralleled
  modules that share the peak and cool in turns.
- `IP-35` (Parameter Changes) — swap the cooling medium for a phase-change
  thermal buffer that absorbs the peak-heat burst without a bigger fan.

**Result:** parallel modular converters `[IP-1 Segmentation]` with a
phase-change thermal buffer `[IP-35 Parameter Changes]` — peak power up,
cabinet unchanged.

## Education / learning

**Problem:** Students must retain more of the lesson, but adding review time
leaves no room for new content.

**Branch detection:** The router matched `students`, `lesson` from the
`Education TRIZ` rule; the `--branch education` filter isolates it.

**Route:** `python .agents/skills/triz-innovation/scripts/triz.py --branch education route "Students must retain more of the lesson, but adding review time leaves no room for new content."`
Live output — top methods: Engineering Contradiction + 40 Inventive Principles
(7), then Education TRIZ (4). The "must ... but" trade-off is detected as a
contradiction (score 7); the two education keyword hits add the domain rule (2
hits × 2).

**Parameter translation:** `Loss of information` → *knowledge decay / what
students forget*; `Loss of time` → *idle class time / review overhead*;
`Quantity of substance` → *content volume / seat hours*. Improving = 24 Loss of
information, worsening = 25 Loss of time.

**Solution via soft principles:**
- `IP-19` (Periodic Action) — spaced repetition: schedule short review bursts
  at growing intervals so retention climbs without a dedicated review block.
- `IP-2` (Taking out) — move the explanation out of the live lecture to a
  video; class time is then freed for retrieval practice.
- `IP-10` (Preliminary Action) — pre-teach the key vocabulary before the
  lesson so new content lands on prepared ground.

**Result:** spaced-repetition review bursts `[IP-19 Periodic Action]` and
pre-taught vocabulary `[IP-10 Preliminary Action]` — retention up, new content
still fits.

## Construction / civil

**Problem:** The concrete must finish curing faster, but accelerating the cure
makes the slab brittle and prone to cracking.

**Branch detection:** The router matched `concrete`, `curing` from the
`Construction TRIZ` rule; the `--branch construction` filter isolates it.

**Route:** `python .agents/skills/triz-innovation/scripts/triz.py --branch construction route "The concrete must finish curing faster, but accelerating the cure makes the slab brittle and prone to cracking."`
Live output — top methods: Engineering Contradiction + 40 Inventive Principles
(4), Construction TRIZ (4). The "must ... but" trade-off is detected as a
contradiction; the `concrete` + `curing` keyword hits add the domain rule (2
hits × 2).

**Parameter translation:** `Loss of time` → *construction schedule / curing
wait*; `Strength` → *concrete grade / early compressive strength*;
`Object-affected harmful factors` → *shrinkage / thermal cracking / freeze-thaw*.
Improving = 25 Loss of time, worsening = 14 Strength.

**Solution via soft principles:**
- `IP-24` (Intermediary) — a curing compound or sacrificial membrane holds the
  moisture so the hydration front advances evenly and fast.
- `IP-3` (Local Quality) — use accelerating admixtures only in the zone that
  must reach early strength; leave the rest on the normal mix.
- `IP-35` (Parameter Changes) — raise the curing temperature locally with
  heated formwork, but cool the surface gradually to stop thermal shock.

**Result:** curing compound + heated formwork `[IP-24 Intermediary]`
`[IP-35 Parameter Changes]` — the slab reaches stripping strength sooner,
without the brittle, crack-prone fast cure.

## Robotics / IoT / embedded

**Problem:** The robot arm must move faster, but higher speed causes oscillation
at the end effector.

**Branch detection:** The router matched `robot arm`, `oscillation`,
`end effector` from the `Robotics TRIZ` rule; the `--branch robotics` filter
isolates it.

**Route:** `python .agents/skills/triz-innovation/scripts/triz.py --branch robotics route "The robot arm must move faster, but higher speed causes oscillation at the end effector."`
Live output — top methods: Robotics TRIZ (8), then Engineering Contradiction +
40 Inventive Principles (4). The `robot arm`, `oscillation` and `end effector`
keyword hits add the domain rule (score 8); the "must ... but" wording is also
read as a contradiction.

**Parameter translation:** `Speed` → *cycle time / joint velocity*; `Stability
of the object's composition` → *control stability / oscillation / drift*;
`Measurement accuracy` → *end-effector pose error / encoder resolution*.
Improving = 9 Speed, worsening = 13 Stability of the object's composition.

**Solution via soft principles:**
- `IP-15` (Dynamization) — adaptive gains / impedance control that stiffens on
  contact and softens during fast moves, damping the oscillation.
- `IP-10` (Preliminary Action) — pre-compute and smooth the trajectory before
  the move, so the controller never excites the resonance mode.
- `IP-13` (The Other Way Around) — invert the loop: close the servo on the
  residual error and cancel the oscillation with an opposing signal.

**Result:** adaptive impedance control `[IP-15 Dynamization]` plus pre-smoothed
trajectories `[IP-10 Preliminary Action]` — cycle time down, end-effector
settles without oscillation.
