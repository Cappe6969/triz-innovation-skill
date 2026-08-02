# Business TRIZ

TRIZ adapted for business, pricing, org, workflow, and market problems. Same
machinery (functions, contradictions, resources, ideality) with non-engineering
vocabulary. Pairs with the repo's `business_triz/` prompts.

## Translate the core concepts
| Engineering | Business |
|---|---|
| Component | Role, team, process step, document, channel, asset |
| Tool → Action → Object | Who does what to whom (process → outcome → stakeholder) |
| Harmful function | Friction, cost, churn, rework, dissatisfaction |
| Insufficient function | Weak conversion, low adoption, underdelivery |
| Resource | Existing customers, data, brand, idle capacity, staff time, channels |
| Super-system | Market, regulator, partners, competitors |

## Common business contradictions (and where they break)
- **Price vs volume** — *raise price, lose customers.* → Separation by **condition**
  (segment-based pricing), by **time** (intro vs standard), by **parts/whole**
  (free core + paid add-ons). [IP-3 Local quality, IP-4 Asymmetry]
- **Quality vs speed** — → [IP-10 Prior action] templatize; [IP-1 Segmentation] tier the offering.
- **Personalization vs scale** — → [IP-25 Self-service] customer configures; [IP-15 Dynamics] rules engine.
- **Growth vs margin** — Resource Analysis: monetize an existing underused asset before spending.

## Business-specific tools
- **Solutions at system levels** — generate 5–10 super-systems and sub-systems of
  your business, then mine each level for solutions and resources (see
  `business_triz/business_solutions_at_system_levels/`). Great for "rethink the
  model" problems.
- **Perception mapping** — map stakeholder perceptions and "leads-to"
  relationships to find conflict pairs, then translate each conflict into a TRIZ
  contradiction (see `business_triz/business_perception_mapping/`).
- **Non-engineer function analysis** — simplified U/H function table for
  services/processes (see `business_triz/function_analysis/`).

## Pricing playbook (mini)
1. Function-analyze the offer: what useful function does the customer actually pay for? Grade it N/I/E.
2. Find the contradiction (usually price↔adoption or simplicity↔revenue).
3. Resolve by separation: tiers (condition), trials (time), bundle/unbundle (parts↔whole), usage-based (dynamics).
4. IFR check: the customer gets the value *and pays in proportion to value received*, with no friction.
5. Score variants on impact/feasibility/risk/reversibility; pick the smallest reversible price test.

## Ideality for business
Numerator = value delivered to customer + revenue. Denominator = cost to serve +
risk + org complexity. Bias every move toward **self-service** and **using
existing assets** — that's where margin and durability come from.
