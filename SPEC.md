# Use Cases + New Domain Branches (ship build 3)

Build on top of master (`9a6c849`, Phase 2 merged). Phase 2 established the
branch architecture (`branches/fields/<id>/branch.json` × `branches/langs/<lang>/`
with 4 fields + en/it) and a `triz_branches.py` registry. Phase 3 adds the
four user-selected field branches — **mechanical/hardware, data science/ML/AI,
marketing/growth, supply chain/logistics** — with worked use cases, and makes
branch handling data-driven so adding a branch no longer requires editing the
dispatcher or router.

Two workstreams, same split as Phase 2:

- **A — New field branches + use cases (Architect-authored content).** The four
  `branches/fields/<id>/branch.json` data files and `references/use-cases.md`
  are authored by the Architect and shipped in the working tree before the
  build starts. Per ADR-0011, content synthesis is Architect work — the
  Carpenter MUST NOT modify these files (the Reviewer verifies they are
  untouched and schema-valid).
- **B — Data-driven plumbing, router rules, docs, tests (Carpenter-built).**
  Registry canonical order, dispatcher + router branch validation derived from
  the registry, four new router domain rules, SKILL.md documentation, tests,
  and the `.agents` mirror rebuild.

## Requirements

### R1 — Four new field branches (Architect-authored; Carpenter MUST NOT modify)

Files already present in the working tree, one per new domain:

- `branches/fields/mechanical/branch.json` — id `mechanical`, name "Mechanical TRIZ",
  `name_it` "TRIZ meccanico / hardware", keywords covering torque, vibration,
  fatigue, tolerance, wear, friction, bearings, stiffness, thermal, machining.
- `branches/fields/datascience/branch.json` — id `datascience`, name
  "Data Science TRIZ", `name_it` "TRIZ data science e AI", keywords covering
  model/training/dataset/accuracy/overfitting/feature/inference/bias.
- `branches/fields/marketing/branch.json` — id `marketing`, name "Marketing TRIZ",
  `name_it` "TRIZ marketing e crescita", keywords covering conversion/funnel/
  campaign/churn/retention/audience/persona/pricing/growth.
- `branches/fields/supplychain/branch.json` — id `supplychain`, name
  "Supply Chain TRIZ", `name_it` "TRIZ supply chain e logistica", keywords
  covering inventory/lead time/demand/forecast/warehouse/supplier/stockout/
  shipping/replenishment.

Every file follows the exact Phase-2 schema (all keys present):

```json
{
  "id": "<id>",
  "name": "...",
  "name_it": "...",
  "description": "...",
  "keywords": ["..."],
  "parameter_map": {"<39-param name>": "<domain translation>", "...": "..."},
  "principle_soft": {"<IP number>": "<soft reading>", "...": "..."},
  "examples": ["..."]
}
```

Constraints (presence + canonical keys enforced by `triz_branches.py validate()`;
the ≥ counts are authoring guidance for new branches — the Phase 2 branches
legitimately carry fewer):
- `id` equals the directory name; `name_it` present.
- `keywords` non-empty (≥ 10 entries for new branches, English + Italian where
  sensible).
- `parameter_map` non-empty (≥ 5 mappings for new branches) and `principle_soft`
  non-empty (≥ 5 readings for new branches); every `parameter_map` key must be a
  canonical 39-parameter name from `scripts/data/parameters_39.csv`.
- `examples` non-empty (≥ 2 for new branches).
- `general` must NOT define `parameter_map`/`principle_soft` (it IS the
  canonical core).

### R2 — Registry canonical order

In `scripts/triz_branches.py`, extend `_FIELD_IDS` (the canonical ordering) to:

```python
_FIELD_IDS = ["general", "business", "software", "rehab",
              "mechanical", "datascience", "marketing", "supplychain"]
```

`list_branches()` must then report exactly 8 fields in that order. The
`resolve`/`validate`/`check` behavior is unchanged and must pass for all 8.

### R3 — Dispatcher branch validation becomes data-driven

In `scripts/triz.py`:

- Delete the hardcoded `_VALID_BRANCHES = ("general", "business", "software", "rehab")`.
- Add `from triz_branches import list_branches` (same-directory import, exactly
  like `triz_router.py` already does) and derive the valid set at flag-parse
  time: `_valid_branches()` → `list_branches()["fields"]`. `_parse_global_flags`
  calls it instead of reading a constant.
- Keep `--lang` values `("en", "it", "auto")` as-is (a hardcoded list is fine;
  languages are a closed, code-defined set).
- Update the module docstring: the global `--branch` line and the "unknown
  value rejected" note now say "any registered field branch" instead of
  enumerating the ids.
- Behavior: `python triz.py --branch mechanical route "..."` must exit 0 and
  route with the mechanical branch; `--branch nonsense` still exits 1 with a
  clear error.

This resolves the round-1 Medium finding "field and language branch data is not
data-driven": adding a branch now only requires dropping a `branch.json` file.

### R4 — Router: four new domain rules + data-driven branch validation

In `scripts/triz_router.py`:

1. **Four new RULES entries** appended after the existing domain rules, each
   with the method name and keyword set given below (score 2, reason
   "<domain> domain keyword"). Use these EXACT keyword lists:

   - `Mechanical TRIZ`:
     `("torque", "coppia", "vibration", "vibrazione", "vibrazioni", "fatigue", "fatica", "stress", "tolerance", "tolleranza", "wear", "usura", "friction", "attrito", "gear", "ingranaggio", "bearing", "cuscinetto", "stiffness", "rigidità", "deflection", "deformazione", "crack", "cricca", "corrosion", "corrosione", "shaft", "albero", "weld", "saldatura", "thermal", "termico", "heat", "calore", "machining", "lavorazione", "spindle", "mandrino", "clearance", "gioco", "seal", "tenuta", "spring", "molla", "piston", "pistone", "hydraulic", "idraulico", "pneumatic", "pneumatico", "clutch", "frizione", "brake", "freno", "motor", "motore", "gearbox", "cambio", "bolt", "vite", "fastener", "bullone")`

   - `Data Science TRIZ`:
     `("model", "modello", "training", "addestramento", "dataset", "feature", "caratteristica", "accuracy", "accuratezza", "precision", "precisione", "recall", "overfitting", "underfitting", "bias", "distorsione", "gradient", "gradiente", "inference", "inferenza", "prediction", "previsione", "machine learning", "deep learning", "neural", "rete neurale", "embedding", "hyperparameter", "iperparametro", "loss", "metrica", "metric", "cluster", "clustering", "classification", "classificazione", "regression", "regressione", "anomaly", "anomalia", "outlier", "drift", "validation", "validazione", "gpu", "batch", "epoch", "epoca", "weights", "pesi", "tuning", "ottimizzazione", "prompt", "llm", "transformer", "token")`

   - `Marketing TRIZ`:
     `("conversion", "conversione", "funnel", "imbuto", "campaign", "campagna", "churn", "abbandono", "retention", "fidelizzazione", "acquisition", "acquisizione", "engagement", "brand", "click", "cta", "lead", "landing page", "bounce", "rimbalzo", "audience", "pubblico", "segment", "segmento", "positioning", "posizionamento", "pricing", "prezzo", "a/b test", "persona", "market", "mercato", "growth", "crescita", "virality", "viralità", "reach", "copertura", "impression", "impressioni", "ctr", "roi", "content", "contenuto", "social", "influencer", "marketing", "advertising", "pubblicità", "onboarding", "activation", "attivazione", "upsell", "cross-sell")`

   - `Supply Chain TRIZ`:
     `("inventory", "scorte", "stock", "lead time", "tempi di consegna", "demand", "domanda", "forecast", "previsione", "logistics", "logistica", "warehouse", "magazzino", "supplier", "fornitore", "stockout", "esaurimento", "backorder", "capacity", "capacità", "throughput", "flusso", "replenishment", "riassortimento", "dispatch", "spedizione", "shipping", "trasporto", "freight", "cargo", "routing", "percorso", "bullwhip", "effetto frusta", "safety stock", "scorta di sicurezza", "order", "ordine", "lot", "lotto", "picking", "stoccaggio", "pallet", "container", "customs", "dogana", "distribution", "distribuzione", "supply chain", "catena di approvvigionamento", "sourcing", "approvvigionamento", "procurement", "acquisti", "fulfillment", "evasione ordini", "delivery", "consegna", "transportation", "trasporti")`

   Note: overlap with the Business TRIZ rule (e.g. "fidelizzazione", "mercato",
   "prezzo", "consegna") is expected and acceptable — the `--branch` filter
   isolates a single domain's rule when the user picks one.

2. **`_DOMAIN_RULES` extended** to all seven domain branches:

   ```python
   _DOMAIN_RULES = {
       "business": {"Business TRIZ"},
       "software": {"Software TRIZ"},
       "rehab": {"Rehabilitation TRIZ"},
       "mechanical": {"Mechanical TRIZ"},
       "datascience": {"Data Science TRIZ"},
       "marketing": {"Marketing TRIZ"},
       "supplychain": {"Supply Chain TRIZ"},
   }
   ```

3. **Branch validation data-driven.** Replace the hardcoded
   `if branch not in ("general", "business", "software", "rehab")` in
   `suggest_methods` with `if branch != "general" and branch not in _DOMAIN_RULES`
   (so the accepted ids are exactly `general` + the `_DOMAIN_RULES` keys).
   Update the CLI `--branch` validation, the `--list` output, and the usage
   strings the same way (derive from `_DOMAIN_RULES`; never hardcode the id
   list). The docstring keeps `general` described as "all domain rules run".

### R5 — Use-cases reference (Architect-authored; Carpenter MUST NOT modify)

New file `references/use-cases.md` (already in the working tree), mirroring the
tone of the other reference files. Exactly four `##` sections — one per new
branch: `## Mechanical / hardware`, `## Data science / ML / AI`,
`## Marketing / growth`, `## Supply chain / logistics`. Each section contains,
in order, these bold labels:

1. `**Problem:**` — a concrete, ultra-specific problem statement.
2. `**Branch detection:**` — the branch keywords the router matched.
3. `**Route:**` — the exact `python .../triz.py --branch <id> route "<problem>"`
   command and a 2–4 line summary of the router's top methods.
4. `**Parameter translation:**` — 2–3 `parameter_map` rows showing the 39-parameter
   name → domain translation in action.
5. `**Solution via soft principles:**` — 2–3 `principle_soft` readings applied to
   the problem, each producing a concrete mechanism.
6. `**Result:**` — the chosen mechanism, tagged `[IP-NN Name]` and
   `[Separation ...]` where applicable.

The file starts with a one-line `> ` intro stating it demonstrates each field
branch with a worked example.

### R6 — SKILL.md documentation

In `.claude/skills/triz-innovation/SKILL.md`, under the existing `## Branches`
section:

- Update the shipped-fields list from "general, business, software, rehab" to
  all eight: `general`, `business`, `software`, `rehab`, `mechanical`,
  `datascience`, `marketing`, `supplychain`.
- Add one sentence pointing at `references/use-cases.md` as the worked examples
  for the field branches.

### R7 — Regression tests

Extend `tests/test_triz.py` (unittest style, matching the existing suite) with:

- **Registry (8 fields):** `list_branches()["fields"]` has exactly 8 ids in the
  canonical order (general first, supplychain last); `validate()` empty for the
  shipped data.
- **New branches data:** for each of mechanical/datascience/marketing/supplychain —
  `get_field_branch(id)["id"] == id`, `parameter_map` and `principle_soft` are
  non-empty dicts, `name_it` present, `keywords` ≥ 10, `examples` ≥ 2.
- **Routing:** a mechanical-keyword problem (e.g. "the gear wears out under
  vibration and high torque") makes `suggest_methods` include `Mechanical TRIZ`;
  a marketing-keyword problem includes `Marketing TRIZ`; a supply-chain problem
  includes `Supply Chain TRIZ`; a datascience problem includes `Data Science TRIZ`.
- **`--branch` filter:** `suggest_methods(problem, branch="mechanical")` on a
  marketing-only keyword string does NOT include `Marketing TRIZ`;
  `branch="general"` on the same string DOES.
- **Data-driven validation:** `suggest_methods(problem, branch="datascience")`
  does not raise; `branch="bogus"` raises `ValueError`; dispatcher
  `triz.py --branch supplychain route "..."` exits 0 and
  `triz.py --branch bogus route "..."` exits 1.
- **Use-cases file:** `references/use-cases.md` exists and contains exactly the
  four required `## ` headings, each followed by the six `**Label:**` markers
  in order (loop over the file text).
- **Mirror:** `scripts/build_mirror.py --check` exits 0.

### R8 — Mirror rebuild

Run `python scripts/build_mirror.py` so the `.agents/skills/triz-innovation/`
mirror carries the four new branch files, the router/registry changes, and
`references/use-cases.md`; `build_mirror.py --check` must exit 0.

## Acceptance criteria

| # | Criterion | Verified by |
|---|-----------|-------------|
| AC1 | `branches/fields/` contains exactly 8 field branches; all schema-valid (incl. `name_it`, non-empty keywords/parameter_map/principle_soft/examples) | `python .claude/skills/triz-innovation/scripts/triz_branches.py check` → `OK — 8 field branch(es), 2 language overlay(s)` |
| AC2 | `triz_branches.py list` shows the 8 fields in canonical order (general first, supplychain last) | command |
| AC3 | `triz.py --branch <any-of-8> route "..."` works; `--branch bogus` exits non-zero with a clear error; no hardcoded branch-id tuple remains in `triz.py` | tests + grep |
| AC4 | Router routes each new domain's keywords to its own rule; `--branch <domain>` excludes the other domains' rules; unknown branch raises `ValueError` | tests |
| AC5 | `references/use-cases.md` exists with the 4 required `##` sections, each with the 6 `**Label:**` markers in order | tests |
| AC6 | SKILL.md `## Branches` lists all 8 fields and points to `references/use-cases.md` | reviewer |
| AC7 | Full suite passes (existing 100 + new) via `python tests/test_triz.py` | command |
| AC8 | `.agents` mirror in sync (`build_mirror.py --check` exits 0) | command |
| AC9 | No file outside the listed scope is created or modified (branch files, triz_branches.py, triz.py, triz_router.py, SKILL.md, use-cases.md, tests, mirror; SPEC.md/BACKLOG.md allowed) | reviewer diff |

## Out of scope (Phase 4)

- Merging and final doc sync (SKILL.md, usage-guide, source-map, BACKLOG) —
  handled in Phase 4 after this build is merged.
- Any change to `Books/`, `triz-prompt-engineering-main/`, `reddit-post.md`,
  `cases/`, `TRIZ-MASTER.md`.
