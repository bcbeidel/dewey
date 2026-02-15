# Tier 2 LLM-Assisted Audit -- Polish Design

**Date:** 2026-02-15
**Status:** Approved
**Scope:** Test and polish the existing Tier 2 audit flow so `/dewey:health audit` works end-to-end

## Problem Statement

The Tier 2 pre-screener (`tier2_triggers.py`) and the audit workflow (`health-audit.md`) are both written and tested individually, but have never been run end-to-end. The pre-screener produces a structured queue with context data. The workflow describes how Claude should evaluate each item. The gap is validation that these pieces fit together smoothly.

## What Already Exists

1. **`tier2_triggers.py`** -- 5 deterministic triggers (source_drift, depth_accuracy, source_primacy, why_quality, concrete_examples). Each returns `{file, trigger, reason, context}` with pre-computed metrics.
2. **`check_kb.py --tier2`** -- Runs all triggers, returns `{queue: [...], summary: {...}}`.
3. **`health-audit.md`** -- 6-step workflow: run Tier 1, run pre-screener, Claude evaluates each queued item using context, persist to `tier2-report.json`, present combined report, suggest next steps.

## Approach

**Workflow-driven.** No new scripts or API calls. Claude follows the `health-audit.md` workflow instructions, using the pre-computed trigger context to focus its evaluation. The Python pre-screener does the data collection; Claude does the judgment.

## Work Items

1. **Run end-to-end against sandbox KB** -- Execute the audit workflow manually against `sandbox/` to identify friction points.
2. **Fix workflow wording** -- Adjust `health-audit.md` instructions if any steps are ambiguous or produce poor results.
3. **Verify trigger context quality** -- Ensure the context data from each trigger is sufficient for Claude to make good judgments without re-reading entire files.
4. **Test result persistence** -- Verify `.dewey/health/tier2-report.json` is written correctly and `health-review.md` can consume it.
5. **Update CLAUDE.md status** -- Mark Tier 2 audit as complete once validated.

## Non-Goals

- No new trigger types
- No Python-based LLM orchestration (no API calls from scripts)
- No changes to Tier 1 validators
- No changes to Tier 3 design

## Success Criteria

- `/dewey:health audit` can be run against the sandbox KB and produces a combined Tier 1 + Tier 2 report
- Each Tier 2 evaluation includes reasoning, not just pass/fail
- Results persist to `.dewey/health/tier2-report.json`
- No regressions in existing tests (257 passing)
