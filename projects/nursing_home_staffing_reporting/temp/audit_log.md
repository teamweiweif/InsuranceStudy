# Audit Log

Created: 2026-07-07

## Initial Decisions

- Created project workspace under `nursing_home_staffing_reporting/`.
- Raw files and source snapshots will be stored only under `temp/raw_downloads/`.
- Clean analysis-ready outputs will be stored only under `data/`.
- The main empirical design compares higher-exposure and lower-exposure facilities within the same national 2022 CMS transparency/rating reform; lower-exposure facilities will not be called untreated.
- The 2024 federal minimum staffing rule is treated as later policy context, not the main exposure.

## Open Audit Items

- Verify CMS policy dates and exact language from official CMS sources.
- Verify latest available CMS data coverage and API dataset identifiers from official CMS endpoints.
- Document any unavailable or computationally infeasible source, especially PBJ Employee Detail.

## Phase 1 Source Acquisition

- Access date: 2026-07-07.
- Recorded 28 PBJ daily nurse staffing quarterly CSV URLs for 2019-2025.
- Recorded 23 PBJ employee-detail quarterly CSV URLs. Full employee-detail processing is deferred unless feasible because the files are much larger than the daily aggregate files.
- Downloaded or verified 26 Provider Data Catalog nursing-home archive ZIP snapshots.
- Downloaded official CMS policy and HHS OIG source snapshots for the policy timeline.

## Phase 2 Raw Data and Schema Audit

- PBJ daily nurse staffing aggregated to 1,227,294 facility-month rows and 409,098 facility-quarter rows.
- Provider archive snapshots parsed to 286,424 provider rows, 853,548 survey-summary rows, and 284,279 facility-snapshot health-citation summaries.
- PBJ facility identifier is `PROVNUM`, normalized to six-character `facility_id`.
- Provider Data Catalog facility identifier is Federal Provider Number / CMS Certification Number, normalized to the same six-character `facility_id`.

## Phase 3 Panel and Exposure Construction

- Constructed baseline exposures for 15,608 facilities with any 2019-2021 PBJ data.
- Preferred analysis month sample has 1,209,911 facility-month observations.
- Main high-exposure indicator is the top quartile of a pre-2022 composite of low weekend total staffing, low weekend RN staffing, and high weekday-weekend staffing gap.

## Phase 4 Descriptive Diagnostics

- Wrote balance, coverage, missingness, exposure distribution, and raw trend diagnostics to `result\tables` and `result\figures`.
- Analysis sample for descriptive diagnostics contains 15,133 facilities and 1,209,911 facility-month observations.

## Phase 6 Main Models

- Estimated main facility-month panel models for 8 outcomes with facility and month fixed effects, plus a specification with facility and state-by-month fixed effects.
- Estimated January 2022 event-study models with facility and month fixed effects and facility-clustered standard errors.
- Wrote main model results to `result\main_model_results.csv` and event-study coefficients to `result\main_eventstudy_coefficients.csv`.

## Phase 7 Robustness and Falsification

- Ran alternative exposure definitions, 2021-only and no-2020 baselines, COVID-period exclusion, balanced-panel restriction, facility-quarter panel, ownership subsamples, and 2021 placebo timing tests.
- Wrote robustness results to `result\robustness_results.csv`.

## Phase 2 Raw Data and Schema Audit

- PBJ daily nurse staffing aggregated to 1,227,294 facility-month rows and 409,098 facility-quarter rows.
- Provider archive snapshots parsed to 394,880 provider rows, 1,176,574 survey-summary rows, and 284,286 facility-snapshot health-citation summaries.
- PBJ facility identifier is `PROVNUM`, normalized to six-character `facility_id`.
- Provider Data Catalog facility identifier is Federal Provider Number / CMS Certification Number, normalized to the same six-character `facility_id`.

## Phase 3 Panel and Exposure Construction

- Constructed baseline exposures for 15,608 facilities with any 2019-2021 PBJ data.
- Preferred analysis month sample has 1,209,911 facility-month observations.
- Main high-exposure indicator is the top quartile of a pre-2022 composite of low weekend total staffing, low weekend RN staffing, and high weekday-weekend staffing gap.

## Phase 4 Descriptive Diagnostics

- Wrote balance, coverage, missingness, exposure distribution, and raw trend diagnostics to `result\tables` and `result\figures`.
- Analysis sample for descriptive diagnostics contains 15,133 facilities and 1,209,911 facility-month observations.
