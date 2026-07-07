# InsuranceStudy Research Workspace

This repository is organized as a multi-project research workspace. Each project
has its own code, documentation, lightweight outputs, and a GitHub-friendly data
metadata layer.

Large raw downloads, intermediate panels, Parquet files, ZIP archives, and other
bulky rebuildable artifacts are intentionally kept out of Git. For each project,
`data_metadata/` provides enough structure for reviewers to inspect dataset
coverage, variables, missingness, row counts, and observed value distributions
without cloning large data files.

## Projects

| Folder | Topic | Current use |
| --- | --- | --- |
| `projects/insurance_churn_unwinding/` | SIPP and CMS Medicaid unwinding coverage churn | Diagnostic and risk-first insurance coverage project |
| `projects/aca_zero_premium_turnover/` | ACA zero-premium plan turnover / Drake-style replication | Reproducible working snapshot with processed audit files |
| `projects/988_telecom_fee_crisis_performance/` | 988 telecom fee funding and crisis-line performance | Exploratory policy-audit evidence |
| `projects/ccbhc_expansion_capacity/` | CCBHC Medicaid Demonstration expansion and behavioral-health capacity | Monitoring package, no-go for causal paper with current public data |
| `projects/nursing_home_staffing_reporting/` | CMS nursing-home staffing transparency and rating changes | Staffing behavior analysis with weak current causal design |

## Data Metadata

Every project has:

- `data_metadata/dataset_inventory.csv`: one row per profiled data file, with
  format, file size, row count where available, column count, and profiling
  status.
- `data_metadata/variable_catalog.csv`: one row per variable, with dtype,
  missingness, uniqueness, numeric summaries where applicable, and the most
  common observed value.
- `data_metadata/categorical_top_values.csv`: the top observed values for each
  variable in the profiled rows.
- `data_metadata/README.md`: generation notes for that project's metadata.

For large source files, metadata summaries use a sample of rows while preserving
file-level row counts where feasible. This keeps the repository reviewable on
GitHub while avoiding raw-data and large-derived-file commits.

## Repository Rules

- Commit scripts, reports, source inventories, logs, compact tables, figures,
  and data metadata.
- Do not commit raw downloads, large intermediate data, Parquet files, ZIP
  archives, or cache files.
- Use each project's README and report folder as the human-readable entrypoint.
- Use `tools/build_data_metadata.py` to refresh a project's data metadata after
  rebuilding local data.

Example:

```powershell
python tools\build_data_metadata.py `
  --project-name nursing_home_staffing_reporting `
  --source-root "D:\GlobalHealthPolicy Dropbox\Fan Bowei\nh_staffing\nursing_home_staffing_reporting" `
  --output-root "projects\nursing_home_staffing_reporting\data_metadata"
```
