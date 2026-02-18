# Deep Dive: Document Type System for Dual-Audience Knowledge Management

Date: 2026-02-17

## Strategic Summary

A four-type document system (topic, overview, research, plan) is well-grounded
across documentation standards, personal knowledge management, software
engineering practice, cognitive science, and agent context research. The key
insight is that these four types map to two axes: **distillation level**
(curated vs. raw) and **purpose** (reference vs. action). All four share a
common metadata core, but each type has distinct section structures, validation
rules, and lifecycle semantics. The research strongly supports deterministic
validation of structure and metadata across all types, with LLM-assisted
validation reserved for content quality.

## Key Questions This Research Answers

- What section structures work best for each document type?
- What metadata should be shared vs. type-specific?
- What can be validated deterministically vs. requires judgment?
- How do documentation standards, PKM systems, and cognitive science converge?
- How should documents be structured for dual human + AI agent consumption?

---

## 1. The Two-Axis Classification

The four document types map to a 2x2 matrix:

|                    | Reference (consult)       | Action (do/decide)      |
|--------------------|---------------------------|-------------------------|
| **Curated/Stable** | **Topic** + **Overview**  |                         |
| **Work Artifact**  | **Research**              | **Plan**                |

This mirrors patterns across multiple frameworks:

| Framework         | Curated Reference        | Work Artifact / Action       |
|-------------------|--------------------------|------------------------------|
| PARA              | Resources                | Projects                     |
| Zettelkasten      | Permanent notes          | Project notes                |
| Evergreen Notes   | Evergreen (declarative)  | Ephemeral / Log              |
| Diataxis          | Explanation + Reference  | How-to Guides                |
| DITA              | Concept + Reference      | Task                         |
| Software Eng.     | ADRs (accepted)          | RFCs (proposed), Plans       |

The `/context` vs. `/artifacts` directory split naturally encodes this axis:
distilled knowledge lives in `/context`, work products live in `/artifacts`.

---

## 2. Common Metadata (All Four Types)

Every surveyed system that succeeds at scale has machine-readable metadata.
The Agent Skills spec, Cursor `.mdc` files, MADR ADRs, and PEPs all use
frontmatter or structured headers. The convergence is clear:

### Required Fields (All Types)

| Field            | Type            | Purpose                                    | Grounding                                   |
|------------------|-----------------|--------------------------------------------|----------------------------------------------|
| `document_type`  | enum            | Route to correct validation + template     | DITA topic types, Diataxis quadrants         |
| `description`    | string (1-3 sentences) | Information scent for progressive disclosure | Agent Skills spec, Pirolli & Card IFT, DITA `<shortdesc>` |
| `last_updated`   | ISO 8601 date   | When content was last modified             | Dublin Core `Date.modified`, JATS `revised`  |

### Optional Fields (All Types)

| Field     | Type          | Purpose                                     |
|-----------|---------------|---------------------------------------------|
| `tags`    | list[string]  | Cross-cutting discovery across types         |
| `related` | list[path]    | Non-hierarchical connections to other records |
| `status`  | enum          | Lifecycle state (type-specific values)       |

### Type-Specific Required Fields

| Field              | Topic | Overview | Research | Plan |
|--------------------|:-----:|:--------:|:--------:|:----:|
| `sources`          | Yes   | No       | Yes      | No   |
| `last_validated`   | Yes   | Yes      | No       | No   |
| `status`           | No    | No       | Optional | Yes  |

**Rationale for each decision:**

- `sources` required for topic + research because both are grounded in external
  material. Overviews aggregate topics (not sources directly). Plans are
  forward-looking artifacts, not source-grounded.
- `last_validated` required for context types (topic + overview) because they
  must stay fresh. Research is a point-in-time snapshot. Plans are ephemeral.
- `status` required for plans because they have an active lifecycle
  (draft/active/complete/abandoned). Optional for research (complete vs.
  in-progress). Context types don't need status -- staleness is tracked via
  `last_validated`.

---

## 3. Cross-Cutting Design Principles

Seven cognitive science principles and three agent context findings converge
on consistent structural recommendations:

### Front-Load Critical Content

- **Serial position effect** (Ebbinghaus/Murdock): First and last items are
  recalled best; middle is recalled worst.
- **Lost in the Middle** (Liu et al., 2024): LLMs show the same U-shaped
  pattern -- 30%+ degradation when relevant info is in the middle.
- **Information foraging** (Pirolli & Card): Readers evaluate "information
  scent" from the first content they see to decide whether to continue.

**Design rule**: Every document type should open with a summary or the most
actionable content. Never bury key information in the middle.

### Keep Documents Short and Focused

- **Context rot** (Chroma, 2025): 13.9-85% performance degradation as input
  tokens increase, even with perfect retrieval.
- **300 vs. 113K finding**: Focused prompts outperform full context by 30-60%.
- **EPPO self-containment**: Each document should fulfill its purpose without
  requiring other documents to be loaded alongside it.

**Design rule**: Each document should be under 5,000 tokens. Move detail to
linked documents rather than expanding a single file.

### Use Progressive Disclosure

- **Agent Skills spec**: 3-tier model (~100 tokens metadata, <5,000 tokens
  body, unbounded references).
- **Cursor `.mdc`**: Agent-Requested mode uses description for routing,
  loads full body only when relevant.
- **DITA maps + `<shortdesc>`**: Metadata layer enables scan-before-load.

**Design rule**: `description` field (~50 tokens) enables scanning 20+
documents for ~1,000 tokens. Full content loads only when needed.

### Label Document Depth Explicitly

- **Expertise reversal effect** (Kalyuga et al., 2003): Material designed
  for novices actively hinders experts and vice versa.
- **Matuschak's "titles as APIs"**: Well-titled notes can be selected or
  rejected without reading their content.
- **EPPO "stays on one level"**: Each document should operate at one
  abstraction level.

**Design rule**: `document_type` serves as an explicit level label. Agents
and humans self-select the appropriate depth.

### Include "Why" Reasoning

- **Elaborative interrogation** (Dunlosky et al., 2013): "Why" explanations
  improve comprehension for humans.
- **Agent reasoning**: Causal explanations in context help agents adapt
  principles to novel situations. Rules without rationale can only be applied
  literally.
- **Desirable difficulties** (Bjork, 1994): Counter-evidence and exceptions
  create discriminative contrast that improves decision quality.

**Design rule**: All types should explain rationale, not just prescribe.
Plans explain why this approach; research explains why these findings matter;
topics explain why guidance works.

---

## 4. Per-Type Analysis

### 4.1 Topic (Distilled Actionable Knowledge)

**Lives in**: `/context/{area}/{topic}.md`

**Analogues across frameworks**:

| Framework          | Analogue                                         |
|--------------------|--------------------------------------------------|
| DITA               | Task topic + Concept topic (merged)              |
| Diataxis           | How-to Guide + Explanation (merged)              |
| EPPO               | Domain-specific topic pattern                    |
| Information Mapping | Principle + Procedure information types           |
| Zettelkasten       | Permanent note (declarative)                     |
| Evergreen Notes    | Evergreen note (declarative claim)               |
| PARA               | Resource                                          |

**Section structure** (current, validated by research):

| Section       | Position | Cognitive Rationale                              |
|---------------|----------|--------------------------------------------------|
| Guidance      | 1st      | Primacy effect -- most actionable content first   |
| Context       | 2nd      | Elaborative interrogation -- the "why"            |
| In Practice   | 3rd      | Dual coding -- concrete examples in attention valley |
| Pitfalls      | 4th      | Desirable difficulties + recency effect           |
| Go Deeper     | 5th      | Information foraging -- onward paths              |

**Validation (deterministic)**:
- Required sections present and in order
- Frontmatter fields valid (sources, last_validated, description)
- Size bounds (10-400 lines)
- Source diversity (2+ domains)
- Citation grounding (body URLs in sources)
- Readability (FK grade-level bounds)
- Heading hierarchy (one H1, no skipped levels)
- Placeholder detection
- Go Deeper links (external + internal)

**Validation (LLM-assisted)**:
- Source drift (are claims still current?)
- Depth accuracy (does document_type match content complexity?)
- Why quality (does Context section explain rationale?)
- In-Practice concreteness (are examples specific enough?)

### 4.2 Overview (Area Navigation and Orientation)

**Lives in**: `/context/{area}/overview.md`

**Analogues across frameworks**:

| Framework          | Analogue                                         |
|--------------------|--------------------------------------------------|
| DITA               | Map / Bookmap (structural overlay)               |
| Diataxis           | Explanation quadrant (orientation function)       |
| EPPO               | Structure note / Hub note                        |
| Obsidian           | Map of Content (MOC)                             |
| Zettelkasten       | Hub note / Structure note                        |
| Johnny Decimal     | Area-level index                                  |
| Agent Skills       | SKILL.md (discovery + routing metadata)          |

**Section structure**:

| Section          | Position | Rationale                                     |
|------------------|----------|-----------------------------------------------|
| What This Covers | 1st      | Information scent -- area-level orientation    |
| Topics           | 2nd      | Navigation hub -- progressive disclosure table |
| Key Sources      | 3rd      | Source primacy at area level                   |

**Validation (deterministic)**:
- Sections present and in order
- What This Covers >= 30 words
- Topics section contains a markdown table with Description column
- Bidirectional sync: table links <-> files on disk
- Frontmatter valid (last_validated, description)
- Size bounds (5-150 lines)
- Exactly one overview.md per area directory

**Validation (LLM-assisted)**:
- Coverage quality (does What This Covers provide genuine orientation?)
- Navigation quality (do descriptions provide information scent?)

### 4.3 Research (Investigation Artifacts)

**Lives in**: `/artifacts/research/{date}-{slug}.md`

**Analogues across frameworks**:

| Framework           | Analogue                                         |
|---------------------|--------------------------------------------------|
| Agile               | Technical spike document                         |
| Software Eng.       | RFC Motivation section (expanded to full doc)    |
| Google              | Design doc Context + Alternatives sections       |
| Zettelkasten        | Literature note (processed, source-attributed)   |
| PARA                | Progressive summarization Layer 4 (own words)    |
| Evergreen Notes     | Literature note (organized around a source/question) |

**Key insight from the research**: Spikes are explicitly "fact-finding, not
decision-making." Research documents produce evidence; decisions and plans
consume it. This clean interface means research documents should present
findings and implications without prescribing action.

**Recommended section structure**:

| Section       | Position | Rationale                                        |
|---------------|----------|--------------------------------------------------|
| Question      | 1st      | Primacy -- what we investigated and why           |
| Findings      | 2nd      | The bulk -- organized by sub-question or theme    |
| Implications  | 3rd      | So what -- how findings affect decisions          |
| Sources       | 4th      | Provenance -- what was consulted                  |

**Rationale for section choices**:
- **Question** (not "Abstract" or "Summary"): Research is driven by a question.
  Naming it explicitly creates stronger information scent -- a reader can
  decide in one line whether this investigation is relevant.
- **Findings** (not "Analysis"): The primary value is what was learned, not
  the methodology. Methodology can be noted within findings or in a
  subsection, but it should not consume a top-level section.
- **Implications** (not "Recommendations"): Research informs; it does not
  decide. Implications say "this means X for Y" without prescribing action.
  Recommendations belong in plans or topics that consume the research.
- **Sources**: Required because research is source-grounded. Unlike topics
  (which distill sources into guidance), research documents present the
  sources' content more directly.

**Validation (deterministic)**:
- Required sections present (Question, Findings, Sources at minimum)
- Frontmatter valid (sources list non-empty, description, last_updated)
- Size bounds (suggested: 20-600 lines -- research can be longer than topics)
- At least one source in frontmatter
- Question section non-empty
- Date prefix in filename matches last_updated

**Validation (LLM-assisted)**:
- Source authority (are sources credible for the domain?)
- Finding groundedness (do findings follow from cited sources?)
- Implication relevance (do implications connect to actionable concerns?)

### 4.4 Plan (Work Planning Artifacts)

**Lives in**: `/artifacts/plans/{date}-{slug}.md`

**Analogues across frameworks**:

| Framework           | Analogue                                       |
|---------------------|------------------------------------------------|
| PARA                | Project                                        |
| Agile               | Implementation plan / Sprint goal              |
| Google              | Design doc Goals/Non-Goals + Proposed Solution |
| Zettelkasten        | Project note (discarded after project)         |
| MADR                | ADR Context + Decision (action-oriented)       |

**Key insight from the research**: Plans have the most active lifecycle of
all four types. MADR's status enum (proposed/accepted/deprecated/superseded)
and Google's design doc lifecycle (draft/review/approved/archived) both show
that plans need explicit status tracking. Unlike context types that degrade
gradually (tracked via `last_validated`), plans transition between discrete
states.

**Recommended section structure**:

| Section        | Position | Rationale                                       |
|----------------|----------|-------------------------------------------------|
| Objective      | 1st      | Primacy -- what we're trying to accomplish       |
| Context        | 2nd      | Links to research/decisions that inform the plan |
| Steps          | 3rd      | The ordered work items                           |
| Verification   | 4th      | Recency -- how we know it's done                 |

**Rationale for section choices**:
- **Objective** (not "Summary"): Plans are goal-oriented. The objective
  answers "what will be true when this is done?" Google's design doc
  Goals/Non-Goals pattern is excellent -- consider optional Non-Goals
  subsection to prevent scope creep.
- **Context** (not "Background"): Links to research documents, prior
  decisions, or topics that inform the plan. This creates the natural
  document chain: Research -> Plan -> execution.
- **Steps**: Ordered work items. Each step should be independently
  verifiable. Microsoft's spike template and implementation plan templates
  both emphasize that each deliverable needs acceptance criteria.
- **Verification**: How success is measured. Implementation plans universally
  include acceptance criteria; curation plans should too. Placing this last
  exploits recency -- the verification criteria are fresh in mind when
  execution begins.

**Status enum**: `draft | active | complete | abandoned`

**Validation (deterministic)**:
- Required sections present (Objective, Steps at minimum)
- Frontmatter valid (status in enum, description, last_updated)
- Status field present and valid
- Size bounds (suggested: 10-300 lines)
- If status is "complete", all steps should be marked done
- Date prefix in filename

**Validation (LLM-assisted)**:
- Step specificity (are steps concrete enough to execute?)
- Verification completeness (do criteria cover the objective?)

---

## 5. Shared Validation Components

The research confirms that maximum reuse of validation components is
achievable. Here is a breakdown of what can be shared:

### Validators That Apply to All Four Types

| Validator                    | What It Checks                                |
|------------------------------|-----------------------------------------------|
| `check_frontmatter_fields`   | Required fields present, correct types         |
| `check_description_quality`  | 1-3 sentences, not a category label            |
| `check_title_heading`        | Exactly one H1                                 |
| `check_heading_hierarchy`    | No skipped levels, no extra H1s                |
| `check_size_bounds`          | Per-type min/max lines                         |
| `check_placeholder_comments` | No TODO/TBD stubs                              |
| `check_date_fields`          | Valid dates, not in the future                  |
| `check_naming_conventions`   | Slug-style filenames                            |

### Validators Shared by Subset

| Validator                  | Types           | Rationale                        |
|----------------------------|-----------------|----------------------------------|
| `check_section_presence`   | All four        | Each type has required sections  |
| `check_section_ordering`   | All four        | Each type has canonical order    |
| `check_source_diversity`   | Topic, Research | Both are source-grounded         |
| `check_citation_grounding` | Topic, Research | Body claims must trace to sources |
| `check_last_validated`     | Topic, Overview | Freshness tracking for context   |
| `check_readability`        | Topic, Overview | FK grade-level for distilled content |
| `check_status_field`       | Plan (required), Research (optional) | Lifecycle tracking |

### Type-Specific Validators

| Validator                    | Type     | What It Checks                     |
|------------------------------|----------|-------------------------------------|
| `check_go_deeper_links`     | Topic    | External + internal links present   |
| `check_overview_topic_sync` | Overview | Bidirectional table <-> disk sync   |
| `check_topics_table_format` | Overview | Table with Description column       |
| `check_research_question`   | Research | Question section non-empty          |
| `check_plan_status`         | Plan     | Status field in valid enum          |

### Cross-File Validators

| Validator                    | Scope    | What It Checks                     |
|------------------------------|----------|-------------------------------------|
| `check_link_graph`          | All      | Internal links resolve              |
| `check_duplicate_content`   | All      | No near-duplicate paragraphs        |
| `check_naming_conventions`  | All      | Consistent slug patterns            |
| `check_overview_topic_sync` | Context  | Overview table matches topic files  |

---

## 6. The Document Lifecycle Chain

The research on ADRs, RFCs, and planning documents reveals a natural flow:

```
Research --> informs --> Plan --> produces --> Topics + Overviews
                                         --> may trigger --> more Research

Research documents are snapshots. They do not update.
Plans are living documents until complete/abandoned.
Topics and overviews are maintained long-term via last_validated.
```

**Linking conventions**:
- Plans SHOULD reference the research documents that informed them (in Context)
- Topics MAY reference the plan that created them (in metadata or Go Deeper)
- Research documents link to their sources (in Sources section)
- Overviews link to their topics (in Topics table)

This mirrors the PEP `Requires` / `Replaces` pattern and the MADR
`superseded by` convention. Explicit linking enables agents to trace the
provenance chain: "Why does this topic say X?" -> "Because plan Y decided
it, based on research Z."

---

## 7. Directory Structure

```
/context/                           # Curated, stable knowledge
  {area}/
    overview.md                     # document_type: overview
    {topic}.md                      # document_type: topic

/artifacts/                         # Work products from interactions
  research/
    {date}-{slug}.md                # document_type: research
  plans/
    {date}-{slug}.md                # document_type: plan
```

**Rationale**:
- PARA's actionability axis: `/context` = Resources (consult), `/artifacts` = Projects (act)
- Zettelkasten's permanence axis: `/context` = Permanent notes, `/artifacts` = Project notes
- Date-prefixed filenames for artifacts enable chronological ordering and
  deterministic validation (filename date should match `last_updated`)
- Area subdirectories in `/context` follow EPPO's "domain-shaped organization"
  and Johnny Decimal's bounded hierarchy

---

## 8. Comparative Analysis: How Frameworks Map to Each Type

### Topic

| Dimension          | Best Framework Source              | What It Contributes                    |
|--------------------|------------------------------------|----------------------------------------|
| Section ordering   | Cognitive science (serial position) | Guidance first, Pitfalls near end      |
| Self-containment   | EPPO                               | Each topic works without loading others |
| Source grounding    | Wikipedia neutral POV              | Claims traceable to primary sources    |
| Concrete examples  | Dual coding (Paivio)               | In Practice section with worked examples |
| Counter-evidence   | Desirable difficulties (Bjork)     | Pitfalls section with exceptions       |
| Why explanations   | Elaborative interrogation (Dunlosky) | Context section with causal reasoning |
| Token efficiency   | Agent Skills spec, Chroma study    | <5,000 tokens, every line earns its place |

### Overview

| Dimension           | Best Framework Source              | What It Contributes                   |
|---------------------|------------------------------------|---------------------------------------|
| Navigation hub      | Obsidian MOCs, DITA maps           | Table of contents with descriptions   |
| Information scent   | Pirolli & Card IFT                 | Description column provides scent     |
| Bidirectional sync  | DITA relationship tables           | Table matches files on disk           |
| Level labeling      | Expertise reversal (Kalyuga)       | Explicitly novice-friendly orientation |
| Bounded structure   | Johnny Decimal                     | One overview per area, max 10 areas   |

### Research

| Dimension           | Best Framework Source              | What It Contributes                   |
|---------------------|------------------------------------|---------------------------------------|
| Fact-finding scope  | Agile spikes                       | Research informs; does not decide     |
| Source attribution  | Zettelkasten literature notes      | Written in own words, sources cited   |
| Progressive summary | PARA Layer 4                       | Distilled findings, raw data linked   |
| Question-driven     | PEP Motivation, Rust RFC Prior Art | Clear research question up front      |
| Implications        | Google design doc Alternatives     | "So what" connects findings to action |

### Plan

| Dimension           | Best Framework Source              | What It Contributes                   |
|---------------------|------------------------------------|---------------------------------------|
| Status lifecycle    | MADR (proposed/accepted/deprecated) | Explicit status enum in frontmatter  |
| Objective clarity   | Google design doc Goals/Non-Goals  | What will be true when this is done   |
| Step verification   | Implementation plan acceptance criteria | Each step independently verifiable |
| Context linking     | PEP Requires/Replaces fields       | Links to research that informs plan  |
| Ephemeral nature    | Zettelkasten project notes         | Discarded/archived after completion   |

---

## 9. Key Takeaways

1. **The four types map cleanly to established frameworks.** Every surveyed
   system (DITA, Diataxis, EPPO, Zettelkasten, PARA, ADRs, RFCs) recognizes
   the distinction between curated reference material and work artifacts.
   The `/context` vs. `/artifacts` split is well-grounded.

2. **Common metadata is achievable.** `document_type`, `description`, and
   `last_updated` work across all four types. Type-specific fields (`sources`,
   `last_validated`, `status`) are justified by the different lifecycle
   semantics of each type.

3. **Deterministic validation covers 70-80% of quality checks.** Section
   presence, ordering, metadata validity, size bounds, link integrity,
   source diversity, placeholder detection, and naming conventions are all
   deterministic. LLM-assisted validation is needed only for content quality
   (source drift, reasoning quality, specificity).

4. **Section ordering should exploit the U-shaped attention curve.** All
   four types should front-load the most critical content (primacy) and
   place action items or summaries near the end (recency).

5. **Research and plan types need lighter validation than context types.**
   Research is a point-in-time snapshot; plans are ephemeral. Heavy
   validation (readability, source freshness, citation grounding) belongs
   on the long-lived context types.

6. **The document lifecycle chain matters.** Research -> Plan -> Topic is a
   natural flow. Explicit linking between types enables provenance tracing
   and helps agents understand why knowledge exists.

7. **"Favor human readability when in conflict" remains correct.** The
   cognitive science research shows that clear, well-structured documents
   designed for human comprehension also work well for AI agents. The
   reverse is not true.

## Remaining Unknowns

- [ ] Exact size bounds for research and plan types (need empirical data)
- [ ] Whether `status` should be required or optional for research documents
- [ ] How to handle research documents that become outdated (archive? deprecate?)
- [ ] Whether plans should support a `superseded_by` field like ADRs
- [ ] Optimal section count for research (2 sections? 4? flexible?)

---

## Sources

### Documentation Standards
- OASIS DITA 1.3 Specification
- Diataxis Framework (diataxis.fr)
- Mark Baker, "Every Page is Page One" (XML Press, 2013)
- Robert E. Horn, "Structured Writing as a Paradigm" (1998)

### Agent Context Engineering
- Anthropic, "Effective Context Engineering for AI Agents" (2025)
- Agent Skills Specification (agentskills.io)
- Chroma Research, "Context Rot" (2025) -- research.trychroma.com/context-rot
- Liu et al., "Lost in the Middle" (TACL, 2024)
- Cursor .mdc file format documentation
- GitHub Copilot custom instructions documentation

### Personal Knowledge Management
- Luhmann's Zettelkasten method (zettelkasten.de)
- Tiago Forte, "Building a Second Brain" / PARA method
- Andy Matuschak, Evergreen Notes (notes.andymatuschak.org)
- Nick Milo, LYT / Maps of Content framework
- Johnny Decimal system (johnnydecimal.com)
- Obsidian Dataview plugin documentation

### ADRs, RFCs, Design Docs
- Michael Nygard, "Documenting Architecture Decisions" (Cognitect, 2011)
- MADR template (adr.github.io/madr)
- Rust RFC process and template (rust-lang.github.io/rfcs)
- Python PEP 1 and PEP 12 (peps.python.org)
- React RFC template (github.com/reactjs/rfcs)
- Malte Ubl, "Design Docs at Google" (industrialempathy.com)
- HashiCorp RFC template (works.hashicorp.com)
- Microsoft Engineering Playbook spike template
- Gergely Orosz, "Engineering Planning with RFCs" (Pragmatic Engineer)

### Cognitive Science
- Sweller, "Cognitive Load Theory" (1988)
- Paivio, "Mental Representations: A Dual Coding Approach" (1986)
- Pirolli & Card, "Information Foraging" (Psychological Review, 1999)
- Kalyuga et al., "Expertise Reversal Effect" (Educational Psychologist, 2003)
- Bjork, "Memory and Metamemory Considerations" (1994)
- Dunlosky et al., "Improving Students' Learning" (Psych. Sci. Public Interest, 2013)
- Ebbinghaus serial position effect; Murdock (1962); Glanzer & Cunitz (1966)
