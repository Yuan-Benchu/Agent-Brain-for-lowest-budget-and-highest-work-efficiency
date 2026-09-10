"""Offline tests of observable routing, evidence and accounting invariants."""
import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "skills" / "agent-brain"
spec = importlib.util.spec_from_file_location("brain", SKILL / "scripts" / "brain.py")
brain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brain)
NOW = datetime(2026, 9, 10, tzinfo=timezone.utc)


class BrainBehavior(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL / "assets" / "demo.plan.json").read_text())

    def test_quality_gate_beats_cheaper_preference(self):
        result = brain.plan(self.data, NOW)
        self.assertEqual(result["selected"]["id"], "demo-terra")
        self.assertFalse(result["dispatch_performed"])

    def test_shared_pool_blocks_every_model(self):
        self.data["pools"]["demo-codex"]["remaining_percent"] = 0
        self.assertIsNone(brain.plan(self.data, NOW)["selected"])

    def test_unverified_pool_identity_is_not_assumed_independent(self):
        self.data["pools"]["demo-codex"]["identity_verified"] = False
        self.assertIsNone(brain.plan(self.data, NOW)["selected"])

    def test_desktop_capability_cannot_be_replaced_by_cli(self):
        self.data["task"]["requires"] = ["cowork-drive"]
        self.assertEqual(brain.plan(self.data, NOW)["status"], "blocked")

    def test_explicit_choice_is_not_silently_replaced(self):
        self.data["task"]["requested_model"] = "example-gemini"
        self.assertIsNone(brain.plan(self.data, NOW)["selected"])

    def test_unknown_quota_is_not_zero_cost(self):
        self.data["pools"]["demo-codex"]["remaining_percent"] = None
        self.assertEqual(brain.plan(self.data, NOW)["status"], "blocked")

    def test_stale_capability_and_quota_need_refresh(self):
        for subject in (self.data["agents"][1], self.data["pools"]["demo-codex"]):
            previous = subject["valid_until"]
            subject["valid_until"] = "2020-01-01T00:00:00Z"
            self.assertIsNone(brain.plan(self.data, NOW)["selected"])
            subject["valid_until"] = previous

    def test_whole_task_estimate_can_outweigh_preference(self):
        self.data["task"]["min_tier"] = 1
        self.data["agents"][0]["estimated_total"] = {"value": 6, "unit": "demo-credit"}
        self.data["agents"][1]["estimated_total"] = {"value": 5, "unit": "demo-credit"}
        self.assertEqual(brain.plan(self.data, NOW)["selected"]["id"], "demo-terra")
        self.data["agents"][0]["estimated_total"]["unit"] = "different-provider-credit"
        result = brain.plan(self.data, NOW)
        self.assertEqual(result["selected"]["id"], "demo-luna")
        self.assertIn("unavailable", result["ranking_basis"])

    def test_low_reserve_prefers_independent_available_pool(self):
        self.data["pools"]["demo-codex"]["remaining_percent"] = 15
        self.data["pools"]["demo-google"]["remaining_percent"] = 80
        self.assertEqual(brain.plan(self.data, NOW)["selected"]["id"], "demo-gemini")
        self.data["task"]["requested_model"] = "example-terra"
        result = brain.plan(self.data, NOW)
        self.assertEqual(result["selected"]["id"], "demo-terra")
        self.assertTrue(result["reserve_warning"])

    def test_nonzero_exit_survives_misleading_pass_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.log"
            raw = "passed\n" * 500 + "ERROR checkout.py:42 wrong total\n" + "passed\n" * 500
            path.write_text(raw, encoding="utf-8")
            result = brain.digest(path, 1, max_lines=10)
            self.assertEqual(result["command_state"], "failed")
            self.assertEqual(result["acceptance"], "not_determined")
            self.assertTrue(any("checkout.py:42" in line["text"] for line in result["lines"]))
            self.assertTrue(result["truncated"])
            self.assertLessEqual(len(result["lines"]), 10)
            self.assertEqual(path.read_text(encoding="utf-8"), raw)

    def test_long_line_truncation_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.log"
            path.write_text("ERROR " + "x" * 200, encoding="utf-8")
            result = brain.digest(path, 0, max_chars=20)
            self.assertTrue(result["partial_line"])
            self.assertEqual(result["acceptance"], "not_determined")
            self.assertLessEqual(sum(len(line["text"]) for line in result["lines"]), 20)

    def test_unrecognized_middle_failure_requires_source_review(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.log"
            path.write_text("ok\n" * 50 + "expected 4, got 5\n" + "ok\n" * 50)
            self.assertTrue(brain.digest(path, 1)["needs_source_review"])

    def test_accounting_separates_models_and_retains_unknown(self):
        data = json.loads((SKILL / "assets" / "demo.usage.json").read_text())
        result = brain.account(data)
        inputs = [r for r in result["groups"] if r["metric"] == "input_tokens"]
        self.assertEqual(sorted(r["known_subtotal"] for r in inputs), [350, 1200])
        costs = [r for r in result["groups"] if r["metric"] == "estimated_cost"]
        self.assertTrue(all(r["known_subtotal"] is None for r in costs))
        self.assertIsNone(result["savings_percent"])
        extra = copy.deepcopy(data["entries"][0])
        extra["event_id"], extra["pool"] = "other-pool", "independent-pool"
        data["entries"].append(extra)
        self.assertEqual(len(brain.account(data)["groups"]), 6)

    def test_duplicate_and_cumulative_counters_rejected(self):
        data = json.loads((SKILL / "assets" / "demo.usage.json").read_text())
        data["entries"].append(copy.deepcopy(data["entries"][0]))
        with self.assertRaises(ValueError):
            brain.account(data)
        data["entries"].pop()
        data["entries"][0]["counter_mode"] = "cumulative"
        with self.assertRaises(ValueError):
            brain.account(data)

    def test_parent_aggregate_is_rejected(self):
        data = json.loads((SKILL / "assets" / "demo.usage.json").read_text())
        data["entries"][0]["scope"] = "including_children"
        with self.assertRaises(ValueError):
            brain.account(data)


if __name__ == "__main__":
    unittest.main()
