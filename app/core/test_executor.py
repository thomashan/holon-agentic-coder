"""
Unit tests for app/core/executor.py
"""

import json
import pytest

from app.core import executor as e


class TestExecutePlan:
    def test_execute_returns_measured_result(self, tmp_path):
        result = e.execute_plan(
            plan_id="p-1",
            intent_id="I-100",
            branch_name="I-100-v1/v1",
            ledger_dir=str(tmp_path),
        )
        # Stub executor always returns completed
        assert result["status"] in ("completed", "failed")
        assert result.get("plan_id") == "p-1"
        assert result.get("intent_id") == "I-100"

    def test_execute_raises_on_nonexistent_branch(self, tmp_path):
        result = e.execute_plan(
            plan_id="p-none",
            intent_id="I-no-branch",
            branch_name="nonexistent/branch/path",
            ledger_dir=str(tmp_path),
        )
        assert result["status"] == "failed"

    def test_execution_event_written_to_jsonl(self, tmp_path):
        e.execute_plan("p-ev", "I-ev", "no-such-branch", str(tmp_path))
        path = e._events_path(str(tmp_path))
        assert path.exists()
        lines = path.read_text().splitlines()
        entry = json.loads(lines[-1])
        assert entry.get("plan_id") == "p-ev"


class TestMeasuredEV:
    def test_measured_ev_formula(self):
        measured = {
            "actual_p_success": 0.8,
            "actual_entropy": 0.2,
            "actual_cost": 1.5,
        }
        ev = e._measured_ev(measured)
        assert ev == 0.8 - 0.1 * 0.2 - 1.5


class TestLearningValue:
    def test_learning_value_is_float(self):
        result = {"status": "completed", "p_success": 1.0}
        lv = e._compute_learning_value(result)
        assert isinstance(lv, float)