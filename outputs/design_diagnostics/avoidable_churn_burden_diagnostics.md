# Avoidable Churn Burden Diagnostics

## Purpose

This round tests whether short-horizon `avoidable churn` outcomes are more informative than the original one-step uninsured exit outcome.

The main comparison is between:

- `medicaid_exit_to_uninsured_next`
- `persistent_uninsured_h2`
- `broad_exit_resolved_insured_h2`

and between:

- single burden indicators
- small composite burden indices

## 2023 Core H2 Support

| MONTHCODE | state_cells | eligible_rows_h2 | eligible_weight_h2 |
| --- | --- | --- | --- |
| 8.0 | 51.0 | 7289.0 | 69605876.44908981 |
| 9.0 | 51.0 | 7271.0 | 69166098.78273985 |
| 10.0 | 51.0 | 7234.0 | 68678526.84992746 |

## Top Ranking: Core Window

| exposure_family | exposure_variant | exposure_kind | window | alignment | mean_signed_corr_all | mean_signed_corr_harm_only | all_expected_direction | outcomes_used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| composite_burden_index | backlog_automation_index | composite | core_aug_oct_2023_h2 | lead1 | 0.1618 | 0.2675 | False | 3 |
| composite_burden_index | backlog_form_index | composite | core_aug_oct_2023_h2 | lead1 | 0.1481 | 0.2107 | True | 3 |
| ex_parte_renewal_relief | ex_parte_renewal_rate | single | core_aug_oct_2023_h2 | lead1 | 0.1355 | 0.2034 | False | 3 |
| composite_burden_index | backlog_automation_index | composite | core_aug_oct_2023_h2 | same | 0.1242 | 0.1522 | True | 3 |
| pending_backlog_burden | pending_rate | single | core_aug_oct_2023_h2 | same | 0.1127 | 0.1342 | True | 3 |
| pending_backlog_burden | pending_rate | single | core_aug_oct_2023_h2 | lead1 | 0.0888 | 0.1678 | False | 3 |
| manual_renewal_burden | renewal_form_rate | single | core_aug_oct_2023_h2 | lead1 | 0.0884 | 0.0853 | True | 3 |
| composite_burden_index | full_burden_index | composite | core_aug_oct_2023_h2 | lead1 | 0.0785 | 0.1139 | True | 3 |

## Top Ranking: Mature Window

| exposure_family | exposure_variant | exposure_kind | window | alignment | mean_signed_corr_all | mean_signed_corr_harm_only | all_expected_direction | outcomes_used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| composite_burden_index | backlog_automation_index | composite | mature_jun_oct_2023_h2 | lead1 | 0.1165 | 0.1733 | True | 3 |
| composite_burden_index | backlog_automation_index | composite | mature_jun_oct_2023_h2 | same | 0.1105 | 0.1345 | True | 3 |
| ex_parte_renewal_relief | ex_parte_renewal_rate | single | mature_jun_oct_2023_h2 | lead1 | 0.1009 | 0.1771 | False | 3 |
| pending_backlog_burden | pending_rate | single | mature_jun_oct_2023_h2 | same | 0.0944 | 0.0898 | True | 3 |
| composite_burden_index | backlog_automation_index | composite | mature_jun_oct_2023_h2 | lag1 | 0.0763 | 0.0947 | True | 3 |
| composite_burden_index | backlog_form_index | composite | mature_jun_oct_2023_h2 | lead1 | 0.0691 | 0.0786 | True | 3 |
| ex_parte_renewal_relief | ex_parte_renewal_rate | single | mature_jun_oct_2023_h2 | same | 0.069 | 0.1071 | False | 3 |
| pending_backlog_burden | pending_rate | single | mature_jun_oct_2023_h2 | lead1 | 0.0654 | 0.0688 | True | 3 |

## Candidate Selection

- verdict: `PROMISING_H2_UPGRADE`
- chosen candidate: `backlog_automation_index / same`
- core score: `0.1242`
- mature score: `0.1105`

## Candidate Falsification Check

| exposure_family | exposure_variant | alignment | outcome | pre_2021_contrast | pre_2022_contrast | unwinding_2023_contrast | max_pre_abs_contrast | same_direction_big_pre | falsification_pass_outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| composite_burden_index | backlog_automation_index | same | medicaid_exit_to_uninsured_next | 0.0009 | 0.0007 | 0.0023 | 0.0009 | False | True |
| composite_burden_index | backlog_automation_index | same | persistent_uninsured_h2 | 0.0009 | 0.0007 | 0.0016 | 0.0009 | False | True |
| composite_burden_index | backlog_automation_index | same | broad_exit_resolved_insured_h2 | -0.0004 | -0.0014 | -0.0026 | 0.0014 | False | True |

## Interpretation

- If a composite burden index stays positive on `persistent_uninsured_h2` and negative on `broad_exit_resolved_insured_h2`, that is better aligned with an avoidable-churn story than the original one-step screen.
- `lead1` can still be informative, but this memo does not treat lead-driven wins as clean upgrades.
- The main question is whether a same-month or lagged non-lead signal survives in both windows.
