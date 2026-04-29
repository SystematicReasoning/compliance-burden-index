"""Repo-level metadata: version string and snapshot date.

Version is loaded from the VERSION file at the repo root.
Snapshot date is loaded from model/snapshot.yaml.

Both are loaded once and cached. Scripts that emit results MUST use these
loaders rather than hard-coding values or calling date.today().
"""

from datetime import date
from pathlib import Path
from typing import Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

_version_cache: Optional[str] = None
_snapshot_cache: Optional[date] = None


def get_version() -> str:
    """Return the methodology version string from /VERSION."""
    global _version_cache
    if _version_cache is None:
        path = REPO_ROOT / "VERSION"
        _version_cache = path.read_text().strip()
    return _version_cache


def get_snapshot_date() -> date:
    """Return the snapshot date from model/snapshot.yaml.

    Snapshot date is the canonical date of the latest measurement update;
    it does NOT change with date.today(). Scripts should use this instead
    of date.today() so that the same commit produces identical outputs
    regardless of when it is run.
    """
    global _snapshot_cache
    if _snapshot_cache is None:
        path = REPO_ROOT / "model" / "snapshot.yaml"
        with open(path) as f:
            cfg = yaml.safe_load(f)
        d = cfg["snapshot_date"]
        _snapshot_cache = d if isinstance(d, date) else date.fromisoformat(d)
    return _snapshot_cache
