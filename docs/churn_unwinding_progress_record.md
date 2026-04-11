# Churn / Unwinding Progress Record

Last updated: `2026-04-11`

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

## Current Control Documents

If a new agent starts now, the preferred reading order is:

1. [churn_unwinding_execution_handoff.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_execution_handoff.md)
2. [churn_unwinding_round2_execution_handoff.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round2_execution_handoff.md)
3. [churn_unwinding_round2_diagnostics_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round2_diagnostics_memo.md)
4. [churn_unwinding_administrative_burden_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_administrative_burden_memo.md)
5. [churn_unwinding_avoidable_churn_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_avoidable_churn_memo.md)
6. [churn_unwinding_outcome_reassessment_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_outcome_reassessment_memo.md)
7. [churn_unwinding_avoidable_churn_results_briefing.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_avoidable_churn_results_briefing.md)
8. [churn_unwinding_next_tests_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_next_tests_memo.md)
9. [churn_unwinding_round3_robustness_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_round3_robustness_memo.md)
10. [churn_unwinding_paper_strategy_memo.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/churn_unwinding_paper_strategy_memo.md)
