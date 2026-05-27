# Step 3 Descriptive Replication Report

## 1. Executive Summary

Overall status: **Fix Step 2 before Step 4**.

This Step 3 audit can reproduce the broad public OEP reenrollment patterns, but it does not yet justify formal treatment regressions without repairing or tightening Step 2 treatment construction. The main concerns are the 2,188 vs 2,159 county-count discrepancy, proxy-based zero-premium treatment, and weaker 2023-to-2024 plan mapping.

Main warnings:

- Primary sample has 2188 counties versus Drake's 2159.
- Turnover prevalence is high under the proxy definition; proxy may be broad.
- Problem-state sensitivity identified data-quality states: GA,NC.
- Treatment is proxy-based and not household-specific net premium.

## 2. What Was Tested

- Dataset readability for the full, primary, and Nebraska sensitivity CSVs.
- Sample alignment against Drake-style 29-state HealthCare.gov county-year structure.
- Table 1-style reenrollment descriptives against manually encoded Drake anchors.
- Turnover prevalence by year and state-year.
- Table 2-style descriptive comparisons by turnover status.
- Step 2 weaknesses: 2021 fallback, 2023-to-2024 join weakness, and zero-premium proxy quality.

## 3. Sample Alignment

Our primary sample has 6564 county-years, 2188 counties, and 29 states. Drake reports 2,159 counties in the same 29-state sample.

AK in primary sample: False; HI in primary sample: False; NE in primary sample: False. Nebraska sensitivity exists: True.

The 2,188 vs 2,159 county discrepancy is not resolved by year coverage because all current primary counties appear in all three years. Exact extra counties cannot be identified without Drake's county list. Candidate diagnostic reasons are:

| candidate_discrepancy_reason | counties |
| --- | --- |
| included_by_current_sample_rule | 2082 |
| missing_or_suppressed_table1_outcome | 76 |
| treatment_not_constructible_all_years;missing_crosswalk_flag;missing_current_plan_flag;missing_premium_flag | 29 |
| treatment_not_constructible_all_years | 1 |

A transparent harmonization rule should be chosen before Step 4. Plausible non-arbitrary rules include requiring complete Table 1 outcome availability in all years, treatment constructibility in all years, or both. The current script reports these counts but does not force the sample to match Drake by arbitrary deletion.

## 4. Outcome Replication

Closest Table 1-style comparison:

| year | measure | our_value | drake_value | difference | absolute_difference | weighting_used |
| --- | --- | --- | --- | --- | --- | --- |
| 2022 | overall_reenrollment_pct_enrollment | 76.66 | 76.70 | -0.04 | 0.04 | Cnsmr_weighted_mean |
| 2022 | automatic_pct_enrollment | 21.32 | 21.20 | 0.12 | 0.12 | Cnsmr_weighted_mean |
| 2022 | active_pct_enrollment | 55.35 | 55.40 | -0.05 | 0.05 | Cnsmr_weighted_mean |
| 2022 | active_stay_pct_enrollment | 23.94 | 24.00 | -0.06 | 0.06 | Cnsmr_weighted_mean |
| 2022 | active_switch_pct_enrollment | 31.41 | 31.50 | -0.09 | 0.09 | Cnsmr_weighted_mean |
| 2022 | automatic_pct_reenrollment | 27.81 | 27.70 | 0.11 | 0.11 | Tot_Renrl_weighted_mean |
| 2022 | active_pct_reenrollment | 72.19 | 72.30 | -0.11 | 0.11 | Tot_Renrl_weighted_mean |
| 2022 | active_stay_pct_reenrollment | 31.22 | 31.10 | 0.12 | 0.12 | Tot_Renrl_weighted_mean |
| 2022 | active_switch_pct_reenrollment | 40.98 | 41.20 | -0.22 | 0.22 | Tot_Renrl_weighted_mean |
| 2023 | overall_reenrollment_pct_enrollment | 75.28 | 75.30 | -0.02 | 0.02 | Cnsmr_weighted_mean |
| 2023 | automatic_pct_enrollment | 20.81 | 20.80 | 0.01 | 0.01 | Cnsmr_weighted_mean |
| 2023 | active_pct_enrollment | 54.46 | 54.60 | -0.14 | 0.14 | Cnsmr_weighted_mean |
| 2023 | active_stay_pct_enrollment | 23.02 | 23.20 | -0.18 | 0.18 | Cnsmr_weighted_mean |
| 2023 | active_switch_pct_enrollment | 31.45 | 31.40 | 0.05 | 0.05 | Cnsmr_weighted_mean |
| 2023 | automatic_pct_reenrollment | 27.65 | 27.60 | 0.05 | 0.05 | Tot_Renrl_weighted_mean |
| 2023 | active_pct_reenrollment | 72.35 | 72.40 | -0.05 | 0.05 | Tot_Renrl_weighted_mean |
| 2023 | active_stay_pct_reenrollment | 30.58 | 30.40 | 0.18 | 0.18 | Tot_Renrl_weighted_mean |
| 2023 | active_switch_pct_reenrollment | 41.78 | 42.00 | -0.22 | 0.22 | Tot_Renrl_weighted_mean |
| 2024 | overall_reenrollment_pct_enrollment | 74.13 | 74.10 | 0.03 | 0.03 | Cnsmr_weighted_mean |
| 2024 | automatic_pct_enrollment | 22.18 | 22.10 | 0.08 | 0.08 | Cnsmr_weighted_mean |
| 2024 | active_pct_enrollment | 51.95 | 52.00 | -0.05 | 0.05 | Cnsmr_weighted_mean |
| 2024 | active_stay_pct_enrollment | 23.29 | 23.30 | -0.01 | 0.01 | Cnsmr_weighted_mean |
| 2024 | active_switch_pct_enrollment | 28.66 | 28.70 | -0.04 | 0.04 | Cnsmr_weighted_mean |
| 2024 | automatic_pct_reenrollment | 29.92 | 30.00 | -0.08 | 0.08 | Tot_Renrl_weighted_mean |
| 2024 | active_pct_reenrollment | 70.08 | 70.00 | 0.08 | 0.08 | Tot_Renrl_weighted_mean |
| 2024 | active_stay_pct_reenrollment | 31.42 | 31.30 | 0.12 | 0.12 | Tot_Renrl_weighted_mean |
| 2024 | active_switch_pct_reenrollment | 38.66 | 38.70 | -0.04 | 0.04 | Tot_Renrl_weighted_mean |
| total | overall_reenrollment_pct_enrollment | 75.14 | 75.20 | -0.06 | 0.06 | Cnsmr_weighted_mean |
| total | automatic_pct_enrollment | 21.53 | 21.50 | 0.03 | 0.03 | Cnsmr_weighted_mean |
| total | active_pct_enrollment | 53.61 | 53.70 | -0.09 | 0.09 | Cnsmr_weighted_mean |
| total | active_stay_pct_enrollment | 23.37 | 23.40 | -0.03 | 0.03 | Cnsmr_weighted_mean |
| total | active_switch_pct_enrollment | 30.24 | 30.30 | -0.06 | 0.06 | Cnsmr_weighted_mean |
| total | automatic_pct_reenrollment | 28.65 | 28.60 | 0.05 | 0.05 | Tot_Renrl_weighted_mean |
| total | active_pct_reenrollment | 71.35 | 71.40 | -0.05 | 0.05 | Tot_Renrl_weighted_mean |
| total | active_stay_pct_reenrollment | 31.11 | 31.00 | 0.11 | 0.11 | Tot_Renrl_weighted_mean |
| total | active_switch_pct_reenrollment | 40.24 | 40.40 | -0.16 | 0.16 | Tot_Renrl_weighted_mean |

The weighting closest to Drake is Cnsmr-weighted for enrollment-denominator measures and Tot_Renrl-weighted for reenrollment-denominator measures. Differences that remain likely reflect the county-count discrepancy, public PUF suppression/missingness, and aggregate county-year construction.

## 5. Treatment Prevalence

| year | county_years | counties | states | enrollment | treatment_constructibility_rate | missing_treatment_rate | not_constructible_count | any_share_all_county_years | any_share_constructible | any_enrollment_weighted_share_all | any_enrollment_weighted_share_constructible | across_issuer_share_all_county_years | across_issuer_share_constructible | across_issuer_enrollment_weighted_share_all | across_issuer_enrollment_weighted_share_constructible | within_issuer_share_all_county_years | within_issuer_share_constructible | within_issuer_enrollment_weighted_share_all | within_issuer_enrollment_weighted_share_constructible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022.000 | 2188.000 | 2188.000 | 29.000 | 9803559.000 | 1.000 | 0.000 | 1.000 | 0.803 | 0.803 | 0.936 | 0.936 | 0.044 | 0.044 | 0.028 | 0.028 | 0.763 | 0.764 | 0.929 | 0.929 |
| 2023.000 | 2188.000 | 2188.000 | 29.000 | 11708754.000 | 1.000 | 0.000 | 0.000 | 0.700 | 0.700 | 0.729 | 0.729 | 0.006 | 0.006 | 0.044 | 0.044 | 0.695 | 0.695 | 0.687 | 0.687 |
| 2024.000 | 2188.000 | 2188.000 | 29.000 | 16195598.000 | 0.987 | 0.013 | 29.000 | 0.638 | 0.646 | 0.797 | 0.812 | 0.006 | 0.006 | 0.025 | 0.026 | 0.633 | 0.642 | 0.797 | 0.812 |

The comparison to Drake exposure values is partial because exact eTable exposure values were not encoded here. The main qualitative anchor is that exposure increased after ARPA and persisted through 2024. Our proxy prevalence is high in 2022 and remains substantial through 2024, which may be plausible directionally but suggests the benchmark-based proxy may be broad.

## 6. Treatment-Status Descriptive Comparison

| comparison | variable | untreated_county_years | treated_county_years | unweighted_difference_pp | cnsmr_weighted_difference_pp | notes |
| --- | --- | --- | --- | --- | --- | --- |
| any_zero_to_positive_turnover | overall_reenrollment_share | 1851 | 4683 | 0.503 | 1.570 | Descriptive comparison only; not a causal contrast. |
| any_zero_to_positive_turnover | automatic_passive_share | 1851 | 4683 | -1.192 | -1.581 | Descriptive comparison only; not a causal contrast. |
| any_zero_to_positive_turnover | active_share | 1851 | 4683 | 1.676 | 3.151 | Descriptive comparison only; not a causal contrast. |
| any_zero_to_positive_turnover | active_stay_share | 1851 | 4683 | -4.637 | -2.224 | Descriptive comparison only; not a causal contrast. |
| any_zero_to_positive_turnover | active_switch_share | 1851 | 4683 | 6.347 | 5.375 | Descriptive comparison only; not a causal contrast. |
| any_zero_to_positive_turnover_across_issuer | overall_reenrollment_share | 6411 | 123 | 2.697 | -1.198 | Descriptive comparison only; not a causal contrast. |
| any_zero_to_positive_turnover_across_issuer | automatic_passive_share | 6411 | 123 | -3.764 | -2.733 | Descriptive comparison only; not a causal contrast. |
| any_zero_to_positive_turnover_across_issuer | active_share | 6411 | 123 | 6.487 | 1.535 | Descriptive comparison only; not a causal contrast. |
| any_zero_to_positive_turnover_across_issuer | active_stay_share | 6411 | 123 | 1.798 | -1.936 | Descriptive comparison only; not a causal contrast. |
| any_zero_to_positive_turnover_across_issuer | active_switch_share | 6411 | 123 | 4.651 | 3.470 | Descriptive comparison only; not a causal contrast. |

Sign checks:

| comparison | variable | expected_descriptive_direction_from_drake_anchor | unweighted_difference | cnsmr_weighted_difference | sign_check | question_answered | composition_note | interpretation_limit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| any_zero_to_positive_turnover | active_switch_share | positive | 0.063 | 0.054 | same_direction | Treated counties have higher active switching descriptively. | Weighted and unweighted signs match. | Descriptive signs are not causal and need not match regression signs exactly. |
| any_zero_to_positive_turnover | active_stay_share | negative | -0.046 | -0.022 | same_direction | Treated counties have lower active stay descriptively. | Weighted and unweighted signs match. | Descriptive signs are not causal and need not match regression signs exactly. |
| any_zero_to_positive_turnover_across_issuer | automatic_passive_share | negative | -0.038 | -0.027 | same_direction | Across-issuer treated counties have lower automatic/passive reenrollment descriptively. | Weighted and unweighted signs match. | Descriptive signs are not causal and need not match regression signs exactly. |

These are descriptive differences only. They are not adjusted regression estimates and should not be interpreted causally.

## 7. Step 2 Unresolved Issues

- 2021 fallback: all 2022 treatment rows depend on the 2021-to-2022 transition built from fallback inputs. The 2023-2024-only sensitivity is therefore central.
- 2023-to-2024 join weakness: Step 2 reported a national current-plan join rate around 0.935 for top-two rows, weaker than the Step 1 prototype.
- Zero-premium proxy: the measure is benchmark-based and low-income age-40, not exact household net premium.
- Nebraska sensitivity: Nebraska remains outside the primary sample until county-market mapping is verified.
- Aggregate county-year limitation: public OEP PUFs do not support individual retention or income-stratified county outcomes.

Problem states identified for data-quality sensitivity:

GA, NC

## 8. Sensitivity Results

| sensitivity_dataset | path | rows | counties | states | years | treatment_prevalence_constructible | treatment_constructibility_rate | outcome_missingness | table1_mean_absolute_difference_closest | table1_mean_absolute_difference_change_vs_primary | any_turnover_active_switch_weighted_diff | any_turnover_active_stay_weighted_diff | problem_states_excluded |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| primary_2023_2024_only | data\processed\drake_replication_primary_2023_2024_only.csv | 4376 | 2188 | 29 | 2023,2024 | 0.673 | 0.993 | 0.014 | 0.175 | 0.092 | 0.036 | -0.010 |  |
| primary_constructible_only | data\processed\drake_replication_primary_constructible_only.csv | 6534 | 2188 | 29 | 2022,2023,2024 | 0.717 | 1.000 | 0.020 | 0.079 | -0.004 | 0.054 | -0.022 |  |
| primary_no_problem_states | data\processed\drake_replication_primary_no_problem_states.csv | 5787 | 1929 | 27 | 2022,2023,2024 | 0.698 | 1.000 | 0.022 | 0.257 | 0.174 | 0.053 | -0.018 | GA,NC |

## 9. Honest Limitations

- No causal claims are made.
- No individual-level HTE can be estimated from these public aggregate PUFs.
- No household-specific APTC calculation is present.
- The treatment proxy differs from exact Drake construction unless later proven otherwise.
- Differences from Drake may reflect proxy treatment, sample construction, weighting, and missing or suppressed cells.

## 10. Recommendation

Recommendation: **B. Repair Step 2 treatment construction first.**

The conservative recommendation is to repair or tighten Step 2 treatment construction before formal Step 4 treatment regressions. Outcome descriptives are useful, but treatment prevalence and sample alignment are not yet close enough to treat Step 2 as frozen.

## Final Self-Audit Checklist

- [x] Did I avoid causal claims?
- [x] Did I avoid DID/regression/covariate-adjusted causal models?
- [x] Did I read the Step 2 report and validation flags?
- [x] Did I verify that processed datasets are actually readable and nonempty?
- [x] Did I reproduce Table 1-style reenrollment descriptives?
- [x] Did I compare our values to Drake reference values?
- [x] Did I compute treatment prevalence by year and state-year?
- [x] Did I investigate 2188 vs 2159 county discrepancy?
- [x] Did I inspect 2021 fallback sensitivity?
- [x] Did I inspect 2023-to-2024 join failure weakness?
- [x] Did I audit zero-premium proxy quality?
- [x] Did I produce a 2023-2024-only sensitivity file?
- [x] Did I produce a clear Markdown report?
- [x] Did I state whether Step 4 is justified?
- [x] Did I report honestly what failed or remains uncertain?
