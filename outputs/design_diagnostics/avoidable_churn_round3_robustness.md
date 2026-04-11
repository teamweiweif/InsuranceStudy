# Avoidable Churn Round-3 Robustness

## Purpose

This round advances the next locked testing order:

1. outcome robustness around persistence definitions
2. exposure decomposition around the leading burden candidate

The goal is to test whether the current `avoidable churn` branch remains coherent under nearby outcome definitions and whether the leading composite candidate still earns its place when compared with its components.

## 2023 Core Outcome Support

| outcome | support_rows | support_weight | event_rate_weighted |
| --- | --- | --- | --- |
| medicaid_exit_to_uninsured_next | 21847 | 208140509.34 | 0.003178 |
| persistent_uninsured_h2 | 21794 | 207450502.08 | 0.002933 |
| broad_exit_persistent_uninsured_h2 | 21794 | 207450502.08 | 0.002984 |
| persistent_uninsured_h3 | 14519 | 138213910.95 | 0.002668 |
| broad_exit_resolved_insured_h2 | 21794 | 207450502.08 | 0.005024 |

## Outcome Robustness: Best Nonlead Alignment By Outcome

| outcome | window | alignment | weighted_corr | high_minus_low | direction_flag |
| --- | --- | --- | --- | --- | --- |
| broad_exit_persistent_uninsured_h2 | core_aug_oct_2023 | same | 0.1438 | 0.0025 | expected |
| broad_exit_persistent_uninsured_h2 | mature_jun_oct_2023 | same | 0.1288 | 0.0027 | expected |
| broad_exit_resolved_insured_h2 | core_aug_oct_2023 | lag1 | -0.0457 | -0.0037 | expected |
| broad_exit_resolved_insured_h2 | mature_jun_oct_2023 | lag1 | -0.0395 | -0.0023 | expected |
| medicaid_exit_to_uninsured_next | core_aug_oct_2023 | same | 0.1636 | 0.003 | expected |
| medicaid_exit_to_uninsured_next | mature_jun_oct_2023 | same | 0.142 | 0.003 | expected |
| persistent_uninsured_h2 | core_aug_oct_2023 | same | 0.1407 | 0.0024 | expected |
| persistent_uninsured_h2 | mature_jun_oct_2023 | same | 0.1269 | 0.0026 | expected |
| persistent_uninsured_h3 | core_aug_oct_2023 | same | 0.1933 | 0.0029 | expected |
| persistent_uninsured_h3 | mature_jun_oct_2023 | same | 0.15 | 0.003 | expected |

## Outcome Robustness: Falsification For `backlog_automation_index / same`

| exposure_variant | alignment | outcome | pre_2021_contrast | pre_2022_contrast | unwinding_2023_contrast | max_pre_abs_contrast | same_direction_big_pre | falsification_pass_outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backlog_automation_index | same | medicaid_exit_to_uninsured_next | 0.0009 | 0.0007 | 0.0023 | 0.0009 | False | True |
| backlog_automation_index | same | persistent_uninsured_h2 | 0.0009 | 0.0007 | 0.0016 | 0.0009 | False | True |
| backlog_automation_index | same | broad_exit_persistent_uninsured_h2 | 0.0009 | 0.0007 | 0.0018 | 0.0009 | False | True |
| backlog_automation_index | same | persistent_uninsured_h3 | 0.0002 | 0.0019 | 0.0027 | 0.0019 | False | True |
| backlog_automation_index | same | broad_exit_resolved_insured_h2 | -0.0004 | -0.0014 | -0.0026 | 0.0014 | False | True |

## Exposure Decomposition: Top Nonlead Rankings In Core Window

| exposure_family | exposure_variant | exposure_kind | window | alignment | mean_signed_corr_all | all_expected_direction | outcomes_used |
| --- | --- | --- | --- | --- | --- | --- | --- |
| backlog_automation_composite | backlog_automation_rank_index | composite_rank | core_aug_oct_2023 | same | 0.1482 | True | 3 |
| backlog_automation_composite | backlog_automation_index | composite_z | core_aug_oct_2023 | same | 0.1242 | True | 3 |
| pending_backlog_component | pending_rate | component | core_aug_oct_2023 | same | 0.1128 | True | 3 |
| backlog_automation_composite | backlog_automation_rank_index | composite_rank | core_aug_oct_2023 | lead1 | 0.0875 | False | 3 |
| backlog_automation_composite | backlog_automation_index | composite_z | core_aug_oct_2023 | lead1 | 0.0858 | False | 3 |

## Exposure Decomposition: Top Nonlead Rankings In Mature Window

| exposure_family | exposure_variant | exposure_kind | window | alignment | mean_signed_corr_all | all_expected_direction | outcomes_used |
| --- | --- | --- | --- | --- | --- | --- | --- |
| backlog_automation_composite | backlog_automation_rank_index | composite_rank | mature_jun_oct_2023 | same | 0.1362 | True | 3 |
| backlog_automation_composite | backlog_automation_index | composite_z | mature_jun_oct_2023 | same | 0.1105 | True | 3 |
| backlog_automation_composite | backlog_automation_rank_index | composite_rank | mature_jun_oct_2023 | lag1 | 0.1002 | True | 3 |
| pending_backlog_component | pending_rate | component | mature_jun_oct_2023 | same | 0.0945 | True | 3 |
| backlog_automation_composite | backlog_automation_rank_index | composite_rank | mature_jun_oct_2023 | lead1 | 0.087 | False | 3 |

## Exposure Decomposition: Falsification On `persistent_uninsured_h2`

| exposure_variant | alignment | outcome | pre_2021_contrast | pre_2022_contrast | unwinding_2023_contrast | max_pre_abs_contrast | falsification_pass_outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pending_rate | same | persistent_uninsured_h2 | -0.0007 | -0.0005 | 0.0027 | 0.0007 | True |
| ex_parte_renewal_rate | same | persistent_uninsured_h2 | -0.0015 | -0.0009 | -0.0018 | 0.0015 | True |
| backlog_automation_index | same | persistent_uninsured_h2 | 0.0009 | 0.0007 | 0.0016 | 0.0009 | True |
| backlog_automation_rank_index | same | persistent_uninsured_h2 | 0.0006 | 0.0006 | 0.0017 | 0.0006 | True |
| backlog_form_index | same | persistent_uninsured_h2 | 0.0008 | 0.0005 | 0.0022 | 0.0008 | True |

## Interpretation

- Outcome robustness is better if at least two harmful persistence-style outcomes retain an expected-sign `same` or `lag1` signal across both windows.
- Exposure decomposition is better if the backlog-automation composite stays competitive relative to `pending_rate` and `ex_parte_renewal_rate`, rather than collapsing once it is unpacked.
- This round still treats `lead1` as informative but not sufficient for a clean upgrade.

## Summary Verdict

- verdict: `ROUND3_SUPPORTS_CONTINUATION`
- outcome exposure used for robustness: `backlog_automation_index`
- robust harmful outcomes found: `4`
- composite falsification pass on `persistent_uninsured_h2`: `True`
- pending-only falsification pass on `persistent_uninsured_h2`: `True`
- ex-parte-only falsification pass on `persistent_uninsured_h2`: `True`
