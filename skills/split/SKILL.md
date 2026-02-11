---
description: Intelligently split large files using LLM analysis to maintain semantic coherence
allowed-tools: Bash(python *)
---

# Split Large Files

Intelligently split large context files (>500 lines) into a scannable main file and topically organized reference files, following Anthropic's best practices for context organization.

## How to Use

```
/dewey:split file.md
/dewey:split file.md --dry-run
```

## What It Does

This command uses the current Claude Code session to:

1. **Analyze** the file content semantically
2. **Identify** the overarching theme and determine semantic folder name
3. **Organize** content into topically focused files
4. **Create** a folder at the same hierarchy level with semantic name
5. **Generate** `main.md` with overview and navigation
6. **Create** supporting files with semantic names for each topic
7. **Maintain** all information with clear bidirectional links
8. **Backup** the original file to `.dewey/backups/` and remove it

## Arguments

The command accepts a file path and optional flags:

- `file.md` - Path to the file to split
- `--dry-run` - Preview what would be created without writing files
- `--max-lines N` - Custom threshold (default: 500)
- `--target-lines N` - Target main file size (default: 150)

**Note**: `$ARGUMENTS` in this command will be the file path and any flags provided.

## What You Get

### Example 1: Recipe Collection

**Before:**
```
/context/recipes.md (850 lines covering Italian, French, and Asian recipes)
```

**After:**
```
/context/cooking/
  ├── main.md (~150 lines)
  │   - Overview of recipe collection
  │   - Navigation to specific cuisines
  │   - Cooking tips and guidelines
  ├── italian-pasta.md
  ├── french-desserts.md
  └── asian-stir-fry.md

Backup: .dewey/backups/recipes_20260210.md
Original: recipes.md (removed after successful split)
```

### Example 2: Implementation Plan

**Before:**
```
/context/IMPLEMENTATION_PLAN.md (973 lines covering multiple project phases)
```

**After:**
```
/context/project-phases/
  ├── main.md (~200 lines)
  │   - Project overview
  │   - Key principles
  │   - Phase navigation
  ├── phase-1-measurement.md
  ├── phase-2-3-optimization.md
  └── testing-completion.md

Backup: .dewey/backups/IMPLEMENTATION_PLAN_20260210.md
Original: IMPLEMENTATION_PLAN.md (removed after successful split)
```

**Key points:**
- Folder name reflects content theme (not old filename)
- Main file is always `main.md`
- Supporting files have semantic names
- Everything stays at same hierarchy level
- Original file backed up then removed

## Implementation

Use the Python helper functions to implement this command:

```python
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path("${CLAUDE_PLUGIN_ROOT}/skills/split/scripts")
sys.path.insert(0, str(scripts_dir))

from skill_splitter import skill_based_split, implement_refactor_plan

# Parse arguments
args = "$ARGUMENTS".split()
file_path = Path(args[0]) if args else None
dry_run = "--dry-run" in "$ARGUMENTS"

if not file_path:
    print("Error: Please provide a file path")
    sys.exit(1)

# Generate analysis prompt
request, prompt = skill_based_split(
    file_path,
    max_lines=500,
    target_main_lines=150,
    dry_run=dry_run
)

# Display file info
print(f"File: {request.file_path}")
print(f"Current lines: {request.total_lines}")
print(f"Target main lines: {request.target_main_lines}")
print(f"\n{prompt}")
```

## Analysis Task

When invoked, I (Claude) will analyze the file content and provide a refactoring plan in JSON format:

```json
{
  "folder_name": "semantic-theme-name",
  "main_content": "Refactored main.md with overview and navigation",
  "detail_files": [
    {
      "name": "descriptive-kebab-case-name",
      "content": "Full content for this detail file"
    }
  ],
  "summary": "Brief description of organizational strategy",
  "reasoning": "Explanation of why content was grouped this way and folder naming choice"
}
```

**Important:**
- `folder_name`: Must describe the CONTENT THEME (e.g., "software-development", "cooking-techniques")
- DO NOT use generic terms like "references", "docs", "files", or "content" in folder_name
- Use lowercase with hyphens (kebab-case)
- Example: "cooking" not "recipes", "project-phases" not "IMPLEMENTATION_PLAN"
- Main content will be saved as `main.md` in the folder
- Detail files are topical supporting files in the same folder

After providing the plan, I will use `implement_refactor_plan()` to write the files unless `--dry-run` is specified.

## Best Practices Applied

- **Scannable main files**: Overview + key concepts + navigation
- **Topical organization**: Related content grouped logically
- **Semantic coherence**: No mid-section cuts
- **Information preservation**: All content retained
- **Clear navigation**: Bidirectional links between files

## Integration

Works seamlessly with:
- `/dewey:analyze` - Identifies files that need splitting
- Other optimization commands (to be implemented)

---

**Process the arguments**: $ARGUMENTS
