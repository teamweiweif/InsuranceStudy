# Premium Calculation Reconciliation Report

## 1. Executive Diagnosis

The direct PY2021 QHP Landscape source issue is no longer the main blocker. The remaining blocker is premium construction: no tested premium/subsidy/rounding variant simultaneously reproduces Drake's treatment anchors and remains fully confirmed by the article/supplement. The most text-faithful public-file implementation remains the all-state EHB-adjusted 125%-FPL proxy, but it undercounts both any turnover and across-insurer turnover. Step 4 remains **No-Go**.

## 2. Drake Exact Premium Rules From Article/Supplement

- Unit/exposure universe: article pp. 3-4 says Drake calculated postsubsidy premiums for the prior-year lowest and second-lowest silver plans and their current-year default plans using the Plan ID Crosswalk.
- Representative enrollee: Supplement 1 p. 7, eAppendix 2 uses a single 40-year-old enrollee in the 100%-150% FPL group.
- Income point: Supplement 1 p. 7, eAppendix 2 sets income at 125% FPL, the midpoint of 100%-150% FPL.
- Required contribution: Supplement 1 p. 7 states that under ARPA subsidized enrollees in 100%-150% FPL receive enough subsidies to purchase zero-dollar silver plans regardless of age. The supplement does not provide a numeric annual income or a line-by-line APTC equation.
- Non-EHB: Supplement 1 p. 8 says non-EHB coverage is considered because federal subsidies cannot reduce non-EHB costs to zero; it names Illinois and Oregon as examples where required non-EHB coverage precludes zero-premium plans.
- Missing EHB percent and rounding: the article/supplement do not state how missing EHBPercentTotalPremium is handled, nor whether zero is defined by <=0, <=$0.01, rounded whole-dollar display, or another threshold.
- Premium source: article p. 3 identifies QHP Landscape as the premium/benefit source and Plan ID Crosswalk as default-plan source. It does not state that Rate PUF premiums override QHP Landscape displayed age-40 premiums.

## 3. Current Repo Premium Logic

The current primary logic computes age-40 gross premiums from QHP Landscape, applies EHBPercentTotalPremium to split EHB and non-EHB components, proxies APTC as the county-year SLCSP EHB premium under a 125%-FPL zero-contribution assumption, and defines net premium as max(plan EHB premium - benchmark EHB premium, 0) plus non-EHB residual. Missing EHB percent is treated as 100% EHB. Zero is <= $0.01; positive is > $0.01.

## 4. Differences Between Drake And Current Repo

- Confirmed aligned: top-two prior silver universe, 40-year-old representative enrollee, 125% FPL proxy, QHP Landscape source, Plan ID Crosswalk defaulting, and non-EHB concept.
- Not fully confirmed: exact APTC equation, exact handling of EHBPercentTotalPremium missingness, whether non-EHB adjustment applies beyond named states, and exact rounding/zero threshold.
- Current public-file implementation cannot observe individual household APTC or actual defaulted enrollee premium bills.

## 5. Variant Comparison Table

| variant_name | issuer_concept | current_plan_lookup_rule | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | whether_supported_by_drake_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cent_threshold_zero | crosswalk_issuer_only | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| current_ehb_all_states | crosswalk_issuer_only | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| ehb_missing_as_missing | crosswalk_issuer_only | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | diagnostic_only |
| ehb_named_states_only | crosswalk_issuer_only | all_metal_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_only_when_ehb_percent_less_than_100 | crosswalk_issuer_only | all_metal_panel | 4218 | 107 | 28.18419 | 0.524394 | -234 | -104 | plausible |
| gross_only | crosswalk_issuer_only | all_metal_panel | 4626 | 123 | 30.253534 | 1.192653 | 174 | -88 | diagnostic_only |
| one_dollar_threshold | crosswalk_issuer_only | all_metal_panel | 4208 | 122 | 29.054814 | 1.056219 | -244 | -89 | diagnostic_only |
| rounded_to_dollars_zero | crosswalk_issuer_only | all_metal_panel | 4086 | 118 | 27.812889 | 0.755478 | -366 | -93 | diagnostic_only |
| strict_zero | crosswalk_issuer_only | all_metal_panel | 4179 | 107 | 28.060771 | 0.524394 | -273 | -104 | diagnostic_only |
| cent_threshold_zero | plan_id_prefix | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| current_ehb_all_states | plan_id_prefix | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| ehb_missing_as_missing | plan_id_prefix | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | diagnostic_only |
| ehb_named_states_only | plan_id_prefix | all_metal_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_only_when_ehb_percent_less_than_100 | plan_id_prefix | all_metal_panel | 4218 | 107 | 28.18419 | 0.524394 | -234 | -104 | plausible |
| gross_only | plan_id_prefix | all_metal_panel | 4626 | 123 | 30.253534 | 1.192653 | 174 | -88 | diagnostic_only |
| one_dollar_threshold | plan_id_prefix | all_metal_panel | 4208 | 122 | 29.054814 | 1.056219 | -244 | -89 | diagnostic_only |
| rounded_to_dollars_zero | plan_id_prefix | all_metal_panel | 4086 | 118 | 27.812889 | 0.755478 | -366 | -93 | diagnostic_only |
| strict_zero | plan_id_prefix | all_metal_panel | 4179 | 107 | 28.060771 | 0.524394 | -273 | -104 | diagnostic_only |
| cent_threshold_zero | plan_panel_issuer_only | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| current_ehb_all_states | plan_panel_issuer_only | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| ehb_missing_as_missing | plan_panel_issuer_only | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | diagnostic_only |
| ehb_named_states_only | plan_panel_issuer_only | all_metal_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_only_when_ehb_percent_less_than_100 | plan_panel_issuer_only | all_metal_panel | 4218 | 107 | 28.18419 | 0.524394 | -234 | -104 | plausible |
| gross_only | plan_panel_issuer_only | all_metal_panel | 4626 | 123 | 30.253534 | 1.192653 | 174 | -88 | diagnostic_only |
| one_dollar_threshold | plan_panel_issuer_only | all_metal_panel | 4208 | 122 | 29.054814 | 1.056219 | -244 | -89 | diagnostic_only |
| rounded_to_dollars_zero | plan_panel_issuer_only | all_metal_panel | 4086 | 118 | 27.812889 | 0.755478 | -366 | -93 | diagnostic_only |
| strict_zero | plan_panel_issuer_only | all_metal_panel | 4179 | 107 | 28.060771 | 0.524394 | -273 | -104 | diagnostic_only |
| cent_threshold_zero | plan_panel_preferred | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| current_ehb_all_states | plan_panel_preferred | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| ehb_missing_as_missing | plan_panel_preferred | all_metal_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | diagnostic_only |
| ehb_named_states_only | plan_panel_preferred | all_metal_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_only_when_ehb_percent_less_than_100 | plan_panel_preferred | all_metal_panel | 4218 | 107 | 28.18419 | 0.524394 | -234 | -104 | plausible |
| gross_only | plan_panel_preferred | all_metal_panel | 4626 | 123 | 30.253534 | 1.192653 | 174 | -88 | diagnostic_only |
| one_dollar_threshold | plan_panel_preferred | all_metal_panel | 4208 | 122 | 29.054814 | 1.056219 | -244 | -89 | diagnostic_only |
| rounded_to_dollars_zero | plan_panel_preferred | all_metal_panel | 4086 | 118 | 27.812889 | 0.755478 | -366 | -93 | diagnostic_only |
| strict_zero | plan_panel_preferred | all_metal_panel | 4179 | 107 | 28.060771 | 0.524394 | -273 | -104 | diagnostic_only |
| cent_threshold_zero | crosswalk_issuer_only | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| current_ehb_all_states | crosswalk_issuer_only | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| ehb_missing_as_missing | crosswalk_issuer_only | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | diagnostic_only |
| ehb_named_states_only | crosswalk_issuer_only | silver_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_only_when_ehb_percent_less_than_100 | crosswalk_issuer_only | silver_panel | 4218 | 107 | 28.18419 | 0.524394 | -234 | -104 | plausible |
| gross_only | crosswalk_issuer_only | silver_panel | 4626 | 123 | 30.253534 | 1.192653 | 174 | -88 | diagnostic_only |
| one_dollar_threshold | crosswalk_issuer_only | silver_panel | 4208 | 122 | 29.054814 | 1.056219 | -244 | -89 | diagnostic_only |
| rounded_to_dollars_zero | crosswalk_issuer_only | silver_panel | 4086 | 118 | 27.812889 | 0.755478 | -366 | -93 | diagnostic_only |
| strict_zero | crosswalk_issuer_only | silver_panel | 4179 | 107 | 28.060771 | 0.524394 | -273 | -104 | diagnostic_only |
| cent_threshold_zero | plan_id_prefix | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| current_ehb_all_states | plan_id_prefix | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| ehb_missing_as_missing | plan_id_prefix | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | diagnostic_only |
| ehb_named_states_only | plan_id_prefix | silver_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_only_when_ehb_percent_less_than_100 | plan_id_prefix | silver_panel | 4218 | 107 | 28.18419 | 0.524394 | -234 | -104 | plausible |
| gross_only | plan_id_prefix | silver_panel | 4626 | 123 | 30.253534 | 1.192653 | 174 | -88 | diagnostic_only |
| one_dollar_threshold | plan_id_prefix | silver_panel | 4208 | 122 | 29.054814 | 1.056219 | -244 | -89 | diagnostic_only |
| rounded_to_dollars_zero | plan_id_prefix | silver_panel | 4086 | 118 | 27.812889 | 0.755478 | -366 | -93 | diagnostic_only |
| strict_zero | plan_id_prefix | silver_panel | 4179 | 107 | 28.060771 | 0.524394 | -273 | -104 | diagnostic_only |
| cent_threshold_zero | plan_panel_issuer_only | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| current_ehb_all_states | plan_panel_issuer_only | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| ehb_missing_as_missing | plan_panel_issuer_only | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | diagnostic_only |
| ehb_named_states_only | plan_panel_issuer_only | silver_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_only_when_ehb_percent_less_than_100 | plan_panel_issuer_only | silver_panel | 4218 | 107 | 28.18419 | 0.524394 | -234 | -104 | plausible |
| gross_only | plan_panel_issuer_only | silver_panel | 4626 | 123 | 30.253534 | 1.192653 | 174 | -88 | diagnostic_only |
| one_dollar_threshold | plan_panel_issuer_only | silver_panel | 4208 | 122 | 29.054814 | 1.056219 | -244 | -89 | diagnostic_only |
| rounded_to_dollars_zero | plan_panel_issuer_only | silver_panel | 4086 | 118 | 27.812889 | 0.755478 | -366 | -93 | diagnostic_only |
| strict_zero | plan_panel_issuer_only | silver_panel | 4179 | 107 | 28.060771 | 0.524394 | -273 | -104 | diagnostic_only |
| cent_threshold_zero | plan_panel_preferred | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| current_ehb_all_states | plan_panel_preferred | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | plausible |
| ehb_missing_as_missing | plan_panel_preferred | silver_panel | 4188 | 107 | 28.064756 | 0.524394 | -264 | -104 | diagnostic_only |
| ehb_named_states_only | plan_panel_preferred | silver_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_only_when_ehb_percent_less_than_100 | plan_panel_preferred | silver_panel | 4218 | 107 | 28.18419 | 0.524394 | -234 | -104 | plausible |
| gross_only | plan_panel_preferred | silver_panel | 4626 | 123 | 30.253534 | 1.192653 | 174 | -88 | diagnostic_only |
| one_dollar_threshold | plan_panel_preferred | silver_panel | 4208 | 122 | 29.054814 | 1.056219 | -244 | -89 | diagnostic_only |
| rounded_to_dollars_zero | plan_panel_preferred | silver_panel | 4086 | 118 | 27.812889 | 0.755478 | -366 | -93 | diagnostic_only |
| strict_zero | plan_panel_preferred | silver_panel | 4179 | 107 | 28.060771 | 0.524394 | -273 | -104 | diagnostic_only |

Closest variants by combined anchor gap:

| variant_name | issuer_concept | current_plan_lookup_rule | pooled_any_turnover_county_years | pooled_across_issuer_turnover_county_years | pooled_any_turnover_enrollee_years_millions | pooled_across_issuer_enrollee_years_millions | difference_vs_drake_any_count | difference_vs_drake_across_count | whether_supported_by_drake_text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ehb_named_states_only | plan_id_prefix | silver_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_named_states_only | plan_panel_issuer_only | silver_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_named_states_only | crosswalk_issuer_only | silver_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_named_states_only | plan_panel_preferred | silver_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_named_states_only | plan_id_prefix | all_metal_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_named_states_only | plan_panel_issuer_only | all_metal_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_named_states_only | crosswalk_issuer_only | all_metal_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |
| ehb_named_states_only | plan_panel_preferred | all_metal_panel | 4344 | 123 | 29.269052 | 1.192653 | -108 | -88 | plausible |

## 6. Which Variant Best Matches Drake Anchors

Numerically, the IL/OR-only EHB variant is closest across the encoded anchors, while all-metal current lookup does not change the treatment counts in the current data. None reaches the Drake anchors for both any turnover and across-insurer turnover. Gross-only overcounts any-turnover county-years and enrollee-years and is not faithful to the non-EHB text.

## 7. Whether That Variant Is Justified By Drake Text

The best text-supported variant is `current_ehb_all_states` with the top-two prior silver universe and Plan ID Crosswalk current default lookup. It is plausible rather than confirmed because Drake does not disclose missing-EHB and rounding rules. IL/OR-only EHB is plausible as a sensitivity because IL and OR are named, but the word 'including' means the supplement does not prove only those states should receive the adjustment.

## 8. Why Across-Insurer Remains Underdetected

Across-insurer undercount persists across premium variants, implying that premium calculation alone does not explain the 211-count Drake anchor. The likely remaining mechanisms are crosswalk default-row selection, current mapped plan lookup/metal handling, or an unobserved detail in Drake's exact premium/default construction. Issuer concept sensitivity alone has not closed the gap.

## 9. Kansas 2022

Kansas 2022 remains concentrated in across-insurer turnover under all variants. The new Kansas audit file preserves plan-pair premiums, EHB shares, crosswalk fields, and variant flags. Current evidence does not prove Kansas is an artifact of premium calculation; it should next be audited against crosswalk default selection and issuer/default mapping.

## 10. Exact Next Action Before Step 4

Reconcile Plan ID Crosswalk default-row hierarchy and current default-plan lookup against Drake's exact implementation. Premium variants alone do not solve the treatment-count gap.

## 11. Final Recommendation

**No-Go for Step 4.** Use `current_ehb_all_states` as the most text-faithful public-file premium proxy for continued diagnostics, not as a finalized treatment for formal regression replication.

Text-faithful baseline anchor gaps:

- any turnover county-years: 4188 vs 4452 (-264)
- across-insurer county-years: 107 vs 211 (-104)
- any turnover enrollee-years: 28.065M vs 28.4M (-0.335M)
- across-insurer enrollee-years: 0.524M vs 0.8M (-0.276M)
