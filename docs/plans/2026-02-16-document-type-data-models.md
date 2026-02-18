# Document Type Data Models

Date: 2026-02-17

Implementation reference for the document type system using Pydantic v2.
For the normative specification with rationale, see
`docs/plans/2026-02-16-document-type-specification.md`.
For the concise rules reference, see
`docs/plans/2026-02-16-document-type-reference.md`.

---

## 1. Enums and Constants

```python
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    OVERVIEW = "overview"
    TOPIC = "topic"
    RESEARCH = "research"
    PLAN = "plan"


class PlanStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETE = "complete"
    ABANDONED = "abandoned"


# Type groupings for validation dispatch
CONTEXT_TYPES = {DocumentType.OVERVIEW, DocumentType.TOPIC}
ARTIFACT_TYPES = {DocumentType.RESEARCH, DocumentType.PLAN}
SOURCE_GROUNDED_TYPES = {DocumentType.TOPIC, DocumentType.RESEARCH}
FRESHNESS_TRACKED_TYPES = {DocumentType.TOPIC, DocumentType.OVERVIEW}
```

---

## 2. Shared Models

```python
class Source(BaseModel):
    url: str
    title: str


class FrontmatterBase(BaseModel):
    """Fields common to all four document types."""
    description: str = Field(min_length=10)
    last_updated: date

    # Optional fields available on all types
    tags: Optional[list[str]] = None
    related: Optional[list[str]] = None

    @field_validator("description")
    @classmethod
    def description_not_a_label(cls, v: str) -> str:
        if len(v.split()) < 5:
            raise ValueError("description must be descriptive, not a category label")
        return v

    @field_validator("last_updated")
    @classmethod
    def not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("date must not be in the future")
        return v
```

---

## 3. Type-Specific Frontmatter Models

```python
class TopicFrontmatter(FrontmatterBase):
    document_type: Literal["topic"]
    sources: list[Source] = Field(min_length=1)
    last_validated: date

    @field_validator("last_validated")
    @classmethod
    def validated_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("last_validated must not be in the future")
        return v


class OverviewFrontmatter(FrontmatterBase):
    document_type: Literal["overview"]
    last_validated: date

    @field_validator("last_validated")
    @classmethod
    def validated_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("last_validated must not be in the future")
        return v


class ResearchFrontmatter(FrontmatterBase):
    document_type: Literal["research"]
    sources: list[Source] = Field(min_length=1)
    status: Optional[PlanStatus] = None  # optional for research


class PlanFrontmatter(FrontmatterBase):
    document_type: Literal["plan"]
    status: PlanStatus  # required for plans


# Discriminated union: Pydantic routes to the correct model
# based on the `document_type` field value.
Frontmatter = Annotated[
    Union[
        TopicFrontmatter,
        OverviewFrontmatter,
        ResearchFrontmatter,
        PlanFrontmatter,
    ],
    Field(discriminator="document_type"),
]
```

---

## 4. Section Definitions

```python
class SectionSpec(BaseModel):
    """Defines a required section for a document type."""
    name: str
    position: int  # 1-indexed canonical position
    min_words: Optional[int] = None


SECTIONS: dict[DocumentType, list[SectionSpec]] = {
    DocumentType.TOPIC: [
        SectionSpec(name="Guidance", position=1),
        SectionSpec(name="Context", position=2),
        SectionSpec(name="In Practice", position=3),
        SectionSpec(name="Pitfalls", position=4),
        SectionSpec(name="Go Deeper", position=5),
    ],
    DocumentType.OVERVIEW: [
        SectionSpec(name="What This Covers", position=1, min_words=30),
        SectionSpec(name="Topics", position=2),
        SectionSpec(name="Key Sources", position=3),
    ],
    DocumentType.RESEARCH: [
        SectionSpec(name="Question", position=1),
        SectionSpec(name="Findings", position=2),
        SectionSpec(name="Implications", position=3),
        SectionSpec(name="Sources", position=4),
    ],
    DocumentType.PLAN: [
        SectionSpec(name="Objective", position=1),
        SectionSpec(name="Context", position=2),
        SectionSpec(name="Steps", position=3),
        SectionSpec(name="Verification", position=4),
    ],
}

# Optional sections with positional constraints
OPTIONAL_SECTIONS: dict[DocumentType, dict[str, dict]] = {
    DocumentType.TOPIC: {
        "Quick Reference": {"after": "Pitfalls", "before": "Go Deeper"},
    },
}
```

---

## 5. Size Constraints

```python
class SizeBounds(BaseModel):
    min_lines: int
    max_lines: Optional[int] = None  # None = no upper bound


SIZE_BOUNDS: dict[DocumentType, SizeBounds] = {
    DocumentType.TOPIC:    SizeBounds(min_lines=10, max_lines=500),
    DocumentType.OVERVIEW: SizeBounds(min_lines=5, max_lines=150),
    DocumentType.RESEARCH: SizeBounds(min_lines=20),
    DocumentType.PLAN:     SizeBounds(min_lines=10),
}
```

---

## 6. Document Model

```python
class Document(BaseModel):
    """A complete parsed knowledge record."""
    path: str
    frontmatter: Frontmatter  # discriminated union dispatches here
    title: str
    sections: dict[str, str]  # section_name -> section_content
    raw_content: str

    @property
    def document_type(self) -> DocumentType:
        return DocumentType(self.frontmatter.document_type)

    @property
    def required_sections(self) -> list[SectionSpec]:
        return SECTIONS[self.document_type]

    @property
    def size_bounds(self) -> SizeBounds:
        return SIZE_BOUNDS[self.document_type]


def parse_document(path: str, content: str) -> Document:
    """Parse a markdown file into a validated Document.

    Raises ValidationError with clear messages on:
    - Missing or invalid frontmatter fields
    - Wrong document_type value
    - Invalid dates, empty sources, bad status values
    - Type-specific field violations
    """
    frontmatter_dict, title, sections, raw = _split_markdown(content)
    frontmatter = Frontmatter.model_validate(frontmatter_dict)
    return Document(
        path=path,
        frontmatter=frontmatter,
        title=title,
        sections=sections,
        raw_content=raw,
    )
```

---

## 7. Directory Layout

```python
import re

DIRECTORY_PATTERNS: dict[DocumentType, str] = {
    DocumentType.TOPIC:    r"context/[\w-]+/[\w-]+\.md$",
    DocumentType.OVERVIEW: r"context/[\w-]+/overview\.md$",
    DocumentType.RESEARCH: r"artifacts/research/\d{4}-\d{2}-\d{2}-[\w-]+\.md$",
    DocumentType.PLAN:     r"artifacts/plans/\d{4}-\d{2}-\d{2}-[\w-]+\.md$",
}

DATE_PREFIX_TYPES = {DocumentType.RESEARCH, DocumentType.PLAN}


def check_directory_placement(doc: Document) -> list[dict]:
    """Validate that a document lives in the correct directory."""
    pattern = DIRECTORY_PATTERNS[doc.document_type]
    if not re.search(pattern, doc.path):
        return [{"file": doc.path, "message": (
            f"document_type '{doc.document_type.value}' should live at "
            f"pattern {pattern}, found at {doc.path}"
        ), "severity": "warn"}]
    return []
```

---

## 8. Validation Dispatch

```python
# Validators are functions: (Document) -> list[dict]
# The dispatch table determines which validators run for which types.

VALIDATORS_ALL_TYPES: list[str] = [
    "check_description_quality",
    "check_title_heading",
    "check_heading_hierarchy",
    "check_size_bounds",
    "check_placeholder_comments",
    "check_date_fields",
    "check_naming_conventions",
    "check_section_presence",
    "check_section_ordering",
    "check_directory_placement",
]
# Note: check_frontmatter_fields is replaced by Pydantic validation
# at parse time — invalid frontmatter raises ValidationError before
# validators run.

VALIDATORS_BY_TYPE: dict[DocumentType, list[str]] = {
    DocumentType.TOPIC: [
        "check_source_diversity",
        "check_citation_grounding",
        "check_go_deeper_links",
        "check_readability",
        "check_last_validated",
    ],
    DocumentType.OVERVIEW: [
        "check_overview_topic_sync",
        "check_topics_table_format",
        "check_what_this_covers_length",
        "check_readability",
        "check_last_validated",
    ],
    DocumentType.RESEARCH: [
        "check_source_diversity",
        "check_citation_grounding",
        "check_question_nonempty",
        "check_date_prefix_matches",
    ],
    DocumentType.PLAN: [
        "check_date_prefix_matches",
    ],
}
# Note: check_status_field for plans is replaced by Pydantic —
# PlanFrontmatter.status is a required PlanStatus enum field.

CROSS_VALIDATORS: list[str] = [
    "check_link_graph",
    "check_duplicate_content",
    "check_naming_conventions",
    "check_overview_topic_sync",
]
```

---

## 9. Tier 2 Triggers (LLM-Assisted)

Tier 2 triggers run deterministically to detect _candidates_ for LLM review.
Each trigger gathers context data that the LLM uses to evaluate quality.
Triggers fire when heuristic thresholds are crossed — the LLM then determines
whether there is an actual problem.

```python
# Each trigger returns:
# {"file": str, "trigger": str, "reason": str, "context": dict}
#
# The "context" dict provides structured data the LLM needs to
# make its assessment — word counts, section text, source lists, etc.

# ── Shared triggers (multiple types) ────────────────────────────

TIER2_TRIGGERS_SHARED = {
    "trigger_description_quality": {
        "types": DOCUMENT_TYPES,
        "fires_when": "description is under 10 words or reads like a category label",
        "context": ["description_text", "word_count"],
        "llm_evaluates": (
            "Does this description provide genuine information scent? "
            "Could a reader decide whether to load the full document "
            "based on this description alone?"
        ),
    },
}

# ── Topic triggers ──────────────────────────────────────────────

TIER2_TRIGGERS_TOPIC = {
    "trigger_why_quality": {
        "fires_when": "Context section is thin (< 50 words) or missing causal language",
        "context": ["context_section_text", "word_count", "causal_keywords_found"],
        "llm_evaluates": (
            "Does the Context section explain WHY the guidance works, "
            "not just WHAT to do? Look for causal reasoning: 'because', "
            "'this matters when', 'the reason is'."
        ),
    },
    "trigger_in_practice_concreteness": {
        "fires_when": "In Practice section lacks code blocks, tables, or specific examples",
        "context": ["in_practice_text", "code_block_count", "table_count"],
        "llm_evaluates": (
            "Does the In Practice section contain concrete, specific "
            "examples a practitioner could apply directly? Or is it "
            "abstract guidance restated?"
        ),
    },
    "trigger_source_drift": {
        "fires_when": "last_validated is more than 90 days old",
        "context": ["sources_list", "days_since_validated", "key_claims"],
        "llm_evaluates": (
            "Given the sources and key claims, is there a meaningful "
            "risk that the guidance is outdated? Consider how fast "
            "this domain evolves."
        ),
    },
    "trigger_source_authority": {
        "fires_when": "sources are from unfamiliar or potentially low-authority domains",
        "context": ["source_domains", "source_urls"],
        "llm_evaluates": (
            "Are these sources authoritative for this domain? Look for "
            "official docs, peer-reviewed research, recognized experts, "
            "or established organizations."
        ),
    },
    "trigger_pitfalls_completeness": {
        "fires_when": "Pitfalls section has fewer than 2 items",
        "context": ["pitfalls_text", "pitfall_count", "guidance_text"],
        "llm_evaluates": (
            "Given the guidance provided, are there obvious pitfalls, "
            "edge cases, or common mistakes that are missing from the "
            "Pitfalls section?"
        ),
    },
}

# ── Overview triggers ───────────────────────────────────────────

TIER2_TRIGGERS_OVERVIEW = {
    "trigger_overview_coverage_quality": {
        "fires_when": "What This Covers section is under 30 words",
        "context": ["what_this_covers_text", "word_count"],
        "llm_evaluates": (
            "Does this section provide genuine orientation for the area? "
            "Could a reader new to this domain understand what they'll "
            "find here and whether it's relevant to them?"
        ),
    },
    "trigger_overview_navigation_quality": {
        "fires_when": "Topics table lacks a Description column or descriptions are terse",
        "context": ["topics_table_text", "description_lengths"],
        "llm_evaluates": (
            "Do the topic descriptions provide information scent? "
            "Could a reader choose the right topic without clicking "
            "through to each one?"
        ),
    },
}

# ── Research triggers ───────────────────────────────────────────

TIER2_TRIGGERS_RESEARCH = {
    "trigger_question_clarity": {
        "fires_when": "Question section is under 20 words or lacks a clear question",
        "context": ["question_text", "word_count"],
        "llm_evaluates": (
            "Is the research question specific enough to guide a "
            "focused investigation? Could another researcher "
            "reproduce the scope of this inquiry from the question alone?"
        ),
    },
    "trigger_finding_groundedness": {
        "fires_when": "Findings section has fewer inline citations than claims",
        "context": ["findings_text", "citation_count", "claim_sentences"],
        "llm_evaluates": (
            "Are the findings grounded in the cited sources? Look for "
            "claims that lack attribution, opinions presented as facts, "
            "or conclusions that don't follow from the evidence presented."
        ),
    },
    "trigger_implication_relevance": {
        "fires_when": "Implications section exists but is under 30 words",
        "context": ["implications_text", "findings_summary"],
        "llm_evaluates": (
            "Do the implications connect findings to actionable "
            "concerns? Or do they merely restate findings without "
            "explaining what they mean for decisions or next steps?"
        ),
    },
}

# ── Plan triggers ───────────────────────────────────────────────

TIER2_TRIGGERS_PLAN = {
    "trigger_step_specificity": {
        "fires_when": "Steps section has items under 10 words or lacks verifiable outcomes",
        "context": ["steps_text", "step_count", "avg_step_length"],
        "llm_evaluates": (
            "Are the steps concrete enough for an agent to execute "
            "without asking clarifying questions? Each step should "
            "describe a verifiable action, not a vague intention."
        ),
    },
    "trigger_verification_completeness": {
        "fires_when": "Verification section is under 20 words or lacks observable criteria",
        "context": ["verification_text", "objective_text"],
        "llm_evaluates": (
            "Do the verification criteria cover the objective? Could "
            "someone confirm the plan succeeded by checking only the "
            "verification section? Look for concrete commands, expected "
            "outputs, or measurable outcomes."
        ),
    },
    "trigger_objective_clarity": {
        "fires_when": "Objective section describes activity ('we will do X') rather than outcome",
        "context": ["objective_text", "word_count"],
        "llm_evaluates": (
            "Does the objective describe what will be TRUE when the "
            "plan is complete, or does it describe activity? "
            "'Implement feature X' is activity; 'Users can do Y' is outcome."
        ),
    },
    "trigger_context_sufficiency": {
        "fires_when": "Context section is empty or has no links to research/prior work",
        "context": ["context_text", "link_count"],
        "llm_evaluates": (
            "Does the plan provide enough context for someone to "
            "understand WHY this approach was chosen? Are there links "
            "to research or prior decisions that informed the plan?"
        ),
    },
}

# ── Dispatch ────────────────────────────────────────────────────

TIER2_TRIGGERS_BY_TYPE = {
    "topic":    {**TIER2_TRIGGERS_SHARED, **TIER2_TRIGGERS_TOPIC},
    "overview": {**TIER2_TRIGGERS_SHARED, **TIER2_TRIGGERS_OVERVIEW},
    "research": {**TIER2_TRIGGERS_SHARED, **TIER2_TRIGGERS_RESEARCH},
    "plan":     {**TIER2_TRIGGERS_SHARED, **TIER2_TRIGGERS_PLAN},
}
```
