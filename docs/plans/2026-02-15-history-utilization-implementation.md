# History & Utilization Tracking Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add health score history (baselines over time) and utilization tracking (which topics get referenced) to the Dewey health skill.

**Architecture:** Two new stdlib-only Python modules (`history.py`, `utilization.py`) with append-only JSONL storage in `.dewey/history/` and `.dewey/utilization/`. Integrated into `check_kb.py` (auto-snapshot) and health workflows (reference tracking, trend display).

**Tech Stack:** Python 3.9+ (stdlib only), JSONL files, unittest

**Design Doc:** `docs/plans/2026-02-15-history-utilization-design.md`

---

### Task 1: Create history.py with record_snapshot

**Files:**
- Create: `dewey/skills/health/scripts/history.py`
- Create: `tests/skills/health/test_history.py`

**Step 1: Write the failing tests**

```python
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
    """Tests for record_snapshot."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / ".dewey" / "history").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_log_file(self):
        """First snapshot should create health-log.jsonl."""
        record_snapshot(self.tmpdir, _tier1_summary(), _tier2_summary())
        log = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        self.assertTrue(log.exists())

    def test_appends_valid_json_line(self):
        """Each snapshot should be a single valid JSON line."""
        record_snapshot(self.tmpdir, _tier1_summary(), _tier2_summary())
        log = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        lines = log.read_text().strip().split("\n")
        self.assertEqual(len(lines), 1)
        entry = json.loads(lines[0])
        self.assertIn("timestamp", entry)
        self.assertIn("tier1", entry)
        self.assertIn("tier2", entry)

    def test_multiple_snapshots_append(self):
        """Multiple calls should append, not overwrite."""
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=3), _tier2_summary())
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=1), _tier2_summary())
        log = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        lines = log.read_text().strip().split("\n")
        self.assertEqual(len(lines), 2)
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        self.assertEqual(first["tier1"]["fail_count"], 3)
        self.assertEqual(second["tier1"]["fail_count"], 1)

    def test_snapshot_includes_summaries(self):
        """Snapshot should contain the exact tier1 and tier2 summaries passed in."""
        t1 = _tier1_summary(fail_count=2, warn_count=3)
        t2 = _tier2_summary(trigger_counts={"depth_accuracy": 4}, files_with_triggers=3)
        record_snapshot(self.tmpdir, t1, t2)
        log = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        entry = json.loads(log.read_text().strip())
        self.assertEqual(entry["tier1"], t1)
        self.assertEqual(entry["tier2"], t2)

    def test_creates_directory_if_missing(self):
        """Should create .dewey/history/ if it doesn't exist."""
        fresh = Path(tempfile.mkdtemp())
        try:
            record_snapshot(fresh, _tier1_summary(), _tier2_summary())
            log = fresh / ".dewey" / "history" / "health-log.jsonl"
            self.assertTrue(log.exists())
        finally:
            shutil.rmtree(fresh)

    def test_tier2_summary_optional(self):
        """tier2_summary=None should store null for tier2."""
        record_snapshot(self.tmpdir, _tier1_summary(), None)
        log = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        entry = json.loads(log.read_text().strip())
        self.assertIsNone(entry["tier2"])


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/skills/health/test_history.py -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
"""Health score history tracking.

Persists timestamped snapshots of health check summaries to
``.dewey/history/health-log.jsonl`` so trends can be displayed.

Only stdlib is used.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def record_snapshot(
    kb_root: Path,
    tier1_summary: dict,
    tier2_summary: Optional[dict] = None,
) -> Path:
    """Append a health check snapshot to the history log.

    Parameters
    ----------
    kb_root:
        Root directory of the knowledge base.
    tier1_summary:
        Summary dict from ``run_health_check``.
    tier2_summary:
        Summary dict from ``run_tier2_prescreening``, or ``None``.

    Returns
    -------
    Path
        Path to the log file.
    """
    log_dir = kb_root / ".dewey" / "history"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "health-log.jsonl"

    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tier1": tier1_summary,
        "tier2": tier2_summary,
    }

    with log_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    return log_file
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/skills/health/test_history.py -v`
Expected: 6 passed

**Step 5: Commit**

```bash
git add dewey/skills/health/scripts/history.py tests/skills/health/test_history.py
git commit -m "Add history.py with record_snapshot for health score baselines"
```

---

### Task 2: Add read_history to history.py

**Files:**
- Modify: `dewey/skills/health/scripts/history.py`
- Modify: `tests/skills/health/test_history.py`

**Step 1: Write the failing tests**

Add to `test_history.py`:

```python
class TestReadHistory(unittest.TestCase):
    """Tests for read_history."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / ".dewey" / "history").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_empty_history(self):
        """No log file should return empty list."""
        result = read_history(self.tmpdir)
        self.assertEqual(result, [])

    def test_returns_snapshots_in_order(self):
        """Should return snapshots in chronological order."""
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=5), None)
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=3), None)
        record_snapshot(self.tmpdir, _tier1_summary(fail_count=1), None)
        result = read_history(self.tmpdir)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["tier1"]["fail_count"], 5)
        self.assertEqual(result[2]["tier1"]["fail_count"], 1)

    def test_limit_parameter(self):
        """limit=N should return only the last N snapshots."""
        for i in range(5):
            record_snapshot(self.tmpdir, _tier1_summary(fail_count=i), None)
        result = read_history(self.tmpdir, limit=2)
        self.assertEqual(len(result), 2)
        # Last two: fail_count 3 and 4
        self.assertEqual(result[0]["tier1"]["fail_count"], 3)
        self.assertEqual(result[1]["tier1"]["fail_count"], 4)

    def test_limit_larger_than_history(self):
        """limit larger than available snapshots returns all."""
        record_snapshot(self.tmpdir, _tier1_summary(), None)
        result = read_history(self.tmpdir, limit=100)
        self.assertEqual(len(result), 1)

    def test_each_entry_has_expected_keys(self):
        """Every entry should have timestamp, tier1, tier2."""
        record_snapshot(self.tmpdir, _tier1_summary(), _tier2_summary())
        result = read_history(self.tmpdir)
        entry = result[0]
        self.assertIn("timestamp", entry)
        self.assertIn("tier1", entry)
        self.assertIn("tier2", entry)
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/skills/health/test_history.py::TestReadHistory -v`
Expected: FAIL (function exists from import but not implemented)

**Step 3: Write minimal implementation**

Add to `history.py`:

```python
def read_history(kb_root: Path, limit: int = 10) -> list[dict]:
    """Read the last *limit* health check snapshots.

    Parameters
    ----------
    kb_root:
        Root directory of the knowledge base.
    limit:
        Maximum number of snapshots to return.

    Returns
    -------
    list[dict]
        Snapshots in chronological order (oldest first).
    """
    log_file = kb_root / ".dewey" / "history" / "health-log.jsonl"
    if not log_file.exists():
        return []

    lines = log_file.read_text().strip().split("\n")
    if not lines or lines == [""]:
        return []

    entries = [json.loads(line) for line in lines]
    return entries[-limit:]
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/skills/health/test_history.py -v`
Expected: 11 passed (6 + 5 new)

**Step 5: Commit**

```bash
git add dewey/skills/health/scripts/history.py tests/skills/health/test_history.py
git commit -m "Add read_history for retrieving health score trend data"
```

---

### Task 3: Create utilization.py with record_reference

**Files:**
- Create: `dewey/skills/health/scripts/utilization.py`
- Create: `tests/skills/health/test_utilization.py`

**Step 1: Write the failing tests**

```python
"""Tests for skills.health.scripts.utilization — reference tracking."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from utilization import record_reference, read_utilization


class TestRecordReference(unittest.TestCase):
    """Tests for record_reference."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / ".dewey" / "utilization").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_log_file(self):
        """First reference should create log.jsonl."""
        record_reference(self.tmpdir, "docs/topic.md")
        log = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        self.assertTrue(log.exists())

    def test_appends_valid_json_line(self):
        """Each reference should be a single valid JSON line."""
        record_reference(self.tmpdir, "docs/topic.md")
        log = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        lines = log.read_text().strip().split("\n")
        self.assertEqual(len(lines), 1)
        entry = json.loads(lines[0])
        self.assertIn("file", entry)
        self.assertIn("timestamp", entry)
        self.assertIn("context", entry)

    def test_default_context_is_user(self):
        """Default context should be 'user'."""
        record_reference(self.tmpdir, "docs/topic.md")
        log = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        entry = json.loads(log.read_text().strip())
        self.assertEqual(entry["context"], "user")

    def test_custom_context(self):
        """Custom context should be recorded."""
        record_reference(self.tmpdir, "docs/topic.md", context="audit")
        log = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        entry = json.loads(log.read_text().strip())
        self.assertEqual(entry["context"], "audit")

    def test_multiple_references_append(self):
        """Multiple calls should append, not overwrite."""
        record_reference(self.tmpdir, "docs/a.md")
        record_reference(self.tmpdir, "docs/b.md")
        log = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        lines = log.read_text().strip().split("\n")
        self.assertEqual(len(lines), 2)

    def test_creates_directory_if_missing(self):
        """Should create .dewey/utilization/ if it doesn't exist."""
        fresh = Path(tempfile.mkdtemp())
        try:
            record_reference(fresh, "docs/topic.md")
            log = fresh / ".dewey" / "utilization" / "log.jsonl"
            self.assertTrue(log.exists())
        finally:
            shutil.rmtree(fresh)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/skills/health/test_utilization.py -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
"""Utilization tracking for knowledge base topics.

Records when knowledge base files are referenced so health reviews
can surface underused content.  Append-only JSONL log in
``.dewey/utilization/log.jsonl``.

Only stdlib is used.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def record_reference(
    kb_root: Path,
    file_path: str,
    context: str = "user",
) -> Path:
    """Record that a knowledge base file was referenced.

    Parameters
    ----------
    kb_root:
        Root directory of the knowledge base.
    file_path:
        Relative path to the referenced file (e.g. ``docs/topic.md``).
    context:
        How the reference happened (``user``, ``audit``, ``curate``).

    Returns
    -------
    Path
        Path to the log file.
    """
    log_dir = kb_root / ".dewey" / "utilization"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "log.jsonl"

    entry = {
        "file": file_path,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "context": context,
    }

    with log_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    return log_file
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/skills/health/test_utilization.py -v`
Expected: 6 passed

**Step 5: Commit**

```bash
git add dewey/skills/health/scripts/utilization.py tests/skills/health/test_utilization.py
git commit -m "Add utilization.py with record_reference for topic tracking"
```

---

### Task 4: Add read_utilization to utilization.py

**Files:**
- Modify: `dewey/skills/health/scripts/utilization.py`
- Modify: `tests/skills/health/test_utilization.py`

**Step 1: Write the failing tests**

Add to `test_utilization.py`:

```python
class TestReadUtilization(unittest.TestCase):
    """Tests for read_utilization."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / ".dewey" / "utilization").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_empty_log(self):
        """No log file should return empty dict."""
        result = read_utilization(self.tmpdir)
        self.assertEqual(result, {})

    def test_single_reference(self):
        """One reference should produce one entry with count=1."""
        record_reference(self.tmpdir, "docs/topic.md")
        result = read_utilization(self.tmpdir)
        self.assertIn("docs/topic.md", result)
        self.assertEqual(result["docs/topic.md"]["count"], 1)

    def test_multiple_references_same_file(self):
        """Multiple references to same file should increment count."""
        record_reference(self.tmpdir, "docs/topic.md")
        record_reference(self.tmpdir, "docs/topic.md")
        record_reference(self.tmpdir, "docs/topic.md")
        result = read_utilization(self.tmpdir)
        self.assertEqual(result["docs/topic.md"]["count"], 3)

    def test_multiple_files(self):
        """Different files should have separate entries."""
        record_reference(self.tmpdir, "docs/a.md")
        record_reference(self.tmpdir, "docs/b.md")
        result = read_utilization(self.tmpdir)
        self.assertEqual(len(result), 2)
        self.assertIn("docs/a.md", result)
        self.assertIn("docs/b.md", result)

    def test_includes_last_referenced(self):
        """Each entry should include last_referenced timestamp."""
        record_reference(self.tmpdir, "docs/topic.md")
        result = read_utilization(self.tmpdir)
        self.assertIn("last_referenced", result["docs/topic.md"])

    def test_includes_first_referenced(self):
        """Each entry should include first_referenced timestamp."""
        record_reference(self.tmpdir, "docs/topic.md")
        result = read_utilization(self.tmpdir)
        self.assertIn("first_referenced", result["docs/topic.md"])

    def test_last_referenced_is_latest(self):
        """last_referenced should be the most recent timestamp."""
        record_reference(self.tmpdir, "docs/topic.md")
        record_reference(self.tmpdir, "docs/topic.md")
        result = read_utilization(self.tmpdir)
        stats = result["docs/topic.md"]
        self.assertGreaterEqual(stats["last_referenced"], stats["first_referenced"])
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/skills/health/test_utilization.py::TestReadUtilization -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Add to `utilization.py`:

```python
def read_utilization(kb_root: Path) -> dict[str, dict]:
    """Read utilization stats per file.

    Parameters
    ----------
    kb_root:
        Root directory of the knowledge base.

    Returns
    -------
    dict[str, dict]
        Mapping of file path to ``{"count": int,
        "first_referenced": str, "last_referenced": str}``.
    """
    log_file = kb_root / ".dewey" / "utilization" / "log.jsonl"
    if not log_file.exists():
        return {}

    lines = log_file.read_text().strip().split("\n")
    if not lines or lines == [""]:
        return {}

    stats: dict[str, dict] = {}
    for line in lines:
        entry = json.loads(line)
        fp = entry["file"]
        ts = entry["timestamp"]

        if fp not in stats:
            stats[fp] = {
                "count": 0,
                "first_referenced": ts,
                "last_referenced": ts,
            }

        stats[fp]["count"] += 1
        if ts < stats[fp]["first_referenced"]:
            stats[fp]["first_referenced"] = ts
        if ts > stats[fp]["last_referenced"]:
            stats[fp]["last_referenced"] = ts

    return stats
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/skills/health/test_utilization.py -v`
Expected: 13 passed (6 + 7 new)

**Step 5: Commit**

```bash
git add dewey/skills/health/scripts/utilization.py tests/skills/health/test_utilization.py
git commit -m "Add read_utilization for per-file reference stats"
```

---

### Task 5: Integrate history snapshots into check_kb.py

Auto-persist a snapshot after each health check run.

**Files:**
- Modify: `dewey/skills/health/scripts/check_kb.py`
- Modify: `tests/skills/health/test_check_kb.py`

**Step 1: Write the failing test**

Add to `test_check_kb.py`:

```python
class TestHistoryIntegration(unittest.TestCase):
    """Tests for automatic history snapshot persistence."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.kb = self.tmpdir / "docs"
        self.kb.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_tier1_persists_snapshot(self):
        """run_health_check should persist a history snapshot."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        run_health_check(self.tmpdir)
        log = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        self.assertTrue(log.exists())
        entry = json.loads(log.read_text().strip())
        self.assertIn("tier1", entry)
        self.assertIsNone(entry["tier2"])

    def test_combined_persists_snapshot(self):
        """run_combined_report should persist a snapshot with both tiers."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        run_combined_report(self.tmpdir)
        log = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        self.assertTrue(log.exists())
        entry = json.loads(log.read_text().strip())
        self.assertIn("tier1", entry)
        self.assertIsNotNone(entry["tier2"])

    def test_tier2_persists_snapshot(self):
        """run_tier2_prescreening should persist a snapshot."""
        area = self.kb / "area-one"
        area.mkdir()
        _write(area / "overview.md", _valid_md("overview"))
        run_tier2_prescreening(self.tmpdir)
        log = self.tmpdir / ".dewey" / "history" / "health-log.jsonl"
        self.assertTrue(log.exists())
        entry = json.loads(log.read_text().strip())
        self.assertIsNone(entry["tier1"])
        self.assertIn("tier2", entry)
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/skills/health/test_check_kb.py::TestHistoryIntegration -v`
Expected: FAIL (no snapshot is written yet)

**Step 3: Implement the integration**

Add import to `check_kb.py`:
```python
from history import record_snapshot
```

Add `import json` to test file if not already there.

Add snapshot call at end of `run_health_check`:
```python
    # Persist history snapshot
    record_snapshot(kb_root, result["summary"], None)

    return result
```

Where `result` is the dict being returned. Restructure slightly — assign to variable before returning:
```python
    result = {
        "issues": all_issues,
        "summary": { ... },
    }
    record_snapshot(kb_root, result["summary"], None)
    return result
```

Add snapshot call at end of `run_tier2_prescreening`:
```python
    result = {
        "queue": queue,
        "summary": { ... },
    }
    record_snapshot(kb_root, None, result["summary"])
    return result
```

Add snapshot call at end of `run_combined_report`:
```python
    result = {
        "tier1": run_health_check(kb_root),
        "tier2": run_tier2_prescreening(kb_root),
    }
    # run_health_check and run_tier2_prescreening each persist their own snapshots.
    # The combined report persists a combined snapshot too.
    record_snapshot(kb_root, result["tier1"]["summary"], result["tier2"]["summary"])
    return result
```

**Important:** `run_health_check` and `run_tier2_prescreening` will each write their own snapshot. When `run_combined_report` calls both, that would create 3 snapshots (one per sub-call + one combined). To avoid this, add a `_persist_history` parameter defaulting to `True`:

```python
def run_health_check(kb_root: Path, *, _persist_history: bool = True) -> dict:
    ...
    if _persist_history:
        record_snapshot(kb_root, result["summary"], None)
    return result

def run_tier2_prescreening(kb_root: Path, *, _persist_history: bool = True) -> dict:
    ...
    if _persist_history:
        record_snapshot(kb_root, None, result["summary"])
    return result

def run_combined_report(kb_root: Path) -> dict:
    result = {
        "tier1": run_health_check(kb_root, _persist_history=False),
        "tier2": run_tier2_prescreening(kb_root, _persist_history=False),
    }
    record_snapshot(kb_root, result["tier1"]["summary"], result["tier2"]["summary"])
    return result
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/skills/health/test_check_kb.py -v`
Expected: All tests pass

Run: `python3 -m pytest tests/ -v -k "not test_scaffold_sandbox"`
Expected: All tests pass (no regressions)

**Step 5: Commit**

```bash
git add dewey/skills/health/scripts/check_kb.py tests/skills/health/test_check_kb.py
git commit -m "Auto-persist history snapshot after each health check run"
```

---

### Task 6: Update SKILL.md and CLAUDE.md

**Files:**
- Modify: `dewey/skills/health/SKILL.md`
- Modify: `CLAUDE.md`

**Step 1: Update SKILL.md scripts_integration section**

Add entries for `history.py` and `utilization.py` in the `<scripts_integration>` section:

```markdown
**history.py** -- Health score history tracking
- `record_snapshot(kb_root, tier1_summary, tier2_summary)` -- Appends timestamped snapshot to `.dewey/history/health-log.jsonl`
- `read_history(kb_root, limit=10)` -- Returns the last N snapshots in chronological order
- Auto-called by `check_kb.py` after each run

**utilization.py** -- Topic reference tracking
- `record_reference(kb_root, file_path, context="user")` -- Appends to `.dewey/utilization/log.jsonl`
- `read_utilization(kb_root)` -- Returns per-file stats: `{file: {count, first_referenced, last_referenced}}`
```

**Step 2: Update CLAUDE.md status table**

Change:
```
| Utilization tracking | Infrastructure scaffolded |
| History / baselines | Infrastructure scaffolded |
```

To:
```
| Utilization tracking | Complete |
| History / baselines | Complete |
```

**Step 3: Run tests to confirm no regressions**

Run: `python3 -m pytest tests/ -v -k "not test_scaffold_sandbox"`
Expected: All tests pass

**Step 4: Commit**

```bash
git add dewey/skills/health/SKILL.md CLAUDE.md
git commit -m "Document history and utilization modules in SKILL.md and CLAUDE.md"
```

---

### Task 7: Final test run and summary

**Step 1: Run the full test suite**

Run: `python3 -m pytest tests/ -v -k "not test_scaffold_sandbox"`
Expected: All tests pass (263 original + new history + utilization tests)

**Step 2: Verify end-to-end**

```bash
python3 dewey/skills/health/scripts/check_kb.py --kb-root sandbox --both
cat sandbox/.dewey/history/health-log.jsonl
```

Verify the snapshot was written after the run.

**Step 3: Review commit history**

```bash
git log --oneline -10
```
