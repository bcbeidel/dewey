"""Tests for skills.health.scripts.utilization — topic reference tracking."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from utilization import read_utilization, record_reference


class TestRecordReference(unittest.TestCase):
    """Tests for the record_reference function."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    # ------------------------------------------------------------------
    # test_creates_log_file
    # ------------------------------------------------------------------
    def test_creates_log_file(self):
        """First reference creates log.jsonl."""
        log_path = record_reference(self.tmpdir, "topic/foo.md")
        self.assertTrue(log_path.exists())
        self.assertEqual(log_path.name, "log.jsonl")

    # ------------------------------------------------------------------
    # test_appends_valid_json_line
    # ------------------------------------------------------------------
    def test_appends_valid_json_line(self):
        """Entry has file, timestamp, context keys."""
        record_reference(self.tmpdir, "topic/foo.md")
        log_path = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        line = log_path.read_text().strip()
        entry = json.loads(line)
        self.assertIn("file", entry)
        self.assertIn("timestamp", entry)
        self.assertIn("context", entry)

    # ------------------------------------------------------------------
    # test_default_context_is_user
    # ------------------------------------------------------------------
    def test_default_context_is_user(self):
        """Default context is 'user'."""
        record_reference(self.tmpdir, "topic/foo.md")
        log_path = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        entry = json.loads(log_path.read_text().strip())
        self.assertEqual(entry["context"], "user")

    # ------------------------------------------------------------------
    # test_custom_context
    # ------------------------------------------------------------------
    def test_custom_context(self):
        """Custom context like 'audit' is recorded."""
        record_reference(self.tmpdir, "topic/foo.md", context="audit")
        log_path = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        entry = json.loads(log_path.read_text().strip())
        self.assertEqual(entry["context"], "audit")

    # ------------------------------------------------------------------
    # test_multiple_references_append
    # ------------------------------------------------------------------
    def test_multiple_references_append(self):
        """Multiple calls append, not overwrite."""
        record_reference(self.tmpdir, "topic/foo.md")
        record_reference(self.tmpdir, "topic/bar.md", context="audit")
        log_path = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        lines = [l for l in log_path.read_text().splitlines() if l.strip()]
        self.assertEqual(len(lines), 2)
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        self.assertEqual(first["file"], "topic/foo.md")
        self.assertEqual(second["file"], "topic/bar.md")

    # ------------------------------------------------------------------
    # test_creates_directory_if_missing
    # ------------------------------------------------------------------
    def test_creates_directory_if_missing(self):
        """Creates .dewey/utilization/ if absent."""
        util_dir = self.tmpdir / ".dewey" / "utilization"
        self.assertFalse(util_dir.exists())
        record_reference(self.tmpdir, "topic/foo.md")
        self.assertTrue(util_dir.is_dir())


class TestReadUtilization(unittest.TestCase):
    """Tests for the read_utilization function."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    # ------------------------------------------------------------------
    # test_empty_log
    # ------------------------------------------------------------------
    def test_empty_log(self):
        """No log file returns empty dict."""
        result = read_utilization(self.tmpdir)
        self.assertEqual(result, {})

    # ------------------------------------------------------------------
    # test_single_reference
    # ------------------------------------------------------------------
    def test_single_reference(self):
        """One reference produces count=1."""
        record_reference(self.tmpdir, "topic/foo.md")
        stats = read_utilization(self.tmpdir)
        self.assertEqual(stats["topic/foo.md"]["count"], 1)

    # ------------------------------------------------------------------
    # test_multiple_references_same_file
    # ------------------------------------------------------------------
    def test_multiple_references_same_file(self):
        """3 references to same file produce count=3."""
        for _ in range(3):
            record_reference(self.tmpdir, "topic/foo.md")
        stats = read_utilization(self.tmpdir)
        self.assertEqual(stats["topic/foo.md"]["count"], 3)

    # ------------------------------------------------------------------
    # test_multiple_files
    # ------------------------------------------------------------------
    def test_multiple_files(self):
        """Different files have separate entries."""
        record_reference(self.tmpdir, "topic/foo.md")
        record_reference(self.tmpdir, "topic/bar.md")
        stats = read_utilization(self.tmpdir)
        self.assertIn("topic/foo.md", stats)
        self.assertIn("topic/bar.md", stats)
        self.assertEqual(stats["topic/foo.md"]["count"], 1)
        self.assertEqual(stats["topic/bar.md"]["count"], 1)

    # ------------------------------------------------------------------
    # test_includes_last_referenced
    # ------------------------------------------------------------------
    def test_includes_last_referenced(self):
        """Entry has last_referenced key."""
        record_reference(self.tmpdir, "topic/foo.md")
        stats = read_utilization(self.tmpdir)
        self.assertIn("last_referenced", stats["topic/foo.md"])

    # ------------------------------------------------------------------
    # test_includes_first_referenced
    # ------------------------------------------------------------------
    def test_includes_first_referenced(self):
        """Entry has first_referenced key."""
        record_reference(self.tmpdir, "topic/foo.md")
        stats = read_utilization(self.tmpdir)
        self.assertIn("first_referenced", stats["topic/foo.md"])

    # ------------------------------------------------------------------
    # test_last_referenced_is_latest
    # ------------------------------------------------------------------
    def test_last_referenced_is_latest(self):
        """last_referenced >= first_referenced."""
        record_reference(self.tmpdir, "topic/foo.md")
        record_reference(self.tmpdir, "topic/foo.md")
        stats = read_utilization(self.tmpdir)
        entry = stats["topic/foo.md"]
        self.assertGreaterEqual(
            entry["last_referenced"], entry["first_referenced"]
        )


if __name__ == "__main__":
    unittest.main()
