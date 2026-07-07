# Nursing Home Staffing Reporting Project

This workspace builds a reproducible empirical pipeline for:

**Transparency or Labeling? The Effect of CMS Weekend Staffing and Turnover Reporting on U.S. Nursing Homes.**

## Reproduction

From the project root, run:

```bash
bash script/run_all.sh
```

Equivalent Python sequence:

```bash
python script/00_setup.py
python script/01_acquire_sources.py
python script/02_build_analysis_data.py
python script/03_construct_exposures_outcomes.py
python script/04_descriptive_diagnostics.py
python script/05_main_models.py
python script/06_robustness.py
python script/07_write_report.py
```

The PBJ daily nurse staffing files are streamed from official CMS CSV URLs recorded in `temp/pbj_daily_sources.csv`. Provider Data Catalog nursing-home archive ZIPs are cached under `temp/raw_downloads/provider_archives/`.

## Directory Map

- `data/`: clean analysis-ready Parquet and CSV extracts.
- `script/`: reusable reproduction scripts.
- `result/`: tables, figures, model outputs, diagnostics.
- `report/`: clean human-readable documentation and final report.
- `temp/`: raw downloads, source snapshots, manifests, audit logs, and iteration notes.

## Official Source Families

- CMS Payroll Based Journal Daily Nurse Staffing: https://data.cms.gov/
- CMS Provider Data Catalog nursing-home archive: https://data.cms.gov/provider-data/archived-data/nursing-homes
- CMS QSO-22-08-NH policy memo: https://www.cms.gov/files/document/qso-22-08-nh.pdf
- CMS July 2022 Care Compare/Five-Star updates: https://www.cms.gov/newsroom/fact-sheets/updates-care-compare-website-july-2022

## Notes

The lower-exposure group is not untreated. All Medicare/Medicaid-certified nursing homes were exposed to the national 2022 reporting regime; identification comes from differential exposure intensity measured before 2022.
