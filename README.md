# Dewey -- Knowledge Base Management for Claude Code

Dewey is a Claude Code plugin that helps you build, curate, and maintain structured knowledge bases. It implements a [specification](docs/plans/2026-02-14-knowledge-base-spec-design.md) for role-specific knowledge bases that serve both AI agents and humans.

## Why

AI agents produce better outputs when they have access to curated, relevant knowledge. But knowledge bases serve two consumers: the **agent** (who needs structured, token-efficient context) and the **human** (who needs readable, navigable content). Dewey defines a standard for what a well-formed knowledge base looks like and provides skills to create and maintain one.

The spec is provider-agnostic -- the output works with any agent (Claude Code, Codex, Gemini CLI, Cursor, etc.).

## Skills

| Skill | Purpose |
|-------|---------|
| `/dewey:init` | Bootstrap a new knowledge base with directory structure, AGENTS.md, and templates |
| `/dewey:curate` | Add topics, propose additions, promote proposals, ingest from URLs |
| `/dewey:health` | Validate quality, check freshness, analyze coverage gaps, generate reports |
| `/dewey:explore` | Discover what knowledge domains to capture through guided conversation |

### `/dewey:init`

Scaffolds a new knowledge base. Provide a role name and optionally domain areas:

```
/dewey:init --role "Platform Engineer" --areas "Infrastructure,Observability,CI/CD"
```

Creates: AGENTS.md (persona + manifest), CLAUDE.md (agent instructions), docs/ directory with overview files per area, and the `.dewey/` metadata directories.

### `/dewey:curate`

Manages the content lifecycle:

- **add** -- Research a topic, draft working-knowledge and reference files, update all indexes
- **propose** -- Submit a topic proposal for review before committing
- **promote** -- Move a validated proposal into a domain area
- **ingest** -- Ingest an external URL, evaluate against existing KB, then propose new content or update existing topics

```
/dewey:curate add Project Structure in python-foundations
/dewey:curate propose "Dependency Injection" --rationale "Coverage gap"
/dewey:curate promote dependency-injection --target-area python-foundations
```

### `/dewey:health`

Validates knowledge base quality with deterministic checks (Tier 1):

- Frontmatter completeness (sources, last_validated, relevance, depth)
- Section ordering for working-knowledge files
- Cross-reference integrity
- Size bounds per depth level
- Coverage gaps (missing overviews, missing reference companions)
- Freshness (staleness by last_validated date)
- Source URL format validation

```
/dewey:health check
/dewey:health freshness
/dewey:health coverage
```

### `/dewey:explore`

Guided discovery conversation to identify what knowledge domains matter for a role, before committing to structure.

## Knowledge Base Structure

A Dewey-conformant knowledge base looks like:

```
project-root/
  AGENTS.md                          # Role persona + topic manifest
  CLAUDE.md                          # Agent instructions + domain area index
  docs/
    <domain-area>/
      overview.md                    # Area orientation (depth: overview)
      <topic>.md                     # Working knowledge (depth: working)
      <topic>.ref.md                 # Expert reference (depth: reference)
    _proposals/                      # Staged additions pending review
  .dewey/
    health/                          # Quality scores
    history/                         # Change log
    utilization/                     # Reference tracking
```

Every knowledge file carries YAML frontmatter: `sources`, `last_validated`, `relevance`, and `depth`.

## Design Principles

Twelve principles grounded in agent context research (Anthropic, OpenAI) and cognitive science (Sweller, Vygotsky, Paivio, Bjork, Pirolli, Kalyuga, Dunlosky).

### From Agent Context Research

1. **Source Primacy** -- The knowledge base is a curated guide, not a replacement for primary sources. Every entry points to one. When an agent or human needs to go deeper, the path is always clear.
2. **Dual Audience** -- Every entry serves the agent (structured, token-efficient context) and the human (readable, navigable content). When these conflict, favor human readability -- agents are more adaptable readers.
3. **Three-Dimensional Quality** -- Content quality measured across relevance, accuracy/freshness, and structural fitness simultaneously.
4. **Collaborative Curation** -- Either the human or an agent can propose additions, but all content passes through validation. The human brings domain judgment. The agent brings systematic coverage. Neither is sufficient alone.
5. **Provenance & Traceability** -- Every piece of knowledge carries metadata about where it came from, when it was last validated, and why it's in the KB.
6. **Domain-Shaped Organization** -- Organized around the domain's natural structure, not file types or technical categories. The taxonomy should feel intuitive to a practitioner.
7. **Right-Sized Scope** -- Contains what's needed to be effective in the role, and no more. The curation act is as much about what you exclude as what you include.
8. **Empirical Feedback** -- Observable signals about KB health: coverage gaps, stale entries, unused content. Proxy metrics inform curation decisions.
9. **Progressive Disclosure** -- Layered access so agents can discover what's available without loading everything. Metadata -> summaries -> full content -> deep references.

### From Cognitive Science Research

10. **Explain the Why** -- Causal explanations produce better comprehension and retention than stating facts alone. Every entry explains not just what to do, but why.
11. **Concrete Before Abstract** -- Lead with examples and worked scenarios, then build toward the abstraction. Concrete concepts create stronger memory traces.
12. **Multiple Representations** -- Important concepts should exist at multiple levels of depth (overview, working knowledge, reference). Material that helps novices can hinder experts and vice versa -- label each level clearly so readers self-select.

See the full [specification](docs/plans/2026-02-14-knowledge-base-spec-design.md) for detailed rationale and research sources.

## Tech Stack

- Python 3.9+ (stdlib only -- zero dependencies)
- Markdown with YAML frontmatter
- Claude Code skills framework

## Development

```bash
git clone https://github.com/bcbeidel/dewey.git
cd dewey

# Symlink the plugin for local development
ln -s "$(pwd)/dewey" ~/.claude/plugins/dewey

# Run tests
python3 -m pytest tests/ -v
```

## Project Structure

```
dewey/
  .claude-plugin/plugin.json         # Plugin manifest
  skills/
    init/                             # KB bootstrapping
      SKILL.md
      scripts/scaffold.py, templates.py
      workflows/init.md
      references/kb-spec-summary.md
    curate/                           # Content lifecycle
      SKILL.md
      scripts/create_topic.py, propose.py, promote.py
      workflows/curate-add.md, curate-propose.md, curate-promote.md, curate-ingest.md
    health/                           # Quality validation
      SKILL.md
      scripts/validators.py, check_kb.py
      workflows/health-check.md, health-audit.md, health-review.md, health-coverage.md, health-freshness.md
      references/validation-rules.md, quality-dimensions.md
    explore/                          # Domain discovery
      SKILL.md
      workflows/explore-discovery.md
docs/plans/                           # Design documents
tests/                                # Test suite (185 tests)
```

## Status

**v1.0.0** -- Core skills implemented and tested.

| Feature | Status |
|---------|--------|
| KB scaffolding (`/dewey:init`) | Complete |
| Content lifecycle (`/dewey:curate add/propose/promote`) | Complete |
| URL ingestion (`/dewey:curate ingest`) | Complete |
| Tier 1 deterministic health checks | Complete (7 validators) |
| Tier 2 LLM-assisted health assessments | Designed, not yet implemented |
| Domain discovery (`/dewey:explore`) | Complete |
| Utilization tracking | Infrastructure scaffolded |
| History / baselines | Infrastructure scaffolded |

## Documentation

- [Knowledge Base Specification](docs/plans/2026-02-14-knowledge-base-spec-design.md) -- The full design spec
- [Implementation Plan](docs/plans/2026-02-14-kb-skills-implementation.md) -- How the skills were built (completed)
