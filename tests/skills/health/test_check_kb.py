"""Tests for skills.health.scripts.check_kb — health check runner."""

import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from check_kb import run_health_check, run_tier2_prescreening


def _write(path: Path, text: str) -> Path:
    """Helper — write *text* to *path*, creating parents as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _valid_md(depth: str = "working", extra_body: str = "") -> str:
    """Return a minimal valid markdown document with proper frontmatter."""
    today = date.today().isoformat()
    # Ensure enough lines to pass size bounds for the given depth
    padding = "\n".join([f"Line {i}" for i in range(15)])
    return (
        f"---\n"
        f"sources:\n"
        f"  - https://example.com/doc\n"
        f"last_validated: {today}\n"
        f"relevance: core\n"
        f"depth: {depth}\n"
        f"---\n"
        f"\n"
        f"# Topic\n"
        f"\n"
        f"## In Practice\n"
        f"Concrete guidance here.\n"
        f"\n"
        f"## Key Guidance\n"
        f"Abstract principles here.\n"
        f"\n"
        f"{padding}\n"
        f"{extra_body}\n"
    )


class TestRunHealthCheck(unittest.TestCase):
    """Tests for the run_health_check function."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.kb = self.tmpdir / "docs"
        self.kb.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    # ------------------------------------------------------------------
    # test_returns_structured_report
    # ------------------------------------------------------------------
    def test_returns_structured_report(self):
        """Result has 'issues' and 'summary' keys."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        result = run_health_check(self.tmpdir)
        self.assertIn("issues", result)
        self.assertIn("summary", result)
        self.assertIsInstance(result["issues"], list)
        self.assertIsInstance(result["summary"], dict)

    # ------------------------------------------------------------------
    # test_reports_missing_overview
    # ------------------------------------------------------------------
    def test_reports_missing_overview(self):
        """Area without overview.md produces a fail-severity issue."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "topic.md", _valid_md("working"))
        result = run_health_check(self.tmpdir)
        overview_issues = [
            i for i in result["issues"]
            if "overview.md" in i["message"]
        ]
        self.assertTrue(len(overview_issues) > 0)
        self.assertTrue(any(i["severity"] == "fail" for i in overview_issues))

    # ------------------------------------------------------------------
    # test_clean_kb_has_no_failures
    # ------------------------------------------------------------------
    def test_clean_kb_has_no_failures(self):
        """A valid KB produces zero fail-severity issues."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        _write(area / "topic.md", _valid_md("working"))
        _write(area / "topic.ref.md", _valid_md("reference"))
        result = run_health_check(self.tmpdir)
        fails = [i for i in result["issues"] if i["severity"] == "fail"]
        self.assertEqual(fails, [], f"Unexpected failures: {fails}")

    # ------------------------------------------------------------------
    # test_summary_includes_counts
    # ------------------------------------------------------------------
    def test_summary_includes_counts(self):
        """Summary contains total_files, fail_count, warn_count, pass_count."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        result = run_health_check(self.tmpdir)
        summary = result["summary"]
        for key in ("total_files", "fail_count", "warn_count", "pass_count"):
            self.assertIn(key, summary, f"Missing summary key: {key}")
            self.assertIsInstance(summary[key], int)

    # ------------------------------------------------------------------
    # test_skips_proposals
    # ------------------------------------------------------------------
    def test_skips_proposals(self):
        """Files inside _proposals/ are not validated."""
        proposals = self.kb / "_proposals"
        proposals.mkdir()
        _write(proposals / "draft.md", "# No frontmatter at all\n")
        result = run_health_check(self.tmpdir)
        proposal_issues = [
            i for i in result["issues"]
            if "_proposals" in i.get("file", "")
        ]
        self.assertEqual(proposal_issues, [])

    # ------------------------------------------------------------------
    # test_total_files_count
    # ------------------------------------------------------------------
    def test_total_files_count(self):
        """total_files accurately counts markdown files."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        _write(area / "topic.md", _valid_md("working"))
        result = run_health_check(self.tmpdir)
        self.assertEqual(result["summary"]["total_files"], 2)


class TestRunTier2Prescreening(unittest.TestCase):
    """Tests for the run_tier2_prescreening function."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.kb = self.tmpdir / "docs"
        self.kb.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_returns_structured_queue(self):
        """Result has 'queue' and 'summary' keys."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        result = run_tier2_prescreening(self.tmpdir)
        self.assertIn("queue", result)
        self.assertIn("summary", result)
        self.assertIsInstance(result["queue"], list)
        self.assertIsInstance(result["summary"], dict)

    def test_stale_file_produces_trigger(self):
        """A file with old last_validated should produce a source_drift trigger."""
        area = self.kb / "area-one"
        area.mkdir()
        stale_md = (
            "---\n"
            "sources:\n"
            "  - https://example.com/doc\n"
            "last_validated: 2020-01-01\n"
            "relevance: core\n"
            "depth: overview\n"
            "---\n"
            "\n"
            "# Topic\n"
            "\n"
            "Content here.\n"
        )
        _write(area / "stale.md", stale_md)
        result = run_tier2_prescreening(self.tmpdir)
        drift_items = [i for i in result["queue"] if i["trigger"] == "source_drift"]
        self.assertTrue(len(drift_items) > 0)

    def test_summary_includes_counts(self):
        """Summary contains total_files_scanned, files_with_triggers, trigger_counts."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        result = run_tier2_prescreening(self.tmpdir)
        summary = result["summary"]
        for key in ("total_files_scanned", "files_with_triggers", "trigger_counts"):
            self.assertIn(key, summary, f"Missing summary key: {key}")

    def test_clean_file_no_triggers(self):
        """A well-formed file should produce no triggers."""
        area = self.kb / "area-one"
        area.mkdir()
        # Pad with enough words to satisfy Tier 2 depth_accuracy (min 50 for overview)
        extra = "\n".join([f"Additional content line {i} with words." for i in range(10)])
        _write(area / "overview.md", _valid_md("overview", extra_body=extra))
        result = run_tier2_prescreening(self.tmpdir)
        overview_triggers = [
            i for i in result["queue"]
            if "overview.md" in i["file"]
        ]
        self.assertEqual(overview_triggers, [])


class TestTier2OutputSchema(unittest.TestCase):
    """Validate the output schema of run_tier2_prescreening for workflow consumption."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.kb = self.tmpdir / "docs"
        self.kb.mkdir()

        # Create test data that triggers multiple trigger types.
        area = self.kb / "area-one"
        area.mkdir()

        # A stale overview file — triggers source_drift (old last_validated)
        stale_md = (
            "---\n"
            "sources:\n"
            "  - https://example.com/doc\n"
            "last_validated: 2020-01-01\n"
            "relevance: core\n"
            "depth: overview\n"
            "---\n"
            "\n"
            "# Topic\n"
            "\n"
            "Content here.\n"
        )
        _write(area / "overview.md", stale_md)

        # A thin working-depth file — triggers depth_accuracy (too few words),
        # why_quality (missing section), concrete_examples (no concrete elements),
        # and source_primacy (no inline sources).
        thin_working_md = (
            "---\n"
            "sources:\n"
            "  - https://example.com/doc\n"
            "last_validated: 2020-01-01\n"
            "relevance: core\n"
            "depth: working\n"
            "---\n"
            "\n"
            "# Topic\n"
            "\n"
            "## Key Guidance\n"
            "- Do the thing\n"
            "- Do the other thing\n"
            "- And another thing\n"
            "\n"
            "## In Practice\n"
            "Just some text without concrete elements.\n"
        )
        _write(area / "topic.md", thin_working_md)

        self.result = run_tier2_prescreening(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    # ------------------------------------------------------------------
    # test_queue_item_schema
    # ------------------------------------------------------------------
    def test_queue_item_schema(self):
        """Every queue item must have file, trigger, reason, context keys;
        context must be a dict."""
        queue = self.result["queue"]
        self.assertTrue(len(queue) > 0, "Expected at least one queue item")

        required_keys = {"file", "trigger", "reason", "context"}
        for item in queue:
            for key in required_keys:
                self.assertIn(key, item, f"Missing key '{key}' in queue item: {item}")
            self.assertIsInstance(
                item["context"], dict,
                f"context should be a dict, got {type(item['context']).__name__}",
            )

    # ------------------------------------------------------------------
    # test_trigger_counts_match_queue
    # ------------------------------------------------------------------
    def test_trigger_counts_match_queue(self):
        """Summary trigger_counts must match actual counts from the queue."""
        queue = self.result["queue"]
        summary_counts = self.result["summary"]["trigger_counts"]

        # Count triggers from the queue directly
        actual_counts: dict[str, int] = {}
        for item in queue:
            t = item["trigger"]
            actual_counts[t] = actual_counts.get(t, 0) + 1

        self.assertEqual(
            summary_counts, actual_counts,
            f"trigger_counts mismatch: summary={summary_counts}, actual={actual_counts}",
        )

    # ------------------------------------------------------------------
    # test_valid_trigger_names
    # ------------------------------------------------------------------
    def test_valid_trigger_names(self):
        """Every trigger name must be one of the 5 known triggers."""
        known_triggers = {
            "source_drift",
            "depth_accuracy",
            "source_primacy",
            "why_quality",
            "concrete_examples",
        }
        queue = self.result["queue"]
        self.assertTrue(len(queue) > 0, "Expected at least one queue item")

        for item in queue:
            self.assertIn(
                item["trigger"], known_triggers,
                f"Unknown trigger '{item['trigger']}' in queue item: {item}",
            )


if __name__ == "__main__":
    unittest.main()
