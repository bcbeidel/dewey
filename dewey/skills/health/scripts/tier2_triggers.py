"""Tier 2 deterministic trigger functions for LLM-assisted health assessment.

Each trigger identifies files that need LLM evaluation and returns structured
context so Claude's assessment is focused and efficient.  Triggers fire based
on deterministic conditions; the actual quality judgment happens in Tier 2.

Every trigger returns a list of dicts::

    {"file": str, "trigger": str, "reason": str, "context": dict}

Only stdlib is used.  No network requests are made.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from validators import parse_frontmatter

# ------------------------------------------------------------------
# Depth-based expected ranges
# ------------------------------------------------------------------

DEPTH_WORD_RANGES: dict[str, tuple[int, int]] = {
    "overview": (50, 800),
    "working": (200, 3000),
    "reference": (20, 500),
}

DEPTH_PROSE_RANGES: dict[str, tuple[float, float]] = {
    "overview": (0.3, 0.9),
    "working": (0.3, 0.8),
    "reference": (0.0, 0.5),
}

# ------------------------------------------------------------------
# Shared helpers (module-internal)
# ------------------------------------------------------------------


def _body_without_frontmatter(text: str) -> str:
    """Strip content between first two ``---`` lines."""
    lines = text.split("\n")
    delimiter_count = 0
    start = 0
    for idx, line in enumerate(lines):
        if line.strip() == "---":
            delimiter_count += 1
            if delimiter_count == 2:
                start = idx + 1
                break
    if delimiter_count < 2:
        return text
    return "\n".join(lines[start:])


def _extract_section(body: str, heading: str) -> str | None:
    """Extract text between ``## <heading>`` and next ``## `` (or EOF).

    Uses case-insensitive substring match on *heading*, matching the
    convention in ``check_section_ordering`` (e.g. ``"In Practice" in h``).
    """
    lines = body.split("\n")
    capturing = False
    section_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if capturing:
                break
            heading_text = line[3:].strip()
            if heading.lower() in heading_text.lower():
                capturing = True
                continue
        elif capturing:
            section_lines.append(line)

    if not section_lines and not capturing:
        return None
    return "\n".join(section_lines)


def _count_words(text: str) -> int:
    """Count words via simple split."""
    return len(text.split())


def _compute_prose_ratio(body: str) -> float:
    """Ratio of prose lines to total non-blank lines.

    Non-prose lines: headings (``#``), list items (``- `` / ``* `` / ``1. ``),
    code fences (`` ``` ``), table rows (``|``), blank lines.
    """
    lines = body.split("\n")
    non_blank = [l for l in lines if l.strip()]
    if not non_blank:
        return 0.0

    prose_count = 0
    for line in non_blank:
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped.startswith(("- ", "* ")) or re.match(r"^\d+\.\s", stripped):
            continue
        if stripped.startswith("```"):
            continue
        if stripped.startswith("|"):
            continue
        prose_count += 1

    return prose_count / len(non_blank)


def _extract_source_urls(fm: dict) -> list[str]:
    """Extract URLs from frontmatter sources, handling both bare and structured format."""
    sources = fm.get("sources")
    if not isinstance(sources, list):
        return []

    urls: list[str] = []
    for entry in sources:
        url = str(entry).strip()
        # Handle structured format: "url: https://..." from YAML dicts
        if url.startswith("url:"):
            url = url[4:].strip()
        if url.startswith(("http://", "https://")):
            urls.append(url)
    return urls


# ------------------------------------------------------------------
# Trigger functions
# ------------------------------------------------------------------


def trigger_source_drift(file_path: Path, max_age_days: int = 90) -> list[dict]:
    """Trigger when ``last_validated`` is missing or older than *max_age_days*.

    Context includes source URLs so the LLM can fetch and compare.
    """
    results: list[dict] = []
    name = str(file_path)
    fm = parse_frontmatter(file_path)

    last_validated = fm.get("last_validated")
    source_urls = _extract_source_urls(fm)

    if not last_validated:
        results.append({
            "file": name,
            "trigger": "source_drift",
            "reason": "Missing last_validated date — cannot determine content age",
            "context": {
                "last_validated": None,
                "age_days": None,
                "source_urls": source_urls,
            },
        })
        return results

    try:
        validated_date = date.fromisoformat(str(last_validated))
    except ValueError:
        results.append({
            "file": name,
            "trigger": "source_drift",
            "reason": f"Invalid last_validated date: {last_validated}",
            "context": {
                "last_validated": str(last_validated),
                "age_days": None,
                "source_urls": source_urls,
            },
        })
        return results

    age_days = (date.today() - validated_date).days
    if age_days > max_age_days:
        results.append({
            "file": name,
            "trigger": "source_drift",
            "reason": f"Content is {age_days} days old (threshold: {max_age_days})",
            "context": {
                "last_validated": str(last_validated),
                "age_days": age_days,
                "source_urls": source_urls,
            },
        })

    return results


def trigger_depth_accuracy(file_path: Path) -> list[dict]:
    """Trigger when word count or prose ratio is outside expected range for depth."""
    results: list[dict] = []
    name = str(file_path)
    fm = parse_frontmatter(file_path)
    depth = fm.get("depth")

    if depth not in DEPTH_WORD_RANGES:
        return results

    text = file_path.read_text()
    body = _body_without_frontmatter(text)
    word_count = _count_words(body)
    prose_ratio = _compute_prose_ratio(body)

    word_lo, word_hi = DEPTH_WORD_RANGES[depth]
    prose_lo, prose_hi = DEPTH_PROSE_RANGES[depth]

    word_ok = word_lo <= word_count <= word_hi
    prose_ok = prose_lo <= prose_ratio <= prose_hi

    if not word_ok or not prose_ok:
        reasons = []
        if not word_ok:
            reasons.append(
                f"word count {word_count} outside [{word_lo}, {word_hi}]"
            )
        if not prose_ok:
            reasons.append(
                f"prose ratio {prose_ratio:.2f} outside [{prose_lo}, {prose_hi}]"
            )

        results.append({
            "file": name,
            "trigger": "depth_accuracy",
            "reason": f"Depth '{depth}' mismatch: {'; '.join(reasons)}",
            "context": {
                "declared_depth": depth,
                "word_count": word_count,
                "prose_ratio": round(prose_ratio, 3),
                "expected_word_range": [word_lo, word_hi],
                "expected_prose_range": [prose_lo, prose_hi],
            },
        })

    return results


def trigger_source_primacy(file_path: Path) -> list[dict]:
    """Trigger when inline source references are sparse relative to recommendations.

    Working-depth only.  Fires when external markdown links < 1 per 3
    recommendation items in "Key Guidance" and "Watch Out For" sections.
    """
    results: list[dict] = []
    name = str(file_path)
    fm = parse_frontmatter(file_path)

    if fm.get("depth") != "working":
        return results

    text = file_path.read_text()
    body = _body_without_frontmatter(text)

    sections_checked: list[str] = []
    recommendation_count = 0
    inline_source_count = 0

    for section_name in ("Key Guidance", "Watch Out For"):
        section = _extract_section(body, section_name)
        if section is None:
            continue
        sections_checked.append(section_name)

        # Count recommendation items (list items starting with - or *)
        items = re.findall(r"^[\s]*[-*]\s+", section, re.MULTILINE)
        recommendation_count += len(items)

        # Count external markdown links
        links = re.findall(r"\[([^\]]*)\]\((https?://[^)]+)\)", section)
        inline_source_count += len(links)

    if not sections_checked or recommendation_count == 0:
        return results

    # Threshold: at least 1 source per 3 recommendations
    expected = recommendation_count / 3.0
    if inline_source_count < expected:
        results.append({
            "file": name,
            "trigger": "source_primacy",
            "reason": (
                f"{inline_source_count} inline sources for "
                f"{recommendation_count} recommendations "
                f"(expect >= 1 per 3)"
            ),
            "context": {
                "recommendation_count": recommendation_count,
                "inline_source_count": inline_source_count,
                "ratio": round(
                    inline_source_count / recommendation_count, 2
                )
                if recommendation_count
                else 0,
                "sections_checked": sections_checked,
            },
        })

    return results


def trigger_why_quality(file_path: Path, min_words: int = 50) -> list[dict]:
    """Trigger when "Why This Matters" section is missing or too thin.

    Working-depth only.
    """
    results: list[dict] = []
    name = str(file_path)
    fm = parse_frontmatter(file_path)

    if fm.get("depth") != "working":
        return results

    text = file_path.read_text()
    body = _body_without_frontmatter(text)
    section = _extract_section(body, "Why This Matters")

    has_section = section is not None
    word_count = _count_words(section) if section else 0

    if not has_section or word_count < min_words:
        results.append({
            "file": name,
            "trigger": "why_quality",
            "reason": (
                "Missing 'Why This Matters' section"
                if not has_section
                else f"'Why This Matters' has {word_count} words (min: {min_words})"
            ),
            "context": {
                "has_section": has_section,
                "word_count": word_count,
                "min_required": min_words,
            },
        })

    return results


def trigger_concrete_examples(file_path: Path) -> list[dict]:
    """Trigger when "In Practice" section lacks concrete elements.

    Working-depth only.  Checks for code blocks, tables, or numeric examples.
    """
    results: list[dict] = []
    name = str(file_path)
    fm = parse_frontmatter(file_path)

    if fm.get("depth") != "working":
        return results

    text = file_path.read_text()
    body = _body_without_frontmatter(text)
    section = _extract_section(body, "In Practice")

    has_section = section is not None

    if not has_section:
        results.append({
            "file": name,
            "trigger": "concrete_examples",
            "reason": "Missing 'In Practice' section",
            "context": {
                "has_section": False,
                "has_code_block": False,
                "has_table": False,
                "has_numeric_example": False,
                "section_word_count": 0,
            },
        })
        return results

    has_code_block = "```" in section
    has_table = bool(re.search(r"^\s*\|", section, re.MULTILINE))
    has_numeric_example = bool(re.search(r"\d+(\.\d+)?%|\$\d|\d{2,}", section))
    section_word_count = _count_words(section)

    if not has_code_block and not has_table and not has_numeric_example:
        results.append({
            "file": name,
            "trigger": "concrete_examples",
            "reason": "No concrete elements (code blocks, tables, or numeric examples) in 'In Practice'",
            "context": {
                "has_section": True,
                "has_code_block": has_code_block,
                "has_table": has_table,
                "has_numeric_example": has_numeric_example,
                "section_word_count": section_word_count,
            },
        })

    return results
