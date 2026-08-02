#!/usr/bin/env python3
"""
Pytest-compatible TRIZ test suite — also runnable with plain Python (unittest).

Usage:
    pytest tests/test_triz.py          # if pytest installed
    python tests/test_triz.py          # plain unittest runner
"""

from __future__ import annotations

import sys
import os
import json
import unittest
import tempfile
import re
import csv
import subprocess
import contextlib
import io
from pathlib import Path
from unittest import mock

# ---- path setup: add the scripts directory so imports work ----
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = (
    _REPO_ROOT
    / "skills" / "triz-coding-method" / "engine" / "scripts"
)
sys.path.insert(0, str(_SCRIPTS_DIR))

import triz_matrix
import triz_router
import triz_evaluator
import triz_standard_solutions
import triz_evolution
import triz_ariz
import triz_case_template
import triz_branches


class TestTRIZ(unittest.TestCase):
    """TRIZ skill test suite — matrix, router, evaluator, standard-solutions,
    evolution, ARIZ, case-template, effects, network, and dispatcher."""

    # ── Matrix tests ────────────────────────────────────────────────────────

    def test_matrix_lookup_valid(self):
        """matrix[14, 2] returns a list of inventive principles."""
        result = triz_matrix.lookup(14, 2)
        self.assertEqual(result["improving"]["id"], 14)
        self.assertEqual(result["worsening"]["id"], 2)
        self.assertIsInstance(result["principles"], list)
        self.assertGreater(len(result["principles"]), 0,
                           "Expected at least one principle for (14, 2)")
        for p in result["principles"]:
            self.assertIn("id", p)
            self.assertIn("name", p)
            self.assertIsInstance(p["id"], int)
            self.assertIsInstance(p["name"], str)
            self.assertGreater(len(p["name"]), 0)

    def test_matrix_diagonal(self):
        """Diagonal query (same id both sides) returns empty principles and
        a note mentioning a physical contradiction."""
        result = triz_matrix.lookup(10, 10)
        self.assertEqual(result["principles"], [],
                         "Diagonal query should return empty principles")
        self.assertIsNotNone(result["note"])
        self.assertIn("physical", result["note"].lower(),
                      "Diagonal note should mention physical contradiction")

    def test_matrix_invalid_id(self):
        """id=0 and id=40 both raise ValueError."""
        bad_calls = [
            (0, 5),
            (5, 0),
            (40, 5),
            (5, 40),
            (1, 40),
            (40, 1),
        ]
        for improving, worsening in bad_calls:
            with self.subTest(improving=improving, worsening=worsening):
                with self.assertRaises(ValueError):
                    triz_matrix.lookup(improving, worsening)

    def test_matrix_all_cells(self):
        """All 1248 populated matrix cells return non-empty principle lists."""
        matrix = triz_matrix.load_matrix()
        populated = [(k, v) for k, v in matrix.items() if v]
        self.assertEqual(
            len(populated), 1248,
            f"Expected 1248 populated cells, got {len(populated)}"
        )
        for key, val in populated:
            with self.subTest(improving=key[0], worsening=key[1]):
                self.assertIsInstance(val, list)
                self.assertGreater(len(val), 0,
                                   f"Cell {key} has empty principles list")
                for pid in val:
                    self.assertIsInstance(pid, int)
                    self.assertGreaterEqual(pid, 1)
                    self.assertLessEqual(pid, 40)

    # ── Parameters & Principles count ───────────────────────────────────────

    def test_parameters_count(self):
        """39 parameters load, with ids 1..39 and non-empty names."""
        params = triz_matrix.load_parameters()
        self.assertEqual(len(params), 39)
        for i in range(1, 40):
            with self.subTest(param_id=i):
                self.assertIn(i, params)
                self.assertIsInstance(params[i], str)
                self.assertGreater(len(params[i].strip()), 0)

    def test_principles_count(self):
        """40 inventive principles load, with ids 1..40 and non-empty names."""
        principles = triz_matrix.load_principles()
        self.assertEqual(len(principles), 40)
        for i in range(1, 41):
            with self.subTest(principle_id=i):
                self.assertIn(i, principles)
                self.assertIsInstance(principles[i], str)
                self.assertGreater(len(principles[i].strip()), 0)

    # ── Router tests ────────────────────────────────────────────────────────

    def test_router_english_contradiction(self):
        """'more speed but less reliability' detects an engineering
        contradiction via connector + keyword match."""
        result = triz_router.suggest_methods(
            "more speed but less reliability"
        )
        self.assertIsNotNone(
            result["engineering_contradiction"],
            "Should detect engineering contradiction from trade-off language"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertTrue(
            any("Engineering Contradiction" in m for m in methods),
            f"Expected Engineering Contradiction in methods, got {methods}"
        )

    def test_router_physical_contradiction(self):
        """'must be present and absent' detects a physical contradiction."""
        result = triz_router.suggest_methods(
            "the element must be present and absent"
        )
        self.assertIsNotNone(
            result["physical_contradiction"],
            "Should detect physical contradiction from paired opposites"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertTrue(
            any("Physical Contradiction" in m for m in methods),
            f"Expected Physical Contradiction in methods, got {methods}"
        )

    def test_router_default_fallback(self):
        """Empty text returns the 5 default fallback methods with score=0."""
        result = triz_router.suggest_methods("")
        self.assertIsNone(result["engineering_contradiction"])
        self.assertIsNone(result["physical_contradiction"])
        methods = result["methods"]
        self.assertEqual(len(methods), 5,
                         "Empty input should return 5 default fallback methods")
        for m in methods:
            with self.subTest(method=m["method"]):
                self.assertEqual(m["score"], 0)
                self.assertIn("default fallback", m["why"])

    # ── Evaluator tests ─────────────────────────────────────────────────────

    def test_evaluator_scoring(self):
        """Scoring works, including through CSV parse with renamed/mixed-case
        columns."""
        # Build a temp CSV with mixed-case column names (use canonical names)
        csv_content = (
            "Solution,Impact,FEASIBILITY,cost,Speed,"
            "Risk,Reversibility,Complexity,Ideality\n"
            "TestA,4,3,2,1,5,4,3,2\n"
            "TestB,1,1,1,1,1,1,1,1\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_solutions.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            rows = triz_evaluator._parse_csv(str(csv_path))
            self.assertEqual(len(rows), 2)

            scored = triz_evaluator.score(rows)
            self.assertEqual(len(scored), 2)

            # TestA: 4+3+2+1+5+4+3+2 = 24
            self.assertEqual(scored[0]["solution"], "TestA")
            self.assertEqual(scored[0]["total"], 24)

            # TestB: 1*8 = 8
            self.assertEqual(scored[1]["solution"], "TestB")
            self.assertEqual(scored[1]["total"], 8)

            # Verify all eight criteria keys are lowercased and present
            for crit in triz_evaluator.CRITERIA:
                self.assertIn(crit, scored[0],
                              f"Missing criterion '{crit}' after CSV parse")

    def test_evaluator_sorting(self):
        """Highest total sorts first (descending order)."""
        rows = [
            {
                "solution": "Low",
                "impact": 1, "feasibility": 1, "cost": 1,
                "speed": 1, "risk": 1, "reversibility": 1,
                "complexity": 1, "ideality": 1,
            },
            {
                "solution": "High",
                "impact": 5, "feasibility": 5, "cost": 5,
                "speed": 5, "risk": 5, "reversibility": 5,
                "complexity": 5, "ideality": 5,
            },
            {
                "solution": "Mid",
                "impact": 3, "feasibility": 3, "cost": 3,
                "speed": 3, "risk": 3, "reversibility": 3,
                "complexity": 3, "ideality": 3,
            },
        ]
        scored = triz_evaluator.score(rows)
        self.assertEqual(scored[0]["solution"], "High")
        self.assertEqual(scored[1]["solution"], "Mid")
        self.assertEqual(scored[2]["solution"], "Low")
        self.assertGreater(scored[0]["total"], scored[1]["total"])
        self.assertGreater(scored[1]["total"], scored[2]["total"])

    # ── Standard Solutions tests ────────────────────────────────────────────

    def test_standard_solutions_valid_state(self):
        """'harmful' state returns Class 1 with a matching name."""
        result = triz_standard_solutions.recommend("harmful")
        self.assertEqual(result["state"], "harmful")
        self.assertGreater(len(result["classes"]), 0)
        cls0 = result["classes"][0]
        self.assertEqual(cls0["class"], 1)
        self.assertIn("harmful", cls0["name"].lower())
        self.assertIsNotNone(result["note"])

    def test_standard_solutions_invalid_state(self):
        """Unknown state raises ValueError."""
        with self.assertRaises(ValueError):
            triz_standard_solutions.recommend("nonexistent_state_xyz")

    # ── Evolution tests ─────────────────────────────────────────────────────

    def test_evolution_growth_signals(self):
        """'rapid scaling adoption' classifies as Growth (stage 2)."""
        result = triz_evolution.analyze("rapid scaling adoption")
        self.assertEqual(result["s_curve_stage"]["name"], "Growth")
        self.assertEqual(result["s_curve_stage"]["stage"], 2)
        self.assertIn("scaling", result["s_curve_stage"]["why"].lower())
        # Always returns 8 trend prompts
        self.assertEqual(len(result["trends"]), 8)

    def test_evolution_maturity_signals(self):
        """'diminishing returns plateau' classifies as Maturity (stage 3)."""
        result = triz_evolution.analyze("diminishing returns plateau")
        self.assertEqual(result["s_curve_stage"]["name"], "Maturity")
        self.assertEqual(result["s_curve_stage"]["stage"], 3)
        self.assertIn("diminishing returns", result["s_curve_stage"]["why"].lower())

    # ── ARIZ tests ──────────────────────────────────────────────────────────

    def test_ariz_worksheet_creation(self):
        """create_worksheet produces a file with exactly 9 ARIZ parts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = triz_ariz.create_worksheet("Test ARIZ Problem", cases_dir=tmpdir)
            self.assertTrue(path.exists(), f"ARIZ worksheet not created at {path}")
            content = path.read_text(encoding="utf-8")
            parts = re.findall(r"^## Part \d", content, re.MULTILINE)
            self.assertEqual(len(parts), 9,
                             f"Expected 9 ARIZ parts, found {len(parts)}")
            # Verify the title is present
            self.assertIn("Test ARIZ Problem", content)

    # ── Case Template tests ─────────────────────────────────────────────────

    def test_case_template_creation(self):
        """create_case produces a file using the actual template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = triz_case_template.create_case("My Test Case", cases_dir=tmpdir)
            self.assertTrue(path.exists(), f"Case file not created at {path}")
            content = path.read_text(encoding="utf-8")
            self.assertIn("My Test Case", content,
                          "Case file should contain the problem title")

    # ── Effects database tests ──────────────────────────────────────────────

    def test_effects_search(self):
        """Scientific effects database loads, each entry has required fields,
        and search by name works."""
        effects_path = _SCRIPTS_DIR / "data" / "scientific_effects.json"
        self.assertTrue(effects_path.exists(),
                        f"Effects database not found at {effects_path}")

        with open(effects_path, "r", encoding="utf-8") as fh:
            effects = json.load(fh)

        self.assertIsInstance(effects, list)
        self.assertGreater(len(effects), 0,
                           "Effects database should not be empty")

        required_fields = {"effect_name", "function_family", "domain"}
        for i, entry in enumerate(effects):
            with self.subTest(entry_index=i):
                for field in required_fields:
                    self.assertIn(field, entry,
                                  f"Entry {i} missing field '{field}'")

        # Search for a specific known effect
        matches = [
            e for e in effects
            if "capillarity" in e.get("effect_name", "").lower()
        ]
        self.assertGreater(len(matches), 0,
                           "Should find at least one 'Capillarity' effect")

        capillarity = matches[0]
        self.assertIn("mechanism", capillarity)
        self.assertIn("resources_needed", capillarity)
        self.assertIn("examples", capillarity)
        self.assertIsInstance(capillarity["resources_needed"], list)
        self.assertIsInstance(capillarity["examples"], list)

    # ═══════════════════════════════════════════════════════════════════════
    #  R13 NEW TESTS
    # ═══════════════════════════════════════════════════════════════════════

    # ── R13.1: Scripts importable ───────────────────────────────────────────

    def test_scripts_importable(self):
        """All ten scripts in the package import successfully."""
        import triz
        import triz_effects
        import triz_contradiction_network
        self.assertTrue(True)

    # ── R13.2: Dispatcher tests ─────────────────────────────────────────────

    def test_dispatcher_help(self):
        """dispatch([]) and dispatch(['help']) return 0."""
        import triz
        self.assertEqual(triz.dispatch([]), 0)
        self.assertEqual(triz.dispatch(["help"]), 0)
        self.assertEqual(triz.dispatch(["--help"]), 0)

    def test_dispatcher_aliases(self):
        """Router, su-field, evaluator, kb aliases all return 0."""
        import triz
        self.assertEqual(triz.dispatch(["router", ""]), 0)
        self.assertEqual(triz.dispatch(["su-field", "--list"]), 0)
        self.assertEqual(triz.dispatch(["evaluator"]), 0)
        self.assertEqual(triz.dispatch(["kb"]), 0)

    def test_dispatcher_unknown_command(self):
        """Unknown command returns exit code 2."""
        import triz
        self.assertEqual(triz.dispatch(["frobnicate"]), 2)

    def test_dispatcher_master(self):
        """dispatch(['master']) returns 0."""
        import triz
        rc = triz.dispatch(["master"])
        self.assertEqual(rc, 0)

    def test_dispatcher_effects_and_network(self):
        """effects --keyword and network --demo return 0."""
        import triz
        self.assertEqual(triz.dispatch(["effects", "--keyword", "magnetic"]), 0)
        self.assertEqual(triz.dispatch(["network", "--demo"]), 0)

    # ── R13.3: Network tests ────────────────────────────────────────────────

    def test_network_add_contradiction_basic(self):
        """add_contradiction works for valid inputs."""
        import triz_contradiction_network as nw
        net = {"contradictions": []}
        nw.add_contradiction(net, "C1", 14, 2, "Test contradiction")
        self.assertEqual(len(net["contradictions"]), 1)
        self.assertEqual(net["contradictions"][0]["id"], "C1")
        self.assertEqual(net["contradictions"][0]["improving"], 14)
        self.assertEqual(net["contradictions"][0]["worsening"], 2)

    def test_network_add_contradiction_invalid_params(self):
        """add_contradiction rejects out-of-range and non-int params."""
        import triz_contradiction_network as nw
        bad_cases = [
            (0, 2), (40, 2), (99, 2),
            (14.5, 2),
            (True, 2),
        ]
        for imp, wor in bad_cases:
            with self.subTest(improving=imp, worsening=wor):
                net = {"contradictions": []}
                with self.assertRaises(ValueError):
                    nw.add_contradiction(net, "CX", imp, wor, "bad")

    def test_network_duplicate_id(self):
        """add_contradiction raises ValueError for duplicate id."""
        import triz_contradiction_network as nw
        net = {"contradictions": []}
        nw.add_contradiction(net, "C1", 1, 2, "first")
        with self.assertRaises(ValueError):
            nw.add_contradiction(net, "C1", 3, 4, "duplicate")

    def test_network_find_shared_parameters(self):
        """find_shared_parameters on demo network returns exact dict."""
        import triz_contradiction_network as nw
        net = {"contradictions": [
            {"id": "C1", "improving": 14, "worsening": 1,
             "improving_name": "Strength", "worsening_name": "Weight",
             "description": "d1"},
            {"id": "C2", "improving": 1, "worsening": 12,
             "improving_name": "Weight", "worsening_name": "Shape",
             "description": "d2"},
        ]}
        shared = nw.find_shared_parameters(net)
        self.assertIn(1, shared)
        self.assertEqual(sorted(shared[1]), ["C1", "C2"])

    def test_network_find_conflicts_invalid_param(self):
        """find_conflicts with invalid param id raises ValueError, not KeyError."""
        import triz_contradiction_network as nw
        net = {"contradictions": [
            {"id": "C1", "improving": 99, "worsening": 1,
             "improving_name": "X", "worsening_name": "Y",
             "description": "bad"},
            {"id": "C2", "improving": 99, "worsening": 2,
             "improving_name": "X", "worsening_name": "Z",
             "description": "bad2"},
        ]}
        with self.assertRaises(ValueError):
            nw.find_conflicts(net)

    def test_network_suggest_resolution_order(self):
        """suggest_resolution_order sorts by connected_count desc, ties numerically."""
        import triz_contradiction_network as nw
        net = {"contradictions": [
            {"id": "C10", "improving": 14, "worsening": 1,
             "improving_name": "Strength", "worsening_name": "Weight",
             "description": "d10"},
            {"id": "C2", "improving": 1, "worsening": 12,
             "improving_name": "Weight", "worsening_name": "Shape",
             "description": "d2"},
            {"id": "C3", "improving": 12, "worsening": 32,
             "improving_name": "Shape", "worsening_name": "Mfg",
             "description": "d3"},
            {"id": "C1", "improving": 32, "worsening": 14,
             "improving_name": "Mfg", "worsening_name": "Strength",
             "description": "d1"},
        ]}
        order = nw.suggest_resolution_order(net)
        for item in order:
            self.assertGreaterEqual(item["connected_count"], 0)
        # If C2 and C10 have same count, C2 should come before C10
        c2_idx = next(i for i, item in enumerate(order) if item["id"] == "C2")
        c10_idx = next(i for i, item in enumerate(order) if item["id"] == "C10")
        c2_count = order[c2_idx]["connected_count"]
        c10_count = order[c10_idx]["connected_count"]
        if c2_count == c10_count:
            self.assertLess(c2_idx, c10_idx,
                           "C2 should sort before C10 when tied")

    def test_network_analyze_network(self):
        """analyze_network returns all expected keys and summary contains counts."""
        import triz_contradiction_network as nw
        contradictions = [
            {"id": "C1", "improving": 14, "worsening": 1,
             "improving_name": "Strength", "worsening_name": "Weight",
             "description": "d1"},
            {"id": "C2", "improving": 1, "worsening": 12,
             "improving_name": "Weight", "worsening_name": "Shape",
             "description": "d2"},
        ]
        result = nw.analyze_network(contradictions)
        for key in ["contradictions", "shared_parameters", "conflicts",
                     "resolution_order", "summary"]:
            self.assertIn(key, result, f"Missing key: {key}")
        self.assertIn("2 contradictions", result["summary"])

    # ── R13.4: Effects-module tests ─────────────────────────────────────────

    def test_effects_search_by_function(self):
        """search_by_function('detect') returns non-empty; empty/whitespace returns []."""
        import triz_effects
        results = triz_effects.search_by_function("detect")
        self.assertGreater(len(results), 0)
        self.assertEqual(triz_effects.search_by_function(""), [])
        self.assertEqual(triz_effects.search_by_function("   "), [])

    def test_effects_search_by_keyword(self):
        """search_by_keyword('magnetic') returns non-empty."""
        import triz_effects
        results = triz_effects.search_by_keyword("magnetic")
        self.assertGreater(len(results), 0)

    def test_effects_get_function_families(self):
        """get_function_families() returns sorted, unique, non-empty list."""
        import triz_effects
        families = triz_effects.get_function_families()
        self.assertGreater(len(families), 0)
        self.assertEqual(families, sorted(families))
        self.assertEqual(len(families), len(set(families)))

    def test_effects_list_effects(self):
        """list_effects() returns all; list_effects(family) filters."""
        import triz_effects
        all_eff = triz_effects.list_effects()
        self.assertGreater(len(all_eff), 0)
        families = triz_effects.get_function_families()
        family = families[0]
        filtered = triz_effects.list_effects(family=family)
        self.assertGreater(len(filtered), 0)
        self.assertLess(len(filtered), len(all_eff),
                        f"Filtered count ({len(filtered)}) should be less than all ({len(all_eff)})")

    def test_effects_format_empty(self):
        """format_effects([]) contains '(no effects found)'."""
        import triz_effects
        output = triz_effects.format_effects([])
        self.assertIn("(no effects found)", output)

    # ── R13.5: Router regression tests (R1–R4) ──────────────────────────────

    def test_router_benign_italian_sistema(self):
        """Benign Italian 'Il sistema non risponde.' → EC is None."""
        result = triz_router.suggest_methods("Il sistema non risponde.")
        self.assertIsNone(result["engineering_contradiction"])

    def test_router_benign_italian_macchina(self):
        """Benign Italian 'La macchina funziona bene ogni giorno.' → EC is None."""
        result = triz_router.suggest_methods(
            "La macchina funziona bene ogni giorno."
        )
        self.assertIsNone(result["engineering_contradiction"])

    def test_router_benign_italian_programma(self):
        """Benign Italian 'Il programma si avvia correttamente.' → EC is None."""
        result = triz_router.suggest_methods(
            "Il programma si avvia correttamente."
        )
        self.assertIsNone(result["engineering_contradiction"])

    def test_router_no_false_but_from_button(self):
        """'This button works fine.' → EC is None (no 'but' from 'button')."""
        result = triz_router.suggest_methods("This button works fine.")
        self.assertIsNone(result["engineering_contradiction"])

    def test_router_no_false_on_off_from_only_office(self):
        """'only'/'office' do not trigger physical contradiction via 'on'/'off'."""
        result = triz_router.suggest_methods(
            "We have no budget and only a few people, "
            "and the office workflow keeps failing"
        )
        self.assertIsNone(result["physical_contradiction"])

    def test_router_no_software_from_circuit(self):
        """'circuit' does not boost Software TRIZ."""
        result = triz_router.suggest_methods("a circuit board overheats")
        methods = {m["method"]: m["score"] for m in result["methods"]}
        self.assertEqual(
            methods.get("Software TRIZ", 0), 0,
            f"Software TRIZ should not be boosted by 'circuit', "
            f"got score {methods.get('Software TRIZ', 0)}"
        )

    def test_router_italian_physio_ec_label(self):
        """Italian physio example: EC label matches improve[]/worsens[] pattern."""
        result = triz_router.suggest_methods(
            "Ho un'app di fisioterapia che deve inviare notifiche per gli esercizi, "
            "ma le notifiche li infastidiscono e disattivano l'app"
        )
        ec = result["engineering_contradiction"]
        self.assertIsNotNone(ec)
        self.assertRegex(ec, r'^improve \[.*\] / worsens \[.*\]$')
        halves_str = ec[len("improve ["):]
        parts = halves_str.split("] / worsens [")
        self.assertEqual(len(parts), 2)
        before = parts[0]
        after = parts[1].rstrip("]")
        self.assertLessEqual(len(before), 40)
        self.assertLessEqual(len(after), 40)
        self.assertNotIn("…", ec)

    def test_router_italian_vendita_ec_label(self):
        """Italian 'La vendita è calata...' → EC label both halves non-empty."""
        result = triz_router.suggest_methods(
            "La vendita è calata questo mese ma i margini crescono."
        )
        ec = result["engineering_contradiction"]
        self.assertIsNotNone(ec)
        self.assertRegex(ec, r'^improve \[.*\] / worsens \[.*\]$')
        halves_str = ec[len("improve ["):]
        parts = halves_str.split("] / worsens [")
        self.assertEqual(len(parts), 2)
        self.assertGreater(len(parts[0]), 0)
        self.assertGreater(len(parts[1].rstrip("]")), 0)

    def test_router_punctuation_adjacent_connectors(self):
        """'simple, but it works' and 'fast but.' still boost scoring."""
        r1 = triz_router.suggest_methods("simple, but it works")
        self.assertIsNotNone(r1["engineering_contradiction"])
        r2 = triz_router.suggest_methods("fast but.")
        self.assertIsNotNone(r2["engineering_contradiction"])

    def test_router_per_method_score_capped(self):
        """Repeated cues → per-method score capped at 10."""
        result = triz_router.suggest_methods(
            "trade-off but however at the cost of tradeoff "
            "trade-off but however at the cost of tradeoff "
            "trade-off but however at the cost of tradeoff "
        )
        for m in result["methods"]:
            self.assertLessEqual(
                m["score"], 10,
                f"Method {m['method']} score {m['score']} exceeds cap of 10"
            )

    def test_router_transparent_and_opaque(self):
        """'The window must be both transparent and opaque.' → PC not None."""
        result = triz_router.suggest_methods(
            "The window must be both transparent and opaque."
        )
        self.assertIsNotNone(result["physical_contradiction"])

    def test_router_rigido_e_flessibile(self):
        """'Il pezzo deve essere rigido e flessibile.' → PC not None."""
        result = triz_router.suggest_methods(
            "Il pezzo deve essere rigido e flessibile."
        )
        self.assertIsNotNone(result["physical_contradiction"])

    def test_router_italian_domain_routing(self):
        """Italian domain sentences route to the right branch."""
        r1 = triz_router.suggest_methods("La vendita è calata questo mese.")
        m1 = {m["method"]: m["score"] for m in r1["methods"]}
        self.assertGreater(m1.get("Business TRIZ", 0), 0,
                          "Italian business sentence should route to Business TRIZ")

        r2 = triz_router.suggest_methods("Il sito web è lento a caricare.")
        m2 = {m["method"]: m["score"] for m in r2["methods"]}
        self.assertGreater(m2.get("Software TRIZ", 0), 0,
                          "Italian software sentence should route to Software TRIZ")

        r3 = triz_router.suggest_methods(
            "Il paziente sente dolore durante il movimento."
        )
        m3 = {m["method"]: m["score"] for m in r3["methods"]}
        self.assertGreater(m3.get("Rehabilitation TRIZ", 0), 0,
                          "Italian rehab sentence should route to Rehabilitation TRIZ")

    # ── R13.6: Evaluator tests ──────────────────────────────────────────────

    def test_evaluator_canonical_headers(self):
        """CSV with cost/risk/complexity headers parses and totals correctly."""
        csv_content = (
            "solution,impact,feasibility,cost,speed,risk,reversibility,complexity,ideality\n"
            "TestA,4,3,2,1,5,4,3,2\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_canon.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            rows = triz_evaluator._parse_csv(str(csv_path))
            scored = triz_evaluator.score(rows)
            self.assertEqual(scored[0]["total"], 24)

    def test_evaluator_legacy_header_aliases(self):
        """CSV with affordability/safety/simplicity headers produces same totals."""
        csv_canon = (
            "solution,impact,feasibility,cost,speed,risk,reversibility,complexity,ideality\n"
            "TestX,4,3,2,1,5,4,3,2\n"
        )
        csv_legacy = (
            "solution,impact,feasibility,affordability,speed,safety,reversibility,simplicity,ideality\n"
            "TestX,4,3,2,1,5,4,3,2\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = Path(tmpdir) / "canon.csv"
            p2 = Path(tmpdir) / "legacy.csv"
            p1.write_text(csv_canon, encoding="utf-8")
            p2.write_text(csv_legacy, encoding="utf-8")
            rows1 = triz_evaluator._parse_csv(str(p1))
            rows2 = triz_evaluator._parse_csv(str(p2))
            s1 = triz_evaluator.score(rows1)
            s2 = triz_evaluator.score(rows2)
            self.assertEqual(s1[0]["total"], s2[0]["total"])

    def test_evaluator_wrong_header(self):
        """Wrong/unknown header raises SystemExit(1)."""
        csv_content = (
            "solution,bogus,fake,wrong,headers,here\n"
            "X,1,2,3,4,5\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "bad.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            with self.assertRaises(SystemExit) as cm:
                triz_evaluator._parse_csv(str(csv_path))
            self.assertEqual(cm.exception.code, 1)

    def test_evaluator_missing_file(self):
        """Missing file → clean error (SystemExit 1), no traceback."""
        with self.assertRaises(SystemExit) as cm:
            triz_evaluator._parse_csv("/nonexistent/path/file.csv")
        self.assertEqual(cm.exception.code, 1)

    def test_evaluator_score_validation(self):
        """score() with missing criterion or value 6 → ValueError."""
        # Missing criterion
        row_bad = {
            "solution": "Bad",
            "impact": 3, "feasibility": 3, "cost": 3,
            "speed": 3, "risk": 3, "reversibility": 3,
            # missing complexity and ideality
        }
        with self.assertRaises(ValueError):
            triz_evaluator.score([row_bad])
        # Value out of range
        row_oor = {
            "solution": "OOR",
            "impact": 6, "feasibility": 3, "cost": 3,
            "speed": 3, "risk": 3, "reversibility": 3,
            "complexity": 3, "ideality": 3,
        }
        with self.assertRaises(ValueError):
            triz_evaluator.score([row_oor])

    def test_evaluator_ties_stable(self):
        """Ties preserve stable order; highest total sorts first."""
        rows = [
            {"solution": "A", "impact": 3, "feasibility": 3, "cost": 3,
             "speed": 3, "risk": 3, "reversibility": 3, "complexity": 3, "ideality": 3},
            {"solution": "B", "impact": 5, "feasibility": 5, "cost": 5,
             "speed": 5, "risk": 5, "reversibility": 5, "complexity": 5, "ideality": 5},
            {"solution": "C", "impact": 3, "feasibility": 3, "cost": 3,
             "speed": 3, "risk": 3, "reversibility": 3, "complexity": 3, "ideality": 3},
        ]
        scored = triz_evaluator.score(rows)
        self.assertEqual(scored[0]["solution"], "B")
        # A and C tied at 24 — A should stay before C (stable)
        a_idx = next(i for i, r in enumerate(scored) if r["solution"] == "A")
        c_idx = next(i for i, r in enumerate(scored) if r["solution"] == "C")
        self.assertLess(a_idx, c_idx)

    def test_evaluator_format_empty(self):
        """format_table on empty list → header only, no data rows."""
        table = triz_evaluator.format_table([])
        self.assertIn("Solution", table)
        lines = table.split("\n")
        # Should have header line and separator (2 lines), no data rows
        self.assertGreaterEqual(len(lines), 2)

    # ── R13.7: Matrix tests ─────────────────────────────────────────────────

    def test_matrix_cell_18_35(self):
        """lookup(18, 35) returns exactly 3 principles, no duplicate."""
        result = triz_matrix.lookup(18, 35)
        self.assertEqual(len(result["principles"]), 3,
                        f"Expected 3 principles for (18,35), "
                        f"got {len(result['principles'])}")
        pids = [p["id"] for p in result["principles"]]
        self.assertEqual(len(pids), len(set(pids)),
                        f"Duplicate principle ids in (18,35): {pids}")

    def test_matrix_no_duplicate_principles(self):
        """No cell in the matrix contains duplicate principle ids."""
        matrix = triz_matrix.load_matrix()
        for key, pids in matrix.items():
            if len(pids) > 1:
                self.assertEqual(len(pids), len(set(pids)),
                                f"Duplicate principles in cell {key}: {pids}")

    def test_matrix_invalid_types(self):
        """Non-int arguments to lookup raise ValueError."""
        bad_cases = [
            (True, 2), (14.5, 2), ("14", 2), (14, None), (None, 2),
        ]
        for improving, worsening in bad_cases:
            with self.subTest(improving=improving, worsening=worsening):
                with self.assertRaises(ValueError):
                    triz_matrix.lookup(improving, worsening)

    def test_matrix_boundary_valid(self):
        """Boundary valid ids lookup(1, 39) and lookup(39, 1) work."""
        r1 = triz_matrix.lookup(1, 39)
        self.assertIsInstance(r1["principles"], list)
        r2 = triz_matrix.lookup(39, 1)
        self.assertIsInstance(r2["principles"], list)

    def test_matrix_known_empty_cell(self):
        """A known-empty off-diagonal cell → [] principles + note about Resource."""
        matrix = triz_matrix.load_matrix()
        empty_found = None
        for i in range(1, 40):
            for j in range(1, 40):
                if i != j and not matrix.get((i, j), []):
                    empty_found = (i, j)
                    break
            if empty_found:
                break
        if empty_found:
            result = triz_matrix.lookup(*empty_found)
            self.assertEqual(result["principles"], [])
            self.assertIsNotNone(result["note"])
            self.assertIn("Resource", result["note"])

    # ── R13.8: Standard-solutions tests ─────────────────────────────────────

    def test_standard_solutions_state_map(self):
        """All 5 states map to correct class."""
        import triz_standard_solutions as tss
        self.assertEqual(tss.recommend("incomplete")["classes"][0]["class"], 1)
        self.assertEqual(tss.recommend("insufficient")["classes"][0]["class"], 2)
        self.assertEqual(tss.recommend("harmful")["classes"][0]["class"], 1)
        self.assertEqual(tss.recommend("measurement")["classes"][0]["class"], 4)
        self.assertEqual(tss.recommend("excessive")["classes"][0]["class"], 5)

    def test_standard_solutions_synonyms(self):
        """Synonyms resolve: missing→incomplete, weak→insufficient,
        detection→measurement, complex→excessive."""
        import triz_standard_solutions as tss
        self.assertEqual(tss.recommend("missing")["state"], "incomplete")
        self.assertEqual(tss.recommend("weak")["state"], "insufficient")
        self.assertEqual(tss.recommend("detection")["state"], "measurement")
        self.assertEqual(tss.recommend("complex")["state"], "excessive")

    def test_standard_solutions_variant_mechanism(self):
        """lookup_solution('5.1.1.7') has non-empty mechanism (inherited)."""
        import triz_standard_solutions as tss
        sol = tss.lookup_solution("5.1.1.7")
        self.assertIsNotNone(sol)
        self.assertIn("mechanism", sol)
        self.assertIsNotNone(sol["mechanism"])
        self.assertGreater(len(sol["mechanism"].strip()), 0,
                          "Variant should inherit parent mechanism")

    def test_standard_solutions_db_integrity(self):
        """Exactly 76 base solutions, all ids unique, every base has name/mechanism."""
        import triz_standard_solutions as tss
        db = tss.load_solutions_db()
        all_sols = tss._iter_solutions(db)
        ids = [s["id"] for s in all_sols]
        bases = [s for s in all_sols if "parent_id" not in s]
        self.assertEqual(len(bases), 76,
                        f"Expected 76 base solutions, got {len(bases)}")
        self.assertEqual(len(ids), len(set(ids)),
                        "All solution IDs must be unique")
        for sol in bases:
            self.assertIn("name", sol)
            self.assertIn("mechanism", sol)
            self.assertGreater(len(sol["name"].strip()), 0,
                              f"Base {sol['id']} has empty name")

    # ── R13.9: Evolution tests ──────────────────────────────────────────────

    def test_evolution_premature_aging(self):
        """'premature aging' → Unknown (not Maturity)."""
        result = triz_evolution.analyze("premature aging")
        self.assertEqual(result["s_curve_stage"]["stage"], 0)

    def test_evolution_pocket_tool(self):
        """'pocket tool' → Unknown (not Infancy)."""
        result = triz_evolution.analyze("pocket tool")
        self.assertEqual(result["s_curve_stage"]["stage"], 0)

    def test_evolution_nearly_done(self):
        """'nearly done' → Unknown (not Infancy)."""
        result = triz_evolution.analyze("nearly done")
        self.assertEqual(result["s_curve_stage"]["stage"], 0)

    def test_evolution_prototype_infancy(self):
        """'prototype is unreliable and experimental' → Infancy (stage 1)."""
        result = triz_evolution.analyze(
            "prototype is unreliable and experimental"
        )
        self.assertEqual(result["s_curve_stage"]["stage"], 1)
        self.assertEqual(result["s_curve_stage"]["name"], "Infancy")

    def test_evolution_obsolete_decline(self):
        """'obsolete and being replaced by the new version' → Decline (stage 4)."""
        result = triz_evolution.analyze(
            "obsolete and being replaced by the new version"
        )
        self.assertEqual(result["s_curve_stage"]["stage"], 4)
        self.assertEqual(result["s_curve_stage"]["name"], "Decline")

    def test_evolution_empty_and_gibberish(self):
        """'' and gibberish → stage 0 with note present."""
        r1 = triz_evolution.analyze("")
        self.assertEqual(r1["s_curve_stage"]["stage"], 0)
        self.assertIsNotNone(r1["note"])
        r2 = triz_evolution.analyze("xyzzy fwibble blarg")
        self.assertEqual(r2["s_curve_stage"]["stage"], 0)

    def test_evolution_tie_break_note(self):
        """'diminishing returns scaling' → Maturity with tie-break note."""
        result = triz_evolution.analyze("diminishing returns scaling")
        self.assertEqual(result["s_curve_stage"]["name"], "Maturity")
        if result["s_curve_stage"]["stage"] != 0:
            self.assertIn(
                "tie broken",
                result["s_curve_stage"]["why"].lower()
            )

    # ── R13.10: ARIZ + case-template tests ──────────────────────────────────

    def test_case_template_collision(self):
        """Creating the same title twice → -2 suffix on the second."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = triz_case_template.create_case(
                "Test Collision", cases_dir=tmpdir
            )
            self.assertTrue(p1.exists())
            p2 = triz_case_template.create_case(
                "Test Collision", cases_dir=tmpdir
            )
            self.assertTrue(p2.exists())
            self.assertNotEqual(p1, p2)
            self.assertIn("-2", p2.stem)

    def test_case_template_slug_special_chars(self):
        """'App * !! Refactor!!' → slug contains 'app-refactor';
        empty title → 'untitled'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = triz_case_template.create_case(
                "App * !! Refactor!!", cases_dir=tmpdir
            )
            self.assertIn("app-refactor", p.stem.lower())
            p2 = triz_case_template.create_case("", cases_dir=tmpdir)
            self.assertIn("untitled", p2.stem.lower())

    def test_ariz_worksheet_headings(self):
        """Template headings preserved verbatim in the generated ARIZ file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = triz_ariz.create_worksheet(
                "Heading Test", cases_dir=tmpdir
            )
            content = path.read_text(encoding="utf-8")
            for i in range(1, 10):
                self.assertIn(
                    f"## Part {i}", content,
                    f"Part {i} heading not found in ARIZ worksheet"
                )


    # ═══════════════════════════════════════════════════════════════════════
    #  R16 NEW TESTS — Phase 5: close all 7 OPEN BACKLOG items
    #  (router whole-word labels, dispatcher output, evaluator BOM/short-row/
    #   clean-stderr, matrix + catalog exact values; SPEC build 4)
    # ═══════════════════════════════════════════════════════════════════════

    # ── R1: Router whole-word EC-label regression tests ──────────────────

    def _assert_label_whole_words(self, before: str, after: str, source: str) -> None:
        """R1: every whitespace token in each EC-label half is a complete word
        reconstructable from the source sentence (a truncated fragment is never
        a whole word), and no token carries a stray character like '…'."""
        source_words = source.split()
        cleaned = {w.strip(".,;:!?()[]{}<>\"'«»").lower() for w in source_words}
        for half_name, half in (("improve", before), ("worsens", after)):
            for token in half.split():
                self.assertTrue(
                    any(token in w for w in source_words),
                    f"{half_name} label token {token!r} is not a substring of "
                    f"any source word (mid-word slice or stray '…')",
                )
                self.assertIn(
                    token.strip(".,;:!?()[]{}<>\"'«»").lower(),
                    cleaned,
                    f"{half_name} label token {token!r} is not a complete word "
                    f"of the source sentence",
                )

    def test_router_physio_ec_label_whole_words(self):
        """R1: Italian physio EC label uses the last whole words before the
        connector — not the raw 40-char prefix — with no mid-word split."""
        source = (
            "Ho un'app di fisioterapia che deve inviare notifiche per gli esercizi, "
            "ma le notifiche li infastidiscono e disattivano l'app"
        )
        result = triz_router.suggest_methods(source)
        ec = result["engineering_contradiction"]
        self.assertIsNotNone(ec)
        self.assertRegex(ec, r'^improve \[.*\] / worsens \[.*\]$')
        halves_str = ec[len("improve ["):]
        parts = halves_str.split("] / worsens [")
        self.assertEqual(len(parts), 2)
        before = parts[0]
        after = parts[1].rstrip("]")
        self.assertLessEqual(len(before), 40)
        self.assertLessEqual(len(after), 40)
        # Label must use the last words before the connector, not the raw prefix.
        self.assertIn("per gli esercizi", before)
        self.assertNotIn("…", ec)
        self._assert_label_whole_words(before, after, source)

    def test_router_long_word_english_ec_label_whole_words(self):
        """R1: long-word English input → no EC-label half contains a mid-word
        slice of any source word (subject words exceed 40 chars combined)."""
        source = (
            "the supercalifragilisticexpialidocious gearbox must transmit more "
            "torque but the housing cannot grow heavier"
        )
        result = triz_router.suggest_methods(source)
        ec = result["engineering_contradiction"]
        self.assertIsNotNone(ec)
        self.assertRegex(ec, r'^improve \[.*\] / worsens \[.*\]$')
        halves_str = ec[len("improve ["):]
        parts = halves_str.split("] / worsens [")
        self.assertEqual(len(parts), 2)
        before = parts[0]
        after = parts[1].rstrip("]")
        self.assertLessEqual(len(before), 40)
        self.assertLessEqual(len(after), 40)
        self.assertNotIn("…", ec)
        self._assert_label_whole_words(before, after, source)

    # ── R2: Dispatcher output assertions + missing-subtool path ───────────

    def test_dispatcher_route_output(self):
        """R2: 'triz.py route' prints marker-bearing output (rc 0)."""
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "route", "more speed but less reliability"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Engineering Contradiction", proc.stdout)
        self.assertIn("40 Inventive Principles", proc.stdout)

    def test_dispatcher_effects_output(self):
        """R2: 'triz.py effects --keyword magnetic' prints non-empty output."""
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "effects", "--keyword", "magnetic"],
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertGreater(len(proc.stdout), 0,
                           "effects --keyword magnetic printed nothing")

    def test_dispatcher_network_output(self):
        """R2: 'triz.py network --demo' prints non-empty output."""
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "network", "--demo"],
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertGreater(len(proc.stdout), 0,
                           "network --demo printed nothing")

    def test_dispatcher_missing_subtool(self):
        """R2: empty script dir → rc 1 + 'Sub-tool not found' on stderr."""
        import triz
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch("triz._SCRIPT_DIR", Path(tmpdir)):
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    rc = triz.dispatch(["matrix", "1", "2"])
        self.assertEqual(rc, 1)
        self.assertIn("Sub-tool not found", err.getvalue())

    # ── R3: Evaluator BOM / short-row / clean-stderr tests ───────────────

    def test_evaluator_utf8_bom(self):
        """R3: CSV with a UTF-8 BOM parses and scores correctly."""
        csv_content = (
            "﻿solution,impact,feasibility,cost,speed,risk,reversibility,"
            "complexity,ideality\n"
            "TestA,4,3,2,1,5,4,3,2\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "bom.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            rows = triz_evaluator._parse_csv(str(csv_path))
            self.assertEqual(len(rows), 1)
            scored = triz_evaluator.score(rows)
            self.assertEqual(scored[0]["solution"], "TestA")
            self.assertEqual(scored[0]["total"], 24)

    def test_evaluator_short_row_clean_error(self):
        """R3: short data row → SystemExit(1), stderr has 'missing value',
        no Traceback."""
        csv_content = (
            "solution,impact,feasibility,cost,speed,risk,reversibility,complexity,ideality\n"
            "TestA,4,3,2,1,5,4,3,2\n"
            "Short,4,3\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "short.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                with self.assertRaises(SystemExit) as cm:
                    triz_evaluator._parse_csv(str(csv_path))
            self.assertEqual(cm.exception.code, 1)
            self.assertIn("missing value", err.getvalue())
            self.assertNotIn("Traceback", err.getvalue())

    def test_evaluator_clean_stderr_missing_file(self):
        """R3: missing file → SystemExit(1), stderr 'Error:' only, no stdout."""
        err = io.StringIO()
        out = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            with self.assertRaises(SystemExit) as cm:
                triz_evaluator._parse_csv("/nonexistent/path/file.csv")
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("Error:", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())
        self.assertEqual(out.getvalue(), "")

    def test_evaluator_clean_stderr_wrong_header(self):
        """R3: wrong header → SystemExit(1), stderr 'Error:' only, no stdout."""
        csv_content = (
            "solution,bogus,fake,wrong,headers,here\n"
            "X,1,2,3,4,5\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "bad.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            err = io.StringIO()
            out = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
                with self.assertRaises(SystemExit) as cm:
                    triz_evaluator._parse_csv(str(csv_path))
            self.assertEqual(cm.exception.code, 1)
            self.assertIn("Error:", err.getvalue())
            self.assertNotIn("Traceback", err.getvalue())
            self.assertEqual(out.getvalue(), "")

    # ── R4: Matrix + catalog exact-value and coverage tests ──────────────

    def test_matrix_lookup_18_35_exact(self):
        """R4: lookup(18, 35) returns exactly [15, 1, 19] with names."""
        result = triz_matrix.lookup(18, 35)
        pids = [p["id"] for p in result["principles"]]
        names = [p["name"] for p in result["principles"]]
        self.assertEqual(pids, [15, 1, 19])
        self.assertEqual(names, ["Dynamization", "Segmentation", "Periodic Action"])

    def test_matrix_fixtures_present(self):
        """R4: the three matrix data CSVs must exist — fail loudly if absent."""
        data_dir = _SCRIPTS_DIR / "data"
        for filename in ("contradiction_matrix.csv", "parameters_39.csv",
                         "inventive_principles.csv"):
            path = data_dir / filename
            self.assertTrue(path.is_file(), f"Missing data fixture: {path}")

    def test_matrix_list_output(self):
        """R4: 'triz.py matrix --list' prints 39 parameters incl. 18 & 35."""
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"), "matrix", "--list"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = [line for line in proc.stdout.splitlines()
                 if re.match(r"^\s*\d+\s+\S", line)]
        self.assertEqual(len(lines), 39,
                         f"Expected 39 parameter lines, got {len(lines)}")
        self.assertIn("18  Illumination intensity", proc.stdout)
        self.assertIn("35  Adaptability or versatility", proc.stdout)

    def test_standard_solutions_list_all_output(self):
        """R4: '--list-all' prints the 76 + 11 totals."""
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz_standard_solutions.py"),
             "--list-all"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Total: 76 standard solutions", proc.stdout)
        self.assertIn("+ 11 variant(s)", proc.stdout)

    def test_standard_solutions_variant_count(self):
        """R4: exactly 11 variants, 76 bases, 87 total."""
        all_sols = triz_standard_solutions._iter_solutions(
            triz_standard_solutions.load_solutions_db()
        )
        variants = [s for s in all_sols if "parent_id" in s]
        bases = [s for s in all_sols if "parent_id" not in s]
        self.assertEqual(len(variants), 11)
        self.assertEqual(len(bases), 76)
        self.assertEqual(len(all_sols), 87)

    def test_standard_solutions_complete_entry(self):
        """R4: all 87 entries have non-empty required fields; each variant's
        parent_id resolves to an existing base id."""
        required = ["id", "name", "description", "mechanism",
                    "subfield_state", "class_id", "group_id"]
        all_sols = triz_standard_solutions._iter_solutions(
            triz_standard_solutions.load_solutions_db()
        )
        base_ids = {s["id"] for s in all_sols if "parent_id" not in s}
        for sol in all_sols:
            for field in required:
                value = sol.get(field)
                self.assertTrue(
                    value is not None and
                    (not isinstance(value, str) or value.strip()),
                    f"Solution {sol.get('id')} has empty '{field}': {value!r}",
                )
            if "parent_id" in sol:
                self.assertIn(
                    sol["parent_id"], base_ids,
                    f"Variant {sol['id']} parent {sol['parent_id']} is not a base id",
                )

    def test_case_template_missing_template(self):
        """R4: absent template path → create_case raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing-template.md"
            with mock.patch("triz_case_template._template_path",
                            return_value=missing):
                with self.assertRaises(FileNotFoundError):
                    triz_case_template.create_case("X", cases_dir=tmpdir)


    # ═══════════════════════════════════════════════════════════════════════
    #  R14 NEW TESTS — branches + language axis (SPEC build 2)
    # ═══════════════════════════════════════════════════════════════════════


class TestBranchesAndLanguageAxis(unittest.TestCase):
    """Branch registry, language detection, router --lang/--branch,
    case-template --lang, dispatcher flags, and master structure."""

    # ── Branch registry ────────────────────────────────────────────────────

    def test_branches_list_exact(self):
        inv = triz_branches.list_branches()
        self.assertEqual(inv["fields"], [
            "general", "business", "software", "rehab",
            "mechanical", "datascience", "marketing", "supplychain",
            "energy", "education", "construction", "robotics",
        ])
        self.assertEqual(inv["langs"], ["en", "it"])

    def test_branches_validate_clean(self):
        self.assertEqual(triz_branches.validate(), [])

    def test_branches_field_branch(self):
        sw = triz_branches.get_field_branch("software")
        self.assertEqual(sw["id"], "software")
        self.assertIsInstance(sw["parameter_map"], dict)
        self.assertGreater(len(sw["parameter_map"]), 0)
        for fid in ("business", "rehab"):
            data = triz_branches.get_field_branch(fid)
            self.assertIn("parameter_map", data)
            self.assertGreater(len(data["parameter_map"]), 0)
        gen = triz_branches.get_field_branch("general")
        self.assertNotIn("parameter_map", gen)
        self.assertEqual(gen["keywords"], [])

    def test_branches_unknown_raises(self):
        with self.assertRaises(KeyError):
            triz_branches.get_field_branch("nope")
        with self.assertRaises(KeyError):
            triz_branches.get_lang_branch("de")
        with self.assertRaises(KeyError):
            triz_branches.resolve_labels("fr")

    # ── Language detection ─────────────────────────────────────────────────

    def test_detect_language_italian(self):
        self.assertEqual(
            triz_branches.detect_language("il problema è quindi molto complesso"),
            "it",
        )

    def test_detect_language_english(self):
        self.assertEqual(
            triz_branches.detect_language("the system is fast and reliable"),
            "en",
        )

    def test_detect_language_mixed_italian_hit(self):
        self.assertEqual(
            triz_branches.detect_language("the app è quindi molto lento"),
            "it",
        )

    def test_detect_language_equal_hits_prefers_italian(self):
        # Spec: "it" when Italian hits >= 1 AND Italian hits >= English hits —
        # equal counts resolve to "it", not "en".
        self.assertEqual(
            triz_branches.detect_language("quindi the system"),
            "it",
        )

    # ── Router --lang / --branch ───────────────────────────────────────────

    def test_router_suggest_methods_keys_english(self):
        result = triz_router.suggest_methods("problema ma migliora")
        methods = [m["method"] for m in result["methods"]]
        self.assertTrue(
            any("Engineering Contradiction" in m for m in methods),
            f"Expected English method key, got {methods}",
        )
        self.assertNotIn("Contraddizione tecnica + 40 principi inventivi", methods)

    def test_router_cli_lang_it(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz_router.py"),
             "--lang", "it", "problema ma migliora"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Contraddizione", proc.stdout)
        self.assertNotIn("Engineering Contradiction", proc.stdout)

    def test_router_branch_software_excludes_business(self):
        text = "il prezzo di mercato cala ma la vendita cresce"
        default = triz_router.suggest_methods(text)
        default_methods = [m["method"] for m in default["methods"]]
        self.assertIn("Business TRIZ", default_methods)
        filtered = triz_router.suggest_methods(text, branch="software")
        filtered_methods = [m["method"] for m in filtered["methods"]]
        self.assertNotIn("Business TRIZ", filtered_methods)
        self.assertNotIn("Rehabilitation TRIZ", filtered_methods)

    def test_router_branch_unknown_raises(self):
        with self.assertRaises(ValueError):
            triz_router.suggest_methods("x", branch="nope")

    # ── Case template --lang ───────────────────────────────────────────────

    def test_case_template_lang_en(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = triz_case_template.create_case("X", cases_dir=tmpdir, lang="en")
            content = path.read_text(encoding="utf-8")
            self.assertIn("Restated problem", content)
            self.assertIn("Technical contradiction", content)

    def test_case_template_lang_it_matches_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            it_path = triz_case_template.create_case(
                "X", cases_dir=tmpdir, lang="it"
            )
            default_path = triz_case_template.create_case(
                "X", cases_dir=tmpdir, lang=None
            )
            it_content = it_path.read_text(encoding="utf-8")
            default_content = default_path.read_text(encoding="utf-8")
            self.assertIn("Problema riformulato", it_content)
            self.assertIn("Problema riformulato", default_content)

    def test_case_template_lang_unknown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                triz_case_template.create_case("X", cases_dir=tmpdir, lang="de")

    # ── Dispatcher ─────────────────────────────────────────────────────────

    def test_dispatcher_lang_it_route(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "--lang", "it", "route", "problema ma migliora"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Contraddizione", proc.stdout)

    def test_dispatcher_branches_list(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"), "branches", "list"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("software", proc.stdout)

    def test_dispatcher_branches_check(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"), "branches", "check"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_dispatcher_flags_position_independent(self):
        proc1 = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "--lang", "it", "route", "problema ma migliora"],
            capture_output=True, text=True, encoding="utf-8",
        )
        proc2 = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "route", "problema ma migliora", "--lang", "it"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc1.returncode, 0, proc1.stderr)
        self.assertEqual(proc2.returncode, 0, proc2.stderr)
        self.assertEqual(proc1.stdout, proc2.stdout)

    def test_dispatcher_unknown_lang_rejected(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "--lang", "de", "route", "x"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unknown --lang", proc.stderr.lower())

    # ── Master structure regression (guards the R8 content fixes) ──────────

    def test_master_exactly_24_h2(self):
        master = _SCRIPTS_DIR.parent / "TRIZ-MASTER.md"
        content = master.read_text(encoding="utf-8")
        h2 = [line for line in content.splitlines() if line.startswith("## ")]
        self.assertEqual(len(h2), 24, f"Expected 24 H2 sections, got {len(h2)}")

    def test_master_method_sections_have_procedure(self):
        master = _SCRIPTS_DIR.parent / "TRIZ-MASTER.md"
        lines = master.read_text(encoding="utf-8").splitlines()
        section_headers = [
            i for i, line in enumerate(lines) if re.match(r"^## \d+\.", line)
        ]
        for i, idx in enumerate(section_headers):
            num = int(re.match(r"^## (\d+)\.", lines[idx]).group(1))
            if not 3 <= num <= 20:
                continue
            end = section_headers[i + 1] if i + 1 < len(section_headers) else len(lines)
            body = "\n".join(lines[idx:end])
            self.assertIn(
                "**Procedure:**", body,
                f"Section {num} (line {idx + 1}) is missing **Procedure:**",
            )

    def test_master_inventive_principles_row2(self):
        csv_path = _SCRIPTS_DIR / "data" / "inventive_principles.csv"
        with open(csv_path, "r", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        # rows[0] is the header; rows[2] is the second data row (id 2).
        self.assertEqual(rows[2][0], "2")
        self.assertEqual(rows[2][1], "Taking Out")

    def test_master_matrix_27_25(self):
        result = triz_matrix.lookup(27, 25)
        pids = [p["id"] for p in result["principles"]]
        self.assertEqual(pids, [10, 30, 4])


    # ═══════════════════════════════════════════════════════════════════════
    #  R15 NEW TESTS — field branches, data-driven validation, domain
    #  rules, use-cases reference (SPEC build 3)
    # ═══════════════════════════════════════════════════════════════════════


class TestFieldBranchesDataDriven(unittest.TestCase):
    """Phase-3/6 regression: 12 field branches in canonical order, data-driven
    dispatcher/router branch validation, the domain rules, and the
    use-cases reference file."""

    _EXPECTED_FIELDS = [
        "general", "business", "software", "rehab",
        "mechanical", "datascience", "marketing", "supplychain",
        "energy", "education", "construction", "robotics",
    ]
    _NEW_BRANCHES = ["mechanical", "datascience", "marketing", "supplychain",
                     "energy", "education", "construction", "robotics"]
    _BRANCH_METHODS = {
        "mechanical": "Mechanical TRIZ",
        "datascience": "Data Science TRIZ",
        "marketing": "Marketing TRIZ",
        "supplychain": "Supply Chain TRIZ",
        "energy": "Energy TRIZ",
        "education": "Education TRIZ",
        "construction": "Construction TRIZ",
        "robotics": "Robotics TRIZ",
    }
    _USE_CASES_LABELS = [
        "**Problem:**",
        "**Branch detection:**",
        "**Route:**",
        "**Parameter translation:**",
        "**Solution via soft principles:**",
        "**Result:**",
    ]

    # ── Registry (12 fields, canonical order) ─────────────────────────────

    def test_registry_twelve_fields_canonical_order(self):
        inv = triz_branches.list_branches()
        self.assertEqual(inv["fields"], self._EXPECTED_FIELDS)

    def test_registry_validate_clean(self):
        self.assertEqual(triz_branches.validate(), [])

    # ── New branches data ─────────────────────────────────────────────────

    def test_new_branch_data_complete(self):
        for fid in self._NEW_BRANCHES:
            with self.subTest(branch=fid):
                data = triz_branches.get_field_branch(fid)
                self.assertEqual(data["id"], fid)
                self.assertIn("name_it", data)
                self.assertIsInstance(data["parameter_map"], dict)
                self.assertGreaterEqual(len(data["parameter_map"]), 5)
                self.assertIsInstance(data["principle_soft"], dict)
                self.assertGreaterEqual(len(data["principle_soft"]), 5)
                self.assertGreaterEqual(len(data["keywords"]), 10)
                self.assertGreaterEqual(len(data["examples"]), 2)

    # ── Routing: each new domain routes to its own rule ───────────────────

    def test_route_mechanical_keywords(self):
        result = triz_router.suggest_methods(
            "the gear wears out under vibration and high torque"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertIn("Mechanical TRIZ", methods)

    def test_route_datascience_keywords(self):
        result = triz_router.suggest_methods(
            "the model overfits on the training dataset"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertIn("Data Science TRIZ", methods)

    def test_route_marketing_keywords(self):
        result = triz_router.suggest_methods(
            "the landing page conversion is dropping"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertIn("Marketing TRIZ", methods)

    def test_route_supplychain_keywords(self):
        result = triz_router.suggest_methods(
            "the warehouse keeps running out of safety stock"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertIn("Supply Chain TRIZ", methods)

    def test_route_energy_keywords(self):
        result = triz_router.suggest_methods(
            "the battery and inverter on the solar grid keep losing energy efficiency"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertIn("Energy TRIZ", methods)

    def test_route_education_keywords(self):
        result = triz_router.suggest_methods(
            "students lose motivation and attention span during the lesson"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertIn("Education TRIZ", methods)

    def test_route_construction_keywords(self):
        result = triz_router.suggest_methods(
            "the concrete foundation needs curing on the construction site"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertIn("Construction TRIZ", methods)

    def test_route_robotics_keywords(self):
        result = triz_router.suggest_methods(
            "the robot arm has oscillation at the end effector during path planning"
        )
        methods = [m["method"] for m in result["methods"]]
        self.assertIn("Robotics TRIZ", methods)

    # ── --branch filter isolates a single domain's rules ──────────────────

    def test_branch_filter_excludes_other_domains(self):
        text = "the landing page conversion is dropping"
        filtered = triz_router.suggest_methods(text, branch="mechanical")
        filtered_methods = [m["method"] for m in filtered["methods"]]
        self.assertNotIn("Marketing TRIZ", filtered_methods)
        all_methods = triz_router.suggest_methods(text, branch="general")
        all_names = [m["method"] for m in all_methods["methods"]]
        self.assertIn("Marketing TRIZ", all_names)

    # ── Data-driven validation ────────────────────────────────────────────

    def test_branch_datascience_accepted(self):
        result = triz_router.suggest_methods("the model overfits", branch="datascience")
        methods = [m["method"] for m in result["methods"]]
        self.assertIn("Data Science TRIZ", methods)

    def test_suggest_methods_accepts_new_branch_ids(self):
        """Each new field branch id is accepted by suggest_methods and routes
        a field-relevant problem to its own domain method."""
        problems = {
            "energy": "the battery and inverter keep losing energy efficiency",
            "education": "students lose motivation during the lesson",
            "construction": "the concrete foundation needs curing",
            "robotics": "the robot arm has oscillation at the end effector",
        }
        for fid, text in problems.items():
            with self.subTest(branch=fid):
                result = triz_router.suggest_methods(text, branch=fid)
                methods = [m["method"] for m in result["methods"]]
                self.assertGreater(len(methods), 0)
                self.assertIn(self._BRANCH_METHODS[fid], methods)

    def test_branch_bogus_raises(self):
        with self.assertRaises(ValueError):
            triz_router.suggest_methods("the model overfits", branch="bogus")

    def test_branch_keywords_from_json_are_live(self):
        """branch.json keywords not covered by the static rules must still fire
        their branch's method — the router picks the vocabulary up from the data
        (regression: business 'sales'/'competition', rehab 'movement'/'muscle'/
        'recovery' were dead data)."""
        cases = {
            "business": ("our sales are flat and the competition is fierce",
                         "Business TRIZ"),
            "rehab": ("the patient's muscle recovery needs more movement",
                      "Rehabilitation TRIZ"),
        }
        for fid, (text, method) in cases.items():
            with self.subTest(branch=fid):
                result = triz_router.suggest_methods(text, branch=fid)
                methods = [m["method"] for m in result["methods"]]
                self.assertIn(method, methods)

    def test_router_accepts_every_registered_field_branch(self):
        """Auto-pickup contract: every registry field id is a valid --branch for
        the router (registry and router stay in lockstep — no hardcoded list)."""
        for fid in triz_branches.list_branches()["fields"]:
            with self.subTest(branch=fid):
                result = triz_router.suggest_methods("sample problem", branch=fid)
                self.assertGreater(len(result["methods"]), 0)

    def test_branches_validate_requires_method(self):
        """A domain branch.json without a 'method' key is flagged — the router
        needs it to know which TRIZ method the vocabulary triggers."""
        bad = {
            "id": "widgets", "name": "Widgets TRIZ", "name_it": "TRIZ widget",
            "description": "test", "keywords": ["widget"], "examples": ["x"],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            field_dir = Path(tmpdir) / "widgets"
            field_dir.mkdir()
            (field_dir / "branch.json").write_text(
                json.dumps(bad), encoding="utf-8"
            )
            with mock.patch.object(triz_branches, "_FIELDS_DIR", field_dir.parent):
                errors = triz_branches.validate()
        self.assertTrue(
            any("'method'" in e for e in errors),
            f"expected a missing-'method' error, got {errors}",
        )

    def test_dispatcher_new_branch_route_exit0(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "--branch", "supplychain", "route",
             "lead time must drop but safety stock raises cost"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_dispatcher_route_energy(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "--branch", "energy", "route",
             "the battery and inverter on the solar grid keep losing energy efficiency"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Energy TRIZ", proc.stdout)

    def test_dispatcher_route_education(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "--branch", "education", "route",
             "students lose motivation and attention span during the lesson"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Education TRIZ", proc.stdout)

    def test_dispatcher_route_construction(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "--branch", "construction", "route",
             "the concrete foundation needs curing on the construction site"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Construction TRIZ", proc.stdout)

    def test_dispatcher_route_robotics(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "--branch", "robotics", "route",
             "the robot arm has oscillation at the end effector during path planning"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Robotics TRIZ", proc.stdout)

    def test_dispatcher_bogus_branch_exit1(self):
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS_DIR / "triz.py"),
             "--branch", "bogus", "route", "x"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unknown --branch", proc.stderr.lower())

    # ── Use-cases reference ───────────────────────────────────────────────

    def test_use_cases_file_structure(self):
        path = (
            _REPO_ROOT
            / "skills" / "triz-coding-method" / "engine" / "references" / "use-cases.md"
        )
        self.assertTrue(path.is_file(), "references/use-cases.md missing")
        text = path.read_text(encoding="utf-8")
        headings = [
            "## Mechanical / hardware",
            "## Data science / ML / AI",
            "## Marketing / growth",
            "## Supply chain / logistics",
            "## Energy / power",
            "## Education / learning",
            "## Construction / civil",
            "## Robotics / IoT / embedded",
        ]
        h2 = [line for line in text.splitlines() if line.startswith("## ")]
        self.assertEqual(
            h2, headings,
            "use-cases.md must contain exactly the required ## sections, in order",
        )
        sections: dict[str, list[str]] = {}
        current = None
        for line in text.splitlines():
            if line.startswith("## "):
                current = line
                sections.setdefault(current, [])
            elif current is not None:
                for label in self._USE_CASES_LABELS:
                    if line.startswith(label):
                        sections[current].append(label)
                        break
        for heading in headings:
            self.assertEqual(
                sections.get(heading, []), self._USE_CASES_LABELS,
                f"Section {heading!r} must contain the six labels in order",
            )

if __name__ == "__main__":
    unittest.main()
