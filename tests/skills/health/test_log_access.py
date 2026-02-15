"""Tests for skills.health.scripts.log_access — hook-driven utilization logging."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from log_access import log_if_knowledge_file


class TestLogIfKnowledgeFile(unittest.TestCase):
    """Tests for log_if_knowledge_file."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.kb_dir = self.tmpdir / "docs"
        self.kb_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_logs_file_under_knowledge_dir(self):
        """A file under the knowledge directory should be logged."""
        topic = self.kb_dir / "area" / "topic.md"
        topic.parent.mkdir(parents=True)
        topic.write_text("content")
        logged = log_if_knowledge_file(self.tmpdir, str(topic))
        self.assertTrue(logged)
        log = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        self.assertTrue(log.exists())
        entry = json.loads(log.read_text().strip())
        self.assertIn("docs/area/topic.md", entry["file"])

    def test_ignores_file_outside_knowledge_dir(self):
        """A file outside the knowledge directory should not be logged."""
        other = self.tmpdir / "README.md"
        other.write_text("content")
        logged = log_if_knowledge_file(self.tmpdir, str(other))
        self.assertFalse(logged)
        log = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        self.assertFalse(log.exists())

    def test_ignores_proposals(self):
        """Files under _proposals/ should not be logged."""
        proposal = self.kb_dir / "_proposals" / "draft.md"
        proposal.parent.mkdir(parents=True)
        proposal.write_text("content")
        logged = log_if_knowledge_file(self.tmpdir, str(proposal))
        self.assertFalse(logged)

    def test_ignores_non_md_files(self):
        """Non-markdown files should not be logged."""
        img = self.kb_dir / "area" / "diagram.png"
        img.parent.mkdir(parents=True)
        img.write_text("binary")
        logged = log_if_knowledge_file(self.tmpdir, str(img))
        self.assertFalse(logged)

    def test_context_is_hook(self):
        """Context should be 'hook' for auto-captured access."""
        topic = self.kb_dir / "area" / "topic.md"
        topic.parent.mkdir(parents=True)
        topic.write_text("content")
        log_if_knowledge_file(self.tmpdir, str(topic))
        log = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        entry = json.loads(log.read_text().strip())
        self.assertEqual(entry["context"], "hook")

    def test_stores_relative_path(self):
        """Logged file path should be relative to kb_root, not absolute."""
        topic = self.kb_dir / "area" / "topic.md"
        topic.parent.mkdir(parents=True)
        topic.write_text("content")
        log_if_knowledge_file(self.tmpdir, str(topic))
        log = self.tmpdir / ".dewey" / "utilization" / "log.jsonl"
        entry = json.loads(log.read_text().strip())
        self.assertFalse(entry["file"].startswith("/"))

    def test_custom_knowledge_dir(self):
        """Should respect custom knowledge_dir from .dewey/config.json."""
        config_dir = self.tmpdir / ".dewey"
        config_dir.mkdir(parents=True)
        (config_dir / "config.json").write_text('{"knowledge_dir": "knowledge"}')
        knowledge = self.tmpdir / "knowledge"
        knowledge.mkdir()
        topic = knowledge / "area" / "topic.md"
        topic.parent.mkdir(parents=True)
        topic.write_text("content")
        logged = log_if_knowledge_file(self.tmpdir, str(topic))
        self.assertTrue(logged)

    def test_nonexistent_file_no_error(self):
        """A nonexistent file path should return False without error."""
        logged = log_if_knowledge_file(self.tmpdir, "/nonexistent/path.md")
        self.assertFalse(logged)


if __name__ == "__main__":
    unittest.main()
