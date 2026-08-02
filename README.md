# TRIZ Coding Method

Find the smallest safe solution to a software trade-off. The method starts by
deleting or reusing; it invokes TRIZ only when two required qualities still
conflict.

Version 0.1.0 is experimental. The implementation is dependency-free Python,
has no network calls, UI, telemetry, or automatic configuration writes.

## When to use it

Use it for a coding/design decision where the first answer looks too large, a
legacy change is risky, an algorithm or API shape must be chosen, or improving
one property appears to worsen another. Do not use it for a mechanical rename,
routine formatting, or broad non-software innovation; the general TRIZ CLI is
available separately for the latter.

## Method in one minute

1. Frame behavior, harmful effects, constraints, and proof.
2. Try, in order: delete; stdlib/native; configure/compose; adapt existing code;
   smallest new code.
3. State the Ideal Final Result and the feasible almost-IFR.
4. Load data/algorithm, legacy/debug, or architecture guidance only when the
   task signals it.
5. If a contradiction remains, use separation, trimming, resources, or the
   contradiction matrix. Otherwise skip TRIZ.
6. Verify with reproducible evidence.

Modes are `lite`, `focused` (the `auto` default), and `ultra`.

## Quick starts

### Codex

Build the native archive, place it in a local Codex plugin marketplace you
control, then install it by its marketplace name:

```text
python scripts/package_release.py --target codex
codex plugin add triz-coding-method@<your-local-marketplace>
```

Start a new Codex thread and use:

```text
Use $triz-coding-method to find the smallest safe solution to this coding trade-off.
```

### Claude Code

Run the source tree as a development plugin, or unpack the Claude archive:

```text
python scripts/package_release.py --target claude
claude --plugin-dir .
```

Claude discovers `skills/` and `.mcp.json` from the plugin root.

### OpenCode

Build the OpenCode bundle and copy its `.opencode/` directory into the target
repository. Review the included MCP snippet before merging it with an existing
`opencode.json`; the installer never edits user configuration.

```text
python scripts/package_release.py --target opencode
```

## CLI and MCP

```text
python skills/triz-coding-method/scripts/method.py route --mode auto "more speed but less reliability"
python skills/triz-coding-method/engine/scripts/triz.py route "a general TRIZ problem"
python skills/triz-coding-method/engine/scripts/triz_matrix.py 18 35
python skills/triz-coding-method/engine/scripts/triz_case_template.py "Case title" --output-dir ./my-cases
python skills/triz-coding-method/scripts/triz_mcp_server.py --self-test
```

The read-only MCP server exposes:

- `triz_coding_route`
- `triz_matrix_lookup`
- `triz_coding_evaluate`

Requests are capped at 256 KiB. Route problems are capped at 20,000 characters;
evaluation accepts 1–50 solutions with at most 2,000 characters each. MCP never
creates files.

## Honest before/after

Before: “Sort 2D points and compare adjacent entries” sounds small, but is not
correct for the general closest-pair problem.

After: keep O(n²) as the test oracle and use the standard divide-and-conquer
algorithm with a bounded strip for the O(n log n) implementation. The method
did not force a TRIZ detour: data/algorithm analysis was sufficient. See
[`docs/examples/coding/2026-08-02-algorithm-closest-pair.md`](docs/examples/coding/2026-08-02-algorithm-closest-pair.md).

## Benchmark status

`benchmarks/` defines ten paired baseline/treatment fixtures and the release
gate. No performance claim is made until real Codex 0.146.0 runs with
`gpt-5.6-luna` (low reasoning) are recorded and blind-scored. Fixture validation
and dry runs do not count as benchmark results.

The gate requires treatment tests 10/10, no regressions, blind preference at
least 7/10, median production lines no greater than baseline, and no
unjustified dependency. Raw JSONL logs must accompany any published result.

## Limitations and security

Routing is heuristic and cannot prove that a contradiction is real. Matrix
principles are prompts for design exploration, not correctness evidence. Keep
human review for security-, safety-, data-, and migration-sensitive changes.

The software reads only bundled local data. It does not request credentials or
send task text over the network. The benchmark runner invokes the locally
installed Codex CLI only when explicitly requested; dry-run validation does
not invoke a model. Do not place secrets in benchmark fixtures.

## License and provenance

MIT licensed; see [`LICENSE`](LICENSE). The internal TRIZ engine retains a
small derived subset of the MIT-licensed `jenson500/triz-prompt-engineering`
project pinned at commit `a3812e200711ad443c3db5fc57ebc05fe0c5c91d`; see
[`PROVENANCE.md`](skills/triz-coding-method/engine/PROVENANCE.md) and the
[`bibliography`](docs/bibliography.md). Full upstream prompts and source books
are not vendored.
