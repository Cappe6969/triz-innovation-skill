# Scientific Effects (Function → Effect database)

Often the hard part isn't *what* you want to do but *how* to do it cheaply. The
TRIZ "effects" approach flips the search: start from the **function** you need
(verb + parameter), then pull the known **effects** (physical, chemical,
geometric — and in other domains, behavioral/economic) that deliver it. This is
how you find non-obvious mechanisms already proven elsewhere.

> Use inside ARIZ Part 5 and stage 8 when you have a clear required action ("move
> liquid without a pump", "detect a crack without disassembly", "keep users
> engaged without notifications") but no mechanism yet.

## How to use
1. State the function as **action + object + condition**: "heat a small region
   without contact", "hold a part without a clamp", "measure level without a
   sensor inside the tank".
2. Pick the **function family** below and scan its effects.
3. For each candidate effect, ask: *do I have the resource it needs?* (cf.
   `references/resource-analysis.md`). Keep the ones that use resources already
   present.
4. Tag the solution `[Effect: capillarity]`, `[Effect: resonance]`, etc.

## Function families → effects (starter catalog)

**Move / transport a substance:** capillarity, osmosis, electro-/magneto-phoresis,
gravity & siphon, thermal convection, pressure difference, ultrasonic streaming,
diffusion. *(Non-engineering: incentives, defaults, social proof move behavior.)*

**Hold / fix / position:** magnetism, electrostatics, vacuum/suction, freezing
(phase change to solid), surface tension, friction, interference/snap geometry,
gyroscopic stiffening.

**Heat / cool a region:** Joule heating, induction, Peltier effect, evaporative
cooling, exothermic reaction, microwave/dielectric heating, radiative cooling.

**Detect / measure:** resonance & natural frequency shift, thermal imaging,
luminescence/fluorescent markers, change of color/phase indicators, capacitance
change, Hall effect, Doppler shift, measuring a *derivative* or a *difference*.

**Change properties on demand:** phase transitions, shape-memory alloys/polymers,
thixotropy (gel↔liquid under shear), magneto-/electro-rheological fluids,
photochromism/thermochromism, piezoelectricity (force↔voltage).

**Generate force / motion:** thermal expansion, piezo actuation, magnetostriction,
shape-memory, electrostatic/magnetic attraction, pressure/phase-change expansion,
bimetallic bending.

**Separate / mix / purify:** centrifugation, electrophoresis, magnetic separation,
distillation/phase change, filtration via porous/capillary media, flotation,
adsorption.

## Cross-domain translation
The same move maps across domains: "use an environmental field for free" →
software: use the OS/browser's existing events instead of polling; business: use
existing customer behavior (defaults, habits) instead of new campaigns; rehab: use
the patient's daily routine as the trigger (self-service field) instead of an added
reminder. The discipline is identical: name the function, borrow a proven effect,
check the resource is already there.
