<objective>
View, add to, or remove items from the curation plan -- the persistent record of topics this knowledge base intends to cover.
</objective>

<process>
## Step 1: Parse arguments and determine action

Parse `$ARGUMENTS` after `plan`. Valid invocations:

- `/dewey:curate plan` -- view the current plan with progress summary
- `/dewey:curate plan add Session State in streamlit-patterns` -- add an item to an area
- `/dewey:curate plan add Session State in streamlit-patterns --relevance core --rationale "managing state across reruns"` -- add with metadata
- `/dewey:curate plan remove Session State` -- remove an item by name

**Actions:**
- No sub-arguments or `view` -> **View** (show plan + progress)
- `add <topic> in <area>` -> **Add** (append item to area)
- `remove <topic>` -> **Remove** (delete item from plan)

## Step 2: Locate or create the plan file

Look for `.dewey/curation-plan.md` in the knowledge base root.

**If the file does not exist** and the action is **view**:
- Inform the user: "No curation plan found. Tell me what you'd like to add, and I'll build a plan as part of the process."

**If the file does not exist** and the action is **add**:
- Create the file with frontmatter (`last_updated: <today>`) and the standard header before adding the item.

## Step 3: Execute the action

### View

1. Read `.dewey/curation-plan.md`
2. Count total items, completed items (`[x]`), and pending items (`[ ]`)
3. Present the plan to the user with a progress summary:

```
Curation Plan: X of Y topics completed (Z remaining)

<full plan content>
```

### Add

Parse the topic name, area slug, relevance (default: `core`), and rationale from arguments.

1. Read `.dewey/curation-plan.md`
2. Find the `## <area-slug>` section. If it does not exist, append a new section.
3. Append the new item: `- [ ] Topic Name -- relevance -- rationale`
4. Update `last_updated` in the frontmatter to today's date
5. Write the updated file
6. Confirm: "Added 'Topic Name' to the curation plan under `<area-slug>`."

### Remove

Parse the topic name from arguments.

1. Read `.dewey/curation-plan.md`
2. Search for a line matching `- [ ] <topic>` or `- [x] <topic>` (case-insensitive match on the topic name portion before ` -- `)
3. If not found, inform the user: "No item matching '<topic>' found in the curation plan."
4. If found, remove the line. If the area section is now empty (no items under the heading), remove the section heading and blank lines too.
5. Update `last_updated` in the frontmatter to today's date
6. Write the updated file
7. Confirm: "Removed 'Topic Name' from the curation plan."
</process>

<success_criteria>
- View: plan displayed with accurate progress counts
- Add: new item appended under the correct area section, last_updated refreshed
- Remove: matching item deleted, last_updated refreshed
- File created automatically on first add if it doesn't exist
</success_criteria>
