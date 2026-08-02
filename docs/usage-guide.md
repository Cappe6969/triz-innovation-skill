# Usage Guide — `triz-innovation`

How to use the TRIZ skill in Claude Code, invoke it manually, add references,
save cases, run the scripts, and use the MCP server.

## 1. Using the skill in Claude Code
The skill auto-triggers when you describe a real problem involving contradictions,
bottlenecks, constraints, function/root-cause analysis, resources, ideality,
trimming, redesign, or innovation (see the `description` in
`.claude/skills/triz-innovation/SKILL.md`).

Just describe your problem naturally, e.g.:
> "Use TRIZ to help me: my physio app needs better exercise adherence, but more
> notifications make it annoying."

Claude will run the 10-stage pipeline and end with a testable experiment.

### Invoking it manually / forcing it
- Be explicit: start your message with **"Run the triz-innovation skill on: …"**
- Or open the skill file and tell Claude: *"Follow
  `.claude/skills/triz-innovation/SKILL.md` for this problem."*
- To go deep on one method, ask Claude to read the specific reference, e.g.
  *"Read `references/physical-contradictions.md` and apply it here."*

## 2. The pipeline (what you'll get)
1. Problem framing → 2. Function analysis → 3. Root cause → 4. Contradictions →
5. Resources → 6. Ideal Final Result → 7. Method selection → 8. Solutions
(3 conservative / 3 creative / 3 non-obvious / 2 high-risk / 1 minimal) →
9. Evaluation (1–5 on 8 criteria) → 10. Experiment plan.

## 3. Adding new references
1. Create `references/<topic>.md` under `.claude/skills/triz-innovation/`.
2. Keep it **operational**: checklists, tables, procedures — not essays.
3. Add a row to the **Reference index** table in `SKILL.md` so the skill knows
   when to load it.
4. If it changes routing, also add keyword cues to
   `references/triz-method-map.md` (and the router script).
5. Record provenance in `docs/source-map.md`.

## 4. Saving TRIZ cases
```
python .claude/skills/triz-innovation/scripts/triz_case_template.py "Short problem title"
```
Creates `cases/YYYY-MM-DD-short-problem-title.md` from `cases/template-triz-case.md`.
Fill each section as you work; after running the experiment, update **Risultati**
and **Follow-up**. See `cases/README.md`.

## 5. Using the Python scripts
All scripts are plain-stdlib MVPs (no install needed; Python 3.8+).

**Master dispatcher — one entrypoint:**
```
python .claude/skills/triz-innovation/scripts/triz.py route "Ho un'app di fisioterapia che deve aiutare i pazienti ad aderire agli esercizi, ma se aggiungo troppe notifiche diventa fastidiosa."
```
`triz.py` forwards to the right sub-tool (`matrix`, `ariz`, `effects`,
`branches`, …). Run with no args for the full command list.

**Router — which methods to use:**
```
python .claude/skills/triz-innovation/scripts/triz_router.py "…"
```
Prints likely engineering/physical contradictions and a ranked list of suggested
TRIZ methods. The router (and dispatcher) accept two global flags:
`--branch <id>` and `--lang <lang>` (or `--lang auto` to detect the language of
the problem text). See *Field and language branches* below.

**Case template generator:** see section 4.

**Evaluator — score solutions:**
```
python .claude/skills/triz-innovation/scripts/triz_evaluator.py solutions.csv
```
CSV columns: `solution,impact,feasibility,cost,speed,risk,reversibility,complexity,ideality`
(scores 1–5; for cost/risk/complexity, 5 = cheap/safe/simple). Prints a table
sorted by total. Run with `--help` for the exact format, or with no args to see a
demo on built-in sample data.

### Field and language branches
The skill is a mix of branches — pure-data JSON that tunes the same TRIZ core to a
field or a language, no code.

- **Field branches** (`branches/fields/<id>/branch.json`) carry domain vocabulary:
  keywords, parameter translations, soft readings of the 40 principles, and worked
  examples. Shipped: `general`, `business`, `software`, `rehab`, `mechanical`,
  `datascience`, `marketing`, `supplychain`. `general` is the canonical core.
- **Language branches** (`branches/langs/<lang>/branch.json`) carry localized labels
  plus stopwords for auto-detection. Shipped: `en` (default), `it`.

Use them through the dispatcher — the flags are position-independent:
```
python .../triz.py --branch mechanical --lang en route "The gearbox must transmit more torque, but the housing cannot grow heavier"
python .../triz.py --lang auto route "…"          # detect the language from the text
python .../triz.py branches list|check|resolve --lang it
```
`--branch <domain>` restricts the router to that field's domain rule; `--lang it`
prints Italian labels; `--lang auto` detects the language. Worked examples for each
field branch are in `references/use-cases.md`. Adding a branch is pure data: drop a
`branch.json` in `branches/fields/<id>/` (or `branches/langs/<lang>/`) and the
registry and router pick it up automatically — no code change.

## 6. MCP server
The skill ships a minimal local MCP server at
`.claude/skills/triz-innovation/mcp/triz_mcp_server.py`. It is **pure stdlib**
(`json`, `sys`, `io`, `argparse` only — no `mcp` SDK, no pip install, Python
3.8+), speaking **newline-delimited JSON-RPC 2.0 over stdio** (not
Content-Length framing): one JSON request object per stdin line, one JSON
response object per stdout line; logs go to stderr only. On Windows the stdio
streams are re-configured to UTF-8 so non-ASCII output never crashes.

It exposes three tools mirroring the scripts:

| Tool | Arguments | Returns |
|---|---|---|
| `triz_route` | `problem` (required, str), `branch` (str, default `general`) | Human-readable methods + detected contradictions (wraps `triz_router.suggest_methods`) |
| `triz_new_case` | `title` (required, str), `lang` (`"en"`/`"it"`, default `it`) | Absolute path of the created case file (wraps `triz_case_template.create_case`) |
| `triz_evaluate` | `solutions` (required, array of `{solution, impact, feasibility, cost, speed, risk, reversibility, complexity, ideality}` — criteria ints 1–5) | Sorted markdown table (wraps `triz_evaluator.score` + `format_table`) |

### Run it standalone / self-check
```
python .claude/skills/triz-innovation/mcp/triz_mcp_server.py            # serve on stdio
python .claude/skills/triz-innovation/mcp/triz_mcp_server.py --self-test # in-memory check
```
`--self-test` drives the handler through an in-memory conversation
(`initialize` → notification → `ping` → `tools/list` → all three tools → an
unknown-method request) with no client and no network, prints `SELF-TEST OK`,
and exits 0 on success, 1 on failure.

### Register it
Because the server is pure stdlib, any Python 3.8+ on `PATH` works — no install
step. Register it explicitly as a local stdio server.

**Claude Code (project scope):**
```
claude mcp add triz -- python "C:\Dev\TRIZskill.md\.claude\skills\triz-innovation\mcp\triz_mcp_server.py"
```
Windows quoting note: the absolute path is wrapped in double quotes and `python`
must be on `PATH`.

**Claude Desktop:** add a `triz-innovation` entry to `claude_desktop_config.json`
(equivalent to the CLI registration above):
```json
{
  "mcpServers": {
    "triz-innovation": {
      "type": "stdio",
      "command": "python",
      "args": ["C:\\Dev\\TRIZskill.md\\.claude\\skills\\triz-innovation\\mcp\\triz_mcp_server.py"]
    }
  }
}
```

**Do not** commit a repo-root `.mcp.json` — it would auto-spawn the server on
every Claude Code session. Register the server explicitly (as above) instead.

## 7. Codex / other agents
A portable mirror lives at `.agents/skills/triz-innovation/SKILL.md` — a
self-contained copy of the pipeline, references, scripts, and branches, with
`.claude/` paths rewritten to `.agents/` (same `name`/`description`). Point
Codex Agent Skills at that folder. The mirror is generated from the canonical
`.claude` sources — after any change to the skill, regenerate it:
```
python scripts/build_mirror.py
python scripts/build_mirror.py --check    # verify it's in sync (exit 1 on drift)
```
