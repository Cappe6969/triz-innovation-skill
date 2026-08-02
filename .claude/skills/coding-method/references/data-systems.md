# data-systems

Data-system decisions from Kleppmann's *Designing Data-Intensive Applications*:
how to choose and combine storage, replication, and processing so the composite
data system stays reliable, scalable, and maintainable — and your code is thin
glue, not the correctness mechanism. Reach for it when the data-heavy signal
fires: databases, pipelines, analytics, caches, indexes, queues, or any place
several tools must stay consistent with one source of truth.

## When to use it
- A **composite data system** — a database plus a cache, search index, analytics
  store, or queue that application code keeps in sync by hand.
- Choosing the data model or storage engine for a workload (document vs
  relational vs graph; OLTP vs OLAP).
- Deciding whether replication/partitioning is even needed, or whether one node
  still suffices.
- Consistency questions: which anomalies matter, which isolation level you
  actually need, sync vs async replication, leaderless vs single-leader.
- Any "should this be distributed?" question — before adding the complexity.
- Streaming/pipeline design: batch vs stream, event sourcing, change data
  capture, exactly-once semantics.

## Core method

### Frame it as a composite data system [Composite data system]
Most services are already a data system: several tools stitched together by
application code. The service interface hides that. The moment you write glue to
keep a cache, index, or analytics store in sync with a database, YOU are the
data-system designer — every guarantee the composite provides (cache
invalidation, consistent reads) is now your correctness burden. Ask first whether
one tool can do the whole job before assembling several.

### Name the three concerns before choosing anything [RSM]
Every data system is judged on three axes; name them before touching a tool:
- **Reliability** — keep working correctly in the face of adversity.
  [Fault vs failure]: a fault is one component deviating from its spec; a failure
  is the system stopping service. Fault probability can't reach zero, so design
  so faults don't become failures. Inject faults deliberately (Chaos Monkey) —
  most critical bugs live in error handling, and fault injection is what
  exercises it. Prevention beats cure only where there is no undo (security).
- **Scalability** — not a one-dimensional label: "X scales" is meaningless.
  [Load parameters]: pick the few numbers that describe YOUR load — req/s,
  read:write ratio, cache hit rate, fan-out (a post to 30M followers is 30M
  writes). Architecture is built around which operations are common vs rare; get
  that wrong and the scaling effort is wasted. Rethink on every order of
  magnitude.
- **Maintainability** — many people will work on it over time: operability,
  simplicity (managing complexity), evolvability (ease of change via rolling
  upgrades).

### Measure response time as a distribution, not an average [Tail latency]
Response time is a distribution, not a single number. Mean hides the user
experience; use percentiles — p50 (typical), p95/p99 (outliers), and watch p999
because the slowest customers are often the most valuable. [Tail latency
amplification]: one slow backend call among N parallel calls slows the whole
request, and the chance of one rises with the number of calls. Queueing causes
head-of-line blocking — measure on the client side. Set SLOs/SLAs in percentile
terms. Never average percentiles across machines or windows; add the histograms.

### Pick the data model for the access pattern [Data model choice]
- **Document** — data comes in self-contained documents, relationships rare.
  Schema-on-read vs schema-on-write: a schema exists in your code either way;
  the question is where it is enforced.
- **Relational** — many-to-many, joins, ad-hoc querying.
- **Graph** — anything potentially related to everything.
Each is emulatable in the others but awkward; the awkwardness of the mapping is
the signal you are using the wrong model.

### Storage engine: OLTP vs OLAP [Storage engine]
- **OLTP** (user-facing, keyed lookups, disk-seek bound): two schools —
  log-structured (append-only, LSM: random writes become sequential → high write
  throughput) vs update-in-place (B-trees, fixed pages). Choose by
  write-vs-read profile.
- **OLAP** (analytics, full scans, disk-bandwidth bound): column-oriented
  storage + compression, not row indexes.

### Encode for evolution [Backward/forward compat]
Rolling upgrades mean old and new code run simultaneously, so every payload needs
backward compatibility (new code reads old data) and forward compatibility (old
code reads new data). Language-specific serialization fails this. JSON/XML/CSV
depend on how you use them (optional schemas, vague types). Binary schema-driven
formats (Thrift, Protobuf, Avro) give defined compat semantics. Applies across
all three dataflow modes: database, RPC/REST, async messaging.

### Replication: pick the leader model by consistency needs [Replication]
- **Single-leader** — all writes to one leader, reads from any replica (may be
  stale). Easy to reason about, no conflict resolution. Sync vs async decides
  durability on leader failure: promoting an asynchronously updated follower can
  lose recently committed writes.
- **Multi-leader** — writes to several leaders; conflicts must be resolved or
  accepted.
- **Leaderless** — write and read from several nodes to detect and repair stale
  copies.
Replication lag creates anomalies; the three guarantees that matter:
[Read-after-write] (you always see your own writes), [Monotonic reads] (never
see the past after the present), [Consistent prefix] (causally-ordered views —
a reply never appears before its question).

### Partition when one machine can't hold it [Partitioning]
Goal: spread data + query load evenly, avoid hot spots. Two schemes:
**key-range** (sorted — efficient range queries, hot spots on adjacent keys) vs
**hash** (even distribution, destroys ordering). Secondary indexes:
document-partitioned (local — cheap writes, scatter/gather reads) vs
term-partitioned (global — multi-partition writes, single-partition reads).
Rebalance by dynamic range split or by fixed partition count + moving whole
partitions.

### Transactions: pay for the isolation you actually need [Isolation ladder]
Transactions reduce a huge class of errors to "abort and retry". Anomalies,
weakest → strongest:

| Anomaly | Example | Prevented by |
|---|---|---|
| Dirty read / dirty write | read or overwrite another client's uncommitted write | read committed |
| Read skew | see different parts of the DB at different times | snapshot isolation (MVCC) |
| Lost update | concurrent read-modify-write; one update silently lost | snapshot + care, or lock |
| Write skew | decide from a value, write after the premise changed | serializable only |
| Phantom | search-condition results change mid-transaction | serializable (range locks / SSI) |

Serializable via: serial execution (if throughput fits one core), two-phase
locking, or SSI (optimistic, abort on conflict). Weak isolation leaves you to
handle anomalies by hand — often with explicit locks. Simple access patterns
(single-record reads/writes) can skip transactions; complex interacting access
cannot.

### Distributed systems: assume partial failure [Partial failure]
The defining trait of a distributed system: any message can be lost or delayed,
clocks lie (NTP is not enough; a paused process can be declared dead and "come
back" without knowing), and there is no shared memory or common knowledge. Fault
detection is already hard — timeouts can't distinguish network from node failure,
and a "limping" node (degraded NIC) is worse than a cleanly dead one. If you can
avoid opening Pandora's box — keep it on one machine — do. Distributed is
justified by fault tolerance and geographic latency, not scalability alone.

### Consistency: linearizability vs causality [Consistency model]
- **Linearizability** — makes replicated data look like one copy; simple to
  reason about (like a single-threaded variable), but slow under network delay.
- **Causal consistency** — orders only cause-effect events; concurrent things
  branch and merge; cheap and robust to network problems.
Needing uniqueness (a username), a compare-and-set register, atomic commit,
total-order broadcast, locks/leases, or membership — all of these are
[Consensus reducibility]: reducible to consensus. A single leader delivers them
all, but leader failover needs consensus too. Use a proven algorithm or a
coordination service (ZooKeeper) — never write your own. Leaderless and
multi-leader skip global consensus by accepting conflicts and merging.

### Derived data: separate source of truth from derived systems [Derived data]
The book's master idea (Part III): distinguish the **source of truth** (the
system of record) from **derived data systems** (caches, search indexes,
materialized views, analytics stores). A derived system can always be **rebuilt
by replaying history** — that property is what makes it disposable, recomputable,
and eventually consistent without manual patching.
- **Batch** (bounded input): immutable input, output derived, "do one thing
  well" + pipes. Fault tolerance falls out of retries: deterministic operators,
  discard partial output of failed tasks, retry safely. Joins: sort-merge (all
  records with the same key to one reducer), broadcast hash (small side fits in
  memory), partitioned hash (both sides pre-partitioned the same way).
- **Stream** (unbounded input): message brokers (task-queue style — messages
  acknowledged and deleted) vs **log-based** brokers (partitioned, ordered,
  replayable, consumers checkpoint offsets). Capture DB changes as a stream via
  **change data capture** or **event sourcing**; log compaction turns the log
  into a full copy of the database. Three joins: stream-stream (window),
  stream-table (enrich), table-table (materialized view). Distinguish processing
  time from event time — stragglers arrive after the window seemed closed.
  Exactly-once via microbatching, checkpointing, transactions, or idempotent
  writes.

## TRIZ reconciliation
DDIA is TRIZ applied to data systems; the vocabulary maps cleanly:
- **The single-machine default IS ideality** — "if you can avoid it, keep it on
  one machine" = increase ideality by NOT adding the distributed denominator
  [IFR]. Distributed is only justified by a real contradiction (fault tolerance,
  latency, scale) that one machine cannot resolve.
- **Reliability vs cost** → [IP-11 Beforehand cushioning] (redundancy, spare
  capacity) + [IP-16 Partial action]: fault injection targets the risky
  error-handling paths — Chaos Monkey exercises exactly the rarely-run code.
- **Consistency vs speed** → [IP-13 Other way round] eventual + reconcile;
  [Separation in time] per-operation freshness — read-after-write where it
  matters, eventual elsewhere.
- **Write fan-out vs read fan-out (Twitter)** → [IP-10 Prior action]: do work at
  write time so reads are cheap — but the celebrity hybrid (outliers fetched at
  read time) is [Separation in condition]: the common path is precomputed, the
  outlier is not.
- **The manual-sync glue in a composite system** → [Trimming] (Rule C: move the
  function into an existing resource): derive caches and indexes from the
  source-of-truth log instead of writing sync code. The keep-in-sync function
  relocates into the changelog; the derived store is rebuildable, so its sync
  machinery disappears.
- **Write skew / phantoms** → the serializable "one timeline" is the [IFR]; SSI
  is [Separation in time] of conflict detection — optimistic, abort on commit.
- **Consensus-reducible problems** → a genuine contradiction (availability vs
  agreement) with no elimination: [IP-24 Intermediary] — a proven coordination
  service as the intermediary, never bespoke algorithms.

## Ponytail reconciliation
The ladder is the default: YAGNI (is this system needed at all?), stdlib (one
node, the platform handles it), existing-dep (a real database engine instead of
hand-rolled storage). DDIA is the **deliberate-escalation gate**: it tells you
when the data-heavy / distributed rung is actually required and makes that step
safe. "No magic scaling sauce" is the anti-[YAGNI] warning — scaling architecture
is load-specific, nothing is free. "Keep the database on one node until forced"
is ponytail verbatim. When you DO escalate, DDIA's guarantees (derived data,
exactly-once, the isolation ladder) are what make the added complexity pay — the
framework that hides distributed problems is the existing-dep rung taken
seriously.

## Worked example
An e-commerce read path that has grown: `orders` in PostgreSQL, plus a Redis
cache, an Elasticsearch index, and a nightly analytics load — all kept consistent
by hand-written glue (`invalidate cache on write`, `reindex on write`, `sync to
warehouse`). Every write triggers three fragile code paths; drift is a recurring
incident.

1. **Frame it as a composite data system** [Composite data system]: the glue IS
   the correctness mechanism. Cache, index, and warehouse are all **derived
   data** from the `orders` source of truth.
2. **Make the source of truth emit a changelog** [Derived data]: capture CDC (or
   event sourcing) into a log-based broker; derived consumers build and maintain
   each derived store. The glue becomes "replay the log" — cache invalidation
   and reindexing are the same consumer code.
3. **Trade-off check** [RSM]: reliability improves (no manual-sync bugs; a
   derived store is rebuilt by replaying history), scalability is a free
   byproduct (consumers scale independently), maintainability improves (one
   rebuild path). Cost: a broker to operate — accepted because a fourth sync path
   would cost more. Record an ADR (`architecture-tradeoffs.md`).
4. **Consistency contract** [Replication]: writes are single-leader synchronous
   to the source of truth; reads accept bounded staleness — read-after-write for
   the buyer's own order via a per-user marker, monotonic reads for the timeline.
5. **Isolation** [Isolation ladder]: checkout needs serializable (write skew on
   stock); analytics is snapshot isolation — no one pays for serializable
   analytics.
6. **Run the gate**: the sync glue is deleted (trimmed), the derived stores are
   rebuildable. Numeric criterion: 0 manual-sync code paths left; cache rebuilt
   from the log on demand in < 5 min; p99 read stays under the SLO.

## How it feeds the pipeline
Powers the **data-heavy fork**: `method.py route` detects the data-heavy signal
and routes here. Feeds **stage 1** (frame as a composite system — the three
concerns [RSM] are the frame), **stage 2** (the deliberate-escalation gate:
"keep it on one machine" is the ladder's last rung), **stage 3** (derived-data
rebuildability is the IFR — the sync mechanism disappears), **stage 4**
(data-model, storage-engine, and partition choice = structure from data at system
level), **stage 5** (the consistency/isolation ladder IS the
contradiction-resolution vocabulary — which anomaly you are actually trading
away), **stage 8** (percentile-based success criteria; ADR + CDC as verify and
record). Cross-links: `method-map.md` (data-heavy path), `architecture-tradeoffs.md`
(trade-off matrix + ADR), `computation-models.md` (declarative streams),
`algorithm-strategies.md` (join algorithms), `triz-for-code.md` (separation,
trimming, IP-10/IP-13), `sustainable-engineering.md` (the same guarantees at
Google scale). triz-innovation: `references/software-triz.md`,
`branches/fields/software`, `branches/fields/datascience`.

## Source
*Designing Data-Intensive Applications* — Martin Kleppmann, O'Reilly.
