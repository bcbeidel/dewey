# Skills Architecture Design

Date: 2026-02-17

Complementary design for the document type system. Defines the discovery layer
(how agents find and use the knowledge base) and the skills architecture
(what operations support the document lifecycle).

For the document type system this builds on, see:
- `2026-02-16-document-type-reference.md` (concise rules)
- `2026-02-16-document-type-specification.md` (normative spec with rationale)
- `2026-02-16-document-type-data-models.md` (Pydantic models and validators)

---

## 1. Design Foundation: Schema-First Architecture

Everything derives from the Pydantic document type models. The models are the
single source of truth; skills, validators, templates, and the discovery layer
are all consumers of model-defined dispatch tables.

```
Document Type Models (source of truth)
    |
    +-- Templates          "How do I create one?"
    +-- Validators          "Is this one valid?"
    +-- Section specs       "What sections does it have?"
    +-- Size bounds         "How big should it be?"
    +-- Directory rules     "Where does it live?"
    +-- Discovery rules     "Is it agent-facing?"
    +-- Lifecycle rules     "What happens to it over time?"
```

### Extension Protocol

Adding a new document type:

1. Add a Pydantic frontmatter model (e.g. `InitiativeFrontmatter`)
2. Add to the discriminated union (`Frontmatter`)
3. Add entries to dispatch tables: `SECTIONS`, `SIZE_BOUNDS`, `VALIDATORS_BY_TYPE`,
   `TIER2_TRIGGERS_BY_TYPE`, `DIRECTORY_PATTERNS`
4. Add a template function
5. Done — no skill routing changes, no discovery layer changes

### Document Types vs. Entity Types

The dispatch table mechanism is designed for **document types** — markdown files
with frontmatter and sections (topic, overview, research, plan, and future types
like initiative or guide).

**Entity types** (people, tasks, events) are a different category:
- More numerous (dozens/hundreds vs. tens)
- Smaller and more structured
- Need state management (status transitions, ordering, dependencies)
- May use different storage (single file, JSONL, structured YAML)

The schema-first **principle** (Pydantic models as source of truth, derive
validators from models) extends to entity types, but the dispatch table
**mechanism** is document-specific. Entity support would be a separate
extension when needed.

---

## 2. Discovery Layer

How agents discover what's in the knowledge base and how to use it.

### 2.1 CLAUDE.md as the Manifest

CLAUDE.md is the primary discovery surface. It contains a knowledge base section
with the topic/overview index — context types only. Artifacts (research, plans)
are not in the manifest; they are reachable through `related` links in context
documents.

```markdown
<!-- dewey:knowledge-base:begin -->
## Knowledge Base

### chess
[Overview](context/chess/overview.md)

| Topic | Description |
|-------|-------------|
| [Opening Principles](context/chess/opening-principles.md) | Core principles for the first 10-15 moves... |
| [Endgame Techniques](context/chess/endgame-techniques.md) | Converting material advantages... |

### cooking
[Overview](context/cooking/overview.md)

| Topic | Description |
|-------|-------------|
| [Knife Skills](context/cooking/knife-skills.md) | Fundamental cuts and techniques... |
<!-- dewey:knowledge-base:end -->
```

**Design rules:**
- **Context types only** — topics and overviews are the agent-facing surface
- **Auto-generated** from files on disk — never hand-edited within markers
- **Marker-delimited** — scaffold only touches content between
  `<!-- dewey:knowledge-base:begin/end -->` markers; user content outside
  markers is preserved
- **Description column** provides information scent — agents decide what to
  load without reading full files (progressive disclosure)

AGENTS.md mirrors the same content for provider-agnostic discovery.

### 2.2 Rules File

`.claude/rules/dewey-knowledge-base.md` teaches agents the document type system:

- What the four document types are and where they live
- When to consult existing documents vs. create new ones
- How to use `description` for lightweight scanning
- How to follow `related` links to artifacts
- Required frontmatter fields per type
- How to propose new content

This file is fully managed by scaffold — auto-generated, not user-edited.
Under 50 lines, actionable guidance only, no rationale.

### 2.3 Maintenance

Both CLAUDE.md manifest and the rules file are **derived artifacts** — the
source of truth is files on disk.

**Regeneration triggers:**
1. After every content operation (curate creates/promotes/deletes a document)
2. Health cross-validator `check_manifest_sync` detects drift
3. Explicit re-scaffold via setup skill

**Conflict resolution:**
- Content outside markers: user-owned, never modified
- Content inside markers: overwritten on regeneration (it is a cache)
- Rules file: fully managed, always overwritten

---

## 3. Skills Architecture

### 3.1 Design Principles

**Operation-aligned, not type-aligned.** Skills are organized around what you
do (setup, curate, validate, maintain), not what type you're working with.
Document type dispatch happens inside skills via the model dispatch tables.

**Health observes, maintain acts.** Health is read-only (can run in CI).
Maintain is write (requires approval). Separating them enables different
permission models.

**Free-text intake where possible.** Users describe intent; Claude classifies
and routes. No command memorization.

### 3.2 Core Skills (Tier 1)

These form the working system. Build first.

#### setup

**Purpose:** Initialize and scaffold a new knowledge base.

**Operations:**
- `setup-init`: Scaffold directory structure (`/context/`, `/artifacts/`),
  generate CLAUDE.md manifest section, create `.dewey/config.json`,
  generate rules file
- `setup-area`: Add a new domain area to an existing knowledge base
  (create area directory, overview.md, update manifest)

**Routing:** Does `.dewey/config.json` exist? No → init. Yes → area.

**Outputs:** Directory structure, CLAUDE.md section, AGENTS.md, rules file,
config file.

#### curate

**Purpose:** Create, update, and manage documents through their content
lifecycle.

**Operations:**
- `curate-add`: Create a new document of any type. Claude infers document type
  from user intent:
  - "I want to investigate X" → research document in `/artifacts/research/`
  - "Let's plan how to do Y" → plan document in `/artifacts/plans/`
  - "Add a topic about Z" → topic document in `/context/{area}/`
  - "Update the overview for {area}" → overview update
- `curate-ingest`: Pull content from URL, evaluate source quality (SIFT),
  create or update a document
- `curate-propose`: Submit a draft document for review
- `curate-promote`: Move a validated proposal into the knowledge base
- `curate-update`: Modify an existing document (preserving frontmatter
  integrity via Pydantic validation)

**Routing:** Free-text intent classification. State checks:
- No knowledge base → redirect to setup
- Has knowledge base → classify intent and route

**Type dispatch:** Templates, section specs, and frontmatter models are
selected via `document_type` from the dispatch tables. No type-specific
branching in routing logic.

#### health

**Purpose:** Observe and report on knowledge base quality. Read-only.

**Operations:**
- `health-check`: Tier 1 deterministic validation (fast, CI-friendly)
- `health-audit`: Tier 1 + Tier 2 LLM-assisted assessment
- `health-review`: Full assessment + Tier 3 human decision queue
- `health-coverage`: Gap analysis — what's missing from the knowledge base?
- `health-freshness`: Staleness report grouped by urgency

**Routing:** Keyword in arguments (check/audit/review/coverage/freshness).

**Type dispatch:** Validators are selected per document type from
`VALIDATORS_BY_TYPE` and `TIER2_TRIGGERS_BY_TYPE`. Adding a new document type
means adding entries to these tables; no validator code changes needed for
existing validators.

#### maintain

**Purpose:** Act on health signals. Write operations that modify the
knowledge base.

**Operations:**
- `maintain-fix`: Auto-fix common issues flagged by health
  (formatting, missing fields, section ordering)
- `maintain-lifecycle`: Transition document status
  (mark plan complete, archive old research)
- `maintain-regenerate`: Rebuild CLAUDE.md manifest and rules file from disk
- `maintain-cleanup`: Remove orphaned files, dead links, empty proposals

**Routing:** What action is needed? Often triggered by health report findings.

#### report-issue

**Purpose:** Submit feedback, bug reports, and feature ideas back to the
Dewey source repo. Lets users push context and relevant details from their
knowledge base usage back to the maintainers.

**Operations:**
- `report-issue-submit`: Gather feedback → classify (bug/feature/feedback) →
  draft issue with context → preview → submit via `gh`

**Routing:** Linear workflow, no conditional branching.

### 3.3 Capability Skills (Tier 2)

Enhance the quality of work that feeds the knowledge base. Build second.

#### research

**Purpose:** Deep investigation using evidence-based methodology. Produces
`research` documents.

**Core methodology: SIFT framework**
(Mike Caulfield, University of Washington)

| Step | Agent behavior |
|------|---------------|
| **Stop** | Don't include a source until it passes the next 3 checks |
| **Investigate the source** | Check domain authority, author credentials, organizational backing |
| **Find better coverage** | Search for the same claim from more authoritative sources |
| **Trace claims** | Follow citation chains to primary sources |

**Source hierarchy** (from `source-evaluation.md`):
```
Official docs > Institutional research > Peer-reviewed >
Expert practitioners > Community content > AI-generated
```

**Research modes:**

| Mode | Question shape | Emphasis |
|------|---------------|----------|
| Deep dive | "What do we know about X?" | Thorough SIFT on all sources, full citation chains, counter-evidence |
| Landscape | "What's the space around X?" | Breadth: map players, tools, trends, gaps. Lighter per-source eval |
| Technical | "How do we implement X?" | Approaches: libraries, patterns, tradeoffs. Weight official docs |
| Feasibility | "Can we actually do X?" | Constraint-focused: blockers, dependencies, unknowns |
| Competitive | "Who else does X and how?" | Comparative: feature grids, strengths/weaknesses |
| Options | "Should we use A or B?" | Side-by-side evaluation on same criteria |
| Historical | "What's been tried before?" | Prior attempts, lessons learned, what changed |
| Open source | "What existing tools solve X?" | Tool discovery: maturity, maintenance, adoption signals |

**Mode affects methodology intensity, not output structure.** All modes
produce a standard `research` document (Question → Findings → Implications →
Sources).

```
              Deep dive  Landscape  Technical  Feasibility
Source count    5-10+      10-20+    3-5        5-10
SIFT rigor     Full       Light     Full top 3  Full blockers
Counter-evidence Required  Optional  Required   Required
Citation trace  Deep       Shallow   Official   Primary
```

**Workflow:**
1. Frame the question (scope, success criteria)
2. Initial source gathering (breadth-first)
3. Source evaluation (SIFT per source, intensity per mode)
4. Synthesis (findings by sub-question, agreement/disagreement noted)
5. Implications ("so what" — how findings affect decisions)
6. Produce research document

**Quality differentiators vs. naive "search and summarize":**
- Source hierarchy enforcement (not all sources weighted equally)
- Counter-evidence requirement (active search for disagreement)
- Claim tracing (follow citation chains to primary sources)

#### consider

**Purpose:** Structured reasoning using mental models. Helps agents think
more clearly before researching, planning, or deciding.

**Pattern:** Follows the taches-cc-resources `consider:*` pattern — each
mental model is an independent command file. No parent orchestrator.

```
dewey/skills/consider/
  SKILL.md                    # Lists available models, routing
  models/
    first-principles.md       # /consider:first-principles
    occams-razor.md           # /consider:occams-razor
    inversion.md              # /consider:inversion
    second-order.md           # /consider:second-order
    eisenhower-matrix.md      # /consider:eisenhower-matrix
    opportunity-cost.md       # /consider:opportunity-cost
    via-negativa.md           # /consider:via-negativa
    pareto.md                 # /consider:pareto
    5-whys.md                 # /consider:5-whys
    swot.md                   # /consider:swot
    10-10-10.md               # /consider:10-10-10
    one-thing.md              # /consider:one-thing
    circle-of-competence.md   # /consider:circle-of-competence
    map-vs-territory.md       # /consider:map-vs-territory
    reversibility.md          # /consider:reversibility
    hanlons-razor.md          # /consider:hanlons-razor
```

**Each model file follows a uniform structure (~45 lines):**

```yaml
---
description: Brief description of the mental model
argument-hint: topic or question to analyze
---
```

```xml
<objective>
Apply [Framework] to $ARGUMENTS (or current discussion).
[1-2 sentence explanation of the framework.]
</objective>

<process>
1. [Step 1]
2. [Step 2]
...
</process>

<output_format>
**[Section 1]:**
- [template]
...
</output_format>

<success_criteria>
- [Criterion 1]
- [Criterion 2]
...
</success_criteria>
```

**Extending:** Add a new `.md` file in `models/` = new model available.
No routing changes, no registration step.

**Initial catalog (16 models, ported from taches + 4 new):**

| Model | When to use |
|-------|------------|
| First principles | Breaking down assumptions, building from fundamentals |
| Occam's razor | Choosing between explanations, simplifying |
| Inversion | Problem solving, risk identification |
| Second-order | Decision making, anticipating consequences |
| Eisenhower matrix | Prioritization, time management |
| Opportunity cost | Resource allocation, trade-off analysis |
| Via negativa | Improving by removing, simplifying systems |
| Pareto (80/20) | Focus, identifying leverage points |
| 5 Whys | Root cause analysis |
| SWOT | Strategic assessment |
| 10-10-10 | Decision making across time horizons |
| One thing | Identifying highest-leverage single action |
| Circle of competence | Scope decisions, knowing what you don't know |
| Map vs. territory | Recognizing model limitations |
| Reversibility | Decision risk assessment (one-way vs. two-way doors) |
| Hanlon's razor | Interpreting behavior, avoiding conspiracy thinking |

**Sources for model content:**
- Farnam Street (fs.blog/mental-models/) — curated latticework
- Charlie Munger's "Poor Charlie's Almanack" — interdisciplinary models
- Kahneman "Thinking, Fast and Slow" — cognitive bias awareness
- Shane Parrish "The Great Mental Models" series

**Landscape context:** Several implementations exist but none combine
well-sourced frameworks with the simple per-file extensibility pattern.
Notable prior art:
- [Jeffallan/claude-skills "The Fool"](https://github.com/Jeffallan/claude-skills) (3k stars) — adversarial thinking
- [m0n0x41d/quint-code](https://github.com/m0n0x41d/quint-code) (1.1k stars) — first principles with audit trails
- [clear-thought-patterns MCP](https://www.npmjs.com/package/@davenportsociety/clear-thought-patterns) — 16 thinking tools as MCP

### 3.4 Extended Skills (Tier 3)

Amplifiers for mature knowledge bases. Build when needed.

#### import

**Purpose:** Bulk ingestion from existing documentation into the document
type system.

**Operations:**
- Scan source directory for markdown files
- Classify each file → document type (topic, research, plan, overview)
- Convert frontmatter to required format
- Validate via health check
- Report: what converted cleanly, what needs manual review

**Sources:** Existing markdown docs, wiki exports, Notion exports,
Confluence exports.

#### observe

**Purpose:** Analytics and utilization tracking. Understand how the knowledge
base is actually used.

**Operations:**
- Track which documents agents read (via PostToolUse hooks)
- Surface patterns: high-use documents, never-referenced content,
  stale-but-frequently-read
- Generate recommendations: expand depth, archive unused, refresh stale

**Integration:** Feeds into health (coverage metrics) and maintain
(cleanup decisions).

#### history

**Purpose:** Track how knowledge evolves over time.

**Operations:**
- Document-level change tracking (git-based)
- Diff visualization between versions
- Knowledge archaeology: when was this claim added? What research informed it?
- Change attribution: who (human or agent) made each change?

**Integration:** Git is the storage backend. History reads git log, not a
separate database.

#### connect

**Purpose:** Integrate the knowledge base with external systems.

**Operations:**
- CI pipeline: run `health-check` as a CI step, fail on `severity: fail`
- Documentation site: generate static HTML from context documents
- Project tracker: sync plan status with external tracking tools

**Provider-specific:** Each integration is an adapter. The knowledge base
format is provider-agnostic; adapters handle the translation.

#### teach

**Purpose:** Help new agents and humans understand the knowledge base system.

**Operations:**
- Guided tour: walk through the structure, explain conventions
- Answer "how do I...?" questions about the system
- Explain document types, frontmatter fields, lifecycle
- Suggest next steps for someone new to the knowledge base

**This is the rules file made interactive.** Where the rules file is static
reference, teach is conversational guidance.

---

## 4. Skill Dependencies

```
                    consider --> research --> curate --> health --> maintain
                                            |          |          |
                                            |          |          +-- fix, lifecycle, regenerate
                                            |          +-- validate, report
                                            +-- create, update, promote

setup ------------------------------------------------> (foundation)
import ---------> curate ---------> health              (bulk path)
observe <------------------------------------------------ (reads from all)
history <------------------------------------------------ (tracks all changes)
connect ---------> health, observe                       (external pipes)
teach <-------------------------------------------------- (explains all)
```

### Build Order

| Phase | Skills | Rationale |
|-------|--------|-----------|
| 1. Core | setup, curate, health, maintain, report-issue | The working system |
| 2. Capabilities | research, consider | Improve content quality at the source |
| 3. Extended | import, observe, history, connect, teach | Amplifiers for mature KBs |

---

## 5. Type Dispatch Across Skills

The dispatch table pattern ensures consistency. Here is how each skill
uses the tables:

| Dispatch table | setup | curate | health | maintain |
|---------------|-------|--------|--------|----------|
| `SECTIONS` | — | Generate section headings | Validate section presence/order | — |
| `SIZE_BOUNDS` | — | Warn during creation | Validate size | — |
| `VALIDATORS_BY_TYPE` | — | — | Run per-type validators | Select auto-fixes |
| `TIER2_TRIGGERS_BY_TYPE` | — | — | Run per-type triggers | — |
| `DIRECTORY_PATTERNS` | Create directories | Place files correctly | Validate placement | — |
| `TEMPLATES` | — | Render new documents | — | — |
| Frontmatter models | — | Validate on create/update | Validate on check | Validate after fix |

Adding a new document type: add entries to these tables. Every skill that
consumes the tables automatically handles the new type.

---

## 6. Related Documents

| Document | Purpose |
|----------|---------|
| `2026-02-16-document-type-reference.md` | Concise rules for creating/validating documents |
| `2026-02-16-document-type-specification.md` | Normative rules with rationale |
| `2026-02-16-document-type-data-models.md` | Pydantic models, validation dispatch, Tier 2 triggers |
| `../artifacts/research/2026-02-17-document-type-system-deep-dive.md` | Research: evidence base from five investigation threads |
