#!/usr/bin/env python3
"""Read-only TRIZ Coding Method MCP server over stdio.

Supports newline-delimited JSON-RPC and Content-Length framing. Requests are
bounded to 256 KiB and errors never include tracebacks or local paths.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Any, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
_ENGINE_SCRIPTS = _SCRIPT_DIR.parent / "engine" / "scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
if str(_ENGINE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ENGINE_SCRIPTS))

import method as coding_method  # noqa: E402
import triz_evaluator  # noqa: E402
import triz_matrix  # noqa: E402

SERVER_NAME = "triz-coding-method"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL_VERSION = "2025-06-18"
SUPPORTED_PROTOCOL_VERSIONS = frozenset(
    {"2024-11-05", "2025-03-26", "2025-06-18"}
)
MAX_REQUEST_BYTES = 256 * 1024
MAX_HEADER_BYTES = 8192
MAX_PROBLEM_CHARS = 20_000
MAX_SOLUTIONS = 50
MAX_SOLUTION_CHARS = 2_000

_SOLUTION_PROPERTIES = {
    "solution": {"type": "string", "minLength": 1, "maxLength": MAX_SOLUTION_CHARS},
    **{
        criterion: {"type": "integer", "minimum": 1, "maximum": 5}
        for criterion in triz_evaluator.CRITERIA
    },
}

TOOLS = [
    {
        "name": "triz_coding_route",
        "description": "Select the smallest safe coding-decision path and escalate to TRIZ only for a remaining contradiction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {"type": "string", "minLength": 1, "maxLength": MAX_PROBLEM_CHARS},
                "mode": {"type": "string", "enum": list(coding_method.MODES), "default": "auto"},
            },
            "required": ["problem"],
            "additionalProperties": False,
        },
    },
    {
        "name": "triz_matrix_lookup",
        "description": "Look up inventive principles for one improving/worsening parameter pair.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "improving": {"type": "integer", "minimum": 1, "maximum": 39},
                "worsening": {"type": "integer", "minimum": 1, "maximum": 39},
            },
            "required": ["improving", "worsening"],
            "additionalProperties": False,
        },
    },
    {
        "name": "triz_coding_evaluate",
        "description": "Rank 1-50 coding solutions using eight explicit 1-5 criteria.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "solutions": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": MAX_SOLUTIONS,
                    "items": {
                        "type": "object",
                        "properties": _SOLUTION_PROPERTIES,
                        "required": ["solution", *triz_evaluator.CRITERIA],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["solutions"],
            "additionalProperties": False,
        },
    },
]


def _response(request_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _tool_result(request_id: Any, text: str, structured: dict) -> dict:
    return _response(
        request_id,
        {
            "content": [{"type": "text", "text": text}],
            "structuredContent": structured,
            "isError": False,
        },
    )


def _tool_error(request_id: Any, message: str) -> dict:
    return _response(
        request_id,
        {"content": [{"type": "text", "text": message}], "isError": True},
    )


def _closed_arguments(arguments: Any, allowed: set[str]) -> Optional[str]:
    if not isinstance(arguments, dict):
        return "arguments must be an object"
    extras = sorted(set(arguments) - allowed)
    if extras:
        return "unexpected argument(s): " + ", ".join(extras)
    return None


def _route_tool(request_id: Any, arguments: Any) -> dict:
    problem = _closed_arguments(arguments, {"problem", "mode"})
    if problem:
        return _tool_error(request_id, "Invalid parameters: " + problem)
    text = arguments.get("problem")
    mode = arguments.get("mode", "auto")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_PROBLEM_CHARS:
        return _tool_error(request_id, f"Invalid parameters: problem must contain 1-{MAX_PROBLEM_CHARS} characters")
    if mode not in coding_method.MODES:
        return _tool_error(request_id, "Invalid parameters: unsupported mode")
    try:
        result = coding_method.route(text, mode)
    except (TypeError, ValueError):
        return _tool_error(request_id, "Invalid parameters")
    summary = [
        f"Mode: {result['mode']}",
        "Stages: " + ", ".join(str(stage) for stage in result["stages"]),
        f"Smallest likely rung: {result['selected_rung']}",
        "IFR: " + result["ifr"],
        "Almost-IFR: " + result["almost_ifr"],
        "TRIZ escalation: " + ("required" if result["triz_escalated"] else "not required"),
    ]
    structured = {
        "mode": result["mode"],
        "stages": result["stages"],
        "ladder": result["ladder"],
        "ifr": result["ifr"],
        "almost_ifr": result["almost_ifr"],
        "contradiction": result["remaining_contradiction"],
        "references": result["references"],
    }
    return _tool_result(request_id, "\n".join(summary), structured)


def _matrix_tool(request_id: Any, arguments: Any) -> dict:
    problem = _closed_arguments(arguments, {"improving", "worsening"})
    if problem:
        return _tool_error(request_id, "Invalid parameters: " + problem)
    improving = arguments.get("improving")
    worsening = arguments.get("worsening")
    if any(isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 39 for value in (improving, worsening)):
        return _tool_error(request_id, "Invalid parameters: improving and worsening must be integers in 1..39")
    try:
        result = triz_matrix.lookup(improving, worsening)
    except (TypeError, ValueError):
        return _tool_error(request_id, "Invalid parameters")
    principles = result["principles"]
    text = (
        f"Improve {result['improving']['id']} {result['improving']['name']}; "
        f"worsens {result['worsening']['id']} {result['worsening']['name']}.\n"
        + ("Principles: " + ", ".join(f"{p['id']} {p['name']}" for p in principles) if principles else "No matrix principles found.")
    )
    if result.get("note"):
        text += "\n" + result["note"]
    return _tool_result(request_id, text, result)


def _validate_solutions(value: Any) -> Optional[str]:
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_SOLUTIONS:
        return f"solutions must contain 1-{MAX_SOLUTIONS} items"
    allowed = {"solution", *triz_evaluator.CRITERIA}
    for index, solution in enumerate(value):
        if not isinstance(solution, dict):
            return f"solution {index} must be an object"
        extras = sorted(set(solution) - allowed)
        missing = sorted(allowed - set(solution))
        if extras:
            return f"solution {index} has unexpected fields"
        if missing:
            return f"solution {index} is missing required fields"
        label = solution["solution"]
        if not isinstance(label, str) or not label.strip() or len(label) > MAX_SOLUTION_CHARS:
            return f"solution {index} text must contain 1-{MAX_SOLUTION_CHARS} characters"
        for criterion in triz_evaluator.CRITERIA:
            score = solution[criterion]
            if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
                return f"solution {index} scores must be integers in 1..5"
    return None


def _evaluate_tool(request_id: Any, arguments: Any) -> dict:
    problem = _closed_arguments(arguments, {"solutions"})
    if problem:
        return _tool_error(request_id, "Invalid parameters: " + problem)
    solutions = arguments.get("solutions")
    problem = _validate_solutions(solutions)
    if problem:
        return _tool_error(request_id, "Invalid parameters: " + problem)
    try:
        ranked = triz_evaluator.score(solutions)
        text = triz_evaluator.format_table(ranked)
    except (TypeError, ValueError):
        return _tool_error(request_id, "Invalid parameters")
    return _tool_result(request_id, text, {"solutions": ranked})


def _tools_call(request_id: Any, params: dict) -> dict:
    if set(params) - {"name", "arguments"}:
        return _error(request_id, -32602, "Invalid params")
    name = params.get("name")
    arguments = params.get("arguments", {})
    if name == "triz_coding_route":
        return _route_tool(request_id, arguments)
    if name == "triz_matrix_lookup":
        return _matrix_tool(request_id, arguments)
    if name == "triz_coding_evaluate":
        return _evaluate_tool(request_id, arguments)
    return _error(request_id, -32602, "Unknown tool")


def handle_message(message: Any) -> Optional[dict]:
    """Handle one parsed JSON-RPC request without I/O."""
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
        return _error(None, -32600, "Invalid Request")
    if "id" not in message:
        return None
    request_id = message.get("id")
    if isinstance(request_id, bool) or not isinstance(request_id, (str, int, type(None))):
        return _error(None, -32600, "Invalid Request")
    if set(message) - {"jsonrpc", "id", "method", "params"}:
        return _error(request_id, -32600, "Invalid Request")
    method_name = message.get("method")
    params = message.get("params", {})
    if not isinstance(method_name, str) or not isinstance(params, dict):
        return _error(request_id, -32600, "Invalid Request")
    if method_name == "initialize":
        version = params.get("protocolVersion")
        if version not in SUPPORTED_PROTOCOL_VERSIONS:
            return _error(request_id, -32602, "Unsupported protocol version")
        return _response(
            request_id,
            {
                "protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )
    if method_name == "ping":
        return _response(request_id, {})
    if method_name == "tools/list":
        return _response(request_id, {"tools": TOOLS})
    if method_name == "tools/call":
        return _tools_call(request_id, params)
    if method_name.startswith("notifications/"):
        return None
    return _error(request_id, -32601, "Method not found")


def _handle_payload(payload: bytes) -> Optional[dict]:
    if len(payload) > MAX_REQUEST_BYTES:
        return _error(None, -32600, "Request too large")
    try:
        message = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _error(None, -32700, "Parse error")
    try:
        return handle_message(message)
    except Exception:
        return _error(message.get("id") if isinstance(message, dict) else None, -32603, "Internal error")


def _handle_line(line: str) -> Optional[dict]:
    return _handle_payload(line.encode("utf-8"))


def _encode(response: dict) -> bytes:
    return json.dumps(response, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _discard(stream: Any, count: int) -> None:
    remaining = count
    while remaining:
        chunk = stream.read(min(remaining, 65_536))
        if not chunk:
            return
        remaining -= len(chunk)


def serve_streams(raw_in: Any, raw_out: Any) -> None:
    """Serve binary streams. Kept public for framing/limit tests."""
    while True:
        line = raw_in.readline(MAX_REQUEST_BYTES + 2)
        if not line:
            return
        if not line.strip():
            continue
        framed = not line.lstrip().startswith((b"{", b"["))
        if not framed:
            if len(line) > MAX_REQUEST_BYTES + 1:
                while line and not line.endswith(b"\n"):
                    line = raw_in.readline(MAX_REQUEST_BYTES + 2)
                response = _error(None, -32600, "Request too large")
            else:
                response = _handle_payload(line.rstrip(b"\r\n"))
        else:
            headers = [line]
            header_bytes = len(line)
            while True:
                item = raw_in.readline(MAX_HEADER_BYTES + 1)
                if not item or item in (b"\r\n", b"\n"):
                    break
                headers.append(item)
                header_bytes += len(item)
                if header_bytes > MAX_HEADER_BYTES:
                    break
            length = None
            if header_bytes <= MAX_HEADER_BYTES:
                for header in headers:
                    name, separator, value = header.partition(b":")
                    if separator and name.strip().lower() == b"content-length":
                        try:
                            length = int(value.strip())
                        except ValueError:
                            length = None
                        break
            if length is None or length < 0:
                response = _error(None, -32600, "Invalid Content-Length")
            elif length > MAX_REQUEST_BYTES:
                _discard(raw_in, length)
                response = _error(None, -32600, "Request too large")
            else:
                body = raw_in.read(length)
                response = _handle_payload(body) if len(body) == length else _error(None, -32600, "Incomplete request")
        if response is None:
            continue
        payload = _encode(response)
        if framed:
            raw_out.write(b"Content-Length: " + str(len(payload)).encode("ascii") + b"\r\n\r\n" + payload)
        else:
            raw_out.write(payload + b"\n")
        raw_out.flush()


def _serve_stdio() -> None:
    raw_in = getattr(sys.stdin, "buffer", sys.stdin)
    raw_out = getattr(sys.stdout, "buffer", sys.stdout)
    serve_streams(raw_in, raw_out)


def _self_test() -> None:
    initialize = handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": DEFAULT_PROTOCOL_VERSION}})
    assert initialize and initialize["result"]["serverInfo"]["name"] == SERVER_NAME
    listed = handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert [tool["name"] for tool in listed["result"]["tools"]] == [
        "triz_coding_route", "triz_matrix_lookup", "triz_coding_evaluate"
    ]
    routed = handle_message({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "triz_coding_route", "arguments": {"problem": "more speed but less reliability"}}})
    assert routed and not routed["result"]["isError"]


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        _self_test()
        print("SELF-TEST OK")
        return
    _serve_stdio()


if __name__ == "__main__":
    main()
