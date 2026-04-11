# SIPP 2018-2023 Health Insurance Correction Specification

Last updated: `2026-04-10`

## Purpose

This note is the `Step 3` correction specification for the churn / unwinding project.

Its job is to translate the current official Census warning set into a practical, year-specific correction plan for the `2018-2023` `SIPP` health-insurance layer.

This is a design and execution gate.

It does **not**:

- implement the full corrected stack
- repair every variable in the file
- harmonize all high-dimensional covariates
- validate downstream harm outcomes
- authorize final estimation

It does:

- define the minimum correction target needed for the project's churn / unwinding line
- identify which variables should be repaired, restricted, or avoided
- group the years into workable correction regimes
- estimate the implementation burden
- state whether a corrected multi-year stack looks realistic enough to justify further work

Pilot status:

- the first bounded `2023` correction pilot has now been completed in [../prototype/sipp_2023_correction_pilot_audit.md](../prototype/sipp_2023_correction_pilot_audit.md)
- that pilot supports the narrow correction path described in this note
- it also adds one important caution: do not force a full `RPRIMTH` rebuild from the currently used local source fields
- the next bounded extension to [../prototype/sipp_2022_correction_pilot_audit.md](../prototype/sipp_2022_correction_pilot_audit.md) is now also complete
- taken together, the `2023` and `2022` pilots support the phased corrected-stack path through the late-year group

## Why This Step Matters

The project still aims, if the data support it, to move beyond descriptive churn and toward:

- person-level coverage dynamics
- state-month unwinding context
- later `heterogeneity / causal ML / targeting`

That higher-value contribution is not reachable if the core monthly insurance layer is unstable.

`Step 1` froze a clean `2024 release` template.

`Step 2` showed that a real CMS `state x month` unwinding context layer can be merged to that template.

`Step 3` now asks the next necessary question:

- can `2018-2023` be corrected cleanly enough to justify a broader multi-year stack?

## Governing Evidence

This note builds on:

- [sipp_preflight_2026-04-10.md](sipp_preflight_2026-04-10.md)
- [sipp_2024_deep_audit_2026-04-10.md](sipp_2024_deep_audit_2026-04-10.md)
- [sipp_warning_registry.csv](sipp_warning_registry.csv)
- [sipp_variable_triage.csv](sipp_variable_triage.csv)
- [sipp_core_variable_stability.csv](sipp_core_variable_stability.csv)
- [../prototype/sipp_2024_coverage_layer_spec.md](../prototype/sipp_2024_coverage_layer_spec.md)
- [../prototype/sipp_2024_state_month_merge_audit.md](../prototype/sipp_2024_state_month_merge_audit.md)
- [../../docs/churn_unwinding_execution_handoff.md](../../docs/churn_unwinding_execution_handoff.md)
- [../../docs/churn_targeting_reset_2026-04-10.md](../../docs/churn_targeting_reset_2026-04-10.md)

Official Census source family used here:

- 2023 `Monthly Health Insurance Variables Error`
- 2023 `Health Insurance Begin/End Month Status Flag Error`
- 2022 `Medicaid End-Month Variable Error`
- 2023 `Processing Error Effects on Uninsured Care`
- 2021 `_SCRNR` variables versus recodes
- 2022 `_SCRNR` variables removed from public-use
- 2022 annual health insurance recode note
- 2022 marketplace-coverage scope note
- 2022 other-coverage ambiguity note
- 2021 health-insurance coverage-units note
- 2021 health-insurance feedback spell fix
- 2021 missing values for some health-insurance plan-detail variables

## Scope Of Correction

The correction target is intentionally narrow.

This step focuses on the project's core `insurance measurement layer`, not the full feature matrix.

### In scope now

- monthly coverage state needed for churn construction
- Medicaid-related monthly indicators
- begin/end month spell variables that directly contaminate monthly Medicaid / public / other coverage logic
- corresponding status flags
- the minimum recoded monthly indicators needed to create a corrected churn layer
- year-specific comparability rules for the above

### Not in scope now

- full harmonization of high-dimensional covariates
- full repair of uninsured-care outcomes
- full repair of plan-detail variables
- reconstruction of coverage-unit analysis
- final weighting strategy for a multi-year estimating stack
- causal estimation

Practical interpretation:

- the current correction target is the project's `label layer`
- broader covariate and outcome harmonization remains a later phase if the stack is judged worth building

## Time-Structure Reminder

This correction spec does **not** assume that `2018-2024` form one seamless long panel.

Safer interpretation:

- each annual release is a `person-month` file with panel structure
- later releases, especially `2024`, are overlapping-panels files
- a corrected stack here means a defensible stacked annual-release `person-month` layer
- it does **not** automatically mean a fully validated seven-year continuous person panel

That distinction matters for later `causal ML / targeting` work.

The current goal is to make the monthly churn layer stackable enough to judge whether a broader design is worth pursuing.

## Minimum Corrected Target Layer

The corrected stack does **not** need to recover every insurance object in the public-use files.

It needs to recover, as defensibly as possible, the minimum objects required for the project's first serious multi-year churn design:

| Project object | Working corrected target |
| --- | --- |
| `state_t` | `TEHC_ST`, with the same valid-state filtering used in Step 1 |
| `time_t` | `MONTHCODE`, interpreted within each release's reference-year structure |
| `insured_t` | corrected `RHLTHMTH`-based monthly any-insurance concept |
| `uninsured_t` | corrected `RHLTHMTH = 2` monthly uninsured concept |
| `public_t` | corrected `RPUBMTH` monthly broad public-coverage concept |
| `pure_medicaid_t` | corrected `EMDMTH = 1` monthly strict Medicaid concept |
| `medicaid_exit_next` | one-step transition from corrected `pure_medicaid_t` to corrected `pure_medicaid_t+1 != 1` |
| `medicaid_exit_to_uninsured_next` | one-step transition from corrected `pure_medicaid_t` to corrected `uninsured_t+1 = 1` |

Anything beyond that should be treated as supplemental unless separately audited.

## Year Grouping

The official notes imply that `2018-2023` should not be treated as one homogeneous block.

Use the following year groups for correction work:

| Year group | Why it should be treated separately |
| --- | --- |
| `2018-2020` | Affected by the monthly HI error family and the Medicaid end-month problem, but before the `2021` feedback-spell processing change. |
| `2021` | Still affected by the same core monthly error family, but also marks the health-insurance feedback spell-fix regime shift and the plan-detail missing-value note. |
| `2022-2023` | Still affected by the monthly HI error family, but annual recodes are now present and `_SCRNR` variables are no longer released on public-use files. |
| `2024` | Not a correction target in this step. It remains the clean template reference and validation anchor. |

This grouping is narrow enough to reflect the official changes without pretending every year is wholly unique.

## Official Rule Translation

The key official notes are not just warnings.

They imply a concrete order of operations.

### Rule 1: Correct begin/end spell fields when values extend past the reported spell

Applies primarily to `2018-2023`.

The `Monthly Health Insurance Variables Error` note states that begin/end values for Medicare, Medicaid, and Other coverage were incorrectly assigned to months beyond the reported spell, and should be recoded to missing when the spell end month is earlier than the current `MONTHCODE`.

Project translation:

- for the impacted insurance families, do **not** trust raw `BMONTH` / `EMONTH` values when `EMONTH < MONTHCODE`
- recode impacted edited begin/end variables to missing in those person-months
- treat the raw spell fields as repair targets, not as prototype-ready inputs

For the project's priority variables, this matters most for:

- `EMD_BMONTH`
- `EMD_EMONTH`
- the monthly Medicaid indicator derived from them
- related broader public / other-coverage recodes touched by the same logic

### Rule 2: Correct corresponding status flags

Applies primarily to `2018-2023`.

The `Health Insurance Begin/End Month Status Flag Error` note says status flags should be `0 = not in universe` when the corresponding edited begin/end month variable is missing.

Project translation:

- after correcting begin/end variables, corresponding status flags must be reset
- raw status-flag filters should not be used before this correction
- status flags are supporting repair objects, not trusted analysis variables

This matters most for:

- `AMD_BMONTH`
- `AMD_EMONTH`
- parallel Medicare / private / military / other status flags if they affect broader monthly recodes used in the project

### Rule 3: Apply the Medicaid end-month repair where begin month exceeds end month

Applies to `2018-2022`.

The `Medicaid End-Month Variable Error` note gives a specific fix when `EMD_BMONTH > EMD_EMONTH`: recode `EMD_EMONTH` to the maximum `MONTHCODE` value for the spell.

Project translation:

- `2018-2022` require an extra Medicaid spell repair layer beyond the general `EMONTH < MONTHCODE` cleanup
- this is one reason the Medicaid layer cannot be treated as a simple global recode

This rule is central because the project's strict Medicaid month is currently anchored on `EMDMTH`.

### Rule 4: Recompute or repair affected monthly indicator logic before using churn outcomes

Applies primarily to `2018-2023`.

The `Monthly Health Insurance Variables Error` note explicitly states that the error propagates into associated edited and recoded monthly indicator variables.

Project translation:

- corrected churn work cannot stop at fixing spell fields
- the monthly indicators that feed `insured`, `public`, and `Medicaid` logic must also be corrected or re-derived
- the project should privilege the minimum corrected monthly state layer over trying to rescue every insurance subtype

At minimum, the corrected layer must settle:

- `RHLTHMTH`
- `RPUBMTH`
- `EMDMTH`
- `RPUBTYPE2`
- `EOTMTH`

### Rule 5: Do not treat uninsured-care variables as part of the first corrected stack

Applies primarily to `2018-2023`.

The `Processing Error Effects on Uninsured Care` note says users should first correct the monthly insurance variables and then impute uninsured-care values themselves.

Project translation:

- uninsured-care variables are outside the first corrected stack
- they should be marked `avoid for now`
- they are not needed to decide whether the churn / unwinding design is viable

### Rule 6: Do not use `_SCRNR` variables as a cross-year solution

Applies to `2018-2023`.

The `2021` note says `_SCRNR` variables can underestimate annual coverage by type and should not be used to generate annual coverage estimates.

The `2022` note says `_SCRNR` variables are no longer released on public-use files from `2022` onward.

Project translation:

- `_SCRNR` variables are not a valid bridge across the `2018-2023` correction problem
- do not build any cross-year pipeline that depends on them
- any annual coverage checks should rely on other logic

### Rule 7: Annual recodes are supplemental, not the main correction path

Applies to `2022-2023` in this step.

The annual recode note says `2022 SIPP` added annual recodes such as `RHICOVANN`, `RPUBANN`, and `RMCAIDANN`.

Project translation:

- these can be used for annual consistency checks beginning in `2022`
- they cannot solve `2018-2021`
- they cannot substitute for corrected month-level churn logic

### Rule 8: Marketplace and other-coverage variables remain auxiliary

Applies to `2018-2023`.

The marketplace note says `RMARKTPLACE` does not identify coverage type.

The other-coverage note says the `other` line is substantively ambiguous.

Project translation:

- `RMARKTPLACE` is not a payer-type variable
- `EOTMTH` should remain auxiliary
- neither should be allowed to redefine strict Medicaid for the core churn layer

## Variable Handling Map

The table below states how the project should handle the most relevant variables in the corrected stack.

| Variable or family | `2018-2020` | `2021` | `2022-2023` | Working rule |
| --- | --- | --- | --- | --- |
| `SSUID`, `PNUM`, `MONTHCODE` | Use | Use | Use | Stable core keys. No correction target. |
| `SPANEL`, `SWAVE` | Use | Use | Use | Stable structure fields. Use for interpretation only. |
| `TEHC_ST` | Use | Use | Use | Use as monthly state key, with non-state exclusions applied consistently. |
| `WPFINWGT` | Use | Use | Use | Stable weight field. Weighting strategy remains separate from correction logic. |
| `RHLTHMTH` | Repair then use | Repair then use | Repair then use | Core any-insurance / uninsured recode. Treat as affected by monthly HI error family until corrected. |
| `RPUBMTH` | Repair then use | Repair then use | Repair then use | Broad public-coverage concept. Same caution as above. |
| `EMDMTH` | Repair then use | Repair then use | Repair then use | Core strict Medicaid month. Must reflect corrected spell logic first. |
| `RPUBTYPE2` | Repair then restrict | Repair then restrict | Repair then restrict | Keep separate from strict Medicaid. Use only as broader public-assistance context. |
| `EMD_BMONTH`, `EMD_EMONTH` | Repair | Repair | Repair | Direct repair targets. Do not use raw. `2018-2022` need the extra Medicaid end-month fix. |
| `AMD_BMONTH`, `AMD_EMONTH`, analogous status flags | Repair | Repair | Repair | Reset after corresponding edited variables are corrected. |
| `EOTMTH`, other-coverage spell variables | Repair then restrict | Repair then restrict | Repair then restrict | Repair if needed to preserve broader recodes, but keep auxiliary due to conceptual ambiguity. |
| `_SCRNR` family | Avoid | Avoid | Not available | Do not use for annual estimation or cross-year bridging. |
| annual recodes (`RHICOVANN`, `RPUBANN`, `RMCAIDANN`, etc.) | Not available | Not available | Supplemental only | Use only for annual validation checks in `2022-2023`. |
| uninsured-care variables | Avoid | Avoid | Avoid | Outside the first corrected stack. |
| plan-detail variables named in missing-value note | Avoid | Avoid | Not central | Not needed for first corrected churn layer. |
| coverage-unit variables | Not available in checked public-use schemas | Not available in checked public-use schemas | Not available in checked public-use schemas | Outside public-use scope. |

## Recommended Correction Workflow

This is the preferred execution order for the actual implementation phase.

### Phase A: Build one narrow corrected monthly insurance layer

Start from each annual release main file and retain only the variables needed for:

- person-month identification
- state/month linkage
- weights
- monthly insurance correction
- Step 1-compatible churn definitions

Do **not** widen the scope yet to all possible covariates or outcomes.

### Phase B: Apply official spell and status corrections

For the affected years:

1. apply the official `EMONTH < MONTHCODE` recodes for impacted spell variables
2. apply the official status-flag recodes where edited begin/end variables are missing
3. for `2018-2022`, apply the additional Medicaid end-month repair when `EMD_BMONTH > EMD_EMONTH`

### Phase C: Rebuild the project-facing monthly state variables

After spell and flag correction, rebuild or verify the minimum monthly state layer needed for the project:

- `insured_t`
- `uninsured_t`
- `public_t`
- `pure_medicaid_t`
- auxiliary broader-public / other-coverage flags

The project should prefer a narrow, defendable layer over a large but unstable one.

### Phase D: Validate against the `2024` template, not against raw intuition

Use `2024` as the clean reference for:

- variable meanings
- state filtering
- outcome definitions
- the distinction between strict Medicaid and broader public assistance

This is especially important for:

- `EMDMTH` versus `RPUBTYPE2`
- transition definitions
- how to keep `other coverage` out of the core policy category

### Phase E: Pilot one late year before full back-extension

The first implementation pilot should be:

- `2023` first

Reason:

- it is closest to the clean `2024` template
- annual recodes are available for supplemental checks
- it is the year most directly adjacent to the current unwinding prototype path

Then extend backward to:

- `2022`
- `2021`
- `2018-2020`

That order minimizes wasted effort if the corrected stack proves too fragile.

## What Should Not Be Corrected In This Phase

To keep the project aligned with its research objective, do **not** turn this phase into a universal data-cleaning exercise.

Specifically, this phase should not try to:

- perfect all plan-detail insurance variables
- rescue uninsured-care outcomes
- harmonize all demographic or labor-market covariates
- build a final downstream-harm outcome set
- solve every annual-coverage question

Those are separate tasks.

The current gate is whether the project can support a defendable corrected multi-year churn layer.

## Implementation Burden Estimate

Burden estimate:

- `moderate to heavy`, but not prohibitive

Why it is not light:

- multiple official notes interact
- Medicaid requires an extra year-specific spell fix in `2018-2022`
- the corrected layer must be revalidated at the monthly-indicator level, not just spell fields
- there is a `2021` regime-shift caution from the feedback-spell fix
- later `causal ML / targeting` would eventually require broader covariate and outcome harmonization beyond this step

Why it still looks tractable:

- the official notes provide explicit recode logic for the most important contaminated variables
- the project's first corrected target layer is narrow
- the `2024` template already exists as a clean anchor
- `2023` can be used as a bounded pilot year before deeper back-extension

## Stack Feasibility Judgment

Current judgment:

- a corrected multi-year churn stack looks `realistic enough to justify implementation`
- but it is **not yet** validated enough to be treated as estimation-ready

More precise judgment:

- `go` for a narrow correction-implementation phase focused on the monthly insurance / churn layer
- `not yet go` for full multi-year estimation
- `not yet go` for claiming the stack is strong enough for final `causal ML / targeting`

This means the project should proceed in two distinct stages:

1. implement the narrow corrected monthly insurance layer, beginning with `2023`
2. only then decide whether the corrected stack is clean enough to support broader estimation and later `causal ML / targeting`

## Relation To The Project's Intended Contribution

This correction step is not a retreat from the project's higher-value ambition.

It is the gate that determines whether that ambition is data-credible.

The project still aims, if feasible, to contribute through:

- person-level churn dynamics
- state-month unwinding context
- later heterogeneity and possible `causal ML`
- eventual targeting / prioritization logic

But none of those are defensible if the churn labels are unstable across `2018-2023`.

So the correct reading of this step is:

- `Step 3` protects the possibility of later `causal ML / targeting`
- it does not guarantee it

## Post-Pilot Clarifications

This section records clarification points that came up after the first `2023` correction pilot.

It should be read together with:

- [../prototype/sipp_2023_correction_pilot_audit.md](../prototype/sipp_2023_correction_pilot_audit.md)
- [../../docs/churn_unwinding_execution_handoff.md](../../docs/churn_unwinding_execution_handoff.md)

### Clarification 1: the correction target is still narrow

The pilot should not be read as a full correction of all `SIPP` variables.

At this stage, `correction` means:

- repair the monthly insurance measurement layer
- repair the project-facing churn-label layer derived from it

It does **not** yet mean:

- harmonize all high-dimensional covariates
- repair all downstream outcomes
- build a final targeting feature set

### Clarification 2: the pilot shows that raw outcome construction was affected

The pilot did **not** show that official corrections are irrelevant.

It showed the opposite.

The official spell and recode corrections changed the project's own churn outcomes in meaningful ways.

Most importantly:

- some raw Medicaid months were being carried forward when they should no longer have counted as active coverage
- once corrected, one-step Medicaid exits became more visible

So the correct reading is:

- the raw monthly insurance layer does affect churn-outcome construction
- the public / Medicaid / uninsured correction path is usable
- the project should not return to naive raw stacking for `2018-2023`

### Clarification 3: the current fix is partial but credible

The pilot does **not** imply that every insurance subtype is now clean.

Current more precise reading:

- `EMDMTH`, `RPUBMTH`, `RPUBTYPE2`, `EOTMTH`, and `RHLTHMTH` can be handled in a bounded correction framework for the project's first churn layer
- `RPRIMTH` should remain conservative for now because direct rebuilding from the currently used local fields diverged too much from the raw recode

So the quality choice remains:

- fix the public / Medicaid side where the logic is defensible
- do not force a private-coverage rebuild beyond what the data support

### Clarification 4: why earlier years can still matter for an unwinding-focused paper

`Unwinding` itself is concentrated in recent years.

That does **not** eliminate the value of earlier corrected years.

Within the current project logic, earlier years can still contribute as:

- pre-period support
- baseline churn-risk support
- baseline heterogeneity support
- validation support for the corrected monthly churn layer

They should not be sold as unwinding-treated years.

If the project stays focused on unwinding, the estimand should remain anchored on unwinding-era treatment variation.

### Clarification 5: what a corrected stack would and would not add for later `causal ML`

A corrected multi-year stack would help later `causal ML / targeting` work by:

- reducing measurement error in the churn labels
- improving sample support for heterogeneity work
- giving later `DiD / event-study / DML` designs a longer and cleaner pre-period

But it would **not** by itself:

- validate the unwinding treatment definition
- settle timing interpretation
- complete causal identification
- make targeting claims automatically defendable

So the right reading is:

- the corrected stack is potentially enabling
- not automatically sufficient

## Immediate Next Execution Recommendation

The first `2023` correction pilot is now complete.

That means the next active decision is no longer "whether to pilot."

It is:

- whether to treat the pilot as strong enough to justify a formal corrected-stack `go`

That extension to `2022` is now complete.

So the next active artifact should be:

- a constrained design-diagnostics memo

Only after that should the project decide whether to:

- extend through `2021`
- backfill `2018-2020`
- or narrow the eventual corrected stack further

## Bottom Line

The project does **not** need a full-file, all-variable correction pass right now.

It needs a narrow, high-quality correction layer for the insurance variables that define:

- Medicaid month
- uninsured month
- next-month Medicaid exit
- next-month exit to uninsured

That layer looks buildable.

The practical recommendation is:

- proceed
- start with `2023`
- keep the correction target narrow
- treat broader covariates and downstream outcomes as later phases

Current status update:

- `2023` pilot completed
- `2022` extension completed
- the next move should now shift from stack-feasibility testing to design diagnostics

## References

Official Census pages:

- Monthly HI error: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2023-usernotes/2023-monthly-hi-variables-error.html>
- Begin/end status-flag error: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2023-usernotes/2023-hi-month-flag-status.html>
- Medicaid end-month error: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-medicaid-variable-error.html>
- Uninsured-care processing effects: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2023-usernotes/2023-processing-error-effects.html>
- `_SCRNR` versus recodes: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2021-usernotes/scrnr-health-ins-var-vs-recod.html>
- `_SCRNR` removed from public-use: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-health-ins-scrnr-var.html>
- Annual recodes: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-ann-health-ins-covr-recods.html>
- Marketplace scope: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-health-ins-mrktpl-covr.html>
- Other-coverage ambiguity: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-othr-health-ins-cov-reprts.html>
- Coverage units: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2021-usernotes/2021-sipp-health-Insurance-coverage-units.html>
- Feedback spell fix: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2021-usernotes/health-ins-feedbk-spell-fix.html>
- Missing plan-detail values: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2021-usernotes/miss-val-some-health-ins-vars.html>
