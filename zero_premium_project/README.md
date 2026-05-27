# Zero Premium Project

This folder contains a reproducible working snapshot for the ACA zero-premium turnover / Drake-style replication project.

## Current Status

The project is at Step 2 complete: a county-year replication dataset for 2022-2024 has been built and validated. The documented status is a conditional go for Step 3 descriptive replication and non-causal comparison.

Main status files:

- `docs/drake_replication_dataset_report.md`
- `docs/step2_progress_and_limitations.md`
- `logs/step2_build.log`
- `logs/step2_validation.log`

## Included

- `scripts/`: download, inspection, dataset construction, and validation scripts.
- `docs/`: feasibility, reproducibility, and Step 2 progress documentation.
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

The zero-premium measure is a benchmark-based low-income age-40 proxy, not exact household-specific net premium. Public PUFs do not support individual-level retention or household-specific APTC calculation. Nebraska is excluded from the primary sample and provided only as a sensitivity output.
