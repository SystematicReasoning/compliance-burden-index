"""
Compute headline numbers and historical trajectory.

Reads inputs from data/, parameters from model/parameters.yaml, writes outputs
to results/.

No values from the empirical substrate are hard-coded in this script. The
observed window comes from cabf_tls_br_observed_window.csv; corpus measurements
come from cabf_tls_br_corpus.csv; parameters come from parameters.yaml.
"""

import json
import csv
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from model.budget import Parameters, compute_team_budget, re_read_passes_per_year
from model.data_io import load_corpus_versions, load_observed_window
from model.meta import get_version, get_snapshot_date

PARAMS_PATH = REPO_ROOT / "model" / "parameters.yaml"
RESULTS_DIR = REPO_ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list, fieldnames: list) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def historical_trajectory(corpus_versions, params: Parameters, keyword_delta_multiplier: float):
    """Per-version annualized trajectory.

    For each consecutive pair of measured versions, treat the interval as a
    cadence sample. Estimate changes-per-year via a heuristic linked to the
    requirement-keyword delta. The estimator is documented and is intended to
    be replaced with directly-measured per-version change counts as the data
    pipeline expands.

    The multiplier is loaded from model/parameters.yaml under
    historical_trajectory.keyword_delta_multiplier.
    """
    rows = []
    for i in range(1, len(corpus_versions)):
        prev = corpus_versions[i - 1]
        curr = corpus_versions[i]
        period_days = (curr.date - prev.date).days
        if period_days <= 0:
            continue
        versions_per_year = 365.0 / period_days
        keyword_delta = abs(curr.rfc2119_keywords - prev.rfc2119_keywords)
        est_changes_in_period = keyword_delta * keyword_delta_multiplier
        changes_per_year = est_changes_in_period * 365.0 / period_days

        team = compute_team_budget(
            word_count=curr.word_count,
            versions_per_year=versions_per_year,
            changes_per_year=changes_per_year,
            params=params,
        )
        rows.append({
            "version": curr.version,
            "date": curr.date.isoformat(),
            "period_days": period_days,
            "word_count": curr.word_count,
            "versions_per_year": round(versions_per_year, 2),
            "changes_per_year_estimated": round(changes_per_year, 1),
            "team_total_hours": round(team.total_hours, 1),
            "team_total_capacity_hours": round(team.total_capacity, 1),
            "team_capacity_ratio": round(team.aggregate_capacity_ratio, 2),
            "estimator": f"keyword_delta_x{keyword_delta_multiplier}_illustrative",
        })
    return rows


def main():
    # Load empirical inputs
    corpus = load_corpus_versions()
    window = load_observed_window()
    latest_measured = corpus[-1]

    # Build scenarios
    params_low = Parameters.from_yaml(PARAMS_PATH, scenario="low")
    params_central = Parameters.from_yaml(PARAMS_PATH, scenario="central")
    params_high = Parameters.from_yaml(PARAMS_PATH, scenario="high")

    # Headline: latest measured corpus + observed-window cadence
    obs_versions_per_year = window.annualized_versions
    obs_changes_per_year = window.annualized_changes

    team_low = compute_team_budget(
        word_count=latest_measured.word_count,
        versions_per_year=obs_versions_per_year,
        changes_per_year=obs_changes_per_year,
        params=params_low,
    )
    team_central = compute_team_budget(
        word_count=latest_measured.word_count,
        versions_per_year=obs_versions_per_year,
        changes_per_year=obs_changes_per_year,
        params=params_central,
    )
    team_high = compute_team_budget(
        word_count=latest_measured.word_count,
        versions_per_year=obs_versions_per_year,
        changes_per_year=obs_changes_per_year,
        params=params_high,
    )

    # Historical trajectory — load the keyword-delta multiplier from parameters
    import yaml as _yaml
    with open(PARAMS_PATH) as _f:
        _cfg = _yaml.safe_load(_f)
    keyword_delta_multiplier = _cfg["historical_trajectory"]["keyword_delta_multiplier"]["central"]

    historical = historical_trajectory(corpus, params_central, keyword_delta_multiplier)
    write_csv(
        TABLES_DIR / "historical_trajectory_central.csv",
        historical,
        list(historical[0].keys()),
    )

    # Per-persona table for the headline central scenario
    persona_rows = [p.as_dict() for p in team_central.personas]
    write_csv(
        TABLES_DIR / "per_persona_central.csv",
        persona_rows,
        list(persona_rows[0].keys()),
    )

    # Headline JSON
    headline = {
        "regime_id": "cabf-tls-br",
        "snapshot_date": get_snapshot_date().isoformat(),
        "methodology_version": get_version(),
        "data_provenance": {
            "corpus_measured_through": {
                "version": latest_measured.version,
                "date": latest_measured.date.isoformat(),
                "word_count": latest_measured.word_count,
                "rfc2119_keywords": latest_measured.rfc2119_keywords,
            },
            "observed_cadence_window": {
                "window_id": window.window_id,
                "start": window.window_start.isoformat(),
                "end": window.window_end.isoformat(),
                "days": window.days,
                "start_version": window.start_version,
                "end_version": window.end_version,
                "version_count": window.version_count,
                "added": window.added,
                "removed": window.removed,
                "modified": window.modified,
                "total_changes": window.total_changes,
                "annualized_versions": round(window.annualized_versions, 2),
                "annualized_changes": round(window.annualized_changes, 1),
                "provenance": window.provenance,
                "extraction_method": window.extraction_method,
            },
            "note": (
                "Corpus measurements end at the latest measured version; "
                "observed-window cadence may extend past that version. "
                "The headline uses the latest measured corpus for the W input "
                "and the observed-window cadence for the V and E inputs. "
                "Both inputs are stated explicitly in this provenance block."
            ),
        },
        "scenario_envelope": {
            "low": {
                "label": "optimistic",
                "team_total_hours": round(team_low.total_hours, 1),
                "team_total_capacity_hours": round(team_low.total_capacity, 1),
                "team_capacity_ratio": round(team_low.aggregate_capacity_ratio, 2),
            },
            "central": {
                "label": "central",
                "team_total_hours": round(team_central.total_hours, 1),
                "team_total_capacity_hours": round(team_central.total_capacity, 1),
                "team_capacity_ratio": round(team_central.aggregate_capacity_ratio, 2),
            },
            "high": {
                "label": "pessimistic",
                "team_total_hours": round(team_high.total_hours, 1),
                "team_total_capacity_hours": round(team_high.total_capacity, 1),
                "team_capacity_ratio": round(team_high.aggregate_capacity_ratio, 2),
            },
        },
        "central_team_budget": team_central.as_dict(),
        "decay_passes_central": re_read_passes_per_year(120, 0.70),
    }
    with open(RESULTS_DIR / "current.json", "w") as f:
        json.dump(headline, f, indent=2)

    # ------------------------------------------------------------
    # Console output
    # ------------------------------------------------------------
    sep = "=" * 78
    print(sep)
    print("CABF TLS Baseline Requirements — Knowledge Currency Budget")
    print(f"Methodology version {get_version()} (snapshot {get_snapshot_date().isoformat()})")
    print(sep)
    print()
    print("DATA PROVENANCE")
    print("-" * 78)
    print(f"  Corpus measured through:  {latest_measured.version} "
          f"({latest_measured.date}, {latest_measured.word_count:,} words, "
          f"{latest_measured.rfc2119_keywords} RFC 2119 keywords)")
    print(f"  Observed cadence window:  {window.window_start} to {window.window_end}")
    print(f"                            {window.start_version} → {window.end_version}")
    print(f"                            {window.version_count} versions, "
          f"{window.total_changes} changes "
          f"({window.added} added, {window.removed} removed, {window.modified} modified)")
    print(f"  Annualized:               {window.annualized_versions:.1f} versions/yr, "
          f"{window.annualized_changes:.0f} changes/yr")
    print(f"  Provenance:               {window.provenance}")
    print()
    print("TEAM-LEVEL HEADLINE (across all personas, central scenario)")
    print("-" * 78)
    print(f"  Total budget:             {team_central.total_hours:7.1f} hours/year")
    print(f"  Total capacity:           {team_central.total_capacity:7.1f} hours/year")
    print(f"  Capacity ratio:           {team_central.aggregate_capacity_ratio:7.2f}×")
    print()
    print("PER-PERSONA BREAKDOWN (central scenario)")
    print("-" * 78)
    print(f"  {'Persona':<26} {'Hours/yr':>9} {'Capacity':>10} {'Ratio':>7}")
    for p in team_central.personas:
        print(f"  {p.persona_id:<26} {p.total_hours:>9.1f} {p.capacity_hours:>10.1f} {p.capacity_ratio:>7.2f}×")
    print()
    print("SCENARIO ENVELOPE (team-level capacity ratio)")
    print("-" * 78)
    print(f"  Low (optimistic):         {team_low.aggregate_capacity_ratio:7.2f}×  "
          f"({team_low.total_hours:.0f} h / {team_low.total_capacity:.0f} h)")
    print(f"  Central:                  {team_central.aggregate_capacity_ratio:7.2f}×  "
          f"({team_central.total_hours:.0f} h / {team_central.total_capacity:.0f} h)")
    print(f"  High (pessimistic):       {team_high.aggregate_capacity_ratio:7.2f}×  "
          f"({team_high.total_hours:.0f} h / {team_high.total_capacity:.0f} h)")
    print()
    print(f"Wrote: {RESULTS_DIR / 'current.json'}")
    print(f"Wrote: {TABLES_DIR / 'historical_trajectory_central.csv'}")
    print(f"Wrote: {TABLES_DIR / 'per_persona_central.csv'}")


if __name__ == "__main__":
    main()
