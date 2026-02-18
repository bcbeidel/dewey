# Document Type Reference

Quick reference for creating and validating knowledge base documents.
For rationale and justifications, see the full specification at
`docs/plans/2026-02-16-document-type-specification.md`.
For Pydantic data models and validation dispatch, see
`docs/plans/2026-02-16-document-type-data-models.md`.

## Four Document Types

|                    | Reference (consult)       | Action (do/decide)      |
|--------------------|---------------------------|-------------------------|
| **Curated Context** | **Topic** · **Overview** |                         |
| **Work Artifact**  | **Research**              | **Plan**                |

## Directory Layout

```
/context/                           # Curated, stable knowledge
  {area}/
    overview.md                     # document_type: overview
    {topic}.md                      # document_type: topic

/artifacts/                         # Work products from interactions
  research/
    {YYYY-MM-DD}-{slug}.md          # document_type: research
  plans/
    {YYYY-MM-DD}-{slug}.md          # document_type: plan
```

## Document Lifecycle

```
Research → informs → Plan → produces → Topics + Overviews
                                    → may trigger → more Research
```

- Research documents are snapshots — they do not update after completion.
- Plans are living documents until complete or abandoned.
- Topics and overviews are maintained long-term via `last_validated`.

## Metadata by Type

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

### Field Rules

- **`description`**: 1-3 sentences. Describe the knowledge, not the document. Must provide information scent.
- **`sources`**: List of `{url, title}` objects. At least one entry. Required for source-grounded types (topic, research).
- **`last_validated`**: ISO 8601 date (YYYY-MM-DD). Not in the future. Required for context types (topic, overview).
- **`last_updated`**: ISO 8601 date (YYYY-MM-DD). Not in the future. Required for all types.
- **`status`**: One of `draft | active | complete | abandoned`. Required for plans. Optional for research.
- **`tags`**: Lowercase, hyphenated strings. No duplicates.
- **`related`**: Relative file paths to peer documents.

## Sections by Type

### Topic (`/context/{area}/{topic}.md`)

| # | Section | Content |
|---|---------|---------|
| 1 | `## Guidance` | Actionable recommendations. Bold statement + explanation + citation. |
| 2 | `## Context` | Why this matters. Causal reasoning. |
| 3 | `## In Practice` | Concrete examples, worked scenarios, code blocks. |
| 4 | `## Pitfalls` | Mistakes, anti-patterns, counter-evidence. |
| 5 | `## Go Deeper` | Links to primary sources and further reading. |

Optional: `## Quick Reference` (between Pitfalls and Go Deeper) — tables/lists only, no prose.

### Overview (`/context/{area}/overview.md`)

| # | Section | Content |
|---|---------|---------|
| 1 | `## What This Covers` | Area scope prose. Min 30 words. |
| 2 | `## Topics` | Markdown table with link + Description column. Bidirectional sync with files on disk. |
| 3 | `## Key Sources` | Bulleted links to area-level sources. |

One overview.md per area directory. Exactly one.

### Research (`/artifacts/research/{date}-{slug}.md`)

| # | Section | Content |
|---|---------|---------|
| 1 | `## Question` | What was investigated and why. Non-empty. |
| 2 | `## Findings` | What was learned, by sub-question or theme. Cite sources inline. |
| 3 | `## Implications` | "So what" — how findings affect decisions. Inform, don't prescribe. |
| 4 | `## Sources` | Full bibliography with URLs and access dates. |

Research presents evidence. It does not prescribe action.

### Plan (`/artifacts/plans/{date}-{slug}.md`)

| # | Section | Content |
|---|---------|---------|
| 1 | `## Objective` | What will be true when done. May include Non-Goals subsection. |
| 2 | `## Context` | Links to research and prior decisions that inform the plan. |
| 3 | `## Steps` | Ordered work items. Each independently verifiable. |
| 4 | `## Verification` | Observable success criteria — commands, expected outputs, measurable outcomes. |

Status enum: `draft | active | complete | abandoned` (required in frontmatter).

## Size Constraints

| Type | Min lines | Max lines |
|------|-----------|-----------|
| Topic | 10 | 500 |
| Overview | 5 | 150 |
| Research | 20 | — (no upper bound) |
| Plan | 10 | — (no upper bound) |

## Source Integration (Topic + Research only)

- **Citation density**: Every claim in Guidance must have an inline citation. Findings should cite sources.
- **Source diversity**: At least 2 different domains or authors.
- **Counter-evidence**: Topics should include limitations in Pitfalls. Research should note disagreement across sources.

## Frontmatter Examples

### Topic

```yaml
---
document_type: topic
description: "Core principles for the first 10-15 moves of a chess game, with position evaluation and common openings"
last_updated: 2026-02-17
last_validated: 2026-02-17
sources:
  - url: https://example.com/chess-openings
    title: "Chess Opening Principles"
tags: [chess, openings, strategy]
---
```

### Overview

```yaml
---
document_type: overview
description: "Chess strategy covers opening principles, middlegame tactics, and endgame techniques for competitive play"
last_updated: 2026-02-17
last_validated: 2026-02-17
---
```

### Research

```yaml
---
document_type: research
description: "Investigation of document type systems across DITA, Diataxis, Zettelkasten, and agent context engineering"
last_updated: 2026-02-17
sources:
  - url: https://diataxis.fr/
    title: "Diataxis Framework"
status: complete
---
```

### Plan

```yaml
---
document_type: plan
description: "Implementation plan for four-type document system with Pydantic models and validators"
last_updated: 2026-02-17
status: active
---
```
