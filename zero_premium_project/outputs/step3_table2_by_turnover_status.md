# Step 3 Table 2-Style Descriptive Comparison By Turnover Status

Outcome shares are shown as percentage-point differences below. The CSV also includes available plan-market variables and absent-variable rows. These diagnostics are unadjusted; when `enrollment_2021_weight` is available the script uses it, otherwise it falls back to current-year `Cnsmr` weights. Drake Table 2 also uses year-adjusted differences, which are not estimated here.

| comparison | variable | untreated_county_years | treated_county_years | unweighted_difference | cnsmr_weighted_difference | weighting_used | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| any_zero_to_positive_turnover | overall_reenrollment_share | 2289 | 4187 | -0.130 | 0.870 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover | automatic_passive_share | 2289 | 4187 | -0.850 | -1.758 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover | active_share | 2289 | 4187 | 0.720 | 2.629 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover | active_stay_share | 2289 | 4187 | -5.550 | -3.899 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover | active_switch_share | 2289 | 4187 | 6.318 | 6.528 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | overall_reenrollment_share | 6369 | 107 | 3.394 | 1.247 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | automatic_passive_share | 6369 | 107 | -3.598 | -0.383 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | active_share | 6369 | 107 | 7.037 | 1.629 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | active_stay_share | 6369 | 107 | 3.230 | 2.215 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | active_switch_share | 6369 | 107 | 3.768 | -0.587 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
