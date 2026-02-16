---
paths:
  - "dewey/**/*.py"
  - "tests/**/*.py"
---
# Python Conventions

- Python 3.9+ stdlib only -- zero external dependencies
- Use `from __future__ import annotations` at the top of every file for union syntax (`str | None`) in type annotations
- Use `Optional[str]` in runtime expressions and function parameter defaults (Python 3.9 compat)
- Scripts live in `skills/<skill>/scripts/` and import each other directly (no package `__init__.py`)
- Cross-skill imports: add sibling scripts dirs to `sys.path` with idempotency check (see `check_kb.py` for pattern)
- Docstrings use NumPy/SciPy style (`Parameters\n----------`), not Google style
- Module-private helpers use `_underscore_prefix`; public constants use `UPPERCASE`
- CLI scripts use `if __name__ == "__main__"` with argparse, `--kebab-case` args, output to stdout via `print()`
- Persistence uses JSONL append-only logs (`json.dumps(entry) + "\n"`)
- For the canonical script pattern, see `validators.py`
