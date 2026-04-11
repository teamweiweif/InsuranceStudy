# Churn / Unwinding Round-3 Robustness Memo

Last updated: `2026-04-11`

## Purpose

This memo records the next unattended testing round after the first `avoidable churn` upgrade.

This round executed the first two items from the locked next-test order:

1. `outcome robustness around persistence definitions`
2. `exposure decomposition around the leading burden candidate`

It also added one bounded external check for the new top exposure candidate.

## Result 1: Outcome Robustness

### Question

Does the current signal survive if the project moves from one exact harmful transition outcome to nearby persistence-style outcomes?

### Sample / Unit

- data: corrected `SIPP 2021-2023`
- unit: `state-month` cells built from person-month observations
- main windows:
  - `core_aug_oct_2023`
  - `mature_jun_oct_2023`

### Outcome

The outcome family now included:

- `medicaid_exit_to_uninsured_next`
- `persistent_uninsured_h2`
- `broad_exit_persistent_uninsured_h2`
- `persistent_uninsured_h3`
- `broad_exit_resolved_insured_h2`

Plain-language meanings:

- `medicaid_exit_to_uninsured_next`
  - pure Medicaid at `t`, uninsured at `t+1`

- `persistent_uninsured_h2`
  - pure Medicaid at `t`, uninsured at both `t+1` and `t+2`

- `broad_exit_persistent_uninsured_h2`
  - broad exit at `t+1`, uninsured at `t+2`

- `persistent_uninsured_h3`
  - pure Medicaid at `t`, uninsured through `t+3`

- `broad_exit_resolved_insured_h2`
  - broad exit at `t+1`, insured again by `t+2`

### Treatment / Exposure

- `backlog_automation_index / same`

Meaning:

- more pending renewals
- weaker automatic or ex parte renewal
- therefore a heavier administrative renewal environment in that state-month

### Purpose

The point was to test whether the branch depends too much on one exact hand-built outcome.

### Numerical Result

Core `2023` support:

- `medicaid_exit_to_uninsured_next`
  - support rows `21,847`
  - weighted rate `0.003178`

- `persistent_uninsured_h2`
  - support rows `21,794`
  - weighted rate `0.002933`

- `broad_exit_persistent_uninsured_h2`
  - support rows `21,794`
  - weighted rate `0.002984`

- `persistent_uninsured_h3`
  - support rows `14,519`
  - weighted rate `0.002668`

For the chosen exposure, the best nonlead alignment was stable:

- `medicaid_exit_to_uninsured_next`
  - core same-month corr `0.1636`
  - mature same-month corr `0.1420`

- `persistent_uninsured_h2`
  - core same-month corr `0.1407`
  - mature same-month corr `0.1269`

- `broad_exit_persistent_uninsured_h2`
  - core same-month corr `0.1438`
  - mature same-month corr `0.1288`

- `persistent_uninsured_h3`
  - core same-month corr `0.1933`
  - mature same-month corr `0.1500`

Falsification also held:

- `persistent_uninsured_h2`
  - pre `2021`: `0.0009`
  - pre `2022`: `0.0007`
  - unwinding `2023`: `0.0016`

- `persistent_uninsured_h3`
  - pre `2021`: `0.0002`
  - pre `2022`: `0.0019`
  - unwinding `2023`: `0.0027`

### Interpretation

This is the clearest positive result in the whole round.

The current burden story does **not** collapse when the harmful outcome is tightened from:

- one-step uninsured exit

to:

- persistent uninsured loss over `h2`
- and even over `h3`

That means the branch is no longer hanging on one fragile outcome choice.

### Evaluation

- strong for a diagnostic round
- enough to treat the harmful outcome side as materially improved

### Caveat

- `lead1` is still not dead
- so this does not solve timing, it only shows the signal survives under tighter outcome definitions

## Result 2: Exposure Decomposition

### Question

Is the current composite burden candidate really useful, or is one component doing most of the work?

### Sample / Unit

- data: corrected `SIPP 2021-2023`
- unit: `state-month` cells
- outcomes used for decomposition:
  - `medicaid_exit_to_uninsured_next`
  - `persistent_uninsured_h2`
  - `broad_exit_resolved_insured_h2`

### Outcome

The main harmful outcome for decomposition emphasis was:

- `persistent_uninsured_h2`

The contrast outcome remained:

- `broad_exit_resolved_insured_h2`

### Treatment / Exposure

This round compared:

- `pending_rate`
- `ex_parte_renewal_rate`
- `backlog_automation_index`
- `backlog_automation_rank_index`
- `backlog_form_index`

Meaning:

- `pending_rate`
  - backlog strain alone

- `ex_parte_renewal_rate`
  - automation relief alone

- `backlog_automation_index`
  - equal-weight z-score composite of backlog and weak automation

- `backlog_automation_rank_index`
  - rank-based composite of backlog and weak automation

- `backlog_form_index`
  - comparison composite using backlog plus manual renewal burden

### Purpose

The point was to test whether:

- the current composite still beats its parts
- and whether a more robust rank-based version works even better

### Numerical Result

Top nonlead rankings in `core_aug_oct_2023`:

- `backlog_automation_rank_index / same`
  - mean signed corr `0.1482`

- `backlog_automation_index / same`
  - mean signed corr `0.1242`

- `pending_rate / same`
  - mean signed corr `0.1128`

Top nonlead rankings in `mature_jun_oct_2023`:

- `backlog_automation_rank_index / same`
  - mean signed corr `0.1362`

- `backlog_automation_index / same`
  - mean signed corr `0.1105`

- `backlog_automation_rank_index / lag1`
  - mean signed corr `0.1002`

For `persistent_uninsured_h2`, same-month falsification passed for all compared exposures, but the new rank-based composite had the cleanest relative combination:

- `backlog_automation_rank_index`
  - pre `2021`: `0.0006`
  - pre `2022`: `0.0006`
  - unwinding `2023`: `0.0017`

### Interpretation

This means two things.

First:

- the composite is not collapsing when unpacked

Second:

- the strongest current candidate is no longer the old z-score version
- it is now the rank-based version:
  - `backlog_automation_rank_index / same`

That suggests the story is probably real at the level of ordering and relative burden, not just the exact scale of the raw CMS rates.

### Evaluation

- materially encouraging
- this is a real upgrade, not cosmetic

### Caveat

- the margin over the old z-score composite is not huge
- so this should be treated as a preferred current candidate, not a final locked treatment variable

## Result 3: HPS External Echo For The New Top Candidate

### Question

Does the new top candidate still look plausible outside SIPP?

### Sample / Unit

- data: `HPS 2023`
- unit: `state-week`
- window: `Weeks 60-63`
- exposure mapped from state-month using survey end-month

### Outcome

External rough outcomes:

- `current_medicaid_rate`
- `uninsured_rate`
- `public_coverage_rate`

### Treatment / Exposure

- `backlog_automation_rank_index / same`

### Purpose

The purpose was not to build a second main design.

It was only to see whether the new top candidate still has an external directional echo.

### Numerical Result

- `current_medicaid_rate`
  - weighted correlation `-0.1963`
  - high-low contrast `-0.0180`

- `uninsured_rate`
  - weighted correlation `0.2391`
  - high-low contrast `0.0136`

- `public_coverage_rate`
  - weighted correlation `-0.2448`
  - high-low contrast `-0.0206`

All directions were expected.

### Interpretation

The new top candidate does not only look better inside SIPP.

In HPS too, higher burden states look like:

- lower Medicaid/public coverage
- higher uninsurance

### Evaluation

- a useful external plus
- stronger than the earlier HPS echo for the old candidate

### Caveat

- still repeated cross-section only
- still not person-level churn validation

## Bottom Line

This round did three important things:

1. it showed that the harmful outcome side is now genuinely more robust
2. it upgraded the best current exposure candidate from:
   - `backlog_automation_index / same`
   to:
   - `backlog_automation_rank_index / same`
3. it showed that the new top candidate also has a stronger HPS echo

So the overall round-3 verdict is:

- `ROUND3_SUPPORTS_CONTINUATION`

That still does **not** mean:

- ready for publication
- ready for `DID / DML / causal ML`

It means:

- the branch now has a clearer core
- and the next highest-value work should shift to:
  - timing stress tests
  - subgroup stability round 2

## Main Artifacts

- [avoidable_churn_round3_robustness.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_round3_robustness.md)
- [avoidable_churn_outcome_robustness_timing.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_outcome_robustness_timing.csv)
- [avoidable_churn_exposure_decomposition_ranking.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/avoidable_churn_exposure_decomposition_ranking.csv)
- [hps_avoidable_churn_round3_crosscheck.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/hps_avoidable_churn_round3_crosscheck.md)
