# Contributing

This repository is a research artifact maintained by Systematic Reasoning, Inc. The methodology direction is set by the maintainer. Pull requests are welcome and reviewed on the following terms.

## Welcome contributions

- Bug reports for the model implementation, scripts, or paper build.
- Data corrections, particularly to the per-section change records under `data/cabf_*_per_change_records.csv` (with citation to the source of correction).
- Additional ingestion sources for Tier 2 regimes (Mozilla, Chrome, Apple, Microsoft) per the roadmap.
- Test coverage improvements.
- Documentation clarifications.

## Out of scope without prior discussion

- Changes to the methodology framing, formula structure, or persona model. These are part of the research direction and are evolved deliberately across releases. File an issue describing the proposed change before opening a PR.
- Headline parameter changes (τ, τ_decay, φ central values). These are calibrated against external evidence and changing them requires evidence-of-change documentation.
- Adding new regimes to the CABF stack analysis. The data ingestion path is being automated separately (see Open Data Work item 1 in the README).

## Process

1. Open an issue describing the change.
2. Wait for maintainer response before investing significant effort.
3. Submit a PR referencing the issue.
4. CI must pass (`pytest tests/` and the paper build).
5. The PR description should explain how the change preserves or modifies the headline numbers and which sections of the methodology are affected.

## Code style

- Python: PEP 8, type hints where they aid clarity.
- LaTeX: avoid em-dashes and AI-tell phrasing; the paper voice is benchmarked against unmitigatedrisk.com.
- Data: CSV with explicit headers and provenance columns (`source_url`, `extraction_method`, `tabulated_date`).

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Interactions in issues and pull requests follow the Contributor Covenant.
