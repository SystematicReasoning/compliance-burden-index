"""
Multi-dimensional regime workload comparison.

Cadence (versions/year) is one dimension of workload across regimes. The dev
app tracks several others that the cadence-only view does not capture:

    - Pending enforcements (date-bound action requirements)
    - Active deprecation ballots
    - Total changes tracked in the system
    - Date-bound events on the calendar (sunsets, prohibitions, retirements)

This script pulls all of these into a unified per-regime workload table and
generates a comparison figure showing the workload variation across the
regime stack along multiple axes simultaneously.

Output:
    results/tables/per_regime_workload.csv
    results/figures/fig7_regime_workload_grid.pdf
"""

import csv
import sys
from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from model.data_io import load_observed_window
from model.meta import get_snapshot_date

DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def _read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def load_simple_versions(path):
    rows = []
    for r in _read_csv(path):
        d = date.fromisoformat(r["date"]) if r["date"] else None
        rows.append({"version": r["version"], "date": d})
    return rows


def cadence_from_versions(versions, min_versions=2):
    dated = [v for v in versions if v["date"] is not None]
    if len(dated) < min_versions:
        return None
    dates = sorted(d["date"] for d in dated)
    span_days = (dates[-1] - dates[0]).days
    if span_days <= 0:
        return None
    return len(dates) * 365.0 / span_days


def _load_cabf_window(filename: str):
    """Read the single-row observed-window CSV for a CABF regime and compute cadence."""
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path) as f:
        for row in csv.DictReader(f):
            start = date.fromisoformat(row["window_start"])
            end = date.fromisoformat(row["window_end"])
            days = (end - start).days
            if days <= 0:
                return None
            return int(row["version_count"]) * 365.0 / days
    return None


def collect_workload_table():
    state = _read_csv(DATA_DIR / "regime_stack_state.csv")
    rows = []
    for s in state:
        rid = s["regime_id"]
        # Cadence
        if rid == "cabf_tls_br":
            window = load_observed_window()
            cadence = window.annualized_versions
            cadence_basis = "observed window"
        elif rid == "cabf_smime_br":
            cadence = _load_cabf_window("cabf_smime_br_observed_window.csv")
            cadence_basis = "observed window"
        elif rid == "cabf_netsec":
            cadence = _load_cabf_window("cabf_netsec_observed_window.csv")
            cadence_basis = "observed window"
        elif rid == "cabf_codesigning_br":
            cadence = _load_cabf_window("cabf_codesigning_br_observed_window.csv")
            cadence_basis = "observed window"
        elif rid == "cabf_ev_guidelines":
            # EVG: literal window has restructure ballot; use extended baseline
            extended_days = (date(2026, 4, 28) - date(2024, 4, 17)).days
            cadence = 2 * 365.0 / extended_days  # 2 versions over extended baseline
            cadence_basis = "extended baseline (post-restructure)"
        elif rid == "mozilla_root_program_policy":
            v = load_simple_versions(DATA_DIR / "mozilla_root_store_policy_versions.csv")
            cadence = cadence_from_versions(v)
            cadence_basis = "full tracked history"
        elif rid == "chrome_root_program_policy":
            v = load_simple_versions(DATA_DIR / "chrome_root_program_policy_versions.csv")
            cadence = cadence_from_versions(v)
            cadence_basis = "full tracked history" if cadence else "data incomplete"
        else:
            cadence = None
            cadence_basis = "data insufficient"

        rows.append({
            "regime_id": rid,
            "regime_name": s["regime_name"],
            "versions_tracked": int(s["versions_tracked"]),
            "cadence_versions_per_year": round(cadence, 2) if cadence else None,
            "cadence_basis": cadence_basis,
            "changes_tracked": int(s["changes_tracked"]),
            "pending_enforcements": int(s["pending_enforcements"]),
            "active_deprecation_ballots": int(s["active_deprecation_ballots"]),
            "corpus_measured": s["corpus_measured"],
        })
    return rows


def write_table(rows):
    path = TABLES_DIR / "per_regime_workload.csv"
    fields = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote: {path}")


def make_grid_figure(rows):
    """Multi-axis comparison: cadence, changes, enforcements, deprecations."""
    plt.rcParams.update({
        "font.family": "DejaVu Serif",
        "font.size": 9.5,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
    })

    # Display labels (short and uniform-width to avoid rotation collisions)
    short_label = {
        "cabf_tls_br": "TLS BR",
        "cabf_smime_br": "S/MIME BR",
        "cabf_ev_guidelines": "EV Guidelines",
        "cabf_netsec": "NetSec",
        "cabf_codesigning_br": "Code Signing",
        "mozilla_root_program_policy": "Mozilla MRSP",
        "chrome_root_program_policy": "Chrome RPP",
        "apple_root_program_policy": "Apple RP",
        "microsoft_root_program_policy": "Microsoft TRP",
    }
    labels = [short_label.get(r["regime_id"], r["regime_id"]) for r in rows]

    # Wider and taller; rotation 45° with bigger bottom margin to clear labels
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.6))

    metrics = [
        ("cadence_versions_per_year", "Versions / year", "cadence"),
        ("changes_tracked", "Changes tracked\n(in current data)", "change records"),
        ("pending_enforcements", "Pending\nenforcements", "date-bound actions"),
        ("active_deprecation_ballots", "Active deprecation\nballots", "ballots in flight"),
    ]

    COLOR_TLS = "#a23b3b"
    COLOR_OTHER = "#1f4e79"
    COLOR_NA = "#cbd5dc"

    for ax, (key, ylabel, sub) in zip(axes, metrics):
        values = []
        colors = []
        for r in rows:
            v = r[key]
            if v is None:
                values.append(0)
                colors.append(COLOR_NA)
            else:
                values.append(v)
                colors.append(COLOR_TLS if r["regime_id"] == "cabf_tls_br" else COLOR_OTHER)

        bars = ax.bar(range(len(rows)), values, color=colors, edgecolor="white", linewidth=0.5)
        ax.set_xticks(range(len(rows)))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8.5)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(axis="y", color="#e6e6e6", linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        max_val = max(values) if max(values) > 0 else 1
        ax.set_ylim(0, max_val * 1.25)

        for i, (v, r) in enumerate(zip(values, rows)):
            if r[key] is None:
                ax.text(i, max_val * 0.05, "n/a", ha="center", fontsize=8,
                        color="#888888", style="italic")
            else:
                ax.text(i, v + max_val * 0.03, f"{v}", ha="center",
                        fontsize=8.5, color="#333333")

    fig.suptitle(
        "Per-regime workload across the CA stack — four dimensions of currency burden",
        fontsize=11.5, y=1.0, fontweight="bold",
    )
    fig.text(
        0.5, -0.04,
        "TLS BR carries the dominant share along every dimension visible in the tracking system. "
        "Apple and Microsoft show zero on most dimensions, but their actual change communication "
        "occurs largely outside versioned policy releases (developer documentation, mailing lists, "
        "blog posts), and the tracking gap reflects upstream practice rather than absence of change.",
        ha="center", fontsize=8.5, color="#555555", wrap=True,
    )

    fig.tight_layout(rect=[0, 0.04, 1, 0.97])
    out = FIG_DIR / "fig7_regime_workload_grid.pdf"
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig7_regime_workload_grid.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Wrote: {out}")


def make_calendar_figure():
    """Date-bound action calendar for TLS BRs - the scheduled propagation events."""
    rows = _read_csv(DATA_DIR / "cabf_tls_br_relevant_dates.csv")
    today = get_snapshot_date()

    plt.rcParams.update({
        "font.family": "DejaVu Serif",
        "font.size": 9.5,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
    })

    # Sort by effective date
    rows = sorted(rows, key=lambda r: r["effective_date"])

    type_color = {
        "prohibition": "#a23b3b",
        "sunset": "#c0392b",
        "validation_method_retirement": "#386fa4",
    }
    type_label = {
        "prohibition": "Prohibition",
        "sunset": "Sunset",
        "validation_method_retirement": "Validation method retirement",
    }

    # Compute a wider range for the x-axis based on actual data
    days_values = [(date.fromisoformat(r["effective_date"]) - today).days for r in rows]
    min_day = min(days_values)
    max_day = max(days_values)
    # Pad: enough left of min_day for the section column, enough right for the
    # description text. The section column lives in axis coords, the description
    # text is appended to the right of the bar.
    x_min = -120  # space for "§7.1.3.2.1" left of zero
    x_max = max_day + 380  # extra room for description text

    fig, ax = plt.subplots(figsize=(11.0, 4.2))

    for i, r in enumerate(rows):
        eff = date.fromisoformat(r["effective_date"])
        days_until = (eff - today).days
        color = type_color.get(r["event_type"], "#888")

        ax.barh(i, days_until, color=color, edgecolor="white", linewidth=0.6, height=0.55)

        # Section label in a fixed left column, well clear of any negative-day bars
        ax.text(
            x_min + 8, i,
            f"§{r['section']}",
            va="center", ha="left", fontsize=9, color="#1a1a1a", fontweight="bold",
        )

        # Description text positioned to the right of the bar's RIGHTMOST extent.
        # If the bar is negative, that rightmost extent is 0; if positive, it is days_until.
        right_edge = max(days_until, 0)
        # Truncate long descriptions and ellipsize to keep within plot area
        full_desc = r['description']
        if len(full_desc) > 100:
            short_desc = full_desc[:97] + "…"
        else:
            short_desc = full_desc
        ax.text(
            right_edge + 25, i,
            f"{r['effective_date']}  ({days_until:+d} days)  —  {short_desc}",
            va="center", fontsize=8.5, color="#333333",
        )

    ax.axvline(0, color="#1a1a1a", linewidth=0.8)
    ax.set_yticks([])
    ax.set_xlabel(f"Days from snapshot ({today.isoformat()})")
    ax.set_title("Scheduled propagation events on the TLS BR calendar", loc="left")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(len(rows) - 0.5, -0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.5)
    ax.set_axisbelow(True)

    # Legend below the plot, not in a corner that collides with rows
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in type_color.values()]
    ax.legend(
        handles,
        [type_label[t] for t in type_color.keys()],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=3,
        fontsize=9,
        frameon=False,
    )

    fig.tight_layout()
    out = FIG_DIR / "fig8_relevant_dates_calendar.pdf"
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig8_relevant_dates_calendar.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Wrote: {out}")


def main():
    rows = collect_workload_table()
    write_table(rows)
    make_grid_figure(rows)
    make_calendar_figure()

    print()
    print("Per-regime workload summary:")
    print("-" * 78)
    print(f"  {'Regime':<32} {'Cadence':>10} {'Changes':>10} {'Enf':>6} {'Dep':>6}")
    for r in rows:
        cad = f"{r['cadence_versions_per_year']:.2f}/yr" if r['cadence_versions_per_year'] else "  --"
        print(f"  {r['regime_name'][:30]:<32} {cad:>10} "
              f"{r['changes_tracked']:>10} "
              f"{r['pending_enforcements']:>6} "
              f"{r['active_deprecation_ballots']:>6}")


if __name__ == "__main__":
    main()
