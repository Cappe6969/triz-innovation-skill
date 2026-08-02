#!/usr/bin/env python3
"""TRIZ innovation MCP server — pure-stdlib JSON-RPC 2.0 over stdio.

Exposes the skill's three Python scripts as MCP tools:
    triz_route      -> triz_router.suggest_methods
    triz_new_case   -> triz_case_template.create_case
    triz_evaluate   -> triz_evaluator.score + format_table

Protocol: newline-delimited JSON-RPC 2.0 over stdio (NOT Content-Length
framing). One JSON request object per stdin line, one JSON response object per
stdout line. Logs / progress go to stderr only — never stdout.

Stdlib only (json, sys, io, argparse) — no `mcp` SDK, no pip install.
Python 3.8+.

Usage:
    python triz_mcp_server.py             # serve on stdio
    python triz_mcp_server.py --self-test # in-memory protocol self-check
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import tempfile

# ── sys.path bootstrap ──────────────────────────────────────────────────────
# Resolve the scripts dir from this file's location so the skill's own modules
# import cleanly no matter how python is invoked (cwd-independent, cross-platform).
_MCP_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.join(os.path.dirname(_MCP_DIR), "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import triz_router
import triz_evaluator
import triz_case_template
from triz_branches import detect_language  # noqa: E402  (after sys.path insert)

_DEFAULT_PROTOCOL_VERSION = "2025-06-18"
_SERVER_NAME = "triz-innovation"
_SERVER_VERSION = "0.1.0"

# ── Tool registry ───────────────────────────────────────────────────────────
_TOOLS = [
    {
        "name": "triz_route",
        "description": (
            "Suggest TRIZ methods for a free-text problem description "
            "(wraps triz_router.suggest_methods). Returns the detected "
            "engineering/physical contradictions and a ranked list of methods "
            "with scores and reasons."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {
                    "type": "string",
                    "description": "Free-text problem description (English or Italian).",
                },
                "branch": {
                    "type": "string",
                    "description": "Field branch id (general, business, software, rehab, mechanical, datascience, marketing, supplychain). Default: general.",
                },
            },
            "required": ["problem"],
        },
    },
    {
        "name": "triz_new_case",
        "description": (
            "Create a new dated TRIZ case markdown file from the template "
            "(wraps triz_case_template.create_case). Returns the absolute path "
            "of the created file."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short problem title, used for the slugified filename.",
                },
                "lang": {
                    "type": "string",
                    "description": "Template language: 'en' or 'it' (default: it).",
                },
            },
            "required": ["title"],
        },
    },
    {
        "name": "triz_evaluate",
        "description": (
            "Score candidate solutions 1-5 on eight criteria and return a "
            "sorted markdown table (wraps triz_evaluator.score + format_table). "
            "Each solution needs 'solution' plus the eight criteria as ints 1-5: "
            "impact, feasibility, cost, speed, risk, reversibility, complexity, ideality."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "solutions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "solution": {"type": "string"},
                            "impact": {"type": "integer", "minimum": 1, "maximum": 5},
                            "feasibility": {"type": "integer", "minimum": 1, "maximum": 5},
                            "cost": {"type": "integer", "minimum": 1, "maximum": 5},
                            "speed": {"type": "integer", "minimum": 1, "maximum": 5},
                            "risk": {"type": "integer", "minimum": 1, "maximum": 5},
                            "reversibility": {"type": "integer", "minimum": 1, "maximum": 5},
                            "complexity": {"type": "integer", "minimum": 1, "maximum": 5},
                            "ideality": {"type": "integer", "minimum": 1, "maximum": 5},
                        },
                        "required": [
                            "solution", "impact", "feasibility", "cost",
                            "speed", "risk", "reversibility", "complexity", "ideality",
                        ],
                    },
                },
            },
            "required": ["solutions"],
        },
    },
]


# ── stdio helpers ───────────────────────────────────────────────────────────
def _reconfigure_stdio() -> None:
    """Force UTF-8 on piped stdio (Windows pipes default to cp1252, which would
    crash on any non-ASCII output with ensure_ascii=False)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError, io.UnsupportedOperation):
        pass
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, io.UnsupportedOperation):
        pass


def _write_response(response: dict) -> None:
    """Write one JSON-RPC response object as a single stdout line, then flush."""
    sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _response(req_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error_response(req_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": message}}


def _text_result(req_id, text: str) -> dict:
    return _response(req_id, {"content": [{"type": "text", "text": text}]})


def _tool_error(req_id, text: str) -> dict:
    return _response(req_id, {"content": [{"type": "text", "text": text}],
                              "isError": True})


# ── handshake / version helpers ─────────────────────────────────────────────
def _looks_like_version(value) -> bool:
    """Heuristic: is this string shaped like an MCP protocol version?

    Accepts YYYY-MM-DD (the MCP convention, e.g. "2025-06-18") and dotted
    "X.Y.Z" versions. Anything else falls back to the server default.
    """
    if not isinstance(value, str) or not value:
        return False
    if value.count("-") == 2:
        y, m, d = value.split("-")
        return (len(y) == 4 and y.isdigit()
                and len(m) == 2 and m.isdigit()
                and len(d) == 2 and d.isdigit())
    if value.count(".") == 2:
        a, b, c = value.split(".")
        return a.isdigit() and b.isdigit() and c.isdigit()
    return False


def _handle_initialize(params: dict) -> dict:
    requested = params.get("protocolVersion")
    version = requested if _looks_like_version(requested) else _DEFAULT_PROTOCOL_VERSION
    return {
        "protocolVersion": version,
        "capabilities": {"tools": {}},
        "serverInfo": {"name": _SERVER_NAME, "version": _SERVER_VERSION},
    }


# ── tools/call implementations ──────────────────────────────────────────────
def _detect_lang(problem: str) -> str:
    try:
        return detect_language(problem)
    except Exception:
        return "en"


def _format_route_result(result: dict, problem: str, branch: str) -> str:
    """Human-readable route output — same flavor as the CLI `route` command."""
    lang = _detect_lang(problem)
    eng = result.get("engineering_contradiction")
    phys = result.get("physical_contradiction")
    methods = result.get("methods", [])

    lines = [
        f"Engineering Contradiction: {eng if eng else '(none detected)'}",
        f"Physical Contradiction: {phys if phys else '(none detected)'}",
        "",
        f"Branch: {branch}   Language: {lang}",
        "",
        f"{'Method':<55} {'Score':>5}",
        "-" * 62,
    ]
    for m in methods:
        lines.append(f"{m.get('method', '?'):<55} {m.get('score', 0):>5}")
    lines.append("")
    lines.append("Reasons:")
    for m in methods:
        lines.append(f"  [{m.get('method', '?')}] {m.get('why', '')}")
    return "\n".join(lines)


def _tool_triz_route(req_id, arguments: dict) -> dict:
    problem = arguments.get("problem")
    if not isinstance(problem, str) or not problem.strip():
        return _error_response(req_id, -32602,
                               "Invalid params: 'problem' (string) is required")
    branch = arguments.get("branch")
    if branch is None:
        branch = "general"
    if not isinstance(branch, str) or not branch:
        return _error_response(req_id, -32602,
                               "Invalid params: 'branch' must be a string")
    try:
        result = triz_router.suggest_methods(problem, branch=branch)
    except Exception as exc:
        return _tool_error(req_id, f"triz_route failed: {exc}")
    return _text_result(req_id, _format_route_result(result, problem, branch))


def _tool_triz_new_case(req_id, arguments: dict) -> dict:
    title = arguments.get("title")
    if not isinstance(title, str) or not title.strip():
        return _error_response(req_id, -32602,
                               "Invalid params: 'title' (string) is required")
    lang = arguments.get("lang")
    if lang is not None:
        if not isinstance(lang, str) or lang not in ("en", "it"):
            return _error_response(req_id, -32602,
                                   "Invalid params: 'lang' must be 'en' or 'it'")
    try:
        path = triz_case_template.create_case(title, lang=lang)
    except FileNotFoundError as exc:
        return _tool_error(req_id, f"triz_new_case failed: {exc}")
    except Exception as exc:
        return _tool_error(req_id, f"triz_new_case failed: {exc}")
    return _text_result(req_id, str(path))


def _validate_solutions(solutions: list) -> list:
    """Return a list of human-readable problems, or [] if all rows are valid.

    Each row must be an object with a string 'solution' plus all eight criteria
    as ints in 1..5.
    """
    problems: list = []
    for i, sol in enumerate(solutions):
        if not isinstance(sol, dict):
            problems.append(f"row {i}: expected an object")
            continue
        if not isinstance(sol.get("solution"), str):
            problems.append(f"row {i}: 'solution' must be a string")
        for crit in triz_evaluator.CRITERIA:
            value = sol.get(crit)
            if value is None:
                problems.append(f"row {i}: missing criterion '{crit}'")
            elif isinstance(value, bool) or not isinstance(value, int):
                problems.append(f"row {i}: criterion '{crit}' must be an integer 1-5")
            elif value < 1 or value > 5:
                problems.append(f"row {i}: criterion '{crit}' must be in 1..5")
    return problems


def _tool_triz_evaluate(req_id, arguments: dict) -> dict:
    solutions = arguments.get("solutions")
    if not isinstance(solutions, list) or not solutions:
        return _error_response(req_id, -32602,
                               "Invalid params: 'solutions' (non-empty array) is required")
    problems = _validate_solutions(solutions)
    if problems:
        return _tool_error(req_id, "triz_evaluate failed: " + "; ".join(problems))
    try:
        scored = triz_evaluator.score(solutions)
        table = triz_evaluator.format_table(scored)
    except Exception as exc:
        return _tool_error(req_id, f"triz_evaluate failed: {exc}")
    return _text_result(req_id, table)


def _handle_tools_call(req_id, params: dict) -> dict:
    name = params.get("name")
    if not isinstance(name, str) or not name:
        return _error_response(req_id, -32602, "Invalid params: missing tool name")
    arguments = params.get("arguments")
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        return _error_response(req_id, -32602,
                               "Invalid params: 'arguments' must be an object")

    if name == "triz_route":
        return _tool_triz_route(req_id, arguments)
    if name == "triz_new_case":
        return _tool_triz_new_case(req_id, arguments)
    if name == "triz_evaluate":
        return _tool_triz_evaluate(req_id, arguments)
    return _error_response(req_id, -32602, f"Invalid params: unknown tool {name!r}")


# ── protocol core ───────────────────────────────────────────────────────────
def handle_message(msg) -> dict | None:
    """Handle one parsed JSON-RPC request. Returns the response dict, or None
    for notifications (no reply). This is the pure, unit-testable core."""
    if not isinstance(msg, dict):
        return _error_response(None, -32600, "Invalid Request")

    # JSON-RPC notifications have no "id" — never reply to them.
    if "id" not in msg:
        return None

    req_id = msg.get("id")
    method = msg.get("method")
    if not isinstance(method, str) or not method:
        return _error_response(req_id, -32600, "Invalid Request")
    # Defensive: MCP notifications carry a method but must never be answered
    # even if a client (incorrectly) includes an id.
    if method.startswith("notifications/"):
        return None

    params = msg.get("params")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return _error_response(req_id, -32600, "Invalid Request")

    if method == "initialize":
        return _response(req_id, _handle_initialize(params))
    if method == "ping":
        return _response(req_id, {})
    if method == "tools/list":
        return _response(req_id, {"tools": list(_TOOLS)})
    if method == "tools/call":
        return _handle_tools_call(req_id, params)
    return _error_response(req_id, -32601, "Method not found")


def _handle_line(line: str) -> dict | None:
    """Parse one stdin line and produce a response, or None for notifications."""
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        return _error_response(None, -32700, "Parse error")
    try:
        return handle_message(msg)
    except Exception as exc:  # defensive: a handler bug must not crash the server
        req_id = msg.get("id") if isinstance(msg, dict) else None
        return _error_response(req_id, -32603, f"Internal error: {exc}")


# ── self-test ───────────────────────────────────────────────────────────────
def _temp_cases_dir() -> str:
    """Return a throwaway 'cases/' dir so the self-test never writes into the repo."""
    base = tempfile.mkdtemp(prefix="triz-mcp-selftest-")
    cases = os.path.join(base, "cases")
    os.makedirs(cases)
    return cases


def _self_test() -> None:
    """Drive the handler through an in-memory conversation, asserting each reply.
    Raises AssertionError on the first failure. No client, no network needed."""
    # 1. initialize — echoes a valid protocolVersion, echoes the requested one.
    r = handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {"protocolVersion": "2025-06-18",
                                   "capabilities": {}, "clientInfo": {}}})
    assert r is not None and r["id"] == 1, r
    assert r["result"]["protocolVersion"] == "2025-06-18", r
    assert r["result"]["capabilities"] == {"tools": {}}, r
    assert r["result"]["serverInfo"] == {"name": _SERVER_NAME, "version": _SERVER_VERSION}, r

    # initialize fallback for a non-version protocolVersion.
    r = handle_message({"jsonrpc": "2.0", "id": 2, "method": "initialize",
                        "params": {"protocolVersion": "not-a-version"}})
    assert r["result"]["protocolVersion"] == _DEFAULT_PROTOCOL_VERSION, r

    # 2. notification -> None (no output).
    assert handle_message({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None

    # 3. ping.
    r = handle_message({"jsonrpc": "2.0", "id": 3, "method": "ping"})
    assert r is not None and r["id"] == 3 and r["result"] == {}, r

    # 4. tools/list — exactly the three tools.
    r = handle_message({"jsonrpc": "2.0", "id": 4, "method": "tools/list"})
    names = [t["name"] for t in r["result"]["tools"]]
    assert names == ["triz_route", "triz_new_case", "triz_evaluate"], names

    # 5. tools/call triz_route.
    r = handle_message({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                        "params": {"name": "triz_route",
                                   "arguments": {"problem": "more speed but less reliability"}}})
    assert "error" not in r, r
    text = r["result"]["content"][0]["text"]
    assert "40 Inventive Principles" in text, text

    # 6. tools/call triz_evaluate (valid rows -> markdown table).
    r = handle_message({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                        "params": {"name": "triz_evaluate", "arguments": {"solutions": [
                            {"solution": "Gamified reminders", "impact": 4, "feasibility": 3,
                             "cost": 2, "speed": 4, "risk": 3, "reversibility": 5,
                             "complexity": 2, "ideality": 3},
                            {"solution": "Therapist calls", "impact": 5, "feasibility": 3,
                             "cost": 1, "speed": 2, "risk": 4, "reversibility": 4,
                             "complexity": 4, "ideality": 2},
                        ]}}})
    assert "error" not in r, r
    assert "Solution" in r["result"]["content"][0]["text"], r

    # 7. tools/call triz_new_case — redirect the output dir so no file lands in the repo.
    tmp_cases = _temp_cases_dir()
    orig = triz_case_template.create_case

    def _patched_create_case(title, cases_dir=None, lang=None):
        return orig(title, cases_dir=tmp_cases, lang=lang)

    triz_case_template.create_case = _patched_create_case
    try:
        r = handle_message({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                            "params": {"name": "triz_new_case",
                                       "arguments": {"title": "MCP Self Test"}}})
    finally:
        triz_case_template.create_case = orig
    assert "error" not in r, r
    assert r["result"]["content"][0]["text"], r

    # 8. unknown method -> -32601.
    r = handle_message({"jsonrpc": "2.0", "id": 8, "method": "bogus/method"})
    assert r["error"]["code"] == -32601, r


# ── CLI entrypoint ──────────────────────────────────────────────────────────
def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="triz_mcp_server",
        description="TRIZ innovation MCP server (stdlib JSON-RPC 2.0 over stdio).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run an in-memory protocol self-check and exit (no client/network needed).",
    )
    args = parser.parse_args(argv)

    _reconfigure_stdio()

    if args.self_test:
        try:
            _self_test()
        except AssertionError as exc:
            print(f"SELF-TEST FAILED: {exc}", file=sys.stderr)
            sys.exit(1)
        print("SELF-TEST OK")
        sys.exit(0)

    # Serve: one JSON request per stdin line, one response per stdout line.
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = _handle_line(line)
        if response is not None:
            _write_response(response)


if __name__ == "__main__":
    main()
