#!/usr/bin/env python3
"""Contract and wire tests for the read-only MCP server."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SERVER_DIR = ROOT / "skills" / "triz-coding-method" / "scripts"
SERVER = SERVER_DIR / "triz_mcp_server.py"
sys.path.insert(0, str(SERVER_DIR))
import triz_mcp_server as mcp  # noqa: E402


def request(method, params=None, request_id=1):
    value = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        value["params"] = params
    return value


def call(name, arguments):
    return mcp.handle_message(request("tools/call", {"name": name, "arguments": arguments}))


def sample_solution(name="small"):
    return {
        "solution": name,
        "impact": 3,
        "feasibility": 4,
        "cost": 5,
        "speed": 4,
        "risk": 5,
        "reversibility": 5,
        "complexity": 5,
        "ideality": 4,
    }


class TestProtocol(unittest.TestCase):
    def test_initialize_supported_version(self):
        result = mcp.handle_message(request("initialize", {"protocolVersion": "2025-06-18"}))
        self.assertEqual(result["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual(result["result"]["serverInfo"], {"name": "triz-coding-method", "version": "0.1.0"})

    def test_initialize_rejects_unsupported_version(self):
        result = mcp.handle_message(request("initialize", {"protocolVersion": "2099-01-01"}))
        self.assertEqual(result["error"]["code"], -32602)

    def test_requires_jsonrpc_2(self):
        result = mcp.handle_message({"id": 1, "method": "ping"})
        self.assertEqual(result["error"]["code"], -32600)

    def test_rejects_extra_request_fields(self):
        message = request("ping")
        message["extra"] = True
        self.assertEqual(mcp.handle_message(message)["error"]["code"], -32600)

    def test_notification_has_no_response(self):
        self.assertIsNone(mcp.handle_message({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_unknown_method(self):
        self.assertEqual(mcp.handle_message(request("unknown"))["error"]["code"], -32601)


class TestSchemas(unittest.TestCase):
    def setUp(self):
        self.tools = mcp.handle_message(request("tools/list"))["result"]["tools"]

    def test_exact_read_only_tools(self):
        self.assertEqual([tool["name"] for tool in self.tools], [
            "triz_coding_route", "triz_matrix_lookup", "triz_coding_evaluate"
        ])
        self.assertNotIn("triz_new_case", json.dumps(self.tools))

    def test_all_object_schemas_are_closed(self):
        def visit(node):
            if isinstance(node, dict):
                if node.get("type") == "object":
                    self.assertIs(node.get("additionalProperties"), False)
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for value in node:
                    visit(value)
        for tool in self.tools:
            visit(tool["inputSchema"])

    def test_schema_limits(self):
        schemas = {tool["name"]: tool["inputSchema"] for tool in self.tools}
        self.assertEqual(schemas["triz_coding_route"]["properties"]["problem"]["maxLength"], 20000)
        solutions = schemas["triz_coding_evaluate"]["properties"]["solutions"]
        self.assertEqual(solutions["maxItems"], 50)
        self.assertEqual(solutions["items"]["properties"]["solution"]["maxLength"], 2000)


class TestTools(unittest.TestCase):
    def test_route_structured_content(self):
        result = call("triz_coding_route", {"problem": "more speed but less reliability"})["result"]
        self.assertFalse(result["isError"])
        structured = result["structuredContent"]
        self.assertEqual(structured["mode"], "focused")
        self.assertIn(5, structured["stages"])
        self.assertIsNotNone(structured["contradiction"])
        self.assertTrue(all(not ref.startswith(("/", "C:")) for ref in structured["references"]))

    def test_route_explicit_modes(self):
        for mode in ("lite", "focused", "ultra"):
            with self.subTest(mode=mode):
                result = call("triz_coding_route", {"problem": "choose an API", "mode": mode})
                self.assertEqual(result["result"]["structuredContent"]["mode"], mode)

    def test_route_rejects_size_and_extra(self):
        self.assertTrue(call("triz_coding_route", {"problem": "x" * 20001})["result"]["isError"])
        self.assertTrue(call("triz_coding_route", {"problem": "x", "branch": "general"})["result"]["isError"])

    def test_matrix_exact_lookup(self):
        result = call("triz_matrix_lookup", {"improving": 18, "worsening": 35})["result"]
        self.assertFalse(result["isError"])
        self.assertEqual([item["id"] for item in result["structuredContent"]["principles"]], [15, 1, 19])

    def test_matrix_rejects_bool_and_range(self):
        self.assertTrue(call("triz_matrix_lookup", {"improving": True, "worsening": 2})["result"]["isError"])
        self.assertTrue(call("triz_matrix_lookup", {"improving": 40, "worsening": 2})["result"]["isError"])

    def test_evaluate_orders_scores(self):
        low = sample_solution("low")
        low.update({criterion: 1 for criterion in mcp.triz_evaluator.CRITERIA})
        result = call("triz_coding_evaluate", {"solutions": [low, sample_solution("high")]})["result"]
        self.assertFalse(result["isError"])
        self.assertEqual(result["structuredContent"]["solutions"][0]["solution"], "high")

    def test_evaluate_rejects_limits(self):
        self.assertTrue(call("triz_coding_evaluate", {"solutions": []})["result"]["isError"])
        self.assertTrue(call("triz_coding_evaluate", {"solutions": [sample_solution()] * 51})["result"]["isError"])
        too_long = sample_solution("x" * 2001)
        self.assertTrue(call("triz_coding_evaluate", {"solutions": [too_long]})["result"]["isError"])

    def test_evaluate_rejects_bad_and_extra_fields(self):
        bad = sample_solution()
        bad["risk"] = True
        self.assertTrue(call("triz_coding_evaluate", {"solutions": [bad]})["result"]["isError"])
        extra = sample_solution()
        extra["notes"] = "no"
        self.assertTrue(call("triz_coding_evaluate", {"solutions": [extra]})["result"]["isError"])

    def test_internal_error_is_sanitized(self):
        payload = json.dumps(request("tools/call", {"name": "triz_coding_route", "arguments": {"problem": "x"}})).encode()
        with mock.patch.object(mcp.coding_method, "route", side_effect=RuntimeError("C:\\private\\secret.py")):
            result = mcp._handle_payload(payload)
        rendered = json.dumps(result)
        self.assertIn("Internal error", rendered)
        self.assertNotIn("private", rendered)
        self.assertNotIn("Traceback", rendered)


class TestWire(unittest.TestCase):
    def _serve(self, payload):
        output = io.BytesIO()
        mcp.serve_streams(io.BytesIO(payload), output)
        return output.getvalue()

    def test_newline_framing(self):
        wire = json.dumps(request("ping")).encode() + b"\n"
        response = json.loads(self._serve(wire))
        self.assertEqual(response["result"], {})

    def test_content_length_framing(self):
        body = json.dumps(request("ping")).encode()
        wire = b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
        response_wire = self._serve(wire)
        _, response_body = response_wire.split(b"\r\n\r\n", 1)
        self.assertEqual(json.loads(response_body)["result"], {})

    def test_malformed_json(self):
        response = json.loads(self._serve(b"{bad}\n"))
        self.assertEqual(response["error"]["code"], -32700)

    def test_oversized_newline_request(self):
        response = json.loads(self._serve(b"{" + b"x" * (mcp.MAX_REQUEST_BYTES + 10) + b"}\n"))
        self.assertEqual(response["error"]["message"], "Request too large")

    def test_oversized_framed_request(self):
        size = mcp.MAX_REQUEST_BYTES + 1
        wire = b"Content-Length: " + str(size).encode() + b"\r\n\r\n" + b"x" * size
        response_wire = self._serve(wire)
        _, body = response_wire.split(b"\r\n\r\n", 1)
        self.assertEqual(json.loads(body)["error"]["message"], "Request too large")

    def test_self_test_cli(self):
        completed = subprocess.run([sys.executable, str(SERVER), "--self-test"], capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("SELF-TEST OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
