"""
FTE-equivalent visualization of the CABF stack change-handling burden.

The 1,094 h/yr steady-state burden translates to person-time equivalents
under three different capacity bases. This figure presents the same
underlying number through the three lenses that resonate with different
audiences (executives think in FTE, compliance teams think in their own
allocated capacity, standards bodies think in expert-equivalents).

Capacity-base values are loaded from model/parameters.yaml (nominal and
realistic-focused-expert) and from results/current.json (model-allocated
team capacity, which is a computed value), so this script does not embed
the denominators as constants.
"""

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from model.meta import get_snapshot_date

PARAMS_PATH = REPO_ROOT / "model" / "parameters.yaml"
RESULTS_DIR = REPO_ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"


def load_steady_state_burden() -> float:
    """Read the CABF stack steady-state change-handling burden from the
    aggregate output table produced by stack_change_burden.py."""
    path = TABLES_DIR / "cabf_stack_aggregate.csv"
    with open(path) as f:
        for row in csv.DictReader(f):
            if "steady-state" in row["label"].lower() and "incl" not in row["label"].lower():
                return float(row["central_hr"])
    raise ValueError("steady-state row not found in cabf_stack_aggregate.csv")


def load_fte_bases() -> list:
    """Load the three capacity bases.

    Nominal and realistic-focused-expert come from parameters.yaml.
    Model-allocated team capacity comes from results/current.json (computed,
    not stipulated).
    """
    with open(PARAMS_PATH) as f:
        params = yaml.safe_load(f)
    with open(RESULTS_DIR / "current.json") as f:
        headline = json.load(f)

    bases_cfg = params["fte_capacity_bases"]
    team_capacity = headline["central_team_budget"]["team_total_capacity_hours"]

    return [
        {
            "label": bases_cfg["nominal_full_fte"]["label"],
            "denominator": bases_cfg["nominal_full_fte"]["hours_per_year"],
            "denominator_label": (
                f"{bases_cfg['nominal_full_fte']['hours_per_year']:,} h\n"
                f"(standard FTE,\nno PTO/sick/training)"
            ),
            "color": "#84a9c0",
        },
        {
            "label": bases_cfg["realistic_focused_expert"]["label"],
            "denominator": bases_cfg["realistic_focused_expert"]["hours_per_year"],
            "denominator_label": (
                f"{bases_cfg['realistic_focused_expert']['hours_per_year']:,} h\n"
                f"(effective hours\nafter meeting overhead)"
            ),
            "color": "#386fa4",
        },
        {
            "label": bases_cfg["model_allocated_team_capacity"]["label"],
            "denominator": team_capacity,
            "denominator_label": (
                f"{team_capacity:,.0f} h\n"
                f"(7 personas, central\nTLS-BR allocation)"
            ),
            "color": "#1f4e79",
        },
    ]


def make_figure(steady_state_hours: float):
    """Three-bar comparison of the same hours against three capacity bases."""
    bases = load_fte_bases()

    plt.rcParams.update({
        "font.family": "DejaVu Serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelcolor": "#1a1a1a",
        "axes.edgecolor": "#888888",
        "axes.linewidth": 0.6,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#e6e6e6",
        "grid.linewidth": 0.5,
    })

    for b in bases:
        b["fte"] = steady_state_hours / b["denominator"]

    fig, ax = plt.subplots(figsize=(8.0, 5.0))

    x = np.arange(len(bases))
    w = 0.55

    fte_values = [b["fte"] for b in bases]
    colors = [b["color"] for b in bases]
    bars = ax.bar(x, fte_values, w, color=colors, edgecolor="white", linewidth=0.7)

    # 1.0× reference line. Add a clarifying annotation: 1.0 means a different
    # number of hours under each capacity basis, so the line is a visual
    # reference, not a single threshold across all three bars.
    ax.axhline(1.0, color="#a23b3b", linewidth=0.8, linestyle="--", alpha=0.7)
    ax.text(0.02, 1.02, "1.0 person-year (different hours per basis)",
            transform=ax.get_yaxis_transform(),
            fontsize=8.5, color="#a23b3b", ha="left", va="bottom",
            fontweight="bold",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))

    for i, (bar, b) in enumerate(zip(bars, bases)):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.02,
                f"{b['fte']:.2f} FTE",
                ha="center", fontsize=12, fontweight="bold", color="#1a1a1a")

    ax.set_xticks(x)
    ax.set_xticklabels([b["label"] for b in bases], fontsize=10, fontweight="bold")
    ax.set_ylabel("Person-year equivalents (FTE)")
    ax.set_title(
        f"CABF stack steady-state change-handling: {steady_state_hours:.0f} h/yr\n"
        f"expressed as person-year equivalents under three capacity bases",
        loc="left",
        pad=14,
    )
    ax.set_ylim(0, max(fte_values) * 1.25)

    # Denominator labels below the x-tick labels
    for i, b in enumerate(bases):
        ax.text(i, -0.20,
                b["denominator_label"],
                ha="center", va="top", fontsize=8, color="#444444",
                linespacing=1.4, transform=ax.get_xaxis_transform())

    # Footnote
    fig.text(
        0.5, -0.12,
        "What this measures: the cost of staying current enough to know what changed, what it means, who it affects, and what needs to be done.\n"
        "What this does not measure: the cost of actually doing it (engineering changes, CPS edits, audit support, incident response, customer assurance).\n"
        f"CABF stack: TLS BR + S/MIME BR + NetSec + Code Signing BR (steady-state). Excludes EV transition baseline. Snapshot {get_snapshot_date().isoformat()}.",
        ha="center", fontsize=8, color="#555555", linespacing=1.4,
    )

    fig.tight_layout()
    out_pdf = FIG_DIR / "fig10_cabf_stack_fte.pdf"
    out_png = FIG_DIR / "fig10_cabf_stack_fte.png"
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Wrote: {out_pdf}")


def main():
    burden = load_steady_state_burden()
    bases = load_fte_bases()

    print(f"CABF steady-state change-handling burden: {burden:.0f} h/yr")
    print()
    print("Person-year equivalents:")
    for b in bases:
        fte = burden / b["denominator"]
        print(f"  {b['label']:<32} ({b['denominator']:>5,.0f} h)  {fte:>5.2f} FTE")
    print()
    make_figure(burden)


if __name__ == "__main__":
    main()
