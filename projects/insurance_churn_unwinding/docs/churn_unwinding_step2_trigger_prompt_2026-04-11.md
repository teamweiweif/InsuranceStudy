# Step 2 Trigger Prompt

Use the following prompt in Codex chat to start **Step 2 only**.

---

Read these files first, in order:
1. `docs/churn_unwinding_step2_execution_note_2026-04-11.md`
2. `docs/churn_unwinding_operational_plan_2026-04-11.md`
3. `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`
4. `docs/churn_unwinding_progress_record.md`
5. `docs/churn_unwinding_execution_handoff.md`

Current status:
- only operational-plan Step 1 has been executed
- Step 1 verdict is `STEP1_TIMING_STRESS_PASSED_WITH_CAVEAT`
- primary candidate remains `backlog_automation_rank_index / same`
- core aggregate signed score is `0.1722`
- mature aggregate signed score is `0.1509`
- future-month `lead1` placebo did not dominate the best non-lead alignment in either primary window
- main caveat: timing looks better on aggregate, but this remains a diagnostic state-month screen
- Step 2 is unlocked but has not been started

Do not reopen broad topic search or alternative dataset exploration.
Do not start `DID`, `DDD`, `event-study`, `DML`, `causal ML`, or targeting work.

If continuing, execute only **Step 2: Subgroup Stability Round 2 On The New Outcome Layer** from the operational plan.

Requirements:
- use only the retained subgroup families and outcome layer specified in the Step 2 execution note
- create all Step 2 artifacts exactly at the required paths
- use the locked reporting structure for each main result block
- after Step 2 is complete, update:
  - `docs/churn_unwinding_progress_record.md`
  - `docs/churn_unwinding_execution_handoff.md`
- if Step 2 materially changes the paper-positioning logic, also update:
  - `docs/churn_unwinding_paper_strategy_memo.md`

At the end, report back with:
1. what you ran
2. what files you created or updated
3. the explicit Step 2 verdict
4. the main caveat
5. whether Step 3 is now unlocked

Do not start Step 3 until Step 2 is explicitly closed.
