"""
Build the academic-style methodology paper.

Reads:
  - papers/compliance-burden-index/cbi.tex         (source)
  - results/figures/*.pdf                          (figures, must exist already)

Writes:
  - papers/compliance-burden-index/cbi.pdf         (final)
  - papers/compliance-burden-index/build/*.aux/log (intermediate; gitignored)

Determinism notes:
  - SOURCE_DATE_EPOCH is set to the snapshot date so embedded timestamps are stable.
  - pdflatex is invoked with -interaction=nonstopmode and a fixed -output-directory
    so no interactive prompts can vary by environment.
  - Two passes are run for cross-references, but only if the .tex source is present.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from model.meta import get_snapshot_date, get_version  # noqa: E402

PAPERS_DIR = REPO_ROOT / "papers" / "compliance-burden-index"
TEX_SOURCE = PAPERS_DIR / "cbi.tex"
BUILD_DIR = PAPERS_DIR / "build"
FIGURES_DIR = REPO_ROOT / "results" / "figures"


def _check_figures():
    """Verify all figures referenced in the paper exist."""
    required = [
        "fig1_capacity_ratio_trajectory.pdf",
        "fig2_corpus_growth.pdf",
        "fig3_per_persona_ratios.pdf",
        "fig4_team_decomposition.pdf",
        "fig5_sensitivity_heatmap.pdf",
        "fig5b_phi_sensitivity.pdf",
        "fig6_per_regime_cadence.pdf",
        "fig7_regime_workload_grid.pdf",
        "fig8_relevant_dates_calendar.pdf",
        "fig9_stack_change_burden.pdf",
        "fig10_cabf_stack_fte.pdf",
    ]
    missing = [f for f in required if not (FIGURES_DIR / f).exists()]
    if missing:
        print(
            "ERROR: missing figures (run the figure scripts first):",
            file=sys.stderr,
        )
        for f in missing:
            print(f"  {FIGURES_DIR / f}", file=sys.stderr)
        sys.exit(1)


def _epoch_for_snapshot() -> str:
    """Convert the snapshot date into a SOURCE_DATE_EPOCH value (UTC midnight)."""
    snap = get_snapshot_date()
    import datetime as _dt
    dt = _dt.datetime(snap.year, snap.month, snap.day, tzinfo=_dt.timezone.utc)
    return str(int(dt.timestamp()))


def _run_pdflatex(pass_num: int) -> None:
    """Run one pass of pdflatex with deterministic environment."""
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = _epoch_for_snapshot()

    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={BUILD_DIR}",
        str(TEX_SOURCE.name),
    ]
    print(f"  Pass {pass_num}: pdflatex {TEX_SOURCE.name}", flush=True)
    result = subprocess.run(
        cmd,
        cwd=str(PAPERS_DIR),
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Print the last 60 lines of the log for diagnosis
        print("pdflatex failed. Tail of output:", file=sys.stderr)
        for line in result.stdout.splitlines()[-60:]:
            print(line, file=sys.stderr)
        print("--- stderr ---", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    if not TEX_SOURCE.exists():
        print(f"ERROR: source missing: {TEX_SOURCE}", file=sys.stderr)
        sys.exit(2)

    if shutil.which("pdflatex") is None:
        print("ERROR: pdflatex not found on PATH. Install TeX Live.", file=sys.stderr)
        sys.exit(3)

    _check_figures()

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Building paper for v{get_version()} (snapshot {get_snapshot_date()})")
    print(f"  Source:  {TEX_SOURCE}")
    print(f"  Build:   {BUILD_DIR}")
    print(f"  Figures: {FIGURES_DIR}")

    # Two passes for cross-references (\ref / \label).
    _run_pdflatex(1)
    _run_pdflatex(2)

    built_pdf = BUILD_DIR / TEX_SOURCE.with_suffix(".pdf").name
    final_pdf = PAPERS_DIR / TEX_SOURCE.with_suffix(".pdf").name

    if not built_pdf.exists():
        print(f"ERROR: expected output not produced: {built_pdf}", file=sys.stderr)
        sys.exit(4)

    shutil.copy2(built_pdf, final_pdf)
    print(f"Wrote: {final_pdf}")


if __name__ == "__main__":
    main()
