"""Tests for skills.health.scripts.history — health score history tracking."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from history import record_snapshot, read_history


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


class TestReadHistory(unittest.TestCase):
    """Tests for the read_history function."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    # ------------------------------------------------------------------
    # test_empty_history
    # ------------------------------------------------------------------
    def test_empty_history(self):
        """No log file returns empty list."""
        result = read_history(self.tmpdir)
        self.assertEqual(result, [])

    # ------------------------------------------------------------------
    # test_returns_snapshots_in_order
    # ------------------------------------------------------------------
    def test_returns_snapshots_in_order(self):
        """Chronological order preserved (oldest first)."""
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=3))
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=2))
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=1))

        history = read_history(self.tmpdir)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["tier1"]["fail_count"], 3)
        self.assertEqual(history[1]["tier1"]["fail_count"], 2)
        self.assertEqual(history[2]["tier1"]["fail_count"], 1)

    # ------------------------------------------------------------------
    # test_limit_parameter
    # ------------------------------------------------------------------
    def test_limit_parameter(self):
        """limit=N returns only last N snapshots."""
        for i in range(5):
            record_snapshot(self.tmpdir, _tier1_summary(fail_count=i))

        history = read_history(self.tmpdir, limit=2)
        self.assertEqual(len(history), 2)
        # Last two entries: fail_count 3 and 4
        self.assertEqual(history[0]["tier1"]["fail_count"], 3)
        self.assertEqual(history[1]["tier1"]["fail_count"], 4)

    # ------------------------------------------------------------------
    # test_limit_larger_than_history
    # ------------------------------------------------------------------
    def test_limit_larger_than_history(self):
        """limit bigger than available returns all."""
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=1))
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=2))

        history = read_history(self.tmpdir, limit=100)
        self.assertEqual(len(history), 2)

    # ------------------------------------------------------------------
    # test_each_entry_has_expected_keys
    # ------------------------------------------------------------------
    def test_each_entry_has_expected_keys(self):
        """Each entry has timestamp, tier1, tier2 keys."""
        t2 = _tier2_summary(trigger_counts={"stale_source": 1})
        record_snapshot(self.tmpdir, _tier1_summary(), tier2_summary=t2)

        history = read_history(self.tmpdir)
        self.assertEqual(len(history), 1)
        entry = history[0]
        self.assertIn("timestamp", entry)
        self.assertIn("tier1", entry)
        self.assertIn("tier2", entry)


class TestFileListInSnapshots(unittest.TestCase):
    """Tests for file_list field in history snapshots."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_snapshot_includes_file_list(self):
        """file_list is stored in the snapshot entry."""
        files = ["area/overview.md", "area/topic.md"]
        record_snapshot(self.tmpdir, _tier1_summary(), file_list=files)
        log_path = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        entry = json.loads(log_path.read_text().strip())
        self.assertEqual(entry["file_list"], files)

    def test_file_list_defaults_to_empty(self):
        """file_list defaults to empty list when not provided."""
        record_snapshot(self.tmpdir, _tier1_summary())
        log_path = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        entry = json.loads(log_path.read_text().strip())
        self.assertEqual(entry["file_list"], [])

    def test_file_list_preserved_in_read_history(self):
        """read_history returns entries with file_list intact."""
        files = ["sagemaker/overview.md", "sagemaker/mlops.md"]
        record_snapshot(self.tmpdir, _tier1_summary(), file_list=files)
        history = read_history(self.tmpdir)
        self.assertEqual(history[0]["file_list"], files)


if __name__ == "__main__":
    unittest.main()
