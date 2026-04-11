# 2024 SIPP Deep Audit

Last updated: `2026-04-10`

## Scope

This audit focuses on `2024 SIPP` only.

It does **not** yet audit:

- cross-year harmonization beyond a first structural check
- 2018-2023 correction implementation
- outcome modeling
- machine learning

The purpose is narrower:

- determine whether `2024 SIPP` is a usable template year for churn / unwinding work

Important clarification:

- `2024 SIPP` is the `2024` release / collection-year label
- most reference-year content in this release is for `January-December 2023`
- this note therefore treats `2024 SIPP` as the `2024` release, not as a literal `CY2024` reference-year file

## Files Used

Primary local data:

- [pu2024_csv.zip](../../data/raw/feasibility_audit/sipp/2024/pu2024_csv.zip)
- [lgtwgt2024yr4_csv.zip](../../data/raw/feasibility_audit/sipp/2024/lgtwgt2024yr4_csv.zip)

Primary local documentation:

- [2024_sipp_users_guide.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_users_guide.pdf)
- [2024_sipp_data_dictionary.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_data_dictionary.pdf)
- [2024_schema.json](../../reference/external/feasibility_audit/sipp/2024_schema.json)

Generated audit outputs:

- [sipp_2024_core_profile.json](sipp_2024_core_profile.json)
- [sipp_2024_consistency_detail.json](sipp_2024_consistency_detail.json)
- [sipp_2024_panel_wave_counts.csv](sipp_2024_panel_wave_counts.csv)
- [sipp_2024_core_value_counts.csv](sipp_2024_core_value_counts.csv)
- [sipp_2024_public_assistance_mismatch_sample.csv](sipp_2024_public_assistance_mismatch_sample.csv)

## 1. High-Level Judgment

`2024 SIPP` is usable as a template year.

Why:

- the file is structurally coherent
- person-month keys are unique
- panel-wave composition matches official Census guidance
- core insurance, geography, and weight variables are present
- basic Medicaid spell checks do not show obvious internal contradictions

But:

- the file is a **collection-year overlapping-panel file**, not a single pure panel
- some weight values are zero, so analysis must follow official weighting rules carefully
- `RPUBTYPE2` is broader than `EMDMTH`, so those variables must not be treated as interchangeable

## 2. Structure And Keys

Observed local counts:

- rows: `437,168`
- unique persons: `36,915`
- duplicate `SSUID + PNUM + MONTHCODE` keys: `0`

This is a strong positive result.

It means the file behaves like a proper person-month panel-style file for within-year construction.

## 3. Panel-Wave Composition

Observed composition:

- `SPANEL=2021`, `SWAVE=4`: `67,567`
- `SPANEL=2022`, `SWAVE=3`: `139,584`
- `SPANEL=2023`, `SWAVE=2`: `90,973`
- `SPANEL=2024`, `SWAVE=1`: `139,044`

This exactly matches the overlapping-panel logic described in the official guide.

Interpretation:

- `2024 SIPP` should be treated as a **collection-year file composed of multiple panels**
- it is valid for within-year monthly analysis
- it is not valid to describe it as "the 2024 panel" without qualification

## 4. Weights

Observed `WPFINWGT` status:

- missing weights: `0`
- non-positive weights: `1,285`
- minimum: `0`
- maximum: `101,077.12454`
- mean: `9,065.72`

Month-specific zero-weight counts:

- month `1`: `194`
- month `2`: `187`
- month `3`: `165`
- month `4`: `140`
- month `5`: `124`
- month `6`: `116`
- month `7`: `100`
- month `8`: `79`
- month `9`: `62`
- month `10`: `52`
- month `11`: `38`
- month `12`: `28`

December check:

- unique persons with a month-12 row: `36,214`
- unique persons with positive month-12 weight: `36,186`

Interpretation:

- `WPFINWGT` is present and usable
- but zero-weight cases exist and cannot be ignored
- for calendar-year estimates, the official December-weight rule matters in practice

Current practical reading:

- if we later build a `2024` release prototype, we should use the **December-positive-weight cohort** as the cleanest reference-year estimation base

## 5. Geography

Observed `TEHC_ST`:

- no missing values
- top states by raw row count include `06`, `48`, `12`, `36`, `17`

Observed `TST_INTV`:

- missing values: `5,153`

Missing `TST_INTV` by `THHLDSTATUS`:

- status `3`: `1,650`
- status `4`: `2,931`
- status `5`: `112`
- status `6`: `460`

Observed nonstandard `TEHC_ST` codes:

- `60`: `22`
- `61`: `909`

This is not automatically a problem.

The official guide states that `TEHC_ST` can also identify world region for respondents who lived outside the United States during the reference year.

Interpretation:

- `TEHC_ST` is the stronger variable for month-level state linkage
- any state-policy linkage step should explicitly filter out non-state `TEHC_ST` codes such as `60` and `61`

## 6. Core Insurance Variables

Observed main monthly counts:

- `RHLTHMTH=1`: `399,457`
- `RHLTHMTH=2`: `37,711`

- `RPRIMTH=1`: `282,421`
- `RPUBMTH=1`: `195,241`
- `RPUBTYPE1=1` (Medicare-type public): `118,463`
- `RPUBTYPE2=1`: `93,823`
- `EMDMTH=1`: `88,716`

Two important findings:

### Finding A

`RPUBMTH` and `RHLTHMTH` are internally coherent on the simple check performed here.

Observed cross-tab:

- `RPUBMTH=1`, `RHLTHMTH=1`: `195,241`
- `RPUBMTH=2`, `RHLTHMTH=1`: `204,216`
- `RPUBMTH=2`, `RHLTHMTH=2`: `37,711`

No impossible `RPUBMTH=1` with `RHLTHMTH=2` case appeared in this audit.

### Finding B

`RPUBTYPE2` and `EMDMTH` are **not identical**.

Observed cross-tab:

- `RPUBTYPE2=1`, `EMDMTH=1`: `88,716`
- `RPUBTYPE2=1`, `EMDMTH=2`: `5,107`
- `RPUBTYPE2=2`, `EMDMTH=2`: `343,345`

This difference is explainable from the documentation plus the sampled rows.

In the Users Guide, `RPUBTYPE2` is described as:

- `Medicaid coverage or other government/public assistance coverage`

Sampled mismatch rows show:

- `RPUBTYPE2=1`
- `EMDMTH=2`
- `EOTMTH=1`

Interpretation:

- those `5,107` rows are not necessarily data corruption
- they appear to be cases where the broader recode is picking up `other government/public assistance` rather than edited Medicaid

Practical rule:

- do **not** substitute `RPUBTYPE2` for pure Medicaid
- if the target concept is strictly Medicaid / Medical Assistance, `EMDMTH` is the cleaner candidate
- if the target concept is broader public assistance coverage, `RPUBTYPE2` is the broader recode

## 7. Medicaid Spell Variables

Observed missingness:

- `EMD_BMONTH` missing: `348,452`
- `EMD_EMONTH` missing: `348,452`
- `RMD_CFLG` missing: `353,132`

This pattern is expected because the universe for these variables is narrower than "all person-month rows."

The more important result is the internal-consistency check.

In the checks performed here, there were **no** observed cases of:

- `EMDMTH=1` with missing spell bounds
- `EMDMTH!=1` with spell bounds still present
- `EMD_BMONTH > EMD_EMONTH`
- `EMD_BMONTH > MONTHCODE`
- `EMD_EMONTH < MONTHCODE`

Interpretation:

- on this basic within-year check, the `2024` Medicaid spell fields look internally coherent
- this is encouraging, especially because the official local error note currently targets `2018-2023`

## 8. THHLDSTATUS And Universe Caution

Observed `THHLDSTATUS` counts:

- `1`: `278,439`
- `2`: `153,576`
- `3`: `1,650`
- `4`: `2,931`
- `5`: `112`
- `6`: `460`

This matters because some variables have universes that effectively operate on subsets of household status.

Current implication:

- missingness in variables such as `TST_INTV` and `TMOVER` should not automatically be read as a data failure
- later modeling or descriptive work must apply universe-aware filtering rather than blanket complete-case rules

## 9. What 2024 Can Already Support

Based on this audit, `2024` is good enough to support a first prototype for:

- person-month coverage status
- public vs private coverage distinction
- pure Medicaid monthly indicator using `EMDMTH`
- uninsured month definition using `RHLTHMTH`
- month-level state linkage using `TEHC_ST`

It is also good enough to support a first-generation:

- churn-risk prototype
- state-linked descriptive prototype

It is **not** yet enough to justify:

- full multi-year stack
- multi-year longitudinal weighting
- causal ML
- targeting / policy learning

## 10. Immediate Recommendation

The next best step is now very specific:

1. treat `2024` as the template year
2. define one clean monthly Medicaid / uninsured / public-coverage variable set
3. write the exact rule for which variable is used for which concept
4. only then compare `2018-2023` against this template, especially where the official user-note correction matters

If you want the shortest version:

- `2024` passes the structural audit
- `2024` does **not** remove the need for a `2018-2023` correction audit
- `EMDMTH` and `RPUBTYPE2` should be treated as different concepts, not duplicates

## References

Official Census sources used in this audit:

- 2024 Users Guide: <https://www2.census.gov/programs-surveys/sipp/tech-documentation/methodology/2024_SIPP_Users_Guide.pdf>
- 2024 Source and Accuracy Statement: <https://www2.census.gov/programs-surveys/sipp/tech-documentation/source-accuracy-statements/2024/SIPP-2024-SA.pdf>

Local supporting files:

- [2024_sipp_users_guide.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_users_guide.pdf)
- [2024_sipp_data_dictionary.pdf](../../reference/external/feasibility_audit/sipp/2024_sipp_data_dictionary.pdf)
- [2024_schema.json](../../reference/external/feasibility_audit/sipp/2024_schema.json)
