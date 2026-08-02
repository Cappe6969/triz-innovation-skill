# Trends of Engineering System Evolution (TESE) & the S-Curve

TRIZ claims that technical (and many non-technical) systems evolve along
**predictable trends**, not randomly. If you know where a system sits on these
trends, you can **predict its next move and leapfrog competitors** instead of
optimizing a dying design. Use this for "where is this headed / how do we
reinvent this" questions — stage 6 (IFR) and stage 7 (method selection).

## The S-curve (system maturity)

Every system follows an S-shaped performance-vs-effort curve through 4 stages:

| Stage | Signs | What to do |
|---|---|---|
| **1. Infancy** | low performance, high cost, unreliable, few patents | invest if the IFR is compelling; expect rough edges |
| **2. Growth** | rapid improvement, investment pours in, patents rise | optimize hard, scale, capture market |
| **3. Maturity** | gains shrink, cost of each improvement rises, patent *quantity* peaks then falls while patent *level* drops (minor tweaks) | stop polishing — look for the **next S-curve** |
| **4. Decline** | performance plateaus, replaced by a new principle | jump to a new operating principle (new S-curve) |

**Diagnostic:** if you're spending more and more to gain less and less, and recent
"innovations" are cosmetic, you're in late maturity — the leverage is in switching
curves, not tuning this one. The classifier hints at the stage:
`python .agents/skills/triz-innovation/scripts/triz_evolution.py --signals "gains shrinking, cost rising, minor tweaks"`.

## The 8 trends (laws) of evolution

Each trend is a direction systems tend to move. Ask: *"Where is my system on this
trend, and what's the next step along it?"*

1. **Increasing ideality.** More useful function per unit cost/harm; functions get
   delivered with fewer or no added components (toward IFR). The master trend.
2. **Non-uniform development of parts.** Sub-systems evolve at different rates; the
   slowest-evolving part becomes the bottleneck and the next contradiction. Find it.
3. **Increasing dynamism & controllability.** Rigid → jointed → flexible → fluid/
   field; manual → automatic → adaptive. Static things become tunable in real time.
4. **Increasing complexity then simplification (mono → bi → poly → trim).** Systems
   add parts/functions (mono→bi→poly-system), then **trim** back to fewer parts
   carrying more functions. Know which half you're in.
5. **Matching & mismatching of parts.** Parts evolve from unmatched → matched →
   dynamically matched → deliberately mismatched to exploit a difference.
6. **Transition to the super-system & micro-level.** Mature systems merge into a
   bigger system or drop to act at the micro/field level (cf. Su-Field Class 3).
7. **Decreasing human involvement.** Functions migrate from human → tool → fully
   automatic/self-service. Each manual step is a future automation.
8. **Uneven flow / increasing field controllability.** Energy/substance/information
   conduction improves; fields shift toward more controllable ones (mechanical →
   electromagnetic), flows become smoother and lossless.

## How to run an evolution analysis
1. **Place the system on the S-curve** (which stage? evidence?).
2. **Walk the 8 trends**: for each, state where the system is now and the *next
   step* along that trend. Most systems are "behind" on 2–3 trends — those are the
   cheap wins.
3. **Combine with System Operator** (`references/system-operator.md`): the "future"
   column of the 9 windows is exactly a trends forecast.
4. **Convert forecasts into solutions** in stage 8, tagged `[Trend 3: dynamism]`,
   `[Trend 7: less human involvement]`, etc.

## Worked example (software)
A monolithic deploy script (manual, rigid, one big step):
- Trend 7 (less human involvement): manual → one-click → automatic on merge → self-
  healing rollback. Next step: auto-deploy on green CI.
- Trend 3 (dynamism): one fixed pipeline → configurable per-service → adapts to
  change size. Next step: risk-based pipeline that scales checks to the diff.
- Trend 4 (mono→poly→trim): one script doing build+test+deploy → split stages →
  then trim duplicated setup into a shared cached layer.
Pick the trend with the best ideality gain for the least effort, then test it.
