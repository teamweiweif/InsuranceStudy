# Iteration Notes

Created: 2026-07-07

## Phase 0: Skill and Workspace Setup

Workspace directories were created. Relevant installed empirical, AER identification, robustness, replication, causal-inference, and economics-writing skills were discovered and read. The design is constrained by a national reform with no pure untreated group, so the empirical strategy must compare exposure intensity based only on pre-2022 facility characteristics.

Next phase check: Is the policy exposure correctly defined? The next step must verify January 2022 transparency posting and July 2022 Five-Star methodology inclusion from official CMS materials and avoid treating the 2024 minimum staffing rule as the main shock.

## Phase 1: Source and Policy Audit

CMS QSO-22-08-NH and CMS's July 27, 2022 fact sheet confirm the two policy shocks: January 2022 public posting of weekend staffing and turnover measures and July 27, 2022 incorporation into Five-Star staffing-domain methodology. PBJ daily nurse staffing is available quarterly through 2025 Q4 in the CMS data catalog. Provider Data Catalog nursing-home archive snapshots are available back to 2019 and were selected quarterly to support rating and facility-characteristic outcomes.

Self-question: The policy exposure is correctly defined as the 2022 transparency/rating sequence. The 2024 minimum staffing rule remains later context, not the main exposure.

## Phase 2: Raw Data Acquisition and Schema Audit

The data cover 2019 Q1 through 2025 Q4 for PBJ daily staffing. Provider Data Catalog snapshots were cached quarterly from 2019 through 2025, with the July 27, 2022 release included. Facility identifiers are normalized consistently across PBJ and Provider Data Catalog files.

Self-question: The data cover a long pre-period and post-period. PBJ Q1 2020 remains COVID-disrupted and should be excluded in a robustness check rather than silently dropped from all analyses.

## Phase 3: Analysis-Ready Panel Construction

Facility-month and facility-quarter panels were built from PBJ daily staffing. Exposures use only 2019-2021 PBJ staffing and are merged back to post-2022 outcomes. Provider archive characteristics are attached for baseline balance and heterogeneity when available.

Self-question: Identifiers are stable enough for a facility-level panel after normalizing CMS Certification Numbers to six characters. Facility exits remain in the unbalanced panel; robustness checks must test whether results change in a balanced or active-facility sample.

## Phase 4: Outcome Construction

Primary outcomes are policy-proximal staffing measures from PBJ daily records: weekend total nurse HPRD, weekend RN HPRD, weekday counterparts, weekend-weekday gaps, total HPRD, RN share, and contract share. Provider Data Catalog ratings and deficiencies are retained as secondary downstream outcomes.

Self-question: Outcomes are valid for staffing behavior and ratings. Facility-level deficiencies are downstream quality signals, not resident-level health outcomes.

## Phase 5: Exposure and Comparison Construction

The preferred comparison is high exposure versus lower exposure, where high exposure is the top quartile of the pre-2022 composite index. Balance and raw trend diagnostics were exported before model estimation. The comparison group remains exposed to the national policy and is not described as untreated.

Self-question: The most credible construction depends on pre-trends. Main models will test dynamic pre-policy coefficients and robustness will compare alternative exposure definitions.

## Phase 6: Main Models

Main panel and event-study models were estimated using high pre-policy exposure interacted with January-June 2022 and post-July 2022 indicators, plus dynamic event-time interactions around January 2022. Standard errors are clustered by facility. Lowest pre-trend p-value is 0.0000 for weekend_total_nurse_hprd.

Self-question: Causal interpretation depends on acceptable pre-trends. The final go/no-go judgment must treat small or systematic pre-period event coefficients as a design weakness.

## Phase 7: Robustness and Falsification

Robustness checks test whether the preferred result is driven by exposure construction, the COVID-disrupted 2020 period, unbalanced facility panels, time aggregation, ownership composition, or fake pre-policy timing.

Self-question: A result should be described as credible only if it has the same sign and similar magnitude across substantively reasonable exposure definitions and does not appear under placebo timing.

## Phase 8: Final Interpretation and Report

The report uses economics-writing guidance: lead with the empirical judgment, state the exact exposure and comparison, report concrete coefficients, and separate limitations from claims. Final judgment: Weak causal design under current specification. At least one primary staffing outcome rejects the joint pre-trend null at the 5% level. At least one primary post-July staffing estimate excludes zero. A placebo 2021 timing test is statistically significant, which weakens causal interpretation.

Self-question: Claims are limited to staffing behavior and administrative downstream measures. The report does not claim resident-level health effects.

## Phase 2: Raw Data Acquisition and Schema Audit

The data cover 2019 Q1 through 2025 Q4 for PBJ daily staffing. Provider Data Catalog snapshots were cached quarterly from 2019 through 2025, with the July 27, 2022 release included. Facility identifiers are normalized consistently across PBJ and Provider Data Catalog files.

Self-question: The data cover a long pre-period and post-period. PBJ Q1 2020 remains COVID-disrupted and should be excluded in a robustness check rather than silently dropped from all analyses.

## Phase 3: Analysis-Ready Panel Construction

Facility-month and facility-quarter panels were built from PBJ daily staffing. Exposures use only 2019-2021 PBJ staffing and are merged back to post-2022 outcomes. Provider archive characteristics are attached for baseline balance and heterogeneity when available.

Self-question: Identifiers are stable enough for a facility-level panel after normalizing CMS Certification Numbers to six characters. Facility exits remain in the unbalanced panel; robustness checks must test whether results change in a balanced or active-facility sample.

## Phase 4: Outcome Construction

Primary outcomes are policy-proximal staffing measures from PBJ daily records: weekend total nurse HPRD, weekend RN HPRD, weekday counterparts, weekend-weekday gaps, total HPRD, RN share, and contract share. Provider Data Catalog ratings and deficiencies are retained as secondary downstream outcomes.

Self-question: Outcomes are valid for staffing behavior and ratings. Facility-level deficiencies are downstream quality signals, not resident-level health outcomes.

## Phase 8: Final Interpretation and Report

The report uses economics-writing guidance: lead with the empirical judgment, state the exact exposure and comparison, report concrete coefficients, and separate limitations from claims. Final judgment: Weak causal design under current specification. At least one primary staffing outcome rejects the joint pre-trend null at the 5% level. At least one primary post-July staffing estimate excludes zero. A placebo 2021 timing test is statistically significant, which weakens causal interpretation.

Self-question: Claims are limited to staffing behavior and administrative downstream measures. The report does not claim resident-level health effects.

## Phase 5: Exposure and Comparison Construction

The preferred comparison is high exposure versus lower exposure, where high exposure is the top quartile of the pre-2022 composite index. Balance and raw trend diagnostics were exported before model estimation. The comparison group remains exposed to the national policy and is not described as untreated.

Self-question: The most credible construction depends on pre-trends. Main models will test dynamic pre-policy coefficients and robustness will compare alternative exposure definitions.
