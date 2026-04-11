# SIPP 2022 Correction Pilot Audit

Last updated: `2026-04-10`

## Purpose

This note records the second bounded implementation pilot that follows the `Step 3` correction specification.

The pilot uses the `2022 SIPP release` as the next back-extension test after the successful `2023` pilot.

This is **not** a final estimating file.

This is **not** an unwinding-year analysis file.

Its purpose is narrower:

- test whether the correction path remains stable one year earlier
- implement the extra `2018-2022` Medicaid end-month repair required by the official Census note
- measure whether the corrected monthly churn layer still behaves coherently
- use the `2022` annual recodes as bounded supplemental checks, not as the main correction logic

## Governing Inputs

The pilot follows:

- [../data_audit/sipp_2018_2023_hi_correction_spec.md](../data_audit/sipp_2018_2023_hi_correction_spec.md)
- [../data_audit/sipp_preflight_2026-04-10.md](../data_audit/sipp_preflight_2026-04-10.md)
- [../data_audit/sipp_2024_deep_audit_2026-04-10.md](../data_audit/sipp_2024_deep_audit_2026-04-10.md)
- [sipp_2024_coverage_layer_spec.md](sipp_2024_coverage_layer_spec.md)
- [sipp_2023_correction_pilot_audit.md](sipp_2023_correction_pilot_audit.md)

Builder script:

- [../../scripts/prototype/build_sipp_2022_corrected_coverage_layer.py](../../scripts/prototype/build_sipp_2022_corrected_coverage_layer.py)

Produced files:

- [sipp_2022_corrected_person_month_flags.parquet](sipp_2022_corrected_person_month_flags.parquet)
- [sipp_2022_correction_pilot_summary.json](sipp_2022_correction_pilot_summary.json)

## Time Interpretation

Use the following interpretation consistently:

- `2022 SIPP` here means the `2022 release`
- this pilot is interpreted mainly as `reference year 2021`
- the file remains a person-month panel-structured release, not a simple cross-section
- observed `SPANEL` values in the retained valid-state file are:
  - `2020`
  - `2021`
  - `2022`

This matters because the pilot is still a correction and comparability exercise, not a direct unwinding estimate.

## Pilot Scope

The pilot intentionally corrected only the project's core monthly insurance / churn layer.

It did **not** attempt to:

- harmonize all covariates
- repair uninsured-care outcomes
- repair plan-detail variables
- build a final multi-year stack

The pilot corrected:

- Medicaid spell overrun effects
- the additional `2018-2022` Medicaid end-month problem
- other-coverage spell overrun effects
- affected status flags
- broader public-assistance recodes tied to those spell errors
- broad public coverage and any-insurance recodes, where the official logic could be applied safely

## Implemented Rules

### State filter

The pilot used the same valid-state scope as the `2024` template:

- retain `TEHC_ST` in `1..56`
- exclude non-state codes

### 2022-specific Medicaid end-month repair

Implemented from the official `Medicaid End-Month Variable Error` note:

- if `EMD_BMONTH > EMD_EMONTH`, reset `EMD_EMONTH` to the maximum `MONTHCODE` observed for that spell

Operationally this pilot treated the spell as grouped within person by:

- `SSUID`
- `PNUM`
- `EMD_BMONTH`

This repaired base end month is then used before the usual overrun rule is applied.

### Medicaid and other-coverage spell overrun rules

Implemented from the official `Monthly Health Insurance Variables Error` note:

- if corrected `EMD_EMONTH < MONTHCODE`, treat the Medicaid spell as out of scope for that person-month
- if `EOT_EMONTH < MONTHCODE`, treat the other-coverage spell as out of scope for that person-month

Operationally this means:

- `corr_EMDMTH = 2` when the corrected Medicaid spell is out of scope
- `corr_EOTMTH = 2` when the other-coverage spell is out of scope
- corresponding begin/end edited variables are left missing where the spell should not exist
- corresponding status flags are reset to `0` where the edited begin/end variables are missing

### Public-assistance recode rule

Implemented from the official note:

- `corr_RPUBTYPE2 = 2` when the Medicaid spell is out of scope
- also set `corr_RPUBTYPE2 = 2` when the other-coverage spell is out of scope and raw `EOTHCOVTYPE = 1`

### Public and any-insurance recodes

The pilot recomputed:

- `corr_RPUBMTH`
- `corr_RHLTHMTH`

using the same bounded logic as the `2023` pilot after the corrected monthly components were updated.

### Conservative private-coverage handling

The pilot again did **not** fully recompute `RPRIMTH`.

It retained the same conservative handling as the `2023` pilot:

- retain raw `RPRIMTH`
- recompute `RPUBMTH`
- recompute `RHLTHMTH` from retained `RPRIMTH` plus corrected `RPUBMTH`

## Structural Results

Retained valid-state file:

- rows: `486,618`
- persons: `41,040`
- duplicate `SSUID + PNUM + MONTHCODE` keys after filtering: `0`
- retained `MONTHCODE`: `1..12`
- retained `SPANEL`: `2020, 2021, 2022`

Excluded non-state scope:

- rows: `1,118`
- persons: `144`

December-positive-weight cohort:

- persons: `40,473`
- rows: `483,315`

Structural verdict:

- the pilot file is clean enough to function as a second bounded corrected person-month test object

## Correction Trigger Counts

Rows that actually triggered the main correction rules:

- `medicare_spell_overrun_rows`: `295`
- `medicaid_begin_gt_end_rows`: `16`
- `medicaid_spell_overrun_rows`: `1,342`
- `other_spell_overrun_rows`: `148`

Interpretation:

- the special `2022` Medicaid begin-greater-than-end problem exists locally, but it is very small in row count
- the broader Medicaid spell-overrun problem remains much more important for churn construction

## Changed Variables

Changed row counts in the retained valid-state file:

| Variable | Changed rows |
| --- | ---: |
| `EMD_BMONTH` | `0` |
| `EMD_EMONTH` | `16` |
| `AMD_BMONTH` | `3,457` |
| `AMD_EMONTH` | `3,457` |
| `EMDMTH` | `1,342` |
| `EOT_BMONTH` | `0` |
| `EOT_EMONTH` | `0` |
| `AOT_BMONTH` | `504` |
| `AOT_EMONTH` | `504` |
| `EOTMTH` | `148` |
| `RPUBTYPE2` | `1,405` |
| `RPUBMTH` | `1,217` |
| `RHLTHMTH` | `509` |
| `RPRIMTH` | `0` |

Important interpretation:

- the special `2022` Medicaid end-month repair is small
- but the downstream churn-label changes are still meaningful because the broader spell-overrun problem continues to propagate into monthly recodes

## Formula Diagnostics

Direct formula-reproduction differences against raw recodes:

| Diagnostic | Difference count |
| --- | ---: |
| raw private formula vs raw `RPRIMTH` | `64,834` |
| raw public formula vs raw `RPUBMTH` | `1,217` |
| raw any-insurance formula vs raw `RHLTHMTH` | `34,434` |

Interpretation:

- the public-coverage formula again behaves like a usable correction target
- the private-coverage formula again does **not** safely reproduce the raw private recode from the local fields used here
- the `RPRIMTH` caution is therefore not just a `2023` artifact

## Category Shifts

Raw versus corrected monthly category counts:

| Category | Raw | Corrected | Change |
| --- | ---: | ---: | ---: |
| `insured_t` | `441,712` | `441,203` | `-509` |
| `uninsured_t` | `44,906` | `45,415` | `+509` |
| `public_t` | `212,252` | `211,035` | `-1,217` |
| `private_t` | `314,669` | `314,669` | `0` |
| `pure_medicaid_t` | `98,644` | `97,302` | `-1,342` |
| `broad_public_assistance_non_medicaid_t` | `5,843` | `5,789` | `-54` |
| `other_coverage_t` | `17,268` | `17,120` | `-148` |

Interpretation:

- the largest direct effect is again on strict Medicaid month and broad public month
- the any-insurance effect is smaller in level terms but still real
- the correction layer remains meaningfully non-cosmetic one year earlier

## Transition Shifts

Raw versus corrected one-step transition counts:

| Transition count | Raw | Corrected | Change |
| --- | ---: | ---: | ---: |
| `has_consecutive_next_month` | `445,563` | `445,563` | `0` |
| `eligible_medicaid_transition` | `90,150` | `89,010` | `-1,140` |
| `medicaid_exit_next` | `42` | `252` | `+210` |
| `medicaid_exit_to_uninsured_next` | `27` | `101` | `+74` |

Interpretation:

- the correction rules again shrink the eligible Medicaid-transition universe slightly
- but they materially increase observed next-month exits
- the same core lesson from the `2023` pilot therefore survives one year earlier

## Annual Recode Diagnostics

Because `2022 SIPP` includes annual health-insurance recodes, this pilot adds bounded person-level checks inside the December-positive-weight cohort.

These are supplemental checks only.

They are **not** the main correction logic.

Comparison results:

| Annual recode | Persons compared | Annual yes / monthly no | Annual no / monthly yes | Exact match count |
| --- | ---: | ---: | ---: | ---: |
| `RHICOVANN` | `40,473` | `0` | `0` | `40,473` |
| `RPUBANN` | `40,473` | `0` | `0` | `40,473` |
| `RPRIVANN` | `40,473` | `0` | `1,578` | `38,895` |
| `RMCAIDANN` | `40,473` | `500` | `0` | `39,973` |

Interpretation:

- corrected monthly any-insurance and public coverage line up perfectly with the annual recodes in this bounded check
- `RPRIVANN` again reinforces the caution that the private layer is not yet something the project should aggressively reconstruct
- `RMCAIDANN` differs for a small subset of people, which is a reminder that the annual recode is useful as a check, not as a replacement for corrected monthly Medicaid logic

## Comparison To The 2023 Pilot And 2024 Template

What remains stable across the `2022` and `2023` pilots:

- same valid-state filtering logic
- same clean person-month key structure
- same one-step transition framework
- same finding that raw insurance errors materially affect churn outcomes
- same caution that private-coverage rebuilding is not yet safe

What is specific to `2022`:

- the extra Medicaid end-month repair is required, but small in trigger count
- annual recodes are available and behave as useful bounded checks
- the file is one step further from the `2024` clean template in time

## Evaluation

This pilot should also be treated as a success.

Why:

- the implementation ran cleanly
- the corrected file preserves a stable person-month structure
- the special `2018-2022` Medicaid end-month rule was successfully integrated
- the correction rules again changed the core churn layer in substantively meaningful ways
- the annual recodes provide supportive bounded checks rather than contradiction

What it does **not** prove:

- that a full corrected `2018-2023` or `2018-2024` stack is already estimation-ready
- that the project has already validated final identification
- that earlier `2021` and `2018-2020` groups will be equally easy

But it does show:

- the corrected-stack path remains credible after moving one year earlier
- the project now has more than one successful correction pilot year
- the next planning step should move from stack feasibility to constrained design diagnostics

## Immediate Implication

The project now has enough evidence to stop treating the corrected-stack path as only a tentative idea.

Current practical reading:

- `go` for continued narrow corrected-stack implementation
- still `not yet go` for full estimation
- still `not yet go` for final `causal ML / targeting`

The next active choice should now be:

1. write the constrained design-diagnostics memo
2. only then decide whether to extend through `2021` or narrow the final stack

## Bottom Line

The `2022` correction pilot confirms that the `2023` pilot was not a one-year fluke.

The narrow correction path continues to look real and useful.

The strongest current takeaway is:

- correcting the Medicaid/public monthly layer remains worth doing
- the `2018-2022` special Medicaid end-month rule is manageable
- private-coverage handling should still remain conservative
- the project is now ready to shift from stack-feasibility testing toward design diagnostics
