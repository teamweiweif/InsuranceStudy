# SIPP 2024 State-Month Merge Audit

Last updated: `2026-04-10`

## Purpose

This note records `Step 2` of the churn / unwinding execution path:

- the first audited merge of the `2024 SIPP release` prototype file
- to one chosen CMS unwinding metric family
- using `TEHC_ST x MONTHCODE`

This is a merge audit, not a causal analysis.

## CMS Metric Family Used

Exact metric family used:

- `Updated Medicaid and CHIP Renewal Outcomes`

Official dataset page:

- <https://data.medicaid.gov/dataset/e6205a51-e6d7-4849-9882-4483b8a28c41>

Local source records used to build this merge:

- [../../reference/external/feasibility_audit/medicaid_unwinding/monthly_data_reports_historical.html](../../reference/external/feasibility_audit/medicaid_unwinding/monthly_data_reports_historical.html)
- [../../reference/external/feasibility_audit/medicaid_unwinding/eligibility_processing_data_report_specifications.pdf](../../reference/external/feasibility_audit/medicaid_unwinding/eligibility_processing_data_report_specifications.pdf)
- [../../reference/external/feasibility_audit/medicaid_unwinding/data_medicaid_snapshot_page.html](../../reference/external/feasibility_audit/medicaid_unwinding/data_medicaid_snapshot_page.html)

## Produced Artifacts

Step 2 output files:

- [cms_updated_renewal_outcomes_state_month_2023.parquet](cms_updated_renewal_outcomes_state_month_2023.parquet)
- [sipp_2024_cms_updated_renewal_outcomes_merged.parquet](sipp_2024_cms_updated_renewal_outcomes_merged.parquet)
- [sipp_2024_cms_updated_renewal_merge_summary.json](sipp_2024_cms_updated_renewal_merge_summary.json)

Builder script:

- [../../scripts/prototype/build_sipp_2024_cms_updated_renewal_merge.py](../../scripts/prototype/build_sipp_2024_cms_updated_renewal_merge.py)

Upstream Step 1 file:

- [sipp_2024_person_month_flags.parquet](sipp_2024_person_month_flags.parquet)

## Merge Design

### SIPP side

The SIPP prototype file comes from the `2024 release`, interpreted mainly as `reference year 2023`.

Frozen Step 1 concepts are documented in:

- [sipp_2024_coverage_layer_spec.md](sipp_2024_coverage_layer_spec.md)

State key:

- `TEHC_ST`

Time key:

- `reference_year * 100 + MONTHCODE`

State crosswalk rule:

- `TEHC_ST` was converted from public-use state FIPS-style codes to USPS state abbreviations
- the merge kept the valid Step 1 state scope only

### CMS side

Selected reporting periods:

- `202303`
- `202304`
- `202305`
- `202306`
- `202307`
- `202308`
- `202309`
- `202310`
- `202311`
- `202312`

These were downloaded from the official `Updated Medicaid and CHIP Renewal Outcomes` Excel links listed on the local historical Medicaid reports page.

CMS variables retained in the state-month table:

- `cms_updated_renewal_due_n`
- `cms_updated_renewed_total_n`
- `cms_updated_renewed_ex_parte_n`
- `cms_updated_renewed_form_n`
- `cms_updated_terminated_total_n`
- `cms_updated_ineligible_form_n`
- `cms_updated_procedural_termination_n`
- `cms_updated_pending_n`
- rate versions of the same core outcomes
- `cms_updated_procedural_share_of_terminated`

## Official Timing Interpretation

The month alignment is operationally clear, but conceptually imperfect.

From the local CMS specifications:

- `Metric 5` is defined as beneficiaries whose renewal is **due** in the reporting period
- the due month is aligned to the cohort's last day of coverage
- it is **not** defined as the first date bulk terminations are effective
- the `Updated Renewal Outcomes` files reflect the outcomes of renewals previously reported as pending, as updated three months after the renewal was due, plus corrections

Practical implication:

- the merge key is defensible at the `state x reporting_month` level
- but the CMS month should be interpreted as a `renewal due / updated disposition month`, not a clean person-level disenrollment month

This is the main reason the merge verdict is not stronger than `usable with caveats`.

## Match Results

### Overall merge outcome

- SIPP person-month rows in the Step 1 prototype: `436,237`
- rows matched to a CMS updated-renewal state-month record: `280,044`
- unmatched rows: `156,193`
- overall matched share: `64.20%`

### State coverage

For the selected reporting periods, the CMS state-month table contains `51` jurisdiction rows per month after excluding the national `US` summary row.

Operationally matched SIPP states across the full merge:

- all `50 states + DC`

### Month coverage

Matched SIPP months:

- `3..12`

Unmatched SIPP months:

- `1`
- `2`

Important interpretation:

- `January` and `February 2023` are unmatched by design for this Step 2 metric family because the official historical page did not list `Updated Renewal Outcomes` files for `202301` or `202302`

### Person-month match share by SIPP month

| SIPP month | Matched rows | Total rows | Matched share |
| --- | ---: | ---: | ---: |
| `1` | `0` | `36,540` | `0.000` |
| `2` | `0` | `36,538` | `0.000` |
| `3` | `1,039` | `36,493` | `0.028` |
| `4` | `9,357` | `36,430` | `0.257` |
| `5` | `20,345` | `36,388` | `0.559` |
| `6` | `32,490` | `36,337` | `0.894` |
| `7` | `35,610` | `36,308` | `0.981` |
| `8` | `36,275` | `36,275` | `1.000` |
| `9` | `36,257` | `36,257` | `1.000` |
| `10` | `36,245` | `36,245` | `1.000` |
| `11` | `36,225` | `36,225` | `1.000` |
| `12` | `36,201` | `36,201` | `1.000` |

### CMS available state count by reporting period

This is the key caveat the merge surfaced.

The merge keys themselves worked.

The limiting issue is early-period CMS coverage completeness in the selected metric family:

| Reporting period | CMS states with non-missing updated renewal data |
| --- | ---: |
| `202303` | `4` |
| `202304` | `18` |
| `202305` | `37` |
| `202306` | `49` |
| `202307` | `50` |
| `202308` | `51` |
| `202309` | `51` |
| `202310` | `51` |
| `202311` | `51` |
| `202312` | `51` |

Interpretation:

- the early `2023` merge weakness is primarily a CMS source-coverage issue
- it is not a `TEHC_ST` merge failure
- by `August 2023`, the selected CMS metric family provides full `50 states + DC` coverage

## What This Merge Does Establish

- the project can operationally link `SIPP` person-month observations to a real official CMS unwinding metric family
- the `TEHC_ST x MONTHCODE` design is structurally viable
- `Updated Renewal Outcomes` can generate a real state-month exposure surface for at least part of `reference year 2023`
- the merge is good enough to continue the project into correction-spec work
- the merge is also good enough to preserve the project's longer-run possibility of `causal ML / targeting`, because there is now a real external unwinding context layer to validate against

## What This Merge Does Not Establish

- it does **not** validate a final causal treatment definition
- it does **not** mean the CMS reporting month equals the individual month of observed coverage loss in SIPP
- it does **not** eliminate the need for `2018-2023` SIPP correction work
- it does **not** justify immediate causal estimation or `policy targeting`

## Merge Verdict

Verdict:

- `usable with caveats`

Reason for this verdict:

- `usable` because the state-month merge works mechanically, covers all `50 states + DC` by `August-December 2023`, and produces a nontrivial linked file
- `with caveats` because:
  - `January-February 2023` have no selected-CMS-metric coverage in this Step 2 setup
  - `March-July 2023` have partial state availability in the chosen CMS metric family
  - the CMS reporting month is a `renewal due / updated disposition` month, not a clean event-time equivalent of person-level disenrollment

## Step 2 Closure Verdict

`Step 2` is complete.

The closure test is satisfied because:

- the exact CMS metric family is named
- month alignment is documented
- matched and unmatched month coverage is documented
- state coverage limitations are documented
- the merge is explicitly rated `usable with caveats`

This unlocks:

- `Step 3`: write the `2018-2023` SIPP correction specification
