# Data files

This directory holds the empirical inputs to the Compliance Burden Index. Outputs are written to `results/`, not here.

## Per-change record files

Files of the form `cabf_*_per_change_records.csv` hold per-section change records for each CABF regime. Schema:

| Column | Meaning |
|---|---|
| `version` | Version that introduced the change (e.g. `v2.2.6`) |
| `section` | Section number affected (e.g. `7.1.2.7.7`) |
| `type` | `added` / `removed` / `changed` |
| `description_snippet` | Short human-readable description |
| `tabulated_date` | Date the record was extracted into this CSV |

### Ingestion status as of v0.1

| Regime | File | Records | Status |
|---|---|---|---|
| TLS BR | `cabf_tls_br_per_change_records.csv` | **139 of 139 (complete)** | full per-section provenance for v2.1.7 → v2.2.6 observed window |
| S/MIME BR | `cabf_smime_br_per_change_records.csv` | **29 of 29 (complete)** | full per-section provenance for v1.0.9 → v1.0.13 |
| NetSec | `cabf_netsec_per_change_records.csv` | **48 of 48 (complete)** | full per-section provenance for v2.0.4 → v2.0.5 |
| Code Signing BR | `cabf_codesigning_br_per_change_records.csv` | **19 of 19 (complete)** | full per-section provenance for v3.9.0 → v3.10.0 |
| EV Guidelines | `cabf_evg_per_change_records.csv` | **145 of 145 (complete)** | full per-section provenance for v2.0.0 → v2.0.1 restructure window; concentrated in Appendix H Registration Schemes and §3.2.2.x identity-verification sections |

All five CABF regimes now have complete per-section provenance, totaling 380 fully-classified change records.

Note on Code Signing BR version notation: 16 of 19 records carry `version=v3.x.0` and 3 carry `version=v3.10.0`, preserving the CPS Dev App's source notation. All 19 changes occur in the v3.9.0 → v3.10.0 transition; the `v3.x.0` form is the dev-app draft notation for the same release.

Where per-change records are complete, downstream calibration work (substantive-vs-editorial classification of φ, regime-specific persona engagement weights) can begin without further upstream ingestion. Where per-change records are partial or absent, aggregate counts (added / removed / modified totals) are still available in the corresponding `*_observed_window.csv` file, which is the input the model uses for the headline numbers.

Some TLS BR records reflect repeated change events on the same section across consecutive ballots (for example, Appendix B onion-verification methods added and removed across v2.2.5 and v2.2.6). These are not scrape duplicates; each row is a distinct change event in the upstream ballot record.


## Observed-window files

Files of the form `cabf_*_observed_window.csv` hold the cadence-and-aggregate-changes input that the model uses. One row per regime, summarizing a measurement window. The TLS BR file additionally has a per-version sidecar (`cabf_tls_br_observed_window_versions.csv`) for the within-window cadence breakdown.

## Regime registry

`regime_registry.csv` and `regime_stack_state.csv` are the canonical regime inventory. The registry holds metadata (corpus measurement status, cadence measurement status, change measurement status). The state file holds tier classification and per-regime tracking state used by the workload comparison view. These files are the single source of truth for which regimes are in scope and what is known about each.

## Root program version files

`mozilla_root_store_policy_versions.csv`, `chrome_root_program_policy_versions.csv` hold the version histories used to compute Tier 2 cadence floors. Apple and Microsoft do not have version-history files because their actual change communication is through channels other than versioned policy releases (developer documentation, mailing lists, blog posts, KB articles); the regime registry classifies them as Tier 2 with cadence not computable from the upstream version data alone. See methodology §9 for the tier classification.

## Provenance for upstream-tracked regimes

All CABF observed-window CSVs include `provenance` and `extraction_method` columns identifying the source of the tabulated counts. The current source for v0.1 is the CPS Dev App tracking system; per-section ballot-level provenance from the CA/B Forum redline records is the next-release ingestion target.
