<objective>
Run Tier 1 deterministic checks followed by Tier 2 LLM-assisted quality assessment on flagged or stale entries.
</objective>

<process>
## Step 1: Run Tier 1 checks

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/health/scripts/check_kb.py --kb-root <kb_root>
```

Capture the JSON output. Present the Tier 1 summary as in the health-check workflow.

## Step 2: Run Tier 2 pre-screening

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/health/scripts/check_kb.py --kb-root <kb_root> --tier2
```

Capture the JSON output. The pre-screener runs 5 deterministic triggers on each file and returns a structured queue with context data for each item.

Present the trigger summary:

| Trigger | Count | Description |
|---------|-------|-------------|
| source_drift | N | Files with stale or missing last_validated dates |
| depth_accuracy | N | Files where word count or prose ratio doesn't match depth |
| source_primacy | N | Working files with low inline citation density |
| why_quality | N | Working files with missing or thin "Why This Matters" |
| concrete_examples | N | Working files with missing or abstract "In Practice" |

"**Tier 2 evaluation queue:** <N> items across <M> files."

## Step 3: Perform Tier 2 LLM assessment

Iterate the queue items from Step 2. Each item includes pre-computed context data -- use it to focus assessment rather than manually counting or re-reading.

### 3a. Source drift

For items with `trigger: source_drift`, the context includes `source_urls`. For each URL, use the **WebFetch** tool to retrieve the current content:

```
WebFetch(url=<source_url>, prompt="Summarize the key claims and recommendations in this document")
```

Compare the fetched content against the claims in the knowledge base entry. Flag if:
- The knowledge base entry makes claims not supported by the sources
- The sources have been updated with information not reflected in the knowledge base entry
- Sources are no longer accessible (WebFetch returns an error)

If a source URL cannot be fetched (timeout, 404, paywall), note: "Source drift check skipped for `<url>` -- not accessible." and continue with the remaining sources.

### 3b. Depth label accuracy

For items with `trigger: depth_accuracy`, the context includes `declared_depth`, `word_count`, `prose_ratio`, and expected ranges. Use these metrics to guide evaluation:
- **overview** -- Should orient: what is this area, why it matters, how topics connect. Should NOT contain detailed how-to guidance.
- **working** -- Should have actionable guidance: In Practice examples, Key Guidance, Watch Out For. Should NOT be terse/scannable-only.
- **reference** -- Should be terse and scannable: tables, lists, lookup patterns. Should NOT have lengthy narrative.

Flag if the content does not match its declared depth.

### 3c. "Why This Matters" quality

For items with `trigger: why_quality`, the context includes `has_section`, `word_count`, and `min_required`. Evaluate:
- Does it explain **why**, not just **what**?
- Does it connect to the role's goals and outcomes?
- Would someone unfamiliar with the topic understand the stakes?

Flag if the section reads as a description rather than a motivation.

### 3d. "In Practice" concreteness

For items with `trigger: concrete_examples`, the context includes `has_section`, `has_code_block`, `has_table`, `has_numeric_example`, and `section_word_count`. Evaluate:
- Does it contain a **concrete example** (specific scenario, numbers, names)?
- Could someone follow this guidance in a real situation?
- Is it actionable, not just theoretical?

Flag if the section is abstract or generic.

### 3e. Source primacy

For items with `trigger: source_primacy`, the context includes `recommendation_count`, `inline_source_count`, and `sections_checked`. Evaluate whether the guidance is adequately backed by inline citations to authoritative sources.

## Step 4: Persist results

Write the combined Tier 2 assessment to `.dewey/health/tier2-report.json` so `health-review.md` can read results without re-running:

```python
import json
from pathlib import Path

report_dir = Path("<kb_root>") / ".dewey" / "health"
report_dir.mkdir(parents=True, exist_ok=True)
(report_dir / "tier2-report.json").write_text(json.dumps(report, indent=2))
```

## Step 5: Present combined report

Format the combined Tier 1 + Tier 2 report:

```
## Audit Report

### Tier 1: Deterministic Checks
<summary from Step 1>

### Tier 2: LLM Assessment
<N> entries evaluated.

| File | Source Drift | Depth Accuracy | Why Quality | In Practice Quality | Source Primacy |
|------|-------------|----------------|-------------|---------------------|---------------|
| <path> | OK / Flag | OK / Flag | OK / Flag | OK / Flag | OK / Flag |

### Detailed Findings
<for each flagged item, provide specific reasoning and a recommendation>
```

## Step 6: Suggest next steps

- Entries with Tier 2 flags -> "Re-validate these entries against their sources and update the content."
- Entries with depth mismatches -> "Consider changing the depth label or restructuring the content."
- Entries with weak Why/In Practice -> "Strengthen these sections with causal reasoning and concrete examples."
- If many entries are flagged -> "Consider running `/dewey:health review` to surface items for human decision."
</process>

<success_criteria>
- Tier 1 checks run successfully and results are presented
- Tier 2 pre-screener runs and produces a structured trigger queue with context data
- Each Tier 2 assessment uses pre-computed context to focus evaluation
- Combined report clearly separates Tier 1 and Tier 2 findings
- Results are persisted to `.dewey/health/tier2-report.json`
- Recommendations are actionable and specific to each finding
</success_criteria>
