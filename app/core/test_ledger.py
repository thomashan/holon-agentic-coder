"""
Unit tests for app/core/ledger.py
"""

import json
import pytest

from app.core import ledger as l


class TestAppendLedger:
    def test_creates_file_if_missing(self, tmp_path):
        l.append_ledger(str(tmp_path), "events", {"event_id": "e1"})
        path = tmp_path / "events.jsonl"
        assert path.exists()
        lines = path.read_text().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["event_id"] == "e1"

    def test_append_is_idempotent(self, tmp_path):
        l.append_ledger(str(tmp_path), "events", {"id": 1})
        l.append_ledger(str(tmp_path), "events", {"id": 2})
        path = tmp_path / "events.jsonl"
        lines = path.read_text().splitlines()
        assert len(lines) == 2
        ids = [json.loads(line).get("id") for line in lines]
        assert ids == [1, 2]


class TestReadLedger:
    def test_returns_empty_list_for_missing_file(self, tmp_path):
        entries = l.read_ledger(str(tmp_path), "nonexistent")
        assert entries == []

    def test_read_all_entries(self, tmp_path):
        l.append_ledger(str(tmp_path), "plans", {"id": 1})
        l.append_ledger(str(tmp_path), "plans", {"id": 2})
        entries = l.read_ledger(str(tmp_path), "plans")
        assert len(entries) == 2
        ids = [e.get("id") for e in entries]
        assert ids == [1, 2]


class TestQueryLedger:
    def test_filters_by_key_value(self, tmp_path):
        l.append_ledger(str(tmp_path), "plans", {"id": 1, "intent_id": "I-100"})
        l.append_ledger(str(tmp_path), "plans", {"id": 2, "intent_id": "I-200"})
        results = l.query_ledger(str(tmp_path), "plans", intent_id="I-100")
        assert len(results) == 1
        assert results[0]["id"] == 1


class TestLatestLedgerEntry:
    def test_returns_none_for_empty_ledger(self, tmp_path):
        assert l.latest_ledger_entry(str(tmp_path), "events") is None

    def test_returns_last_entry(self, tmp_path):
        l.append_ledger(str(tmp_path), "events", {"seq": 1})
        l.append_ledger(str(tmp_path), "events", {"seq": 2})
        latest = l.latest_ledger_entry(str(tmp_path), "events")
        assert latest["seq"] == 2


class TestLedgerError:
    def test_ledger_error_is_exception(self):
        with pytest.raises(l.LedgerError, match="Could not write"):
            l.append_ledger("/nonexistent/path", "events", {})