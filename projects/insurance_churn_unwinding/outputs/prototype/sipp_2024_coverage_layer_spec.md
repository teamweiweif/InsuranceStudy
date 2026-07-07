# SIPP 2024 Coverage Layer Specification

Last updated: `2026-04-10`

## Purpose

This note freezes the `Step 1` prototype variable map for the churn / unwinding line.

It does **not** validate:

- a final unwinding treatment definition
- a CMS merge design
- a corrected `2018-2023` stack
- a final modeling dataset

It does define one audited `2024 SIPP release` person-month prototype file that future work must treat as the current baseline.

## Governing Evidence

This specification is based on:

- [../data_audit/sipp_preflight_2026-04-10.md](../data_audit/sipp_preflight_2026-04-10.md)
- [../data_audit/sipp_2024_deep_audit_2026-04-10.md](../data_audit/sipp_2024_deep_audit_2026-04-10.md)

## Time Structure Interpretation

Use the following interpretation consistently:

- `2024 SIPP` here means the `2024 release`, not literal calendar-year `2024` reference months
- the prototype should be interpreted mainly as `reference year 2023`
- the release is an overlapping-panels file, not "the 2024 panel"
- locally observed `SPANEL` values in the retained file are:
  - `2021`
  - `2022`
  - `2023`
  - `2024`

## Output Artifacts

Frozen Step 1 artifacts:

- [sipp_2024_person_month_flags.parquet](sipp_2024_person_month_flags.parquet)
- [sipp_2024_coverage_layer_summary.json](sipp_2024_coverage_layer_summary.json)

Builder script:

- [../../scripts/prototype/build_sipp_2024_coverage_layer.py](../../scripts/prototype/build_sipp_2024_coverage_layer.py)

## Universe And Exclusions

Input source:

- `data/raw/feasibility_audit/sipp/2024/pu2024_csv.zip`

Retained universe:

- person-month observations with `TEHC_ST` in the valid public-use state scope `1..56`

Excluded from the prototype file:

- `TEHC_ST = 60`
- `TEHC_ST = 61`

Observed exclusion counts:

- excluded rows: `931`
- excluded persons: `157`

Month scope:

- retained `MONTHCODE` values: `1..12`
- next-month transition outcomes are only defined when the same person has an observed consecutive next month
- in practice, the eligible transition universe is restricted to `MONTHCODE = 1..11`

## Frozen Variable Map

| Concept | Prototype rule | Notes |
| --- | --- | --- |
| `state` | `TEHC_ST` | Primary public-use state linkage variable. `60` and `61` excluded from the prototype. |
| `time` | `MONTHCODE` | Interpreted as reference months in `2023` for the `2024` release. |
| `insured_t` | `RHLTHMTH = 1` | Broad "any insurance this month" concept. |
| `uninsured_t` | `RHLTHMTH = 2` | Broad uninsured month concept. Do not extend this to uninsured-care outcomes yet. |
| `public_t` | `RPUBMTH = 1` | Broad public coverage concept. |
| `private_t` | `RPRIMTH = 1` | Private coverage indicator retained for prototype context. |
| `pure_medicaid_t` | `EMDMTH = 1` | Strict Medicaid / Medical Assistance month concept for the prototype. |
| `broad_public_assistance_non_medicaid_t` | `RPUBTYPE2 = 1` and `EMDMTH != 1` | Keeps broader public assistance separate from strict Medicaid. |
| `other_coverage_t` | `EOTMTH = 1` | Retained as an auxiliary "other / ambiguous coverage" flag. |
| `positive_month_weight` | `WPFINWGT > 0` | Month-level positive-weight indicator. |
| `in_december_positive_weight_cohort` | same person has `MONTHCODE = 12` with `WPFINWGT > 0` | Retained because the official December-weight rule matters for reference-year analysis. |

Important interpretation rule:

- `RPUBTYPE2` must **not** be treated as interchangeable with `EMDMTH`

## Transition Definitions

Sorting rule:

- sort by `SSUID`, `PNUM`, `MONTHCODE`

Consecutive-month rule:

- `has_consecutive_next_month = 1` when the next observed month for the same person is exactly `MONTHCODE + 1`

Transition universe:

- `eligible_medicaid_transition = 1` when `pure_medicaid_t = 1` and `has_consecutive_next_month = 1`

Frozen one-step outcomes:

- `medicaid_exit_next = 1` when `pure_medicaid_t = 1` and `EMDMTH_(t+1) != 1`
- `medicaid_exit_next = 0` when `pure_medicaid_t = 1` and `EMDMTH_(t+1) = 1`
- `medicaid_exit_to_uninsured_next = 1` when `pure_medicaid_t = 1` and `RHLTHMTH_(t+1) = 2`
- `medicaid_exit_to_uninsured_next = 0` when `pure_medicaid_t = 1` and `RHLTHMTH_(t+1) != 2`

Outside the eligible transition universe:

- `medicaid_t_plus_1`, `uninsured_t_plus_1`, `medicaid_exit_next`, and `medicaid_exit_to_uninsured_next` are left undefined

This is intentional.

The Step 1 prototype is a one-step transition layer, not a final spell-based churn system.

## Produced Dataset Summary

Observed counts from the built prototype:

- raw rows: `437,168`
- raw unique persons: `36,915`
- retained valid-state rows: `436,237`
- retained valid-state persons: `36,901`
- duplicate `SSUID + PNUM + MONTHCODE` keys after filtering: `0`
- retained `MONTHCODE` values: `1..12`
- retained `SPANEL` values:
  - `2021`
  - `2022`
  - `2023`
  - `2024`

Category counts in the retained file:

- `insured_t = 1`: `399,179`
- `uninsured_t = 1`: `37,058`
- `public_t = 1`: `195,128`
- `private_t = 1`: `282,193`
- `pure_medicaid_t = 1`: `88,636`
- `broad_public_assistance_non_medicaid_t = 1`: `5,094`
- `other_coverage_t = 1`: `12,902`

Transition counts:

- `has_consecutive_next_month = 1`: `399,317`
- `eligible_medicaid_transition = 1`: `81,207`
- `medicaid_exit_next = 1`: `549`
- `medicaid_exit_to_uninsured_next = 1`: `250`

December-positive-weight cohort:

- persons: `36,186`
- rows: `432,056`

## Current Constraints

- This prototype supports `Step 2` merge work, not final estimation.
- The file does **not** solve the `2018-2023` correction problem.
- The file does **not** validate a causal unwinding exposure.
- The file does **not** justify moving straight to `ML` beyond possible later `risk prediction`.
- `other_coverage_t` and broader public-assistance categories remain auxiliary and should not be overinterpreted.

## Step 1 Closure Verdict

`Step 1` is complete at the prototype-definition level.

The closure test is satisfied because:

- variable definitions are frozen
- exclusions are stated
- transition outcomes are defined
- artifact paths are recorded

This unlocks:

- `Step 2`: audited `TEHC_ST x MONTHCODE` merge to one chosen CMS unwinding metric family
