# Crosswalk Default Mapping Reconciliation Report

## 1. Executive Diagnosis

Premium variants did not close the Drake treatment gap, so this audit tests Plan ID Crosswalk default-row selection. The current repo rule remains a plausible but not fully confirmed implementation. No tested default mapping rule simultaneously reproduces Drake's 4452 any-turnover county-years and 211 across-insurer county-years with text support. Step 4 remains **No-Go**.

Key diagnostic result: among prior top-two silver plan pairs, the raw candidate audit found 15030 joined candidate rows across 15030 plan-pair groups, with 0 groups having more than one raw candidate row. In this constructed public-file sample, duplicate/default-row choice does not move the treatment counts.

## 2. What Drake Says About Default Mapping

Drake states that prior-year top-two silver plans default through the Plan ID Crosswalk: if the same plan is available it defaults to itself; otherwise a similar plan becomes the new default. Drake does not disclose duplicate-row resolution, ZIP-to-county aggregation, ReasonForCrosswalk priority, or CrosswalkLevel 4/5 handling.

## 3. What CMS Plan ID Crosswalk Documentation Says

CMS defines FIPSCode, ZipCode, CrosswalkLevel, and ReasonForCrosswalk in the Plan ID Crosswalk Data Dictionary. `ZipCode = 00000` means the county was not split into ZIP rows. CrosswalkLevel 0-3 identify same-plan, plan-level, county-coverage, and ZIP-level mappings; levels 4 and 5 indicate no reenrollment/default option. ReasonForCrosswalk = 8 is a CMS-determined crosswalk to a different issuer.

## 4. Current Repo Default Mapping Rule

The current repo selects one row per state/county/prior plan after filtering to nondental prior silver rows. It prioritizes mapped current plans, current silver metal, same issuer, lowest CrosswalkLevel, then current plan/issuer IDs.

## 5. Same-Issuer Priority

Same-issuer priority can suppress across-insurer rows when a same-issuer and across-issuer candidate coexist. The diagnostic variants remove this priority and directly measure whether across-insurer counts increase.

In the current joined prior-top-two universe, no plan-pair group has multiple raw candidates, so removing same-issuer priority does not change any Drake-harmonized treatment count.

## 6. ZIP-Level Versus County-Level Aggregation

`county_any_zip_turnover` and `county_any_zip_across_turnover` test whether any ZIP-level candidate is enough to classify a county-year. These are diagnostic only because Drake does not say that ZIP-level candidate existence alone defines county-year treatment.

In this audit, ZIP-level and any-ZIP diagnostic rules do not change the pooled Drake-harmonized counts. The across-insurer gap is therefore not explained by county aggregation of alternative ZIP-level candidate rows.

## 7. Default Mapping Variant Comparison

| default_mapping_rule | premium_variant | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | drake_text_support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| county_any_zip_across_turnover | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | diagnostic_only |
| county_any_zip_turnover | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | diagnostic_only |
| current_repo_rule | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | plausible |
| exclude_level4_5 | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | plausible |
| include_level4_5_as_missing_current | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | diagnostic_only |
| lowest_crosswalk_level | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | diagnostic_only |
| no_same_issuer_priority | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | diagnostic_only |
| reason8_priority | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | diagnostic_only |
| same_plan_if_available_else_lowest_level | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | plausible |
| same_plan_if_available_else_source_order | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | plausible |
| source_order_first_valid | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | diagnostic_only |
| whole_county_00000_only | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | diagnostic_only |
| county_any_zip_across_turnover | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| county_any_zip_turnover | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| current_repo_rule | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| exclude_level4_5 | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| include_level4_5_as_missing_current | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| lowest_crosswalk_level | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| no_same_issuer_priority | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| reason8_priority | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| same_plan_if_available_else_lowest_level | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| same_plan_if_available_else_source_order | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| source_order_first_valid | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| whole_county_00000_only | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |

Closest plausible/text-supported rows:

| default_mapping_rule | premium_variant | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | drake_text_support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current_repo_rule | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| exclude_level4_5 | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| same_plan_if_available_else_source_order | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| same_plan_if_available_else_lowest_level | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| exclude_level4_5 | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | plausible |
| current_repo_rule | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | plausible |
| same_plan_if_available_else_lowest_level | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | plausible |
| same_plan_if_available_else_source_order | current_ehb_all_states | 4188 | 107 | 28.065 | 0.524 | -264 | -104 | plausible |

Closest numeric rows, including diagnostic-only rules:

| default_mapping_rule | premium_variant | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | drake_text_support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| county_any_zip_across_turnover | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| county_any_zip_turnover | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| exclude_level4_5 | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| current_repo_rule | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | plausible |
| no_same_issuer_priority | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| reason8_priority | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| lowest_crosswalk_level | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |
| include_level4_5_as_missing_current | ehb_named_states_only | 4344 | 123 | 29.269 | 1.193 | -108 | -88 | diagnostic_only |

## 8. Across-Insurer Gap Diagnosis

The across-gap file reports, by state-year and rule, whether raw across candidates exist but are not selected, whether Reason 8 candidates exist, and whether ZIP-level candidates could explain the gap. In this run, none of the default-row rules changes the pooled across-insurer count. That means the remaining across-insurer mismatch is not fixed by same-issuer priority, Reason 8 priority, CrosswalkLevel priority, or ZIP-level candidate aggregation in the joined public-file Crosswalk rows.

## 9. Kansas 2022 Conclusion

| default_mapping_rule | ks_counties_with_across |
| --- | --- |
| current_repo_rule | 87 |
| no_same_issuer_priority | 87 |
| source_order_first_valid | 87 |
| lowest_crosswalk_level | 87 |
| same_plan_if_available_else_source_order | 87 |
| same_plan_if_available_else_lowest_level | 87 |
| whole_county_00000_only | 87 |
| county_any_zip_turnover | 87 |
| county_any_zip_across_turnover | 87 |
| reason8_priority | 87 |
| exclude_level4_5 | 87 |
| include_level4_5_as_missing_current | 87 |

Kansas 2022 is not primarily a premium-calculation artifact. This audit checks whether it persists under source-order, lowest-level, same-plan, ZIP, and Reason 8 rules. A rule that removes Kansas solely by diagnostic priority is not automatically more faithful.

## 10. Whether Any Rule Matches Drake Anchors

No tested text-supported rule exactly matches both Drake anchors. No diagnostic-only default-row rule moves the pooled Drake-harmonized anchors either. The crosswalk default-row rule does not appear to be the main remaining source of the treatment mismatch in the current public-file construction.

## 11. Recommended Rule Going Forward

Keep `current_repo_rule` as the baseline until a more exact Drake rule is documented. Treat same-plan-if-available variants as plausible sensitivities and any-ZIP/Reason 8 variants as diagnostics.

## 12. Step 4 Recommendation

**No-Go for Step 4.** The project should continue Step 2 treatment repair until the crosswalk/default-row rule is either reproduced from Drake's implementation or the remaining mismatch is explicitly bounded and justified.
