"""
Unit tests for app/core/planner.py  (unittest — stdlib)
"""

import json
import os
import shutil
import tempfile

from app.core import planner as p


class TestEV:
    def test_higher_p_success_wins(self):
        high = {"p_success": 0.9, "entropy": 0.1, "impact": 1.0, "cost": 0.0}
        low = {"p_success": 0.5, "entropy": 0.1, "impact": 1.0, "cost": 0.0}
        self.assertGreater(p._ev(high), p._ev(low))

    def test_entropy_is_punished(self):
        calm = {"p_success": 0.7, "entropy": 0.0, "impact": 1.0, "cost": 0.0}
        noisy = {"p_success": 0.7, "entropy": 1.0, "impact": 1.0, "cost": 0.0}
        self.assertGreater(p._ev(calm), p._ev(noisy))

    def test_defaults_when_missing_keys(self):
        plan = {}
        ev = p._ev(plan)
        # Defaults: P=0.5, S=0, I=1, C=0  => EV = 0.5*1 - 0
        self.assertEqual(ev, 0.5 * 1.0)


class TestGeneratePlans:
    def test_generates_correct_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            plans = p.generate_plans("I-123", tmp, max_variants=4)
            self.assertEqual(len(plans), 4)
            ids = [pl["plan_id"] for pl in plans]
            self.assertListEqual(ids,
                                 ["I-123-v1", "I-123-v2", "I-123-v3",
                                  "I-123-v4"])

    def test_each_plan_has_ev(self):
        with tempfile.TemporaryDirectory() as tmp:
            plans = p.generate_plans("I-456", tmp)
            for plan in plans:
                self.assertIn("ev", plan)
                self.assertIsInstance(plan["ev"], float)

    def test_plans_written_to_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            p.generate_plans("I-789", tmp)
            path = p._plans_path(tmp)
            self.assertTrue(path.exists())
            lines = path.read_text().splitlines()
            self.assertEqual(len(lines), 3)
            for line in lines:
                self.assertEqual(json.loads(line).get("intent_id"),
                                 "I-789")


class TestSelectBestPlanByEv:
    def test_raises_when_no_plans_for_intent_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "No plans found"):
                p.select_best_plan_by_ev("I-does-not-exist", tmp)

    def test_selects_highest_ev(self):
        with tempfile.TemporaryDirectory() as tmp:
            p._append_plan(tmp, {
                "plan_id": "p1", "intent_id": "I-best",
                "p_success": 0.5, "entropy": 0.1,
                "impact": 1.0, "cost": 0.0,
            })
            p._append_plan(tmp, {
                "plan_id": "p2", "intent_id": "I-best",
                "p_success": 0.9, "entropy": 0.1,
                "impact": 1.0, "cost": 0.0,
            })
            best = p.select_best_plan_by_ev("I-best", tmp)
            self.assertEqual(best["plan_id"], "p2")

    def test_ignores_other_intents(self):
        with tempfile.TemporaryDirectory() as tmp:
            p._append_plan(tmp, {
                "plan_id": "x", "intent_id": "I-other",
                "p_success": 0.9, "entropy": 0.1,
                "impact": 1.0, "cost": 0.0,
            })
            p._append_plan(tmp, {
                "plan_id": "y", "intent_id": "I-target",
                "p_success": 0.5, "entropy": 0.1,
                "impact": 1.0, "cost": 0.0,
            })
            best = p.select_best_plan_by_ev("I-target", tmp)
            self.assertEqual(best["plan_id"], "y")


if __name__ == "__main__":
    import unittest
    unittest.main()