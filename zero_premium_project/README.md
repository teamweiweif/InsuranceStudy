# Zero Premium Project

This folder contains a reproducible working snapshot for the ACA zero-premium turnover / Drake-style replication project.

## Current Status

Step 3 descriptive replication diagnostics have been rerun against Drake et al. and the paper supplement. The raw Step 2 primary sample remains 6,564 county-years / 2,188 counties, but Step 3 now applies Drake supplement eTable 3 county exclusions and writes a Drake-harmonized sample with 6,477 county-years / 2,159 counties:

- `data/processed/drake_replication_primary_drake_harmonized_2022_2024.csv`

Outcome descriptives closely reproduce Drake Table 1. The current judgment is **Fix Step 2 before Step 4** because treatment construction remains proxy-based, across-insurer turnover is under-detected relative to Drake, and 2021 enrollment weights / bronze spread / insurer-count controls are not yet retained in the current processed files.

`scripts/03_build_drake_replication_dataset.py` has been updated to produce those Step 2 repair fields on the next full raw-data rebuild. The current processed datasets were not rebuilt from raw files in this pass because `data/raw/` is intentionally excluded from the repo.

Main status files:

- `docs/drake_replication_dataset_report.md`
- `docs/step2_repair_implementation_notes.md`
- `docs/step3_descriptive_replication_report.md`
- `docs/step3_progress_and_limitations.md`
- `docs/step2_progress_and_limitations.md`
- `literature/README.md`
- `logs/step3_descriptive_replication.log`
- `logs/step2_build.log`
- `logs/step2_validation.log`

## Included

- `scripts/`: download, inspection, dataset construction, and validation scripts.
- `docs/`: feasibility, reproducibility, and Step 2 progress documentation.
- `literature/`: Drake et al. article and supplementary material used for replication audit.
- `logs/`: Step 2 build and validation logs.
- `outputs/`: compact diagnostics and validation CSVs.
- `data/metadata/`: manifests, inventories, and sample definition metadata.
- `data/processed/`: final county-year replication datasets.

## Excluded

The raw CMS/Data.HealthCare.gov downloads are intentionally not committed:

- `data/raw/`
- `data/intermediate/`
- `outputs/sample_rows/`
- Python cache files

Raw files are large public downloads and should be regenerated from the scripts when needed. Intermediate files are derived and can be rebuilt. `outputs/sample_rows/` is omitted because it is optional inspection output with very long generated filenames.

## Reproducibility

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

See `docs/reproducibility_notes.md` for the initial download and inspection workflow. The Step 2 dataset was generated with:

```bash
python scripts/03_build_drake_replication_dataset.py
python scripts/04_validate_drake_replication_dataset.py
```

## Data Caveats

The zero-premium measure is a benchmark-based low-income age-40 proxy, not exact household-specific net premium. Public PUFs do not support individual-level retention or household-specific APTC calculation. Nebraska is excluded from the primary sample and provided only as a sensitivity output. Step 3 uses a Drake-harmonized sample for descriptive diagnostics, but the raw Step 2 sample is preserved for auditability.
