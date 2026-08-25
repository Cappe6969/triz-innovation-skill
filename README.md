# triz-innovation-skill

A **TRIZ problem-solving engine for AI coding agents** — packaged as an agent
skill (Claude Code / opencode compatible) plus a small, dependency-free Python
toolset. It runs a fixed 10-stage pipeline that turns a messy real-world
problem into a small set of **evaluated, testable solutions** — method over
inspiration.

TRIZ (Theory of Inventive Problem Solving) is Genrich Altshuller's
systematic innovation methodology: contradictions, function analysis,
resources, ideality, trimming, and the 40 inventive principles.

## What it does

Given a problem ("my app's notifications annoy users but users need them"),
the skill walks a disciplined pipeline:

1. Problem framing · 2. Function analysis · 3. Root cause analysis ·
4. Contradiction analysis (39×39 matrix + 40 principles) · 5. Resource
analysis · 6. Ideal Final Result · 7. Method selection · 8. Solution
generation (3 conservative / 3 creative / 3 TRIZ / 2 high-risk / 1 minimal) ·
9. Scored evaluation · 10. A concrete experiment plan — always.

Every proposed solution is tagged with the TRIZ method that produced it, and
no analysis closes without a testable next step.

## Quick start

Requirements: **Python 3.9+** (standard library only — nothing to install).

**Use as an agent skill:** copy the skill folder into your project (or user
skills directory) and ask your agent to use it:

```
.claude/skills/triz-innovation/   ->  <your-project>/.claude/skills/triz-innovation/
```

Then: *"Use the triz-innovation skill on this problem: ..."*

**Or use the tools directly** from any directory:

```bash
python .claude/skills/triz-innovation/scripts/triz.py route "more speed but less reliability"
python .claude/skills/triz-innovation/scripts/triz.py matrix 18 35        # contradiction-matrix cell
python .claude/skills/triz-innovation/scripts/triz.py                     # full command list
```

## CLI reference

One dispatcher, `scripts/triz.py`, fronts every tool:

| Command | Purpose |
|---|---|
| `route "<text>"` | Suggest methods + likely contradictions from problem text |
| `matrix <imp> <wor>` | 39×39 contradiction-matrix lookup (`--list` for parameters) |
| `sufield --state <state>` | Su-Field diagnosis → 76 standard solutions |
| `ariz "<title>"` | Generate an ARIZ-85C worksheet |
| `evolution --signals "..."` | S-curve stage + 8 evolution trends |
| `effects --function/--keyword <q>` | Function → scientific effects catalog |
| `evaluate <csv>` | Score & rank candidate solutions |
| `case "<title>"` | Create a pre-filled case file in `cases/` |
| `network` | Contradiction network demo / stdin JSON analysis |
| `branches list\|check\|info\|resolve\|detect` | Manage field + language branches |
| `master` | Show the TRIZ-MASTER knowledge-base sections |

Global flags: `--branch <id>` (field), `--lang en|it|auto` (language,
auto-detected). Aliases included (`router`→`route`, `evaluator`→`evaluate`,
…).

## Field × language branches

The same TRIZ core is tuned per domain and language with pure-data JSON — no
code forks:

- **Fields** (`branches/fields/`): `general` (canonical), `business`,
  `software`, `rehab`, `mechanical`, `datascience`, `marketing`,
  `supplychain`, `energy`, `education`, `construction`, `robotics`.
- **Languages** (`branches/langs/`): English (default), Italian — localized
  labels plus stopwords for auto-detection.

Add a branch by dropping a `branch.json` in the right folder; the registry
picks it up automatically.

## MCP server

`mcp/triz_mcp_server.py` is a stdlib-only MCP server (JSON-RPC 2.0 over
stdio) exposing `triz_route`, `triz_new_case`, and `triz_evaluate` as tools.
Self-check: `python mcp/triz_mcp_server.py --self-test`.

## Repository layout

```
.claude/skills/triz-innovation/
├── SKILL.md            # the skill: pipeline + operating rules
├── TRIZ-MASTER.md      # single-file knowledge base (24 sections)
├── references/         # one file per TRIZ method, loaded on demand
├── scripts/            # triz.py dispatcher + sub-tools + CSV/JSON data
├── branches/           # field (JSON) × language overlays
├── mcp/                # stdlib MCP server
├── docs/               # usage guide, source map, implementation notes
└── examples/           # worked example problems
cases/                  # saved analyses (create with `triz.py case`)
tests/                  # unittest suite (run by CI)
.github/workflows/      # CI: tests + registry validation + MCP self-test
```

## Development

Full local gate (mirrors CI):

```bash
python -m unittest discover -s tests -p "test_*.py"
python .claude/skills/triz-innovation/scripts/triz.py branches check
python .claude/skills/triz-innovation/mcp/triz_mcp_server.py --self-test
# Windows: scripts/check_all.cmd does all three
```

CI runs the suite on Ubuntu + Windows against Python 3.9 / 3.11 / 3.13.

Design/history notes live in `.claude/skills/triz-innovation/docs/`;
deferred findings in `BACKLOG.md`.

## Sources & provenance

Everything under `references/` is original operational rewriting — see
[docs/source-map.md](.claude/skills/triz-innovation/docs/source-map.md). The
external MIT-licensed [triz-prompt-engineering](https://github.com/jenson500/triz-prompt-engineering)
prompt collection (ccTOPP initiative) was consulted for structure and
checklists during development (snapshot not vendored here); copyrighted book
material was used as conceptual cross-check only and never distributed.

## License

[MIT](LICENSE)
