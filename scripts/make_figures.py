"""
Generate figures for the methodology and headline reporting.

Figures:
  fig1_capacity_ratio_trajectory.pdf   Team-level capacity ratio over time
  fig2_corpus_growth.pdf                Word count and RFC 2119 keyword count growth
  fig3_per_persona_ratios.pdf           Per-persona capacity ratios at central
  fig4_team_decomposition.pdf           Team-level budget decomposition by scenario
  fig5_sensitivity_heatmap.pdf          Capacity ratio across decay parameter space
"""

import csv
import json
import math
import sys
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from model.budget import Parameters, compute_team_budget, re_read_passes_per_year
from model.data_io import load_corpus_versions, load_observed_window

PARAMS_PATH = REPO_ROOT / "model" / "parameters.yaml"
RESULTS_DIR = REPO_ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Restrained palette
COLOR_TEXT = "#1a1a1a"
COLOR_GRID = "#e6e6e6"
COLOR_LINE = "#1f4e79"
COLOR_ACCENT = "#a23b3b"
COLOR_AT_RISK = "#c0392b"
COLOR_OK = "#2c7a4b"
COLOR_BAR_1 = "#1f4e79"
COLOR_BAR_2 = "#386fa4"
COLOR_BAR_3 = "#84a9c0"
COLOR_BAR_4 = "#c5d5e1"

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 10,
    "axes.labelcolor": COLOR_TEXT,
    "axes.edgecolor": "#888888",
    "axes.linewidth": 0.6,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": COLOR_GRID,
    "grid.linewidth": 0.5,
    "xtick.color": COLOR_TEXT,
    "ytick.color": COLOR_TEXT,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "figure.dpi": 120,
})


def _save(fig, name):
    fig.savefig(FIG_DIR / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / f"{name}.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Wrote: {FIG_DIR / (name + '.pdf')}")


def fig1_capacity_ratio_trajectory():
    """Team-level capacity ratio over time, with observed-window point and envelope."""
    rows = []
    with open(RESULTS_DIR / "tables" / "historical_trajectory_central.csv") as f:
        for r in csv.DictReader(f):
            rows.append({
                "date": date.fromisoformat(r["date"]),
                "ratio": float(r["team_capacity_ratio"]),
                "hours": float(r["team_total_hours"]),
            })

    with open(RESULTS_DIR / "current.json") as f:
        headline = json.load(f)
    obs = headline["data_provenance"]["observed_cadence_window"]
    obs_date = date.fromisoformat(obs["end"])
    env = headline["scenario_envelope"]
    obs_low = env["low"]["team_capacity_ratio"]
    obs_central = env["central"]["team_capacity_ratio"]
    obs_high = env["high"]["team_capacity_ratio"]

    fig, ax = plt.subplots(figsize=(7.0, 4.4))

    dates = [r["date"] for r in rows]
    ratios = [r["ratio"] for r in rows]
    ax.plot(dates, ratios, marker="o", linewidth=1.2, color=COLOR_LINE,
            markersize=4, label="Per-version period (illustrative cadence estimate)")

    # Observed window with envelope
    ax.errorbar(
        [obs_date], [obs_central],
        yerr=[[obs_central - obs_low], [obs_high - obs_central]],
        fmt="s", color=COLOR_ACCENT, markersize=8, capsize=4, elinewidth=1.0,
        label="Observed 2025-08 to 2026-03 (scenario envelope)",
    )

    # Threshold line
    ax.axhline(1.0, color=COLOR_AT_RISK, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.text(date(2013, 6, 1), 1.10, "Model-implied capacity deficit (ratio ≥ 1.0)",
            fontsize=8.5, color=COLOR_AT_RISK, fontweight="bold",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))

    ax.set_xlabel("Version release date")
    ax.set_ylabel("Team aggregate capacity ratio\n(currency-maintenance burden ÷ allocated capacity)")
    ax.set_title("Capacity ratio for the CABF TLS Baseline Requirements over time")
    ax.set_ylim(0, max(obs_high * 1.05, 1.15))

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    fig.text(
        0.5, -0.02,
        "Capacity baseline: standard FTE × focused-work fraction × persona-specific TLS BR allocation, summed across 7 personas.",
        ha="center", fontsize=8, color="#555555",
    )
    fig.tight_layout()
    _save(fig, "fig1_capacity_ratio_trajectory")


def fig2_corpus_growth():
    """Word count and RFC 2119 keyword count over time."""
    versions = load_corpus_versions()
    dates = [v.date for v in versions]
    words = [v.word_count for v in versions]
    keywords = [v.rfc2119_keywords for v in versions]

    fig, ax1 = plt.subplots(figsize=(7.0, 4.0))

    ax1.plot(dates, words, marker="o", color=COLOR_LINE, linewidth=1.2,
             markersize=4, label="Word count (left)")
    ax1.set_xlabel("Version release date")
    ax1.set_ylabel("Word count", color=COLOR_LINE)
    ax1.tick_params(axis="y", labelcolor=COLOR_LINE)
    ax1.set_ylim(0, max(words) * 1.1)

    ax2 = ax1.twinx()
    ax2.plot(dates, keywords, marker="s", color=COLOR_ACCENT, linewidth=1.2,
             markersize=4, linestyle="--", label="RFC 2119 keywords (right)")
    ax2.set_ylabel("RFC 2119 keyword count", color=COLOR_ACCENT)
    ax2.tick_params(axis="y", labelcolor=COLOR_ACCENT)
    ax2.set_ylim(0, max(keywords) * 1.1)
    ax2.grid(False)

    ax1.set_title("Corpus growth: CABF TLS Baseline Requirements, 2012–2025")
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    growth_words = words[-1] / words[0]
    growth_keywords = keywords[-1] / keywords[0]
    ax1.text(
        0.02, 0.95,
        f"Growth (v1.0 → v2.2.1):  words ×{growth_words:.1f}  ·  RFC 2119 keywords ×{growth_keywords:.1f}",
        transform=ax1.transAxes, fontsize=9, color="#333333",
        verticalalignment="top",
    )
    fig.tight_layout()
    _save(fig, "fig2_corpus_growth")


def fig3_per_persona_ratios():
    """Per-persona capacity ratios at central scenario."""
    with open(RESULTS_DIR / "current.json") as f:
        headline = json.load(f)
    personas = headline["central_team_budget"]["personas"]

    ids = [p["persona_id"].replace("_", " ") for p in personas]
    ratios = [p["capacity_ratio"] for p in personas]
    hours = [p["total_hours"] for p in personas]
    capacity = [p["capacity_hours"] for p in personas]

    # Sort by ratio descending
    order = np.argsort(ratios)[::-1]
    ids = [ids[i] for i in order]
    ratios = [ratios[i] for i in order]
    hours = [hours[i] for i in order]
    capacity = [capacity[i] for i in order]

    colors = [COLOR_AT_RISK if r >= 1.0 else COLOR_LINE for r in ratios]

    fig, ax = plt.subplots(figsize=(8.0, 4.8))

    bars = ax.barh(ids, ratios, color=colors, edgecolor="white", linewidth=0.6)
    ax.axvline(1.0, color=COLOR_AT_RISK, linestyle="--", linewidth=0.8, alpha=0.7)

    # Place the "Capacity deficit" label above the plot, near the threshold line,
    # rather than on top of bar value labels.
    ax.annotate(
        "Capacity deficit (ratio ≥ 1.0)",
        xy=(1.0, -0.5), xytext=(1.0, -0.9),
        fontsize=8.5, color=COLOR_AT_RISK, ha="center", fontweight="bold",
        annotation_clip=False,
        arrowprops=dict(arrowstyle="-", color=COLOR_AT_RISK, alpha=0.6, linewidth=0.6),
    )

    for i, (h, c, r) in enumerate(zip(hours, capacity, ratios)):
        ax.text(r + 0.02, i, f"{r:.2f}× ({h:.0f} h / {c:.0f} h)",
                va="center", fontsize=8.5, color="#333333")

    ax.set_xlabel("Capacity ratio (currency-maintenance hours ÷ allocated capacity)")
    ax.set_title("Per-persona capacity ratios — TLS BRs alone, central scenario", pad=24)
    ax.set_xlim(0, max(ratios) * 1.45)
    ax.invert_yaxis()

    fig.tight_layout()
    _save(fig, "fig3_per_persona_ratios")


def fig4_team_decomposition():
    """Stacked bar: team-level decomposition by scenario, capacity overlay."""
    with open(RESULTS_DIR / "current.json") as f:
        headline = json.load(f)

    obs = headline["data_provenance"]["observed_cadence_window"]
    word_count = headline["data_provenance"]["corpus_measured_through"]["word_count"]
    versions_per_year = obs["annualized_versions"]
    changes_per_year = obs["annualized_changes"]

    teams = {}
    for scenario in ("low", "central", "high"):
        params = Parameters.from_yaml(PARAMS_PATH, scenario=scenario)
        teams[scenario] = compute_team_budget(
            word_count=word_count,
            versions_per_year=versions_per_year,
            changes_per_year=changes_per_year,
            params=params,
        )

    # Sum components across personas
    def comp(team, attr):
        return sum(getattr(p, attr) for p in team.personas)

    labels = ["Low\n(optimistic)", "Central", "High\n(pessimistic)"]
    baseline = [comp(teams[s], "baseline_hours") for s in ("low", "central", "high")]
    diff = [comp(teams[s], "diff_review_hours") for s in ("low", "central", "high")]
    triage = [comp(teams[s], "triage_hours") for s in ("low", "central", "high")]
    propagation = [comp(teams[s], "propagation_hours") for s in ("low", "central", "high")]
    capacities = [teams[s].total_capacity for s in ("low", "central", "high")]
    totals = [teams[s].total_hours for s in ("low", "central", "high")]

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    x = np.arange(3)
    w = 0.55

    ax.bar(x, baseline, w, color=COLOR_BAR_1, label="Baseline corpus reads")
    ax.bar(x, diff, w, bottom=baseline, color=COLOR_BAR_2, label="Per-version diff review")
    ax.bar(x, triage, w, bottom=[a + b for a, b in zip(baseline, diff)],
           color=COLOR_BAR_3, label="Per-change triage")
    ax.bar(x, propagation, w,
           bottom=[a + b + c for a, b, c in zip(baseline, diff, triage)],
           color=COLOR_BAR_4, label="Substantive propagation")

    # Capacity overlay (red horizontal line + offset label to the right)
    for i, cap in enumerate(capacities):
        ax.hlines(cap, i - w / 2, i + w / 2, colors=COLOR_AT_RISK,
                  linewidth=2.0, linestyles="-")
        # Place capacity label to the right of the line, vertically centered on it
        ax.text(i + w / 2 + 0.04, cap, f"capacity {cap:.0f} h",
                va="center", ha="left", fontsize=8, color=COLOR_AT_RISK,
                fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Hours per year (team aggregate, 7 personas)")
    ax.set_title("Team budget decomposition vs allocated capacity\n(TLS BRs, observed 2025–2026 cadence)")

    # Burden labels above the top of each stacked bar
    for i, t in enumerate(totals):
        ax.text(i, t + max(totals) * 0.025, f"burden\n{t:.0f} h",
                ha="center", va="bottom", fontsize=8, color="#1a1a1a",
                fontweight="bold")

    ax.legend(loc="upper left", fontsize=8.5, frameon=False)
    ax.set_ylim(0, max(max(totals), max(capacities)) * 1.22)
    # Extend x-limits so capacity labels don't get clipped
    ax.set_xlim(-0.5, len(x) - 0.5 + 0.4)

    fig.tight_layout()
    _save(fig, "fig4_team_decomposition")


def fig5_sensitivity_heatmap():
    """Capacity ratio (not absolute hours) across decay parameter space."""
    with open(RESULTS_DIR / "current.json") as f:
        headline = json.load(f)
    obs = headline["data_provenance"]["observed_cadence_window"]
    word_count = headline["data_provenance"]["corpus_measured_through"]["word_count"]

    params_central = Parameters.from_yaml(PARAMS_PATH, scenario="central")

    taus = np.linspace(60, 240, 19)
    thresholds = np.linspace(0.50, 0.90, 17)
    grid = np.zeros((len(thresholds), len(taus)))

    base_capacity = sum(
        params_central.effective_hours_per_year
        * params_central.focused_work_fraction
        * p.domain_allocation
        for p in params_central.personas
    )

    for i, thr in enumerate(thresholds):
        for j, tau in enumerate(taus):
            n_passes = re_read_passes_per_year(tau, thr)
            # Manually compute team total at varying decay (without re-loading params)
            total = 0.0
            for p in params_central.personas:
                baseline = n_passes * (word_count * p.corpus_depth) / (60.0 * params_central.reading_wpm)
                diff = (
                    obs["annualized_versions"] * params_central.per_version_diff_review_hours
                    if p.requires_version_diff_review else 0.0
                )
                triage = obs["annualized_changes"] * p.corpus_depth * params_central.per_change_triage_hours
                propagation = (
                    obs["annualized_changes"]
                    * p.corpus_depth
                    * p.change_responsibility
                    * params_central.substantive_change_fraction
                    * params_central.per_substantive_change_propagation_hours
                )
                total += baseline + diff + triage + propagation
            grid[i, j] = total / base_capacity

    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    im = ax.imshow(
        grid,
        origin="lower",
        aspect="auto",
        extent=[taus[0], taus[-1], thresholds[0], thresholds[-1]],
        cmap="YlOrRd",
        vmin=0.5,
        vmax=max(1.5, grid.max()),
    )

    cs = ax.contour(taus, thresholds, grid, levels=[0.7, 0.85, 1.0, 1.2],
                    colors="#222222", linewidths=0.7)
    ax.clabel(cs, fmt="%.2f×", fontsize=8)

    ax.plot([120], [0.70], marker="*", markersize=14, color="#1a1a1a",
            markerfacecolor="white", markeredgewidth=1.2)
    ax.annotate("central (0.84×)", xy=(120, 0.70), xytext=(140, 0.62),
                fontsize=9, color="#1a1a1a")

    ax.set_xlabel("Decay time constant τ (days)")
    ax.set_ylabel("Working accuracy threshold")
    ax.set_title("Sensitivity: team capacity ratio across decay parameters")
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Team capacity ratio", fontsize=9)

    ax.grid(False)
    fig.tight_layout()
    _save(fig, "fig5_sensitivity_heatmap")


def fig5b_phi_sensitivity():
    """One-axis sensitivity: team capacity ratio as a function of φ.

    The substantive-change fraction φ is the single parameter most directly
    affecting the headline. Its central value is a practitioner_estimate, not
    a measurement, so the headline's robustness to φ is worth showing on its
    own scan. The relationship is linear in the propagation component, which
    is the largest of the four budget components.
    """
    with open(RESULTS_DIR / "current.json") as f:
        headline = json.load(f)
    obs = headline["data_provenance"]["observed_cadence_window"]
    word_count = headline["data_provenance"]["corpus_measured_through"]["word_count"]

    params_central = Parameters.from_yaml(PARAMS_PATH, scenario="central")
    n_passes = re_read_passes_per_year(
        params_central.decay_time_constant_days, params_central.working_accuracy_threshold
    )

    base_capacity = sum(
        params_central.effective_hours_per_year
        * params_central.focused_work_fraction
        * p.domain_allocation
        for p in params_central.personas
    )

    phis = np.linspace(0.05, 1.00, 39)
    ratios = np.zeros_like(phis)

    for k, phi in enumerate(phis):
        total = 0.0
        for p in params_central.personas:
            baseline = n_passes * (word_count * p.corpus_depth) / (60.0 * params_central.reading_wpm)
            diff = (
                obs["annualized_versions"] * params_central.per_version_diff_review_hours
                if p.requires_version_diff_review else 0.0
            )
            triage = obs["annualized_changes"] * p.corpus_depth * params_central.per_change_triage_hours
            propagation = (
                obs["annualized_changes"]
                * p.corpus_depth
                * p.change_responsibility
                * phi
                * params_central.per_substantive_change_propagation_hours
            )
            total += baseline + diff + triage + propagation
        ratios[k] = total / base_capacity

    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.plot(phis, ratios, color=COLOR_LINE, linewidth=1.8)
    ax.axhline(1.0, color=COLOR_AT_RISK, linestyle="--", linewidth=0.8, alpha=0.7)
    ax.axvline(params_central.substantive_change_fraction, color="#666",
               linestyle=":", linewidth=0.8)

    central_phi = params_central.substantive_change_fraction
    central_ratio = float(np.interp(central_phi, phis, ratios))
    ax.plot([central_phi], [central_ratio], marker="*", markersize=14,
            color="#1a1a1a", markerfacecolor="white", markeredgewidth=1.2)
    ax.annotate(
        f"central (φ={central_phi:.2f},\nratio={central_ratio:.2f}×)",
        xy=(central_phi, central_ratio),
        xytext=(central_phi + 0.08, central_ratio - 0.10),
        fontsize=9, color="#1a1a1a",
    )

    # Mark φ envelope endpoints used elsewhere in the model
    for phi_mark, label in [(0.20, "low envelope"), (0.60, "high envelope")]:
        ratio_at = float(np.interp(phi_mark, phis, ratios))
        ax.plot([phi_mark], [ratio_at], marker="o", markersize=5, color="#888")
        ax.annotate(f"{label}\n({ratio_at:.2f}×)", xy=(phi_mark, ratio_at),
                    xytext=(phi_mark - 0.02, ratio_at + 0.06),
                    fontsize=8, color="#666", ha="right")

    ax.set_xlabel("Substantive-change fraction φ")
    ax.set_ylabel("Team capacity ratio")
    ax.set_title("Sensitivity: team capacity ratio is linear in φ")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, max(1.5, ratios.max() * 1.1))
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "fig5b_phi_sensitivity")


if __name__ == "__main__":
    fig1_capacity_ratio_trajectory()
    fig2_corpus_growth()
    fig3_per_persona_ratios()
    fig4_team_decomposition()
    fig5_sensitivity_heatmap()
    fig5b_phi_sensitivity()
    print("\nAll figures generated.")
