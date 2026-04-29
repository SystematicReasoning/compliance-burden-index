"""
Cross-regime cadence comparison.

Reports per-regime visible cadence (versions per year), classified by tier:

  Tier 1 — versioned, ballot-driven. CABF documents. The version count is the
  unit of normative change; per-version edits are auditable from redlines.
  Visible cadence is a complete measure of normative change rate.

  Tier 2 — continuously communicated. Root programs. Versioned policy is a
  periodic snapshot of decisions propagated through m.d.s.policy, CCADB,
  GitHub repos, blog posts, developer documentation, and direct
  correspondence. Visible (versioned) cadence is a floor and a partial
  measure; actual normative volume is captured in the channels we do not
  yet ingest.

The H(R) budget computation in this index applies directly to Tier 1
regimes. Applying it to Tier 2 regimes using version-only cadence would
produce a misleading underestimate because the input quantity (E, edits per
year) is missing the predominant channel.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from model.data_io import load_observed_window

DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def load_simple_versions(path: Path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            d = None
            if r["date"]:
                d = date.fromisoformat(r["date"])
            rows.append({"version": r["version"], "date": d, "note": r.get("note", "")})
    return rows


def cadence_from_versions(versions, min_versions=2):
    """Compute versions/year using release-count over span: n_releases × 365 / span_days.

    Matches the convention used for TLS BR observed-window cadence
    (10 releases / 218 days × 365 = 16.74).
    """
    dated = [v for v in versions if v["date"] is not None]
    if len(dated) < min_versions:
        return None, None, None
    dates = sorted(d["date"] for d in dated)
    span_days = (dates[-1] - dates[0]).days
    if span_days <= 0:
        return None, None, None
    return len(dates) * 365.0 / span_days, dates[0], dates[-1]


def load_regime_stack_state():
    rows = []
    with open(DATA_DIR / "regime_stack_state.csv") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def load_cabf_observed_window(path: Path):
    with open(path) as f:
        for r in csv.DictReader(f):
            return r
    return None


def compute_per_regime_cadence():
    """Aggregate per-regime cadence with tier classification."""
    out = []

    # Tier 1: TLS BRs (full data via observed window)
    window = load_observed_window()
    out.append({
        "regime_id": "cabf_tls_br",
        "regime_name": "CA/Browser Forum TLS Baseline Requirements",
        "tier": "1_versioned_ballot_driven",
        "visible_cadence_versions_per_year": round(window.annualized_versions, 2),
        "cadence_interpretation": "complete_change_rate",
        "computation_basis": (
            f"Observed window {window.window_start} to {window.window_end} "
            f"({window.version_count} versions in {window.days} days). "
            f"Per-version edits auditable from CABF redlines: 139 changes."
        ),
        "status": "computed",
    })

    # Tier 1: other CABF regimes from their observed-window CSVs
    cabf_regimes = [
        ("cabf_smime_br_observed_window.csv", "cabf_smime_br",
         "CA/Browser Forum S/MIME Baseline Requirements"),
        ("cabf_netsec_observed_window.csv", "cabf_netsec",
         "CA/Browser Forum Network Security Requirements"),
        ("cabf_evg_observed_window.csv", "cabf_ev_guidelines",
         "CA/Browser Forum Extended Validation Guidelines"),
        ("cabf_codesigning_br_observed_window.csv", "cabf_codesigning_br",
         "CA/Browser Forum Code Signing Baseline Requirements"),
    ]
    for csv_name, rid, name in cabf_regimes:
        path = DATA_DIR / csv_name
        if not path.exists():
            continue
        row = load_cabf_observed_window(path)
        if row is None:
            continue
        start = date.fromisoformat(row["window_start"])
        end = date.fromisoformat(row["window_end"])
        days = (end - start).days
        if days <= 0:
            continue
        version_count = int(row["version_count"])
        total_changes = int(row["total_changes"])

        # EV Guidelines special-case: literal 19-day window is non-representative
        # due to restructure ballot. Use extended baseline if present in note.
        if rid == "cabf_ev_guidelines":
            note = row.get("extraction_method", "") + " " + row.get("note", "")
            if "Annualized over ~2 years" in note or "extended" in note.lower():
                # Use extended baseline of ~2 years
                extended_days = (date.fromisoformat("2026-04-28")
                                 - date.fromisoformat("2024-04-17")).days
                vy = version_count * 365.0 / extended_days
                basis = (f"Extended baseline annualization. Literal 19-day window "
                         f"contained 145 restructure changes; {extended_days}-day "
                         f"baseline used.")
            else:
                vy = version_count * 365.0 / days
                basis = f"{version_count} versions over {days} days"
        else:
            vy = version_count * 365.0 / days
            basis = (f"{version_count} versions over {days} days "
                     f"({row['start_version']} to {row['end_version']}); "
                     f"{total_changes} total changes")

        out.append({
            "regime_id": rid,
            "regime_name": name,
            "tier": "1_versioned_ballot_driven",
            "visible_cadence_versions_per_year": round(vy, 2),
            "cadence_interpretation": "complete_change_rate",
            "computation_basis": basis,
            "status": "computed",
        })

    # Tier 2: Mozilla MRSP
    moz = load_simple_versions(DATA_DIR / "mozilla_root_store_policy_versions.csv")
    moz_vy, moz_start, moz_end = cadence_from_versions(moz)
    out.append({
        "regime_id": "mozilla_root_store_policy",
        "regime_name": "Mozilla Root Store Policy",
        "tier": "2_continuously_communicated",
        "visible_cadence_versions_per_year": round(moz_vy, 2) if moz_vy else None,
        "cadence_interpretation": "versioned_snapshot_floor",
        "computation_basis": (
            f"{len([v for v in moz if v['date']])} tracked versions, {moz_start} to {moz_end}. "
            f"Versioned cadence is a floor; actual normative volume propagates through "
            f"m.d.s.policy threads, CCADB records, and Bugzilla."
        ),
        "status": "computed_partial",
    })

    # Tier 2: Chrome RPP (cadence computable from 2 dated versions, treated as Tier 2 floor)
    chrome = load_simple_versions(DATA_DIR / "chrome_root_program_policy_versions.csv")
    chrome_vy, chrome_start, chrome_end = cadence_from_versions(chrome)
    out.append({
        "regime_id": "chrome_root_program_policy",
        "regime_name": "Chrome Root Program Policy",
        "tier": "2_continuously_communicated",
        "visible_cadence_versions_per_year": round(chrome_vy, 2) if chrome_vy else None,
        "cadence_interpretation": "versioned_snapshot_floor",
        "computation_basis": (
            f"{len([v for v in chrome if v['date']])} dated versions ({chrome_start} to {chrome_end}); "
            f"4 versions tracked total. Visible cadence is a floor; normative communication also flows "
            f"via the Chrome Root Program GitHub repo, blog posts, and CABF ballot positions."
        ) if chrome_vy else (
            "Insufficient dated versions for cadence; even when computable, version cadence "
            "would be a floor."
        ),
        "status": "computed_partial" if chrome_vy else "data_incomplete",
    })

    # Tier 2: Apple
    out.append({
        "regime_id": "apple_root_certificate_program",
        "regime_name": "Apple Root Certificate Program",
        "tier": "2_continuously_communicated",
        "visible_cadence_versions_per_year": None,
        "cadence_interpretation": "versioned_snapshot_floor",
        "computation_basis": (
            "Single tracked version. Apple typically communicates normative changes via "
            "developer documentation updates and root program email rather than versioned "
            "policy releases. Version count materially understates change rate."
        ),
        "status": "data_insufficient",
    })

    # Tier 2: Microsoft
    out.append({
        "regime_id": "microsoft_trusted_root_program",
        "regime_name": "Microsoft Trusted Root Program",
        "tier": "2_continuously_communicated",
        "visible_cadence_versions_per_year": None,
        "cadence_interpretation": "versioned_snapshot_floor",
        "computation_basis": (
            "Single tracked version. Microsoft typically communicates normative changes via "
            "TechCommunity posts, security baseline updates, and KB articles rather than "
            "versioned policy releases. Version count materially understates change rate."
        ),
        "status": "data_insufficient",
    })

    return out


def write_table(rows):
    out_path = TABLES_DIR / "per_regime_cadence.csv"
    fields = [
        "regime_id", "regime_name", "tier",
        "visible_cadence_versions_per_year", "cadence_interpretation",
        "computation_basis", "status",
    ]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote: {out_path}")


def make_figure(rows):
    """Cadence comparison with explicit tier separation.

    Tier 1 regimes get a colored bar; Tier 2 regimes get a tinted bar with
    explicit "floor" annotation indicating the visible cadence is incomplete.
    """
    plt.rcParams.update({
        "font.family": "DejaVu Serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
    })

    COLOR_TIER1_FAST = "#a23b3b"
    COLOR_TIER1_MED = "#c47a4a"
    COLOR_TIER2_VISIBLE = "#7c8fa3"
    COLOR_TIER2_HIDDEN = "#cfd5dc"
    COLOR_TEXT = "#1a1a1a"

    # Sort: Tier 1 first by cadence desc, then Tier 2 with cadence, then Tier 2 without
    tier1 = [r for r in rows if r["tier"] == "1_versioned_ballot_driven"]
    tier2_with = [r for r in rows
                  if r["tier"] == "2_continuously_communicated"
                  and r["visible_cadence_versions_per_year"] is not None]
    tier2_without = [r for r in rows
                     if r["tier"] == "2_continuously_communicated"
                     and r["visible_cadence_versions_per_year"] is None]
    tier1.sort(key=lambda r: r["visible_cadence_versions_per_year"], reverse=True)
    tier2_with.sort(key=lambda r: r["visible_cadence_versions_per_year"], reverse=True)
    ordered = tier1 + tier2_with + tier2_without

    labels = []
    values = []
    colors = []
    annotations = []

    for r in ordered:
        labels.append(r["regime_name"])
        v = r["visible_cadence_versions_per_year"]
        if v is None:
            values.append(0.3)  # tiny visible bar to anchor the label
            if r["tier"] == "1_versioned_ballot_driven":
                colors.append(COLOR_TIER1_MED)
            else:
                colors.append(COLOR_TIER2_HIDDEN)
            annotations.append("data incomplete — see methodology")
        elif r["tier"] == "1_versioned_ballot_driven":
            values.append(v)
            colors.append(COLOR_TIER1_FAST)
            annotations.append(f"{v:.2f} versions/yr (complete change rate)")
        else:
            values.append(v)
            colors.append(COLOR_TIER2_VISIBLE)
            annotations.append(f"{v:.2f} versions/yr (visible floor; see note)")

    fig, ax = plt.subplots(figsize=(11.0, 5.0))
    bars = ax.barh(labels, values, color=colors, edgecolor="white", linewidth=0.6)

    max_val = max(values) if values else 1
    for i, (v, ann, r) in enumerate(zip(values, annotations, ordered)):
        text_color = "#444444" if r["tier"] == "2_continuously_communicated" else "#222222"
        style = "italic" if r["visible_cadence_versions_per_year"] is None else "normal"
        ax.text(v + max_val * 0.015, i, ann, va="center",
                fontsize=8.5, color=text_color, style=style)

    ax.set_xlabel("Versions per year (where computable; interpretation depends on tier)")
    ax.set_title(
        "Release cadence by regime — two change-propagation tiers",
        loc="left",
        pad=14,
    )

    # Tier divider
    if tier1 and (tier2_with or tier2_without):
        divider_y = len(tier1) - 0.5
        ax.axhline(divider_y, color="#999999", linewidth=0.6, linestyle=":")
        # Tier band labels at the right edge of the plot, vertically centered in each band
        if tier1:
            tier1_center = (len(tier1) - 1) / 2
            ax.text(max_val * 1.42, tier1_center,
                    "TIER 1\nversioned\nballot-driven\nV ≈ change rate",
                    fontsize=8, color=COLOR_TIER1_FAST, fontweight="bold",
                    ha="left", va="center", linespacing=1.3)
        if tier2_with or tier2_without:
            tier2_center = len(tier1) + (len(tier2_with) + len(tier2_without) - 1) / 2
            ax.text(max_val * 1.42, tier2_center,
                    "TIER 2\ncontinuously\ncommunicated\nV is a floor",
                    fontsize=8, color="#5a6878", fontweight="bold",
                    ha="left", va="center", linespacing=1.3)

    # Generous right margin so neither the annotation nor the tier label clip
    ax.set_xlim(0, max_val * 1.65)
    ax.invert_yaxis()
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    fig.text(
        0.5, -0.04,
        "Tier 2 regimes communicate normative changes via m.d.s.policy, CCADB, GitHub repos, blog posts, "
        "developer documentation, and direct correspondence with CAs. Versioned policy releases are periodic "
        "codifications, not the unit of change. Applying H(R) to Tier 2 regimes using only version cadence "
        "would systematically underestimate burden by an unknown but large factor.",
        ha="center", fontsize=8, color="#555555", wrap=True,
    )

    fig.tight_layout()
    out = FIG_DIR / "fig6_per_regime_cadence.pdf"
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig6_per_regime_cadence.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Wrote: {out}")


def main():
    rows = compute_per_regime_cadence()
    write_table(rows)
    make_figure(rows)
    print()
    print("Per-regime cadence summary:")
    print("-" * 78)
    for r in rows:
        v = r["visible_cadence_versions_per_year"]
        tier = "T1" if r["tier"] == "1_versioned_ballot_driven" else "T2"
        if v is not None:
            print(f"  [{tier}] {r['regime_name']:<55} {v:>5.2f} versions/yr")
        else:
            print(f"  [{tier}] {r['regime_name']:<55} {'  --':>5} ({r['status']})")
    print()
    print("Tier 1 (CABF, versioned + ballot-driven): version cadence = change rate.")
    print("Tier 2 (root programs): version cadence is a floor; primary channels are non-versioned.")


if __name__ == "__main__":
    main()
