# Knowledge Base Skills Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build three Dewey skills (`/dewey:init`, `/dewey:curate`, `/dewey:health`) that implement the knowledge base specification defined in `docs/plans/2026-02-14-knowledge-base-spec-design.md`.

**Architecture:** Each skill follows Dewey's existing pattern: SKILL.md with routing, workflows/ for multi-step processes, references/ for domain knowledge, and scripts/ for Python helpers (stdlib-only, Python 3.9+). Python handles data collection and file operations; Claude handles analysis and judgment.

**Tech Stack:** Python 3.9+ (stdlib only), Markdown, YAML frontmatter, Claude Code skills framework

**Design Doc:** `docs/plans/2026-02-14-knowledge-base-spec-design.md`

---

## Phase 1: `/dewey:init` — Bootstrap a Knowledge Base

### Task 1: Create content templates as Python module

**Files:**
- Create: `skills/init/scripts/templates.py`
- Test: `tests/skills/init/test_templates.py`

**Step 1: Write the failing test**

```python
"""Tests for KB content templates."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "skills" / "init" / "scripts"))
from templates import (
    render_agents_md,
    render_index_md,
    render_overview_md,
    render_topic_md,
    render_topic_ref_md,
    render_proposal_md,
)


class TestAgentsMd(unittest.TestCase):
    def test_renders_with_role_name(self):
        result = render_agents_md(role_name="Paid Media Analyst", domain_areas=[])
        self.assertIn("# Role: Paid Media Analyst", result)

    def test_includes_persona_section(self):
        result = render_agents_md(role_name="Paid Media Analyst", domain_areas=[])
        self.assertIn("## Who You Are", result)
        self.assertIn("## What You Have Access To", result)
        self.assertIn("## How To Use This Knowledge", result)

    def test_includes_domain_areas_in_manifest(self):
        areas = [
            {"name": "Campaign Management", "topics": [
                {"name": "Budget Allocation", "description": "How to allocate budget across campaigns"}
            ]}
        ]
        result = render_agents_md(role_name="Paid Media Analyst", domain_areas=areas)
        self.assertIn("### Campaign Management", result)
        self.assertIn("**Budget Allocation**", result)
        self.assertIn("How to allocate budget across campaigns", result)

    def test_empty_domain_areas(self):
        result = render_agents_md(role_name="Data Scientist", domain_areas=[])
        self.assertIn("## What You Have Access To", result)


class TestTopicMd(unittest.TestCase):
    def test_renders_with_frontmatter(self):
        result = render_topic_md(
            topic_name="Budget Allocation",
            relevance="How to distribute spend across campaigns and ad groups",
        )
        self.assertIn("sources:", result)
        self.assertIn("last_validated:", result)
        self.assertIn("relevance:", result)
        self.assertIn("depth: working", result)

    def test_includes_required_sections(self):
        result = render_topic_md(
            topic_name="Budget Allocation",
            relevance="How to distribute spend",
        )
        self.assertIn("## Why This Matters", result)
        self.assertIn("## In Practice", result)
        self.assertIn("## Key Guidance", result)
        self.assertIn("## Watch Out For", result)
        self.assertIn("## Go Deeper", result)

    def test_topic_name_in_heading(self):
        result = render_topic_md(
            topic_name="Budget Allocation",
            relevance="How to distribute spend",
        )
        self.assertIn("# Budget Allocation", result)


class TestTopicRefMd(unittest.TestCase):
    def test_renders_with_reference_depth(self):
        result = render_topic_ref_md(
            topic_name="Budget Allocation",
            relevance="Quick reference for budget allocation rules",
        )
        self.assertIn("depth: reference", result)

    def test_includes_see_also(self):
        result = render_topic_ref_md(
            topic_name="Budget Allocation",
            relevance="Quick reference",
        )
        self.assertIn("**See also:**", result)


class TestOverviewMd(unittest.TestCase):
    def test_renders_with_overview_depth(self):
        result = render_overview_md(
            area_name="Campaign Management",
            relevance="Overview of campaign management domain",
            topics=[],
        )
        self.assertIn("depth: overview", result)

    def test_includes_topic_listing(self):
        topics = [
            {"name": "Budget Allocation", "filename": "budget-allocation.md", "description": "How to allocate budget"}
        ]
        result = render_overview_md(
            area_name="Campaign Management",
            relevance="Overview",
            topics=topics,
        )
        self.assertIn("[Budget Allocation](budget-allocation.md)", result)


class TestProposalMd(unittest.TestCase):
    def test_includes_proposal_frontmatter(self):
        result = render_proposal_md(
            topic_name="New Topic",
            relevance="Why this is needed",
            proposed_by="human",
            rationale="Gap in coverage",
        )
        self.assertIn("status: proposal", result)
        self.assertIn("proposed_by: human", result)
        self.assertIn("rationale:", result)


class TestIndexMd(unittest.TestCase):
    def test_renders_with_role_name(self):
        result = render_index_md(role_name="Paid Media Analyst", domain_areas=[])
        self.assertIn("Paid Media Analyst", result)

    def test_includes_domain_area_links(self):
        areas = [
            {"name": "Campaign Management", "dirname": "campaign-management"}
        ]
        result = render_index_md(role_name="Paid Media Analyst", domain_areas=areas)
        self.assertIn("[Campaign Management](campaign-management/overview.md)", result)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/skills/init/test_templates.py -v`
Expected: FAIL — `templates` module does not exist

**Step 3: Implement templates.py**

```python
"""Content templates for the knowledge base specification.

Renders markdown files conforming to the KB spec defined in
docs/plans/2026-02-14-knowledge-base-spec-design.md.
"""
from datetime import date


def _today() -> str:
    return date.today().isoformat()


def render_agents_md(role_name: str, domain_areas: list[dict]) -> str:
    """Render AGENTS.md — persona + manifest."""
    sections = [f"# Role: {role_name}", ""]
    sections += [
        "## Who You Are",
        "",
        f"<!-- Define the persona, responsibilities, and behavioral expectations for a {role_name}. -->",
        "",
        "## What You Have Access To",
        "",
    ]
    if domain_areas:
        for area in domain_areas:
            sections.append(f"### {area['name']}")
            for topic in area.get("topics", []):
                sections.append(f"- **{topic['name']}** -- {topic['description']}")
            sections.append("")
    else:
        sections += ["<!-- Add domain areas and topics as the knowledge base grows. -->", ""]

    sections += [
        "## How To Use This Knowledge",
        "",
        "- Load topic files from `knowledge/` when the task relates to that domain area.",
        "- Cite primary sources from the `sources` frontmatter when making recommendations.",
        "- Defer to primary sources for detailed reference — the knowledge base provides curated guidance, not exhaustive documentation.",
        "",
    ]
    return "\n".join(sections)


def render_index_md(role_name: str, domain_areas: list[dict]) -> str:
    """Render index.md — human-readable table of contents."""
    sections = [f"# {role_name} Knowledge Base", ""]
    sections += ["## Domain Areas", ""]
    if domain_areas:
        for area in domain_areas:
            dirname = area.get("dirname", "")
            sections.append(f"- [{area['name']}]({dirname}/overview.md)")
        sections.append("")
    else:
        sections += ["<!-- Domain areas will be listed here as the KB grows. -->", ""]
    return "\n".join(sections)


def render_overview_md(area_name: str, relevance: str, topics: list[dict]) -> str:
    """Render overview.md — domain area orientation."""
    sections = [
        "---",
        "sources:",
        "  - url: <!-- Add primary source URL -->",
        "    title: <!-- Add source title -->",
        f"last_validated: {_today()}",
        f"relevance: \"{relevance}\"",
        "depth: overview",
        "---",
        "",
        f"# {area_name}",
        "",
        "## What This Covers",
        "",
        f"<!-- Describe what {area_name} covers and why it matters to this role. -->",
        "",
        "## How It's Organized",
        "",
    ]
    if topics:
        for topic in topics:
            sections.append(f"- [{topic['name']}]({topic['filename']}) -- {topic['description']}")
        sections.append("")
    else:
        sections += ["<!-- Topics will be listed here as they are added. -->", ""]

    sections += [
        "## Key Sources",
        "",
        "<!-- List the 3-5 most important primary sources for this domain area. -->",
        "",
    ]
    return "\n".join(sections)


def render_topic_md(topic_name: str, relevance: str) -> str:
    """Render <topic>.md — working knowledge."""
    return "\n".join([
        "---",
        "sources:",
        "  - url: <!-- Add primary source URL -->",
        "    title: <!-- Add source title -->",
        f"last_validated: {_today()}",
        f"relevance: \"{relevance}\"",
        "depth: working",
        "---",
        "",
        f"# {topic_name}",
        "",
        "## Why This Matters",
        "",
        "<!-- What problem does this solve? When does a practitioner encounter it?",
        "     Why is the approach here preferred over alternatives? -->",
        "",
        "## In Practice",
        "",
        "<!-- A concrete, worked example showing the concept applied to a realistic",
        "     scenario. Code snippets, specific numbers, real tool output. -->",
        "",
        "> **Source:** [Title](url) -- section or page that informed this example",
        "",
        "## Key Guidance",
        "",
        "<!-- Actionable recommendations. Each explains what to do, why it works,",
        "     and when it applies. Inline source references. -->",
        "",
        "- **Recommendation** -- reasoning ([Source](url))",
        "",
        "## Watch Out For",
        "",
        "<!-- Common mistakes, edge cases, things that change frequently. -->",
        "",
        "## Go Deeper",
        "",
        f"- [{topic_name} Reference]({_slugify(topic_name)}.ref.md) -- quick-lookup version",
        "- [Source Title](url) -- primary source for full treatment",
        "",
    ])


def render_topic_ref_md(topic_name: str, relevance: str) -> str:
    """Render <topic>.ref.md — expert reference."""
    return "\n".join([
        "---",
        "sources:",
        "  - url: <!-- Add primary source URL -->",
        "    title: <!-- Add source title -->",
        f"last_validated: {_today()}",
        f"relevance: \"{relevance}\"",
        "depth: reference",
        "---",
        "",
        f"# {topic_name} -- Reference",
        "",
        "<!-- Tables, lists, quick rules. Minimal prose. -->",
        "",
        "**Quick rules:**",
        "- <!-- Rule 1 -->",
        "",
        f"**See also:** [{topic_name}]({_slugify(topic_name)}.md) | [Primary source](url)",
        "",
    ])


def render_proposal_md(
    topic_name: str,
    relevance: str,
    proposed_by: str,
    rationale: str,
) -> str:
    """Render a proposal in _proposals/."""
    return "\n".join([
        "---",
        f"status: proposal",
        f"proposed_by: {proposed_by}",
        f"rationale: \"{rationale}\"",
        "sources:",
        "  - url: <!-- Add primary source URL -->",
        "    title: <!-- Add source title -->",
        f"last_validated: {_today()}",
        f"relevance: \"{relevance}\"",
        "depth: working",
        "---",
        "",
        f"# {topic_name}",
        "",
        "## Why This Matters",
        "",
        "<!-- Fill in per the working knowledge template. -->",
        "",
        "## In Practice",
        "",
        "<!-- Concrete example. -->",
        "",
        "## Key Guidance",
        "",
        "<!-- Recommendations with sources. -->",
        "",
        "## Watch Out For",
        "",
        "<!-- Gotchas. -->",
        "",
        "## Go Deeper",
        "",
        "<!-- References. -->",
        "",
    ])


def _slugify(name: str) -> str:
    """Convert a topic name to a filename slug."""
    return name.lower().replace(" ", "-").replace("/", "-")
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/skills/init/test_templates.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add skills/init/scripts/templates.py tests/skills/init/test_templates.py
git commit -m "feat: add KB content templates module"
```

---

### Task 2: Create scaffold script

**Files:**
- Create: `skills/init/scripts/scaffold.py`
- Test: `tests/skills/init/test_scaffold.py`

**Step 1: Write the failing test**

```python
"""Tests for KB scaffolding."""
import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "skills" / "init" / "scripts"))
from scaffold import scaffold_kb


class TestScaffoldKb(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_agents_md(self):
        scaffold_kb(self.tmpdir, role_name="Paid Media Analyst")
        self.assertTrue((self.tmpdir / "AGENTS.md").exists())

    def test_creates_knowledge_directory(self):
        scaffold_kb(self.tmpdir, role_name="Paid Media Analyst")
        self.assertTrue((self.tmpdir / "knowledge").is_dir())

    def test_creates_index_md(self):
        scaffold_kb(self.tmpdir, role_name="Paid Media Analyst")
        self.assertTrue((self.tmpdir / "knowledge" / "index.md").exists())

    def test_creates_proposals_directory(self):
        scaffold_kb(self.tmpdir, role_name="Paid Media Analyst")
        self.assertTrue((self.tmpdir / "knowledge" / "_proposals").is_dir())

    def test_creates_dewey_directories(self):
        scaffold_kb(self.tmpdir, role_name="Paid Media Analyst")
        self.assertTrue((self.tmpdir / ".dewey" / "health").is_dir())
        self.assertTrue((self.tmpdir / ".dewey" / "history").is_dir())
        self.assertTrue((self.tmpdir / ".dewey" / "utilization").is_dir())

    def test_agents_md_contains_role(self):
        scaffold_kb(self.tmpdir, role_name="Data Scientist")
        content = (self.tmpdir / "AGENTS.md").read_text()
        self.assertIn("Data Scientist", content)

    def test_creates_domain_area_with_overview(self):
        scaffold_kb(
            self.tmpdir,
            role_name="Paid Media Analyst",
            domain_areas=["Campaign Management"],
        )
        area_dir = self.tmpdir / "knowledge" / "campaign-management"
        self.assertTrue(area_dir.is_dir())
        self.assertTrue((area_dir / "overview.md").exists())

    def test_agents_md_under_100_lines(self):
        scaffold_kb(
            self.tmpdir,
            role_name="Paid Media Analyst",
            domain_areas=["Area One", "Area Two", "Area Three"],
        )
        content = (self.tmpdir / "AGENTS.md").read_text()
        line_count = len(content.strip().splitlines())
        self.assertLess(line_count, 100)

    def test_does_not_overwrite_existing_agents_md(self):
        (self.tmpdir / "AGENTS.md").write_text("existing content")
        scaffold_kb(self.tmpdir, role_name="Paid Media Analyst")
        content = (self.tmpdir / "AGENTS.md").read_text()
        self.assertEqual(content, "existing content")

    def test_scaffold_returns_summary(self):
        result = scaffold_kb(self.tmpdir, role_name="Paid Media Analyst")
        self.assertIn("created", result)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/skills/init/test_scaffold.py -v`
Expected: FAIL — `scaffold` module does not exist

**Step 3: Implement scaffold.py**

```python
"""Scaffold a new knowledge base directory structure.

Creates the directory layout and template files defined by the KB spec.
Will not overwrite existing files.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from templates import (
    render_agents_md,
    render_index_md,
    render_overview_md,
)


def scaffold_kb(
    target_dir: Path,
    role_name: str,
    domain_areas: list[str] | None = None,
) -> str:
    """Create KB directory structure and template files.

    Args:
        target_dir: Root directory for the knowledge base.
        role_name: The role this KB serves (e.g., "Paid Media Analyst").
        domain_areas: Optional list of domain area names to pre-create.

    Returns:
        Summary string of what was created.
    """
    domain_areas = domain_areas or []
    created = []

    # Core directories
    dirs = [
        target_dir / "knowledge",
        target_dir / "knowledge" / "_proposals",
        target_dir / ".dewey" / "health",
        target_dir / ".dewey" / "history",
        target_dir / ".dewey" / "utilization",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        created.append(f"dir: {d.relative_to(target_dir)}")

    # Domain area directories and overviews
    area_metadata = []
    for area_name in domain_areas:
        dirname = _slugify(area_name)
        area_dir = target_dir / "knowledge" / dirname
        area_dir.mkdir(parents=True, exist_ok=True)
        created.append(f"dir: knowledge/{dirname}")
        area_metadata.append({"name": area_name, "dirname": dirname})

        overview_path = area_dir / "overview.md"
        if not overview_path.exists():
            overview_path.write_text(render_overview_md(
                area_name=area_name,
                relevance=f"Overview of {area_name.lower()} domain",
                topics=[],
            ))
            created.append(f"file: knowledge/{dirname}/overview.md")

    # AGENTS.md
    agents_path = target_dir / "AGENTS.md"
    if not agents_path.exists():
        agents_md_areas = [
            {"name": a["name"], "topics": []} for a in area_metadata
        ]
        agents_path.write_text(render_agents_md(
            role_name=role_name,
            domain_areas=agents_md_areas,
        ))
        created.append("file: AGENTS.md")

    # knowledge/index.md
    index_path = target_dir / "knowledge" / "index.md"
    if not index_path.exists():
        index_path.write_text(render_index_md(
            role_name=role_name,
            domain_areas=area_metadata,
        ))
        created.append("file: knowledge/index.md")

    # .dewey/.gitkeep files for empty directories
    for d in [
        target_dir / ".dewey" / "health",
        target_dir / ".dewey" / "history",
        target_dir / ".dewey" / "utilization",
    ]:
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("")

    return f"created: {len(created)} items\n" + "\n".join(f"  {c}" for c in created)


def _slugify(name: str) -> str:
    """Convert a name to a directory slug."""
    return name.lower().replace(" ", "-").replace("/", "-")
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/skills/init/test_scaffold.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add skills/init/scripts/scaffold.py tests/skills/init/test_scaffold.py
git commit -m "feat: add KB scaffold script"
```

---

### Task 3: Create init SKILL.md and workflows

**Files:**
- Create: `skills/init/SKILL.md`
- Create: `skills/init/workflows/init-empty.md`
- Create: `skills/init/workflows/init-from-role.md`
- Create: `skills/init/references/kb-spec-summary.md`

**Step 1: Create SKILL.md**

```markdown
---
name: init
description: Bootstrap a new knowledge base with the standard directory structure, AGENTS.md, and content templates
---

<essential_principles>
## What This Skill Does

Creates a new knowledge base conforming to the KB specification. Scaffolds the directory structure, generates AGENTS.md (persona + manifest), index.md (human TOC), and optionally pre-creates domain areas based on a role description.

## Core Workflow

1. **Determine target directory** - Where the KB will live (default: current directory)
2. **Get role name** - What role this KB serves
3. **Python scaffolds structure** - Creates directories and template files
4. **Claude proposes domain areas** (if from-role) - Suggests initial organization based on the role
5. **Reports what was created** - Summary of files and directories

## Design Philosophy

- **Safe by default** - Never overwrites existing files
- **Minimal viable KB** - Scaffolds the structure, not the content
- **Templates guide quality** - Every generated file follows the content format spec
- **Human refines** - The scaffold is a starting point, not a finished product

## Key Variables

- `$ARGUMENTS` - Arguments passed to this skill (target directory and flags)
- `${CLAUDE_PLUGIN_ROOT}` - Root directory of the Dewey plugin
</essential_principles>

<intake>
Setting up a new knowledge base.

**Default behavior:** Scaffold an empty KB structure with templates.
**From role:** Use `--role "Role Name"` to have Claude propose initial domain areas.

If no `$ARGUMENTS` provided, ask for the role name.
</intake>

<routing>
## Argument-Based Routing

Parse `$ARGUMENTS`:

- Contains `--role` → Route to workflows/init-from-role.md
- Otherwise → Route to workflows/init-empty.md

Both workflows use the same Python scaffold script. The from-role workflow adds a step where Claude proposes domain areas before scaffolding.
</routing>

<workflows_index>
## Available Workflows

All workflows in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| init-empty.md | Scaffold empty KB structure with templates |
| init-from-role.md | Propose domain areas from role description, then scaffold |
</workflows_index>

<references_index>
## Domain Knowledge

All references in `references/`:

| Reference | Content |
|-----------|---------|
| kb-spec-summary.md | Summary of the KB specification principles and structure |
</references_index>

<scripts_integration>
## Python Helper Scripts

Located in `scripts/`:

**scaffold.py** - Main scaffolding script
- Creates directory structure (knowledge/, _proposals/, .dewey/)
- Generates AGENTS.md, index.md, overview.md from templates
- Safe: never overwrites existing files
- Returns summary of what was created

**templates.py** - Content template rendering
- Renders all KB file types (AGENTS.md, index.md, overview.md, topic.md, topic.ref.md, proposal.md)
- Includes correct frontmatter with today's date
- Follows the content format spec

**Usage in workflows:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/scaffold.py --target <dir> --role "Role Name" [--areas "Area One,Area Two"]
```
</scripts_integration>

<success_criteria>
Init is successful when:
- ✅ Directory structure matches the KB spec
- ✅ AGENTS.md exists with role name and manifest structure
- ✅ knowledge/index.md exists with TOC structure
- ✅ knowledge/_proposals/ directory exists
- ✅ .dewey/ directories exist (health, history, utilization)
- ✅ No existing files were overwritten
- ✅ All generated files have valid frontmatter
</success_criteria>
```

**Step 2: Create workflow init-empty.md**

```markdown
<objective>
Scaffold an empty knowledge base with the standard directory structure and template files.
</objective>

<required_reading>
Load `references/kb-spec-summary.md` for context on the KB specification.
</required_reading>

<process>
## Step 1: Determine target directory

If `$ARGUMENTS` contains a path, use that. Otherwise use the current working directory.

Confirm with user: "I'll create a knowledge base in `<directory>`. What role does this KB serve? (e.g., 'Paid Media Analyst', 'Platform Engineer')"

## Step 2: Run scaffold script

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/scaffold.py --target <directory> --role "<role_name>"
```

## Step 3: Report results

Show the user what was created and suggest next steps:
- "Use `/dewey:curate add` to start adding topics"
- "Edit AGENTS.md to refine the persona definition"
- "Create domain area directories as your KB takes shape"
</process>

<success_criteria>
- Directory structure created
- AGENTS.md generated with role name
- index.md generated
- User informed of next steps
</success_criteria>
```

**Step 3: Create workflow init-from-role.md**

```markdown
<objective>
Propose initial domain areas based on a role description, then scaffold the knowledge base.
</objective>

<required_reading>
Load `references/kb-spec-summary.md` for context on the KB specification.
</required_reading>

<process>
## Step 1: Determine target directory and role

Parse `$ARGUMENTS` for `--role "Role Name"` and optional target directory.

## Step 2: Propose domain areas

Based on the role name, propose 3-5 domain areas that reflect how a practitioner in this role thinks about their work. Present to the user:

"For a **<role name>**, I'd suggest organizing the knowledge base around these domain areas:

1. **Area Name** -- brief description of what this covers
2. **Area Name** -- brief description
3. **Area Name** -- brief description

These should map to the major responsibility areas of the role. Would you like to adjust these before I create the structure?"

**Key principle:** Domain-Shaped Organization. Use the practitioner's mental model, not technical categories.

## Step 3: Run scaffold script with areas

After user confirms or adjusts:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/scaffold.py --target <directory> --role "<role_name>" --areas "<area1>,<area2>,<area3>"
```

## Step 4: Report results

Show what was created. For each domain area, note the overview.md that was generated and suggest the user start by:
- Filling in the "What This Covers" section of each overview.md
- Identifying 2-3 primary sources per domain area
- Using `/dewey:curate add` to create the first topics
</process>

<success_criteria>
- Domain areas proposed and confirmed by user
- Directory structure created with domain area directories
- Each domain area has an overview.md
- AGENTS.md manifest includes all domain areas
- User has clear next steps for populating the KB
</success_criteria>
```

**Step 4: Create reference kb-spec-summary.md**

```markdown
# Knowledge Base Specification Summary

Reference for the full spec: `docs/plans/2026-02-14-knowledge-base-spec-design.md`

## Core Principles

1. **Source Primacy** -- Curate and point to primary sources, don't replace them
2. **Dual Audience** -- Serve both agent (efficient) and human (learnable)
3. **Three-Dimensional Quality** -- Relevance, accuracy/freshness, structural fitness
4. **Collaborative Curation** -- Human judgment + agent coverage, both validated
5. **Provenance & Traceability** -- Every entry carries source and validation date
6. **Domain-Shaped Organization** -- Structure mirrors the practitioner's mental model
7. **Right-Sized Scope** -- Include what's needed, exclude what isn't
8. **Empirical Feedback** -- Observable signals guide curation decisions
9. **Progressive Disclosure** -- Layered: metadata -> summary -> full -> deep
10. **Explain the Why** -- Causal reasoning, not just facts
11. **Concrete Before Abstract** -- Examples first, then generalize
12. **Multiple Representations** -- Important concepts at multiple depths

## Directory Structure

```
project-root/
├── AGENTS.md                       # Persona + manifest
├── knowledge/
│   ├── index.md                    # Human TOC
│   ├── <domain-area>/
│   │   ├── overview.md             # Orientation (depth: overview)
│   │   ├── <topic>.md              # Working knowledge (depth: working)
│   │   └── <topic>.ref.md          # Expert reference (depth: reference)
│   └── _proposals/                 # Staged additions
└── .dewey/
    ├── health/                     # Quality scores
    ├── history/                    # Change log
    └── utilization/                # Reference tracking
```

## Content Format

All knowledge files carry YAML frontmatter:
- `sources` -- primary source URLs
- `last_validated` -- date of last verification
- `relevance` -- one-line description of who this helps
- `depth` -- overview | working | reference

## AGENTS.md Constraints

- Under 100 lines
- Defines role persona and behavioral expectations
- Manifest: names and one-line descriptions only (progressive disclosure Level 1)
```

**Step 5: Commit**

```bash
git add skills/init/
git commit -m "feat: add /dewey:init skill with workflows and references"
```

---

### Task 4: Wire scaffold.py for CLI usage

**Files:**
- Modify: `skills/init/scripts/scaffold.py` (add `if __name__ == "__main__"` block)
- Test: `tests/skills/init/test_scaffold_cli.py`

**Step 1: Write the failing test**

```python
"""Tests for scaffold CLI interface."""
import unittest
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent.parent.parent / "skills" / "init" / "scripts" / "scaffold.py"


class TestScaffoldCli(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_cli_creates_kb(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--target", str(self.tmpdir), "--role", "Test Role"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue((self.tmpdir / "AGENTS.md").exists())

    def test_cli_with_areas(self):
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT_PATH),
                "--target", str(self.tmpdir),
                "--role", "Test Role",
                "--areas", "Area One,Area Two",
            ],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue((self.tmpdir / "knowledge" / "area-one" / "overview.md").exists())
        self.assertTrue((self.tmpdir / "knowledge" / "area-two" / "overview.md").exists())

    def test_cli_outputs_summary(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--target", str(self.tmpdir), "--role", "Test Role"],
            capture_output=True, text=True,
        )
        self.assertIn("created", result.stdout)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/skills/init/test_scaffold_cli.py -v`
Expected: FAIL — no CLI entry point

**Step 3: Add CLI entry point to scaffold.py**

Append to `skills/init/scripts/scaffold.py`:

```python
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scaffold a knowledge base.")
    parser.add_argument("--target", required=True, help="Target directory")
    parser.add_argument("--role", required=True, help="Role name")
    parser.add_argument("--areas", default="", help="Comma-separated domain area names")
    args = parser.parse_args()

    areas = [a.strip() for a in args.areas.split(",") if a.strip()] if args.areas else []
    result = scaffold_kb(Path(args.target), args.role, areas)
    print(result)
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/skills/init/test_scaffold_cli.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add skills/init/scripts/scaffold.py tests/skills/init/test_scaffold_cli.py
git commit -m "feat: add CLI interface to scaffold script"
```

---

## Phase 2: `/dewey:curate` — Content Lifecycle

### Task 5: Create topic creation script

**Files:**
- Create: `skills/curate/scripts/create_topic.py`
- Test: `tests/skills/curate/test_create_topic.py`

**Step 1: Write the failing test**

```python
"""Tests for topic creation."""
import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "skills" / "curate" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "skills" / "init" / "scripts"))

from create_topic import create_topic


class TestCreateTopic(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        # Set up a minimal KB structure
        (self.tmpdir / "knowledge" / "campaign-management").mkdir(parents=True)
        (self.tmpdir / "knowledge" / "_proposals").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_topic_file(self):
        create_topic(
            kb_root=self.tmpdir,
            area="campaign-management",
            topic_name="Budget Allocation",
            relevance="How to distribute budget across campaigns",
        )
        topic_path = self.tmpdir / "knowledge" / "campaign-management" / "budget-allocation.md"
        self.assertTrue(topic_path.exists())

    def test_creates_reference_file(self):
        create_topic(
            kb_root=self.tmpdir,
            area="campaign-management",
            topic_name="Budget Allocation",
            relevance="How to distribute budget",
        )
        ref_path = self.tmpdir / "knowledge" / "campaign-management" / "budget-allocation.ref.md"
        self.assertTrue(ref_path.exists())

    def test_topic_has_correct_depth(self):
        create_topic(
            kb_root=self.tmpdir,
            area="campaign-management",
            topic_name="Budget Allocation",
            relevance="How to distribute budget",
        )
        content = (self.tmpdir / "knowledge" / "campaign-management" / "budget-allocation.md").read_text()
        self.assertIn("depth: working", content)

    def test_ref_has_correct_depth(self):
        create_topic(
            kb_root=self.tmpdir,
            area="campaign-management",
            topic_name="Budget Allocation",
            relevance="How to distribute budget",
        )
        content = (self.tmpdir / "knowledge" / "campaign-management" / "budget-allocation.ref.md").read_text()
        self.assertIn("depth: reference", content)

    def test_does_not_overwrite_existing(self):
        topic_path = self.tmpdir / "knowledge" / "campaign-management" / "budget-allocation.md"
        topic_path.write_text("existing content")
        create_topic(
            kb_root=self.tmpdir,
            area="campaign-management",
            topic_name="Budget Allocation",
            relevance="How to distribute budget",
        )
        self.assertEqual(topic_path.read_text(), "existing content")

    def test_raises_if_area_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            create_topic(
                kb_root=self.tmpdir,
                area="nonexistent-area",
                topic_name="Topic",
                relevance="Relevance",
            )

    def test_returns_summary(self):
        result = create_topic(
            kb_root=self.tmpdir,
            area="campaign-management",
            topic_name="Budget Allocation",
            relevance="How to distribute budget",
        )
        self.assertIn("budget-allocation.md", result)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/skills/curate/test_create_topic.py -v`
Expected: FAIL — module does not exist

**Step 3: Implement create_topic.py**

```python
"""Create new topic files in a knowledge base.

Generates both the working knowledge file (<topic>.md) and the
expert reference file (<topic>.ref.md) from templates.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "init" / "scripts"))
from templates import render_topic_md, render_topic_ref_md


def create_topic(
    kb_root: Path,
    area: str,
    topic_name: str,
    relevance: str,
) -> str:
    """Create a new topic with working and reference files.

    Args:
        kb_root: Root of the knowledge base.
        area: Domain area directory name (e.g., "campaign-management").
        topic_name: Human-readable topic name (e.g., "Budget Allocation").
        relevance: One-line relevance statement.

    Returns:
        Summary of what was created.

    Raises:
        FileNotFoundError: If the domain area directory doesn't exist.
    """
    area_dir = kb_root / "knowledge" / area
    if not area_dir.is_dir():
        raise FileNotFoundError(f"Domain area not found: {area_dir}")

    slug = _slugify(topic_name)
    created = []

    topic_path = area_dir / f"{slug}.md"
    if not topic_path.exists():
        topic_path.write_text(render_topic_md(topic_name, relevance))
        created.append(str(topic_path.relative_to(kb_root)))

    ref_path = area_dir / f"{slug}.ref.md"
    if not ref_path.exists():
        ref_path.write_text(render_topic_ref_md(topic_name, f"Quick reference for {topic_name.lower()}"))
        created.append(str(ref_path.relative_to(kb_root)))

    if created:
        return f"Created:\n" + "\n".join(f"  {c}" for c in created)
    return f"Both files already exist for '{topic_name}' in {area}."


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("/", "-")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a new KB topic.")
    parser.add_argument("--kb-root", required=True, help="KB root directory")
    parser.add_argument("--area", required=True, help="Domain area directory name")
    parser.add_argument("--topic", required=True, help="Topic name")
    parser.add_argument("--relevance", required=True, help="One-line relevance statement")
    args = parser.parse_args()

    result = create_topic(Path(args.kb_root), args.area, args.topic, args.relevance)
    print(result)
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/skills/curate/test_create_topic.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add skills/curate/scripts/create_topic.py tests/skills/curate/test_create_topic.py
git commit -m "feat: add topic creation script for /dewey:curate"
```

---

### Task 6: Create proposal and promote scripts

**Files:**
- Create: `skills/curate/scripts/propose.py`
- Create: `skills/curate/scripts/promote.py`
- Test: `tests/skills/curate/test_propose.py`
- Test: `tests/skills/curate/test_promote.py`

**Step 1: Write failing tests for propose**

```python
"""Tests for proposal creation."""
import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "skills" / "curate" / "scripts"))

from propose import create_proposal


class TestCreateProposal(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / "knowledge" / "_proposals").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_proposal_file(self):
        create_proposal(
            kb_root=self.tmpdir,
            topic_name="New Topic",
            relevance="Why this matters",
            proposed_by="human",
            rationale="Coverage gap",
        )
        proposal_path = self.tmpdir / "knowledge" / "_proposals" / "new-topic.md"
        self.assertTrue(proposal_path.exists())

    def test_proposal_has_status(self):
        create_proposal(
            kb_root=self.tmpdir,
            topic_name="New Topic",
            relevance="Why this matters",
            proposed_by="agent",
            rationale="Coverage gap",
        )
        content = (self.tmpdir / "knowledge" / "_proposals" / "new-topic.md").read_text()
        self.assertIn("status: proposal", content)
        self.assertIn("proposed_by: agent", content)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Write failing tests for promote**

```python
"""Tests for proposal promotion."""
import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "skills" / "curate" / "scripts"))

from promote import promote_proposal


class TestPromoteProposal(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / "knowledge" / "_proposals").mkdir(parents=True)
        (self.tmpdir / "knowledge" / "campaign-management").mkdir(parents=True)
        # Create a proposal
        proposal = self.tmpdir / "knowledge" / "_proposals" / "budget-tips.md"
        proposal.write_text("---\nstatus: proposal\nproposed_by: human\nrationale: \"needed\"\nsources:\n  - url: https://example.com\n    title: Example\nlast_validated: 2026-02-14\nrelevance: \"Budget tips\"\ndepth: working\n---\n\n# Budget Tips\n\nContent here.\n")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_moves_proposal_to_area(self):
        promote_proposal(
            kb_root=self.tmpdir,
            proposal_name="budget-tips",
            target_area="campaign-management",
        )
        promoted = self.tmpdir / "knowledge" / "campaign-management" / "budget-tips.md"
        self.assertTrue(promoted.exists())

    def test_removes_proposal_status_from_frontmatter(self):
        promote_proposal(
            kb_root=self.tmpdir,
            proposal_name="budget-tips",
            target_area="campaign-management",
        )
        content = (self.tmpdir / "knowledge" / "campaign-management" / "budget-tips.md").read_text()
        self.assertNotIn("status: proposal", content)
        self.assertNotIn("proposed_by:", content)
        self.assertNotIn("rationale:", content)

    def test_removes_original_proposal(self):
        promote_proposal(
            kb_root=self.tmpdir,
            proposal_name="budget-tips",
            target_area="campaign-management",
        )
        original = self.tmpdir / "knowledge" / "_proposals" / "budget-tips.md"
        self.assertFalse(original.exists())

    def test_raises_if_proposal_not_found(self):
        with self.assertRaises(FileNotFoundError):
            promote_proposal(
                kb_root=self.tmpdir,
                proposal_name="nonexistent",
                target_area="campaign-management",
            )

    def test_raises_if_target_area_not_found(self):
        with self.assertRaises(FileNotFoundError):
            promote_proposal(
                kb_root=self.tmpdir,
                proposal_name="budget-tips",
                target_area="nonexistent-area",
            )


if __name__ == "__main__":
    unittest.main()
```

**Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/skills/curate/test_propose.py tests/skills/curate/test_promote.py -v`
Expected: FAIL — modules don't exist

**Step 4: Implement propose.py**

```python
"""Create proposals for new KB content."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "init" / "scripts"))
from templates import render_proposal_md


def create_proposal(
    kb_root: Path,
    topic_name: str,
    relevance: str,
    proposed_by: str,
    rationale: str,
) -> str:
    """Create a proposal in _proposals/."""
    proposals_dir = kb_root / "knowledge" / "_proposals"
    if not proposals_dir.is_dir():
        raise FileNotFoundError(f"Proposals directory not found: {proposals_dir}")

    slug = topic_name.lower().replace(" ", "-").replace("/", "-")
    proposal_path = proposals_dir / f"{slug}.md"

    if proposal_path.exists():
        return f"Proposal already exists: {proposal_path.relative_to(kb_root)}"

    proposal_path.write_text(render_proposal_md(topic_name, relevance, proposed_by, rationale))
    return f"Created proposal: {proposal_path.relative_to(kb_root)}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a KB proposal.")
    parser.add_argument("--kb-root", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--relevance", required=True)
    parser.add_argument("--proposed-by", default="human")
    parser.add_argument("--rationale", required=True)
    args = parser.parse_args()

    result = create_proposal(Path(args.kb_root), args.topic, args.relevance, args.proposed_by, args.rationale)
    print(result)
```

**Step 5: Implement promote.py**

```python
"""Promote validated proposals into the knowledge base."""
import re
from pathlib import Path


def promote_proposal(
    kb_root: Path,
    proposal_name: str,
    target_area: str,
) -> str:
    """Move a proposal from _proposals/ into a domain area.

    Removes proposal-specific frontmatter (status, proposed_by, rationale)
    and moves the file to the target domain area.
    """
    proposal_path = kb_root / "knowledge" / "_proposals" / f"{proposal_name}.md"
    if not proposal_path.exists():
        raise FileNotFoundError(f"Proposal not found: {proposal_path}")

    target_dir = kb_root / "knowledge" / target_area
    if not target_dir.is_dir():
        raise FileNotFoundError(f"Target area not found: {target_dir}")

    content = proposal_path.read_text()
    content = _strip_proposal_frontmatter(content)

    target_path = target_dir / f"{proposal_name}.md"
    target_path.write_text(content)
    proposal_path.unlink()

    return f"Promoted: _proposals/{proposal_name}.md -> {target_area}/{proposal_name}.md"


def _strip_proposal_frontmatter(content: str) -> str:
    """Remove proposal-specific fields from frontmatter."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content

    in_frontmatter = True
    result_lines = ["---"]
    skip_fields = {"status", "proposed_by", "rationale"}

    for line in lines[1:]:
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
                result_lines.append(line)
                continue
            field_match = re.match(r"^(\w+):", line)
            if field_match and field_match.group(1) in skip_fields:
                continue
            result_lines.append(line)
        else:
            result_lines.append(line)

    return "\n".join(result_lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Promote a KB proposal.")
    parser.add_argument("--kb-root", required=True)
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--target-area", required=True)
    args = parser.parse_args()

    result = promote_proposal(Path(args.kb_root), args.proposal, args.target_area)
    print(result)
```

**Step 6: Run tests to verify they pass**

Run: `python -m pytest tests/skills/curate/test_propose.py tests/skills/curate/test_promote.py -v`
Expected: All PASS

**Step 7: Commit**

```bash
git add skills/curate/scripts/propose.py skills/curate/scripts/promote.py tests/skills/curate/test_propose.py tests/skills/curate/test_promote.py
git commit -m "feat: add propose and promote scripts for /dewey:curate"
```

---

### Task 7: Create curate SKILL.md and workflows

**Files:**
- Create: `skills/curate/SKILL.md`
- Create: `skills/curate/workflows/curate-add.md`
- Create: `skills/curate/workflows/curate-propose.md`
- Create: `skills/curate/workflows/curate-promote.md`
- Create: `skills/curate/workflows/curate-ingest.md`

**Step 1: Create SKILL.md**

Follow the pattern from Task 3. Routing:
- `add` or `--add` → `workflows/curate-add.md`
- `propose` or `--propose` → `workflows/curate-propose.md`
- `promote` or `--promote` → `workflows/curate-promote.md`
- `ingest` or `--ingest` → `workflows/curate-ingest.md`
- No arguments → interactive menu

**Step 2: Create workflows**

Each workflow follows the pattern from init workflows:
- `curate-add.md` — Asks for domain area, topic name, relevance. Runs `create_topic.py`. Reminds user to fill in template sections.
- `curate-propose.md` — Asks for topic, relevance, rationale. Runs `propose.py`. Notes that proposals need validation before promotion.
- `curate-promote.md` — Lists pending proposals. User selects one and target area. Runs `promote.py`. Reminds to update AGENTS.md manifest and index.md.
- `curate-ingest.md` — (Stub) Accepts a URL. Creates a proposal with the URL pre-filled in frontmatter sources. Notes that the human/agent should distill the source content into the template sections.

**Step 3: Commit**

```bash
git add skills/curate/
git commit -m "feat: add /dewey:curate skill with workflows"
```

---

## Phase 3: `/dewey:health` — Quality Validation + Reporting

### Task 8: Create Tier 1 deterministic validators

**Files:**
- Create: `skills/health/scripts/validators.py`
- Test: `tests/skills/health/test_validators.py`

**Step 1: Write failing tests**

Test each deterministic check individually:

```python
"""Tests for Tier 1 deterministic KB validators."""
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import date, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "skills" / "health" / "scripts"))

from validators import (
    check_frontmatter,
    check_section_ordering,
    check_cross_references,
    check_size_bounds,
    check_coverage,
    check_freshness,
    check_source_urls,
)


class TestCheckFrontmatter(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_valid_frontmatter_passes(self):
        f = self.tmpdir / "topic.md"
        f.write_text('---\nsources:\n  - url: https://example.com\n    title: Example\nlast_validated: 2026-02-14\nrelevance: "Test"\ndepth: working\n---\n\n# Topic\n')
        issues = check_frontmatter(f)
        self.assertEqual(len(issues), 0)

    def test_missing_sources_fails(self):
        f = self.tmpdir / "topic.md"
        f.write_text('---\nlast_validated: 2026-02-14\nrelevance: "Test"\ndepth: working\n---\n\n# Topic\n')
        issues = check_frontmatter(f)
        self.assertTrue(any("sources" in i["message"] for i in issues))

    def test_invalid_depth_fails(self):
        f = self.tmpdir / "topic.md"
        f.write_text('---\nsources:\n  - url: https://example.com\n    title: Example\nlast_validated: 2026-02-14\nrelevance: "Test"\ndepth: invalid\n---\n\n# Topic\n')
        issues = check_frontmatter(f)
        self.assertTrue(any("depth" in i["message"] for i in issues))


class TestCheckSectionOrdering(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_correct_order_passes(self):
        f = self.tmpdir / "topic.md"
        f.write_text('---\ndepth: working\n---\n\n# T\n\n## Why This Matters\n\nText\n\n## In Practice\n\nText\n\n## Key Guidance\n\nText\n')
        issues = check_section_ordering(f)
        self.assertEqual(len(issues), 0)

    def test_wrong_order_fails(self):
        f = self.tmpdir / "topic.md"
        f.write_text('---\ndepth: working\n---\n\n# T\n\n## Key Guidance\n\nText\n\n## In Practice\n\nText\n')
        issues = check_section_ordering(f)
        self.assertTrue(len(issues) > 0)

    def test_only_checks_working_depth(self):
        f = self.tmpdir / "topic.ref.md"
        f.write_text('---\ndepth: reference\n---\n\n# T -- Reference\n')
        issues = check_section_ordering(f)
        self.assertEqual(len(issues), 0)


class TestCheckFreshness(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_recent_date_passes(self):
        f = self.tmpdir / "topic.md"
        f.write_text(f'---\nlast_validated: {date.today().isoformat()}\n---\n')
        issues = check_freshness(f, max_age_days=90)
        self.assertEqual(len(issues), 0)

    def test_old_date_fails(self):
        old = (date.today() - timedelta(days=100)).isoformat()
        f = self.tmpdir / "topic.md"
        f.write_text(f'---\nlast_validated: {old}\n---\n')
        issues = check_freshness(f, max_age_days=90)
        self.assertTrue(len(issues) > 0)


class TestCheckCoverage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / "knowledge" / "area-one").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_area_without_overview_fails(self):
        issues = check_coverage(self.tmpdir)
        self.assertTrue(any("overview.md" in i["message"] for i in issues))

    def test_topic_without_ref_fails(self):
        (self.tmpdir / "knowledge" / "area-one" / "overview.md").write_text("# Overview\n")
        (self.tmpdir / "knowledge" / "area-one" / "some-topic.md").write_text("# Topic\n")
        issues = check_coverage(self.tmpdir)
        self.assertTrue(any("ref.md" in i["message"] for i in issues))


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/skills/health/test_validators.py -v`
Expected: FAIL — module does not exist

**Step 3: Implement validators.py**

Implement each validator function. Each returns a list of issue dicts: `{"file": str, "message": str, "severity": "fail"|"warn"}`. Use stdlib only: `re` for frontmatter parsing, `pathlib` for file operations, `datetime` for freshness checks, `urllib.request` for URL checks.

Key implementation notes:
- Parse YAML frontmatter with simple regex (avoid PyYAML dependency) — split on `---` delimiters, parse `key: value` lines
- Section ordering: extract `## ` headings, check "In Practice" index < "Key Guidance" index for `depth: working` files
- Cross-references: extract markdown links `[text](path)`, resolve relative to file, check existence
- Size bounds: configurable per depth level (overview: 10-100 lines, working: 20-300, reference: 5-100)

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/skills/health/test_validators.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add skills/health/scripts/validators.py tests/skills/health/test_validators.py
git commit -m "feat: add Tier 1 deterministic KB validators"
```

---

### Task 9: Create health check runner

**Files:**
- Create: `skills/health/scripts/check_kb.py`
- Test: `tests/skills/health/test_check_kb.py`

**Step 1: Write failing tests**

Test the runner that orchestrates all validators across a KB:

```python
"""Tests for KB health check runner."""
import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "skills" / "health" / "scripts"))

from check_kb import run_health_check


class TestRunHealthCheck(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        # Scaffold a minimal KB
        (self.tmpdir / "knowledge" / "test-area").mkdir(parents=True)
        (self.tmpdir / "knowledge" / "_proposals").mkdir(parents=True)
        (self.tmpdir / "AGENTS.md").write_text("# Role: Test\n")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_returns_structured_report(self):
        report = run_health_check(self.tmpdir)
        self.assertIn("issues", report)
        self.assertIn("summary", report)

    def test_reports_missing_overview(self):
        report = run_health_check(self.tmpdir)
        issues = report["issues"]
        self.assertTrue(any("overview" in i["message"] for i in issues))

    def test_clean_kb_has_no_failures(self):
        # Create a valid overview
        (self.tmpdir / "knowledge" / "test-area" / "overview.md").write_text(
            '---\nsources:\n  - url: https://example.com\n    title: Ex\nlast_validated: 2026-02-14\nrelevance: "Test"\ndepth: overview\n---\n\n# Test Area\n\n## What This Covers\n\nTest.\n\n## How It\'s Organized\n\n## Key Sources\n'
        )
        report = run_health_check(self.tmpdir)
        failures = [i for i in report["issues"] if i["severity"] == "fail"]
        self.assertEqual(len(failures), 0)

    def test_summary_includes_counts(self):
        report = run_health_check(self.tmpdir)
        self.assertIn("total_files", report["summary"])
        self.assertIn("fail_count", report["summary"])
        self.assertIn("warn_count", report["summary"])


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run tests, implement, run tests, commit**

Following the same TDD pattern. The runner:
- Discovers all `.md` files in `knowledge/`
- Runs applicable validators on each file
- Aggregates results into a structured report
- Outputs JSON for Claude to interpret

```bash
git add skills/health/scripts/check_kb.py tests/skills/health/test_check_kb.py
git commit -m "feat: add KB health check runner"
```

---

### Task 10: Create health SKILL.md and workflows

**Files:**
- Create: `skills/health/SKILL.md`
- Create: `skills/health/workflows/health-check.md`
- Create: `skills/health/workflows/health-audit.md`
- Create: `skills/health/workflows/health-review.md`
- Create: `skills/health/workflows/health-coverage.md`
- Create: `skills/health/workflows/health-freshness.md`
- Create: `skills/health/references/validation-rules.md`
- Create: `skills/health/references/quality-dimensions.md`

**Step 1: Create SKILL.md**

Routing:
- `check` or `--check` → `workflows/health-check.md` (Tier 1 only, fast)
- `audit` or `--audit` → `workflows/health-audit.md` (Tier 1 + Tier 2 LLM)
- `review` → `workflows/health-review.md` (Surface Tier 3 items)
- `coverage` → `workflows/health-coverage.md` (Gap analysis)
- `freshness` → `workflows/health-freshness.md` (Staleness report)
- No arguments → runs `check` (safe default)

**Step 2: Create workflows**

- `health-check.md` — Runs `check_kb.py`, Claude formats the structured output into a readable report with priorities.
- `health-audit.md` — Runs Tier 1 checks first. For flagged items, Claude performs Tier 2 LLM assessment (source drift, depth accuracy, "why" quality, concrete example quality). Outputs combined report.
- `health-review.md` — Runs Tier 1 + 2, then surfaces Tier 3 items as a decision queue: "These items need your judgment: [list]. Would you like to go through them?"
- `health-coverage.md` — Parses AGENTS.md for responsibilities, compares against knowledge/ contents. Reports gaps and orphans.
- `health-freshness.md` — Extracts `last_validated` from all files, sorts by staleness, reports entries due for re-validation.

**Step 3: Create references**

- `validation-rules.md` — Complete list of Tier 1 checks with expected values and thresholds
- `quality-dimensions.md` — The three quality dimensions and how they map to checks

**Step 4: Commit**

```bash
git add skills/health/
git commit -m "feat: add /dewey:health skill with workflows and references"
```

---

## Phase 4: Integration and Registration

### Task 11: Register new skills in plugin manifest

**Files:**
- Modify: `dewey/.claude-plugin/plugin.json`

Update the plugin manifest to register the three new skills. Follow the existing pattern.

```bash
git add dewey/.claude-plugin/plugin.json
git commit -m "feat: register kb skills in plugin manifest"
```

---

### Task 12: End-to-end integration test

**Files:**
- Create: `tests/integration/test_kb_lifecycle.py`

**Step 1: Write an end-to-end test**

Test the full lifecycle: init a KB, add a topic, create a proposal, promote it, run health check.

```python
"""End-to-end test for KB lifecycle."""
import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Import all scripts
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "init" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "curate" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills" / "health" / "scripts"))

from scaffold import scaffold_kb
from create_topic import create_topic
from propose import create_proposal
from promote import promote_proposal
from check_kb import run_health_check


class TestKBLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_full_lifecycle(self):
        # 1. Init
        scaffold_kb(self.tmpdir, "Test Analyst", ["Domain A"])

        # 2. Add topic
        create_topic(self.tmpdir, "domain-a", "First Topic", "Testing the lifecycle")

        # 3. Propose
        create_proposal(self.tmpdir, "Second Topic", "Another test", "human", "Testing proposals")

        # 4. Promote
        promote_proposal(self.tmpdir, "second-topic", "domain-a")

        # 5. Verify structure
        self.assertTrue((self.tmpdir / "knowledge" / "domain-a" / "first-topic.md").exists())
        self.assertTrue((self.tmpdir / "knowledge" / "domain-a" / "second-topic.md").exists())
        self.assertFalse((self.tmpdir / "knowledge" / "_proposals" / "second-topic.md").exists())

        # 6. Health check
        report = run_health_check(self.tmpdir)
        self.assertIn("issues", report)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run tests, fix any issues, commit**

```bash
git add tests/integration/test_kb_lifecycle.py
git commit -m "test: add end-to-end KB lifecycle integration test"
```

---

## Summary

| Phase | Skill | Tasks | Key Deliverables |
|-------|-------|-------|------------------|
| 1 | `/dewey:init` | 1-4 | Templates, scaffold script, SKILL.md, 2 workflows |
| 2 | `/dewey:curate` | 5-7 | Topic creation, propose, promote, SKILL.md, 4 workflows |
| 3 | `/dewey:health` | 8-10 | Tier 1 validators, health runner, SKILL.md, 5 workflows |
| 4 | Integration | 11-12 | Plugin registration, end-to-end test |

**Total: 12 tasks, 3 skills, 11 workflows, ~6 Python modules, ~8 test files**
