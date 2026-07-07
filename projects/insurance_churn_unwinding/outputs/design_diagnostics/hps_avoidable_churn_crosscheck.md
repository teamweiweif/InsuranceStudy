# HPS Avoidable Churn Cross-Check

## Purpose

This is a lightweight external cross-check for the candidate chosen in the avoidable-churn burden round.

- chosen candidate: `backlog_automation_index / same`
- HPS window: Weeks 60-63 in 2023
- state-week outcomes are mapped to state-month exposure using the survey end-month
- age restriction: adults 18-64

Week-date mapping source: U.S. Census Bureau 2023 Household Pulse Survey Data Tables page.
https://www.census.gov/data/tables/time-series/demo/hhp/2023.html

## Support

- state-week cells: `204`
- nonmissing candidate exposure cells: `204`
- total respondent weight kept: `791184006.97`

## Summary

| outcome | notes | estimate_or_contrast | direction_flag |
| --- | --- | --- | --- |
| current_medicaid_rate | weighted_state_week_correlation | -0.1534 | expected |
| current_medicaid_rate | high_minus_low_exposure_tertile | -0.0157 | expected |
| uninsured_rate | weighted_state_week_correlation | 0.1836 | expected |
| uninsured_rate | high_minus_low_exposure_tertile | 0.0111 | expected |
| public_coverage_rate | weighted_state_week_correlation | -0.1879 | expected |
| public_coverage_rate | high_minus_low_exposure_tertile | -0.0176 | expected |

## Interpretation

- For a burden candidate, lower current Medicaid and higher uninsured are the expected rough directions.
- This is still a repeated-cross-section validation, not a person-level churn design.
- The purpose is only to test whether the candidate exposure has a plausible external echo outside SIPP.
