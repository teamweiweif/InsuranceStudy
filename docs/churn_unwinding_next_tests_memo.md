# Churn / Unwinding Next Tests Memo

Last updated: `2026-04-11`

## Purpose

This memo records the most defensible next testing steps after the current `avoidable churn` upgrade.

It also answers a practical question:

- is the project already using the time dimension enough, or are more dynamic tests still worth doing?

## Status Update

As of `2026-04-11` after the round-3 robustness run:

- `Priority 1: Outcome-Robustness Around Persistence`
  - executed

- `Priority 2: Exposure Decomposition And Leave-One-Component-Out Checks`
  - executed in a bounded first pass

Current best candidate after that round:

- `backlog_automation_rank_index / same`

So the next active frontier is now:

- `Priority 3: Timing Stress Tests`
- then `Priority 4: Subgroup Stability Round 2`

## Short Answer

- The project has used the time dimension enough for `first serious diagnostics`.
- It has **not** used the time dimension enough for `strong design validation`.
- But the next useful time-based work is **not** classical time-series modeling like `ARIMA`, `VAR`, or generic forecasting.
- The right next work is:
  - lead-lag robustness
  - cohort-resolution timing checks
  - phase-specific unwinding windows
  - placebo timing and state-trend stress tests

So:

- `time series` in the classical sense is not the bottleneck
- `time alignment and dynamic robustness` still are

## Priority Order

### Priority 1: Outcome-Robustness Around Persistence

#### Question

Does the new result depend too much on one exact hand-built persistence rule?

#### Why this is first

Right now the project has one clearly better harmful outcome:

- `persistent_uninsured_h2`

That is good, but still fragile if it is the only persistence definition that works.

#### Tests to run

- compare:
  - `t+1 uninsured`
  - `t+1 and t+2 uninsured`
  - `t+1 uninsured, t+2 not insured`
  - `broad exit with unresolved uninsured by h2`
- add a modest `h3` extension only if support remains acceptable
- keep `broad_exit_resolved_insured_h2` as a contrast outcome in every run

#### Pass condition

- the burden story should survive under at least two nearby persistence definitions

#### Why it matters

If it only works for one exact handcrafted definition, the branch is still too brittle.

### Priority 2: Exposure Decomposition And Leave-One-Component-Out Checks

#### Question

Is `backlog_automation_index` really better because it captures a real composite burden, or just because one component is doing all the work?

#### Why this is second

The current best candidate is a composite:

- `pending backlog`
- plus `weak ex parte automation`

That is promising, but composite variables can be misleading.

#### Tests to run

- compare:
  - `pending_rate` alone
  - `ex_parte_renewal_rate` alone
  - `backlog_automation_index`
- leave-one-component-out versions:
  - backlog only
  - low ex parte only
  - equal-weight composite
  - rank-based composite
  - z-score composite
- test whether the sign and ranking remain stable

#### Pass condition

- the composite should beat either component alone, or at least remain clearly more stable across windows

#### Why it matters

This tells us whether the mechanism is really:

- `backlog + weak automation`

or just:

- `pending backlog only`

### Priority 3: Timing Stress Tests

#### Question

Is the new candidate genuinely better timed, or only less bad than before?

#### Why this is still necessary

The new candidate improved timing, but timing is still the main unresolved design risk.

#### Tests to run

- same / lag1 / lag2 / lead1 ranking under the new persistence outcomes
- distributed-lag style summary:
  - not a regression paper result yet
  - just a design table showing where the mass of signal lives
- split the unwinding into phases:
  - early `Apr-Jul 2023`
  - core `Aug-Oct 2023`
  - late `Nov-Jan` if support allows
- run placebo month shifts:
  - randomly or mechanically move the exposure by one month and see whether the ranking collapses

#### Pass condition

- at least one non-lead alignment should remain competitive across nearby windows

#### Why it matters

If the signal still depends mostly on `lead1`, the project is not ready for stronger design claims.

### Priority 4: Subgroup Stability Round 2 On The New Outcome

#### Question

Does the new outcome improve heterogeneity stability enough to justify later risk-ranking work?

#### Why this is now worth revisiting

The old subgroup work was done before the `avoidable churn` upgrade.

Now the outcome is more targeted, so subgroup ranking may become more stable.

#### Tests to run

- rerun subgroup contrasts using:
  - `persistent_uninsured_h2`
  - `broad_exit_resolved_insured_h2`
- focus on retained subgroup families:
  - `pov_band`
  - `snap_group`
  - `household_child_group`
  - `noncitizen_group`
  - `foreign_born_group`
  - `age_band`
- compare:
  - pre-period ordering
  - unwinding-year ordering
  - whether rankings now carry over better than before

#### Pass condition

- at least one or two subgroup families should show repeatable high-risk ordering

#### Why it matters

If this improves, the project can justify a stronger `risk ranking` phase.

### Priority 5: A More Formal But Still Bounded Risk-Ranking Round

#### Question

Does the improved outcome also improve prediction usefulness?

#### When to do it

Only after Priorities `1-4` look acceptable.

#### Tests to run

- train on `2021-2022`
- test on `2023`
- compare:
  - weighted logistic
  - shallow tree / boosting
  - naive state baseline
- outcome:
  - primary `persistent_uninsured_h2`
  - benchmark `medicaid_exit_to_uninsured_next`
- report:
  - AUC
  - PR
  - top-decile capture
  - subgroup calibration

#### Why it matters

This is the highest-value near-term `ML` use that stays honest.

## What Is Not A Priority Right Now

### 1. Classical time-series models

Examples:

- `ARIMA`
- `VAR`
- generic trend forecasting

Why not:

- the project is not a long single-series forecasting problem
- the number of monthly unwinding periods is too short
- the real issue is treatment-timing interpretation, not time-series prediction

### 2. Full event-study paper regressions

Why not yet:

- timing still needs more stress testing first
- the outcome layer was just upgraded

### 3. Immediate DML / causal forest

Why not yet:

- the exposure and timing layer still need more validation
- otherwise ML will decorate an unstable design

## Recommended Next Actual Execution Order

If execution resumes now, the best order is:

1. `Outcome robustness around h2 persistence`
2. `Exposure decomposition / leave-one-component-out`
3. `Timing stress tests`
4. `Subgroup stability round 2`
5. `Risk-ranking round 2`

## Bottom Line

The project has already used time in a serious way.

But not enough to say:

- `timing risk is solved`

The next gains will come from:

- better dynamic robustness tests
- not from generic time-series machinery
