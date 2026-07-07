# Churn / Unwinding Second-Round Diagnostics

## Purpose

This note extends the first diagnostics pass into a fuller exposure-by-timing matrix, matched-month falsification screen, and subgroup-stability screen.

The working theory frame is now `administrative renewal burden`, not a single-mechanism bet on procedural friction alone.

## Gate Verdict

- final verdict: `GO_RISK_ONLY`
- timing gate: `True`
- falsification gate: `True`
- stability gate: `True`
- chosen variant for gate evaluation: `{'exposure_family': 'manual_renewal_burden', 'exposure_variant': 'renewal_form_rate', 'alignment': 'lag1'}`

## Top Timing Signals

| window | exposure_variant | alignment | outcome | support_rows | estimate_or_contrast | direction_flag |
| --- | --- | --- | --- | --- | --- | --- |
| core_aug_nov_2023 | procedural_term_count | same | medicaid_exit_to_uninsured_next | 204 | 0.2393 | expected |
| core_aug_nov_2023 | ineligible_rate | lead1 | medicaid_exit_to_uninsured_next | 153 | 0.207 | expected |
| core_aug_nov_2023 | pending_rate | lead1 | medicaid_exit_to_uninsured_next | 153 | 0.1619 | expected |
| core_aug_nov_2023 | procedural_term_count | same | medicaid_exit_next | 204 | 0.1273 | expected |
| core_aug_nov_2023 | renewal_form_rate | lag1 | medicaid_exit_to_uninsured_next | 203 | 0.1252 | expected |
| extended_mar_nov_2023 | ineligible_rate | lead1 | medicaid_exit_to_uninsured_next | 358 | 0.1228 | expected |
| core_aug_nov_2023 | pending_rate | lead1 | medicaid_exit_next | 153 | 0.118 | expected |
| core_aug_nov_2023 | ineligible_rate | same | medicaid_exit_to_uninsured_next | 204 | 0.1154 | expected |
| core_aug_nov_2023 | pending_count | lead1 | medicaid_exit_to_uninsured_next | 153 | 0.1131 | expected |
| core_aug_nov_2023 | renewal_due_count | same | medicaid_exit_to_uninsured_next | 204 | 0.11 | expected |
| core_aug_nov_2023 | pending_count | same | medicaid_exit_to_uninsured_next | 204 | 0.1087 | expected |
| extended_mar_nov_2023 | ineligible_rate | same | medicaid_exit_to_uninsured_next | 362 | 0.1077 | expected |

## Top High-Low Contrasts

| window | exposure_variant | alignment | outcome | support_rows | estimate_or_contrast | direction_flag |
| --- | --- | --- | --- | --- | --- | --- |
| core_aug_nov_2023 | pending_rate | lead1 | medicaid_exit_next | 102 | 0.0045 | expected |
| extended_mar_nov_2023 | procedural_term_share | lag2 | medicaid_exit_next | 174 | 0.0044 | expected |
| extended_mar_nov_2023 | ineligible_rate | same | medicaid_exit_next | 242 | 0.0042 | expected |
| core_aug_nov_2023 | pending_count | lead1 | medicaid_exit_next | 102 | 0.0039 | expected |
| extended_mar_nov_2023 | ineligible_rate | lag1 | medicaid_exit_next | 208 | 0.0037 | expected |
| core_aug_nov_2023 | pending_rate | lead1 | medicaid_exit_to_uninsured_next | 102 | 0.0036 | expected |
| core_aug_nov_2023 | ineligible_rate | same | medicaid_exit_to_uninsured_next | 136 | 0.0035 | expected |
| core_aug_nov_2023 | procedural_term_share | same | medicaid_exit_next | 136 | 0.0031 | expected |
| core_aug_nov_2023 | procedural_term_share | lag2 | medicaid_exit_next | 134 | 0.003 | expected |
| core_aug_nov_2023 | ineligible_rate | same | medicaid_exit_next | 136 | 0.0029 | expected |
| core_aug_nov_2023 | procedural_term_share | lag1 | medicaid_exit_next | 136 | 0.0027 | expected |
| core_aug_nov_2023 | pending_count | same | medicaid_exit_next | 136 | 0.0027 | expected |

## Falsification Summary

| exposure_variant | alignment | outcome | pre_2021_contrast | pre_2022_contrast | unwinding_2023_contrast | max_pre_abs_contrast | same_direction_big_pre | falsification_pass_outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| procedural_term_count | same | medicaid_exit_next | 0.0015 | 0.0027 | -0.0043 | 0.0027 | False | True |
| procedural_term_count | same | medicaid_exit_to_uninsured_next | 0.0013 | 0.0007 | -0.0024 | 0.0013 | False | True |
| procedural_term_count | lag1 | medicaid_exit_next | 0.0016 | 0.0027 | -0.0041 | 0.0027 | False | True |
| procedural_term_count | lag1 | medicaid_exit_to_uninsured_next | 0.0014 | 0.0006 | -0.0024 | 0.0014 | False | True |
| procedural_term_count | lead1 | medicaid_exit_next | 0.0009 | 0.0019 | -0.0008 | 0.0019 | False | False |
| procedural_term_count | lead1 | medicaid_exit_to_uninsured_next | 0.0013 | 0.0005 | 0.0 | 0.0013 | True | False |
| procedural_term_count | lag2 | medicaid_exit_next | 0.0008 | 0.003 | -0.0066 | 0.003 | False | True |
| procedural_term_count | lag2 | medicaid_exit_to_uninsured_next | 0.0007 | 0.0008 | -0.0039 | 0.0008 | False | True |
| procedural_term_share | same | medicaid_exit_next | 0.0003 | 0.0009 | 0.0015 | 0.0009 | False | True |
| procedural_term_share | same | medicaid_exit_to_uninsured_next | -0.0009 | -0.0 | 0.0002 | 0.0009 | False | False |
| procedural_term_share | lag1 | medicaid_exit_next | 0.0004 | 0.0012 | 0.0012 | 0.0012 | False | True |
| procedural_term_share | lag1 | medicaid_exit_to_uninsured_next | -0.001 | 0.0002 | -0.0002 | 0.001 | False | False |
| procedural_term_share | lead1 | medicaid_exit_next | -0.0001 | 0.001 | 0.001 | 0.001 | False | True |
| procedural_term_share | lead1 | medicaid_exit_to_uninsured_next | -0.0011 | 0.0002 | 0.0004 | 0.0011 | False | False |
| procedural_term_share | lag2 | medicaid_exit_next | 0.0004 | 0.0016 | 0.0003 | 0.0016 | True | False |
| procedural_term_share | lag2 | medicaid_exit_to_uninsured_next | -0.001 | -0.0001 | 0.0 | 0.001 | False | False |
| renewal_due_count | same | medicaid_exit_next | -0.0001 | 0.0019 | -0.0006 | 0.0019 | False | False |
| renewal_due_count | same | medicaid_exit_to_uninsured_next | 0.0004 | 0.0003 | 0.0007 | 0.0004 | False | True |

## Subgroup Stability Leaders

| feature_family | outcome | groups_compared | pre_top_group | unwinding_top_group | spearman_rank_corr | top_group_match | stable_flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| female_group | medicaid_exit_next | 2 | male | male | 1.0 | True | True |
| household_child_group | medicaid_exit_to_uninsured_next | 2 | household_has_child | household_has_child | 1.0 | True | True |
| noncitizen_group | medicaid_exit_next | 2 | citizen | citizen | 1.0 | True | True |
| pov_band | medicaid_exit_next | 4 | pov_2_4 | pov_2_4 | 1.0 | True | True |
| snap_group | medicaid_exit_next | 2 | snap_no | snap_no | 1.0 | True | True |
| snap_group | medicaid_exit_to_uninsured_next | 2 | snap_no | snap_no | 1.0 | True | True |
| age_band | medicaid_exit_next | 5 | age_18_25 | age_18_25 | 0.7 | True | True |
| age_band | medicaid_exit_to_uninsured_next | 5 | age_26_44 | age_18_25 | 0.6 | False | False |
| pov_band | medicaid_exit_to_uninsured_next | 4 | pov_2_4 | pov_2_4 | 0.2 | True | False |
| state_baseline_tertile | medicaid_exit_next | 3 | high | mid | -0.5 | False | False |
| state_baseline_tertile | medicaid_exit_to_uninsured_next | 3 | high | mid | -0.5 | False | False |
| female_group | medicaid_exit_to_uninsured_next | 2 | female | male | -1.0 | False | False |

## Notes

- `renewal_due_rate` remains omitted because the staged CMS updated-renewal files do not expose a clean shared denominator for that rate.
- Raw count variants are retained for breadth, but they remain size-loaded and are excluded from the gate choice.
- `lag2` is only retained where support remains large enough.
