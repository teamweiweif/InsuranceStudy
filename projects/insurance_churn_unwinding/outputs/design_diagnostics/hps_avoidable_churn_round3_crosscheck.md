# HPS Avoidable Churn Round-3 Cross-Check

## Purpose

This is a lightweight external cross-check for the top nonlead exposure candidate from the round-3 robustness suite.

- chosen candidate: `backlog_automation_rank_index / same`
- HPS window: Weeks 60-63 in 2023
- state-week outcomes are mapped to state-month exposure using the survey end-month
- age restriction: adults 18-64

## Support

- state-week cells: `204`
- nonmissing candidate exposure cells: `204`
- total respondent weight kept: `791184006.97`

## Summary

| outcome | notes | estimate_or_contrast | direction_flag |
| --- | --- | --- | --- |
| current_medicaid_rate | weighted_state_week_correlation | -0.1963 | expected |
| current_medicaid_rate | high_minus_low_exposure_tertile | -0.018 | expected |
| uninsured_rate | weighted_state_week_correlation | 0.2391 | expected |
| uninsured_rate | high_minus_low_exposure_tertile | 0.0136 | expected |
| public_coverage_rate | weighted_state_week_correlation | -0.2448 | expected |
| public_coverage_rate | high_minus_low_exposure_tertile | -0.0206 | expected |

## Interpretation

- For a burden candidate, lower current Medicaid and public coverage and higher uninsured are the expected rough directions.
- This remains a repeated-cross-section echo, not a person-level churn design.
- The purpose is only to test whether the new top candidate still looks plausible outside SIPP.
