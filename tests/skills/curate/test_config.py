"""Tests for skills.init.scripts.config — Dewey configuration read/write."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from config import read_knowledge_dir, write_config


class TestReadKnowledgeDir(unittest.TestCase):
    """Tests for read_knowledge_dir."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_returns_docs_when_no_config(self):
        """Default to 'docs' when no config file exists."""
        self.assertEqual(read_knowledge_dir(self.tmpdir), "docs")

    def test_reads_configured_value(self):
        """Return the configured knowledge_dir value."""
        config_dir = self.tmpdir / ".dewey"
        config_dir.mkdir(parents=True)
        (config_dir / "config.json").write_text(
            json.dumps({"knowledge_dir": "knowledge"})
        )
        self.assertEqual(read_knowledge_dir(self.tmpdir), "knowledge")

    def test_returns_docs_on_invalid_json(self):
        """Default to 'docs' when config.json contains invalid JSON."""
        config_dir = self.tmpdir / ".dewey"
        config_dir.mkdir(parents=True)
        (config_dir / "config.json").write_text("not json")
        self.assertEqual(read_knowledge_dir(self.tmpdir), "docs")

    def test_returns_docs_when_key_missing(self):
        """Default to 'docs' when knowledge_dir key is absent."""
        config_dir = self.tmpdir / ".dewey"
        config_dir.mkdir(parents=True)
        (config_dir / "config.json").write_text(json.dumps({"other": "value"}))
        self.assertEqual(read_knowledge_dir(self.tmpdir), "docs")

    def test_strips_trailing_slash_on_read(self):
        """Trailing slash in stored value is stripped on read."""
        config_dir = self.tmpdir / ".dewey"
        config_dir.mkdir(parents=True)
        (config_dir / "config.json").write_text(
            json.dumps({"knowledge_dir": "docs/"})
        )
        self.assertEqual(read_knowledge_dir(self.tmpdir), "docs")


class TestWriteConfig(unittest.TestCase):
    """Tests for write_config."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_creates_config_file(self):
        """write_config creates .dewey/config.json."""
        path = write_config(self.tmpdir, "docs")
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        self.assertEqual(data["knowledge_dir"], "docs")

    def test_creates_dewey_directory(self):
        """write_config creates .dewey/ if it doesn't exist."""
        write_config(self.tmpdir, "knowledge")
        self.assertTrue((self.tmpdir / ".dewey").is_dir())

    def test_custom_knowledge_dir(self):
        """write_config stores a custom directory name."""
        write_config(self.tmpdir, "kb")
        data = json.loads((self.tmpdir / ".dewey" / "config.json").read_text())
        self.assertEqual(data["knowledge_dir"], "kb")

    def test_roundtrip(self):
        """write_config output is readable by read_knowledge_dir."""
        write_config(self.tmpdir, "my-docs")
        self.assertEqual(read_knowledge_dir(self.tmpdir), "my-docs")

    def test_strips_trailing_slash_on_write(self):
        """Trailing slash is stripped before writing to config."""
        write_config(self.tmpdir, "docs/")
        data = json.loads((self.tmpdir / ".dewey" / "config.json").read_text())
        self.assertEqual(data["knowledge_dir"], "docs")


if __name__ == "__main__":
    unittest.main()
