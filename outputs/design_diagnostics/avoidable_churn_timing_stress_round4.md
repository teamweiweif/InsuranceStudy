# Avoidable Churn Timing Stress Round 4

Last updated: `2026-04-11`

## Purpose

This file records Step 1 from `docs/churn_unwinding_operational_plan_2026-04-11.md`.

It only tests timing discipline for the current avoidable harmful churn branch. It does not open DID, event-study, DML, causal-forest, or targeting work.

## Result 1: Distributed Timing Comparison

### Question

Does the current top burden candidate remain credible when same-month, lagged, and future-month alignments are compared directly?

### Sample / Unit

- Data: corrected `SIPP 2021-2023` avoidable-churn state-month cells produced in the prior round.
- Unit: `state-month` cells aggregated from person-month observations.
- Main year: `2023`.
- Main windows: `core_aug_oct_2023` and `mature_jun_oct_2023`.
- Sensitivity window: `expanded_may_oct_2023`, used because monthly state support is acceptable from May onward.

### Outcome

- `medicaid_exit_to_uninsured_next`
- `persistent_uninsured_h2`
- `broad_exit_persistent_uninsured_h2`
- `persistent_uninsured_h3`
- `broad_exit_resolved_insured_h2` as the contrast outcome

### Treatment / Exposure

- Primary exposure: `backlog_automation_rank_index`.
- Comparison exposures: `backlog_automation_index`, `pending_rate`, `ex_parte_renewal_rate`, and legacy `renewal_form_rate`.

### Purpose

The purpose is to test whether the current branch is mainly a future-month or lead-driven pattern, or whether non-lead alignments remain competitive.

### Numerical Result

| window | alignment | mean_signed_corr_all | mean_signed_corr_harm | all_expected_direction | outcomes_used |
| --- | --- | --- | --- | --- | --- |
| core_aug_oct_2023 | same | 0.1722 | 0.2038 | True | 5 |
| core_aug_oct_2023 | lead1 | 0.126 | 0.178 | False | 5 |
| core_aug_oct_2023 | lag1 | 0.1032 | 0.122 | True | 5 |
| core_aug_oct_2023 | lag2 | 0.0335 | 0.0483 | False | 5 |
| mature_jun_oct_2023 | same | 0.1509 | 0.1711 | True | 5 |
| mature_jun_oct_2023 | lag1 | 0.1214 | 0.1444 | True | 5 |
| mature_jun_oct_2023 | lead1 | 0.1099 | 0.1421 | False | 5 |
| mature_jun_oct_2023 | lag2 | 0.0512 | 0.0666 | False | 5 |

Best non-lead comparison across exposure candidates:

| window | exposure_variant | alignment | mean_signed_corr_all | all_expected_direction | outcomes_used |
| --- | --- | --- | --- | --- | --- |
| core_aug_oct_2023 | backlog_automation_rank_index | same | 0.1722 | True | 5 |
| core_aug_oct_2023 | backlog_automation_index | same | 0.142 | True | 5 |
| core_aug_oct_2023 | pending_rate | same | 0.1141 | True | 5 |
| core_aug_oct_2023 | ex_parte_renewal_rate | same | 0.0962 | True | 5 |
| core_aug_oct_2023 | renewal_form_rate | lag1 | 0.0471 | True | 5 |
| mature_jun_oct_2023 | backlog_automation_rank_index | same | 0.1509 | True | 5 |
| mature_jun_oct_2023 | backlog_automation_index | same | 0.1221 | True | 5 |
| mature_jun_oct_2023 | ex_parte_renewal_rate | same | 0.0921 | False | 5 |
| mature_jun_oct_2023 | pending_rate | same | 0.0884 | True | 5 |
| mature_jun_oct_2023 | renewal_form_rate | lag1 | 0.007 | False | 5 |

### Interpretation

The current top candidate remains strongest among the tested non-lead alternatives in the two primary windows. The best aggregate alignment is `same` in both primary windows.

### Evaluation

- Step 1 verdict: `STEP1_TIMING_STRESS_PASSED_WITH_CAVEAT`
- Non-lead competitive across primary windows: `True`
- Current candidate better than main alternatives: `True`

### Caveat

- Timing looks better on aggregate, but this remains a diagnostic state-month screen.

## Result 2: Placebo Month-Shift Check

### Question

Does the future-month `lead1` alignment dominate the current candidate once it is treated as a timing placebo?

### Sample / Unit

- Data: same `SIPP 2021-2023` state-month cells.
- Unit: `state-month`.
- Main year: `2023`.
- Main windows: `core_aug_oct_2023` and `mature_jun_oct_2023`.

### Outcome

The check averages the signed timing score across the five locked outcome definitions.

### Treatment / Exposure

- Primary exposure: `backlog_automation_rank_index`.
- Placebo alignment: `lead1`, interpreted as a future-month burden value assigned to the current outcome month.

### Purpose

The purpose is to see whether the signal collapses into future exposure timing rather than same-month or lagged timing.

### Numerical Result

| window | same_mean_signed_corr | lag1_mean_signed_corr | lag2_mean_signed_corr | future_placebo_lead1_mean_signed_corr | best_nonlead_alignment | best_nonlead_mean_signed_corr | lead1_minus_best_nonlead | nonlead_competitive | future_placebo_dominates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| core_aug_oct_2023 | 0.1722 | 0.1032 | 0.0335 | 0.126 | same | 0.1722 | -0.0462 | True | False |
| mature_jun_oct_2023 | 0.1509 | 0.1214 | 0.0512 | 0.1099 | same | 0.1509 | -0.041 | True | False |

### Interpretation

The future-month placebo does not dominate the best non-lead alignment for the primary candidate in the two primary windows.

### Evaluation

- Encouraging for a timing diagnostic.
- Still diagnostic rather than causal.

### Caveat

- `lead1` remains informative in some individual outcome rows and should not be ignored later.

## Result 3: Phase Split And Expanded-Window Support

### Question

Does the candidate remain directionally usable when the window is split into supportable early/core/late phases?

### Sample / Unit

- Data: same state-month cells.
- Phase windows: `phase_early_may_jul_2023`, `phase_core_aug_oct_2023`, and `phase_late_sep_oct_2023`.

### Outcome

The phase check uses the same locked outcome family, with special attention to support for `persistent_uninsured_h2` and `persistent_uninsured_h3`.

### Treatment / Exposure

- Primary exposure: `backlog_automation_rank_index`.

### Purpose

The purpose is to document whether an early or phase-specific timing split is feasible without forcing unsupported months.

### Numerical Result

Support check:

| stress_test | window | outcome | months_requested | months_used | min_state_cells_per_used_month | support_rows | support_flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| distributed_timing | expanded_may_oct_2023 | persistent_uninsured_h2 | 5,6,7,8,9,10 | 5,6,7,8,9,10 | 37 | 39207 | True |
| distributed_timing | expanded_may_oct_2023 | persistent_uninsured_h3 | 5,6,7,8,9,10 | 5,6,7,8,9 | 37 | 31889 | True |
| phase_split | phase_early_may_jul_2023 | persistent_uninsured_h2 | 5,6,7 | 5,6,7 | 37 | 17413 | True |
| phase_split | phase_early_may_jul_2023 | persistent_uninsured_h3 | 5,6,7 | 5,6,7 | 37 | 17370 | True |
| phase_split | phase_late_sep_oct_2023 | persistent_uninsured_h2 | 9,10 | 9,10 | 51 | 14505 | True |
| phase_split | phase_late_sep_oct_2023 | persistent_uninsured_h3 | 9,10 | 9 | 51 | 7246 | True |

Phase timing summary:

| window | best_nonlead_alignment | best_nonlead_mean_signed_corr | future_placebo_lead1_mean_signed_corr | nonlead_competitive | future_placebo_dominates |
| --- | --- | --- | --- | --- | --- |
| phase_core_aug_oct_2023 | same | 0.1722 | 0.126 | True | False |
| phase_early_may_jul_2023 | lag1 | 0.1573 | 0.0811 | True | False |
| phase_late_sep_oct_2023 | same | 0.0412 | -0.0057 | True | False |

### Interpretation

The expanded and phase-split windows are supportable from May onward. March-April are not used in the expanded window because CMS state coverage is below the monthly state-cell support rule.

### Evaluation

- Phase splitting is feasible as a diagnostic stress test.
- It does not by itself validate stronger identification.

### Caveat

- Late-window support is constrained by h2/h3 horizon truncation, so late phase evidence is narrower than the core window.

## Closure Test

- At least one non-lead alignment remains competitive across nearby windows: `True`
- The current top candidate still looks better than the main alternatives after timing stress: `True`
- Explicit Step 1 verdict: `STEP1_TIMING_STRESS_PASSED_WITH_CAVEAT`
- Step 2 unlocked: `True`

## Main Caveat

Timing looks better on aggregate, but this remains a diagnostic state-month screen.

## Artifacts

- `outputs/design_diagnostics/avoidable_churn_timing_stress_matrix.csv`
- `outputs/design_diagnostics/avoidable_churn_timing_placebo_summary.csv`
- `scripts/design_diagnostics/build_avoidable_churn_timing_stress_round4.py`
