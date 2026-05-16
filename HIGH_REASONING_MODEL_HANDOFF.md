# Handoff for High-Reasoning Model

Repository target: `teamweiweif/InsuranceStudy`

This workspace contains SIPP 2023 Medicaid coverage diagnostics, CMS Medicaid/CHIP unwinding renewal treatment data, and a first-pass official policy-text archive / policy matrix.

## Current Scope

Do not treat this as a causal-effects package yet. No SIPP-CMS merge and no regressions have been run for the policy-text layer.

The current policy archive is a first-pass, federal-heavy official-source layer. It uses CMS / Medicaid.gov sources successfully, but the automated state official-source crawl did not retrieve usable state agency documents. State-specific policy features in the matrix therefore currently rely mainly on federal CMS structured sources.

## Key Files to Inspect First

1. `output/policy_evidence_books/policy_text_archive_summary.md`
   - Main audit summary for the policy-text archive.
   - Explains source hierarchy, extracted events, matrix coverage, and research-use recommendations.

2. `data_clean/policy_matrix/policy_events_official.csv`
   - One row per official policy event extracted.
   - Currently includes 51 E14 waiver state events and 15 delay procedural disenrollment events.

3. `data_clean/policy_matrix/state_month_policy_matrix_official.csv`
   - State-month policy matrix for 2023-03 through 2024-06.
   - 51 states/DC x 16 months = 816 rows.
   - Includes E14 features, delay/pause features, documentation coverage, and lag1/lag2 variants.

4. `data_clean/policy_matrix/state_month_policy_source_bridge.csv`
   - Long-format traceability bridge from state-month features back to event/source/evidence text.

5. `output/policy_audit/delay_procedural_disenrollment_validation.csv`
   - Validates extracted delay states against CMS-reported total of 15.

6. `output/policy_audit/e14_extraction_validation.csv`
   - Validates first-pass E14 extraction against the embedded CMS structured table.

7. `output/policy_audit/state_source_coverage_dashboard.csv`
   - Shows that direct official state-source coverage is currently missing and should be improved.

8. `output/cms_audit/cms_unwinding_data_audit_summary.md`
   - Audit summary for CMS updated renewal outcomes treatment data.

9. `data_clean/cms/cms_sipp_merge_ready_state_month_2023.csv`
   - Merge-ready CMS state-month treatment file for March-December 2023.

10. `sipp_2023_monthly_insurance_dynamics.csv`
    - SIPP full-year monthly coverage and transition diagnostics.

## Main Results So Far

- Federal source records logged: 21.
- Policy events extracted: 66.
- State-month policy rows: 816.
- E14 state events: 51.
- Delay procedural disenrollment events: 15.
- Official state agency documents downloaded in first pass: 0.

The most credible ex ante policy indicators in the current matrix are:

- `delay_procedural_disenrollment_any`
- `delay_procedural_disenrollment_months`
- `delay_procedural_disenrollment_all_beneficiaries`
- `delay_procedural_disenrollment_MAGI`
- `delay_procedural_disenrollment_nonMAGI`

E14 variables are useful as documented state-level policy-capacity or policy-tool indicators, but should not be interpreted as exact implementation-month treatment variables without additional state-source verification.

## Important Caveats

- Do not infer state-month implementation from posted dates.
- Do not claim causal effects.
- Do not treat missing state-source coverage as evidence that a state had no policy.
- The E14 counts are first-pass structured extraction from official CMS evidence, but precise state-month activation dates remain ambiguous.
- The next improvement should be a targeted state official-source crawl using known Medicaid/HHS agency domains, especially for TX, UT, ID, NC, OR, CA, NY, FL, GA, and PA.

## Suggested Next Query

Ask the high-reasoning model to audit and improve the official state-source layer before any regression work.

