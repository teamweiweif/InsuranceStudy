# Identification Audit

## Strategy

The policy is national, so the design does not compare treated facilities with untreated facilities. It compares facilities with higher pre-policy exposure to the reporting and rating measures against lower-exposure comparison facilities under the same national reform.

The preferred model is:

`Y_it = facility FE + time FE + high_exposure_i x Jan-Jun 2022 + high_exposure_i x post-Jul 2022 + error_it`

The event-study version replaces the post indicators with high-exposure interactions for monthly event time around January 2022. Standard errors are clustered at the facility level.

## Exposure

The preferred exposure is the top quartile of a pre-2022 composite index combining:

- low baseline weekend total nurse HPRD;
- low baseline weekend RN HPRD;
- high baseline weekday-minus-weekend total nurse staffing gap.

All components use PBJ staffing records from January 2019 through December 2021.

## Assumptions

- Higher- and lower-exposure facilities would have followed parallel trends in the absence of the 2022 reporting/rating changes.
- Pre-2022 exposure is not mechanically constructed from post-2022 outcomes.
- Facility exits and missing reports do not differentially create the estimated post-2022 divergence.
- No other contemporaneous policy shock differentially affects high-exposure facilities exactly through the same timing and outcome channels.

## Threats

- COVID-era staffing shocks could create nonparallel pre-trends or change baseline exposure measurement.
- Facilities may strategically reallocate staffing from weekdays to weekends rather than increase total staffing.
- Ratings and deficiencies are downstream and partly endogenous to survey timing, so they should not be overinterpreted as resident health effects.
- Provider Data Catalog turnover fields are not consistently available before the January 2022 reporting change, so turnover exposure is documented but not preferred for the January transparency design.

## Pre-Trend Tests

```
outcome,test,wald_chi2,df,p_value,n_obs,n_facilities
weekend_total_nurse_hprd,joint_pre_2022_event_coefficients_equal_zero,380.0973,23,0.0,1209911,15133
weekend_rn_hprd,joint_pre_2022_event_coefficients_equal_zero,462.82743,23,0.0,1209911,15133
weekday_total_nurse_hprd,joint_pre_2022_event_coefficients_equal_zero,281.35654,23,0.0,1209909,15133
weekday_minus_weekend_total_hprd,joint_pre_2022_event_coefficients_equal_zero,129.29042,23,0.0,1209909,15133
```

## Go/No-Go

**Weak causal design under current specification.** At least one primary staffing outcome rejects the joint pre-trend null at the 5% level. At least one primary post-July staffing estimate excludes zero. A placebo 2021 timing test is statistically significant, which weakens causal interpretation.
