"""Topic reference tracking.

Records when KB files are referenced to ``.dewey/utilization/log.jsonl``
inside the KB root.  This data feeds into utilization-aware health scoring
and curation recommendations.

Only stdlib is used.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


_LOG_DIR = Path(".dewey") / "utilization"
_LOG_FILE = "log.jsonl"


def record_reference(
    kb_root: Path,
    file_path: str,
    context: str = "user",
) -> Path:
    """Append a reference entry to the utilization log.

    Parameters
    ----------
    kb_root:
        Root directory of the knowledge base (the log is written
        inside ``kb_root/.dewey/utilization/``).
    file_path:
        Relative path (from *kb_root*) of the referenced file,
        e.g. ``"topic/foo.md"``.
    context:
        Free-form label describing *how* the file was referenced.
        Defaults to ``"user"``.

    Returns
    -------
    Path
        Absolute path to the log file.
    """
    log_dir = kb_root / _LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / _LOG_FILE

    entry = {
        "file": file_path,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "context": context,
    }

    with log_path.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")

    return log_path
