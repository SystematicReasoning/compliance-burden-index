"""Tests for the Knowledge Currency Budget model.

Run with: pytest tests/
"""

import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from model.budget import (
    Parameters,
    compute_team_budget,
    re_read_passes_per_year,
)
from model.data_io import load_corpus_versions, load_observed_window

PARAMS_PATH = REPO_ROOT / "model" / "parameters.yaml"


def test_re_read_passes_basic():
    """Re-read passes per year should be derived deterministically."""
    # tau=120 days, threshold=0.7: max interval = -120 * ln(0.7) = 42.8 days
    # passes = ceil(365 / 42.8) = 9
    assert re_read_passes_per_year(120, 0.70) == 9
    # tau=60, threshold=0.85: max interval = -60 * ln(0.85) = 9.75 days, passes = 38
    assert re_read_passes_per_year(60, 0.85) == 38
    # tau=180, threshold=0.50: max interval = -180 * ln(0.50) = 124.8 days, passes = 3
    assert re_read_passes_per_year(180, 0.50) == 3


def test_re_read_passes_floor():
    """Passes must have a floor of 1 even at degenerate inputs."""
    assert re_read_passes_per_year(1000, 0.99) >= 1
    assert re_read_passes_per_year(120, 1.0) == 1  # ln(1) = 0, returns 1 by floor


def test_observed_window_loads_from_csv():
    """The 139-change figure must be loaded from the CSV, not hard-coded."""
    window = load_observed_window()
    assert window.total_changes == 139
    assert window.added == 32
    assert window.removed == 34
    assert window.modified == 73
    assert window.version_count == 10
    assert window.start_version == "v2.1.7"
    assert window.end_version == "v2.2.6"
    # Aggregates must sum
    assert window.added + window.removed + window.modified == window.total_changes


def test_corpus_versions_loaded():
    """Corpus versions must be loaded from CSV with measurement_status."""
    versions = load_corpus_versions()
    assert len(versions) == 13
    assert versions[0].version == "v1.0"
    assert versions[-1].version == "v2.2.1"
    assert versions[-1].word_count == 71500
    assert versions[-1].rfc2119_keywords == 1177
    # All should have a documented measurement status. v0.3 relabeled this from
    # "measured" to "extracted_from_tracking_system" pending direct PDF re-extraction.
    valid_statuses = {"measured", "extracted_from_tracking_system", "extrapolated"}
    for v in versions:
        assert v.measurement_status in valid_statuses, (
            f"Unknown measurement status: {v.measurement_status}"
        )


def test_central_team_budget_dimensional_correctness():
    """Verify the budget has correct units (hours/year, not minutes)."""
    versions = load_corpus_versions()
    window = load_observed_window()
    params = Parameters.from_yaml(PARAMS_PATH, scenario="central")
    team = compute_team_budget(
        word_count=versions[-1].word_count,
        versions_per_year=window.annualized_versions,
        changes_per_year=window.annualized_changes,
        params=params,
    )
    # The CPS owner persona (corpus_depth=1.0, change_responsibility=1.0,
    # requires_version_diff_review=true) should be the highest-burden persona
    cps = next(p for p in team.personas if p.persona_id == "cps_owner")
    # Sanity: positive, finite, less than nominal year hours
    assert 100 < cps.total_hours < 2080
    # Reading rate is 238 wpm = 14280 wph. Full corpus 71500 words at 9 passes
    # = 9 * 71500 / 14280 = 45.05 hours. CPS has corpus_depth=1.0.
    assert math.isclose(cps.baseline_hours, 9 * 71500 / 14280, rel_tol=0.01)


def test_scenario_envelope_ordering():
    """Low scenario must produce smaller budget than central, central < high."""
    versions = load_corpus_versions()
    window = load_observed_window()

    def team_total(scenario):
        params = Parameters.from_yaml(PARAMS_PATH, scenario=scenario)
        team = compute_team_budget(
            word_count=versions[-1].word_count,
            versions_per_year=window.annualized_versions,
            changes_per_year=window.annualized_changes,
            params=params,
        )
        return team.total_hours

    low = team_total("low")
    central = team_total("central")
    high = team_total("high")
    assert low < central < high


def test_capacity_ratio_meaningful():
    """Capacity ratio should be a finite positive number under realistic params."""
    versions = load_corpus_versions()
    window = load_observed_window()
    params = Parameters.from_yaml(PARAMS_PATH, scenario="central")
    team = compute_team_budget(
        word_count=versions[-1].word_count,
        versions_per_year=window.annualized_versions,
        changes_per_year=window.annualized_changes,
        params=params,
    )
    assert 0 < team.aggregate_capacity_ratio < 100
    assert team.total_capacity > 0
    assert team.total_hours > 0


def test_persona_corpus_depth_scales_baseline():
    """A persona with corpus_depth=0.5 should have half the baseline of depth=1.0."""
    versions = load_corpus_versions()
    window = load_observed_window()
    params = Parameters.from_yaml(PARAMS_PATH, scenario="central")
    team = compute_team_budget(
        word_count=versions[-1].word_count,
        versions_per_year=window.annualized_versions,
        changes_per_year=window.annualized_changes,
        params=params,
    )
    cps = next(p for p in team.personas if p.persona_id == "cps_owner")
    # Find a persona with depth 0.5 or close
    # validation_lead has depth 0.4
    val_lead = next(p for p in team.personas if p.persona_id == "validation_lead")
    # baseline ratio should equal corpus_depth ratio
    assert math.isclose(
        val_lead.baseline_hours / cps.baseline_hours,
        val_lead.corpus_depth / cps.corpus_depth,
        rel_tol=0.01,
    )


def test_no_hardcoded_observed_total_changes():
    """Confirm that scripts do not embed the OBSERVED_TOTAL_CHANGES constant.

    This test guards against regression to the v0.1 pattern where the script
    hard-coded the 139-change figure rather than loading from CSV.
    """
    script_path = REPO_ROOT / "scripts" / "compute_headline.py"
    text = script_path.read_text()
    forbidden = ["OBSERVED_TOTAL_CHANGES = 139", "OBSERVED_VERSION_COUNT = 10"]
    for f in forbidden:
        assert f not in text, f"Forbidden hardcoded constant present: {f}"


def test_regime_stack_state_csv_loads():
    """Multi-regime tracking state must be present and parseable."""
    import csv as _csv
    path = REPO_ROOT / "data" / "regime_stack_state.csv"
    assert path.exists(), "regime_stack_state.csv missing"
    with open(path) as f:
        rows = list(_csv.DictReader(f))
    regime_ids = {r["regime_id"] for r in rows}
    # At minimum the regimes named in §9 must appear in the tracking state.
    # Registry uses *_root_program_policy convention for browser/OS programs.
    assert "cabf_tls_br" in regime_ids
    mozilla_present = (
        "mozilla_root_program_policy" in regime_ids
        or "mozilla_root_store_policy" in regime_ids
    )
    assert mozilla_present, f"Mozilla policy missing; got: {regime_ids}"
    assert "chrome_root_program_policy" in regime_ids


def test_mozilla_cadence_consistent_with_methodology():
    """Mozilla cadence (1.30 versions/yr) must match the value cited in §9.1."""
    from datetime import date as _date
    import csv as _csv
    path = REPO_ROOT / "data" / "mozilla_root_store_policy_versions.csv"
    with open(path) as f:
        rows = [r for r in _csv.DictReader(f) if r["date"]]
    dates = sorted(_date.fromisoformat(r["date"]) for r in rows)
    span = (dates[-1] - dates[0]).days
    cadence = len(dates) * 365.0 / span
    assert math.isclose(cadence, 1.30, abs_tol=0.05), (
        f"Mozilla cadence drifted from methodology: {cadence:.2f} vs 1.30"
    )


def test_cabf_stack_observed_windows_present():
    """All five CABF regimes must have observed-window CSVs with required fields."""
    expected = [
        "cabf_tls_br_observed_window.csv",
        "cabf_smime_br_observed_window.csv",
        "cabf_netsec_observed_window.csv",
        "cabf_codesigning_br_observed_window.csv",
        "cabf_evg_observed_window.csv",
    ]
    for filename in expected:
        path = REPO_ROOT / "data" / filename
        assert path.exists(), f"Missing observed-window CSV: {filename}"
        import csv as _csv
        with open(path) as f:
            rows = list(_csv.DictReader(f))
        assert len(rows) >= 1, f"Empty observed-window CSV: {filename}"
        r = rows[0]
        for required_field in ("window_start", "window_end", "version_count",
                                "added", "removed", "modified", "total_changes"):
            assert required_field in r and r[required_field], (
                f"Missing/empty field {required_field} in {filename}"
            )
        # Aggregate consistency
        assert int(r["added"]) + int(r["removed"]) + int(r["modified"]) == int(r["total_changes"]), (
            f"Aggregate mismatch in {filename}: "
            f"{r['added']}+{r['removed']}+{r['modified']} != {r['total_changes']}"
        )


def test_v2_2_1_date_consistent_across_files():
    """v2.2.1 date must be the same across all files that reference it."""
    from datetime import date as _date
    import csv as _csv

    # corpus.csv
    corpus_path = REPO_ROOT / "data" / "cabf_tls_br_corpus.csv"
    with open(corpus_path) as f:
        v221_corpus = next(r["date"] for r in _csv.DictReader(f) if r["version"] == "v2.2.1")

    # observed_window_versions.csv
    window_path = REPO_ROOT / "data" / "cabf_tls_br_observed_window_versions.csv"
    with open(window_path) as f:
        v221_window = next(r["date"] for r in _csv.DictReader(f) if r["version"] == "v2.2.1")

    assert v221_corpus == v221_window, (
        f"v2.2.1 date inconsistent: corpus={v221_corpus}, window={v221_window}"
    )
