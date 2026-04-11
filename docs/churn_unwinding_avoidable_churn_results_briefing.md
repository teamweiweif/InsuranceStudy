# Churn / Unwinding Avoidable-Churn Results Briefing

Last updated: `2026-04-11`

## Purpose

This is a plain-language briefing memo for the current `avoidable churn` branch.

It rewrites the latest findings using the locked reporting structure:

1. `Question`
2. `Sample / Unit`
3. `Outcome`
4. `Treatment / Exposure`
5. `Purpose`
6. `Numerical Result`
7. `Interpretation`
8. `Evaluation`
9. `Caveat`

## Result 1: Outcome Reconstruction

### Question

Can the project build a short-horizon churn outcome that is more meaningful than a single one-month uninsured transition?

### Sample / Unit

- Data: corrected `SIPP 2021-2023`
- Unit: person-month
- Core support check: `August-October` in each reference year

### Outcome

Three candidate short-horizon outcomes were central:

- `persistent_uninsured_h2`
  - pure Medicaid at `t`
  - uninsured at `t+1`
  - still uninsured at `t+2`

- `broad_exit_resolved_insured_h2`
  - pure Medicaid at `t`
  - broad exit from Medicaid at `t+1`
  - insured again by `t+2`

- `broad_exit_back_to_medicaid_h2`
  - pure Medicaid at `t`
  - leaves Medicaid at `t+1`
  - returns to pure Medicaid by `t+2`

### Treatment / Exposure

Not the main focus in this step.

This step only asked whether the outcome layer itself is usable.

### Purpose

The earlier screen had a measurement problem:

- `medicaid_exit_to_uninsured_next` was very narrow
- literal `exit -> return to Medicaid` sounded attractive, but might be too rare

This step tested which short-horizon outcomes are actually supportable.

### Numerical Result

In `2023`, core `Aug-Oct`:

- `persistent_uninsured_h2`
  - `64` event rows
  - weighted rate `0.002933`

- `broad_exit_resolved_insured_h2`
  - `75` event rows
  - weighted rate `0.005024`

- `broad_exit_back_to_medicaid_h2`
  - `1` event row
  - weighted rate `0.00007`

### Interpretation

- literal return-to-Medicaid is too sparse to carry the branch
- the usable harmful short-horizon outcome is `persistent_uninsured_h2`
- the usable contrast outcome is `broad_exit_resolved_insured_h2`

### Evaluation

- encouraging as a measurement cleanup
- not a headline result by itself

### Caveat

- these are researcher-defined outcomes, not official CMS published endpoints

## Result 2: Burden Candidate Re-ranking

### Question

Which exposure family now looks most consistent once the project uses the new short-horizon outcomes?

### Sample / Unit

- Data: corrected `SIPP 2021-2023` merged with CMS state-month unwinding metrics
- Unit:
  - estimation screen at the `state-month` cell level after aggregating eligible person-month observations
- Main windows:
  - `core_aug_oct_2023_h2`
  - `mature_jun_oct_2023_h2`

### Outcome

The main tracked outcomes were:

- `medicaid_exit_to_uninsured_next`
- `persistent_uninsured_h2`
- `broad_exit_resolved_insured_h2`

### Treatment / Exposure

The main exposure candidates were:

- `pending_rate`
- `renewal_form_rate`
- `procedural_term_share`
- `ex_parte_renewal_rate`
- `backlog_automation_index`
- `backlog_form_index`
- `full_burden_index`

The current chosen exposure is:

- `backlog_automation_index / same`

Plain-language meaning:

- higher pending renewals
- lower automatic or ex parte renewals
- therefore heavier administrative renewal burden

### Purpose

The old candidate, `renewal_form_rate / lag1`, was not bad, but it still felt partial and fragile.

This step asked whether a broader burden measure fits the theory and the data better.

### Numerical Result

For the chosen candidate:

- verdict: `PROMISING_H2_UPGRADE`
- chosen candidate: `backlog_automation_index / same`
- core score: `0.1242`
- mature score: `0.1105`

Falsification for the same candidate:

- on `medicaid_exit_to_uninsured_next`
  - pre `2021`: `0.0009`
  - pre `2022`: `0.0007`
  - unwinding `2023`: `0.0023`

- on `persistent_uninsured_h2`
  - pre `2021`: `0.0009`
  - pre `2022`: `0.0007`
  - unwinding `2023`: `0.0016`

- on `broad_exit_resolved_insured_h2`
  - pre `2021`: `-0.0004`
  - pre `2022`: `-0.0014`
  - unwinding `2023`: `-0.0026`

### Interpretation

This is the first branch where the empirical story starts to look coherent:

- heavier `backlog + weak automation` lines up with more harmful unresolved loss
- and with less quickly resolved re-insured exit

That is closer to an `avoidable churn` story than the old single-indicator screen.

### Evaluation

- this is the current strongest result in the churn/unwinding line
- still diagnostic, not causal
- strong enough to justify more testing

### Caveat

- `lead1` still scores very high in some tables
- so timing is improved, not solved

## Result 3: Lightweight External Echo In HPS

### Question

Does the new candidate exposure look directionally sensible outside SIPP?

### Sample / Unit

- Data: `HPS 2023`
- Unit: state-week
- Window: `Weeks 60-63`
- age restriction: `18-64`

### Outcome

The external rough outcomes were:

- `current_medicaid_rate`
- `uninsured_rate`
- `public_coverage_rate`

### Treatment / Exposure

- `backlog_automation_index / same`
- mapped from state-month burden into state-week outcomes using survey end-month

### Purpose

This was not meant to be a second main design.

It was only a rough external check:

- does the candidate exposure have any plausible echo outside SIPP?

### Numerical Result

- `current_medicaid_rate`
  - weighted correlation `-0.1534`
  - high-low contrast `-0.0157`

- `uninsured_rate`
  - weighted correlation `0.1836`
  - high-low contrast `0.0111`

- `public_coverage_rate`
  - weighted correlation `-0.1879`
  - high-low contrast `-0.0176`

### Interpretation

Higher burden states look like:

- lower current Medicaid/public coverage
- higher uninsurance

That does not prove the SIPP mechanism, but it does make the new candidate look less idiosyncratic.

### Evaluation

- useful external plus
- not a deciding result

### Caveat

- repeated cross-section only
- not person-level churn validation

## Overall Assessment

### What improved

- the project now has a better primary harmful outcome
- the project now has a better burden candidate
- the external echo is more aligned than before

### What did not improve enough yet

- timing is still not fully pinned down
- this is still not a strong quasi-causal design
- the branch is not yet ready for `DML / causal ML`

### Honest bottom line

The branch is no longer “nothing works.”

But the correct interpretation is still:

- `promising upgraded diagnostics`

not:

- `publication-ready causal result`
