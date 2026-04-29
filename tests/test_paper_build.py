"""Smoke tests for the academic paper build pipeline.

These tests verify the build script's wiring (figure inventory, source
presence, version stamping) without requiring pdflatex on every CI runner.
The actual PDF build is exercised in CI, where LaTeX is installed.
"""

import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PAPER_DIR = REPO_ROOT / "papers" / "compliance-burden-index"
TEX_SOURCE = PAPER_DIR / "cbi.tex"
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build_paper.py"

REQUIRED_FIGURES = [
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


def test_paper_source_present():
    """The LaTeX source must be checked in."""
    assert TEX_SOURCE.exists(), f"missing source: {TEX_SOURCE}"
    assert TEX_SOURCE.stat().st_size > 1000, "source file is suspiciously small"


def test_build_script_present():
    """The paper build script must be present and runnable."""
    assert BUILD_SCRIPT.exists()
    text = BUILD_SCRIPT.read_text()
    assert "pdflatex" in text
    assert "SOURCE_DATE_EPOCH" in text, "build script must set deterministic timestamp"


def test_paper_references_all_figures():
    """The paper must reference every figure produced by the pipeline."""
    text = TEX_SOURCE.read_text()
    for fig in REQUIRED_FIGURES:
        assert fig in text, f"paper does not reference {fig}"


def test_paper_version_consistency():
    """The paper title block must match VERSION."""
    version = (REPO_ROOT / "VERSION").read_text().strip()
    text = TEX_SOURCE.read_text()
    # The version appears in the title block (e.g., "Methodology v0.3.4")
    assert f"v{version}" in text, (
        f"paper does not reference current version v{version}"
    )


def test_paper_no_forbidden_terms_in_body():
    """Sanity check: the paper does not name the company's product."""
    text = TEX_SOURCE.read_text().lower()
    forbidden = ["forgeiqx", "forge iq"]
    for term in forbidden:
        assert term not in text, f"paper must not mention {term!r}"


def _have_pdflatex() -> bool:
    return shutil.which("pdflatex") is not None


def _have_figures() -> bool:
    fig_dir = REPO_ROOT / "results" / "figures"
    return all((fig_dir / f).exists() for f in REQUIRED_FIGURES)


@pytest.mark.skipif(not _have_pdflatex(), reason="pdflatex not installed")
@pytest.mark.skipif(
    not _have_figures(),
    reason="figures not present; run the figure scripts first or rely on CI",
)
def test_paper_builds():
    """If pdflatex is available and figures are present, verify the paper builds."""
    import subprocess

    # Run the build script.
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"build_paper.py failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    pdf = PAPER_DIR / "cbi.pdf"
    assert pdf.exists()
    # Sanity-size: the paper has 10 figures, so the PDF should be substantial.
    assert pdf.stat().st_size > 100_000, "paper PDF is suspiciously small"
