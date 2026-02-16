# Deep Dive: Python-Based Knowledge Base Quality Assertions

## Strategic Summary

Dewey's existing 9 Tier 1 validators and 6 Tier 2 triggers cover 9 of 12 design principles, but three principles have no validators (#4 Collaborative Curation, #7 Right-Sized Scope, #9 Progressive Disclosure beyond index sync), and several covered principles have significant depth gaps. This research identifies 14 new Python-based validators that can be added deterministically, 5 conservative auto-corrections, and draws a clear line between what Python can assert vs. what requires LLM judgment.

## Key Questions

- Which design principles lack validator coverage, and what can Python check?
- What new deterministic checks are feasible with stdlib-only Python?
- Where can Python auto-correct conservatively without risking content damage?
- What is the bright line between Tier 1 (Python) and Tier 2 (LLM)?
- How should the existing validator architecture evolve to support this?

## Overview

The Dewey health system implements a three-tier quality model: deterministic Python checks (Tier 1), LLM-assisted evaluation (Tier 2), and human judgment (Tier 3). The current Tier 1 suite is strong on structural/metadata validation but weak on content quality heuristics. The design principles -- especially those from cognitive science (#10-12) -- are almost entirely delegated to Tier 2 triggers, when several aspects could be asserted deterministically.

The core opportunity: push the boundary of what Python can assert, auto-correct the unambiguous issues, and send only genuinely ambiguous cases to the LLM. This reduces LLM cost, increases speed, and makes the health system more useful in CI-like workflows where LLM access may not be available.

## Current State: Principle Coverage Audit

### Full Coverage Matrix

| # | Principle | Tier 1 Validators | Tier 2 Triggers | Gaps |
|---|-----------|------------------|-----------------|------|
| 1 | Source Primacy | `check_source_urls` | `trigger_source_drift`, `trigger_source_primacy`, `trigger_citation_quality` | No URL reachability check |
| 2 | Dual Audience | `check_size_bounds` | `trigger_depth_accuracy` | No readability metric |
| 3 | Three-Dimensional Quality | `check_freshness` | `trigger_source_drift` | Meta-principle; covered by composition |
| 4 | Collaborative Curation | **NONE** | **NONE** | No proposal workflow integrity checks |
| 5 | Provenance & Traceability | `check_frontmatter` | `trigger_source_primacy`, `trigger_citation_quality` | No source format consistency |
| 6 | Domain-Shaped Organization | `check_cross_references`, `check_coverage`, `check_index_sync` | -- | No AGENTS.md sync, no naming conventions |
| 7 | Right-Sized Scope | **NONE** | **NONE** | No scope metrics at all |
| 8 | Empirical Feedback | `check_freshness`, `check_inventory_regression` | -- | Utilization not integrated into health checks |
| 9 | Progressive Disclosure | `check_frontmatter`, `check_cross_references`, `check_index_sync` | -- | No AGENTS.md manifest sync, no depth-layer completeness |
| 10 | Explain the Why | -- | `trigger_why_quality` | No deterministic section presence check |
| 11 | Concrete Before Abstract | `check_section_ordering` | `trigger_depth_accuracy`, `trigger_concrete_examples` | Only checks ordering, not presence |
| 12 | Multiple Representations | `check_size_bounds`, `check_coverage` | `trigger_depth_accuracy` | No cross-depth consistency check |

### Principles With No Coverage

- **#4 Collaborative Curation**: No checks on `_proposals/` integrity, proposal frontmatter, or stale proposals
- **#7 Right-Sized Scope**: No way to flag topic bloat, off-scope content, or redundancy across files

### Principles With Weak Coverage

- **#2 Dual Audience**: Only line-count bounds; no readability assessment
- **#6 Domain-Shaped Organization**: Good structural checks, but no AGENTS.md ↔ filesystem sync
- **#9 Progressive Disclosure**: Index sync only; AGENTS.md manifest not validated against actual files
- **#10 Explain the Why**: Entirely in Tier 2; section presence is deterministic
- **#11 Concrete Before Abstract**: Ordering checked but section presence not enforced at Tier 1

---

## New Python-Based Validators (Proposed)

### Category A: Structural Integrity (Tier 1, fail/warn severity)

#### A1. `check_heading_hierarchy(file_path)` -- NEW
**Principle**: #2 Dual Audience, #9 Progressive Disclosure
**Checks**:
- Exactly one H1 per file
- No skipped heading levels (H1 → H3 without H2)
- Code blocks excluded from heading detection
**Severity**: warn
**Auto-fix potential**: None (ambiguous which level is wrong)
**Implementation**: Regex on `^#{1,6}\s+` after stripping fenced code blocks

#### A2. `check_section_completeness(file_path)` -- NEW
**Principle**: #10 Explain the Why, #11 Concrete Before Abstract
**Checks**: Required sections present per depth template:
- Working: "Why This Matters", "In Practice", "Key Guidance", "Watch Out For", "Go Deeper"
- Overview: "What This Covers", "How It's Organized"
- Reference: content present (non-empty body)
**Severity**: fail (missing required section), warn (missing optional section)
**Auto-fix potential**: Yes -- can insert stub section with `<!-- TODO: ... -->` placeholder
**Implementation**: Regex search for `## Section Name` (case-insensitive) after frontmatter

#### A3. `check_agents_md_sync(kb_root)` -- NEW
**Principle**: #6 Domain-Shaped Organization, #9 Progressive Disclosure
**Checks**:
- Every area directory on disk appears in AGENTS.md manifest
- Every topic file in an area is listed in the area's table
- No AGENTS.md entries reference nonexistent files
**Severity**: warn
**Auto-fix potential**: Yes -- can regenerate the managed section between `<!-- dewey:kb:begin -->` and `<!-- dewey:kb:end -->` markers
**Implementation**: Parse AGENTS.md for markdown link paths, compare against filesystem glob

#### A4. `check_naming_conventions(kb_root)` -- NEW
**Principle**: #6 Domain-Shaped Organization
**Checks**:
- Area directory names: lowercase, hyphens only, no spaces or underscores
- Topic file names: lowercase, hyphens, `.md` extension
- Reference files: `<topic>.ref.md` naming pattern
- No spaces, uppercase, or special characters in paths
**Severity**: warn
**Auto-fix potential**: Yes -- can rename files (with git mv) to normalized form
**Implementation**: Regex on `Path.name` for each discovered file

#### A5. `check_proposal_integrity(kb_root)` -- NEW
**Principle**: #4 Collaborative Curation
**Checks**:
- Every file in `_proposals/` has `status: proposal` in frontmatter
- Every proposal has `proposed_by` and `rationale` fields
- No proposal older than configurable max age (default 60 days) without action
- Proposal content follows working-depth template (has required sections)
**Severity**: warn (missing fields), warn (stale proposals)
**Auto-fix potential**: None (proposals need human decisions)
**Implementation**: Glob `_proposals/*.md`, parse frontmatter, check fields and dates

### Category B: Content Quality Heuristics (Tier 1, warn severity)

#### B1. `check_readability(file_path)` -- NEW
**Principle**: #2 Dual Audience
**Checks**:
- Flesch-Kincaid grade level within expected range per depth:
  - Overview: grade 8-14 (accessible to broad audience)
  - Working: grade 10-16 (practitioner level)
  - Reference: no check (terse by design)
- Flags excessively complex prose (grade > 16)
**Severity**: warn
**Auto-fix potential**: None (rewriting is LLM territory)
**Implementation**: Stdlib-only Flesch-Kincaid using vowel-group syllable heuristic. Strip markdown syntax before analysis. ~85-90% syllable accuracy is sufficient for band-level gating.

**Algorithm sketch**:
```python
def count_syllables(word):
    """Vowel-group heuristic: count contiguous vowel sequences."""
    word = re.sub(r'e$', '', word.lower())
    groups = re.findall(r'[aeiouy]+', word)
    return max(1, len(groups))

def flesch_kincaid_grade(words, sentences, syllables):
    return 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
```

#### B2. `check_duplicate_content(kb_root)` -- NEW
**Principle**: #7 Right-Sized Scope, #12 Multiple Representations
**Checks**:
- No exact-duplicate paragraphs (40+ chars) across files (via md5 hash)
- No high-overlap file pairs (Jaccard similarity > 0.4 on 5-word shingles)
- Excludes frontmatter and code blocks from comparison
**Severity**: warn
**Auto-fix potential**: None (merging/deduplication requires judgment)
**Implementation**: Two-pass approach:
1. Fast exact-duplicate detection via paragraph hashing (`hashlib.md5`)
2. Cross-file similarity via word shingling + Jaccard coefficient (`collections.defaultdict`)

Both are O(n^2) but feasible for medium-sized KBs (50-200 files).

#### B3. `check_go_deeper_links(file_path)` -- NEW
**Principle**: #1 Source Primacy, #12 Multiple Representations
**Checks**: Working-depth files:
- "Go Deeper" section exists
- Contains link to `.ref.md` companion
- Contains at least one external source link
**Severity**: warn
**Auto-fix potential**: Partial -- can insert ref.md link if companion exists on disk
**Implementation**: Section extraction + regex for markdown links

#### B4. `check_ref_see_also(file_path)` -- NEW
**Principle**: #12 Multiple Representations
**Checks**: Reference-depth files:
- Contains "See also" link back to working-depth companion
- Link target exists on disk
**Severity**: warn
**Auto-fix potential**: Yes -- can insert `**See also:** [Topic](topic.md)` if companion exists
**Implementation**: Regex for `See also` or `## See also` + link extraction

### Category C: Cross-File Consistency (Tier 1, warn severity)

#### C1. `check_link_graph(kb_root)` -- NEW
**Principle**: #6 Domain-Shaped Organization, #9 Progressive Disclosure
**Checks**:
- Orphaned files: `.md` files not linked from any other file (excluding entry points)
- Bidirectional ref ↔ working links: working links to ref, ref links back
- Overview ↔ topic links: overview "How It's Organized" table includes all area topics
**Severity**: warn
**Auto-fix potential**: None (link placement requires judgment)
**Implementation**: Build directed graph from all internal markdown links. Detect orphans via set difference. Check bidirectional edges for ref ↔ working pairs.

#### C2. `check_curation_plan_sync(kb_root)` -- NEW
**Principle**: #4 Collaborative Curation, #8 Empirical Feedback
**Checks**:
- Every `[x]` item in curation plan has a corresponding file on disk
- Every topic file on disk appears in curation plan (as `[x]` or `[ ]`)
- No `[ ]` items that already exist as files (should be checked)
**Severity**: warn
**Auto-fix potential**: Yes -- can update checkboxes to `[x]` for files that exist
**Implementation**: Parse curation plan markdown checkboxes, extract topic names, compare against filesystem

#### C3. `check_terminology_consistency(kb_root, glossary)` -- NEW
**Principle**: #2 Dual Audience, #6 Domain-Shaped Organization
**Checks**:
- Non-canonical term variants flagged against a configurable glossary
- Glossary stored as simple Python dict or `.dewey/glossary.json`
- Code blocks excluded from checking
**Severity**: warn
**Auto-fix potential**: Yes -- can replace non-canonical variants with canonical terms (conservative: only exact whole-word matches)
**Implementation**: Regex word-boundary matching for each glossary variant. O(terms * files) but fast for typical glossary sizes (<100 terms).

### Category D: Utilization Integration (Tier 1, warn severity)

#### D1. `check_utilization_signals(kb_root)` -- NEW
**Principle**: #8 Empirical Feedback
**Checks**:
- Flag files with 0 reads that have been in KB > 30 days
- Flag files with declining read trends (if history has 3+ snapshots)
- This is a lighter version of `generate_recommendations` -- surfaces signals during regular health checks rather than requiring a separate recommendations run
**Severity**: warn
**Auto-fix potential**: None (utilization signals inform human decisions)
**Implementation**: Read utilization log, cross-reference with file ages from history snapshots

---

## Auto-Correction Capabilities (Conservative)

Only unambiguous, reversible corrections. All auto-fixes should:
1. Log what was changed (before/after)
2. Be opt-in via `--fix` flag
3. Create a summary of changes for human review

### Fix 1: Insert Missing Section Stubs
**Trigger**: `check_section_completeness` finds missing required section
**Action**: Insert `## Section Name\n\n<!-- TODO: Add content -->\n` at appropriate position
**Risk**: Low -- adds structure without modifying existing content
**Reversibility**: Easy to find and remove `<!-- TODO -->` markers

### Fix 2: Normalize Frontmatter Formatting
**Trigger**: Frontmatter exists but has formatting issues
**Action**:
- Sort fields to canonical order: sources, last_validated, relevance, depth
- Normalize date format to ISO 8601 (YYYY-MM-DD)
- Ensure sources is a proper YAML list
**Risk**: Low -- metadata-only changes
**Reversibility**: Git diff shows exact changes

### Fix 3: Insert ref ↔ working Cross-Links
**Trigger**: `check_ref_see_also` or `check_go_deeper_links` finds missing companion link
**Action**:
- Add `**See also:** [Topic](topic.md)` to end of .ref.md
- Add `- [Topic Reference](topic.ref.md) -- quick-lookup version` to "Go Deeper" section
**Risk**: Low -- adds links to existing content, doesn't modify prose
**Reversibility**: Easy to identify and remove added lines

### Fix 4: Update Curation Plan Checkboxes
**Trigger**: `check_curation_plan_sync` finds `[ ]` items that exist on disk
**Action**: Change `- [ ] Topic Name` to `- [x] Topic Name`
**Risk**: Very low -- corrects metadata to match reality
**Reversibility**: Trivial

### Fix 5: Normalize File Names
**Trigger**: `check_naming_conventions` finds non-conforming names
**Action**: Rename to lowercase-hyphenated form (via `os.rename`)
**Risk**: Medium -- must also update all internal links that reference the old name
**Recommendation**: Report only by default; `--fix` updates both filename and references atomically
**Reversibility**: Git history preserves old names

---

## The Tier 1 / Tier 2 Boundary

### What Python Can Assert (Tier 1)

Python is the right tool when the check is:
- **Structural**: Does the file have the right sections, fields, links?
- **Metric-based**: Is the word count, line count, readability score in range?
- **Pattern-based**: Does the content match expected patterns (links, code blocks, tables)?
- **Relational**: Do files reference each other correctly? Is the manifest in sync?
- **Historical**: Has anything regressed since the last check?

### What Requires LLM (Tier 2)

The LLM is needed when the check requires:
- **Semantic understanding**: Is the "Why This Matters" section actually explaining why, or just restating what?
- **Source comparison**: Has the source material changed since last validation?
- **Quality judgment**: Are the examples realistic and helpful, or contrived?
- **Depth assessment**: Is this content genuinely working-level, or is it mislabeled overview?
- **Relevance evaluation**: Should this topic be in the KB at all?

### New Tier 2 Triggers (Proposed)

#### T1. `trigger_readability_outlier(file_path)` -- NEW
**When**: Flesch-Kincaid grade > 16 (extremely complex prose)
**Context**: grade_level, reading_ease, longest_sentence, complex_word_count
**Claude's role**: Determine if complexity is justified (technical domain) or needs simplification

#### T2. `trigger_duplicate_overlap(file_a, file_b, similarity)` -- NEW
**When**: Cross-file Jaccard similarity > 0.4
**Context**: similarity score, shared shingles sample, file depths
**Claude's role**: Determine if overlap is intentional (ref mirrors working) or accidental (copy-paste drift)

#### T3. `trigger_scope_drift(file_path)` -- NEW
**When**: File has many inline links to external topics not in the KB
**Context**: external_link_count, linked_domains, file_word_count
**Claude's role**: Assess if the file is trying to cover too broad a scope

---

## Architecture Recommendations

### 1. Organize Validators by Principle

Current: validators are loosely ordered by what they check.
Proposed: group validators into modules by principle cluster:

```
dewey/skills/health/scripts/
├── validators.py          # Keep existing (structural validators)
├── content_checks.py      # NEW: readability, section completeness, duplicate detection
├── graph_checks.py        # NEW: link graph, orphan detection, cross-file consistency
├── sync_checks.py         # NEW: AGENTS.md sync, curation plan sync, index sync (move from validators)
├── tier2_triggers.py      # Keep existing
├── auto_fix.py            # NEW: conservative auto-correction functions
├── check_kb.py            # Keep existing (orchestrator)
├── history.py             # Keep existing
└── utilization.py         # Keep existing
```

### 2. Add `--fix` Flag to check_kb.py

```bash
# Report only (default)
python3 check_kb.py --kb-root /path/to/kb --both

# Report + auto-fix unambiguous issues
python3 check_kb.py --kb-root /path/to/kb --both --fix

# Dry-run: show what would be fixed without changing files
python3 check_kb.py --kb-root /path/to/kb --both --fix --dry-run
```

### 3. Return Format Extension

Current issue format works well. Add an optional `fix` field for auto-correctable issues:

```python
{
    "file": "docs/area/topic.md",
    "message": "Missing 'Go Deeper' section",
    "severity": "warn",
    "fix": {                          # NEW: present only if auto-fixable
        "action": "insert_section",
        "details": "Add ## Go Deeper stub at end of file"
    }
}
```

### 4. Validator Registration Pattern

As the validator count grows, consider a registry pattern for check_kb.py:

```python
# Each validator module exports a list of check functions
TIER1_PER_FILE = [
    check_frontmatter,
    check_heading_hierarchy,       # NEW
    check_section_completeness,    # NEW
    check_section_ordering,
    check_size_bounds,
    check_readability,             # NEW
    check_source_urls,
    check_freshness,
    check_go_deeper_links,         # NEW
    check_ref_see_also,            # NEW
]

TIER1_STRUCTURAL = [
    check_coverage,
    check_index_sync,
    check_agents_md_sync,          # NEW
    check_naming_conventions,      # NEW
    check_proposal_integrity,      # NEW
    check_link_graph,              # NEW
    check_curation_plan_sync,      # NEW
    check_duplicate_content,       # NEW
    check_terminology_consistency, # NEW
    check_utilization_signals,     # NEW
    check_inventory_regression,
]
```

---

## Implementation Priority

### Phase 1: High-Value, Low-Effort (Week 1)
1. **A2: `check_section_completeness`** -- Covers principles #10, #11 at Tier 1. Most content issues stem from missing sections.
2. **A1: `check_heading_hierarchy`** -- Simple regex, catches structural errors early.
3. **B3: `check_go_deeper_links`** + **B4: `check_ref_see_also`** -- Enforces the multiple-representations contract between working ↔ reference pairs.
4. **Fix 1: Insert missing section stubs** -- Immediate remediation for section completeness failures.
5. **Fix 3: Insert ref ↔ working cross-links** -- Immediate remediation for missing companion links.

### Phase 2: Cross-File Consistency (Week 2)
6. **A3: `check_agents_md_sync`** -- Catches manifest drift, which compounds over time.
7. **C2: `check_curation_plan_sync`** -- Connects planning to reality.
8. **A5: `check_proposal_integrity`** -- Enables the collaborative curation principle.
9. **C1: `check_link_graph`** -- Surfaces orphaned content and missing connections.
10. **Fix 4: Update curation plan checkboxes** -- Low-risk auto-correction.

### Phase 3: Content Quality (Week 3)
11. **B1: `check_readability`** -- Readability gating for dual-audience principle.
12. **B2: `check_duplicate_content`** -- Scope control via deduplication detection.
13. **A4: `check_naming_conventions`** -- Convention enforcement.
14. **C3: `check_terminology_consistency`** -- Requires glossary setup first.

### Phase 4: Utilization Integration (Week 4)
15. **D1: `check_utilization_signals`** -- Brings empirical feedback into regular checks.
16. **T1-T3: New Tier 2 triggers** -- LLM-assisted evaluation for edge cases.

---

## Key Takeaways

1. **Three principles have zero coverage** (#4, #7, #9-partial) and five more have depth gaps. The proposed 14 new validators close all gaps that Python can address.

2. **The biggest ROI is section completeness checking** (A2). Most content quality issues manifest as missing sections. This is trivially deterministic and enables auto-fix with stub insertion.

3. **Auto-correction should be conservative and opt-in**. The 5 proposed fixes (section stubs, frontmatter normalization, cross-links, curation plan checkboxes, file naming) are all unambiguous and reversible. A `--fix` flag with `--dry-run` option gives users full control.

4. **Readability metrics work with stdlib**. Flesch-Kincaid with vowel-group syllable heuristic is ~85-90% accurate -- more than enough for band-level gating (grade 8-14 for overviews, 10-16 for working).

5. **The Tier 1/Tier 2 boundary is clear**: Python handles structure, metrics, and patterns. The LLM handles semantics, judgment, and comparison. New Tier 2 triggers (readability outliers, duplicate overlap assessment, scope drift) bridge cases where Python flags but can't decide.

## Remaining Unknowns

- [ ] Should terminology consistency use a checked-in glossary file or auto-discovery? (Recommend: glossary file in `.dewey/glossary.json`, auto-discovery as optional Tier 2 trigger)
- [ ] What readability thresholds are appropriate for the KB's actual domain? (Need to baseline current files before setting bounds)
- [ ] Should link graph checks enforce bidirectional links for all pairs, or only ref ↔ working? (Recommend: only ref ↔ working for now)
- [ ] How should auto-fix interact with git? (Recommend: `--fix` modifies files in-place, user reviews with `git diff` before committing)
- [ ] Should duplicate detection compare across depths intentionally? (Working and ref for the same topic will naturally overlap -- need to exclude known pairs)

## Implementation Context

<claude_context>
<application>
- when_to_use: When extending Dewey's health system to cover more design principles deterministically
- when_not_to_use: For content that requires semantic understanding (accuracy, relevance, quality judgment)
- prerequisites: Existing validator architecture in validators.py, test patterns in test_validators.py
</application>
<technical>
- libraries: Python 3.9+ stdlib only (re, pathlib, hashlib, collections, difflib, math, statistics)
- patterns: Function returns list[dict] with file/message/severity keys. unittest.TestCase with tempfile setUp/tearDown.
- gotchas: Python 3.9 requires Optional[str] at runtime (not str | None). Scripts must be standalone with argparse. Never write to project directory in tests.
</technical>
<integration>
- works_with: check_kb.py orchestrator, history.py for regression tracking, utilization.py for empirical feedback
- conflicts_with: Nothing -- all additive to existing architecture
- alternatives: External tools (markdownlint, vale, textstat) but those violate stdlib-only constraint
</integration>
</claude_context>

**Next Action:** Create implementation plan with phased delivery, starting with section completeness + heading hierarchy validators.

## Sources

- Dewey codebase: `dewey/skills/health/scripts/validators.py` (9 existing validators)
- Dewey codebase: `dewey/skills/health/scripts/tier2_triggers.py` (6 existing triggers)
- Dewey codebase: `dewey/skills/health/scripts/check_kb.py` (orchestrator + recommendations)
- Dewey codebase: `tests/skills/health/` (154 tests across 7 files)
- Dewey codebase: `dewey/skills/health/references/design-principles.md` (12 principles)
- Flesch-Kincaid formula: standard readability metric (Kincaid et al., 1975)
- Jaccard similarity / shingling: standard information retrieval technique (Broder, 1997)
