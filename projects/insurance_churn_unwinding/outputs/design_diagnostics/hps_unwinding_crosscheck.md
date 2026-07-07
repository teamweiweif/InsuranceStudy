# HPS Unwinding Cross-Check

## Purpose

This is a deliberately lightweight external validation screen. It does not attempt to reproduce the SIPP transition design.

- chosen exposure from second-round gate: `manual_renewal_burden / renewal_form_rate / lag1`
- HPS window used here: Weeks 60-63 in 2023
- state-week outcomes are mapped to monthly CMS exposure using the survey end-month
- weights: `PWEIGHT`
- age restriction: adults 18-64

Week-date mapping source: U.S. Census Bureau 2023 Household Pulse Survey Data Tables page.
https://www.census.gov/data/tables/time-series/demo/hhp/2023.html

## Support

- state-week cells: `204`
- state-week cells with nonmissing exposure: `203`
- total respondent weight across kept cells: `791184006.97`

## Summary

| outcome | statistic | value | sign |
| --- | --- | --- | --- |
| current_medicaid_rate | weighted_state_week_correlation | -0.0757 | negative |
| current_medicaid_rate | high_minus_low_exposure_tertile | -0.0069 | negative |
| uninsured_rate | weighted_state_week_correlation | -0.0032 | negative |
| uninsured_rate | high_minus_low_exposure_tertile | -0.0018 | negative |
| public_coverage_rate | weighted_state_week_correlation | -0.1397 | negative |
| public_coverage_rate | high_minus_low_exposure_tertile | -0.0154 | negative |

## Interpretation

- `current_medicaid_rate` should move negative if higher manual-renewal burden is associated with more current coverage loss.
- `uninsured_rate` should move positive if the same burden also shows up as loss into no coverage.
- `public_coverage_rate` is included as a looser cross-check because HPS public coverage is broader than Medicaid.

## Limits

- HPS is a repeated cross-section, not a person-month panel.
- This cross-check uses late-2023 weeks only, so support is much thinner than the SIPP design.
- The month mapping is mechanical and should not be overinterpreted as a clean event-study alignment.
- The validation is only meant to show whether the selected SIPP signal is completely isolated or has a rough echo in another public source.
