<objective>
Ingest an external URL into the knowledge base by fetching the content, evaluating it against existing KB material, and either proposing new content or recommending updates to existing topics.
</objective>

<process>
## Step 1: Parse arguments and resolve defaults

Parse `$ARGUMENTS` for the URL, topic name, and relevance. Examples of valid invocations:

- `/dewey:curate ingest https://docs.example.com/guide` -- URL only
- `/dewey:curate ingest https://docs.example.com/guide "Dependency Injection"` -- URL + topic name
- `/dewey:curate ingest https://docs.example.com/guide "Dependency Injection" --relevance supporting` -- URL + topic name + relevance

**Defaults:**
- **Topic name** -- If not provided, infer from the page title or URL path after fetching
- **Relevance** defaults to `core` unless specified

Do NOT ask the user for information that can be inferred. Get moving quickly.

## Step 2: Fetch and analyze the source

Read AGENTS.md to understand the role context, then fetch the URL:

1. **Fetch the URL** using WebFetch. Extract the main content, stripping navigation, ads, and boilerplate.
2. **Identify key information** relevant to the role: concepts, guidance, examples, caveats, and authoritative claims.
3. If the URL is inaccessible (404, paywall, authentication required), inform the user and offer to record the URL for manual distillation later.

## Step 3: Evaluate against existing KB content

Before proposing new material, check for overlap with what's already in the knowledge base:

1. **Scan existing topics** -- Read AGENTS.md manifest and browse `docs/` area directories to identify existing topics and their descriptions.
2. **Read overlapping topics** -- For any topic that covers related ground, read the working-knowledge file to understand what's already documented.
3. **Classify the source material** into one of three outcomes:

**Outcome A: New topic** -- The source covers material not addressed by any existing topic. Proceed to Step 4.

**Outcome B: Update existing topic(s)** -- The source adds new guidance, examples, or corrections to one or more existing topics. The source should be incorporated into those topics rather than creating a new one.

**Outcome C: Mixed** -- Some material is new and some overlaps. The new material warrants a proposal; the overlapping material should update existing topics.

Present the evaluation to the user:

"After reviewing the source against the existing KB, here's what I found:

- **Overlapping topics:** [list any existing topics that cover similar ground, with a brief note on what overlaps]
- **New material:** [describe what the source contributes that isn't already covered]
- **Recommendation:** [New topic / Update existing / Mixed]

How would you like to proceed?"

Wait for the user to confirm the approach before continuing.

## Step 4: Search for related sources

Search the web for 1-2 additional authoritative sources on the same topic. This cross-references the ingested URL and enriches the draft with multiple perspectives. Prioritize official documentation and recognized expert resources.

## Step 5: Draft content

Based on the user's chosen approach from Step 3:

### If creating a new proposal (Outcome A or new portion of C):

Distill the fetched content and related sources into the working-knowledge template:

- **Why This Matters** -- Causal reasoning: what problem this solves, why this approach. Drawn from the source's introduction or motivation sections.
- **In Practice** -- A concrete, worked example applied realistically. Use examples from the source or construct one based on the source's guidance.
- **Key Guidance** -- Actionable recommendations with inline source citations. Each recommendation should reference the specific source: `([Source Title](url))`.
- **Watch Out For** -- Common mistakes, edge cases, or caveats mentioned in the source.
- **Go Deeper** -- Links to the original ingested URL and all related sources found.

Also draft **reference companion** content:
- Terse, scannable quick-lookup version of the key guidance (tables, lists, quick rules)

### If updating existing topics (Outcome B or overlapping portion of C):

For each existing topic to update, draft:
- Specific additions or revisions to each section (Key Guidance, Watch Out For, etc.)
- New source to add to the frontmatter `sources:` field
- Any corrections to existing content based on the new source

## Step 6: Create proposal or apply updates

### For new proposals:

Run the propose script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/curate/scripts/propose.py --kb-root <kb_root> --topic "<topic_name>" --relevance "<relevance>" --proposed-by "ingest" --rationale "Ingested from: <url>"
```

Then update the proposal file:
1. Replace template placeholder sections with the drafted content
2. Update frontmatter `sources:` with all sources:

```yaml
sources:
  - url: https://docs.example.com/guide
    title: "Example Guide -- Official Docs"
  - url: https://related-source.com/article
    title: "Related Article"
```

### For updates to existing topics:

Present the proposed edits to each existing topic file, showing what would change. Do NOT apply edits until the user approves.

## Step 7: Present draft for review

Present the complete draft (new proposal and/or proposed updates to existing topics) to the user. For each section, note which source(s) informed it. Ask: "Does this capture the key information from the source? Should I adjust anything?"

The human brings domain judgment. Accept their edits and corrections. If they approve, proceed. If they have changes, revise and re-present.

## Step 8: Write approved content and report next steps

Write the final approved content. Then report what was done:

**If a new proposal was created:**
"The proposal has been created at `docs/_proposals/<slug>.md` with content distilled from the source. Next steps:
1. **Validate** -- Use `/dewey:health check` to run quality validators
2. **Promote** -- Use `/dewey:curate promote <slug> --target-area <area>` to move it into a domain area"

**If existing topics were updated:**
"The following topics were updated with new material from `<url>`:
- `docs/<area>/<topic>.md` -- [brief description of changes]
The source has been added to each topic's frontmatter."
</process>

<success_criteria>
- Source URL fetched and content analyzed
- Existing KB scanned for overlap -- evaluation presented to user before drafting
- User confirmed whether to create new content, update existing, or both
- For new proposals: content filled in (not template placeholders), source URL in frontmatter
- For existing topic updates: changes applied with new source added to frontmatter
- Additional related sources found and cited
- Content reviewed and approved by the user before any writes
</success_criteria>
