# Final Report

## Executive Summary

This project estimates whether CMS's 2022 public reporting and Five-Star rating inclusion of weekend staffing and staff turnover changed nursing-home staffing behavior. The analysis uses 1,209,911 facility-month observations from 15,133 facilities over 84 months. The preferred design compares facilities with high pre-2022 weekend-staffing exposure to lower-exposure facilities, with facility and month fixed effects. The current empirical judgment is: **Weak causal design under current specification**. At least one primary staffing outcome rejects the joint pre-trend null at the 5% level. At least one primary post-July staffing estimate excludes zero. A placebo 2021 timing test is statistically significant, which weakens causal interpretation.

## Policy Background

CMS began public reporting of weekend staffing and staff turnover information on Care Compare in January 2022. In July 2022, CMS incorporated weekend staffing and turnover measures into the Five-Star staffing-domain methodology. The 2024 minimum staffing rule is later context, not the exposure studied here.

## Data Sources and Coverage

- PBJ Daily Nurse Staffing provides facility-day staffing hours and resident census. The pipeline aggregates these data to facility-month and facility-quarter panels from 2019 Q1 through 2025 Q4.
- Provider Data Catalog nursing-home archive snapshots provide facility characteristics, ratings, survey outcomes, penalties, and reported turnover/weekend staffing fields when available.
- HHS OIG reports are used only as policy-salience documentation.

## Outcomes

Primary outcomes are weekend total nurse HPRD, weekend RN HPRD, weekday counterparts, weekend-weekday gaps, total nurse HPRD, RN share, and contract staff share. Ratings and deficiencies are secondary downstream outcomes.

## Exposure and Comparison

High exposure is the top quartile of a pre-2022 composite index based on low weekend total nurse HPRD, low weekend RN HPRD, and a large weekday-weekend staffing gap. Lower-exposure facilities are comparison facilities, not untreated controls.

## Main Results

- weekend_total_nurse_hprd: beta=0.149, SE=0.007, 95% CI [0.135, 0.163], p=0.000, N=1,209,911.
- weekend_rn_hprd: beta=0.059, SE=0.003, 95% CI [0.054, 0.064], p=0.000, N=1,209,911.
- weekday_total_nurse_hprd: beta=0.064, SE=0.009, 95% CI [0.047, 0.082], p=0.000, N=1,209,909.
- weekday_minus_weekend_total_hprd: beta=-0.085, SE=0.005, 95% CI [-0.094, -0.076], p=0.000, N=1,209,909.
- total_nurse_hprd: beta=0.089, SE=0.008, 95% CI [0.073, 0.105], p=0.000, N=1,209,911.

The event-study coefficients and raw trend figures are saved under `result/figures/`. Main coefficient tables are saved under `result/tables/`.

## Robustness and Falsification

The robustness battery tests alternative exposure definitions, 2021-only baselines, baselines excluding 2020, COVID-period exclusion, balanced-panel restrictions, facility-quarter aggregation, ownership subsamples, and fake 2021 intervention dates. See `result/robustness_results.csv` and `result/tables/table5_robustness.*`.

## Limitations

- The design is differential exposure within a national reform. It cannot estimate the absolute national effect without stronger assumptions.
- Turnover exposure is not the preferred January 2022 exposure because turnover fields became publicly visible with the reform; PBJ-derived weekend staffing exposure is cleaner.
- Quality outcomes from ratings and deficiencies are facility-level administrative signals. They should not be interpreted as resident-level clinical outcomes.
- Late post-period estimates may be affected by later staffing-policy debates and the 2024 minimum staffing rule context.

## Final Go/No-Go Judgment

**Weak causal design under current specification.** At least one primary staffing outcome rejects the joint pre-trend null at the 5% level. At least one primary post-July staffing estimate excludes zero. A placebo 2021 timing test is statistically significant, which weakens causal interpretation.

## Manuscript Next Steps

1. Inspect the event-study figures and pre-trend table before writing causal claims.
2. If primary staffing outcomes survive robustness and placebo checks, frame the paper as a staffing-behavior response to transparency and rating incentives.
3. If weekend gains are offset by weekday losses, frame the result as staffing reallocation rather than overall improvement.
4. Treat downstream ratings and deficiency results as secondary and descriptive unless their timing and robustness are strong.
