# Curate Skill Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Consolidate explore, init, and curate into a single free-text-first skill that classifies user intent and routes to the appropriate workflow.

**Architecture:** Rewrite curate/SKILL.md as a free-text intent classifier. Move explore-discovery.md and init.md into curate/workflows/ as curate-discover.md and curate-setup.md. Strip argument parsing from existing curate workflows. Delete explore/ and init/ entry points.

**Tech Stack:** Markdown skill files only. No Python changes. Existing scripts (scaffold.py, templates.py, config.py) stay in place.

**Design doc:** `docs/plans/2026-02-15-curate-redesign.md`

---

### Task 1: Create curate-discover.md

Adapt explore-discovery.md into a curate workflow that calls scaffold.py directly and continues into plan-building.

**Files:**
- Source (read only): `dewey/skills/explore/workflows/explore-discovery.md`
- Create: `dewey/skills/curate/workflows/curate-discover.md`

**Step 1: Create the workflow file**

Copy the content of `explore-discovery.md` and modify:

1. In Phase 5 (Handoff to Init), replace the `/dewey:init` invocation with a direct scaffold.py call:

```markdown
## Phase 5: Scaffold the Knowledge Base

Once the user confirms the role and domains:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/scaffold.py --target <directory> --role "<persona>" --areas "<area1>,<area2>,<area3>"
```

Ask the user where to store knowledge base files (default: `docs`). If they specify a directory, add `--knowledge-dir "<dir>"`.
```

2. Add a new Phase 6 that builds the curation plan and resumes the user's original intent:

```markdown
## Phase 6: Build Curation Plan and Resume

After scaffolding:

1. For each domain area, propose 2-3 starter topics based on the user's stated goals
2. Present them grouped by area and ask the user to confirm or adjust
3. Write `.dewey/curation-plan.md` with the confirmed topics:

    ```markdown
    ---
    last_updated: <today's date YYYY-MM-DD>
    ---

    # Curation Plan

    ## <area-slug>
    - [ ] Topic Name -- core -- brief rationale
    ```

4. If the user had a specific topic in mind when they started (e.g., "I want to add a topic about X"), resume by routing to curate-add.md with that topic. Otherwise, present the plan and ask what they'd like to work on first.
```

3. Update `<objective>` to: "Help the user discover what knowledge domains to capture, scaffold the knowledge base, and build an initial curation plan."

4. Keep all other content (Phase 1-4) identical — the guided conversation logic is solid.

**Step 2: Verify the file**

Read `dewey/skills/curate/workflows/curate-discover.md` and confirm:
- No reference to `/dewey:init` or `/dewey:explore`
- scaffold.py called directly with `${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/scaffold.py`
- Phase 6 builds the curation plan
- `required_reading` includes `${CLAUDE_PLUGIN_ROOT}/skills/init/references/kb-spec-summary.md`

**Step 3: Commit**

```bash
git add dewey/skills/curate/workflows/curate-discover.md
git commit -m "Add curate-discover workflow adapted from explore-discovery"
```

---

### Task 2: Create curate-setup.md

Adapt init.md into a curate workflow that continues into the user's actual intent instead of ending with "now use /dewey:curate."

**Files:**
- Source (read only): `dewey/skills/init/workflows/init.md`
- Create: `dewey/skills/curate/workflows/curate-setup.md`

**Step 1: Create the workflow file**

Copy the content of `init/workflows/init.md` and modify:

1. In Step 6, replace the "suggest next steps" ending with plan-building and intent resumption. Replace:

```markdown
"Start with the first unchecked item using `/dewey:curate add <first-topic> in <first-area>`. You can also edit the 'Who You Are' section in AGENTS.md to refine the persona."
```

With:

```markdown
## Step 7: Resume user's original intent

If the user expressed a specific curation intent before setup began (e.g., "add a topic about X"), resume by routing to the appropriate curate workflow with that context. The intake classifier already identified their intent — carry it through.

If no specific intent was expressed (user just wanted to set up the KB), present the curation plan and ask: "What would you like to work on first?"
```

2. Update `<objective>` to: "Evaluate the repo, understand the user's goals, scaffold a knowledge base, build a curation plan, and resume the user's original intent."

3. Update `<required_reading>` to reference init references by full plugin path:

```markdown
<required_reading>
Load `${CLAUDE_PLUGIN_ROOT}/skills/init/references/kb-spec-summary.md` for context on the knowledge base specification.
</required_reading>
```

4. All scaffold.py calls already use `${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/scaffold.py` — verify and keep.

**Step 2: Verify the file**

Read `dewey/skills/curate/workflows/curate-setup.md` and confirm:
- No reference to `/dewey:curate add` or `/dewey:init` as next-step suggestions
- scaffold.py path uses `${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/`
- kb-spec-summary.md path uses `${CLAUDE_PLUGIN_ROOT}/skills/init/references/`
- Step 7 resumes user intent

**Step 3: Commit**

```bash
git add dewey/skills/curate/workflows/curate-setup.md
git commit -m "Add curate-setup workflow adapted from init"
```

---

### Task 3: Modify curate-add.md — strip arg parsing, add update path

**Files:**
- Modify: `dewey/skills/curate/workflows/curate-add.md`

**Step 1: Replace Step 1 (argument parsing)**

Replace the current Step 1 that parses `/dewey:curate add <topic>` syntax with:

```markdown
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
```

**Step 2: Add update-existing path after Step 2**

After Step 2 (verify domain area and create topic files), add a conditional path:

```markdown
### If mode is `update` (updating an existing topic):

1. Read the existing topic file at `docs/<area>/<slug>.md`
2. Present the current content to the user: "Here's what's currently in this topic:"
3. Ask: "What would you like to change or add?"
4. Skip to Step 3 (Research and draft) but scope the research to the specific changes requested
5. In Step 4 (Present draft), show a diff of what changed rather than the full content
```

**Step 3: Remove old argument examples**

Remove these lines from the current Step 1:

```
- `/dewey:curate add Bid Strategies` -- topic name only
- `/dewey:curate add Bid Strategies in campaign-management` -- topic name + area
- `/dewey:curate add Bid Strategies --area campaign-management --relevance supporting` -- explicit flags
```

**Step 4: Verify the file**

Read `dewey/skills/curate/workflows/curate-add.md` and confirm:
- No reference to `$ARGUMENTS` or `/dewey:curate add` syntax
- Step 1 resolves from intake context
- Update-existing path is present
- Steps 3-7 are unchanged

**Step 5: Commit**

```bash
git add dewey/skills/curate/workflows/curate-add.md
git commit -m "Strip arg parsing from curate-add, add update-existing path"
```

---

### Task 4: Modify curate-ingest.md — strip arg parsing

**Files:**
- Modify: `dewey/skills/curate/workflows/curate-ingest.md`

**Step 1: Replace Step 1 (argument parsing)**

Replace the current Step 1 that parses `/dewey:curate ingest <url>` syntax with:

```markdown
## Step 1: Resolve URL and context from intake

The intake classifier identified a URL in the user's input. Extract:

- **URL** — the URL from the user's message
- **Topic name** — if the user mentioned a topic name, use it. Otherwise, infer from the page title after fetching.
- **Relevance** — default to `core` unless the user specified otherwise

Do NOT ask the user for information that can be inferred. Get moving quickly.
```

**Step 2: Verify the file**

Read `dewey/skills/curate/workflows/curate-ingest.md` and confirm:
- No reference to `$ARGUMENTS` or `/dewey:curate ingest` syntax
- Step 1 resolves from intake context
- Steps 2-9 are unchanged

**Step 3: Commit**

```bash
git add dewey/skills/curate/workflows/curate-ingest.md
git commit -m "Strip arg parsing from curate-ingest"
```

---

### Task 5: Modify curate-propose.md — strip arg parsing

**Files:**
- Modify: `dewey/skills/curate/workflows/curate-propose.md`

**Step 1: Replace Step 1 (argument parsing)**

Replace the current Step 1 that parses `/dewey:curate propose <topic>` syntax with:

```markdown
## Step 1: Resolve proposal details from intake

The intake classifier identified a proposal intent. Extract:

- **Topic name** — from the user's free-text input
- **Relevance** — default to `core` unless specified
- **Proposed by** — default to `agent` unless specified
- **Rationale** — if not clear from context, ask the user: "Why should this topic be in the knowledge base?"
```

**Step 2: Verify the file**

Read `dewey/skills/curate/workflows/curate-propose.md` and confirm:
- No reference to `$ARGUMENTS` or `/dewey:curate propose` syntax
- Step 1 resolves from intake context
- Steps 2-5 are unchanged

**Step 3: Commit**

```bash
git add dewey/skills/curate/workflows/curate-propose.md
git commit -m "Strip arg parsing from curate-propose"
```

---

### Task 6: Rewrite curate/SKILL.md

This is the core change — replace the action menu with the free-text intent classifier.

**Files:**
- Rewrite: `dewey/skills/curate/SKILL.md`

**Step 1: Write the new SKILL.md**

The full content should be:

```markdown
---
name: curate
description: Add, update, or manage content in a knowledge base — triggered by command or natural-language curation intent like "save this to my KB"
---

<essential_principles>
## What This Skill Does

Single entry point for all knowledge base operations: discovering domains, scaffolding structure, adding topics, ingesting URLs, managing proposals, and maintaining the curation plan. Replaces the previous explore, init, and curate skills with one unified flow.

## Core Approach

1. **Understand intent** -- The user expresses what they want in natural language. Claude classifies and routes.
2. **Assess KB state** -- Is there a knowledge base? A curation plan? Existing domain areas?
3. **Route to workflow** -- Based on intent + state, route to the right workflow. No menus.

## Design Philosophy

- **Free text first** -- The user says what they want. Claude figures out how.
- **One skill, one entry point** -- No explore/init/curate distinction for the user.
- **Curation plan as prerequisite** -- Created after understanding intent, seeded with the user's goal.
- **New domains inline** -- If a topic doesn't fit, offer to create the area on the spot.
- **Collaborative curation** -- Both humans and agents can propose, review, and add content.
- **Source primacy** -- Every topic should trace back to authoritative sources.

## Key Variables

- `$ARGUMENTS` -- Optional free-text context passed to this skill
- `${CLAUDE_PLUGIN_ROOT}` -- Root directory of the Dewey plugin
</essential_principles>

<intake>
This skill activates on `/dewey:curate` or when the user expresses curation intent in conversation: "add this to the KB", "capture this as a topic", "save this to my knowledge base", "let's put this in the knowledge base", "I want to add a new domain area", or similar phrases.

## Step 1: Gather intent

If the user provided clear intent (via arguments, conversational context, or a natural-language trigger), use it directly. Do not re-ask.

If the user invoked `/dewey:curate` with no arguments and no prior conversational context, ask one open-ended question:

> "What would you like to add or change in your knowledge base?"

## Step 2: Assess knowledge base state

Check for:
1. Does a knowledge base exist? (Look for AGENTS.md and a knowledge base directory configured in `.dewey/config.json`, defaulting to `docs/`)
2. Does `.dewey/curation-plan.md` exist?
3. What domain areas exist?

## Step 3: Route based on state + intent

### No knowledge base exists

- **Vague or exploratory intent** ("help me set up", "I don't know where to start", no specific topic) → Route to `workflows/curate-discover.md`
- **Clear intent with goals** ("I want a KB for marketing analytics", "build a knowledge base for my team") → Route to `workflows/curate-setup.md`
- **Very specific intent** ("add a topic about bid strategies") → Route to `workflows/curate-setup.md` with a note to resume into the specific curation action after scaffolding

### Knowledge base exists, no curation plan

Before routing to any workflow, build the curation plan:

1. Read AGENTS.md to understand the role and domain areas
2. Read the knowledge base directory structure to see what topics exist
3. Tell the user: "Before we proceed, let me build a curation plan so we have a map of what's covered."
4. Propose 2-4 starter topics per domain area. Seed with the user's stated intent as the first item if it maps to a specific topic.
5. Ask the user to confirm or adjust
6. Write `.dewey/curation-plan.md`
7. Then resume routing based on the user's original intent

### Knowledge base exists, plan exists

Classify the user's intent and route:

| Intent | Signal patterns | Routes to |
|--------|----------------|-----------|
| **New topic** | Topic name, "add X", "capture Y", "I learned about Z" — no URL | `workflows/curate-add.md` |
| **Ingest URL** | Message contains a URL | `workflows/curate-ingest.md` |
| **Propose for review** | "propose", "submit for review", "not sure if this fits" | `workflows/curate-propose.md` |
| **Promote proposal** | "promote", "move proposal", "approve", references _proposals/ | `workflows/curate-promote.md` |
| **Manage plan** | "what's planned", "show the plan", "add to plan", "remove from plan" | `workflows/curate-plan.md` |
| **Update existing** | "update X", "revise", "add to the existing topic about Y" | `workflows/curate-add.md` with mode=update |
| **Add domain area** | "new area", "add a domain", "create an area for X" | `workflows/curate-setup.md` (re-init path for adding areas) |

If intent is ambiguous, ask **one** clarifying question — not a menu of options.

### New domain area needed

During classification, if the user's topic doesn't fit any existing domain area:

1. Tell the user: "This doesn't fit your existing areas ([list areas]). Want me to create a new domain area for it?"
2. If yes: route to `workflows/curate-setup.md` (which handles adding areas to an existing KB via its re-init path), then resume into the original curation action
3. If no: ask where they'd like to put it, or whether to skip
</intake>

<workflows_index>
## Available Workflows

All workflows in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| curate-discover.md | Guided conversation to discover role, domains, scaffold KB, and build curation plan |
| curate-setup.md | Evaluate repo, scaffold KB structure (or add areas to existing KB), build plan |
| curate-add.md | Create a new topic or update an existing one in a domain area |
| curate-propose.md | Submit a topic proposal for review |
| curate-promote.md | Promote a validated proposal into a domain area |
| curate-ingest.md | Ingest an external URL — evaluate against KB, then propose or update |
| curate-plan.md | View, add to, or remove items from the curation plan |
</workflows_index>

<scripts_integration>
## Python Helper Scripts

**Curate scripts** in `scripts/`:

**create_topic.py** -- Create topic files in a domain area
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/curate/scripts/create_topic.py --kb-root <root> --area <area> --topic "<name>" --relevance "<relevance>"
```

**propose.py** -- Create a proposal file
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/curate/scripts/propose.py --kb-root <root> --topic "<name>" --relevance "<relevance>" --proposed-by "<who>" --rationale "<why>"
```

**promote.py** -- Move a proposal into a domain area
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/curate/scripts/promote.py --kb-root <root> --proposal "<slug>" --target-area "<area>"
```

**Init scripts** (shared infrastructure) in `${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/`:

**scaffold.py** -- Create or extend KB directory structure
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/init/scripts/scaffold.py --target <dir> --role "<persona>" --areas "<area1>,<area2>"
```

**config.py** -- Read knowledge base configuration
- `read_knowledge_dir(kb_root)` returns the configured knowledge directory (default: `docs`)
</scripts_integration>

<success_criteria>
Curation is successful when:

- Content follows the topic template structure
- Sources are referenced in frontmatter and cited inline
- Frontmatter is complete with title, relevance, and date
- Template sections are filled in (Why This Matters, In Practice, Key Guidance, Watch Out For, Go Deeper)
- AGENTS.md has linked table rows (`[Topic](<knowledge-dir>/<area>/<slug>.md)`) for each topic
- overview.md "How It's Organized" has linked table rows for each topic in the area
- overview.md "Key Sources" is populated with actual sources
- CLAUDE.md Domain Areas table lists the area
</success_criteria>
```

**Step 2: Verify the file**

Read `dewey/skills/curate/SKILL.md` and confirm:
- YAML frontmatter has updated description mentioning natural-language triggers
- No reference to `add`/`propose`/`promote`/`ingest`/`plan` as sub-commands or explicit arguments
- Intake starts with "gather intent" (free text), then "assess KB state", then "route"
- All 7 workflows listed in workflows_index
- Scripts integration references both curate/scripts/ and init/scripts/
- No `<routing>` section with argument-based routing

**Step 3: Commit**

```bash
git add dewey/skills/curate/SKILL.md
git commit -m "Rewrite curate SKILL.md with free-text intake and consolidated routing"
```

---

### Task 7: Delete explore skill entry point

**Files:**
- Delete: `dewey/skills/explore/SKILL.md`
- Delete: `dewey/skills/explore/workflows/explore-discovery.md`

**Step 1: Delete the files**

```bash
rm dewey/skills/explore/SKILL.md
rm dewey/skills/explore/workflows/explore-discovery.md
rmdir dewey/skills/explore/workflows
rmdir dewey/skills/explore
```

**Step 2: Verify**

```bash
ls dewey/skills/explore 2>&1
```

Expected: "No such file or directory"

**Step 3: Commit**

```bash
git add -u dewey/skills/explore/
git commit -m "Remove explore skill — consolidated into curate"
```

---

### Task 8: Delete init skill entry point

Only delete the SKILL.md and workflow. Keep scripts/ and references/ — they're shared infrastructure.

**Files:**
- Delete: `dewey/skills/init/SKILL.md`
- Delete: `dewey/skills/init/workflows/init.md`

**Step 1: Delete the files**

```bash
rm dewey/skills/init/SKILL.md
rm dewey/skills/init/workflows/init.md
rmdir dewey/skills/init/workflows
```

**Step 2: Verify scripts and references are still there**

```bash
ls dewey/skills/init/scripts/
ls dewey/skills/init/references/
```

Expected: scaffold.py, templates.py, config.py in scripts/; kb-spec-summary.md in references/

**Step 3: Commit**

```bash
git add -u dewey/skills/init/SKILL.md dewey/skills/init/workflows/init.md
git commit -m "Remove init skill entry point — consolidated into curate, scripts kept as shared infra"
```

---

### Task 9: Update plugin.json description

**Files:**
- Modify: `dewey/.claude-plugin/plugin.json`

**Step 1: Update the description**

Change the description field from:

```json
"description": "Knowledge base management plugin for Claude Code - scaffold, curate, validate, and explore structured knowledge bases"
```

To:

```json
"description": "Knowledge base management plugin for Claude Code — curate and validate structured knowledge bases"
```

**Step 2: Verify**

Read `dewey/.claude-plugin/plugin.json` and confirm the description is updated.

**Step 3: Commit**

```bash
git add dewey/.claude-plugin/plugin.json
git commit -m "Update plugin description to reflect consolidated skill surface"
```

---

### Task 10: End-to-end verification

**Step 1: Verify skill discovery**

```bash
ls dewey/skills/*/SKILL.md
```

Expected: only `curate/SKILL.md` and `health/SKILL.md`

**Step 2: Verify all workflow files exist**

```bash
ls dewey/skills/curate/workflows/
```

Expected: curate-add.md, curate-discover.md, curate-ingest.md, curate-plan.md, curate-promote.md, curate-propose.md, curate-setup.md

**Step 3: Verify init infrastructure intact**

```bash
ls dewey/skills/init/scripts/ dewey/skills/init/references/
```

Expected: config.py, scaffold.py, templates.py in scripts/; kb-spec-summary.md in references/

**Step 4: Verify no dangling references**

Search all remaining skill and workflow files for references to deleted skills:

```bash
grep -r "/dewey:init\|/dewey:explore" dewey/skills/curate/ dewey/skills/health/
```

Expected: no matches. If any found, update them.

**Step 5: Run existing tests to confirm nothing broke**

```bash
python3 -m pytest tests/ -v -k "not test_scaffold_sandbox"
```

Expected: all tests pass (scripts are unchanged)

**Step 6: Commit any fixes from verification**

If Step 4 found dangling references, fix and commit:

```bash
git add -u
git commit -m "Fix dangling references to removed explore/init skills"
```
