# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run a single test file
python3 -m pytest tests/skills/health/test_check_kb.py -v

# Run a single test class or method
python3 -m pytest tests/skills/health/test_tier2_triggers.py::TestTriggerSourceDrift -v

# Skip sandbox scaffold test (slow, creates real files)
python3 -m pytest tests/ -v -k "not test_scaffold_sandbox"

# Symlink for local plugin development
ln -s "$(pwd)/dewey" ~/.claude/plugins/dewey
```

No build step. No dependencies beyond Python 3.9+ stdlib.

## Architecture

Dewey is a Claude Code plugin that helps build, curate, and maintain structured knowledge bases. The output is provider-agnostic -- it works with any agent (Claude Code, Codex, Gemini CLI, Cursor, etc.).

### Plugin Structure

```
dewey/
  .claude-plugin/plugin.json       # Plugin manifest
  skills/
    <skill>/
      SKILL.md                     # Entry point: description, routing, intake logic
      workflows/                   # Multi-step processes Claude follows
      scripts/                     # Python helpers (stdlib-only, data collection)
      references/                  # Domain knowledge for Claude to consult
```

**Division of labor:** Python handles data collection, file operations, and deterministic validation. Claude handles analysis, judgment, and user interaction.

### Skills

| Skill | Purpose |
|-------|---------|
| `init` | Bootstrap a new knowledge base with directory structure, AGENTS.md, templates |
| `curate` | Add topics, propose additions, promote proposals, ingest from URLs |
| `health` | Validate quality, check freshness, analyze coverage gaps, generate reports |
| `explore` | Discover knowledge domains through guided conversation |

### Three-Tier Health Model

1. **Tier 1 -- Deterministic (Python)** -- Fast automated checks in `validators.py`. Validates frontmatter, section ordering, cross-references, size bounds, source URLs, freshness, coverage. CI-friendly. No LLM required.
2. **Tier 2 -- LLM-Assisted (Claude)** -- Pre-screener in `tier2_triggers.py` flags files with context data. Claude evaluates flagged items: source drift, depth accuracy, why-quality, in-practice concreteness, source primacy.
3. **Tier 3 -- Human Judgment** -- Surfaces decisions requiring human input: relevance questions, scope decisions, pending proposals, conflict resolution.

### Knowledge Base Structure

```
project-root/
  AGENTS.md                        # Role persona + topic manifest
  docs/                            # Knowledge directory (configurable via .dewey/config.json)
    <domain-area>/
      overview.md                  # Area orientation (depth: overview)
      <topic>.md                   # Working knowledge (depth: working)
      <topic>.ref.md               # Expert reference (depth: reference)
    _proposals/                    # Staged additions pending review
  .dewey/
    config.json                    # Settings (knowledge_dir name)
    health/                        # Quality scores, tier2-report.json
    history/                       # Change log
    utilization/                   # Reference tracking
```

Every knowledge file carries YAML frontmatter: `sources`, `last_validated`, `relevance`, `depth`.

## Design Principles

Twelve principles grounded in agent context research (Anthropic, OpenAI) and cognitive science (Sweller, Vygotsky, Paivio, Bjork, Pirolli, Kalyuga, Dunlosky).

### From Agent Context Research

1. **Source Primacy** -- The knowledge base is a curated guide, not a replacement for primary sources. Every entry points to one. When an agent or human needs to go deeper, the path is always clear.
2. **Dual Audience** -- Every entry serves the agent (structured, token-efficient context) and the human (readable, navigable content). When these conflict, favor human readability -- agents are more adaptable readers.
3. **Three-Dimensional Quality** -- Content quality measured across relevance, accuracy/freshness, and structural fitness simultaneously.
4. **Collaborative Curation** -- Either the human or an agent can propose additions, but all content passes through validation. The human brings domain judgment. The agent brings systematic coverage. Neither is sufficient alone.
5. **Provenance & Traceability** -- Every piece of knowledge carries metadata about where it came from, when it was last validated, and why it's in the knowledge base.
6. **Domain-Shaped Organization** -- Organized around the domain's natural structure, not file types or technical categories. The taxonomy should feel intuitive to a practitioner.
7. **Right-Sized Scope** -- Contains what's needed to be effective in the role, and no more. The curation act is as much about what you exclude as what you include.
8. **Empirical Feedback** -- Observable signals about knowledge base health: coverage gaps, stale entries, unused content. Proxy metrics inform curation decisions.
9. **Progressive Disclosure** -- Layered access so agents can discover what's available without loading everything. Metadata -> summaries -> full content -> deep references.

### From Cognitive Science Research

10. **Explain the Why** -- Causal explanations produce better comprehension and retention than stating facts alone. Every entry explains not just what to do, but why.
11. **Concrete Before Abstract** -- Lead with examples and worked scenarios, then build toward the abstraction. Concrete concepts create stronger memory traces.
12. **Multiple Representations** -- Important concepts should exist at multiple levels of depth (overview, working knowledge, reference). Material that helps novices can hinder experts and vice versa -- label each level clearly so readers self-select.

## Conventions

### Python

- **Python 3.9+ stdlib only** -- zero external dependencies
- Use `from __future__ import annotations` for union syntax (`str | None`) in type annotations
- Use `Optional[str]` in runtime expressions and function parameter defaults (Python 3.9 compat)
- Scripts live in `skills/<skill>/scripts/` and import each other directly (no package `__init__.py`)
- Cross-skill imports: add sibling scripts dirs to `sys.path` (see `check_kb.py` for pattern)

### Tests

- Framework: `unittest.TestCase`
- Pattern: `_write()` helper, `tempfile.mkdtemp()` in `setUp`, `shutil.rmtree()` in `tearDown`
- Imports: direct module imports (e.g., `from validators import check_frontmatter`) -- `conftest.py` adds all scripts dirs to `sys.path`
- Location: `tests/skills/<skill>/` mirrors `dewey/skills/<skill>/scripts/`

### Issue Format

All validators and triggers return structured dicts:

```python
# Tier 1 validators
{"file": str, "message": str, "severity": "fail" | "warn"}

# Tier 2 triggers
{"file": str, "trigger": str, "reason": str, "context": dict}
```

### Content Depths

| Depth | Purpose | Size (lines) |
|-------|---------|-------------|
| `overview` | Area orientation: what, why, how it connects | 5-150 |
| `working` | Actionable guidance with examples | 10-400 |
| `reference` | Terse, scannable lookup | 3-150 |

## Current Status

| Feature | Status |
|---------|--------|
| Knowledge base scaffolding (`/dewey:init`) | Complete |
| Content lifecycle (`/dewey:curate add/propose/promote/ingest`) | Complete |
| Domain discovery (`/dewey:explore`) | Complete |
| Tier 1 deterministic health checks (7 validators) | Complete |
| Tier 2 pre-screener (5 triggers) | Complete |
| Tier 2 LLM-assisted audit workflow | Complete |
| Tier 3 human decision queue | Designed, not yet tested |
| Utilization tracking | Complete |
| History / baselines | Complete |
