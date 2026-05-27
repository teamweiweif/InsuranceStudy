# Top-Two Silver Reconciliation Report

## 1. Executive Diagnosis

The current repo top-two rule remains the most text-faithful public-file interpretation: rank prior-year county-level silver QHP Landscape plans by age-40 gross premium, then calculate zero/positive postsubsidy premiums for those selected plans. The new variants show that top-two selection can move the any-turnover count, especially with diagnostic net-premium ranking, but it does not close the across-insurer gap to Drake's 211 county-years. Step 4 remains **No-Go**.

## 2. What Drake Says

Drake says county-years are exposed when either or both prior-year lowest-premium and second-lowest-premium silver plans had zero-dollar premiums and defaulted to positive-premium plans. The premium/subsidy calculations use a representative 40-year-old enrollee at 125% FPL. Drake names QHP Landscape for plan offerings/premiums/benefits and Plan ID Crosswalk for defaults.

## 3. What Drake Does Not Say

Drake does not disclose duplicate-row handling, tie-breaking, PlanId versus StandardComponentId, whether top-two ranking itself uses gross or net premiums, county-rating-area handling, child-only filtering, or source-order behavior.

## 4. What CMS Documentation Implies

QHP Landscape medical individual files provide county-plan rows and example premiums including Adult Individual Age 40, and those premiums exclude tax credits. CMS Exchange PUFs provide Rate, Plan Attributes, Service Area, Benefits, and Crosswalk files. The Plan ID Crosswalk dictionary defines FIPS, ZIP, crosswalk levels, and reasons but does not define Drake's top-two ranking.

## 5. Current Repo Logic

The repo ranks cached silver QHP county-plan rows by `age_40_premium`, drops duplicate `plan_id` rows, and tie-breaks by `issuer_id` and `plan_id`. Direct PY2021 QHP Landscape is used when present. This is plausible and text-faithful, but not fully confirmed.

## 6. Whether Current Repo Appears Text-Faithful

Yes, for the ranking step. It is not exact because Drake did not publish tie, duplicate, or identifier rules.

## 7. Top-Two Variant Comparison

| selection_variant | exposure_universe | county_years_where_lowest_plan_differs_from_current_repo | county_years_where_second_lowest_plan_differs_from_current_repo | county_years_where_either_top_two_plan_differs | states_years_with_most_differences | number_of_differences_involving_ties | number_of_differences_involving_standard_component_collapse | number_of_differences_involving_rating_area_county_issues | number_of_differences_involving_child_only_limited_plans | number_of_differences_involving_missing_or_anomalous_premiums | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rank_by_displayed_qhp_order_if_available | exactly_two_plans | 6824 | 6492 | 7114 | 2023-TX:222; 2022-TX:222; 2021-TX:217; 2022-GA:159; 2021-GA:151; 2021-VA:133; 2022-VA:133; 2023-VA:133; 2023-GA:132; 2021-KY:120 | 0 | 0 | 0 | 0 | 0 | no_official_display_rank_field_used_cached_source_order |
| rank_by_displayed_qhp_order_if_available | include_ties_at_second_lowest | 6824 | 6492 | 7114 | 2023-TX:222; 2022-TX:222; 2021-TX:217; 2022-GA:159; 2021-GA:151; 2021-VA:133; 2022-VA:133; 2023-VA:133; 2023-GA:132; 2021-KY:120 | 0 | 0 | 0 | 0 | 0 | no_official_display_rank_field_used_cached_source_order |
| rank_by_postsubsidy_net_premium | include_ties_at_second_lowest | 6470 | 6180 | 6476 | 2023-TX:254; 2021-TX:253; 2022-TX:244; 2023-GA:159; 2022-GA:153; 2021-GA:147; 2021-VA:133; 2023-VA:129; 2022-VA:117; 2022-MO:115 | 6313 | 0 | 0 | 0 | 0 |  |
| rank_by_postsubsidy_net_premium | exactly_two_plans | 3702 | 3702 | 3702 | 2022-TX:183; 2021-TX:160; 2023-GA:113; 2023-MO:113; 2021-GA:108; 2021-KS:103; 2023-KS:91; 2023-TX:84; 2023-VA:82; 2021-MS:82 | 3539 | 0 | 0 | 0 | 0 |  |
| rank_by_ehb_adjusted_gross_premium | include_ties_at_second_lowest | 765 | 1732 | 1732 | 2021-TX:114; 2021-IN:92; 2022-GA:92; 2021-KS:85; 2022-KS:84; 2023-TN:81; 2021-KY:76; 2023-MS:64; 2021-OH:62; 2022-MS:58 | 132 | 0 | 0 | 0 | 0 |  |
| rank_by_ehb_adjusted_gross_premium | exactly_two_plans | 663 | 1619 | 1619 | 2021-TX:114; 2022-GA:92; 2021-IN:92; 2021-KS:85; 2023-TN:81; 2021-KY:76; 2023-MS:64; 2021-OH:62; 2022-MS:58; 2022-IN:57 | 0 | 0 | 0 | 0 | 0 |  |
| all_tied_lowest_or_second_lowest | include_ties_at_second_lowest | 121 | 134 | 134 | 2022-KS:84; 2023-AL:21; 2022-NE:16; 2023-OR:6; 2023-TX:5; 2021-LA:2 | 134 | 0 | 0 | 0 | 0 |  |
| county_rating_area_specific_top_two | include_ties_at_second_lowest | 121 | 134 | 134 | 2022-KS:84; 2023-AL:21; 2022-NE:16; 2023-OR:6; 2023-TX:5; 2021-LA:2 | 134 | 0 | 134 | 0 | 0 |  |
| exclude_child_only_or_limited_plans | include_ties_at_second_lowest | 121 | 134 | 134 | 2022-KS:84; 2023-AL:21; 2022-NE:16; 2023-OR:6; 2023-TX:5; 2021-LA:2 | 134 | 0 | 0 | 134 | 0 | child_or_limited_flags_not_available_in_cached_panel |
| rank_by_gross_age40_premium_planid | include_ties_at_second_lowest | 121 | 134 | 134 | 2022-KS:84; 2023-AL:21; 2022-NE:16; 2023-OR:6; 2023-TX:5; 2021-LA:2 | 134 | 0 | 0 | 0 | 0 |  |
| rank_by_gross_age40_standard_component | include_ties_at_second_lowest | 121 | 134 | 134 | 2022-KS:84; 2023-AL:21; 2022-NE:16; 2023-OR:6; 2023-TX:5; 2021-LA:2 | 134 | 134 | 0 | 0 | 0 |  |
| rank_by_rate_puf_premium | include_ties_at_second_lowest | 121 | 134 | 134 | 2022-KS:84; 2023-AL:21; 2022-NE:16; 2023-OR:6; 2023-TX:5; 2021-LA:2 | 134 | 0 | 0 | 0 | 0 |  |
| service_area_strict_top_two | include_ties_at_second_lowest | 121 | 134 | 134 | 2022-KS:84; 2023-AL:21; 2022-NE:16; 2023-OR:6; 2023-TX:5; 2021-LA:2 | 134 | 0 | 0 | 0 | 0 | qhp_county_rows_used_as_service_area_availability |
| tie_break_source_order | include_ties_at_second_lowest | 121 | 134 | 134 | 2022-KS:84; 2023-AL:21; 2022-NE:16; 2023-OR:6; 2023-TX:5; 2021-LA:2 | 134 | 0 | 0 | 0 | 0 |  |
| all_tied_lowest_or_second_lowest | exactly_two_plans | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 |  |
| county_rating_area_specific_top_two | exactly_two_plans | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 |  |
| current_repo_top_two | exactly_two_plans | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 |  |
| current_repo_top_two | include_ties_at_second_lowest | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 |  |
| exclude_child_only_or_limited_plans | exactly_two_plans | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 | child_or_limited_flags_not_available_in_cached_panel |
| rank_by_gross_age40_premium_planid | exactly_two_plans | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 |  |
| rank_by_gross_age40_standard_component | exactly_two_plans | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 |  |
| rank_by_rate_puf_premium | exactly_two_plans | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 |  |
| service_area_strict_top_two | exactly_two_plans | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 | qhp_county_rows_used_as_service_area_availability |
| tie_break_source_order | exactly_two_plans | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 |  |

## 8. Does Any Variant Move Counts Toward Drake Anchors?

Closest plausible/text-supported rows:

| top_two_selection_variant | exposure_universe | default_mapping_rule | premium_variant | issuer_concept | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_within_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | difference_vs_drake_any_enrollee_millions | difference_vs_drake_across_enrollee_millions | by_year_2022_any | by_year_2023_any | by_year_2024_any | by_year_2022_across | by_year_2023_across | by_year_2024_across | constructible_county_years | drake_text_support | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current_repo_top_two | exactly_two_plans | current_repo_rule | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Baseline: age-40 gross premium, deduplicate PlanId, tie-break by issuer_id and PlanId. |
| current_repo_top_two | exactly_two_plans | same_plan_if_available_else_source_order | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Baseline: age-40 gross premium, deduplicate PlanId, tie-break by issuer_id and PlanId. |
| current_repo_top_two | exactly_two_plans | source_order_first_valid | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Baseline: age-40 gross premium, deduplicate PlanId, tie-break by issuer_id and PlanId. |
| current_repo_top_two | include_ties_at_second_lowest | current_repo_rule | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Baseline: age-40 gross premium, deduplicate PlanId, tie-break by issuer_id and PlanId. |
| current_repo_top_two | include_ties_at_second_lowest | same_plan_if_available_else_source_order | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Baseline: age-40 gross premium, deduplicate PlanId, tie-break by issuer_id and PlanId. |
| rank_by_gross_age40_premium_planid | exactly_two_plans | same_plan_if_available_else_source_order | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Makes current behavior explicit. |
| rank_by_gross_age40_premium_planid | exactly_two_plans | current_repo_rule | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Makes current behavior explicit. |
| current_repo_top_two | include_ties_at_second_lowest | source_order_first_valid | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Baseline: age-40 gross premium, deduplicate PlanId, tie-break by issuer_id and PlanId. |
| rank_by_gross_age40_premium_planid | exactly_two_plans | source_order_first_valid | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Makes current behavior explicit. |
| rank_by_gross_age40_premium_planid | include_ties_at_second_lowest | current_repo_rule | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Makes current behavior explicit. |
| rank_by_gross_age40_premium_planid | include_ties_at_second_lowest | same_plan_if_available_else_source_order | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Makes current behavior explicit. |
| rank_by_gross_age40_premium_planid | include_ties_at_second_lowest | source_order_first_valid | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | plausible | Makes current behavior explicit. |

Closest numeric rows, including diagnostic-only variants:

| top_two_selection_variant | exposure_universe | default_mapping_rule | premium_variant | issuer_concept | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_within_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | difference_vs_drake_any_enrollee_millions | difference_vs_drake_across_enrollee_millions | by_year_2022_any | by_year_2023_any | by_year_2024_any | by_year_2022_across | by_year_2023_across | by_year_2024_across | constructible_county_years | drake_text_support | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rank_by_ehb_adjusted_gross_premium | exactly_two_plans | source_order_first_valid | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | include_ties_at_second_lowest | current_repo_rule | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | include_ties_at_second_lowest | source_order_first_valid | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | include_ties_at_second_lowest | same_plan_if_available_else_source_order | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | exactly_two_plans | current_repo_rule | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | exactly_two_plans | same_plan_if_available_else_source_order | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_postsubsidy_net_premium | include_ties_at_second_lowest | same_plan_if_available_else_source_order | gross_only | plan_panel_preferred | 4530 | 123 | 4423 | 29.999 | 1.193 | 78 | -88 | 1.599 | 0.393 | 1687 | 1448 | 1395 | 96 | 13 | 14 | 6267 | diagnostic_only | Drake says top-two premium silver plans, but not that ranking is by net premium. |
| rank_by_postsubsidy_net_premium | include_ties_at_second_lowest | current_repo_rule | gross_only | plan_panel_preferred | 4530 | 123 | 4423 | 29.999 | 1.193 | 78 | -88 | 1.599 | 0.393 | 1687 | 1448 | 1395 | 96 | 13 | 14 | 6267 | diagnostic_only | Drake says top-two premium silver plans, but not that ranking is by net premium. |
| rank_by_postsubsidy_net_premium | include_ties_at_second_lowest | source_order_first_valid | gross_only | plan_panel_preferred | 4530 | 123 | 4423 | 29.999 | 1.193 | 78 | -88 | 1.599 | 0.393 | 1687 | 1448 | 1395 | 96 | 13 | 14 | 6267 | diagnostic_only | Drake says top-two premium silver plans, but not that ranking is by net premium. |
| county_rating_area_specific_top_two | exactly_two_plans | source_order_first_valid | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests county/rating-area collapse issues. |
| all_tied_lowest_or_second_lowest | exactly_two_plans | source_order_first_valid | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |
| all_tied_lowest_or_second_lowest | include_ties_at_second_lowest | current_repo_rule | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |

Rows closest to the any-turnover anchor:

| top_two_selection_variant | exposure_universe | default_mapping_rule | premium_variant | issuer_concept | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_within_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | difference_vs_drake_any_enrollee_millions | difference_vs_drake_across_enrollee_millions | by_year_2022_any | by_year_2023_any | by_year_2024_any | by_year_2022_across | by_year_2023_across | by_year_2024_across | constructible_county_years | drake_text_support | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rank_by_ehb_adjusted_gross_premium | exactly_two_plans | source_order_first_valid | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | include_ties_at_second_lowest | current_repo_rule | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | include_ties_at_second_lowest | source_order_first_valid | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | include_ties_at_second_lowest | same_plan_if_available_else_source_order | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | exactly_two_plans | current_repo_rule | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_ehb_adjusted_gross_premium | exactly_two_plans | same_plan_if_available_else_source_order | gross_only | plan_panel_preferred | 4425 | 123 | 4318 | 29.591 | 1.193 | -27 | -88 | 1.191 | 0.393 | 1669 | 1466 | 1290 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether non-EHB premium residual changes prior top-two identity. |
| rank_by_postsubsidy_net_premium | include_ties_at_second_lowest | same_plan_if_available_else_source_order | gross_only | plan_panel_preferred | 4530 | 123 | 4423 | 29.999 | 1.193 | 78 | -88 | 1.599 | 0.393 | 1687 | 1448 | 1395 | 96 | 13 | 14 | 6267 | diagnostic_only | Drake says top-two premium silver plans, but not that ranking is by net premium. |
| rank_by_postsubsidy_net_premium | include_ties_at_second_lowest | current_repo_rule | gross_only | plan_panel_preferred | 4530 | 123 | 4423 | 29.999 | 1.193 | 78 | -88 | 1.599 | 0.393 | 1687 | 1448 | 1395 | 96 | 13 | 14 | 6267 | diagnostic_only | Drake says top-two premium silver plans, but not that ranking is by net premium. |

Rows closest to the across-insurer anchor:

| top_two_selection_variant | exposure_universe | default_mapping_rule | premium_variant | issuer_concept | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_within_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | difference_vs_drake_any_enrollee_millions | difference_vs_drake_across_enrollee_millions | by_year_2022_any | by_year_2023_any | by_year_2024_any | by_year_2022_across | by_year_2023_across | by_year_2024_across | constructible_county_years | drake_text_support | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_tied_lowest_or_second_lowest | exactly_two_plans | current_repo_rule | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |
| all_tied_lowest_or_second_lowest | exactly_two_plans | current_repo_rule | gross_only | plan_panel_preferred | 4626 | 123 | 4519 | 30.254 | 1.193 | 174 | -88 | 1.854 | 0.393 | 1728 | 1503 | 1395 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |
| all_tied_lowest_or_second_lowest | exactly_two_plans | same_plan_if_available_else_source_order | gross_only | plan_panel_preferred | 4626 | 123 | 4519 | 30.254 | 1.193 | 174 | -88 | 1.854 | 0.393 | 1728 | 1503 | 1395 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |
| all_tied_lowest_or_second_lowest | exactly_two_plans | same_plan_if_available_else_source_order | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |
| all_tied_lowest_or_second_lowest | exactly_two_plans | source_order_first_valid | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |
| all_tied_lowest_or_second_lowest | include_ties_at_second_lowest | current_repo_rule | gross_only | plan_panel_preferred | 4626 | 123 | 4519 | 30.254 | 1.193 | 174 | -88 | 1.854 | 0.393 | 1728 | 1503 | 1395 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |
| all_tied_lowest_or_second_lowest | include_ties_at_second_lowest | current_repo_rule | ehb_named_states_only | plan_panel_preferred | 4344 | 123 | 4237 | 29.269 | 1.193 | -108 | -88 | 0.869 | 0.393 | 1654 | 1390 | 1300 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |
| all_tied_lowest_or_second_lowest | exactly_two_plans | source_order_first_valid | gross_only | plan_panel_preferred | 4626 | 123 | 4519 | 30.254 | 1.193 | 174 | -88 | 1.854 | 0.393 | 1728 | 1503 | 1395 | 96 | 13 | 14 | 6477 | diagnostic_only | Tests whether ties are counted more broadly than one selected PlanId per rank. |

## 9. Does Any Variant Explain The Across-Insurer Gap?

No. The largest across-insurer count in this variant matrix is 123, still below Drake's 211. Top-two variants therefore do not fully explain the central across-insurer mismatch.

## 10. Kansas 2022 Update

Kansas 2022 remains present in the deep-dive output with 4935 diagnostic rows. The audit does not identify a top-two rule that removes Kansas across-insurer turnover while remaining text-faithful.

## 11. Likely Remaining Source Of Mismatch

The remaining mismatch is less likely to be caused solely by top-two selection. Premium classification and crosswalk mapping have already been stressed; top-two variants also fail to match across-insurer counts. The residual gap is most likely a private-code detail involving sample/complete-case treatment construction, unpublished premium/default assumptions, or a combination of small implementation choices.

## 12. Exact Next Repair Recommendation

Manually audit the county-years that Drake counts as across-insurer exposure if such a replication file can be obtained from authors. Without author-level exposure data, the smallest next public-file repair is a county-year reconciliation notebook that enumerates all zero prior silver plans, their default plans, and why each is outside the top-two exposure universe.

The file `outputs/top_two_turnover_failure_reason.csv` is intentionally written as a compact state/year/rank/rule summary rather than a full row-level dump. A full selected-plan-pair dump exceeded practical GitHub file-size limits and is reproducible locally from `scripts/08_top_two_silver_selection_audit.py` if needed.

## 13. Step 4 Recommendation

**No-Go.** Do not move to causal modeling until the exposure mismatch is either solved or explicitly accepted as a bounded public-file replication limitation.

## Baseline Row

| top_two_selection_variant | exposure_universe | default_mapping_rule | premium_variant | issuer_concept | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_within_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | difference_vs_drake_any_enrollee_millions | difference_vs_drake_across_enrollee_millions | by_year_2022_any | by_year_2023_any | by_year_2024_any | by_year_2022_across | by_year_2023_across | by_year_2024_across | constructible_county_years | drake_text_support | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current_repo_top_two | exactly_two_plans | current_repo_rule | current_ehb_all_states | plan_panel_preferred | 4188 | 107 | 4088 | 28.065 | 0.524 | -264 | -104 | -0.335 | -0.276 | 1624 | 1258 | 1306 | 88 | 5 | 14 | 6477 | plausible | Baseline: age-40 gross premium, deduplicate PlanId, tie-break by issuer_id and PlanId. |
