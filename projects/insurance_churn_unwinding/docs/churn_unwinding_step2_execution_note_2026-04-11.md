# Churn / Unwinding Step 2 Execution Note

Last updated: `2026-04-11`

## Purpose

This file is the execution note for **Step 2 only** from:

- `docs/churn_unwinding_operational_plan_2026-04-11.md`

Current status before this note:

- Step 1 has been completed.
- Step 1 verdict is `STEP1_TIMING_STRESS_PASSED_WITH_CAVEAT`.
- Primary candidate remains `backlog_automation_rank_index / same`.
- Step 2 is unlocked.
- Step 3 is **not** unlocked.

This note exists to prevent drift.

## What You Are Allowed To Do Now

Execute only:

- `Step 2 — Subgroup Stability Round 2 On The New Outcome Layer`

You may:

- read the mandatory files already listed in the operational plan
- use the currently corrected `SIPP 2021-2023` stack
- use the currently locked avoidable-churn outcome family
- use the retained subgroup families already accepted in round 2
- create the Step 2 artifacts listed below
- update the progress and execution handoff files after Step 2 is closed

## What You Must Not Do Now

Do not:

- reopen broad topic search
- reopen alternative dataset exploration
- reopen `MEPS`, `MCBS`, or other main branches
- start `Step 3`
- start `DID`
- start `DDD`
- start `event study`
- start `DML`
- start `causal forest`
- use causal or welfare-based `targeting` language
- introduce a new main outcome family not already justified in the repo
- replace the current mechanism umbrella `administrative renewal burden`

## Required Inputs

### Subgroup families

Use only the retained subgroup families:

- `age_band`
- `female_group`
- `foreign_born_group`
- `household_child_group`
- `noncitizen_group`
- `pov_band`
- `snap_group`

Do not reopen dropped subgroup families unless a file already staged in the repo makes their missingness clearly acceptable.

### Outcome layer

Primary harmful outcomes:

- `persistent_uninsured_h2`
- `broad_exit_persistent_uninsured_h2`

Contrast outcome:

- `broad_exit_resolved_insured_h2`

Keep `medicaid_exit_to_uninsured_next` only as a benchmark if it helps interpretation, not as the primary Step 2 target.

### Reference comparison

Compare:

- pre-period ordering in `2021-2022`
- unwinding-year ordering in `2023`

The point is not generic subgroup description.
The point is ordering stability.

## Required Questions For Step 2

The step must answer these questions explicitly:

1. Does the upgraded avoidable-churn outcome layer improve subgroup stability relative to the earlier narrower outcome layer?
2. Do at least one or two subgroup families now show repeatable high-risk ordering from pre-period to unwinding year?
3. Does the evidence now support a stronger `risk ranking` interpretation than before?

## Required Output Artifacts

Create exactly these Step 2 artifacts:

- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2.md`
- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2_summary.csv`
- `outputs/design_diagnostics/avoidable_churn_subgroup_ordering_tables.csv`
- `scripts/design_diagnostics/build_avoidable_churn_subgroup_stability_round2.py`

If you create any helper sidecars, keep them inside `outputs/design_diagnostics/` and name them clearly.
Do not scatter temporary files elsewhere.

## Minimum Reporting Structure Inside The Step 2 Memo

For each main result block, report using the locked structure:

1. `Question`
2. `Sample / Unit`
3. `Outcome`
4. `Treatment / Exposure`
5. `Purpose`
6. `Numerical Result`
7. `Interpretation`
8. `Evaluation`
9. `Caveat`

## Required Closure Test

At the end of Step 2, the memo must state explicitly:

- whether at least one or two subgroup families now show repeatable high-risk ordering
- whether the new outcome layer improves stability relative to the earlier round
- whether the evidence supports a stronger `risk ranking` interpretation
- the explicit Step 2 verdict in one line
- whether Step 3 is now unlocked

Do not end with vague language.

## Mandatory File Updates After Step 2

After Step 2 is complete, update:

1. `docs/churn_unwinding_progress_record.md`
2. `docs/churn_unwinding_execution_handoff.md`

If Step 2 materially changes the paper-positioning logic, also update:

3. `docs/churn_unwinding_paper_strategy_memo.md`

## Stop Rule For Step 2

If the new outcome layer does not improve subgroup stability at all, or if no subgroup family shows meaningful repeatable ordering, do not drift into Step 3 as if nothing happened.

Instead:

- write the failure clearly
- close Step 2 honestly
- record that subgroup-driven prioritization remains weak
- hand the branch back for review before further escalation

## Final Standard

A good Step 2 completion should make it easy for a later reviewer to answer:

- whether subgroup structure is now stronger than in the earlier round
- whether the avoidable-churn outcome upgrade materially helped ordering stability
- whether this line is now ready for a stronger risk-ranking round
