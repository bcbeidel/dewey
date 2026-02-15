# Tier 2 Audit Polish Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Polish the Tier 2 LLM-assisted audit flow so `/dewey:health audit` works end-to-end, and commit the CLAUDE.md created during the design phase.

**Architecture:** Workflow-driven. The Python pre-screener (`tier2_triggers.py`) produces a structured queue with context data. The `health-audit.md` workflow instructs Claude how to evaluate each item. No new scripts needed — this is workflow refinement and a test to validate the end-to-end flow.

**Tech Stack:** Python 3.9+ (stdlib only), Claude Code skills framework, Markdown workflows

**Design Doc:** `docs/plans/2026-02-15-tier2-audit-polish-design.md`

---

### Task 1: Commit CLAUDE.md and design doc

**Files:**
- Verify: `CLAUDE.md` (already created)
- Verify: `docs/plans/2026-02-15-tier2-audit-polish-design.md` (already created)

**Step 1: Review the files exist and look correct**

Read both files to verify they were written correctly.

**Step 2: Run existing tests to confirm no regressions**

Run: `python3 -m pytest tests/ -v -k "not test_scaffold_sandbox"`
Expected: 257 passed

**Step 3: Commit**

```bash
git add CLAUDE.md docs/plans/2026-02-15-tier2-audit-polish-design.md
git commit -m "Add CLAUDE.md and Tier 2 audit polish design doc"
```

---

### Task 2: Add `--tier2` output format test

Verify that `check_kb.py --tier2` produces well-structured output that the audit workflow can consume. The function exists and is lightly tested, but we need to validate the output schema more rigorously.

**Files:**
- Modify: `tests/skills/health/test_check_kb.py`

**Step 1: Write the failing test**

Add a test that validates the full shape of `run_tier2_prescreening` output — every queue item has the 4 required keys, every summary field is present, and trigger counts are consistent.

```python
class TestTier2OutputSchema(unittest.TestCase):
    """Validate the output schema of run_tier2_prescreening for workflow consumption."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.kb = self.tmpdir / "docs"
        self.kb.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_queue_item_schema(self):
        """Every queue item must have file, trigger, reason, context keys."""
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
        for item in result["queue"]:
            self.assertIn("file", item)
            self.assertIn("trigger", item)
            self.assertIn("reason", item)
            self.assertIn("context", item)
            self.assertIsInstance(item["context"], dict)

    def test_trigger_counts_match_queue(self):
        """Summary trigger_counts must match actual queue contents."""
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
        # Count triggers manually from queue
        manual_counts = {}
        for item in result["queue"]:
            t = item["trigger"]
            manual_counts[t] = manual_counts.get(t, 0) + 1
        self.assertEqual(result["summary"]["trigger_counts"], manual_counts)

    def test_valid_trigger_names(self):
        """Every trigger name must be one of the 5 known triggers."""
        area = self.kb / "area-one"
        area.mkdir()
        stale_md = (
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
            "Short content.\n"
        )
        _write(area / "topic.md", stale_md)
        result = run_tier2_prescreening(self.tmpdir)
        valid_triggers = {
            "source_drift", "depth_accuracy", "source_primacy",
            "why_quality", "concrete_examples",
        }
        for item in result["queue"]:
            self.assertIn(item["trigger"], valid_triggers,
                          f"Unknown trigger: {item['trigger']}")
```

**Step 2: Run tests to verify they pass**

These tests validate existing behavior, so they should pass immediately.

Run: `python3 -m pytest tests/skills/health/test_check_kb.py::TestTier2OutputSchema -v`
Expected: 3 passed

**Step 3: Commit**

```bash
git add tests/skills/health/test_check_kb.py
git commit -m "Add Tier 2 output schema validation tests"
```

---

### Task 3: Add `--both` flag to check_kb.py for combined Tier 1 + Tier 2 output

The audit workflow needs both Tier 1 and Tier 2 results. Currently these require two separate invocations. Add a `--both` flag that returns a combined report.

**Files:**
- Modify: `dewey/skills/health/scripts/check_kb.py`
- Modify: `tests/skills/health/test_check_kb.py`

**Step 1: Write the failing test**

```python
class TestRunCombinedReport(unittest.TestCase):
    """Tests for the run_combined_report function."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.kb = self.tmpdir / "docs"
        self.kb.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_returns_both_sections(self):
        """Combined report includes tier1 and tier2 keys."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        result = run_combined_report(self.tmpdir)
        self.assertIn("tier1", result)
        self.assertIn("tier2", result)

    def test_tier1_has_issues_and_summary(self):
        """Tier 1 section has standard structure."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        result = run_combined_report(self.tmpdir)
        self.assertIn("issues", result["tier1"])
        self.assertIn("summary", result["tier1"])

    def test_tier2_has_queue_and_summary(self):
        """Tier 2 section has standard structure."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        result = run_combined_report(self.tmpdir)
        self.assertIn("queue", result["tier2"])
        self.assertIn("summary", result["tier2"])
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/skills/health/test_check_kb.py::TestRunCombinedReport -v`
Expected: FAIL with `ImportError` (function doesn't exist yet)

**Step 3: Write minimal implementation**

Add to `check_kb.py`:

```python
def run_combined_report(kb_root: Path) -> dict:
    """Run Tier 1 + Tier 2 pre-screening and return a combined report.

    Parameters
    ----------
    kb_root:
        Root directory containing the knowledge base folder.

    Returns
    -------
    dict
        ``{"tier1": {...}, "tier2": {...}}``
    """
    return {
        "tier1": run_health_check(kb_root),
        "tier2": run_tier2_prescreening(kb_root),
    }
```

Add the `--both` flag to the argparse section:

```python
parser.add_argument(
    "--both",
    action="store_true",
    help="Run both Tier 1 checks and Tier 2 pre-screening.",
)
```

Update the `if __name__` block:

```python
if args.both:
    report = run_combined_report(kb_path)
elif args.tier2:
    report = run_tier2_prescreening(kb_path)
else:
    report = run_health_check(kb_path)
```

**Step 4: Update import in test file**

Add `run_combined_report` to the import line in `test_check_kb.py`:

```python
from check_kb import run_health_check, run_tier2_prescreening, run_combined_report
```

**Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/skills/health/test_check_kb.py -v`
Expected: All tests pass (existing + 3 new)

**Step 6: Commit**

```bash
git add dewey/skills/health/scripts/check_kb.py tests/skills/health/test_check_kb.py
git commit -m "Add combined Tier 1 + Tier 2 report function and --both flag"
```

---

### Task 4: Update health-audit.md to use --both flag

Simplify the workflow to use a single script invocation instead of two.

**Files:**
- Modify: `dewey/skills/health/workflows/health-audit.md`

**Step 1: Read the current workflow**

Read `dewey/skills/health/workflows/health-audit.md` to see current Steps 1 and 2.

**Step 2: Update Steps 1 and 2 to use --both**

Replace the two separate invocations (Step 1: `--kb-root`, Step 2: `--kb-root --tier2`) with a single combined invocation. Keep the Step 2 trigger summary table. Merge Steps 1 and 2 into a single Step 1 that runs `--both` and presents both summaries.

Update Step 1 to:

```markdown
## Step 1: Run Tier 1 checks and Tier 2 pre-screening

\`\`\`bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/health/scripts/check_kb.py --kb-root <kb_root> --both
\`\`\`

Capture the JSON output. It contains two sections:

- `tier1` -- Tier 1 deterministic check results (issues and summary)
- `tier2` -- Tier 2 pre-screener results (queue and summary)

Present the Tier 1 summary:

\`\`\`
### Tier 1: Deterministic Checks
- Total files scanned: <N>
- Passing: <N>
- Failures: <N>
- Warnings: <N>
\`\`\`

Then present the Tier 2 trigger summary:

| Trigger | Count | Description |
|---------|-------|-------------|
| source_drift | N | Files with stale or missing last_validated dates |
| depth_accuracy | N | Files where word count or prose ratio doesn't match depth |
| source_primacy | N | Working files with low inline citation density |
| why_quality | N | Working files with missing or thin "Why This Matters" |
| concrete_examples | N | Working files with missing or abstract "In Practice" |

"**Tier 2 evaluation queue:** <N> items across <M> files."
```

Remove old Step 2 and renumber subsequent steps (Step 3 becomes Step 2, etc.).

**Step 3: Verify the workflow reads clearly**

Re-read the updated file to ensure the steps flow logically and the numbering is consistent.

**Step 4: Run existing tests to confirm no regressions**

Run: `python3 -m pytest tests/ -v -k "not test_scaffold_sandbox"`
Expected: All tests pass

**Step 5: Commit**

```bash
git add dewey/skills/health/workflows/health-audit.md
git commit -m "Simplify audit workflow to use combined --both flag"
```

---

### Task 5: Update SKILL.md scripts_integration section

The SKILL.md `scripts_integration` section documents the Python scripts. Update it to mention the `--both` flag and `run_combined_report`.

**Files:**
- Modify: `dewey/skills/health/SKILL.md`

**Step 1: Read the current scripts_integration section**

Read `dewey/skills/health/SKILL.md` and find the `<scripts_integration>` block.

**Step 2: Add --both flag documentation**

After the existing `--tier2` usage example, add:

```markdown
**Combined Tier 1 + Tier 2:**
\`\`\`bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/health/scripts/check_kb.py --kb-root <kb_root> --both
\`\`\`

Returns `{"tier1": {...}, "tier2": {...}}` with both Tier 1 issues/summary and Tier 2 queue/summary.
```

Also add a brief entry for `tier2_triggers.py`:

```markdown
**tier2_triggers.py** -- Tier 2 deterministic pre-screener
- `trigger_source_drift` -- Flags files with stale or missing last_validated
- `trigger_depth_accuracy` -- Flags files where word count or prose ratio mismatches depth
- `trigger_source_primacy` -- Flags working files with low inline citation density
- `trigger_why_quality` -- Flags working files with missing or thin "Why This Matters"
- `trigger_concrete_examples` -- Flags working files with missing or abstract "In Practice"

Every trigger returns: `{"file": str, "trigger": str, "reason": str, "context": dict}`
```

**Step 3: Run tests to confirm no regressions**

Run: `python3 -m pytest tests/ -v -k "not test_scaffold_sandbox"`
Expected: All tests pass

**Step 4: Commit**

```bash
git add dewey/skills/health/SKILL.md
git commit -m "Document Tier 2 triggers and --both flag in SKILL.md"
```

---

### Task 6: End-to-end validation against sandbox KB

Run the full audit workflow manually against the sandbox KB to validate the end-to-end flow.

**Files:**
- No files created or modified (validation only)

**Step 1: Run the combined report**

```bash
python3 dewey/skills/health/scripts/check_kb.py --kb-root sandbox --both
```

Verify the output contains both `tier1` and `tier2` sections with correct structure.

**Step 2: Simulate the audit workflow**

Walk through the `health-audit.md` steps manually:

1. Parse the combined JSON output
2. Present the Tier 1 summary
3. Present the Tier 2 trigger summary table
4. For each queue item, evaluate using the pre-computed context
5. Note any workflow instructions that are unclear or produce poor results

**Step 3: Document findings**

If any friction points are found, create issues or fix them directly. If the workflow runs cleanly, note this in the commit message.

**Step 4: Update CLAUDE.md status**

Change the Tier 2 audit row from "In progress" to "Complete" in CLAUDE.md.

**Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "Mark Tier 2 audit workflow as complete after e2e validation"
```

---

### Task 7: Final test run and summary

**Step 1: Run the full test suite**

Run: `python3 -m pytest tests/ -v -k "not test_scaffold_sandbox"`
Expected: All tests pass (257 original + new tests)

**Step 2: Review all changes**

```bash
git log --oneline -10
```

Verify commit history is clean and each commit message describes its change clearly.
