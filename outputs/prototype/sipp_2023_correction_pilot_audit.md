# SIPP 2023 Correction Pilot Audit

Last updated: `2026-04-10`

## Purpose

This note records the first bounded implementation pilot that follows the `Step 3` correction specification.

The pilot uses the `2023 SIPP release` as a correction test bed.

This is **not** a final estimating file.

This is **not** an unwinding-year analysis file.

Its purpose is narrower:

- test whether the official `2018-2023` health-insurance correction rules can be translated into a stable implementation
- measure how much those rules actually change the monthly churn layer
- identify any variables that still require conservative handling before back-extension to earlier years

## Governing Inputs

The pilot follows:

- [../data_audit/sipp_2018_2023_hi_correction_spec.md](../data_audit/sipp_2018_2023_hi_correction_spec.md)
- [../data_audit/sipp_preflight_2026-04-10.md](../data_audit/sipp_preflight_2026-04-10.md)
- [../data_audit/sipp_2024_deep_audit_2026-04-10.md](../data_audit/sipp_2024_deep_audit_2026-04-10.md)
- [sipp_2024_coverage_layer_spec.md](sipp_2024_coverage_layer_spec.md)

Builder script:

- [../../scripts/prototype/build_sipp_2023_corrected_coverage_layer.py](../../scripts/prototype/build_sipp_2023_corrected_coverage_layer.py)

Produced files:

- [sipp_2023_corrected_person_month_flags.parquet](sipp_2023_corrected_person_month_flags.parquet)
- [sipp_2023_correction_pilot_summary.json](sipp_2023_correction_pilot_summary.json)

## Time Interpretation

Use the following interpretation consistently:

- `2023 SIPP` here means the `2023 release`
- this pilot is interpreted mainly as `reference year 2022`
- the file remains a person-month panel-structured release, not a simple cross-section
- observed `SPANEL` values in the retained valid-state file are:
  - `2020`
  - `2021`
  - `2022`
  - `2023`

This matters because the pilot is a correction and comparability exercise, not a direct unwinding estimate.

## Pilot Scope

The pilot intentionally corrected only the project's core monthly insurance / churn layer.

It did **not** attempt to:

- harmonize all covariates
- repair uninsured-care outcomes
- repair plan-detail variables
- build a final multi-year stack

The pilot corrected:

- Medicaid spell overrun effects
- other-coverage spell overrun effects
- affected status flags
- broader public-assistance recodes tied to those spell errors
- broad public coverage and any-insurance recodes, where the official logic could be applied safely

## Implemented Rules

### State filter

The pilot used the same valid-state scope as the `2024` template:

- retain `TEHC_ST` in `1..56`
- exclude non-state codes

### Medicaid and other-coverage spell overrun rules

Implemented from the official `Monthly Health Insurance Variables Error` note:

- if `EMD_EMONTH < MONTHCODE`, treat the Medicaid spell as out of scope for that person-month
- if `EOT_EMONTH < MONTHCODE`, treat the other-coverage spell as out of scope for that person-month

Operationally this means:

- `corr_EMDMTH = 2` when `EMD_EMONTH < MONTHCODE`
- `corr_EOTMTH = 2` when `EOT_EMONTH < MONTHCODE`
- corresponding begin/end edited variables are left missing where the spell should not exist
- corresponding status flags are reset to `0` where the edited begin/end variables are missing

### Public-assistance recode rule

Implemented from the official note:

- `corr_RPUBTYPE2 = 2` when `EMD_EMONTH < MONTHCODE`
- also set `corr_RPUBTYPE2 = 2` when `EOT_EMONTH < MONTHCODE` and the raw `EOTHCOVTYPE = 1`

### Public and any-insurance recodes

The pilot recomputed:

- `corr_RPUBMTH`
- `corr_RHLTHMTH`

using the official recode logic after the corrected monthly components were updated.

### Conservative private-coverage handling

The pilot did **not** fully recompute `RPRIMTH`.

Reason:

- the official private-coverage formula, when applied directly to the local source fields, failed to reproduce the raw `RPRIMTH` recode on a large number of rows
- in contrast, the public-coverage formula reproduced raw `RPUBMTH` almost exactly apart from the rows affected by the targeted correction rules

So the pilot used this conservative rule:

- retain raw `RPRIMTH`
- recompute `RPUBMTH`
- recompute `RHLTHMTH` from retained `RPRIMTH` plus corrected `RPUBMTH`

This was the higher-quality choice for the first pilot.

## Structural Results

Retained valid-state file:

- rows: `475,772`
- persons: `40,245`
- duplicate `SSUID + PNUM + MONTHCODE` keys after filtering: `0`
- retained `MONTHCODE`: `1..12`
- retained `SPANEL`: `2020, 2021, 2022, 2023`

Excluded non-state scope:

- rows: `972`
- persons: `138`

December-positive-weight cohort:

- persons: `39,484`
- rows: `471,467`

Structural verdict:

- the pilot file is clean enough to function as a bounded corrected person-month test object

## Correction Trigger Counts

Rows that actually triggered the main official correction rules:

- `medicare_spell_overrun_rows`: `505`
- `medicaid_spell_overrun_rows`: `1,731`
- `other_spell_overrun_rows`: `204`

Interpretation:

- the affected rows are a small minority of the file
- but they are concentrated exactly where the project's churn labels are most sensitive

## Changed Variables

Changed row counts in the retained valid-state file:

| Variable | Changed rows |
| --- | ---: |
| `AMD_BMONTH` | `3,829` |
| `AMD_EMONTH` | `3,829` |
| `EMDMTH` | `1,731` |
| `AOT_BMONTH` | `585` |
| `AOT_EMONTH` | `585` |
| `EOTMTH` | `204` |
| `RPUBTYPE2` | `1,831` |
| `RPUBMTH` | `1,631` |
| `RHLTHMTH` | `566` |
| `RPRIMTH` | `0` |

Important interpretation:

- the raw spell overrun problem is not huge in raw row count
- but it clearly propagates into public-coverage and any-insurance recodes
- that propagation materially changes the project's churn labels

## Formula Diagnostics

This was the main implementation surprise of the pilot.

Direct formula-reproduction differences against raw recodes:

| Diagnostic | Difference count |
| --- | ---: |
| raw private formula vs raw `RPRIMTH` | `66,007` |
| raw public formula vs raw `RPUBMTH` | `1,631` |
| raw any-insurance formula vs raw `RHLTHMTH` | `33,663` |

Interpretation:

- the public-coverage formula behaves like a usable correction target
- the private-coverage formula does **not** safely reproduce the raw private recode from the local fields used here
- therefore a conservative pilot should not force a full `RPRIMTH` rebuild yet

This is now a real recorded caution for later back-extension.

## Category Shifts

Raw versus corrected monthly category counts:

| Category | Raw | Corrected | Change |
| --- | ---: | ---: | ---: |
| `insured_t` | `437,615` | `437,049` | `-566` |
| `uninsured_t` | `38,157` | `38,723` | `+566` |
| `public_t` | `217,047` | `215,418` | `-1,629` |
| `private_t` | `310,681` | `310,681` | `0` |
| `pure_medicaid_t` | `97,652` | `95,921` | `-1,731` |
| `broad_public_assistance_non_medicaid_t` | `5,140` | `5,050` | `-90` |
| `other_coverage_t` | `14,542` | `14,338` | `-204` |

Interpretation:

- the pilot's largest direct effect is on strict Medicaid month and broad public month
- the any-insurance effect is smaller in level terms but still real
- the monthly correction layer is therefore not cosmetic

## Transition Shifts

Raw versus corrected one-step transition counts:

| Transition count | Raw | Corrected | Change |
| --- | ---: | ---: | ---: |
| `has_consecutive_next_month` | `435,519` | `435,519` | `0` |
| `eligible_medicaid_transition` | `89,207` | `87,733` | `-1,474` |
| `medicaid_exit_next` | `71` | `335` | `+264` |
| `medicaid_exit_to_uninsured_next` | `31` | `109` | `+78` |

Interpretation:

- the correction rules shrink the eligible Medicaid-transition universe slightly
- but they increase observed next-month exits materially
- this is exactly the kind of change that justifies doing the correction before any serious multi-year churn analysis

In plain terms:

- the raw file was carrying forward some Medicaid months that should not have been treated as active coverage
- once those are corrected, exits become more visible

## Comparison To The 2024 Template

What aligns well with the `2024` template:

- same valid-state filtering logic
- same clean person-month key structure
- same one-step transition framework
- same distinction between strict Medicaid and broader public assistance

What remains different:

- this pilot uses the `2023 release`, which mainly reflects `reference year 2022`
- `SPANEL` support is shifted back one year relative to the `2024` template
- the private-coverage recode remains more conservative than the public / Medicaid correction path

## Evaluation

This pilot should be treated as a success.

Why:

- the implementation ran cleanly
- the corrected file preserves a stable person-month structure
- the official correction rules changed the core churn layer in substantively meaningful ways
- the pilot produced a concrete caution that improves later implementation quality:
  - do not force a full `RPRIMTH` rebuild from the currently used local fields

What it does **not** prove:

- that the full `2018-2023` corrected stack is already estimation-ready
- that later `causal ML / targeting` is automatically validated
- that earlier years will be equally straightforward

But it does show:

- the narrow correction path is real
- the burden estimate from Step 3 was reasonable
- moving to a formal stack decision is justified

## Immediate Implication

The project now has enough evidence to make a cleaner `Step 4` decision.

Current practical reading:

- `go` for a narrow corrected-stack implementation path
- still `not yet go` for full estimation
- still `not yet go` for claiming readiness for final `causal ML / targeting`

The next active choice should be one of these:

1. formalize the stack decision in `Step 4`
2. if the stack decision is positive, extend the same correction logic to `2022`

## Bottom Line

The `2023` correction pilot confirms that the official `SIPP` health-insurance error notes matter for this project in a way that changes the observed churn layer.

The correction target remains narrow and manageable.

The strongest current takeaway is:

- correcting the Medicaid/public monthly layer is worth doing
- keeping private-coverage handling conservative is the right quality choice for now
