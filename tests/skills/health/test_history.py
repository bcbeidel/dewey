"""Tests for skills.health.scripts.history — health score history tracking."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from history import record_snapshot


def _tier1_summary(fail_count=0, warn_count=0, total_files=5):
    return {
        "total_files": total_files,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "pass_count": total_files - fail_count,
    }


def _tier2_summary(trigger_counts=None, files_with_triggers=0, total_files_scanned=5):
    return {
        "total_files_scanned": total_files_scanned,
        "files_with_triggers": files_with_triggers,
        "trigger_counts": trigger_counts or {},
    }


class TestRecordSnapshot(unittest.TestCase):
    """Tests for the record_snapshot function."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    # ------------------------------------------------------------------
    # test_creates_log_file
    # ------------------------------------------------------------------
    def test_creates_log_file(self):
        """First snapshot creates health-log.jsonl."""
        log_path = record_snapshot(self.tmpdir, _tier1_summary())
        self.assertTrue(log_path.exists())
        self.assertEqual(log_path.name, "health-log.jsonl")

    # ------------------------------------------------------------------
    # test_appends_valid_json_line
    # ------------------------------------------------------------------
    def test_appends_valid_json_line(self):
        """Entry has timestamp, tier1, tier2 keys."""
        record_snapshot(self.tmpdir, _tier1_summary())
        log_path = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        line = log_path.read_text().strip()
        entry = json.loads(line)
        self.assertIn("timestamp", entry)
        self.assertIn("tier1", entry)
        self.assertIn("tier2", entry)

    # ------------------------------------------------------------------
    # test_multiple_snapshots_append
    # ------------------------------------------------------------------
    def test_multiple_snapshots_append(self):
        """Multiple calls append, not overwrite."""
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=1))
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=0))
        log_path = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        lines = [l for l in log_path.read_text().splitlines() if l.strip()]
        self.assertEqual(len(lines), 2)
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        self.assertEqual(first["tier1"]["fail_count"], 1)
        self.assertEqual(second["tier1"]["fail_count"], 0)

    # ------------------------------------------------------------------
    # test_snapshot_includes_summaries
    # ------------------------------------------------------------------
    def test_snapshot_includes_summaries(self):
        """Exact tier1/tier2 dicts preserved."""
        t1 = _tier1_summary(fail_count=2, warn_count=1, total_files=10)
        t2 = _tier2_summary(
            trigger_counts={"source_drift": 3},
            files_with_triggers=2,
            total_files_scanned=10,
        )
        record_snapshot(self.tmpdir, t1, tier2_summary=t2)
        log_path = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        entry = json.loads(log_path.read_text().strip())
        self.assertEqual(entry["tier1"], t1)
        self.assertEqual(entry["tier2"], t2)

    # ------------------------------------------------------------------
    # test_creates_directory_if_missing
    # ------------------------------------------------------------------
    def test_creates_directory_if_missing(self):
        """Creates .dewey/history/ if absent."""
        history_dir = self.tmpdir / ".dewey" / "history"
        self.assertFalse(history_dir.exists())
        record_snapshot(self.tmpdir, _tier1_summary())
        self.assertTrue(history_dir.is_dir())

    # ------------------------------------------------------------------
    # test_tier2_summary_optional
    # ------------------------------------------------------------------
    def test_tier2_summary_optional(self):
        """tier2_summary=None stores null."""
        record_snapshot(self.tmpdir, _tier1_summary())
        log_path = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        entry = json.loads(log_path.read_text().strip())
        self.assertIsNone(entry["tier2"])


if __name__ == "__main__":
    unittest.main()
