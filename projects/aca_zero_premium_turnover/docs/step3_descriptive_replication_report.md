# Step 3 Descriptive Replication Report

## 1. Executive Summary

Overall status: **Fix Step 2 before Step 4**.

This Step 3 audit applies Drake supplement eTable 3 county exclusions and reproduces the public OEP reenrollment patterns closely. The sample-count discrepancy is resolved, and the repaired rebuild now retains 2021 enrollment weights plus silver/bronze market controls. Formal Step 4 replication is still not justified because the main remaining concerns are proxy-based zero-premium treatment, under-detection of across-insurer turnover, and incomplete non-EHB/125 percent FPL premium handling.

Main warnings:

- Any-turnover county-year count differs from Drake by -264.
- Across-issuer turnover count differs from Drake by -104; current proxy likely under-detects across-insurer turnover.
- Enrollment-weighted any-turnover exposure differs from Drake 100-150 FPL exposure by up to 6.5 pp.
- Treatment remains proxy-based; Step 2 does not prove household-specific net premiums, 125 percent FPL contribution, or non-EHB handling.

## 2. What Was Tested

- Dataset readability for the full, primary, and Nebraska sensitivity CSVs.
- Sample alignment against Drake-style 29-state HealthCare.gov county-year structure.
- Table 1-style reenrollment descriptives against manually encoded Drake anchors.
- Turnover prevalence by year and state-year.
- Table 2-style descriptive comparisons by turnover status.
- Step 2 weaknesses: 2021-to-2022 transition source/definition, 2023-to-2024 join weakness, and zero-premium proxy quality.

## 3. Sample Alignment

The raw primary sample has 6564 county-years and 2188 counties. Applying Drake supplement eTable 3 exclusions gives 6477 county-years, 2159 counties, and 29 states.

AK in primary sample: False; HI in primary sample: False; NE in primary sample: False. Nebraska sensitivity exists: True.

Drake's Results text reports 6471 county-years and 2157 unique counties with nonmissing enrollment. Our harmonized data have 6471 county-years and 2157 unique counties with nonmissing `Cnsmr`, matching those anchors.

The 2,188 vs 2,159 county discrepancy is explained by the 29 GA/NC counties in supplement eTable 3 with no crosswalk data from 2023 to 2024. They appear in the raw primary data and are removed from the Drake-harmonized Step 3 analysis. Legacy SD/VA FIPS exclusions are also encoded but do not affect this 2022-2024 primary sample.

eTable 3 counties found in the raw primary sample:

| state | county_fips | county_name_in_supplement | observed_county_names | rows_present | years_present | supplement_reason |
| --- | --- | --- | --- | --- | --- | --- |
| GA | 13009 | Baldwin County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13013 | Barrow County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13021 | Bibb County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13051 | Chatham County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13059 | Clarke County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13141 | Hancock County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13157 | Jackson County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13207 | Monroe County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13215 | Muscogee County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13219 | Oconee County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13225 | Peach County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13227 | Pickens County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13245 | Randolph County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| GA | 13319 | Wilkinson County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37001 | Alamance County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37033 | Caswell County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37037 | Chatham County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37065 | Edgecombe County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37079 | Greene County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37081 | Guilford County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37105 | Lee County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37127 | Nash County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37145 | Person County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37147 | Pitt County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37151 | Randolph County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37157 | Rockingham County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37189 | Watauga County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37191 | Wayne County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |
| NC | 37195 | Wilson County |  | 3 | 2022,2023,2024 | No crosswalk data from 2023 to 2024 per Drake supplement eTable 3. |

County-discrepancy diagnostic reasons after adding the eTable 3 rule:

| candidate_discrepancy_reason | counties |
| --- | --- |
| included_by_current_sample_rule | 2083 |
| missing_or_suppressed_table1_outcome | 76 |
| drake_supplement_etable3_exclusion;treatment_not_constructible_all_years;missing_crosswalk_flag;missing_current_plan_flag;missing_premium_flag | 29 |

This is not arbitrary deletion: the rule is directly taken from Drake supplement eTable 3. The harmonized dataset is written to `data/processed/drake_replication_primary_drake_harmonized_2022_2024.csv` for Step 3 diagnostics.

## 4. Outcome Replication

Closest Table 1-style comparison:

| year | measure | our_value | drake_value | difference | absolute_difference | weighting_used |
| --- | --- | --- | --- | --- | --- | --- |
| 2022 | overall_reenrollment_pct_enrollment | 76.68 | 76.70 | -0.02 | 0.02 | Cnsmr_weighted_mean |
| 2022 | automatic_pct_enrollment | 21.28 | 21.20 | 0.08 | 0.08 | Cnsmr_weighted_mean |
| 2022 | active_pct_enrollment | 55.40 | 55.40 | -0.00 | 0.00 | Cnsmr_weighted_mean |
| 2022 | active_stay_pct_enrollment | 24.01 | 24.00 | 0.01 | 0.01 | Cnsmr_weighted_mean |
| 2022 | active_switch_pct_enrollment | 31.40 | 31.50 | -0.10 | 0.10 | Cnsmr_weighted_mean |
| 2022 | automatic_pct_reenrollment | 27.75 | 27.70 | 0.05 | 0.05 | Tot_Renrl_weighted_mean |
| 2022 | active_pct_reenrollment | 72.25 | 72.30 | -0.05 | 0.05 | Tot_Renrl_weighted_mean |
| 2022 | active_stay_pct_reenrollment | 31.31 | 31.10 | 0.21 | 0.21 | Tot_Renrl_weighted_mean |
| 2022 | active_switch_pct_reenrollment | 40.94 | 41.20 | -0.26 | 0.26 | Tot_Renrl_weighted_mean |
| 2023 | overall_reenrollment_pct_enrollment | 75.33 | 75.30 | 0.03 | 0.03 | Cnsmr_weighted_mean |
| 2023 | automatic_pct_enrollment | 20.81 | 20.80 | 0.01 | 0.01 | Cnsmr_weighted_mean |
| 2023 | active_pct_enrollment | 54.53 | 54.60 | -0.07 | 0.07 | Cnsmr_weighted_mean |
| 2023 | active_stay_pct_enrollment | 23.13 | 23.20 | -0.07 | 0.07 | Cnsmr_weighted_mean |
| 2023 | active_switch_pct_enrollment | 31.40 | 31.40 | -0.00 | 0.00 | Cnsmr_weighted_mean |
| 2023 | automatic_pct_reenrollment | 27.62 | 27.60 | 0.02 | 0.02 | Tot_Renrl_weighted_mean |
| 2023 | active_pct_reenrollment | 72.38 | 72.40 | -0.02 | 0.02 | Tot_Renrl_weighted_mean |
| 2023 | active_stay_pct_reenrollment | 30.70 | 30.40 | 0.30 | 0.30 | Tot_Renrl_weighted_mean |
| 2023 | active_switch_pct_reenrollment | 41.68 | 42.00 | -0.32 | 0.32 | Tot_Renrl_weighted_mean |
| 2024 | overall_reenrollment_pct_enrollment | 74.14 | 74.10 | 0.04 | 0.04 | Cnsmr_weighted_mean |
| 2024 | automatic_pct_enrollment | 22.14 | 22.10 | 0.04 | 0.04 | Cnsmr_weighted_mean |
| 2024 | active_pct_enrollment | 52.00 | 52.00 | -0.00 | 0.00 | Cnsmr_weighted_mean |
| 2024 | active_stay_pct_enrollment | 23.32 | 23.30 | 0.02 | 0.02 | Cnsmr_weighted_mean |
| 2024 | active_switch_pct_enrollment | 28.68 | 28.70 | -0.02 | 0.02 | Cnsmr_weighted_mean |
| 2024 | automatic_pct_reenrollment | 29.87 | 30.00 | -0.13 | 0.13 | Tot_Renrl_weighted_mean |
| 2024 | active_pct_reenrollment | 70.13 | 70.00 | 0.13 | 0.13 | Tot_Renrl_weighted_mean |
| 2024 | active_stay_pct_reenrollment | 31.45 | 31.30 | 0.15 | 0.15 | Tot_Renrl_weighted_mean |
| 2024 | active_switch_pct_reenrollment | 38.68 | 38.70 | -0.02 | 0.02 | Tot_Renrl_weighted_mean |
| total | overall_reenrollment_pct_enrollment | 75.17 | 75.20 | -0.03 | 0.03 | Cnsmr_weighted_mean |
| total | automatic_pct_enrollment | 21.50 | 21.50 | 0.00 | 0.00 | Cnsmr_weighted_mean |
| total | active_pct_enrollment | 53.67 | 53.70 | -0.03 | 0.03 | Cnsmr_weighted_mean |
| total | active_stay_pct_enrollment | 23.44 | 23.40 | 0.04 | 0.04 | Cnsmr_weighted_mean |
| total | active_switch_pct_enrollment | 30.23 | 30.30 | -0.07 | 0.07 | Cnsmr_weighted_mean |
| total | automatic_pct_reenrollment | 28.61 | 28.60 | 0.01 | 0.01 | Tot_Renrl_weighted_mean |
| total | active_pct_reenrollment | 71.39 | 71.40 | -0.01 | 0.01 | Tot_Renrl_weighted_mean |
| total | active_stay_pct_reenrollment | 31.18 | 31.00 | 0.18 | 0.18 | Tot_Renrl_weighted_mean |
| total | active_switch_pct_reenrollment | 40.21 | 40.40 | -0.19 | 0.19 | Tot_Renrl_weighted_mean |

The weighting closest to Drake is Cnsmr-weighted for enrollment-denominator measures and Tot_Renrl-weighted for reenrollment-denominator measures. After eTable 3 harmonization, nearly all differences are well below 1 percentage point. Remaining small differences likely reflect OEP PUF suppression, denominator availability, and public aggregate county-year construction.

## 5. Treatment Prevalence

| year | county_years | counties | states | enrollment | treatment_constructibility_rate | missing_treatment_rate | not_constructible_count | any_share_all_county_years | any_share_constructible | any_enrollment_weighted_share_all | any_enrollment_weighted_share_constructible | across_issuer_share_all_county_years | across_issuer_share_constructible | across_issuer_enrollment_weighted_share_all | across_issuer_enrollment_weighted_share_constructible | within_issuer_share_all_county_years | within_issuer_share_constructible | within_issuer_enrollment_weighted_share_all | within_issuer_enrollment_weighted_share_constructible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022.000 | 2159.000 | 2159.000 | 29.000 | 9636366.000 | 1.000 | 0.000 | 0.000 | 0.752 | 0.752 | 0.889 | 0.889 | 0.041 | 0.041 | 0.011 | 0.011 | 0.712 | 0.712 | 0.882 | 0.882 |
| 2023.000 | 2159.000 | 2159.000 | 29.000 | 11503884.000 | 1.000 | 0.000 | 0.000 | 0.583 | 0.583 | 0.613 | 0.613 | 0.002 | 0.002 | 0.001 | 0.001 | 0.581 | 0.581 | 0.613 | 0.613 |
| 2024.000 | 2159.000 | 2159.000 | 29.000 | 15900650.000 | 1.000 | 0.000 | 0.000 | 0.605 | 0.605 | 0.782 | 0.782 | 0.006 | 0.006 | 0.026 | 0.026 | 0.600 | 0.600 | 0.782 | 0.782 |

Comparison against Drake supplement eTable 1 exposure anchors:

| year | our_any_turnover_enrollment_weighted_pct | our_any_turnover_unweighted_county_pct | drake_100_150_fpl_exposure_pct | difference_vs_drake_100_150_pp | absolute_difference_vs_drake_100_150_pp | drake_150_200_fpl_exposure_pct | comparison_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 88.93 | 75.22 | 93.90 | -4.97 | 4.97 | 7.80 | Closest available comparison is enrollment-weighted any turnover vs Drake 100-150 FPL exposure. Drake exposure is individual/exposure-weighted; this dataset uses county-year OEP enrollment weights. |
| 2023 | 61.33 | 58.27 | 67.80 | -6.47 | 6.47 | 9.20 | Closest available comparison is enrollment-weighted any turnover vs Drake 100-150 FPL exposure. Drake exposure is individual/exposure-weighted; this dataset uses county-year OEP enrollment weights. |
| 2024 | 78.23 | 60.49 | 83.80 | -5.57 | 5.57 | 3.50 | Closest available comparison is enrollment-weighted any turnover vs Drake 100-150 FPL exposure. Drake exposure is individual/exposure-weighted; this dataset uses county-year OEP enrollment weights. |

Turnover count comparison against the main article:

| metric | our_value | drake_reference | difference | notes |
| --- | --- | --- | --- | --- |
| constructible_county_years | 6477.000 | 6459.000 | 18.000 | Drake Table 2 reports 6459 county-years. Our count is constructible rows after eTable 3 exclusions; remaining difference likely reflects Drake's complete-case Table 2 rule, OEP suppression, or treatment-definition details rather than missing repaired controls. |
| any_turnover_county_years | 4188.000 | 4452.000 | -264.000 | Main article reports 4452 county-years with any turnover. |
| across_issuer_turnover_county_years | 107.000 | 211.000 | -104.000 | Main article reports 211 county-years with across-insurer turnover. This is the clearest treatment-definition mismatch. |
| any_turnover_enrollee_years_millions | 28.065 | 28.400 | -0.335 | Main article reports 28.4 million enrollee-years with any turnover. |
| across_issuer_turnover_enrollee_years_millions | 0.524 | 0.800 | -0.276 | Main article reports 0.8 million enrollee-years with across-insurer turnover. |

Treatment-definition sensitivity:

| variant | any_turnover_county_years | across_issuer_turnover_county_years | any_turnover_enrollee_years_millions | across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | difference_vs_drake_any_enrollee_millions | difference_vs_drake_across_enrollee_millions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264.000 | -104.000 | -0.335 | -0.276 |
| ehb_il_or_only | 4344 | 123 | 29.269 | 1.193 | -108.000 | -88.000 | 0.869 | 0.393 |
| gross_only | 4626 | 123 | 30.254 | 1.193 | 174.000 | -88.000 | 1.854 | 0.393 |

The EHB-aware definition follows the supplement statement that non-EHB premiums cannot be reduced to zero by federal subsidies, but it moves county-year counts below Drake while improving any-turnover enrollee-years. The gross-only definition better matches county-year prevalence in some years but ignores non-EHB residuals. This is why Step 4 remains blocked rather than selecting whichever definition happens to look closer.

The enrollment-weighted any-turnover prevalence is close in 2022, higher than Drake in 2023, and lower than Drake in 2024. The bigger problem is across-insurer turnover: the current proxy identifies fewer across-insurer county-years than Drake. That is a Step 2 treatment-construction issue, not an outcome-replication issue.

## 6. Treatment-Status Descriptive Comparison

| comparison | variable | untreated_county_years | treated_county_years | unweighted_difference_pp | cnsmr_weighted_difference_pp | weighting_used | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| any_zero_to_positive_turnover | overall_reenrollment_share | 2289 | 4188 | -0.128 | 0.871 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover | automatic_passive_share | 2289 | 4188 | -0.845 | -1.758 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover | active_share | 2289 | 4188 | 0.717 | 2.628 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover | active_stay_share | 2289 | 4188 | -5.549 | -3.899 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover | active_switch_share | 2289 | 4188 | 6.314 | 6.528 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | overall_reenrollment_share | 6370 | 107 | 3.393 | 1.247 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | automatic_passive_share | 6370 | 107 | -3.601 | -0.383 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | active_share | 6370 | 107 | 7.039 | 1.629 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | active_stay_share | 6370 | 107 | 3.230 | 2.214 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |
| any_zero_to_positive_turnover_across_issuer | active_switch_share | 6370 | 107 | 3.770 | -0.586 | enrollment_2021_weight | Descriptive comparison only; not a causal contrast. Uses Drake-style 2021 enrollment weights. |

Sign checks:

| comparison | variable | expected_descriptive_direction_from_drake_anchor | unweighted_difference | cnsmr_weighted_difference | sign_check | question_answered | composition_note | interpretation_limit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| any_zero_to_positive_turnover | active_switch_share | positive | 0.063 | 0.065 | same_direction | Treated counties have higher active switching descriptively. | Weighted and unweighted signs match. | Descriptive signs are not causal and need not match regression signs exactly. |
| any_zero_to_positive_turnover | active_stay_share | negative | -0.055 | -0.039 | same_direction | Treated counties have lower active stay descriptively. | Weighted and unweighted signs match. | Descriptive signs are not causal and need not match regression signs exactly. |
| any_zero_to_positive_turnover_across_issuer | automatic_passive_share | negative | -0.036 | -0.004 | same_direction | Across-issuer treated counties have lower automatic/passive reenrollment descriptively. | Weighted and unweighted signs match. | Descriptive signs are not causal and need not match regression signs exactly. |

These are descriptive differences only. They are not adjusted regression estimates and should not be interpreted causally. Drake Table 2 uses 2021 enrollment weights and year-adjusted differences; this Step 3 table uses `enrollment_2021_weight` when present and otherwise falls back to current-year `Cnsmr` weights.

## 7. Step 2 Unresolved Issues

- 2021-to-2022 transition: all 2022 treatment rows depend on the prior-year QHP/crosswalk construction. Direct PY2021 QHP Landscape is used when available locally, but the transition still requires treatment-anchor reconciliation.
- 2023-to-2024 join weakness: Drake supplement eTable 3 resolves the main GA/NC county-count issue, but Step 2 still needs source-level crosswalk validation before formal regression work.
- Zero-premium proxy: Drake assumes a single 40-year-old at 125 percent FPL for the 100-150 FPL exposure construction. The current Step 2 output is benchmark-based and does not prove exact household-specific net premiums.
- Non-EHB issue: Drake notes that required non-EHB benefits can prevent zero-dollar premiums in some states. The current Step 2 output does not explicitly retain or audit non-EHB handling.
- Repaired controls/weights: 2021 enrollment weights, bronze spread, silver/bronze plan counts, and insurer-count controls are now present after the local raw-data rebuild.
- Nebraska sensitivity: Nebraska remains outside the primary sample until county-market mapping is verified.
- Aggregate county-year limitation: public OEP PUFs do not support individual retention or income-stratified county outcomes.

Problem states identified for data-quality sensitivity:

None by the configured constructibility/join-failure rule.

## 8. Sensitivity Results

| created | sensitivity_dataset | path | rows | counties | states | years | treatment_prevalence_constructible | treatment_constructibility_rate | outcome_missingness | table1_mean_absolute_difference_closest | table1_mean_absolute_difference_change_vs_primary | any_turnover_active_switch_weighted_diff | any_turnover_active_stay_weighted_diff | problem_states_excluded | not_created_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | primary_2023_2024_only | data\processed\drake_replication_primary_2023_2024_only.csv | 4318 | 2159 | 29 | 2023,2024 | 0.594 | 1.000 | 0.015 | 0.169 | 0.092 | 0.039 | -0.019 |  |  |
| 1 | primary_constructible_only | data\processed\drake_replication_primary_constructible_only.csv | 6477 | 2159 | 29 | 2022,2023,2024 | 0.647 | 1.000 | 0.020 | 0.077 | 0.000 | 0.065 | -0.039 |  |  |
| 0 | primary_no_problem_states |  | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  | No whole-state post-harmonization problem state was identified; eTable 3 supports county-level GA/NC exclusions instead. |

## 9. Honest Limitations

- No causal claims are made.
- No individual-level HTE can be estimated from these public aggregate PUFs.
- No household-specific APTC calculation is present.
- The treatment proxy differs from exact Drake construction unless later proven otherwise.
- Differences from Drake may reflect proxy treatment, sample construction, weighting, and missing or suppressed cells.

## 10. Recommendation

Recommendation: **B. Repair Step 2 treatment construction first.**

The conservative recommendation is to repair Step 2 treatment construction before formal Step 4 treatment regressions. Sample alignment, OEP outcome descriptives, 2021 weights, and market controls are now much stronger after the local raw-data rebuild, but treatment definition, across-insurer classification, and non-EHB handling are not yet close enough to freeze Step 2.

## Final Self-Audit Checklist

- [x] Did I avoid causal claims?
- [x] Did I avoid DID/regression/covariate-adjusted causal models?
- [x] Did I use Drake article and supplement details, especially eAppendix 1/eTable 3 missing-data handling?
- [x] Did I read the Step 2 report and validation flags?
- [x] Did I verify that processed datasets are actually readable and nonempty?
- [x] Did I apply Drake supplement eTable 3 exclusions transparently rather than arbitrary deletion?
- [x] Did I reproduce Table 1-style reenrollment descriptives?
- [x] Did I compare our values to Drake reference values?
- [x] Did I compute treatment prevalence by year and state-year?
- [x] Did I investigate 2188 vs 2159 county discrepancy?
- [x] Did I inspect 2021-to-2022 transition sensitivity?
- [x] Did I inspect 2023-to-2024 join failure weakness?
- [x] Did I audit zero-premium proxy quality?
- [x] Did I produce a 2023-2024-only sensitivity file?
- [x] Did I produce a clear Markdown report?
- [x] Did I state whether Step 4 is justified?
- [x] Did I report honestly what failed or remains uncertain?
