# Prompt For Web GPT After Step 1

Read these files first, in order:

1. `docs/churn_unwinding_operational_plan_2026-04-11.md`
2. `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`
3. `docs/churn_unwinding_progress_record.md`
4. `docs/churn_unwinding_execution_handoff.md`

Current status:

- Only operational-plan `Step 1` has been executed.
- Step 1 verdict: `STEP1_TIMING_STRESS_PASSED_WITH_CAVEAT`.
- Primary candidate: `backlog_automation_rank_index / same`.
- Main results:
  - `core_aug_oct_2023` aggregate signed score: `0.1722`
  - `mature_jun_oct_2023` aggregate signed score: `0.1509`
  - future-month `lead1` placebo did not dominate the best non-lead alignment in either primary window.
- Main caveat: timing looks better on aggregate, but this remains a diagnostic state-month screen.
- Step 2 is unlocked, but has not been started.

Task boundary:

- Do not reopen broad topic search or alternative dataset exploration.
- Do not start DID, DML, causal ML, event-study, or targeting work.
- If asked to continue, execute only `Step 2: Subgroup Stability Round 2 On The New Outcome Layer` from the operational plan.
