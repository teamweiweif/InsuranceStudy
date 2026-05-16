# CMS Updated Renewal Outcomes Audit Summary

Last updated: `2026-05-16T05:26:59.582105+00:00`

## Source Download

- Official CMS CSV successfully downloaded: `yes`.
- Raw CSV: `data_raw/cms/updated-renewal-outcomes-october-2024-releasefinal.csv`.
- Data.gov metadata text saved: `data_raw/cms/medicaid-and-chip-updated-renewal-outcomes_data_gov_metadata.txt`.
- CMS definitions PDF and CMS monthly reports page were verified via official web access, but local curl downloads from this environment closed without usable files; this is logged in `output/cms_audit/source_log.csv`.

## Reporting Months Available

- Raw CSV reporting periods: `202303` through `202403`.
- Main 2023 analytic file keeps: `202303, 202304, 202305, 202306, 202307, 202308, 202309, 202310, 202311, 202312`.
- Optional broader file through March 2024: `data_clean/cms/cms_updated_renewal_outcomes_state_month_2023_2024_optional.csv`.

## States Per Month

- `3`: `51` states
- `4`: `51` states
- `5`: `51` states
- `6`: `51` states
- `7`: `51` states
- `8`: `51` states
- `9`: `51` states
- `10`: `51` states
- `11`: `51` states
- `12`: `51` states

The raw file includes `US`; the state-month analytic and merge-ready files exclude it.

## Accounting Identities

- Rows with `abs(metric5_identity_gap_rate) > 0.01`: `0` of `510`.
- Rows with `abs(metric5a_identity_gap_rate) > 0.01`: `0` of `510`.
- Verdict: Metric 5 accounting identities are mostly valid; in this March-December 2023 state-month file they pass the 1% screen in all rows.

## Rate Validation

- Non-index treatment rates outside `[0, 1]`: `0`.
- Missing values exist where denominators are zero or missing; see `cms_treatment_rate_validation.csv`.
- `burden_index_simple` is a standardized index, so values outside `[0, 1]` are expected and are not rate errors.

## Main Treatment Usability

`procedural_burden_due = procedural_terminations / renewals_due` is the most usable main administrative-burden treatment. It directly captures procedural or administrative terminations among beneficiaries due for renewal.

Useful complementary measures:

- `ex_parte_rate_due`: administrative capacity / low-burden renewal channel.
- `pending_rate_due`: backlog or incomplete-processing pressure.
- `form_rate_due`: reliance on returned renewal forms.
- `burden_index_simple`: combined high-burden index using procedural burden, pending pressure, form reliance, and low ex parte renewal.

## State-Month Variation

Procedural burden and ex parte renewal rates are sufficiently variable across state-months for descriptive and later design diagnostics.

- Widest procedural-burden p90-p10 spread occurs in month `9` with spread `0.348`.
- Widest ex parte p90-p10 spread occurs in month `12` with spread `0.552`.

## SIPP Timing

Use both timing variables in the first SIPP merge:

- `sipp_month_same`: contemporaneous exposure.
- `sipp_month_plus1`: one-month-lagged effect month.

Given CMS reports renewals by the month due and survey coverage loss may appear in the same or following month, use plus-one exposure as the conservative main timing for loss-of-coverage outcomes and keep same-month exposure as a planned comparison. This is a design choice, not an effect estimate.

## Data Problems Before SIPP Merge

- Some state-month rates are missing because denominators are zero or missing; max missing count across non-index rates is 97 of 510 rows.
- Metric 5 and Metric 5a accounting identities pass the 1% gap screen for all March-December 2023 state-month rows.
- The raw CSV includes a `US` aggregate row; it was excluded from state-month and SIPP merge-ready files.
- Timing remains a design choice: the merge-ready file includes same-month and plus-one-month SIPP exposure keys.

## Output Files

- Main clean 2023 file: `data_clean/cms/cms_updated_renewal_outcomes_state_month_2023.csv`
- Optional 2023-2024 file: `data_clean/cms/cms_updated_renewal_outcomes_state_month_2023_2024_optional.csv`
- Merge-ready file: `data_clean/cms/cms_sipp_merge_ready_state_month_2023.csv`
- Column mapping: `output/cms_audit/cms_column_mapping.csv`
- Accounting validation: `output/cms_audit/cms_accounting_validation.csv`
- Rate validation: `output/cms_audit/cms_treatment_rate_validation.csv`
- National monthly summary: `output/cms_audit/cms_monthly_national_summary_2023.csv`
- State-month treatment distribution: `output/cms_audit/cms_state_month_treatment_distribution_2023.csv`
- Top high-burden state-months: `output/cms_audit/cms_top_high_burden_state_months_2023.csv`

## Interpretation Guardrail

This task only prepares and validates CMS treatment data. It does not estimate or claim causal effects.
