# Document Type Specification

Version: 2.0-draft
Date: 2026-02-17

## Abstract

This specification defines a markdown file format for structured documents
optimized for consumption by both AI language model agents and human readers.
It covers four document types organized along two axes:

|                    | Reference (consult)       | Action (do/decide)      |
|--------------------|---------------------------|-------------------------|
| **Curated Context** | **Topic** · **Overview** |                         |
| **Work Artifact**  | **Research**              | **Plan**                |

**Context types** (topic, overview) live in `/context/` and contain distilled,
validated knowledge maintained over time. **Artifact types** (research, plan)
live in `/artifacts/` and capture point-in-time work products.

All four types share a common metadata core, title convention, and file format.
Each type has distinct section structures, size constraints, and validation
requirements defined in this specification.

The format is designed to be implementation-agnostic, delivery-mechanism-agnostic,
and provider-agnostic. It can be consumed by any system that reads markdown files.

## Status

Draft. Open for review. Supersedes v1.0-draft (2026-02-16).

## Conventions

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in RFC 2119.

---

## 1. File Format

A Knowledge Record MUST be a UTF-8 encoded text file with the `.md` extension.

A Knowledge Record MUST consist of, in order:

1. YAML frontmatter (Section 2)
2. A title heading (Section 3)
3. Body sections (Section 4)
4. Optionally, reference-style link definitions (Section 5)

**Justification:** Every major AI coding agent surveyed — Claude Code, Cursor,
GitHub Copilot, Windsurf, Codex, Gemini CLI — converges on Markdown as the
content format for agent-consumed knowledge. McMillan (2025) tested 9,649
experiments across 11 models and 4 formats and found that format does not
significantly affect aggregate accuracy for frontier models (chi-squared=2.45,
p=0.484), but Markdown provides the best human readability while YAML provides
the most token-efficient metadata encoding [1]. XML encodes the same information
with approximately 80% more tokens than Markdown [2].

---

## 2. Frontmatter

A Knowledge Record MUST begin with YAML frontmatter delimited by `---` lines.

### 2.1 Required Fields

#### `description`

- Type: String
- Constraint: 1–3 sentences, descriptive (not a category label)
- Requirement: MUST be present for all document types

The description MUST be a standalone summary that is meaningful without reading
the body. It MUST NOT describe the document ("This document covers...") — it
MUST describe the knowledge ("Tic-tac-toe is a solved game where...").

The description MUST serve as information scent — a signal that helps agents and
humans decide whether to load the full record. It MUST describe who the record
helps and when.

A reader who sees only the description SHOULD walk away with the key insight of
the record.

Examples of conforming values:
- `"Tic-tac-toe is a solved game; first-move advantage, forcing draws, forks, and the complete game tree"`
- `"Core principles for the first 10-15 moves of a chess game, with position evaluation and common openings"`

Examples of non-conforming values:
- `"core"` (category, not description)
- `"important"` (subjective, not informative)
- `"This document covers tic-tac-toe strategy"` (describes the document, not the knowledge)

**Justification:** The `description` field name aligns with the cross-platform
convention used by the Agent Skills specification [3], Cursor rules, GitHub
Copilot instructions, and Windsurf rules — every major agent context system
uses `description` for AI routing and progressive disclosure.

The field creates an intermediate progressive disclosure tier. The Agent Skills
specification defines a 3-tier model: ~100 tokens (description) → <5,000 tokens
(body) → unbounded (references) [3]. Without a description, agents must jump
from a ~15-token manifest entry to a ~2,000-token full file. The description
tier (~50 tokens per topic) lets an agent scan 20 topic descriptions for ~1,000
tokens and decide which to fully load.

The information scent requirement is grounded in Pirolli & Card (1999), who
predict that users follow cues that signal the likelihood of finding relevant
information [12]. A descriptive phrase provides stronger scent than a category
label.

This pattern is independently validated by: DITA's `<shortdesc>` element, which
serves as a standalone topic summary in search results and link previews [4];
Wikipedia's lead section policy, which requires a 100–400 word standalone
summary before the first heading [5]; Azure AI Search's enrichment pipeline,
which generates document summaries for RAG retrieval [6]; and the llms.txt
specification's blockquote summary format [7].

#### `sources`

- Type: List of objects, each with `url` (string) and `title` (string)
- Constraint: MUST contain at least one entry
- Requirement: MUST be present for `document_type: topic` and `document_type: research`

Each source MUST be a primary or authoritative reference for the record's content.

Topics and research documents are source-grounded — they distill or present
evidence from external material. Overview and plan types are not source-grounded:
overviews aggregate topics (not sources directly), and plans are forward-looking
artifacts that reference research documents rather than external sources.

**Justification:** Source primacy — the knowledge base is a curated guide, not a
replacement for primary sources. When an agent or human needs to go deeper, the
path must be clear. This principle is grounded in Anthropic's context engineering
guidance: "point to primary sources" rather than duplicating them, because primary
sources are maintained by domain experts and stay current [8]. Dublin Core's
`Source` element serves the same purpose in metadata standards [9].

#### `last_validated`

- Type: ISO 8601 date (YYYY-MM-DD)
- Constraint: MUST be a valid date not in the future
- Requirement: MUST be present for `document_type: topic` and `document_type: overview`

The date when the record's content was last verified against its sources.

Context types (topic, overview) require `last_validated` because they are
maintained long-term and their accuracy degrades over time. Artifact types
(research, plan) do not require it — research is a point-in-time snapshot, and
plans have explicit status lifecycle tracking instead.

**Justification:** Knowledge freshness degrades over time. Guru's verification
model assigns each knowledge card a verification interval and visual staleness
indicators [10]. JATS (Journal Article Tag Suite) tracks multiple dates per
article: received, revised, accepted, published [11]. The `last_validated` field
enables automated freshness checking: a health system can flag records that
haven't been verified within a configurable threshold.

#### `last_updated`

- Type: ISO 8601 date (YYYY-MM-DD)
- Constraint: MUST be a valid date not in the future

The date when the record's content was last modified.

**Justification:** `last_updated` and `last_validated` track different events.
A record can be edited without re-verifying sources (`last_updated` changes,
`last_validated` stays), or validated without content changes (`last_validated`
changes, `last_updated` stays). Dublin Core's `Date.modified` element serves the
same purpose [9]. JATS tracks `revised` separately from other dates [11]. The
two fields together give a complete picture of content currency: `last_updated`
answers "when did this change?" while `last_validated` answers "when was this
checked?"

#### `document_type`

- Type: Enum string
- Values: `overview` | `topic` | `research` | `plan`
- Constraint: MUST be one of the specified values

Indicates the record's type, which determines its section structure, size
constraints, directory placement, and validation rules.

| Value | Location | Purpose | Sections |
|-------|----------|---------|----------|
| `overview` | `/context/{area}/` | Area navigation and orientation | What This Covers, Topics, Key Sources |
| `topic` | `/context/{area}/` | Distilled actionable knowledge with sources | Guidance, Context, In Practice, Pitfalls, Go Deeper |
| `research` | `/artifacts/research/` | Investigation artifacts with findings | Question, Findings, Implications, Sources |
| `plan` | `/artifacts/plans/` | Work planning with steps and verification | Objective, Context, Steps, Verification |

The four types map to a 2×2 classification:

- **Curated context** (topic, overview): Distilled, validated, maintained
  long-term. Lives in `/context/`. Freshness tracked via `last_validated`.
- **Work artifacts** (research, plan): Point-in-time products of interactions.
  Live in `/artifacts/`. Research is a snapshot; plans have status lifecycle.
- **Reference types** (topic, overview, research): Consulted for information.
- **Action types** (plan): Consumed to drive work forward.

**Justification:** The four-type model is grounded in convergent patterns across
documentation standards, personal knowledge management, and software engineering:

| Framework         | Curated Reference        | Work Artifact / Action       |
|-------------------|--------------------------|------------------------------|
| PARA              | Resources                | Projects                     |
| Zettelkasten      | Permanent notes          | Project notes                |
| Diataxis          | Explanation + Reference  | How-to Guides                |
| DITA              | Concept + Reference      | Task                         |
| Software Eng.     | ADRs (accepted)          | RFCs (proposed), Plans       |

The `document_type` field name is more precise than the previous `depth` field —
it describes *what kind* of record this is, not just its level of detail. The
expertise reversal effect (Kalyuga et al., 2003) demonstrates that material
designed for novices can actively hinder experts and vice versa [14]. The
document type field allows readers to self-select the appropriate depth and
purpose.

### 2.2 Optional Fields

#### `tags`

- Type: List of strings
- Convention: lowercase, hyphenated
- Constraint: No duplicates within a record

Keywords for cross-cutting discovery.

**Justification:** Dublin Core's `Subject` element [9], DITA's `<keyword>`
element [4], and SKOS's `altLabel` [15] all recommend keyword metadata for
retrieval enrichment. Tags enable queries like "all game-theory topics across
all domain areas" that hierarchical directory structure alone cannot serve.

#### `related`

- Type: List of relative file paths
- Constraint: Each path SHOULD resolve to an existing file

Explicit non-hierarchical connections to peer topics.

**Justification:** SKOS defines `skos:related` for non-hierarchical associations
between concepts [15]. DITA uses relationship tables for the same purpose [4].
These connections are distinct from hierarchical parent-child relationships
(implicit in directory structure) and from source links (in Go Deeper).

#### `status`

- Type: Enum string
- Values: `draft` | `active` | `complete` | `abandoned`
- Requirement: MUST be present for `document_type: plan`. MAY be present for
  `document_type: research`.
- Constraint: MUST be one of the specified values when present

The lifecycle state of the record.

Plans have the most active lifecycle of all four types — they transition between
discrete states as work progresses. Context types (topic, overview) do not need
status because their freshness is tracked via `last_validated`. Research
documents MAY use status to distinguish in-progress from complete investigations.

| Status | Meaning |
|--------|---------|
| `draft` | Work in progress, not yet actionable |
| `active` | Currently being executed (plans) or underway (research) |
| `complete` | Work is finished |
| `abandoned` | Work was stopped before completion |

**Justification:** MADR's status lifecycle (proposed/accepted/deprecated/
superseded) [26] and Google's design doc lifecycle (draft/review/approved/
archived) [27] both demonstrate that planning artifacts need explicit status
tracking. PEPs use a 9-value status enum in their RFC 2822 header [28]. The
four-value enum here is deliberately simpler — it covers the lifecycle states
relevant to personal knowledge management without the governance complexity of
multi-stakeholder review processes.

### 2.3 Metadata by Type Summary

| Field            | Topic    | Overview | Research | Plan     |
|------------------|:--------:|:--------:|:--------:|:--------:|
| `document_type`  | Required | Required | Required | Required |
| `description`    | Required | Required | Required | Required |
| `last_updated`   | Required | Required | Required | Required |
| `sources`        | Required | —        | Required | —        |
| `last_validated` | Required | Required | —        | —        |
| `status`         | —        | —        | Optional | Required |
| `tags`           | Optional | Optional | Optional | Optional |
| `related`        | Optional | Optional | Optional | Optional |

---

## 3. Title

The record body MUST begin with a single H1 heading (`# Title`).

There MUST be exactly one H1 heading in the record. All subsequent headings
MUST be H2 (`##`).

**Justification:** Markdown best practice (markdownlint MD025) and DITA's
requirement that every topic has exactly one `<title>` element [4]. A single
H1 provides an unambiguous topic identifier for manifest generation and
cross-referencing.

---

## 4. Sections

### 4.1 Topic Type

A record with `document_type: topic` MUST contain these sections in this order:

1. `## Guidance`
2. `## Context`
3. `## In Practice`
4. `## Pitfalls`
5. `## Go Deeper`

A record with `document_type: topic` MAY contain a `## Quick Reference` section.
If present, it MUST appear between `## Pitfalls` and `## Go Deeper`.

#### 4.1.1 Section Ordering Rationale

The ordering is driven by the U-shaped attention curve in language models.

Liu et al. (2024) demonstrated that LLM performance degrades significantly
when relevant information is placed in the middle of input context, with the
effect confirmed across 6+ follow-up studies and shown to be architectural
rather than training-dependent [16]. The Chroma Research "Context Rot" study
(2025) measured 13.9–85% performance degradation as context length increases
across 18 models [17]. Anthropic's context engineering guidance notes that 300
focused tokens outperform 113,000 unfocused tokens [8].

The section order exploits three attentional effects:

**Primacy effect (Guidance, position 1):** The beginning of input receives
the highest attention weight. Guidance contains the most actionable content —
the section an agent reads if it can only read one section. Placing it first
ensures it occupies the highest-attention position.

**Engagement resistance (In Practice, position 3):** Concrete examples are
inherently more engaging than abstract content. Cognitive science research on
concrete vs. abstract processing (Paivio, 1986) shows concrete material creates
stronger memory traces [18]. Positioning examples in the middle — the lowest-
attention zone — leverages their natural engagement to partially counteract the
attention valley.

**Recency effect (Pitfalls, position 4):** The end of input receives elevated
attention. Warnings and pitfalls benefit from recency — they are the last
substantive content the reader encounters, making them more likely to be
retained and applied.

#### 4.1.2 Guidance

Content: Actionable recommendations the reader can apply immediately.

Format: Numbered items. Each MUST begin with a **bold declarative statement**,
followed by explanation and an inline source citation.

```markdown
**1. The first player cannot lose with perfect play.** A strategy-stealing
argument proves this: if the second player had a winning strategy, the first
player could steal it ([Hamkins][hamkins]).
```

**Justification:** Information Mapping's "principle" information type prescribes
guidelines and rules as the highest-value content in a reference document [19].
DITA's `<taskbody>` places the step sequence (the actionable content) as the
primary body element [4]. The bold-statement-then-explanation pattern provides
dual-speed reading: the bold text is scannable for quick reference, the
explanation provides depth for full reading.

#### 4.1.3 Context

Content: Why this topic matters. When it applies. How it connects to the
broader domain.

The Context section SHOULD contain causal reasoning — explaining *why* guidance
works, not just *what* to do.

**Justification:** Dunlosky et al. (2013) found that elaborative interrogation
(asking "why") produces significantly better learning outcomes than re-reading
or highlighting [20]. Records that explain causal mechanisms produce better
agent outputs than records that state prescriptive rules, because the agent can
adapt the reasoning to novel situations rather than pattern-matching against
specific instructions.

#### 4.1.4 In Practice

Content: Concrete examples, worked scenarios, code blocks, decision tables.

The In Practice section SHOULD lead with a specific scenario before generalizing.

**Justification:** Concrete-before-abstract ordering is grounded in Paivio's
dual coding theory (1986), which demonstrates that concrete concepts create both
verbal and imaginal memory representations, producing stronger encoding [18].
Sweller's cognitive load theory (1988) supports worked examples as reducing
extraneous cognitive load compared to abstract problem-solving [21].

#### 4.1.5 Pitfalls

Content: Mistakes, anti-patterns, and misconceptions.

Each pitfall SHOULD begin with a **bold heading** followed by a brief
explanation.

The Pitfalls section SHOULD include counter-evidence found during research —
reasons the guidance might be wrong or limited.

**Justification:** Bjork's desirable difficulty framework (1994) shows that
encountering and resolving difficulties during learning produces more durable
understanding [22]. Counter-evidence signals intellectual honesty, increasing
reader trust. Wikipedia's neutral point of view policy requires presenting
significant viewpoints — this principle adapts it for curated knowledge, where
the author has a recommendation but acknowledges limitations.

#### 4.1.6 Quick Reference (Optional)

Content: Terse lookup data — tables, lists, decision trees, cheat sheets.

A Quick Reference section MUST NOT contain prose paragraphs. Content MUST be
tables, bullet lists, or other scannable formats.

This section is OPTIONAL. It SHOULD be included only when the topic has
significant factual data that benefits from tabular presentation.

**Justification:** This replaces the previous `.ref.md` companion file pattern.
DITA's reference topic type (`<refbody>`) allows tables and property lists in
any sequence because reference content is shaped by its data, not a narrative
flow [4]. Integrating reference data into the topic record eliminates
companion file synchronization overhead and places the data in a high-attention
position (recency effect at the end of the file).

#### 4.1.7 Go Deeper

Content: Links to primary sources and further reading.

Primary sources (already cited in the body) SHOULD appear first, followed by
supplementary material.

**Justification:** EPPO's "links richly" principle makes connections to related
content first-class [23]. Positioning Go Deeper last mirrors Wikipedia's
convention of placing "References" and "External links" at the end of articles
[5], and DITA's `<related-links>` element at the end of topics [4].

### 4.2 Overview Type

A record with `document_type: overview` MUST contain these sections in this order:

1. `## What This Covers`
2. `## Topics`
3. `## Key Sources`

Each area directory MUST contain exactly one `overview.md` file. The overview
serves as the entry point for its area — a reader who lands in an area directory
reads the overview first.

**Justification:** Overview records serve the "orientation" function identified
by Diataxis as the explanation quadrant [13] and by EPPO's "establishes context"
characteristic [23]. The one-to-many constraint ensures every area has a single
navigation hub. Pirolli & Card's information foraging theory (1999) predicts
that users follow cues that signal the likelihood of finding relevant
information [12] — the overview provides those cues for an entire area.

#### 4.2.1 What This Covers

Content: A prose summary of the area's scope — what topics it contains, who
it serves, and when to consult it.

The What This Covers section MUST contain at least 30 words. It SHOULD be
1–3 paragraphs.

**Justification:** This section provides information scent at the area level.
A reader scanning multiple area overviews uses this section to decide which
area to explore further. The 30-word minimum ensures the section provides
genuine orientation rather than a placeholder stub. This mirrors DITA's
`<shortdesc>` element requirement that topics begin with a standalone summary
[4] and Wikipedia's lead section policy [5].

#### 4.2.2 Topics

Content: A navigation table listing every topic record in the area.

The Topics section MUST contain a Markdown table. The table MUST include at
minimum a column for the topic name (as a relative link) and a Description
column.

The topic table MUST be bidirectionally synchronized with topic files on disk:

- **Forward constraint:** Every file linked in the Topics table MUST exist
  on disk.
- **Reverse constraint:** Every `.md` file with `document_type: topic` in the
  area directory MUST appear as a link in the Topics table.

Reference-type files (`.ref.md` or `document_type: reference`) are excluded
from the reverse constraint.

Example:

```markdown
| Topic | Description |
|-------|-------------|
| [Opening Principles](opening-principles.md) | Core principles for the first 10-15 moves |
| [Endgame Patterns](endgame-patterns.md) | Common endgame positions and techniques |
```

**Justification:** The Topics table is the primary progressive disclosure
mechanism for an area. Pirolli & Card's information scent theory predicts that
navigation succeeds when link labels provide strong cues about target content
[12]. The Description column provides that scent — without it, readers must
click through to determine relevance.

The bidirectional sync constraint prevents two failure modes: stale links
(forward — a reader clicks a link that leads nowhere) and invisible topics
(reverse — a topic exists on disk but is undiscoverable through the overview).
Both degrade the overview's value as a navigation hub.

#### 4.2.3 Key Sources

Content: Links to primary sources that inform the area as a whole — official
documentation, foundational papers, or authoritative references.

The Key Sources section SHOULD contain a bulleted list of links. These are
area-level sources, not duplicates of per-topic sources in Go Deeper sections.

**Justification:** Area-level sources provide orientation that individual
topic sources cannot. A reader new to the area benefits from knowing the
canonical references before diving into specific topics. This implements
Source Primacy (Principle 1) at the area level — the overview points to where
deeper exploration begins.

### 4.3 Research Type

A record with `document_type: research` MUST contain these sections in this
order:

1. `## Question`
2. `## Findings`
3. `## Implications`
4. `## Sources`

Research documents are investigation artifacts — point-in-time snapshots of
what was learned during a research effort. They live in `/artifacts/research/`
and are named with a date prefix: `{YYYY-MM-DD}-{slug}.md`.

Research documents present evidence and analysis. They do not prescribe action —
that is the role of plans and topics that consume the research.

**Justification:** The separation between research (fact-finding) and decision-
making is a well-established pattern. Microsoft's Engineering Fundamentals
Playbook defines technical spikes as "fact-finding, not decision-making" [29].
Google's design docs separate the Context section (research and evidence) from
the Proposed Solution section (decision) [27]. Zettelkasten distinguishes
literature notes (source-attributed, in own words) from permanent notes
(distilled claims) [30]. The research type captures the literature note / spike
phase explicitly.

#### 4.3.1 Question

Content: What was investigated and why. The specific question or questions
this research set out to answer.

The Question section MUST be non-empty. It SHOULD be 1–3 paragraphs.

A reader who sees only the Question section SHOULD be able to determine whether
this investigation is relevant to their current need.

**Justification:** Research is driven by a question — naming it explicitly
creates stronger information scent than generic titles like "Analysis" or
"Investigation" [12]. The Rust RFC process requires a Motivation section that
frames the problem so convincingly that alternatives could be developed even
if the RFC is rejected [31]. The Question section serves the same function:
it makes the research useful even if the findings are superseded.

#### 4.3.2 Findings

Content: What was learned, organized by sub-question or theme.

The Findings section is the primary content section. It SHOULD present evidence
from sources, note areas of agreement and disagreement across sources, and
distinguish well-established findings from tentative conclusions.

Findings SHOULD include inline source citations.

**Justification:** The Findings section combines the roles of Rust RFC's
"Guide-level explanation" (accessible presentation) and PEP's "Specification"
(detailed content) [28][31]. Organizing by sub-question rather than by source
prevents the common failure mode of literature reviews that merely summarize
sources sequentially without synthesis.

#### 4.3.3 Implications

Content: What the findings mean for upcoming decisions, designs, or knowledge
base content. "So what" — how findings connect to actionable concerns.

The Implications section SHOULD say "this means X for Y" without prescribing
specific action. Recommendations belong in plans or topics that consume the
research.

**Justification:** Google's design doc Alternatives Considered section [27]
and Rust RFC's Rationale section [31] both demonstrate that explicit "so what"
analysis is more valuable than leaving readers to draw their own conclusions.
The fact-finding/decision-making boundary is preserved: implications inform
decisions but do not make them.

#### 4.3.4 Sources

Content: A structured list of sources consulted during the investigation.

The Sources section MUST contain at least one entry. Sources SHOULD include
URLs where available and the date accessed.

This section differs from the frontmatter `sources` field: frontmatter sources
are the canonical references for the record; the body Sources section provides
the complete bibliography with context about what each source contributed.

**Justification:** Research documents present source material more directly
than topics do. The body Sources section provides a richer bibliography than
frontmatter alone — including context, access dates, and organization by
sub-topic. This mirrors the convention across academic papers, technical spikes,
and PEPs of placing a full reference list at the end of the document.

### 4.4 Plan Type

A record with `document_type: plan` MUST contain these sections in this order:

1. `## Objective`
2. `## Context`
3. `## Steps`
4. `## Verification`

Plan documents are work planning artifacts — they describe what will be done,
why, and how success is measured. They live in `/artifacts/plans/` and are
named with a date prefix: `{YYYY-MM-DD}-{slug}.md`.

Plans have the most active lifecycle of all four types. They MUST include a
`status` field in frontmatter (Section 2.2).

**Justification:** Plans occupy the "action" quadrant of the type system —
they are consumed to drive work forward, not consulted for reference. MADR's
status lifecycle [26], Google's design doc lifecycle [27], and Zettelkasten's
"project note" concept (notes discarded after project completion) [30] all
demonstrate that planning artifacts are fundamentally different from reference
material and require explicit lifecycle management.

#### 4.4.1 Objective

Content: What will be true when this plan is complete. A clear, concise
statement of purpose.

The Objective section SHOULD answer "what will be true when this is done?"
rather than describing activity ("we will do X").

The Objective section MAY include a Non-Goals subsection that explicitly lists
things that could be goals but are scoped out.

**Justification:** Google's design doc Goals/Non-Goals pattern [27] is widely
cited as a best practice for preventing scope creep. Non-goals are "not a
negated goal" — they are things that could reasonably be in scope but are
explicitly excluded. For AI agents, explicit non-goals prevent retrieval of
this plan for topics it deliberately does not cover.

#### 4.4.2 Context

Content: Links to research documents, prior decisions, or topics that inform
the plan. What the reader needs to understand before evaluating the steps.

The Context section SHOULD reference the research documents that informed the
plan, creating an explicit provenance chain: Research → Plan → execution.

**Justification:** PEP's `Requires` field [28] and MADR's cross-references
[26] both establish explicit dependency chains between documents. The Context
section creates the natural flow: "We investigated X (research), therefore we
plan to do Y (plan), which will produce Z (topic updates)." This chain enables
agents to trace provenance: "Why does this topic say X?" → "Because plan Y
decided it, based on research Z."

#### 4.4.3 Steps

Content: The ordered work items that implement the objective.

Each step SHOULD be independently verifiable — a reader should be able to
confirm whether a step is complete without evaluating other steps.

Steps MAY use a checklist format (`- [ ]` / `- [x]`) when the plan is being
actively tracked.

**Justification:** Microsoft's implementation plan templates emphasize that
each deliverable needs acceptance criteria [29]. Independently verifiable steps
enable partial progress tracking and make it possible to resume work after
interruption. The checklist format is familiar from GitHub issues and provides
visual progress indication for both humans and agents.

#### 4.4.4 Verification

Content: How success is measured. What must be true for the plan to be
considered complete.

The Verification section SHOULD include concrete, observable criteria — test
commands, expected outputs, or measurable outcomes.

**Justification:** Placing verification last exploits the recency effect [16]
— the success criteria are fresh in memory when execution begins. Implementation
plans universally include acceptance criteria [29]. For AI agents, concrete
verification criteria (e.g., "run `pytest tests/ -v` and confirm all pass")
are directly executable, making the plan self-verifying.

---

## 5. Link Definitions

A Knowledge Record SHOULD use reference-style Markdown links.

Reference-style link definitions MUST appear at the end of the file, after
all sections:

```markdown
[wiki]: https://en.wikipedia.org/wiki/Tic-tac-toe
[hamkins]: https://www.infinitelymore.xyz/p/tic-tac-toe-and-variants
```

**Justification:** Reference-style links produce cleaner body text by
separating content from URLs. They eliminate URL duplication when the same
source is cited multiple times. This convention is RECOMMENDED but not REQUIRED
because inline links are semantically equivalent and some authoring tools
handle them better.

---

## 6. Source Integration

Source integration requirements apply to source-grounded types (`document_type:
topic` and `document_type: research`). Overview and plan types are not
source-grounded and are exempt from Sections 6.1–6.3.

### 6.1 Citation Density

For topic records, every factual claim in the Guidance section MUST have an
inline source citation. Claims in other sections SHOULD have inline citations
when the claim is non-obvious or the reader might want to verify.

For research records, findings SHOULD include inline citations to the sources
that support them.

**Justification:** The grounding standard is: a skeptical reader can trace any
key claim to a primary source within one click. This implements the Source
Primacy principle — the record is a curated guide, not a replacement for primary
sources [8].

### 6.2 Source Diversity

A source-grounded record SHOULD include sources from at least 2 different
domains or authors.

**Justification:** Wikidata's provenance model requires references from
independent sources for claim verification [24]. Source diversity reduces the
risk of systematic bias from a single perspective.

### 6.3 Counter-Evidence

During topic record creation, the author SHOULD actively search for counter-
evidence: reasons the guidance might be wrong, limited, or context-dependent.

Counter-evidence findings SHOULD be incorporated into the Pitfalls section.

For research records, findings SHOULD distinguish well-established conclusions
from tentative ones and note areas of disagreement across sources.

**Justification:** Wikipedia's neutral point of view policy and the scientific
method both require consideration of opposing evidence. The Beyond Accuracy
framework (ESEC/FSE 2020) identifies accuracy as only one of ten documentation
quality dimensions — completeness and relevance require addressing edge cases
and limitations [25].

---

## 7. Size Constraints

### 7.1 Topic Type

A record with `document_type: topic` MUST be between 10 and 500 lines.

The recommended token budget is 500–5,000 tokens.

### 7.2 Overview Type

A record with `document_type: overview` MUST be between 5 and 150 lines.

The recommended token budget is 200–2,000 tokens.

### 7.3 Research Type

A record with `document_type: research` MUST be at least 20 lines.

There is no upper bound on research document length. Thoroughness and accuracy
are the priorities — a research document should be as long as the investigation
demands.

The token-efficiency constraints that apply to context types (topic, overview)
do not apply to research artifacts. Context types are loaded into agent working
memory and compete for attention; research artifacts are consulted for evidence
and referenced by plans and topics that distill the findings.

### 7.4 Plan Type

A record with `document_type: plan` MUST be at least 10 lines.

There is no upper bound on plan document length. Plans should follow agentic
planning best practices: steps should be concrete and independently verifiable,
verification criteria should be observable, and the plan should contain enough
context for an agent to execute without requiring external documents. A complex
multi-phase plan will naturally be longer than a simple task plan — the
constraint is clarity and executability, not line count.

### 7.5 Description Field

The `description` field MUST be 1–3 sentences.

The recommended token budget is 30–80 tokens.

### 7.6 Enforcement

Line counts are normative (MUST). Token budgets are informative (SHOULD).

**Justification:** Line counts are deterministic and require no external
dependencies to verify. Token counts vary by tokenizer and model. The Agent
Skills specification uses a similar approach: "<500 lines" as the enforceable
constraint, with token guidance (~5,000 tokens) as the design target [3].

The upper bound of 5,000 tokens aligns with the Agent Skills Tier 2 limit and
with Anthropic's guidance that effective context utilization drops significantly
beyond this range for individual documents within a larger context assembly [8].

---

## 8. Directory Structure

Knowledge Records MUST be organized into two top-level directories:

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

### 8.1 Context Directory

The `/context/` directory contains curated knowledge organized by domain area.

Each area MUST be a directory with a slug-style name (lowercase, hyphens).
Each area directory MUST contain exactly one `overview.md` file.
Topic files MUST be named with slug-style names and the `.md` extension.

### 8.2 Artifacts Directory

The `/artifacts/` directory contains work products organized by type.

Artifact filenames MUST be prefixed with an ISO 8601 date: `{YYYY-MM-DD}-{slug}.md`.
The date prefix SHOULD match the record's `last_updated` frontmatter field.

### 8.3 Document Lifecycle

The natural flow between document types is:

```
Research → informs → Plan → produces → Topics + Overviews
                                    → may trigger → more Research
```

- Plans SHOULD reference the research documents that informed them (in Context).
- Topics MAY reference the plan that created them (in Go Deeper or `related`).
- Research documents link to their sources (in Sources section).
- Overviews link to their topics (in Topics table).

Research documents are snapshots — they do not update after completion.
Plans are living documents until complete or abandoned.
Topics and overviews are maintained long-term via `last_validated`.

**Justification:** The `/context` vs. `/artifacts` split encodes the
curated/artifact axis of the type system. PARA's actionability axis maps
Resources (consult) to `/context/` and Projects (act) to `/artifacts/` [32].
Zettelkasten distinguishes permanent notes (maintained indefinitely) from
project notes (discarded after completion) [30]. Date-prefixed filenames for
artifacts enable chronological ordering and deterministic validation. Area
subdirectories in `/context/` follow EPPO's "domain-shaped organization" [23]
and Johnny Decimal's bounded hierarchy.

---

## 9. Curation Metadata

Source evaluations and research provenance MUST NOT appear in the record body.

Curation metadata SHOULD be stored in a separate file (e.g., JSON) outside
the record's file path.

**Justification:** Source evaluation tables consume approximately 20 lines of
content that serves the curation process, not the consumer. Anthropic's context
engineering guidance emphasizes that "every token matters" and non-essential
content dilutes the signal [8]. The Chroma Research context rot study quantifies
this: additional context that doesn't contribute to the task measurably degrades
performance [17]. Separating curation metadata from consumer content ensures
every line in the record serves the reader.

---

## 10. Conformance

A document conforms to this specification if it satisfies all MUST requirements
defined in Sections 1–9.

A document partially conforms if it satisfies all MUST requirements in Sections
1–3 (file format, frontmatter required fields, title) but not all requirements
in Sections 4–9.

Partial conformance enables incremental adoption — a record can have valid
metadata and structure while its section content is being developed.

---

## References

[1] McMillan, J. (2025). "Structured Context Engineering for AI Models."
arXiv:2602.05447. 9,649 experiments across 11 models and 4 formats. Format
does not significantly affect aggregate accuracy (chi-squared=2.45, p=0.484).

[2] OASIS DITA Technical Committee (2017). "Darwin Information Typing
Architecture (DITA) Version 1.3." OASIS Standard.
https://docs.oasis-open.org/dita/dita/v1.3/dita-v1.3-part3-all-inclusive.html

[3] Agent Skills Specification. https://agentskills.io/specification —
Three-tier progressive disclosure: ~100 tokens (Tier 1), <5,000 tokens
(Tier 2), unbounded (Tier 3).

[4] OASIS DITA 1.3 — Topic types (concept, task, reference), `<shortdesc>`
element, `<prolog>` metadata, `<related-links>`, relationship tables.

[5] Wikipedia Manual of Style: Layout.
https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Layout — Lead section
policy: 100-400 words, standalone summary, no heading.

[6] Microsoft Azure AI Search Documentation. RAG enrichment pipelines
generate document summaries for improved retrieval.

[7] llms.txt Specification. https://llmstxt.org/ — Blockquote summary format
for LLM-consumed documentation.

[8] Anthropic (2025). "Effective Context Engineering for AI Agents."
https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
— Write, Select, Compress, Isolate framework. 300 focused tokens outperform
113K unfocused tokens.

[9] Dublin Core Metadata Element Set.
https://www.dublincore.org/specifications/dublin-core/dces/ — 15 core elements
including Title, Subject, Description, Source, Date, Relation.

[10] Guru Verification Model.
https://help.getguru.com/docs/verifying-and-unverifying-cards — Verification
intervals, assigned verifiers, visual staleness indicators.

[11] JATS (Journal Article Tag Suite). NISO Z39.96-2019. Structured dates:
received, revised, accepted, published. Structured abstracts.

[12] Pirolli, P. & Card, S.K. (1999). "Information Foraging." Psychological
Review, 106(4), 643-675. Information scent theory: users follow cues that
signal the likelihood of finding relevant information.

[13] Diataxis Framework. https://diataxis.fr/ — Four documentation quadrants:
tutorials, how-to guides, explanations, references. Two axes: practical/
theoretical, acquisition/application.

[14] Kalyuga, S., Ayres, P., Chandler, P., & Sweller, J. (2003). "The
Expertise Reversal Effect." Educational Psychologist, 38(1), 23-31. Material
that assists novices can hinder expert performance due to redundancy.

[15] SKOS Reference (W3C Recommendation).
https://www.w3.org/TR/skos-reference/ — `broader`, `narrower`, `related`,
`prefLabel`, `altLabel`, `definition`, `scopeNote`.

[16] Liu, N.F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni,
F., & Liang, P. (2024). "Lost in the Middle: How Language Models Use Long
Contexts." Transactions of the ACL, 12, 157-173. U-shaped attention curve
confirmed across multiple models and tasks.

[17] Chroma Research (2025). "Context Rot." https://research.trychroma.com/context-rot
— 13.9–85% performance degradation as context length increases. 18 models
tested. Architectural, not a training artifact.

[18] Paivio, A. (1986). "Mental Representations: A Dual Coding Approach."
Oxford University Press. Concrete concepts create both verbal and imaginal
memory representations, producing stronger encoding than abstract concepts.

[19] Horn, R.E. (1998). "Structured Writing as a Paradigm." In A. Romiszowski
& C. Dills (Eds.), Instructional Development Paradigms. Six information types:
procedure, process, principle, concept, structure, fact.

[20] Dunlosky, J., Rawson, K.A., Marsh, E.J., Nathan, M.J., & Willingham,
D.T. (2013). "Improving Students' Learning With Effective Learning Techniques."
Psychological Science in the Public Interest, 14(1), 4-58. Elaborative
interrogation and self-explanation rated as moderate-to-high utility.

[21] Sweller, J. (1988). "Cognitive Load During Problem Solving: Effects on
Learning." Cognitive Science, 12(2), 257-285. Worked examples reduce extraneous
cognitive load compared to means-ends problem solving.

[22] Bjork, R.A. (1994). "Memory and Metamemory Considerations in the Training
of Human Beings." In J. Metcalfe & A. Shimamura (Eds.), Metacognition.
Desirable difficulties during learning produce more durable understanding.

[23] Baker, M. (2013). "Every Page is Page One: Topic-based Writing for
Technical Communication and the Web." XML Press. Seven characteristics:
self-contained, specific purpose, domain-typed, establishes context, assumes
qualified reader, stays on one level, links richly.

[24] Wikidata Data Model. https://www.wikidata.org/wiki/Wikidata:Data_model —
Statement model with claims, qualifiers, references, and rank
(preferred/normal/deprecated).

[25] Aghajani, E., et al. (2020). "Software Documentation: The Practitioners'
Perspective." ESEC/FSE 2020. Ten quality dimensions: organization, internal
consistency, accuracy, completeness, currency, relevance, readability,
conciseness, consistency, appeal.

[26] MADR — Markdown Architectural Decision Records. https://adr.github.io/madr/
— Structured decision records with status lifecycle (proposed/accepted/
deprecated/superseded), decision drivers, and explicit pros/cons per option.

[27] Ubl, M. "Design Docs at Google." https://www.industrialempathy.com/posts/design-docs-at-google/
— Goals/Non-Goals pattern, progressive depth (overview then detail),
Alternatives Considered as one of the most important sections.

[28] PEP 1 — PEP Purpose and Guidelines. https://peps.python.org/pep-0001/
— RFC 2822 structured metadata header, 9-value status enum, explicit
`Requires`/`Replaces`/`Superseded-By` linking fields.

[29] Microsoft Engineering Fundamentals Playbook — Technical Spike.
https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/recipes/technical-spike/
— Spikes are "fact-finding, not decision-making." Time-boxed investigation
with reproducible environment setup and summarized findings.

[30] Luhmann's Zettelkasten method. https://zettelkasten.de/ — Permanent notes
(maintained, atomic, in own words) vs. project notes (discarded after project).
Literature notes as processed, source-attributed intermediaries.

[31] Rust RFC Template. https://github.com/rust-lang/rfcs/blob/master/0000-template.md
— Guide-level / Reference-level progressive disclosure split. Required sections:
Summary, Motivation, Drawbacks, Rationale and alternatives, Prior art,
Unresolved questions, Future possibilities.

[32] Forte, T. "Building a Second Brain" / PARA method. Resources (reference
material to consult) vs. Projects (active work with a deadline). Progressive
summarization: Layer 1 (original) through Layer 4 (own words).

---

## Related Documents

This specification is part of a progressive disclosure chain:

| Layer | Document | Purpose |
|-------|----------|---------|
| Reference | `2026-02-16-document-type-reference.md` | Concise rules for creating/validating documents (~150 lines) |
| **Specification** | **this document** | Normative rules with rationale and justifications |
| Data Models | `2026-02-16-document-type-data-models.md` | Pydantic models, validation dispatch, Tier 2 triggers |
| Research | `../artifacts/research/2026-02-17-document-type-system-deep-dive.md` | Evidence base from five research threads |

_Data models and Tier 2 triggers have been moved to
`2026-02-16-document-type-data-models.md` to keep this document focused
on normative rules and rationale._
