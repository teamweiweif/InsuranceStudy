# 988 Telecom Fee Crisis-Line Performance

This workspace evaluates whether state 988 telecom fee funding is associated with improved 988 crisis-line performance using official state-month KPI PDFs, FCC 988 fee accountability reports, and Census denominators.

## Reproduce

From this folder:

```powershell
powershell -ExecutionPolicy Bypass -File script/run_all.ps1
```

Or run the Python scripts in order from `script/00_setup.py` through `script/10_write_report.py`.

## Current Data Coverage

- KPI source months parsed: 58 monthly PDFs, 2021-07-01 through 2026-05-01. The source index snapshot did not list February 2025.
- Jurisdictions in raw KPI panel: 56.
- Primary state/DC sample rows: 2936 across 51 jurisdictions.
- FCC-confirmed state fee collectors by calendar 2024: 9.

## Official Sources

- [988 Lifeline State-based Monthly Reports](https://988lifeline.org/professionals/our-network/state-based-monthly-reports/)
- [SAMHSA 988 Performance Metrics](https://www.samhsa.gov/mental-health/988/performance-metrics)
- [FCC 988 Fee Reports and Reporting](https://www.fcc.gov/988-fee-reports-and-reporting)
- [Census state resident population estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-state-total.html)

## Key Outputs

- `data/analysis_panel_state_month.parquet`: merged analysis panel.
- `data/treatment_timing_state.csv`: policy timing audit.
- `result/main_twfe_models.csv`: fixed-effect treatment checks.
- `result/cs_overall_att.csv`: not-yet-treated cohort ATT estimates.
- `report/final_report.md`: empirical write-up.
- `report/go_no_go_assessment.md`: decision assessment.
