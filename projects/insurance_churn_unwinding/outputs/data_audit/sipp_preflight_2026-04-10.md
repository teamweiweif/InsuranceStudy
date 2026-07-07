# SIPP Audit Memo

Last updated: `2026-04-10`

## Scope

This note upgrades the earlier `SIPP` preflight into a second-stage audit memo for the churn / unwinding project.

It combines:

- local download completeness checks
- local schema checks for `2018-2024`
- the local `2024 SIPP` deep audit
- official Census user notes relevant to health insurance measurement

This note is still **not** a modeling memo.

Its job is narrower:

- clarify the time structure with no loose shorthand
- identify the health-insurance variables that are structurally usable now
- identify the variables that remain too risky for defensible churn construction
- state what is currently feasible, versus what is still only plausible

Important correction:

- earlier shorthand in this workspace sometimes treated `2024 SIPP` like a `CY2024` reference-year file
- that is misleading
- in official Census terminology, `2024 SIPP` is a `2024` collection / release label, while most reference-year content in that release is for `January-December 2023`

## Files Used

Local data and schema files:

- [pu2018_csv.zip](../../data/raw/feasibility_audit/sipp/2018/pu2018_csv.zip)
- [pu2019_csv.zip](../../data/raw/feasibility_audit/sipp/2019/pu2019_csv.zip)
- [pu2020_csv.zip](../../data/raw/feasibility_audit/sipp/2020/pu2020_csv.zip)
- [pu2021_csv.zip](../../data/raw/feasibility_audit/sipp/2021/pu2021_csv.zip)
- [pu2022_csv.zip](../../data/raw/feasibility_audit/sipp/2022/pu2022_csv.zip)
- [pu2023_csv.zip](../../data/raw/feasibility_audit/sipp/2023/pu2023_csv.zip)
- [pu2024_csv.zip](../../data/raw/feasibility_audit/sipp/2024/pu2024_csv.zip)
- [lgtwgt2024yr4_csv.zip](../../data/raw/feasibility_audit/sipp/2024/lgtwgt2024yr4_csv.zip)
- [2018_schema.json](../../reference/external/feasibility_audit/sipp/2018_schema.json)
- [2019_schema.json](../../reference/external/feasibility_audit/sipp/2019_schema.json)
- [2020_schema.json](../../reference/external/feasibility_audit/sipp/2020_schema.json)
- [2021_schema.json](../../reference/external/feasibility_audit/sipp/2021_schema.json)
- [2022_schema.json](../../reference/external/feasibility_audit/sipp/2022_schema.json)
- [2023_schema.json](../../reference/external/feasibility_audit/sipp/2023_schema.json)
- [2024_schema.json](../../reference/external/feasibility_audit/sipp/2024_schema.json)

Local documentation:

- [2024_sipp_users_guide.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_users_guide.pdf)
- [2024_sipp_data_dictionary.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_data_dictionary.pdf)
- [2024_sipp_release_notes.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_release_notes.pdf)
- [2022_monthly_hi_variables_error.html](../../reference/external/feasibility_audit/sipp/2022_monthly_hi_variables_error.html)

Local audit outputs already produced:

- [sipp_2024_deep_audit_2026-04-10.md](sipp_2024_deep_audit_2026-04-10.md)
- [sipp_2024_core_profile.json](sipp_2024_core_profile.json)
- [sipp_2024_consistency_detail.json](sipp_2024_consistency_detail.json)
- [sipp_2024_panel_wave_counts.csv](sipp_2024_panel_wave_counts.csv)
- [sipp_2024_core_value_counts.csv](sipp_2024_core_value_counts.csv)
- [sipp_2024_public_assistance_mismatch_sample.csv](sipp_2024_public_assistance_mismatch_sample.csv)

New sidecar outputs for this note:

- [sipp_warning_registry.csv](sipp_warning_registry.csv)
- [sipp_core_variable_stability.csv](sipp_core_variable_stability.csv)
- [sipp_variable_triage.csv](sipp_variable_triage.csv)

## 1. Download Completeness Check

This check was completed before any structure audit.

Manifest / log status:

- `14` SIPP artifacts were targeted in the local acquisition manifest
- `7` were main data zips for `2018-2024`
- `7` were schema JSON files for `2018-2024`
- all `14/14` manifest targets exist locally
- batch log status was `13 downloaded` and `1 exists`

Zip integrity:

- all local SIPP zip files opened successfully
- the currently staged SIPP data are complete enough for structural audit

Current qualification:

- this confirms completeness relative to the current local acquisition manifest
- it does **not** confirm that every officially available support file has been staged locally
- most importantly, the workspace does **not** currently contain local copies of replicate-weight files or the `FINYR2` / `FINYR3` longitudinal files for the `2024` release

## 2. Time Structure Clarification

This section corrects the main ambiguity left in the earlier note.

### Key concepts

| Concept | Meaning in this project | `2024 SIPP` interpretation |
| --- | --- | --- |
| release / collection year | the Census label for the annual public-use release | `2024` |
| interview year | the year in which the annual collection cycle occurs | `2024` collection cycle |
| reference year | the prior calendar year most content refers to | `2023` |
| reference months | the months indexed by `MONTHCODE` | `1-12` of reference year `2023` |
| panel year | the originating panel identified by `SPANEL` | `2021`, `2022`, `2023`, `2024` are all present locally |
| wave | the interview round within panel | local `2024` file contains `SWAVE=4,3,2,1` across the overlapping panels |
| collection-year file vs panel file | annual public-use file assembled from overlapping panels | `2024 SIPP` is **not** equivalent to "the 2024 panel" |

### Official guidance

From the `2024 SIPP Users Guide`:

- SIPP is collected as yearly overlapping panels beginning with the `2018` panel
- panels collected in a given annual cycle are collectively referred to by the calendar year of collection
- most questions in `2024 SIPP` refer to the **previous calendar year**, `January through December 2023`
- over the four-wave design, each panel covers `48` consecutive reference months
- for `2024 SIPP`, the calendar-year estimates should use the `December` reference month weight

### Local evidence

From the local main files:

- [pu2018_csv.zip](../../data/raw/feasibility_audit/sipp/2018/pu2018_csv.zip) behaves like a single-panel release file with `SPANEL=2018` only
- [pu2024_csv.zip](../../data/raw/feasibility_audit/sipp/2024/pu2024_csv.zip) contains:
  - `SPANEL=2021`, `SWAVE=4`
  - `SPANEL=2022`, `SWAVE=3`
  - `SPANEL=2023`, `SWAVE=2`
  - `SPANEL=2024`, `SWAVE=1`
- `MONTHCODE` takes values `1-12` locally

This is the correct reading:

- `2024 SIPP` is a `2024` release / collection-year file
- most content in that release refers to `reference year 2023`
- the file is assembled from multiple panels
- therefore it should **not** be described loosely as "the 2024 panel"

Practical implication:

- any future merge to external state-month unwinding data must align to **reference months in 2023**, not to the `2024` release label

## 3. 2024 Local Structure Cross-Check

The local `2024` deep audit remains useful, but it now needs to be read with the corrected time structure above.

Observed local counts from [pu2024_csv.zip](../../data/raw/feasibility_audit/sipp/2024/pu2024_csv.zip):

- rows: `437,168`
- unique persons: `36,915`
- duplicate `SSUID + PNUM + MONTHCODE` keys: `0`

Observed local panel-wave composition:

- `SPANEL=2021`, `SWAVE=4`: `67,567`
- `SPANEL=2022`, `SWAVE=3`: `139,584`
- `SPANEL=2023`, `SWAVE=2`: `90,973`
- `SPANEL=2024`, `SWAVE=1`: `139,044`

Interpretation:

- the `2024` release is structurally coherent
- it is usable as the current template year for variable logic
- it is still **not** enough to validate a multi-year churn design by itself

## 4. Health-Insurance Warning Registry

Full sidecar registry:

- [sipp_warning_registry.csv](sipp_warning_registry.csv)

Compact registry:

| Official note | Years affected | Mainly affects | Handling | Why it matters |
| --- | --- | --- | --- | --- |
| [Monthly Health Insurance Variables Error](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2023-usernotes/2023-monthly-hi-variables-error.html) | `2018-2023` | monthly indicators, spell begin/end variables, status flags | `NEEDS YEAR-SPECIFIC CORRECTION` | Official note says monthly Medicare, Medicaid, and Other coverage fields were processed incorrectly in `2018-2023`. |
| [Health Insurance Begin/End Month Status Flag Error](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2023-usernotes/2023-hi-month-flag-status.html) | `2018-2023` | begin/end month status flags | `NEEDS YEAR-SPECIFIC CORRECTION` | Not-in-universe status flags can be wrong when the corresponding begin/end variable is missing. |
| [Medicaid End-Month Variable Error](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-medicaid-variable-error.html) | `2018-2022` | `EMD_EMONTH` and Medicaid spell construction | `NEEDS YEAR-SPECIFIC CORRECTION` | Some Medicaid spells have invalid end months. |
| [Processing Error Effects on Uninsured Care](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2023-usernotes/2023-processing-error-effects.html) | `2018-2023` | uninsured-care outcomes and flags | `AVOID` | Official guidance says users must first repair monthly health insurance fields and then impute uninsured-care values themselves. |
| ["_SCRNR" Health Insurance Variables Versus Recodes](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2021-usernotes/scrnr-health-ins-var-vs-recod.html) | `2018-2021` public-use | annual screener indicators | `AVOID` | Official note says `_SCRNR` variables may underestimate annual coverage and should not be used for annual estimates. |
| [Health Insurance "_SCRNR" Variables](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-health-ins-scrnr-var.html) | `2022-2024` public-use | release availability | `SAFE ALTERNATIVE REQUIRED` | Starting with `2022`, `_SCRNR` variables are not released on the public-use file. |
| [Annual Health Insurance Coverage Recodes](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-ann-health-ins-covr-recods.html) | `2022-2024` | annual recodes | `CAUTION` | Annual recodes exist only from `2022` onward, so they cannot anchor a simple `2018-2024` annual stack. |
| [Health Insurance Marketplace Coverage](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-health-ins-mrktpl-covr.html) | `2018-2024` conceptually relevant | `RMARKTPLACE` | `CAUTION` | Official note says `RMARKTPLACE` does not identify coverage type. |
| [Other Health Insurance Coverage Reports](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-othr-health-ins-cov-reprts.html) | `2018-2024` conceptually relevant | "other coverage" variables | `CAUTION` | Official note says the "other coverage" line is ambiguous. |
| [Health Insurance Coverage Units](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2021-usernotes/2021-sipp-health-Insurance-coverage-units.html) | public-use availability issue | coverage-unit identifiers | `AVOID` | Coverage-unit variables are not available in the checked `2018-2024` public-use schemas. |
| [Health Insurance Feedback Spell Fix](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2021-usernotes/health-ins-feedbk-spell-fix.html) | `2021+` processing regime | spell comparability | `CAUTION` | Processing changed beginning in `2021` to reduce false transitions, so spell comparisons across the `2020` / `2021` boundary need care. |
| [Missing Values for Some Health Insurance Variables](https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2021-usernotes/miss-val-some-health-ins-vars.html) | `2020-2021` | plan-detail variables | `AVOID` | Several plan-detail variables have incorrect missingness and are not first-prototype variables. |

Current decision-quality reading:

- the project has enough official evidence to say that raw `2018-2023` health-insurance fields are **not** ready for final churn construction
- the project does **not** have enough evidence to call the monthly coverage layer clean
- `2024` is the least contaminated template year in the current audit, but even that only supports prototype work

## 5. Working Variable Triage

Full sidecar:

- [sipp_variable_triage.csv](sipp_variable_triage.csv)

Working map:

| Variable or family | Years | Category | Working rule |
| --- | --- | --- | --- |
| `SSUID`, `PNUM`, `MONTHCODE` | `2018-2024` | `SAFE PROTOTYPE` | Use as the person-month key. |
| `SPANEL`, `SWAVE` | `2018-2024` | `SAFE PROTOTYPE` | Use for structure parsing, but do not confuse them with reference-year definitions. |
| `TEHC_ST` | `2018-2024` | `SAFE PROTOTYPE` | Best current person-month state variable for linkage, after excluding non-state codes such as `60` and `61`. |
| `TST_INTV` | `2018-2024` | `USE WITH CAUTION` | Interview-address state, not month-level residence. |
| `TMOVER` | `2018-2024` | `USE WITH CAUTION` | Use for move diagnostics only. |
| `WPFINWGT` | `2018-2024` | `SAFE PROTOTYPE` | Use for reference-year estimates under the official December-weight rule. |
| `FINYR4` | local `2024` longitudinal file only | `USE WITH CAUTION` | Feasible only for the `2024` release and only for the `2020-2023` four-year cohort. |
| `RHLTHMTH`, `RPUBMTH` | `2024` safer; `2018-2023` corrected use only | `USE WITH CAUTION` | Prototype on `2024`; do not stack raw `2018-2023` values. |
| `RPUBTYPE2` | `2018-2024` | `USE WITH CAUTION` | Do not treat as a pure Medicaid indicator. The `2024` deep audit shows it is broader in practice than `EMDMTH`. |
| `EMDMTH` | `2024` safer; `2018-2023` corrected use only | `USE WITH CAUTION` | Best current candidate for pure Medicaid month in `2024`, but not safe to use naively in `2018-2023`. |
| `EMD_BMONTH`, `EMD_EMONTH`, `RMD_CFLG` | `2018-2023` especially risky | `AVOID UNTIL CORRECTED` | Directly implicated by multiple official user notes. |
| `RHICOVANN`, `RPRIVANN`, `RPUBANN`, `RMCAIDANN` | `2022-2024` only | `USE WITH CAUTION` | Useful for annual checks, not for validating monthly churn logic. |
| `EPR_SCRNR`, `EMC_SCRNR`, `EMD_SCRNR`, `EML_SCRNR`, `EOT_SCRNR` | `2018-2021` only | `AVOID` | Do not use as annual coverage indicators; they disappear from `2022+` public-use. |
| `RMARKTPLACE` | `2018-2024` | `USE WITH CAUTION` | Marketplace channel flag only; not a payer-type classifier. |
| `EOTMTH` and "other coverage" family | `2018-2024` | `USE WITH CAUTION` | Keep separate from the core Medicaid / private / uninsured prototype categories unless classified explicitly. |

The `2024` deep audit materially improves this triage:

- it verifies that `SSUID + PNUM + MONTHCODE` is clean locally in `2024`
- it verifies that `TEHC_ST` is populated in `2024`
- it verifies that `EMDMTH` and `RPUBTYPE2` should not be collapsed into the same concept
- it verifies that raw `2024` Medicaid spell fields pass basic internal consistency checks

## 6. Core Variable Stability Matrix

Full sidecar:

- [sipp_core_variable_stability.csv](sipp_core_variable_stability.csv)

Compact cross-year summary:

| Variable family | `2018-2020` | `2021` | `2022-2024` | Break that matters now |
| --- | --- | --- | --- | --- |
| IDs: `SSUID`, `PNUM`, `MONTHCODE` | present, stable labels | present, stable labels | present, stable labels | no structural break found |
| time structure: `SPANEL`, `SWAVE` | present | present | present | no rename, but interpretation must track release-year vs panel-year |
| geography: `TEHC_ST`, `TST_INTV`, `TMOVER` | present | present | present | no schema break found |
| monthly coverage recodes: `RHLTHMTH`, `RPUBMTH`, `RPUBTYPE2` | present | present with wording shifts | present with wording shifts | no rename, but official errors affect `2018-2023`; `RPUBTYPE2` concept needs care |
| Medicaid monthly indicator: `EMDMTH` | present | present with wording shift | present with wording shift | no rename, but official errors affect `2018-2023` |
| Medicaid spell family: `EMD_BMONTH`, `EMD_EMONTH`, `RMD_CFLG` | present | present | present | no rename, but direct official hazards make raw stacking unsafe |
| main-file weight: `WPFINWGT` | present | present | present | structurally stable |
| annual recodes: `RHICOVANN`, `RPRIVANN`, `RPUBANN`, `RMCAIDANN` | absent | absent | present | this is a real cross-year break |
| annual screeners: `_SCRNR` family | present | present | absent | this is a real cross-year break and they are not recommended anyway |
| marketplace / other-coverage: `RMARKTPLACE`, `EOTMTH` | present | present | present | no rename, but both need concept care |

Current conclusion:

- the core structural variables are stable enough to support a serious harmonization layer
- the main break points are not IDs or geography
- the main break points are health-insurance processing warnings and the `2022` shift from `_SCRNR` to annual recodes

## 7. Weight and Merge Feasibility

### What is staged locally now

Calendar / reference-year work:

- `WPFINWGT` is present in the main data files for `2018-2024`

Longitudinal work:

- local `2024` longitudinal weight file: [lgtwgt2024yr4_csv.zip](../../data/raw/feasibility_audit/sipp/2024/lgtwgt2024yr4_csv.zip)
- local columns observed: `ssuid | pnum | spanel | finyr4`

Not staged locally at this time:

- `FINYR2`
- `FINYR3`
- person-month replicate weights files
- longitudinal replicate weights files

### Merge keys

From the official `2024 SIPP Users Guide`:

- main person-month data are keyed by `SSUID + PNUM + MONTHCODE`
- longitudinal weight files merge by `SSUID + PNUM`
- replicate weights, when used, are person-month files merged by `SSUID + PNUM + MONTHCODE`

### What is feasible now

Feasible now:

- reference-year estimates from the `2024` release using `WPFINWGT`
- a `2024` release prototype that applies the official December-weight rule
- a `2024` release merge with `FINYR4` for the `2020-2023` four-year longitudinal cohort

Not yet locally supported:

- `2024` release + `FINYR2`
- `2024` release + `FINYR3`
- replicate-weight-based variance work
- a fully supported multi-year longitudinal design outside the currently staged `FINYR4` cohort

Important correction to earlier shorthand:

- "CY2024 + FINYR4" is the wrong description
- the correct description is "the `2024` release merged with `FINYR4`, which covers the `2020-2023` four-year reference period"

## 8. State-Policy Linkability Memo

### Best current state variable

Current best candidate:

- `TEHC_ST`

Reason:

- it is the monthly state of residence
- it is present in every checked `2018-2024` schema
- the `2024` deep audit found it populated on all `2024` rows

Current weaker candidate:

- `TST_INTV`

Reason:

- it is interview-address state, not month-specific residence
- it has universe-related missingness in `2024`

### Correct linkage unit

The most defensible unit for an unwinding merge is:

- `person-month by TEHC_ST and MONTHCODE`

Not:

- person only
- interview-state only
- release-year only

### Movers

Conceptually, if a respondent changes state within the reference year:

- `TEHC_ST` should carry the month-specific residence state
- `TMOVER` should be used as a diagnostic for mobility and merge sensitivity
- `TST_INTV` should not overwrite `TEHC_ST`

Still unresolved:

- a full move-sensitive state-month merge has not yet been run
- the treatment dataset has not yet been harmonized to the same month coding
- the handling rule for non-state `TEHC_ST` codes needs to be frozen explicitly

### Current verdict

State-policy linkage is:

- `currently plausible at the structure level`

But it is **not yet validated**, because:

- the reference-year alignment must be handled correctly
- the health-insurance variable layer is not yet corrected for `2018-2023`
- the external state-month unwinding dataset has not yet been merged and audited against `TEHC_ST`

## 9. Revised ML Readiness View

The ML question is no longer generic. It separates into three different tasks.

### 1. Risk prediction

Most plausible first use:

- predict who experiences Medicaid exit, uninsured gap, or unstable monthly coverage

What must be true first:

- the monthly coverage variable map must be frozen
- `2018-2023` must either be corrected or excluded
- the target outcome must be defined cleanly at the person-month level

Current status:

- `2024` supports prototype work
- a corrected `2018-2023` stack is **not yet ready**

### 2. Heterogeneity estimation

Meaning here:

- estimate which subgroups are most exposed to harm from churn or unwinding-related loss

What must be true first:

- coverage outcomes must be corrected
- state-month policy linkage must be validated
- the exposure definition must be credible

Current status:

- plausible later
- premature now

### 3. Policy targeting / prioritization

Meaning here:

- recommend who should receive limited outreach or renewal-support resources first

What must be true first:

- reliable risk scores
- a validated policy-exposure layer
- a clearly defined objective function or resource constraint
- a defendable outcome loss function

Current status:

- not yet supportable

Bottom line:

- the first plausible ML layer is `risk prediction`
- `heterogeneous harm` is a later stage
- `policy targeting` remains downstream of both corrected variables and validated state-month linkage

## 10. Current Bottom Line

### 1. Is SIPP still the strongest current public-data candidate for the churn / unwinding line?

Yes, with an important qualification.

It remains the strongest current candidate at the **structure level** because it offers:

- person-month microdata
- public-use state information
- repeated coverage information
- overlap across multiple panels

But that does **not** mean the current health-insurance layer is ready for final modeling.

### 2. What can already be said with confidence?

- the currently staged SIPP acquisition is complete enough for a serious audit
- the `2024` release is structurally coherent and useful as a template year
- `2024 SIPP` is a `2024` collection / release label with most content referring to `reference year 2023`
- `TEHC_ST` is the best current candidate for state-month linkage
- official Census user notes make clear that raw `2018-2023` monthly health-insurance fields are not safe to use naively
- annual recodes begin in `2022`
- `_SCRNR` variables are not a defensible cross-year annual-coverage solution

### 3. What still blocks a defendable prototype?

- an exact corrected-variable rule set for `2018-2023`
- a final decision on whether the first prototype is `2024` release only or a corrected multi-year stack
- a frozen monthly concept map for:
  - insured
  - public coverage
  - pure Medicaid
  - uninsured
  - "other coverage"
- validated state-month linkage to external unwinding policy data
- locally staged `FINYR2` / `FINYR3` or replicate weights if those designs are later chosen

### 4. Immediate next audit tasks

The next tasks should be:

1. write the exact year-specific correction rules for the `2018-2023` monthly health-insurance family
2. freeze one prototype variable map using `2024` as the template year
3. decide whether the first defensible prototype is:
   - `2024` release only
   - or corrected `2018-2024`
4. stage missing weight files only if the design still requires them
5. run one test state-month merge using `TEHC_ST` and the external unwinding data

Current decision-quality verdict:

- `SIPP` is still the best current public-use base
- `2024` is usable as a template year
- a final churn / unwinding model is **not yet defendable**
- the project should stay in audit / variable-definition mode before moving to estimation

## References

Official Census sources:

- SIPP datasets page: <https://www.census.gov/programs-surveys/sipp/data/datasets.html>
- 2024 SIPP Users Guide: <https://www2.census.gov/programs-surveys/sipp/tech-documentation/methodology/2024_SIPP_Users_Guide.pdf>
- 2024 Source and Accuracy Statement: <https://www2.census.gov/programs-surveys/sipp/tech-documentation/source-accuracy-statements/2024/SIPP-2024-SA.pdf>
- 2018 user notes page: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2018-usernotes.html>
- 2019 user notes page: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2019-usernotes.html>
- 2020 user notes page: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2020-usernotes.html>
- 2021 user notes page: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2021-usernotes.html>
- 2022 user notes page: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes.html>
- 2023 user notes page: <https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2023-usernotes.html>

Local supporting files:

- [2024_sipp_users_guide.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_users_guide.pdf)
- [2024_sipp_data_dictionary.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_data_dictionary.pdf)
- [2024_sipp_release_notes.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_release_notes.pdf)
- [2024_schema.json](../../reference/external/feasibility_audit/sipp/2024_schema.json)
- [2022_monthly_hi_variables_error.html](../../reference/external/feasibility_audit/sipp/2022_monthly_hi_variables_error.html)
- [sipp_2024_deep_audit_2026-04-10.md](sipp_2024_deep_audit_2026-04-10.md)
- [sipp_warning_registry.csv](sipp_warning_registry.csv)
- [sipp_core_variable_stability.csv](sipp_core_variable_stability.csv)
- [sipp_variable_triage.csv](sipp_variable_triage.csv)
