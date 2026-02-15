"""Health score history tracking.

Persists timestamped snapshots of Tier 1 (and optionally Tier 2) health
summaries to ``.dewey/history/health-log.jsonl`` inside the KB root.

Only stdlib is used.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


_LOG_DIR = Path(".dewey") / "history"
_LOG_FILE = "health-log.jsonl"


def record_snapshot(
    kb_root: Path,
    tier1_summary: dict,
    tier2_summary: Optional[dict] = None,
) -> Path:
    """Append a timestamped health snapshot to the log file.

    Parameters
    ----------
    kb_root:
        Root directory of the knowledge base (the log is written
        inside ``kb_root/.dewey/history/``).
    tier1_summary:
        Summary dict from ``run_health_check``.
    tier2_summary:
        Optional summary dict from ``run_tier2_prescreening``.

    Returns
    -------
    Path
        Absolute path to the log file.
    """
    log_dir = kb_root / _LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / _LOG_FILE

    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tier1": tier1_summary,
        "tier2": tier2_summary,
    }

    with log_path.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")

    return log_path
