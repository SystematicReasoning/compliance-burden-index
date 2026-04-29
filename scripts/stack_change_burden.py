"""
Multi-regime change-handling burden computation.

For each regime with measured cadence (V) and change count (E), compute the
team-level change-handling burden using the persona-weighted formula from the
core model. Aggregates across the CABF stack to produce a measured (not
inventoried) lower-bound budget for the team's CABF currency-maintenance work.

This script does NOT compute baseline corpus reading for non-TLS-BR regimes,
because we do not yet have corpus word counts for those regimes. Change
handling alone accounts for ~80% of the budget at central parameters (per the
TLS BR analysis), so the multi-regime change-handling number is a meaningful
floor for the multi-regime budget.

Output:
    results/tables/per_regime_change_burden.csv
    results/tables/cabf_stack_aggregate.csv
    results/figures/fig9_stack_change_burden.pdf
"""

import csv
import sys
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from model.budget import Parameters

PARAMS_PATH = REPO_ROOT / "model" / "parameters.yaml"
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def load_observed_window_csv(path):
    """Load a single-row observed-window CSV, return parsed dict."""
    with open(path) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None
    r = rows[0]
    return {
        "window_start": date.fromisoformat(r["window_start"]),
        "window_end": date.fromisoformat(r["window_end"]),
        "version_count": int(r["version_count"]),
        "added": int(r["added"]),
        "removed": int(r["removed"]),
        "modified": int(r["modified"]),
        "total_changes": int(r["total_changes"]),
        "provenance": r.get("provenance", ""),
    }


def annualized(window):
    days = (window["window_end"] - window["window_start"]).days
    if days <= 0:
        return 0.0, 0.0
    v_per_year = window["version_count"] * 365.0 / days
    e_per_year = window["total_changes"] * 365.0 / days
    return v_per_year, e_per_year, days


# Regimes with measured cadence and change data (CABF stack)
CABF_REGIMES = [
    ("cabf_tls_br", "CA/Browser Forum TLS Baseline Requirements", "TLS BR",
     "cabf_tls_br_observed_window.csv", "steady_state"),
    ("cabf_smime_br", "CA/Browser Forum S/MIME Baseline Requirements", "S/MIME BR",
     "cabf_smime_br_observed_window.csv", "steady_state"),
    ("cabf_netsec", "CA/Browser Forum Network Security Requirements", "NetSec",
     "cabf_netsec_observed_window.csv", "single_release_window"),
    ("cabf_codesigning_br", "CA/Browser Forum Code Signing Baseline Requirements", "Code Signing BR",
     "cabf_codesigning_br_observed_window.csv", "steady_state"),
    ("cabf_evg", "CA/Browser Forum Extended Validation Guidelines", "EV Guidelines",
     "cabf_evg_observed_window.csv", "transition_extended_baseline"),
]


def team_change_handling_hours(versions_per_year, changes_per_year, params):
    """Team-level change handling using the persona-weighted formula.

    Aggregates across personas:
      - Diff review: V × t_diff × |personas with requires_version_diff_review|
      - Triage: E × t_assess × Σ d_p
      - Propagation: E × phi × t_propagate × Σ (d_p × c_p)

    Returns (diff, triage, propagation, total).
    """
    n_diff = sum(1 for p in params.personas if p.requires_version_diff_review)
    sum_depth = sum(p.corpus_depth for p in params.personas)
    sum_depth_responsibility = sum(p.corpus_depth * p.change_responsibility for p in params.personas)

    diff_hours = versions_per_year * params.per_version_diff_review_hours * n_diff
    triage_hours = changes_per_year * params.per_change_triage_hours * sum_depth
    propagation_hours = (
        changes_per_year
        * params.substantive_change_fraction
        * params.per_substantive_change_propagation_hours
        * sum_depth_responsibility
    )
    return diff_hours, triage_hours, propagation_hours, diff_hours + triage_hours + propagation_hours


def main():
    params_central = Parameters.from_yaml(PARAMS_PATH, scenario="central")
    params_low = Parameters.from_yaml(PARAMS_PATH, scenario="low")
    params_high = Parameters.from_yaml(PARAMS_PATH, scenario="high")

    rows = []
    cabf_steady_low = 0.0
    cabf_steady_central = 0.0
    cabf_steady_high = 0.0
    cabf_transition_central = 0.0

    for regime_id, regime_name, short_name, csv_file, regime_status in CABF_REGIMES:
        path = DATA_DIR / csv_file
        if not path.exists():
            continue
        window = load_observed_window_csv(path)
        if window is None:
            continue
        v_yr, e_yr, days = annualized(window)

        # Compute at all three scenarios
        results = {}
        for scenario_name, params in [("low", params_low), ("central", params_central), ("high", params_high)]:
            diff, triage, prop, total = team_change_handling_hours(v_yr, e_yr, params)
            results[scenario_name] = {
                "diff": diff, "triage": triage, "propagation": prop, "total": total,
            }

        rows.append({
            "regime_id": regime_id,
            "regime_short": short_name,
            "regime_name": regime_name,
            "regime_status": regime_status,
            "window_days": days,
            "versions_in_window": window["version_count"],
            "changes_in_window": window["total_changes"],
            "annualized_versions": round(v_yr, 2),
            "annualized_changes": round(e_yr, 1),
            "team_change_burden_low_hr": round(results["low"]["total"], 1),
            "team_change_burden_central_hr": round(results["central"]["total"], 1),
            "team_change_burden_high_hr": round(results["high"]["total"], 1),
            "central_diff": round(results["central"]["diff"], 1),
            "central_triage": round(results["central"]["triage"], 1),
            "central_propagation": round(results["central"]["propagation"], 1),
        })

        # Aggregate steady-state vs transition
        if regime_status == "transition_extended_baseline":
            cabf_transition_central += results["central"]["total"]
        else:
            cabf_steady_low += results["low"]["total"]
            cabf_steady_central += results["central"]["total"]
            cabf_steady_high += results["high"]["total"]

    # Write per-regime table
    fields = [
        "regime_id", "regime_short", "regime_name", "regime_status",
        "window_days", "versions_in_window", "changes_in_window",
        "annualized_versions", "annualized_changes",
        "team_change_burden_low_hr", "team_change_burden_central_hr", "team_change_burden_high_hr",
        "central_diff", "central_triage", "central_propagation",
    ]
    with open(TABLES_DIR / "per_regime_change_burden.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote: {TABLES_DIR / 'per_regime_change_burden.csv'}")

    # Aggregate stack table
    aggregate_rows = [
        {"label": "CABF stack (steady-state, 4 regimes)", "low_hr": round(cabf_steady_low, 1),
         "central_hr": round(cabf_steady_central, 1), "high_hr": round(cabf_steady_high, 1),
         "note": "TLS BR + S/MIME BR + NetSec + Code Signing BR. Excludes EV Guidelines transition."},
        {"label": "EV Guidelines transition (extended baseline)", "low_hr": "—",
         "central_hr": round(cabf_transition_central, 1), "high_hr": "—",
         "note": "v2.0.0 restructure annualized over 2 years post-restructure. Treat as transition burden, not steady state."},
        {"label": "CABF stack incl. EV transition (5 regimes)", "low_hr": "—",
         "central_hr": round(cabf_steady_central + cabf_transition_central, 1), "high_hr": "—",
         "note": "Steady-state plus EV transition baseline."},
    ]
    with open(TABLES_DIR / "cabf_stack_aggregate.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["label", "low_hr", "central_hr", "high_hr", "note"])
        w.writeheader()
        for r in aggregate_rows:
            w.writerow(r)
    print(f"Wrote: {TABLES_DIR / 'cabf_stack_aggregate.csv'}")

    # ------------------------------------------------------------
    # Figure 9: stacked horizontal bars showing per-regime change burden
    # ------------------------------------------------------------
    plt.rcParams.update({
        "font.family": "DejaVu Serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
    })

    # Sort by central burden descending
    rows_sorted = sorted(rows, key=lambda r: r["team_change_burden_central_hr"], reverse=True)

    labels = [r["regime_short"] for r in rows_sorted]
    diff_vals = [r["central_diff"] for r in rows_sorted]
    triage_vals = [r["central_triage"] for r in rows_sorted]
    prop_vals = [r["central_propagation"] for r in rows_sorted]

    COLOR_DIFF = "#1f4e79"
    COLOR_TRIAGE = "#84a9c0"
    COLOR_PROP = "#c5d5e1"
    COLOR_TRANSITION = "#a23b3b"

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    y = np.arange(len(labels))
    h = 0.65

    p1 = ax.barh(y, diff_vals, h, color=COLOR_DIFF, label="Per-version diff review")
    p2 = ax.barh(y, triage_vals, h, left=diff_vals, color=COLOR_TRIAGE, label="Per-change triage")
    p3 = ax.barh(y, prop_vals, h, left=[a + b for a, b in zip(diff_vals, triage_vals)],
                 color=COLOR_PROP, label="Substantive propagation")

    # Highlight EV transition with edge color
    for i, r in enumerate(rows_sorted):
        if r["regime_status"] == "transition_extended_baseline":
            for patch in [p1.patches[i], p2.patches[i], p3.patches[i]]:
                patch.set_edgecolor(COLOR_TRANSITION)
                patch.set_linewidth(1.4)

    # Total annotations
    for i, r in enumerate(rows_sorted):
        total = r["team_change_burden_central_hr"]
        marker = " (transition)" if r["regime_status"] == "transition_extended_baseline" else ""
        ax.text(total + 15, i, f"{total:.0f} h/yr{marker}",
                va="center", fontsize=9, color="#1a1a1a")

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Hours per year (team aggregate, 7 personas, central scenario)")
    ax.set_title("Change-handling burden across the CABF regime stack\n(measured cadence, change count from CPS Dev App tracking)")
    ax.invert_yaxis()
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    # Aggregate annotation
    ax.set_xlim(0, max(r["team_change_burden_central_hr"] for r in rows_sorted) * 1.45)
    fig.text(
        0.5, -0.03,
        f"Steady-state CABF stack (4 regimes): {cabf_steady_central:.0f} h/yr.  "
        f"Adding EV transition baseline: {cabf_steady_central + cabf_transition_central:.0f} h/yr.  "
        f"Excludes baseline corpus reading and non-CABF regimes.",
        ha="center", fontsize=8.5, color="#444444",
    )
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)

    fig.tight_layout()
    out = FIG_DIR / "fig9_stack_change_burden.pdf"
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig9_stack_change_burden.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Wrote: {out}")

    # Console summary
    print()
    print("Per-regime change-handling burden (central scenario):")
    print("-" * 78)
    print(f"  {'Regime':<22} {'V/yr':>7} {'E/yr':>7} {'Burden':>9} {'Status':<25}")
    for r in rows_sorted:
        print(f"  {r['regime_short']:<22} {r['annualized_versions']:>7.2f} "
              f"{r['annualized_changes']:>7.1f} {r['team_change_burden_central_hr']:>7.0f} h "
              f"{r['regime_status']:<25}")
    print()
    print(f"CABF stack steady-state: {cabf_steady_central:.0f} h/yr")
    print(f"  Sensitivity envelope:  {cabf_steady_low:.0f} – {cabf_steady_high:.0f} h/yr")
    print(f"EV transition baseline:   {cabf_transition_central:.0f} h/yr (extended)")
    print(f"CABF stack total:         {cabf_steady_central + cabf_transition_central:.0f} h/yr")


if __name__ == "__main__":
    main()
