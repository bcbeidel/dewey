---
paths:
  - "tests/**/*.py"
---
# Test Conventions

- Framework: `unittest.TestCase`
- setUp: `self.tmpdir = Path(tempfile.mkdtemp())`
- tearDown: `shutil.rmtree(self.tmpdir)`
- Use module-level `_write(path, text)` helper for creating test files (creates parents, returns path)
- Direct module imports: `from validators import check_frontmatter` -- `conftest.py` adds all scripts dirs to `sys.path`
- Location mirrors source: `tests/skills/<skill>/` corresponds to `dewey/skills/<skill>/scripts/`
- Never write to the actual project directory -- always use `self.tmpdir`
- For the canonical test pattern, see `tests/skills/health/test_validators.py`
