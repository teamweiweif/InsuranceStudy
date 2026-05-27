# Top-Two Silver Rule Extraction

## Confirmed From Drake Article/Supplement

1. Drake identifies county-years with zero-premium silver plan turnover by first calculating postsubsidy premiums for the two prior-year lowest-premium silver plans and their current-year default plans. Main article p. 3, "Exposure: Turnover in Zero-Premium Plans."
2. The prior-year exposure universe is the lowest-premium and second-lowest-premium silver plans. Main article p. 3 and Table 2 note.
3. The premium calculation is for a single 40-year-old enrollee in the 100%-150% FPL range. Main article p. 3; Supplement 1 eAppendix 2.
4. Supplement 1 eAppendix 2 sets income at 125% FPL, the midpoint of 100%-150% FPL.
5. Drake uses QHP Landscape data for county-year plan offerings, premiums, and benefits, OEP PUFs for county-year reenrollment, and the CCIIO Plan ID Crosswalk for default plans. Main article p. 3.
6. Drake excludes AK and HI because FPL differs and excludes NE because Nebraska does not use county lines to define Marketplace markets. Main article p. 3; Supplement 1 eAppendix 1.
7. Drake excludes counties with missing or inconsistent crosswalk/FIPS/ZIP default data listed in Supplement 1 eTable 3.
8. Drake considers non-EHB costs because APTC cannot reduce non-EHB premium to zero. Supplement 1 eAppendix 3.

## Confirmed From Official CMS/QHP Documentation

1. CMS Exchange PUFs include Rate, Plan Attributes, Service Area, Benefits and Cost Sharing, and Plan ID Crosswalk PUF files on the CMS Exchange PUF page: https://www.cms.gov/marketplace/resources/data/public-use-files.
2. The Plan ID Crosswalk Data Dictionary defines `FIPSCode`, `ZipCode`, `CrosswalkLevel`, and `ReasonForCrosswalk`; `ZipCode = 00000` identifies whole-county rows and CrosswalkLevel 4/5 represent no reenrollment/default option. Source: https://www.cms.gov/files/document/plan-id-crosswalk-datadictionary-py26.pdf.
3. QHP Landscape medical individual instructions state that premium amounts do not include tax credits and include example premium scenarios such as Adult Individual Age 40. Source: https://www.healthcare.gov/downloads/med-ind-lndscp-in.pdf and https://data.healthcare.gov/datafile/py2022/med-ind-lndscp-in.pdf.

## Current Repo Assumption

1. The current repo ranks silver plans within county-year by QHP Landscape `Premium Adult Individual Age 40`.
2. It deduplicates by `PlanId`/`Plan ID (Standard Component)` before ranking.
3. It tie-breaks by `issuer_id` and `plan_id`.
4. It uses QHP Landscape rows as county-plan availability for 2021-2024 when direct QHP files are available.
5. It treats `StandardComponentId` as equivalent to the QHP Landscape plan ID in the cached panel.

## Diagnostic-Only Sensitivities

- Rank by StandardComponentId collapse.
- Rank by estimated postsubsidy net premium.
- Rank by EHB-adjusted gross premium.
- Rank by source/display order.
- Rank by Rate PUF age-40 premium.
- Rank within county-rating-area cells.
- Require stricter service-area evidence.
- Exclude child-only or limited rows if flags are available.
- Preserve source-order tie-breaking.
- Include all ties at the lowest or second-lowest premium.

## Answers To The Requested Rule Questions

1. Drake confirms postsubsidy premiums are calculated for the prior-year top-two and default plans, but the text says the top-two are "lowest-premium" silver plans, not "lowest postsubsidy premium" silver plans. The most text-faithful ranking is gross/displayed silver premium, with net premium used for zero/positive classification.
2. The 40-year-old 100%-150% FPL/125% FPL profile is confirmed for premium/subsidy calculation, not explicitly for ranking. QHP Landscape Adult Individual Age 40 is therefore the closest public-file ranking premium.
3. Drake names QHP Landscape as the plan offering/premium/benefit source. It does not say Rate PUF overrides QHP Landscape for top-two ranking.
4. Drake does not disclose whether Rate, Plan Attributes, Benefits, or Service Area PUFs supplement QHP Landscape for top-two selection.
5. Drake states county-year plan offerings. It does not disclose county-rating-area or county-service-area tie handling.
6. Dental, SHOP, non-individual, and catastrophic exclusions are implicit in using QHP Landscape medical individual silver plans, but Drake does not enumerate all filters.
7. Drake does not state whether CSR variants or duplicated StandardComponentIds are collapsed.
8. Drake does not state whether ranking uses PlanId, StandardComponentId, HIOS ID, or another identifier.
9. Drake does not state duplicate-row collapse rules.
10. Drake does not state which duplicate county/rating-area/service-area row is retained.
11. Drake does not state ranking before or after non-EHB adjustment; non-EHB is confirmed for premium zero-dollar classification.
12. eTable 1 separately reports 100%-150% and 150%-200% FPL exposure, but the main regression exposure uses the 100%-150% profile.
13. AK/HI/NE are excluded from the analytic sample; Drake does not state whether ranking was run before or after these exclusions.
14. HealthCare.gov platform restrictions define the analytic sample; Drake does not state whether plan ranking was computed for excluded states before dropping them.
15. Drake discusses missing OEP/crosswalk/FIPS/ZIP data in eAppendix 1/eTable 3 but not generic missing QHP premium rows or duplicate plan rows.
16. Unstated details require diagnostic variants rather than replacement of the text-faithful baseline.
