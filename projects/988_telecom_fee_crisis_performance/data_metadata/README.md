# Data Metadata

Generated: 2026-07-07T14:33:57+00:00

Source project root: `D:\GlobalHealthPolicy Dropbox\Fan Bowei\nh_staffing\988_telecom_fee_crisis_performance`

This folder is the GitHub-friendly data audit layer for `988_telecom_fee_crisis_performance`. It is
intended to make the datasets inspectable without committing raw downloads,
large intermediate panels, or bulky Parquet/CSV files.

Files:

- `dataset_inventory.csv`: one row per profiled data file, with format, file
  size, row count where available, column count, and whether the profile used the
  full file or the first 10000 rows.
- `variable_catalog.csv`: one row per variable, with dtype, missingness and
  uniqueness in the profiled rows, numeric summaries when applicable, and the
  most common observed value.
- `categorical_top_values.csv`: top observed values for each variable in the
  profiled rows.

For files larger than 50 MB, row counts are still recorded
when feasible, but distribution summaries are based on the first 10000
rows. For smaller supported files, summaries are full-file profiles.
