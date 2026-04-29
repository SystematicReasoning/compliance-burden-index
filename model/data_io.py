"""Data loading utilities for corpus, version, and observed-window inputs."""

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


@dataclass
class CorpusVersion:
    version: str
    date: date
    rfc2119_keywords: int
    word_count: int
    measurement_status: str


@dataclass
class ObservedWindow:
    window_id: str
    window_start: date
    window_end: date
    start_version: str
    end_version: str
    version_count: int
    added: int
    removed: int
    modified: int
    total_changes: int
    provenance: str
    extraction_method: str

    @property
    def days(self) -> int:
        return (self.window_end - self.window_start).days

    @property
    def annualized_versions(self) -> float:
        return self.version_count * 365.0 / self.days

    @property
    def annualized_changes(self) -> float:
        return self.total_changes * 365.0 / self.days


def load_corpus_versions(path: Optional[Path] = None) -> List[CorpusVersion]:
    if path is None:
        path = DATA_DIR / "cabf_tls_br_corpus.csv"
    rows = []
    with open(path) as f:
        for row in csv.DictReader(f):
            rows.append(CorpusVersion(
                version=row["version"],
                date=date.fromisoformat(row["date"]),
                rfc2119_keywords=int(row["rfc2119_keywords"]),
                word_count=int(row["word_count"]),
                measurement_status=row["measurement_status"],
            ))
    rows.sort(key=lambda r: r.date)
    return rows


def load_observed_window(window_id: str = "observed_2025_2026", path: Optional[Path] = None) -> ObservedWindow:
    if path is None:
        path = DATA_DIR / "cabf_tls_br_observed_window.csv"
    with open(path) as f:
        for row in csv.DictReader(f):
            if row["window_id"] == window_id:
                return ObservedWindow(
                    window_id=row["window_id"],
                    window_start=date.fromisoformat(row["window_start"]),
                    window_end=date.fromisoformat(row["window_end"]),
                    start_version=row["start_version"],
                    end_version=row["end_version"],
                    version_count=int(row["version_count"]),
                    added=int(row["added"]),
                    removed=int(row["removed"]),
                    modified=int(row["modified"]),
                    total_changes=int(row["total_changes"]),
                    provenance=row["provenance"],
                    extraction_method=row["extraction_method"],
                )
    raise ValueError(f"Window not found: {window_id}")
