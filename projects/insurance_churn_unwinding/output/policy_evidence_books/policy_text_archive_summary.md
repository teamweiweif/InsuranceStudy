# Policy Text Archive Summary

Last updated: `2026-05-16T10:50:46.217653+00:00`

## Executive Summary

- Federal official source records archived or logged: `21`.
- Federal local files with usable bytes: `12`.
- Official state candidate documents downloaded in first-pass search: `0`.
- Policy events extracted: `66`.
- State-month policy rows: `816`.
- States with at least one official state source downloaded: `0`.
- States relying only on federal source tables in this first pass: `51`.

This first-pass archive emphasizes official CMS federal tables and guidance. State-source discovery is automated and conservative; missing state sources are marked as missing rather than filled from secondary sources.

## Source Hierarchy

1. Federal CMS tables and guidance: E14 waiver approvals and state option to delay procedural disenrollments are the highest-grade structured sources in this pass.
2. State official agency pages: downloaded only when an official `.gov` state source was found and verified by URL/domain.
3. State PDFs/plans/FAQs: parsed if downloaded, but implementation dates are not inferred from posting dates.
4. Secondary sources: not used for primary coding in this pass.

## Key Policy Features

- `e14_*`: CMS Section 1902(e)(14)(A) strategy-count features. These are documented strategy counts, not precise month-specific implementation dates.
- `delay_procedural_disenrollment_*`: CMS state option with renewal due month ranges. These are the strongest month-coded policy features in this pass.
- `official_*` outreach/form/contact/reinstatement features: mostly zero in the current matrix unless backed by structured federal categories; state-document extraction needs manual review before main use.
- `cms_mitigation_strategy_active`: active for state-months covered by the CMS delay option.

## State Examples

- **TX (Texas)**: E14 total=11, ex parte=1, form support=5, contact update=1, reinstatement=1. CMS delay option: 1 month, 2023-10 to 2023-10, population=All beneficiaries.
- **UT (Utah)**: E14 total=10, ex parte=1, form support=5, contact update=0, reinstatement=1. No CMS delay option extracted.
- **ID (Idaho)**: E14 total=10, ex parte=1, form support=5, contact update=0, reinstatement=1. No CMS delay option extracted.
- **NC (North Carolina)**: E14 total=12, ex parte=2, form support=5, contact update=1, reinstatement=1. CMS delay option: Through the end of unwinding, 2023-09 to end_of_unwinding_unspecified, population=All beneficiaries.
- **OR (Oregon)**: E14 total=13, ex parte=2, form support=6, contact update=1, reinstatement=1. No CMS delay option extracted.
- **CA (California)**: E14 total=17, ex parte=3, form support=7, contact update=1, reinstatement=3. No CMS delay option extracted.
- **NY (New York)**: E14 total=15, ex parte=3, form support=6, contact update=1, reinstatement=2. CMS delay option: Through the end of unwinding, 2023-09 to end_of_unwinding_unspecified, population=MAGI beneficiaries.
- **FL (Florida)**: E14 total=11, ex parte=1, form support=5, contact update=1, reinstatement=1. No CMS delay option extracted.
- **GA (Georgia)**: E14 total=12, ex parte=1, form support=6, contact update=1, reinstatement=1. No CMS delay option extracted.
- **PA (Pennsylvania)**: E14 total=14, ex parte=2, form support=6, contact update=1, reinstatement=2. CMS delay option: 1 month, 2023-04 to 2023-04, population=Non-MAGI beneficiaries.

## Research-Use Recommendation

- Credible as ex ante policy indicators now: `delay_procedural_disenrollment_any`, population-specific delay flags, and E14 strategy counts as documented state-level policy capacity indicators.
- Documentation/evidence variables: `n_official_sources_supporting_state_month`, `has_direct_state_source`, `highest_source_grade`, and bridge-file source IDs.
- Auxiliary controls: E14 strategy count groups, especially ex parte, form support, contact update, and reinstatement counts.
- Too ambiguous for main treatment without manual review: exact E14 implementation month, state renewal start dates from generic FAQ pages, and any state page where only a posted date is available.
- Ready to merge with CMS/SIPP for exploratory diagnostics: the state-month matrix and bridge file, with the caveat that E14 timing is documented but not month-specific.

## Validation Summary

- E14 count validation file: `output/policy_audit/e14_extraction_validation.csv`.
- Delay procedural disenrollment validation: extracted `15` states; expected `15`.
- Ambiguities are saved in `output/policy_audit/policy_extraction_ambiguities.csv`.

## Guardrail

This archive does not estimate or claim causal effects. It creates an official policy-document layer for later design diagnostics, mechanism evidence, auxiliary controls, ML features, and validation against CMS realized renewal metrics.
