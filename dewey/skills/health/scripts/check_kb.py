"""Health check runner for the knowledge base.

Discovers all .md files under docs/ (excluding _proposals/),
runs Tier 1 deterministic validators on each, and returns a
structured report.

Only stdlib is used.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# config.py lives in init/scripts/ — add it to sys.path for cross-skill import.
_init_scripts = str(Path(__file__).resolve().parent.parent.parent / "init" / "scripts")
if _init_scripts not in sys.path:
    sys.path.insert(0, _init_scripts)

from config import read_knowledge_dir
from tier2_triggers import (
    trigger_concrete_examples,
    trigger_depth_accuracy,
    trigger_source_drift,
    trigger_source_primacy,
    trigger_why_quality,
)
from validators import (
    check_coverage,
    check_cross_references,
    check_freshness,
    check_frontmatter,
    check_section_ordering,
    check_size_bounds,
    check_source_urls,
)


def _discover_md_files(kb_root: Path, knowledge_dir_name: str = "docs") -> list[Path]:
    """Return all .md files under the knowledge directory, excluding _proposals/."""
    knowledge_dir = kb_root / knowledge_dir_name
    if not knowledge_dir.is_dir():
        return []

    md_files: list[Path] = []
    for md_file in sorted(knowledge_dir.rglob("*.md")):
        # Skip files inside directories that start with _
        parts = md_file.relative_to(knowledge_dir).parts
        if any(part.startswith("_") for part in parts):
            continue
        md_files.append(md_file)

    return md_files


def run_health_check(kb_root: Path) -> dict:
    """Run all Tier 1 validators and return a structured report.

    Parameters
    ----------
    kb_root:
        Root directory containing the ``docs/`` folder.

    Returns
    -------
    dict
        ``{"issues": [...], "summary": {...}}``
    """
    knowledge_dir_name = read_knowledge_dir(kb_root)
    all_issues: list[dict] = []
    md_files = _discover_md_files(kb_root, knowledge_dir_name)

    # Per-file validators
    for md_file in md_files:
        all_issues.extend(check_frontmatter(md_file))
        all_issues.extend(check_section_ordering(md_file))
        all_issues.extend(check_cross_references(md_file, kb_root))
        all_issues.extend(check_size_bounds(md_file))
        all_issues.extend(check_source_urls(md_file))
        all_issues.extend(check_freshness(md_file))

    # Structural validators (run once)
    all_issues.extend(check_coverage(kb_root, knowledge_dir_name=knowledge_dir_name))

    # Build summary
    files_with_fails = set()
    files_with_warns = set()
    all_mentioned_files = set()

    for issue in all_issues:
        f = issue.get("file", "")
        all_mentioned_files.add(f)
        if issue["severity"] == "fail":
            files_with_fails.add(f)
        elif issue["severity"] == "warn":
            files_with_warns.add(f)

    fail_count = sum(1 for i in all_issues if i["severity"] == "fail")
    warn_count = sum(1 for i in all_issues if i["severity"] == "warn")

    return {
        "issues": all_issues,
        "summary": {
            "total_files": len(md_files),
            "fail_count": fail_count,
            "warn_count": warn_count,
            "pass_count": len(md_files) - len(files_with_fails),
        },
    }


_TIER2_TRIGGERS = [
    trigger_source_drift,
    trigger_depth_accuracy,
    trigger_source_primacy,
    trigger_why_quality,
    trigger_concrete_examples,
]


def run_tier2_prescreening(kb_root: Path) -> dict:
    """Run all Tier 2 deterministic triggers and return a structured queue.

    Parameters
    ----------
    kb_root:
        Root directory containing the ``docs/`` folder.

    Returns
    -------
    dict
        ``{"queue": [...], "summary": {...}}``
    """
    knowledge_dir_name = read_knowledge_dir(kb_root)
    md_files = _discover_md_files(kb_root, knowledge_dir_name)

    queue: list[dict] = []
    trigger_counts: dict[str, int] = {}

    for md_file in md_files:
        for trigger_fn in _TIER2_TRIGGERS:
            for item in trigger_fn(md_file):
                queue.append(item)
                t = item["trigger"]
                trigger_counts[t] = trigger_counts.get(t, 0) + 1

    files_with_triggers = len({item["file"] for item in queue})

    return {
        "queue": queue,
        "summary": {
            "total_files_scanned": len(md_files),
            "files_with_triggers": files_with_triggers,
            "trigger_counts": trigger_counts,
        },
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run knowledge base health checks.")
    parser.add_argument(
        "--kb-root",
        required=True,
        help="Root directory containing the docs/ folder.",
    )
    parser.add_argument(
        "--tier2",
        action="store_true",
        help="Run Tier 2 pre-screening instead of Tier 1 checks.",
    )
    args = parser.parse_args()

    kb_path = Path(args.kb_root)
    if args.tier2:
        report = run_tier2_prescreening(kb_path)
    else:
        report = run_health_check(kb_path)
    print(json.dumps(report, indent=2))
