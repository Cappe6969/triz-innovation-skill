# Example — Software problem (worked, condensed)

**Problem:** "Our API endpoint is slow (p95 ~1.2s). Adding a cache would speed it
up, but stale data causes wrong results for some users, and we have no budget for
new infrastructure."

## 1. Framing
System: the read endpoint. Sub: query, serializer, DB. Super: clients, the DB
shared with writes. Main function: *endpoint returns correct, fast results to
client.* Harmful: *slow response* (insufficient) and the feared *stale response*
(harmful). Constraint: no new infra budget. Symptom = p95 latency; goal = fast +
correct; cause = recomputed-per-request heavy query.

## 2. Function analysis (excerpt)
| Tool | Action | Object | U/H | N/I/E |
|---|---|---|---|---|
| Query | computes | result | U | Insufficient (slow) |
| DB | serves | rows | U | Normal |
Trimming candidate: the per-request recomputation.

## 3. Root cause
Slow → heavy aggregation runs on every request → **root cause: no reuse of
identical recent computations** (controllable). Leverage: reuse without going stale.

## 4. Contradiction
- **Engineering:** IF we cache THEN latency drops BUT correctness/staleness risk rises.
- **Physical:** the result must be **cached** (fast) and **fresh** (correct).
- Break via **separation in time/condition**.

## 5. Resources (no new infra)
Existing: app memory, the DB itself, request logs, an `updated_at` column,
the client. Underused: idle memory on app nodes; the write path that already
knows when data changes.

## 6. IFR
The endpoint returns the right answer with **zero recomputation and zero new
service** — it's already computed and only recomputed exactly when the data changed.

## 7. Methods: Contradiction → Physical contradiction (separation) → Resource → Trimming.

## 8. Solutions (tagged)
- Conservative: short TTL in-process cache [IP-10 Prior action]; add DB index; paginate.
- Creative-realistic: **event-driven invalidation** — write path bumps a version key, cache keyed by version [Separation on condition / IP-23 Feedback]; stale-while-revalidate [IP-15 Dynamics].
- Non-obvious TRIZ: push the aggregate to **write time** (materialize on change) so reads are trivial [Trimming Rule A — the read-time compute need disappears / IP-13 Other way round]; let the **client** cache with an ETag [Trimming Rule C — client does the work / IP-25].
- High-risk/high-upside: precompute via a tiny cron into an existing table (no new infra) [IP-10].
- Minimal test: in-process cache + ETag, behind a flag, on the hottest route.

## 9. Evaluation (excerpt)
| Solution | Impact | Feas | Cost | Speed | Risk | Rev | Cplx | Ideal | Total |
|---|---|---|---|---|---|---|---|---|---|
| ETag + in-proc cache | 4 | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 36 |
| Materialize on write | 5 | 3 | 4 | 3 | 3 | 3 | 2 | 5 | 28 |

## 10. Experiment plan
- **Best candidate:** ETag + in-process cache with event-version invalidation.
- **Experiment:** flag on for 10% traffic on the top endpoint, 1 week.
- **Data:** p95/p99 latency, cache hit rate, stale-read count (compare cached vs fresh sampled).
- **Success:** p95 < 400ms AND zero confirmed stale reads.
- **If works:** ramp to 100%, then evaluate write-time materialization for the next hotspot.
- **If fails (staleness):** shorten TTL / tighten invalidation before abandoning.
