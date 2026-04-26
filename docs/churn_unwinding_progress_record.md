# Churn / Unwinding Progress Record

Last updated: `2026-04-26`

## Purpose

This is a compact dated progress ledger for the `SIPP + CMS Medicaid unwinding` line.

Use it to answer:

- what has already been done
- what was concluded at each step
- which document now controls the next step

## 2026-04-10: Stack Reset And Feasibility Consolidation

Main outcome:

- the project formally shifted the active frontier away from `Medicare@65` and toward `coverage churn / Medicaid unwinding / continuity of coverage`

Recorded in:

- [current_exploration_handoff.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/current_exploration_handoff.md)
- [churn_unwinding_execution_handoff.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_execution_handoff.md)
- [public_data_feasibility_audit.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/public_data_feasibility_audit.md)

Key points:

- `SIPP` confirmed as the strongest public-use base for churn and unwinding
- `CMS` unwinding files successfully linked into the prototype stack
- `HPS`, `NHIS`, `MEPS`, and `MCBS` feasibility was audited
- the design was explicitly reset away from premature targeting claims

## 2026-04-10: First-Round Diagnostics Locked

Main outcome:

- first-round diagnostics established the initial core window and exposed the main weaknesses

Recorded in:

- [churn_unwinding_design_diagnostics_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_design_diagnostics_memo.md)
- [churn_targeting_reset_2026-04-10.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_targeting_reset_2026-04-10.md)

Key points:

- core unwinding window set to `August-November 2023`
- timing was still unstable
- `pending_pressure` looked more informative than the originally preferred mechanism
- state-level baseline heterogeneity was not stable enough for policy targeting

## 2026-04-10: Unattended Round-2 Diagnostics Executed

Main outcome:

- the stack moved from rough diagnostics to a fuller `design diagnostics first` implementation

Recorded in:

- [churn_unwinding_round2_execution_handoff.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round2_execution_handoff.md)
- [churn_unwinding_round2_diagnostics_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round2_diagnostics_memo.md)
- [churn_unwinding_administrative_burden_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_administrative_burden_memo.md)

Key points:

- first-round diagnostics were rerun and reproduced
- a `2021-2023` subgroup feature stack was built
- retained subgroup families:
  - `age_band`
  - `female_group`
  - `foreign_born_group`
  - `household_child_group`
  - `noncitizen_group`
  - `pov_band`
  - `snap_group`
- dropped due to high missingness:
  - `employed_group`
  - `disability_group`
- theory framing was reset from narrow `procedural friction` to broader `administrative renewal burden`
- under the implemented gate rule, the chosen exposure became:
  - `manual_renewal_burden / renewal_form_rate / lag1`
- final round-2 verdict:
  - `GO_RISK_ONLY`

## 2026-04-10: Risk Pilot And Lightweight External Checks

Main outcome:

- the stack cleared the narrow threshold for bounded risk work but not for causal escalation

Recorded in:

- [risk_prediction_pilot.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/risk_prediction_pilot.md)
- [hps_unwinding_crosscheck.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/hps_unwinding_crosscheck.md)
- [nhis_public_validation_feasibility.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/nhis_public_validation_feasibility.md)

Key points:

- subgroup-based logistic materially outperformed naive state baseline risk
- `HPS` provided only partial external echo
- `NHIS` public files were confirmed as unsuitable for state-period merge validation

## 2026-04-11: Paper-Strategy Interpretation Added

Main outcome:

- the current stack was translated into a paper-strategy view for future agents and for project-level decision making

Recorded in:

- [churn_unwinding_paper_strategy_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_paper_strategy_memo.md)

Key points:

- current best positioning is `data-driven policy / administrative burden / vulnerability / prioritization`
- current stack is not yet ready to carry the full `causal ML / DML` ambition
- the line is worth continuing, but under a restrained `risk-first` interpretation

## 2026-04-11: Avoidable-Churn Experiments Added

Main outcome:

- the project moved from generic churn diagnostics to a more targeted `avoidable churn` branch

Recorded in:

- [churn_unwinding_avoidable_churn_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_avoidable_churn_memo.md)
- [avoidable_churn_burden_diagnostics.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_burden_diagnostics.md)
- [hps_avoidable_churn_crosscheck.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/hps_avoidable_churn_crosscheck.md)

Key points:

- literal `exit -> return to pure Medicaid` was audited and found too sparse
- the usable harmful short-horizon outcome is now `persistent_uninsured_h2`
- the usable contrast outcome is `broad_exit_resolved_insured_h2`
- the strongest new candidate is now:
  - `backlog_automation_index / same`
- this candidate stayed positive in both `core_aug_oct_2023_h2` and `mature_jun_oct_2023_h2`
- matched pre-period falsification for the candidate was weaker than the unwinding-year contrast
- the HPS external cross-check now lines up in expected directions
- the avoidable-churn branch verdict is:
  - `PROMISING_H2_UPGRADE`

## 2026-04-11: Outcome Reassessment And Reporting Convention Locked

Main outcome:

- the project formally reassessed the new `avoidable churn` outcome choice against official definitions, policy logic, and literature

Recorded in:

- [churn_unwinding_outcome_reassessment_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_outcome_reassessment_memo.md)
- [empirical_result_reporting_convention.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/empirical_result_reporting_convention.md)

Key points:

- `persistent_uninsured_h2` is not a standard CMS published metric, but it is conceptually defensible
- the support comes from:
  - official unwinding concepts around procedural terminations, pending renewals, and ex parte renewals
  - official evidence that renewal outcomes can resolve over multiple months
  - literature and policy work treating coverage gaps and continuity as meaningful outcomes
- the outcome change is best understood as:
  - a measurement upgrade
  - and a sharpening toward `avoidable harmful churn`
- it is not a full pivot to a different research domain
- future empirical reporting is now locked to a structured format that must always define:
  - `Question`
  - `Sample / Unit`
  - `Outcome`
  - `Treatment / Exposure`
  - `Purpose`
  - `Numerical Result`
  - `Interpretation`
  - `Evaluation`
  - `Caveat`

## 2026-04-11: Results Briefing And Next-Test Order Added

Main outcome:

- the current avoidable-churn branch was translated into a plain-language results briefing and a prioritized next-test sequence

Recorded in:

- [churn_unwinding_avoidable_churn_results_briefing.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_avoidable_churn_results_briefing.md)
- [churn_unwinding_next_tests_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_next_tests_memo.md)

Key points:

- the current branch now has a user-facing memo that clearly defines:
  - question
  - sample
  - outcome
  - exposure
  - purpose
  - numerical result
  - interpretation
  - evaluation
  - caveat
- the next recommended empirical order is now locked as:
  - outcome robustness
  - exposure decomposition
  - timing stress tests
  - subgroup stability round 2
  - risk-ranking round 2
- the project has already used the time dimension seriously for diagnostics
- but the next useful work is still `dynamic robustness`, not classical time-series modeling

## 2026-04-11: Round-3 Robustness And External Echo Added

Main outcome:

- the project completed the first two priorities from the next-test order and updated the strongest current burden candidate

Recorded in:

- [churn_unwinding_round3_robustness_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round3_robustness_memo.md)
- [avoidable_churn_round3_robustness.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_round3_robustness.md)
- [hps_avoidable_churn_round3_crosscheck.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/hps_avoidable_churn_round3_crosscheck.md)

Key points:

- the outcome side is now materially more robust:
  - the burden signal survives not only on `medicaid_exit_to_uninsured_next`
  - but also on `persistent_uninsured_h2`
  - `broad_exit_persistent_uninsured_h2`
  - and `persistent_uninsured_h3`
- the leading exposure candidate has improved from:
  - `backlog_automation_index / same`
  - to:
  - `backlog_automation_rank_index / same`
- the new rank-based composite beats:
  - the old z-score composite
  - and `pending_rate` alone
  in both the core and mature windows
- a new HPS cross-check shows a stronger external echo for the new candidate
- the round-3 verdict is now:
  - `ROUND3_SUPPORTS_CONTINUATION`
- the next active empirical frontier should now shift to:
  - timing stress tests
  - subgroup stability round 2

## 2026-04-11: Round-4 Step 1 Timing Stress Tests Completed

Main outcome:

- the first step from the operational plan was executed and explicitly closed

Recorded in:

- [churn_unwinding_operational_plan_2026-04-11.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_operational_plan_2026-04-11.md)
- [avoidable_churn_timing_stress_round4.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md)
- [avoidable_churn_timing_stress_matrix.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_timing_stress_matrix.csv)
- [avoidable_churn_timing_placebo_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_timing_placebo_summary.csv)

Key points:

- the run followed only `Step 1` from the operational plan
- no broad topic search or alternative dataset exploration was opened
- no `DID`, `DML`, causal ML, event-study, or targeting work was started
- the primary candidate remained:
  - `backlog_automation_rank_index / same`
- in the two primary windows, the primary candidate's aggregate signed scores were:
  - `core_aug_oct_2023`: `0.1722`
  - `mature_jun_oct_2023`: `0.1509`
- the future-month `lead1` placebo did not dominate the best non-lead alignment:
  - core `lead1 - best nonlead`: `-0.0462`
  - mature `lead1 - best nonlead`: `-0.0410`
- the candidate ranked first among tested non-lead alternatives in both primary windows
- phase splitting is feasible from May onward, but late-window evidence is narrower because h2/h3 horizons truncate support
- the explicit Step 1 verdict is:
  - `STEP1_TIMING_STRESS_PASSED_WITH_CAVEAT`
- the main caveat is:
  - timing looks better on aggregate, but this remains a diagnostic state-month screen
- Step 2 is now unlocked under the operational plan:
  - `Subgroup Stability Round 2 On The New Outcome Layer`

## 2026-04-26: Round-4 Step 2 Subgroup Stability Round 2 Completed

Main outcome:

- the operational-plan Step 2 subgroup-stability diagnostic was executed on the upgraded avoidable-churn outcome layer

Recorded in:

- [avoidable_churn_subgroup_stability_round2.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2.md)
- [avoidable_churn_subgroup_stability_round2_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2_summary.csv)
- [avoidable_churn_subgroup_ordering_tables.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_subgroup_ordering_tables.csv)
- [build_avoidable_churn_subgroup_stability_round2.py](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/design_diagnostics/build_avoidable_churn_subgroup_stability_round2.py)

Key points:

- the run compared pooled `2021-2022` subgroup ordering against `2023` ordering
- primary harmful outcomes:
  - `persistent_uninsured_h2`
  - `broad_exit_persistent_uninsured_h2`
- contrast outcome:
  - `broad_exit_resolved_insured_h2`
- in the primary `core_aug_oct_2023` window, three subgroup families were stable on both harmful outcomes:
  - `foreign_born_group`
  - `household_child_group`
  - `snap_group`
- the upgraded `persistent_uninsured_h2` layer improved relative to the earlier narrow `medicaid_exit_to_uninsured_next` subgroup round:
  - old stable family count: `2`
  - new stable family count: `3`
  - old mean Spearman: `-0.0286`
  - new mean Spearman: `0.2571`
- the explicit Step 2 verdict is:
  - `SUBGROUP_STABILITY_ROUND2_SUPPORTS_RISK_RANKING`
- Step 3 is now unlocked under the operational plan:
  - `Risk-Ranking Round 2`
- this does not unlock causal ML, DML, event-study, DID, causal forest, or causal targeting work

## 2026-04-26: Round-4 Step 3 Risk-Ranking Round 2 Completed

Main outcome:

- the operational-plan Step 3 risk-ranking diagnostic was executed on the upgraded avoidable-churn outcome layer

Recorded in:

- [avoidable_churn_risk_round2.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_risk_round2.md)
- [avoidable_churn_risk_round2_metrics.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_risk_round2_metrics.csv)
- [avoidable_churn_risk_round2_calibration.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_risk_round2_calibration.csv)
- [avoidable_churn_risk_round2_group_calibration.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_risk_round2_group_calibration.csv)
- [run_avoidable_churn_risk_round2.py](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/design_diagnostics/run_avoidable_churn_risk_round2.py)

Key points:

- training setup:
  - train on `2021-2022`
  - test on `2023`
  - core months `8-10`
  - retained subgroup-family predictors only
- primary outcome:
  - `persistent_uninsured_h2`
- benchmark outcome:
  - `medicaid_exit_to_uninsured_next`
- primary outcome, AUC-leading model:
  - `weighted_logistic`
  - AUC `0.5570`
  - PR AUC `0.0049`
  - top-decile capture `0.1057`
  - AUC gain over naive state baseline `0.1391`
- primary outcome, top-decile-capture-leading model:
  - `compact_boosting`
  - AUC `0.5389`
  - PR AUC `0.0046`
  - top-decile capture `0.1966`
  - top-decile capture gain over naive state baseline `0.1570`
- benchmark outcome, weighted logistic:
  - AUC `0.5633`
  - PR AUC `0.0052`
  - top-decile capture `0.1222`
- comparison against the old risk pilot is mixed:
  - benchmark AUC delta versus old pilot logistic: `-0.0850`
  - benchmark top-decile capture delta versus old pilot logistic: `0.0145`
- the explicit Step 3 verdict is:
  - `RISK_RANKING_ROUND2_MIXED_WITH_CAVEAT`
- Step 4 is unlocked only as a paper-path decision memo:
  - `docs/churn_unwinding_post_round4_path_decision.md`
- no causal ML, DML, event-study, DID, causal forest, or causal targeting work is unlocked

## Current Control Documents

If a new agent starts now, the preferred reading order is:

1. [churn_unwinding_execution_handoff.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_execution_handoff.md)
2. [churn_unwinding_operational_plan_2026-04-11.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_operational_plan_2026-04-11.md)
3. [churn_unwinding_round2_execution_handoff.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round2_execution_handoff.md)
4. [churn_unwinding_round2_diagnostics_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round2_diagnostics_memo.md)
5. [churn_unwinding_administrative_burden_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_administrative_burden_memo.md)
6. [churn_unwinding_avoidable_churn_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_avoidable_churn_memo.md)
7. [churn_unwinding_outcome_reassessment_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_outcome_reassessment_memo.md)
8. [churn_unwinding_avoidable_churn_results_briefing.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_avoidable_churn_results_briefing.md)
9. [churn_unwinding_next_tests_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_next_tests_memo.md)
10. [churn_unwinding_round3_robustness_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round3_robustness_memo.md)
11. [churn_unwinding_paper_strategy_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_paper_strategy_memo.md)
