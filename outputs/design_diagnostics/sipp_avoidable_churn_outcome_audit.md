# SIPP Avoidable Churn Outcome Audit

## Purpose

This audit checks which short-horizon churn outcomes are actually supportable in the current corrected `SIPP 2021-2023` stack.

The original hope was to use literal `exit -> return to Medicaid` outcomes.
This audit shows whether that is realistic or too sparse.

## Continuity Support

| horizon | rows_supported | weighted_support_rate |
| --- | --- | --- |
| plus_1 | 1280399 | 1.0 |
| plus_2 | 1162339 | 0.9999 |
| plus_3 | 1044613 | 0.9999 |

## Core Aug-Oct H2 Outcome Support

| reference_year | outcome | event_rows | event_rate_weighted | keep_for_burden_round |
| --- | --- | --- | --- | --- |
| 2021 | persistent_uninsured_h2 | 20 | 0.001166 | True |
| 2021 | uninsured_gap_resolved_h2 | 1 | 1.6e-05 | False |
| 2021 | broad_exit_resolved_insured_h2 | 34 | 0.001456 | True |
| 2021 | broad_exit_persistent_uninsured_h2 | 20 | 0.001166 | True |
| 2021 | broad_exit_to_private_h2 | 30 | 0.001256 | True |
| 2021 | broad_exit_to_public_h2 | 6 | 0.000274 | False |
| 2021 | broad_exit_back_to_medicaid_h2 | 1 | 1.6e-05 | False |
| 2022 | persistent_uninsured_h2 | 19 | 0.001019 | True |
| 2022 | uninsured_gap_resolved_h2 | 0 | 0.0 | False |
| 2022 | broad_exit_resolved_insured_h2 | 49 | 0.002175 | True |
| 2022 | broad_exit_persistent_uninsured_h2 | 19 | 0.001019 | True |
| 2022 | broad_exit_to_private_h2 | 42 | 0.001947 | True |
| 2022 | broad_exit_to_public_h2 | 9 | 0.000311 | False |
| 2022 | broad_exit_back_to_medicaid_h2 | 0 | 0.0 | False |
| 2023 | persistent_uninsured_h2 | 64 | 0.002933 | True |
| 2023 | uninsured_gap_resolved_h2 | 3 | 0.000255 | False |
| 2023 | broad_exit_resolved_insured_h2 | 75 | 0.005024 | True |
| 2023 | broad_exit_persistent_uninsured_h2 | 65 | 0.002984 | True |
| 2023 | broad_exit_to_private_h2 | 61 | 0.004386 | True |
| 2023 | broad_exit_to_public_h2 | 20 | 0.000976 | False |
| 2023 | broad_exit_back_to_medicaid_h2 | 1 | 7e-05 | False |

## Retained For Burden Diagnostics

- `broad_exit_persistent_uninsured_h2`
- `broad_exit_resolved_insured_h2`
- `broad_exit_to_private_h2`
- `persistent_uninsured_h2`

## Omitted Or Deprioritized

- `broad_exit_back_to_medicaid_h2`
- `broad_exit_to_public_h2`
- `eligible_medicaid_transition_h2`
- `uninsured_gap_resolved_h2`

## Main Takeaways

- `t+2` support is strong enough to use a short-horizon outcome layer.
- Literal `exit -> back to pure Medicaid by t+2` is too sparse to be a main outcome in this stack.
- The most usable harmful short-horizon candidate is `persistent_uninsured_h2`.
- The most usable contrast outcome is `broad_exit_resolved_insured_h2`.
