# Churn / Unwinding Operational Plan

Last updated: `2026-04-11`

## Purpose

This file is the operational execution plan for the current `SIPP + CMS Medicaid unwinding` line.

It is not a brainstorming memo.
It is not a theory note.
It is not a final paper outline.

Its job is to tell the execution agent exactly what to do next, in what order, what to produce, what to avoid, and how to record progress.

## Current Locked Reading

Treat the following as the current project state unless a new artifact proves otherwise:

- The active line is `coverage churn / Medicaid unwinding / continuity of coverage`, now sharpened toward `avoidable harmful churn`.
- `SIPP` remains the strongest current public-use microdata base.
- The corrected-stack path is real enough to continue, but it is still not estimation-ready for strong causal claims.
- The current main harmful outcome family is no longer just `medicaid_exit_to_uninsured_next`; it now includes:
  - `persistent_uninsured_h2`
  - `broad_exit_persistent_uninsured_h2`
  - `persistent_uninsured_h3`
  - with `broad_exit_resolved_insured_h2` as the main contrast outcome.
- The current best burden candidate is:
  - `backlog_automation_rank_index / same`
- The current line is worth continuing as a paper candidate.
- The current line is **not yet** ready for:
  - `DID`
  - `event study`
  - `DML`
  - `causal forest`
  - causal or welfare-based `policy targeting`
- The current strongest positioning is:
  - `administrative renewal burden`
  - `avoidable harmful churn`
  - `vulnerability / prioritization / risk ranking`
  - not yet a full `causal ML` paper.

## What This Plan Is Trying To Achieve

The next phase should answer one narrower question:

- can the current `avoidable harmful churn` branch become a defensible paper core with stronger timing discipline, more credible subgroup structure, and a more mature risk-ranking layer?

This phase should **not** try to solve everything at once.

## Mandatory Reading Order Before Any New Work

Read in this order:

1. `docs/churn_unwinding_execution_handoff.md`
2. `docs/churn_unwinding_round2_execution_handoff.md`
3. `docs/churn_unwinding_round2_diagnostics_memo.md`
4. `docs/churn_unwinding_administrative_burden_memo.md`
5. `docs/churn_unwinding_avoidable_churn_memo.md`
6. `docs/churn_unwinding_outcome_reassessment_memo.md`
7. `docs/churn_unwinding_avoidable_churn_results_briefing.md`
8. `docs/churn_unwinding_next_tests_memo.md`
9. `docs/churn_unwinding_round3_robustness_memo.md`
10. `docs/churn_unwinding_paper_strategy_memo.md`
11. `docs/churn_unwinding_progress_record.md`
12. this file

Do not reopen broad upstream audit files unless needed for a concrete implementation detail.

## Do Not Do These Things In This Phase

Do not:

- reopen the main question of whether the churn / unwinding line should exist
- reopen `MEPS` as the main branch
- reopen `MCBS` as the main branch
- force `NHIS` into a state-period validation role it cannot support in public files
- automatically backfill `2018-2020`
- write final paper prose as if identification is already established
- escalate to `DID`, `DDD`, `event study`, `DML`, `causal forest`, or causal targeting language without a new explicit go decision
- replace the current mechanism umbrella `administrative renewal burden` with narrower `procedural friction` language unless the new evidence clearly supports that move

## Working Interpretation Rules

Use these interpretation rules throughout this phase:

- The project is currently a `data-driven policy / risk / burden / vulnerability` line.
- The current empirical core is `avoidable harmful churn`, not broad churn in general.
- The main design risk is still timing interpretation.
- The main subgroup risk is still weak stability for several families.
- The most honest current ML role is still `risk ranking`, not `causal ML`.

## Execution Order

This phase has four active steps.

### Step 1 — Timing Stress Tests

#### Objective

Test whether the current top candidate `backlog_automation_rank_index / same` remains credible when timing is stressed more aggressively.

#### Required Inputs

Use the current corrected `SIPP 2021-2023` avoidable-churn stack and the current state-month burden layer.

Primary outcomes to test:

- `medicaid_exit_to_uninsured_next`
- `persistent_uninsured_h2`
- `broad_exit_persistent_uninsured_h2`
- `persistent_uninsured_h3`
- `broad_exit_resolved_insured_h2`

Primary exposure:

- `backlog_automation_rank_index`

Comparison exposures:

- `backlog_automation_index`
- `pending_rate`
- `ex_parte_renewal_rate`
- optionally `renewal_form_rate` as legacy comparison only

Timing alignments to test:

- `same`
- `lag1`
- `lag2` if support is acceptable
- `lead1`

Windows to test:

- `core_aug_oct_2023`
- `mature_jun_oct_2023`
- one early or expanded sensitivity window only if support is clearly documented

Required stress tests:

- distributed timing comparison table
- placebo month-shift check
- phase split if support allows
- explicit note on whether non-lead alignments remain competitive

#### Output Artifacts

Create:

- `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`
- `outputs/design_diagnostics/avoidable_churn_timing_stress_matrix.csv`
- `outputs/design_diagnostics/avoidable_churn_timing_placebo_summary.csv`
- `scripts/design_diagnostics/build_avoidable_churn_timing_stress_round4.py`

#### Closure Test

Record clearly whether:

- at least one non-lead alignment remains competitive across nearby windows
- the current top candidate still looks better than the main alternatives after timing stress

#### Decision Unlocked

This step determines whether the branch stays on a paper-supporting path or should remain only a bounded predictive line.

---

### Step 2 — Subgroup Stability Round 2 On The New Outcome Layer

#### Objective

Re-test subgroup stability using the upgraded avoidable-churn outcomes rather than the older narrower outcome layer.

#### Required Inputs

Use the retained subgroup families already judged acceptable:

- `age_band`
- `female_group`
- `foreign_born_group`
- `household_child_group`
- `noncitizen_group`
- `pov_band`
- `snap_group`

Primary harmful outcomes:

- `persistent_uninsured_h2`
- `broad_exit_persistent_uninsured_h2`

Contrast outcome:

- `broad_exit_resolved_insured_h2`

Reference comparison:

- pre-period ordering in `2021-2022`
- unwinding-year ordering in `2023`

#### Output Artifacts

Create:

- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2.md`
- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2_summary.csv`
- `outputs/design_diagnostics/avoidable_churn_subgroup_ordering_tables.csv`
- `scripts/design_diagnostics/build_avoidable_churn_subgroup_stability_round2.py`

#### Closure Test

Record clearly whether:

- at least one or two subgroup families now show repeatable high-risk ordering
- the new outcome layer improves stability relative to the earlier round
- the evidence supports a stronger `risk ranking` interpretation

#### Decision Unlocked

This step determines whether subgroup-driven prioritization remains only descriptive or becomes strong enough for a more serious risk-ranking contribution.

---

### Step 3 — Risk-Ranking Round 2

#### Objective

Upgrade the earlier bounded risk pilot using the improved avoidable-churn outcome layer and the most defensible retained subgroup families.

#### Required Inputs

Training setup:

- train on `2021-2022`
- test on `2023`

Primary outcome:

- `persistent_uninsured_h2`

Benchmark outcome:

- `medicaid_exit_to_uninsured_next`

Models to compare:

- naive state baseline
- weighted logistic
- one shallow tree model
- one boosting-style model only if implementation is stable and interpretation remains clear

Required reporting:

- `AUC`
- `PR AUC`
- `top-decile capture`
- calibration by decile
- subgroup calibration for the retained core subgroup families
- explicit comparison against the old risk pilot

#### Output Artifacts

Create:

- `outputs/design_diagnostics/avoidable_churn_risk_round2.md`
- `outputs/design_diagnostics/avoidable_churn_risk_round2_metrics.csv`
- `outputs/design_diagnostics/avoidable_churn_risk_round2_calibration.csv`
- `outputs/design_diagnostics/avoidable_churn_risk_round2_group_calibration.csv`
- `scripts/design_diagnostics/run_avoidable_churn_risk_round2.py`

#### Closure Test

Record clearly whether:

- the new outcome improves ranking usefulness relative to the old risk pilot
- the signal remains better than naive state baseline
- calibration is good enough to support a modest `risk prioritization prototype`

#### Decision Unlocked

This step determines whether the current line can legitimately claim a bounded `risk ranking / prioritization` contribution.

---

### Step 4 — Paper-Path Decision Memo

#### Objective

Convert the new testing round into one explicit path decision.

#### Required Inputs

Use the outputs from Steps 1-3 only.
Do not add new data or new branches before this memo.

#### The Memo Must Decide Between These Paths

- `Path A: paper-first risk / burden / vulnerability line`
- `Path B: continue design strengthening toward quasi-causal escalation`
- `Path C: keep as supporting branch only and do not make it the main paper`

#### Output Artifact

Create:

- `docs/churn_unwinding_post_round4_path_decision.md`

#### Closure Test

The memo must give one explicit verdict.
It must not end in vague “more work is needed” language.

#### Decision Unlocked

This step decides whether the project should now:

- start paper-outline writing on this line
- continue with one more methodological strengthening round
- or downgrade this line from main candidate status

## Reporting Rules For Every Step

For every empirical result, report using this structure:

1. `Question`
2. `Sample / Unit`
3. `Outcome`
4. `Treatment / Exposure`
5. `Purpose`
6. `Numerical Result`
7. `Interpretation`
8. `Evaluation`
9. `Caveat`

Follow the existing reporting convention already locked in the repo.

## Update Rules

After each completed step, update these files:

1. `docs/churn_unwinding_progress_record.md`
2. `docs/churn_unwinding_execution_handoff.md`

If a step materially changes the active branch, also update:

3. `docs/churn_unwinding_paper_strategy_memo.md`

Do not mark a step complete unless:

- the output artifacts exist
- the key verdict is written explicitly
- the caveat is recorded explicitly

## Stop Rules

Stop escalation and record failure cleanly if any of the following happens:

- timing stress collapses the current candidate into mainly `lead1`
- the new outcome layer does not improve subgroup stability at all
- the new risk round fails to beat the old pilot in a meaningful way
- the branch becomes too dependent on one handcrafted outcome with no nearby robustness

If a stop rule is triggered, do **not** open causal escalation work.
Instead, write the failure clearly into the decision memo and hand the branch back for review.

## Final Standard For This Phase

At the end of this phase, the repo should make it easy for a reviewer or future agent to answer:

- what the current best empirical core is
- whether the timing is good enough to keep investing
- whether subgroup structure is strong enough for a bounded prioritization claim
- whether the project should now become a paper-writing branch or stay in diagnostics mode
