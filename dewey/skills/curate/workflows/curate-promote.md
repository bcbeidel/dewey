<objective>
Promote a validated proposal from _proposals/ into a domain area, create the reference companion, and update all indexes.
</objective>

<process>
## Step 1: List pending proposals

Scan `docs/_proposals/` for .md files. Present the list to the user:

"Here are the pending proposals:

1. `<slug>.md` -- <title from frontmatter>
2. `<slug>.md` -- <title from frontmatter>
..."

If there are no proposals, inform the user: "No pending proposals found in `docs/_proposals/`. Use `/dewey:curate propose` to create one."

## Step 2: Select proposal and target area

Ask the user:

1. **Which proposal** to promote (by number or slug name)
2. **Target domain area** -- Which domain area directory should it go into? (e.g., "campaign-management")

If these were provided in `$ARGUMENTS`, use those values instead of asking.

## Step 3: Verify the target area exists

Check that `docs/<target_area>/` exists. If not, inform the user and suggest creating it first.

## Step 4: Run promote script

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/curate/scripts/promote.py --kb-root <kb_root> --proposal "<slug>" --target-area "<target_area>"
```

This moves the proposal to `docs/<target_area>/<slug>.md` and strips proposal-specific frontmatter (status, proposed_by, rationale).

## Step 5: Create reference companion

If `docs/<target_area>/<slug>.ref.md` does not already exist, create it with:

- Frontmatter matching the promoted topic (same sources, last_validated, relevance, but `depth: reference`)
- A terse, scannable quick-lookup version of the key guidance from the promoted topic
- Tables, lists, quick rules -- minimal prose
- A "See also" link back to the working-knowledge file

## Step 6: Update indexes

Update the three index files. When updating AGENTS.md or CLAUDE.md, only modify content between `<!-- dewey:kb:begin -->` / `<!-- dewey:kb:end -->` markers.

### 6a. AGENTS.md -- add topic to the domain area table

The managed section contains domain area headings like `### area-slug`. Under each heading is a topic table. Add a row:

```markdown
### streamlit-patterns

| Topic | Description |
|-------|-------------|
| [Multipage Apps](docs/streamlit-patterns/multipage-apps.md) | pages/ directory vs st.navigation, routing, and access control |
```

- If no table exists yet under the heading, create one with the header row + separator + new row
- Link format: `[Topic Name](docs/<area>/<slug>.md)` -- always include the file path
- Description: one-line summary of the topic
- Do NOT use bullet lists -- always use a table row with a linked path

### 6b. overview.md -- add topic to table AND populate Key Sources

Make two updates to `docs/<area>/overview.md`:

**"How It's Organized" table** -- add a row:

```markdown
| [Multipage Apps](multipage-apps.md) | pages/ directory vs st.navigation, routing, and access control |
```

Links are relative within the area directory, so use `<slug>.md` (not the full `docs/<area>/` path).

**"Key Sources" section** -- if still a placeholder, replace with the primary sources from the promoted topic's frontmatter:

```markdown
## Key Sources
- [Source Title](https://example.com) -- Brief description
```

### 6c. CLAUDE.md -- verify domain area is listed

CLAUDE.md's Domain Areas table lists areas, not individual topics. After promoting, verify the area already appears in the table. If the area is missing, add a row:

```markdown
| area-name | `docs/area-slug/` | [overview.md](docs/area-slug/overview.md) |
```

If the area is already listed, no changes needed -- do not add individual topics to CLAUDE.md.

## Step 7: Update curation plan

If `.dewey/curation-plan.md` exists, check for an item matching the promoted topic name (case-insensitive match on the name portion before ` -- `). If found, mark it as done by changing `- [ ]` to `- [x]`. Update `last_updated` in the frontmatter to today's date.

## Step 8: Rebuild index.md

Regenerate the table of contents so the promoted topic appears:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/curate/scripts/scaffold.py --target <kb_root> --rebuild-index
```

## Step 9: Report what was done

Summarize all changes:
- Promoted file location
- Reference companion created (if new)
- AGENTS.md row added
- overview.md updated
- CLAUDE.md verified
- Curation plan updated (if applicable)
</process>

<success_criteria>
- Proposal file removed from _proposals/
- Topic file created in target domain area with proposal frontmatter stripped
- Reference companion (`<slug>.ref.md`) created with terse quick-lookup content
- AGENTS.md has a linked table row (`[Topic](docs/<area>/<slug>.md)`) under the domain area heading -- not a bullet
- overview.md "How It's Organized" has a linked table row for the topic
- overview.md "Key Sources" is populated (not a placeholder) if this is the first topic in the area
- CLAUDE.md domain area is present in the Domain Areas table
</success_criteria>
