"""Tests for skills.health.scripts.tier2_triggers — Tier 2 deterministic triggers."""

import shutil
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from tier2_triggers import (
    trigger_concrete_examples,
    trigger_depth_accuracy,
    trigger_source_drift,
    trigger_source_primacy,
    trigger_why_quality,
)


def _write(path: Path, text: str) -> Path:
    """Helper — write *text* to *path*, creating parents as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _fm(depth: str = "working", last_validated: Optional[str] = None,
        sources: str = "  - https://example.com/doc") -> str:
    """Return frontmatter block with given fields."""
    today = last_validated or date.today().isoformat()
    return (
        f"---\n"
        f"sources:\n"
        f"{sources}\n"
        f"last_validated: {today}\n"
        f"relevance: core\n"
        f"depth: {depth}\n"
        f"---\n"
    )


# ======================================================================
# TestTriggerSourceDrift
# ======================================================================


class TestTriggerSourceDrift(unittest.TestCase):
    """Tests for trigger_source_drift."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_fresh_file_no_trigger(self):
        """File validated today should not trigger."""
        f = _write(self.tmpdir / "topic.md", _fm(last_validated=date.today().isoformat()))
        self.assertEqual(trigger_source_drift(f), [])

    def test_stale_file_triggers(self):
        """File older than max_age_days should trigger."""
        old_date = (date.today() - timedelta(days=100)).isoformat()
        f = _write(self.tmpdir / "topic.md", _fm(last_validated=old_date))
        results = trigger_source_drift(f)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["trigger"], "source_drift")
        self.assertIn("100", results[0]["reason"])

    def test_missing_last_validated_triggers(self):
        """Missing last_validated field should trigger."""
        f = _write(self.tmpdir / "topic.md",
                   "---\nsources:\n  - https://example.com\nrelevance: core\ndepth: working\n---\n")
        results = trigger_source_drift(f)
        self.assertEqual(len(results), 1)
        self.assertIn("Missing", results[0]["reason"])

    def test_custom_max_age(self):
        """Custom max_age_days should be respected."""
        old_date = (date.today() - timedelta(days=50)).isoformat()
        f = _write(self.tmpdir / "topic.md", _fm(last_validated=old_date))
        # 50 days old, default 90 — no trigger
        self.assertEqual(trigger_source_drift(f), [])
        # 50 days old, max 30 — trigger
        results = trigger_source_drift(f, max_age_days=30)
        self.assertEqual(len(results), 1)

    def test_context_includes_source_urls(self):
        """Context should include extracted source URLs."""
        old_date = (date.today() - timedelta(days=100)).isoformat()
        f = _write(self.tmpdir / "topic.md", _fm(
            last_validated=old_date,
            sources="  - https://example.com/one\n  - https://example.com/two",
        ))
        results = trigger_source_drift(f)
        self.assertEqual(len(results[0]["context"]["source_urls"]), 2)

    def test_structured_source_urls(self):
        """Should handle 'url: https://...' format in sources."""
        old_date = (date.today() - timedelta(days=100)).isoformat()
        f = _write(self.tmpdir / "topic.md", _fm(
            last_validated=old_date,
            sources="  - url: https://example.com/structured",
        ))
        results = trigger_source_drift(f)
        urls = results[0]["context"]["source_urls"]
        self.assertEqual(urls, ["https://example.com/structured"])


# ======================================================================
# TestTriggerDepthAccuracy
# ======================================================================


class TestTriggerDepthAccuracy(unittest.TestCase):
    """Tests for trigger_depth_accuracy."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_within_range_no_trigger(self):
        """Working-depth file with appropriate content should not trigger."""
        # Mix of prose and structural lines to get realistic ratio (~0.5)
        lines = []
        lines.append("## Overview")
        for i in range(20):
            lines.append(f"This is a prose sentence about topic {i} that adds words.")
            lines.append(f"- List item {i}")
        f = _write(self.tmpdir / "topic.md", _fm("working") + "\n".join(lines) + "\n")
        self.assertEqual(trigger_depth_accuracy(f), [])

    def test_overview_too_verbose(self):
        """Overview with too many words should trigger."""
        prose = " ".join(["word"] * 1000)
        f = _write(self.tmpdir / "topic.md", _fm("overview") + f"\n{prose}\n")
        results = trigger_depth_accuracy(f)
        self.assertEqual(len(results), 1)
        self.assertIn("word count", results[0]["reason"])

    def test_reference_too_narrative(self):
        """Reference file with high prose ratio should trigger."""
        # Many prose lines, pushing ratio above 0.5
        prose_lines = "\n".join([f"This is a narrative sentence number {i}." for i in range(30)])
        f = _write(self.tmpdir / "topic.md", _fm("reference") + f"\n{prose_lines}\n")
        results = trigger_depth_accuracy(f)
        self.assertEqual(len(results), 1)
        self.assertIn("depth_accuracy", results[0]["trigger"])

    def test_working_too_thin(self):
        """Working file with too few words should trigger."""
        f = _write(self.tmpdir / "topic.md", _fm("working") + "\nShort.\n")
        results = trigger_depth_accuracy(f)
        self.assertEqual(len(results), 1)
        self.assertIn("word count", results[0]["reason"])

    def test_unknown_depth_skipped(self):
        """File with unrecognized depth should not trigger."""
        f = _write(self.tmpdir / "topic.md",
                   "---\nsources:\n  - https://example.com\nlast_validated: 2024-01-01\nrelevance: core\ndepth: custom\n---\nContent\n")
        self.assertEqual(trigger_depth_accuracy(f), [])

    def test_context_includes_metrics(self):
        """Context should include word_count, prose_ratio, and expected ranges."""
        prose = " ".join(["word"] * 1000)
        f = _write(self.tmpdir / "topic.md", _fm("overview") + f"\n{prose}\n")
        results = trigger_depth_accuracy(f)
        ctx = results[0]["context"]
        self.assertIn("declared_depth", ctx)
        self.assertIn("word_count", ctx)
        self.assertIn("prose_ratio", ctx)
        self.assertIn("expected_word_range", ctx)
        self.assertIn("expected_prose_range", ctx)


# ======================================================================
# TestTriggerSourcePrimacy
# ======================================================================


class TestTriggerSourcePrimacy(unittest.TestCase):
    """Tests for trigger_source_primacy."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_well_cited_no_trigger(self):
        """Working file with sufficient inline sources should not trigger."""
        body = (
            "## Key Guidance\n"
            "- Do this [source](https://example.com/1)\n"
            "- Do that [source](https://example.com/2)\n"
            "- Also this [ref](https://example.com/3)\n"
        )
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        self.assertEqual(trigger_source_primacy(f), [])

    def test_low_citation_density_triggers(self):
        """Working file with few sources relative to recommendations should trigger."""
        body = (
            "## Key Guidance\n"
            "- Recommendation one\n"
            "- Recommendation two\n"
            "- Recommendation three\n"
            "- Recommendation four\n"
            "- Recommendation five\n"
            "- Recommendation six\n"
        )
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        results = trigger_source_primacy(f)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["trigger"], "source_primacy")

    def test_only_working_depth(self):
        """Non-working depth files should not trigger."""
        body = "## Key Guidance\n- Rec one\n- Rec two\n- Rec three\n- Rec four\n"
        f = _write(self.tmpdir / "topic.md", _fm("overview") + body)
        self.assertEqual(trigger_source_primacy(f), [])

    def test_context_includes_counts(self):
        """Context should include recommendation_count, inline_source_count, ratio."""
        body = (
            "## Key Guidance\n"
            "- Recommendation one\n"
            "- Recommendation two\n"
            "- Recommendation three\n"
        )
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        results = trigger_source_primacy(f)
        self.assertEqual(len(results), 1)
        ctx = results[0]["context"]
        self.assertEqual(ctx["recommendation_count"], 3)
        self.assertEqual(ctx["inline_source_count"], 0)
        self.assertIn("sections_checked", ctx)


# ======================================================================
# TestTriggerWhyQuality
# ======================================================================


class TestTriggerWhyQuality(unittest.TestCase):
    """Tests for trigger_why_quality."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_substantial_section_no_trigger(self):
        """Working file with adequate Why This Matters should not trigger."""
        why_text = " ".join(["reason"] * 60)
        body = f"## Why This Matters\n{why_text}\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        self.assertEqual(trigger_why_quality(f), [])

    def test_thin_section_triggers(self):
        """Working file with too-short Why This Matters should trigger."""
        body = "## Why This Matters\nBrief.\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        results = trigger_why_quality(f)
        self.assertEqual(len(results), 1)
        self.assertIn("words", results[0]["reason"])

    def test_missing_section_triggers(self):
        """Working file without Why This Matters should trigger."""
        body = "## Key Guidance\n- Do stuff\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        results = trigger_why_quality(f)
        self.assertEqual(len(results), 1)
        self.assertIn("Missing", results[0]["reason"])

    def test_only_working_depth(self):
        """Non-working depth files should not trigger."""
        body = "## Some Section\nContent.\n"
        f = _write(self.tmpdir / "topic.md", _fm("overview") + body)
        self.assertEqual(trigger_why_quality(f), [])

    def test_context_includes_word_count(self):
        """Context should include has_section, word_count, min_required."""
        body = "## Why This Matters\nShort.\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        results = trigger_why_quality(f)
        ctx = results[0]["context"]
        self.assertIn("has_section", ctx)
        self.assertTrue(ctx["has_section"])
        self.assertIn("word_count", ctx)
        self.assertIn("min_required", ctx)


# ======================================================================
# TestTriggerConcreteExamples
# ======================================================================


class TestTriggerConcreteExamples(unittest.TestCase):
    """Tests for trigger_concrete_examples."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_code_block_present_no_trigger(self):
        """In Practice with code block should not trigger."""
        body = "## In Practice\nHere's an example:\n```python\nprint('hello')\n```\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        self.assertEqual(trigger_concrete_examples(f), [])

    def test_table_present_no_trigger(self):
        """In Practice with table should not trigger."""
        body = "## In Practice\n| Col1 | Col2 |\n|------|------|\n| a | b |\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        self.assertEqual(trigger_concrete_examples(f), [])

    def test_numeric_example_no_trigger(self):
        """In Practice with numeric data should not trigger."""
        body = "## In Practice\nTypically costs around $500 per campaign.\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        self.assertEqual(trigger_concrete_examples(f), [])

    def test_no_concrete_elements_triggers(self):
        """In Practice with only prose should trigger."""
        body = "## In Practice\nDo the thing well. Be good at it.\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        results = trigger_concrete_examples(f)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["trigger"], "concrete_examples")

    def test_missing_section_triggers(self):
        """Working file without In Practice should trigger."""
        body = "## Key Guidance\n- Stuff\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        results = trigger_concrete_examples(f)
        self.assertEqual(len(results), 1)
        self.assertIn("Missing", results[0]["reason"])

    def test_only_working_depth(self):
        """Non-working depth files should not trigger."""
        body = "## In Practice\nGeneric.\n"
        f = _write(self.tmpdir / "topic.md", _fm("overview") + body)
        self.assertEqual(trigger_concrete_examples(f), [])

    def test_context_flags(self):
        """Context should include all boolean flags and section_word_count."""
        body = "## In Practice\nGeneric text without concrete elements.\n"
        f = _write(self.tmpdir / "topic.md", _fm("working") + body)
        results = trigger_concrete_examples(f)
        ctx = results[0]["context"]
        self.assertIn("has_section", ctx)
        self.assertTrue(ctx["has_section"])
        self.assertFalse(ctx["has_code_block"])
        self.assertFalse(ctx["has_table"])
        self.assertFalse(ctx["has_numeric_example"])
        self.assertIn("section_word_count", ctx)


if __name__ == "__main__":
    unittest.main()
