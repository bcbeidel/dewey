<objective>
Create or update a topic in a domain area, research primary sources, and draft initial content for the user's review.
</objective>

<process>
## Step 1: Resolve topic and area from intake context

The intake classifier has already identified the user's intent. Extract:

- **Topic name** — from the user's free-text input
- **Domain area** — auto-detect:
  1. If only one domain area exists under the knowledge directory, use it
  2. If the user mentioned an area, use that
  3. Otherwise, list available areas and ask the user to pick one
- **Relevance** — default to `core` unless the user specified otherwise
- **Mode** — `new` (create topic) or `update` (modify existing topic). The intake classifier sets this.

Do NOT ask the user for information that can be inferred. Get moving quickly.

## Step 2: Verify the domain area and create topic files

Check that `docs/<area>/` exists. If it does not, inform the user and suggest creating it first.

Run the create_topic script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/curate/scripts/create_topic.py --kb-root <kb_root> --area <area> --topic "<topic_name>" --relevance "<relevance>"
```

### If mode is `update` (updating an existing topic):

1. Read the existing topic file at `docs/<area>/<slug>.md`
2. Present the current content to the user: "Here's what's currently in this topic:"
3. Ask: "What would you like to change or add?"
4. Skip to Step 3 (Research and draft) but scope the research to the specific changes requested
5. In Step 4 (Present draft), show a diff of what changed rather than the full content

## Step 3: Research and draft

Read AGENTS.md to understand the role context, then:

1. **Search the web** for 3-5 high-quality, authoritative sources on this topic relevant to the role. Prioritize official documentation, recognized expert resources, and practitioner-oriented content.

2. **Draft content** for both files using the sources found:

   **Working-knowledge file** (`<slug>.md`):
   - **Why This Matters** -- Causal reasoning: what problem this solves, why this approach
   - **In Practice** -- A concrete, worked example applied realistically
   - **Key Guidance** -- Actionable recommendations with inline source citations
   - **Watch Out For** -- Common mistakes, edge cases, things that change
   - **Go Deeper** -- Links to reference file and primary sources

   **Reference companion** (`<slug>.ref.md`):
   - Terse, scannable quick-lookup version of the key guidance

3. **Update frontmatter** `sources:` field with the actual primary sources found.

## Step 4: Present draft and get approval

Present the complete draft to the user. Cite which sources informed each section. Ask: "Does this capture your understanding, or should I adjust anything?"

The human brings domain judgment. Accept their edits and corrections. If they approve, proceed. If they have changes, revise and re-present.

## Step 5: Write approved content and update manifest

Write the approved content to both topic files, then update the three index files below. When updating AGENTS.md or CLAUDE.md, only modify content between `<!-- dewey:kb:begin -->` / `<!-- dewey:kb:end -->` markers.

### 5a. AGENTS.md — add topic to the domain area table

The managed section contains domain area headings like `### area-slug`. Under each heading is a topic table. Add a row to the table for the new topic:

```markdown
### python-foundations

| Topic | Description |
|-------|-------------|
| [Project Structure](docs/python-foundations/project-structure.md) | src layout, UI/logic separation, pyproject.toml |
```

- If no table exists yet under the heading, create one with the header row + separator + new row
- Link format: `[Topic Name](docs/<area>/<slug>.md)` — always include the file path
- Description: one-line summary of the topic
- Do NOT use bullet lists — always use a table row with a linked path

### 5b. overview.md — add topic to table AND populate Key Sources

Make two updates to `docs/<area>/overview.md`:

**"How It's Organized" table** — add a row for the new topic:

```markdown
| [Project Structure](project-structure.md) | src layout, UI/logic separation |
```

Links are relative within the area directory, so use `<slug>.md` (not the full `docs/<area>/` path).

**"Key Sources" section** — replace `<!-- placeholder -->` (or any empty placeholder) with the primary sources found during research:

```markdown
## Key Sources
- [src layout vs flat layout](https://packaging.python.org/...) -- Python Packaging User Guide
- [Multipage apps with st.Page](https://docs.streamlit.io/...) -- Streamlit Docs
```

List the 3-5 authoritative sources that were used during the research step. Never leave this as a placeholder.

### 5c. CLAUDE.md — verify domain area is listed

CLAUDE.md's Domain Areas table lists areas, not individual topics. After adding a topic, verify the area already appears in the table (it should if the area was initialized). If the area is missing, add a row:

```markdown
| area-name | `docs/area-slug/` | [overview.md](docs/area-slug/overview.md) |
```

If the area is already listed, no changes needed — do not add individual topics to CLAUDE.md.

## Step 6: Rebuild index.md

Regenerate the table of contents so the new topic appears:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/scaffold.py --target <kb_root> --rebuild-index
```

## Step 7: Update curation plan

If `.dewey/curation-plan.md` exists, check for an item matching the topic name just added (case-insensitive match on the name portion before ` -- `). If found, mark it as done by changing `- [ ]` to `- [x]`. Update `last_updated` in the frontmatter to today's date.
</process>

<success_criteria>
- Topic working-knowledge file created with researched content
- Topic reference file created with terse quick-lookup version
- Primary sources identified and cited in frontmatter and inline
- Content reviewed and approved by the user
- AGENTS.md has a linked table row (`[Topic](docs/<area>/<slug>.md)`) under the domain area heading — not a bullet
- overview.md "How It's Organized" has a linked table row (`[Topic](<slug>.md)`) for the topic
- overview.md "Key Sources" is populated with actual sources found during research — not a placeholder
- CLAUDE.md domain area is present in the Domain Areas table
</success_criteria>
