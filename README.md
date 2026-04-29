# Compliance Burden Index

> A reproducible scenario model for estimating the analyst capacity required to maintain operationally useful understanding of a changing normative corpus.

This repository computes the **Knowledge Currency Budget**: the per-persona hours per year required to sustain working accuracy on a normative corpus, given observed corpus size, change cadence, and decay parameters drawn from cognitive-science literature. It then translates that burden into a *capacity ratio* against the time plausibly available for currency-maintenance under realistic role definitions, and into *person-year equivalents* under three capacity bases.

## Headline (v0.1, snapshot 2026-04-28)

**Single-regime measurement (CA/Browser Forum TLS Baseline Requirements).** Observed cadence window 2025-08-25 to 2026-03-31 (10 versions, 139 changes), seven CA personas, central scenario:

| Quantity | Value |
|---|---|
| Team currency-maintenance burden | 850 h / yr |
| Team allocated capacity | 1,012 h / yr |
| **Team capacity ratio** | **0.84×** |

**Two of seven personas exceed the model-implied capacity-deficit threshold of 1.0×:** CPS owner at 1.27× (309 h / 243 h); audit liaison at 1.12× (182 h / 162 h).

**Multi-regime CABF stack measurement.** Five CABF Tier 1 regimes with ingested cadence and change counts:

| Regime | V/yr | E/yr | Team change-handling burden (h/yr) |
|---|---|---|---|
| TLS BR | 16.74 | 232.7 | 696 |
| Network Security Requirements | 3.51 | 84.2 | 248 |
| EV Guidelines (transition baseline) | 0.99 | 71.4 | 208 |
| S/MIME BR | 5.76 | 33.4 | 105 |
| Code Signing BR | 1.54 | 14.7 | 45 |

**Steady-state CABF stack (4 regimes excluding EV transition): ~1,094 h/yr** of change-handling burden, before any baseline corpus reading. Adding the EV Guidelines transition baseline brings the total to ~1,302 h/yr. Sensitivity envelope: 421–3,054 h/yr.

## What 1,094 h/yr means in person-time

Three capacity bases give three lenses on the same number:

| Basis | Hours/year | Person-year equivalents |
|---|---|---|
| Nominal FTE (2,080 h, no PTO/sick/training) | 1,094 | **0.53 FTE** |
| Realistic focused-expert (1,500 h, after meetings/interruption recovery) | 1,094 | **0.73 FTE** |
| Model-allocated team currency capacity (1,012 h) | 1,094 | **1.08 team-equivalents** |

The number measures *the cost of staying current* — knowing what changed, what it means, who it affects, what needs to be done. It does **not** measure the cost of doing the resulting compliance work (engineering changes, CPS edits, audit support, incident response, customer assurance). In practice the burden is fragmented across CPS ownership, validation interpretation, audit liaison, root program coordination, and engineering — not one person sitting in a chair, but the equivalent of one scarce senior person's annual capacity spread across the team.

## Two tiers of regimes

The TLS BRs are one regime out of more than ten that govern a publicly-trusted CA. Two distinct change-propagation models are present, and *H(R)* applies cleanly to one of them and not the other:

**Tier 1 — versioned, ballot-driven.** CA/Browser Forum documents. Version cadence equals change rate; per-version edits are auditable from redlines. *H(R)* applies directly. Applied to TLS BR, S/MIME BR, NetSec, EV Guidelines, and Code Signing BR (above).

**Tier 2 — continuously communicated.** Root programs. Versioned policy is a periodic snapshot of decisions communicated through other channels: m.d.s.policy and CCADB (Mozilla); GitHub repo and blog (Chrome); developer documentation and root program email (Apple); TechCommunity and KB articles (Microsoft). Counting versions to estimate change rate is a category error. We do not compute *H(R)* for Tier 2 in v0.1; visible cadence is reported as a floor.

| Regime | Tier | Visible cadence (versions/yr) |
|---|---|---|
| CA/Browser Forum TLS BR | 1 | 16.74 |
| CA/Browser Forum S/MIME BR | 1 | 5.76 |
| CA/Browser Forum NetSec | 1 | 3.51 |
| CA/Browser Forum Code Signing BR | 1 | 1.54 |
| CA/Browser Forum EV Guidelines | 1 | 0.99 |
| Chrome Root Program Policy | 2 | 3.56 (floor) |
| Mozilla Root Store Policy | 2 | 1.30 (floor) |
| Apple Root Certificate Program | 2 | data insufficient |
| Microsoft Trusted Root Program | 2 | data insufficient |

See `methodology/methodology.md` §9 for the full regime stack inventory and the lower-bound argument.

## What this index claims, and what it does not

This index does not claim that individual analysts are failing to do their jobs. It claims that under the model's stated assumptions, currency-maintenance burden for the audit-centric model exceeds the time plausibly available within the role distribution that the model assumes. Real CAs sustain operational function through specialization, triage, delegation, lowered effective working accuracy, selective attention, and other compensating mechanisms. Each compensation carries a cost that the audit model does not recognize because the model assumes the working-accuracy premise is met. The model-implied capacity deficit is the finding.

The CABF subset of the regime stack is, by construction, a lower bound on the full-stack burden. Tier 2 root programs, ETSI, WebTrust, IETF RFCs, NIST cryptographic policy, and the CA's own CPS reconciled against all of the above are not yet quantified.

## Repository structure

```
.
├── VERSION                                        Single source of truth for methodology version
├── methodology/
│   └── methodology.md                             Full methodology document
├── data/
│   ├── cabf_tls_br_corpus.csv                     Per-version corpus measurements (TLS BR)
│   ├── cabf_tls_br_observed_window.csv            Observed-window cadence aggregate
│   ├── cabf_tls_br_observed_window_versions.csv   Per-version dates within the observed window
│   ├── cabf_tls_br_per_change_records.csv         Per-section change records (50 of 139, partial)
│   ├── cabf_tls_br_relevant_dates.csv             Calendar of scheduled propagation events
│   ├── cabf_smime_br_observed_window.csv          S/MIME BR observed window
│   ├── cabf_netsec_observed_window.csv            NetSec observed window
│   ├── cabf_evg_observed_window.csv               EV Guidelines observed window
│   ├── cabf_codesigning_br_observed_window.csv    Code Signing BR observed window
│   ├── cabf_*_per_change_records.csv              Per-change stub files (queued for the next release)
│   ├── mozilla_root_store_policy_versions.csv     Mozilla MRSP version history
│   ├── chrome_root_program_policy_versions.csv    Chrome RPP version history
│   ├── regime_registry.csv                        Canonical regime inventory
│   └── regime_stack_state.csv                     Multi-regime tracking state with tier classification
├── model/
│   ├── budget.py                                  Knowledge Currency Budget implementation
│   ├── data_io.py                                 CSV loading utilities
│   ├── meta.py                                    Version and snapshot-date loaders
│   ├── parameters.yaml                            Citation-anchored parameters with evidence grades
│   └── snapshot.yaml                              Snapshot date (canonical, used by all scripts)
├── scripts/
│   ├── compute_headline.py                        TLS BR per-persona, capacity ratios, historical trajectory
│   ├── make_figures.py                            Figs 1-5 (TLS BR specific)
│   ├── per_regime_cadence.py                      Fig 6 (two-tier cadence comparison)
│   ├── per_regime_workload.py                     Figs 7-8 (multi-dimensional workload)
│   ├── stack_change_burden.py                     Fig 9 (CABF stack burden)
│   ├── cabf_stack_fte.py                          Fig 10 (FTE-equivalent translation)
│   └── build_paper.py                             Builds the academic-style PDF (two-pass pdflatex)
├── papers/
│   └── compliance-burden-index/
│       ├── cbi.tex                                Academic paper source
│       └── cbi.pdf                                Built paper (committed)
├── tests/
│   ├── test_budget.py                             Model test suite
│   └── test_paper_build.py                        Paper-build smoke tests
├── results/                                       Generated; not version-controlled
│   ├── current.json                               Headline numbers (machine-readable)
│   ├── tables/                                    CSV outputs
│   └── figures/                                   PDF and PNG figures
├── .github/workflows/recompute.yml                CI pipeline (regenerates outputs from versioned inputs; does NOT fetch upstream)
├── requirements.txt
├── .gitignore
└── README.md
```

## Reproducing

```
pip install -r requirements.txt
python scripts/compute_headline.py
python scripts/per_regime_cadence.py
python scripts/per_regime_workload.py
python scripts/stack_change_burden.py
python scripts/cabf_stack_fte.py
python scripts/make_figures.py
python scripts/build_paper.py        # requires pdflatex; produces papers/compliance-burden-index/cbi.pdf
pytest tests/
```

All scripts are deterministic. Every empirical input is loaded from `data/`. Every model parameter is loaded from `model/parameters.yaml`. The methodology version is loaded from `VERSION`. The snapshot date is loaded from `model/snapshot.yaml`. No values are embedded in script source. The paper build sets `SOURCE_DATE_EPOCH` from the snapshot date so the embedded PDF timestamp is stable across rebuilds.

## Paper

The academic-style methodology document is at `papers/compliance-burden-index/cbi.pdf` (built from `cbi.tex`). It is the same content as `methodology/methodology.md` rendered in publication form, with the figures inline at appropriate places, a Known Data Gaps callout block at the top, a references section, and a methodology change log appendix. The PDF is committed; CI rebuilds it on every push and verifies it stays in sync with the figure set.

## Roadmap

- **v0.1 (current).** Initial public release. Full CABF stack at per-section per-change provenance (380 records across TLS BR, S/MIME BR, NetSec, Code Signing BR, EV Guidelines). Two-tier regime classification, seven-persona team budget with capacity stack and FTE translation, sensitivity analysis across τ, τ_decay, and φ, eleven figures, academic-style PDF, and a CI pipeline that regenerates outputs from versioned inputs.
- **v0.2.** Hand-classified φ from labeled change sample (the 380 records make this unblocked). Direct PDF re-extraction of corpus measurements with full provenance metadata. Regime-specific persona engagement weights replacing TLS-shaped weights for non-TLS regimes. Partner-CA persona calibration where possible.
- **v0.3.** First Tier 2 *H(R)* computation: ingest m.d.s.policy thread classification for Mozilla MRSP. Add corpus measurements for Mozilla, Chrome RPP. Cross-regime coupling term.
- **v0.4.** ETSI / WebTrust / Apple / Microsoft / NIST / eIDAS / NIS2. Compute aggregate H_total across the full regime stack. Monte Carlo uncertainty propagation in place of discrete low/central/high.
- **v0.5+.** Extension to non-PKI regimes (FDA medical device, financial services, others).


## Open data work

These are infrastructure tasks for the data layer, separate from the methodology evolution in the roadmap above.

1. **Automate CABF ingestion.** Replace manual paste of CPS Dev App pages with a scripted pull (`scripts/ingest_cabf.py`). Pulls observed-window aggregate counts, per-section change records, and per-version corpus measurements for all five CABF regimes. Runs as an opt-in CI step (`workflow_dispatch` trigger only) so deterministic default builds are preserved. Authentication via repo secrets since the dev app is private.

2. **Uniform corpus and complexity metrics across CABF regimes.** The current model uses per-version word counts and RFC 2119 keyword counts only for TLS BR (`data/cabf_tls_br_corpus.csv`); the multi-regime stack burden of 1,094 h/yr excludes baseline corpus reading for the four other regimes and is therefore a lower bound on the actual stack burden. Closing this gap requires per-version word count, requirement count (MUST/SHALL/SHOULD/MAY/MUST NOT/SHALL NOT), and (ideally) per-section size for S/MIME BR, NetSec, Code Signing BR, and EV Guidelines. Once ingested, the model uses them automatically; no code change required beyond the data files.

3. **Tier 2 ingestion path.** Mozilla, Chrome, Apple, and Microsoft root program changes propagate through channels other than versioned policy releases: m.d.s.policy threads + Bugzilla + CCADB for Mozilla; the Chrome Root Program GitHub repo + blog posts + CABF ballot positions for Chrome; developer documentation + email for Apple; TechCommunity posts + KB articles for Microsoft. The CABF pipeline does not address these. A separate ingestion path is needed before Tier 2 *H(R)* can be computed in v0.3.


## Methodology versioning

Every published number is tagged to the methodology version that produced it. Methodology changes are tracked in §12 of the methodology document. Numbers from one methodology version are not directly comparable to numbers from another without explicit reconciliation.

## Citation

> Systematic Reasoning, Inc. *Compliance Burden Index*, v0.1, snapshot 2026-04-28. https://github.com/systematicreasoning/compliance-burden-index
