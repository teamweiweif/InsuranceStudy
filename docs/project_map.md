# Project Map

## Active Zones

- `scripts/setup/`
  - `bootstrap_packages.R`: installs and verifies packages needed by the active workflow.
- `scripts/qc/`
  - `run_harmonization_checks.R`: runs the harmonization availability and coding checks.
- `scripts/pipeline/`
  - `prepare_pooled_2002_2017.R`: builds the cached pooled dataset in `data/derived/`.
  - `run_rdd_pooled_2002_2017.R`: runs the accepted pooled Medicare@65 analysis.
- `src/features/`
  - harmonization and feature derivation modules used by the current pipeline.
- `src/qc/`
  - source files used by the QC entrypoint.
- `src/utils/`
  - `project_paths.R`: shared project-root and path helpers.

## Data Lineage

- `data/raw/fyc_archives_ssp/`
  - archived `.ssp` public-use downloads used in the earlier conversion workflow.
- `data/raw/fyc_archives_dta/`
  - archived `.dta` zip downloads used for later-year files.
- `data/intermediate/fyc_all_years/`
  - unified yearly `fyc_YYYY.dta` files used by harmonization and pooling.
- `data/derived/`
  - cached pooled datasets for the accepted 2002-2017 workflow.

## Output Policy

- `outputs/rdd_pooled_2002_2017/` is the only current analysis output kept outside `archive/`.
- Earlier single-year output folders were preserved in `archive/legacy_outputs/`.
- `outputs/harmonization_report/` remains active because it is produced by the current QC entrypoint.

## Reference And Archive Policy

- `reference/external/MEPS/` is an external reference repository, not first-party analysis code.
- `archive/legacy_data/` stores superseded data layouts and the 2022-only prototype artifacts.
- `archive/legacy_scripts/` stores retired download, prototype, build-history, setup, and diagnostic scripts.
- `archive/legacy_analysis/` stores older RD pipelines that are no longer current.
- `archive/research_notes/` and `archive/docs_cn/` store notes retained for context, not for active execution.
