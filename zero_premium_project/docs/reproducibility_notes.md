# Reproducibility Notes

## Environment

- Python tested in this workspace: `Python 3.14.0`
- Required packages: `requests`, `beautifulsoup4`, `pandas`, `numpy`, `openpyxl`

Install missing packages with:

```bash
python -m pip install requests beautifulsoup4 pandas numpy openpyxl
```

## Run Order

From the project root:

```bash
python scripts/01_download_marketplace_data.py
python scripts/02_inspect_marketplace_files.py
```

The download script writes `data/metadata/data_manifest.csv` and stores raw files under `data/raw/{source_group}/{year}/`. Existing files are reused unless `--force` is passed.

The inspection script regenerates:

- `data/metadata/file_inventory.csv`
- `data/metadata/column_inventory.csv`
- `outputs/sample_rows/`
- `outputs/missingness_summary.csv`
- `outputs/oep_outcome_feasibility.csv`
- `outputs/prototype_join_diagnostics.csv`
- `data/intermediate/prototype_turnover_2023_2024.csv`
- `docs/aca_zero_premium_turnover_data_feasibility.md`

## Expected Runtime And Disk

Expected download size is roughly 700 MB to 1 GB for the selected OEP, Exchange PUF, QHP Landscape, and fallback Health Plan Finder files. Runtime depends on network speed; inspection is chunked and should generally run in minutes on a normal workstation.

## Manual Downloads

No manual download is expected for the files in the manifest. Some manifest rows are expected to fail because Data.HealthCare.gov did not expose the PY2019-PY2021 QHP Landscape direct URL pattern at the time of this audit. CMS Health Plan Finder files are downloaded as the official fallback for those years.
