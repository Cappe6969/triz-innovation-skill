#!/usr/bin/env python3
"""Tests for the stdlib MCP server (mcp/triz_mcp_server.py).

Pytest-compatible; also runnable with plain Python (unittest).

Usage:
    pytest tests/test_triz_mcp.py
    python tests/test_triz_mcp.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_REPO_ROOT = Path(__file__).resolve().parent.parent
_MCP_DIR = (
    _REPO_ROOT / ".claude" / "skills" / "triz-innovation" / "mcp"
)
_MCP_SERVER = _MCP_DIR / "triz_mcp_server.py"

# Importing the server bootstraps the scripts dir onto sys.path and pulls in
# triz_router / triz_evaluator / triz_case_template as module attributes.
sys.path.insert(0, str(_MCP_DIR))
import triz_mcp_server as mcp  # noqa: E402


def _req(method: str, params=None, req_id: int = 1) -> dict:
    msg: dict = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        msg["params"] = params
    return msg


def _solutions() -> list[dict]:
    return [
        {"solution": "Gamified reminders", "impact": 4, "feasibility": 3,
         "cost": 2, "speed": 4, "risk": 3, "reversibility": 5,
         "complexity": 2, "ideality": 3},
        {"solution": "Therapist calls", "impact": 5, "feasibility": 3,
         "cost": 1, "speed": 2, "risk": 4, "reversibility": 4,
         "complexity": 4, "ideality": 2},
    ]


class TestMCPHandleMessage(unittest.TestCase):
    """Unit tests on the pure handle_message core."""

    # ── initialize ──────────────────────────────────────────────────────────

    def test_initialize_shape_and_protocol_echo(self):
        """initialize returns capabilities + serverInfo, echoing a valid version."""
        r = mcp.handle_message(_req(
            "initialize",
            {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {}},
        ))
        self.assertEqual(r["id"], 1)
        self.assertEqual(r["jsonrpc"], "2.0")
        self.assertEqual(r["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(r["result"]["capabilities"], {"tools": {}})
        self.assertEqual(r["result"]["serverInfo"],
                         {"name": "triz-innovation", "version": "0.1.0"})

    def test_initialize_fallback_protocol_version(self):
        """Non-version protocolVersion falls back to the server default."""
        for bad in ("garbage", "1.0", "", None, 123, True):
            r = mcp.handle_message(_req("initialize", {"protocolVersion": bad}))
            self.assertEqual(r["result"]["protocolVersion"], "2025-06-18",
                             f"for {bad!r}")

    # ── tools/list ──────────────────────────────────────────────────────────

    def test_tools_list_exact_tools_with_schemas(self):
        """tools/list has exactly triz_route / triz_new_case / triz_evaluate,
        each with a valid object inputSchema."""
        r = mcp.handle_message(_req("tools/list"))
        tools = r["result"]["tools"]
        self.assertEqual([t["name"] for t in tools],
                         ["triz_route", "triz_new_case", "triz_evaluate"])
        for t in tools:
            self.assertIn("inputSchema", t)
            schema = t["inputSchema"]
            self.assertEqual(schema["type"], "object")
            self.assertIn("properties", schema)
            self.assertIn("required", schema)
            self.assertIsInstance(schema["properties"], dict)

    # ── tools/call triz_route ───────────────────────────────────────────────

    def test_tools_call_triz_route_returns_method_text(self):
        """triz_route returns a text block containing a recommended method."""
        r = mcp.handle_message(_req(
            "tools/call",
            {"name": "triz_route",
             "arguments": {"problem": "more speed but less reliability"}},
        ))
        self.assertNotIn("error", r)
        self.assertNotIn("isError", r.get("result", {}))
        text = r["result"]["content"][0]["text"]
        self.assertIn("40 Inventive Principles", text)
        self.assertIn("Engineering Contradiction", text)

    def test_tools_call_triz_route_missing_problem_invalid_params(self):
        """Missing required 'problem' -> -32602."""
        r = mcp.handle_message(_req(
            "tools/call",
            {"name": "triz_route", "arguments": {}},
        ))
        self.assertEqual(r["error"]["code"], -32602)

    def test_tools_call_triz_route_unknown_branch_is_error(self):
        """An unknown branch surfaces as a friendly isError result, not a crash."""
        r = mcp.handle_message(_req(
            "tools/call",
            {"name": "triz_route",
             "arguments": {"problem": "x", "branch": "bogus"}},
        ))
        self.assertEqual(r["result"]["isError"], True)
        self.assertIn("triz_route failed", r["result"]["content"][0]["text"])

    # ── tools/call triz_evaluate ────────────────────────────────────────────

    def test_tools_call_triz_evaluate_returns_table(self):
        """Valid rows produce the sorted markdown table."""
        r = mcp.handle_message(_req(
            "tools/call",
            {"name": "triz_evaluate", "arguments": {"solutions": _solutions()}},
        ))
        self.assertNotIn("error", r)
        text = r["result"]["content"][0]["text"]
        self.assertIn("Solution", text)
        self.assertIn("Impact", text)
        self.assertIn("Total", text)
        self.assertIn("Gamified reminders", text)
        self.assertIn("Therapist calls", text)

    def test_tools_call_triz_evaluate_bad_criterion_is_error(self):
        """A criterion out of 1..5 -> isError naming the problem."""
        bad = _solutions()
        bad[0]["impact"] = 9
        r = mcp.handle_message(_req(
            "tools/call",
            {"name": "triz_evaluate", "arguments": {"solutions": bad}},
        ))
        self.assertEqual(r["result"]["isError"], True)
        self.assertIn("impact", r["result"]["content"][0]["text"].lower())

    def test_tools_call_triz_evaluate_non_int_criterion_is_error(self):
        """A non-integer criterion (bool/str) -> isError."""
        bad = _solutions()
        bad[0]["cost"] = "cheap"
        r = mcp.handle_message(_req(
            "tools/call",
            {"name": "triz_evaluate", "arguments": {"solutions": bad}},
        ))
        self.assertEqual(r["result"]["isError"], True)
        self.assertIn("cost", r["result"]["content"][0]["text"].lower())

    # ── tools/call triz_new_case ────────────────────────────────────────────

    def test_tools_call_triz_new_case_missing_template_is_error(self):
        """Absent template path -> friendly isError (patched like test_triz.py)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing-template.md"
            with mock.patch.object(mcp.triz_case_template, "_template_path",
                                   return_value=missing):
                r = mcp.handle_message(_req(
                    "tools/call",
                    {"name": "triz_new_case", "arguments": {"title": "X"}},
                ))
        self.assertEqual(r["result"]["isError"], True)
        self.assertIn("triz_new_case", r["result"]["content"][0]["text"])

    def test_tools_call_triz_new_case_missing_title_invalid_params(self):
        """Missing required 'title' -> -32602."""
        r = mcp.handle_message(_req(
            "tools/call",
            {"name": "triz_new_case", "arguments": {}},
        ))
        self.assertEqual(r["error"]["code"], -32602)

    def test_tools_call_triz_new_case_writes_to_cases_dir(self):
        """With a patched _repo_root, create_case writes into the temp cases dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "cases").mkdir()
            (tmp / "cases" / "template-triz-case.md").write_text(
                "# Title\n\nBody\n", encoding="utf-8"
            )
            with mock.patch.object(mcp.triz_case_template, "_repo_root",
                                   return_value=tmp):
                r = mcp.handle_message(_req(
                    "tools/call",
                    {"name": "triz_new_case", "arguments": {"title": "MCP Unit Test"}},
                ))
        self.assertNotIn("error", r)
        self.assertIn("cases", r["result"]["content"][0]["text"])

    # ── error mapping / protocol ────────────────────────────────────────────

    def test_unknown_method(self):
        """Unknown method -> -32601 Method not found."""
        r = mcp.handle_message(_req("no/such/method"))
        self.assertEqual(r["error"]["code"], -32601)

    def test_invalid_params_missing_tool_name(self):
        """tools/call without a tool name -> -32602 Invalid params."""
        r = mcp.handle_message(_req("tools/call", {}))
        self.assertEqual(r["error"]["code"], -32602)

    def test_invalid_params_unknown_tool(self):
        """tools/call for an unknown tool -> -32602 Invalid params."""
        r = mcp.handle_message(_req(
            "tools/call", {"name": "nope", "arguments": {}},
        ))
        self.assertEqual(r["error"]["code"], -32602)

    def test_notification_returns_none(self):
        """A JSON-RPC notification (no id) must produce no response."""
        self.assertIsNone(mcp.handle_message(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}
        ))

    def test_ping_returns_empty_result(self):
        r = mcp.handle_message(_req("ping"))
        self.assertEqual(r["result"], {})

    def test_bad_json_parse_error(self):
        """Non-JSON line -> -32700 Parse error with id null."""
        r = mcp._handle_line("{not json")
        self.assertEqual(r["error"]["code"], -32700)
        self.assertIsNone(r["id"])

    def test_non_object_request_invalid_request(self):
        """A valid-JSON non-object request -> -32600 Invalid Request."""
        r = mcp._handle_line("[1, 2, 3]")
        self.assertEqual(r["error"]["code"], -32600)


class TestMCPSubprocess(unittest.TestCase):
    """One subprocess test exercising the real --self-test CLI mode."""

    def test_self_test_subprocess(self):
        """`python triz_mcp_server.py --self-test` exits 0 and prints OK."""
        proc = subprocess.run(
            [sys.executable, str(_MCP_SERVER), "--self-test"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("SELF-TEST OK", proc.stdout)
        self.assertEqual(proc.stdout.count("\n"), 1,
                         "self-test should print exactly one line")


if __name__ == "__main__":
    unittest.main()
