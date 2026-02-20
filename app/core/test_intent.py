"""
Unit tests for app/core/intent.py  (unittest — stdlib, no install needed)
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import app.core.intent as intent_mod


class FakeResult:
    def __init__(self, returncode: int, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


# ── intent.py internal helpers ───────────────────────────────────────────────

class TestSlugify:
    def test_slash_becomes_dash(self):
        self.assertEqual(intent_mod._slugify("foo/bar/baz"), "foo-bar-baz")

    def test_non_alphanumeric_replaced(self):
        self.assertEqual(intent_mod._slugify("hello world!"), "hello-world")

    def test_empty_yields_unnamed(self):
        self.assertEqual(intent_mod._slugify(""), " unnamed")


class TestBuildBranch:
    def test_includes_intent_id_and_slug(self):
        intent = {"intent_id": "I-123", "title": "Write tests",
                  "branch": "write-tests"}
        # git not touched — _run patched
        intent_mod._run = lambda cmd, cwd=None: FakeResult(0)
        branch = intent_mod._build_branch(intent)
        self.assertIn("I-123", branch)
        self.assertIn("write-tests", branch)


class TestCreateIntent:
    def test_load_intent_parses_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         delete_after=True) as f:
            f.write('{"intent_id": "I-99", "title": "test"}')
            f.flush()
            loaded = intent_mod._load_intent(f.name)
        self.assertEqual(loaded["intent_id"], "I-99")

    def test_append_intent_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = {"intent_id": "I-77", "status": "created"}
            intent_mod._append_intent(tmp, entry)
            path = Path(tmp) / "intents.jsonl"
            self.assertTrue(path.exists())
            lines = path.read_text().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["intent_id"], "I-77")

    def test_create_intent_returns_enriched_intent(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "intent.json"
            f.write('{"intent_id": "I-55", "title": "bootstrap"}')

            # Patch git to avoid creating real branches
            intent_mod._run = lambda cmd, cwd=None: FakeResult(1)

            result = intent_mod.create_intent(str(f), tmp)
        self.assertEqual(result["intent_id"], "I-55")
    # branch_name added by create_intent
        self.assertIn("branch_name", result)
        self.assertEqual(result["status"], "created")

    def test_create_intent_idempotent_when_branch_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "intent.json"
            f.write('{"intent_id": "I-66", "title": "noop"}')

            # Simulate branch already exists
            intent_mod._run = lambda cmd, cwd=None: FakeResult(0)

            result = intent_mod.create_intent(str(f), tmp)
        self.assertEqual(result["status"], "created")


if __name__ == "__main__":
    unittest.main()