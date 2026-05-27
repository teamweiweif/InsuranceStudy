# Step 3 Progress And Limitations

## Completed

- Verified that processed Step 2 datasets are readable and nonempty.
- Applied Drake supplement eTable 3 county exclusions and wrote a Drake-harmonized Step 3 dataset.
- Produced sample-alignment diagnostics, Table 1-style reenrollment descriptives, treatment prevalence, exposure/count comparisons, Table 2-style descriptive comparisons, sign checks, weakness audits, and sensitivity datasets.
- Rebuilt Step 2 from the local raw-data environment and retained 2021 enrollment weights, bronze spread, silver/bronze plan counts, and insurer-count controls.
- Wrote `docs/step3_descriptive_replication_report.md`.

## Partially Completed

- Treatment prevalence is benchmark-proxy based and only partially comparable to Drake exposure tables.
- Across-insurer turnover remains under-detected relative to Drake.

## Not Completed

- No causal regressions, causal forests, policy learning, or formal Step 4 models were run.
- No exact household-specific APTC or individual-level retention dataset was created.

## Main Findings In Plain English

- The 29-county sample gap is explained by Drake supplement eTable 3; after excluding those counties, the sample matches Drake's county anchors.
- The outcome data very closely reproduce the public OEP reenrollment structure.
- Any-turnover prevalence is directionally plausible, but across-insurer turnover is too low relative to Drake.
- Treatment construction needs stricter validation before formal replication.
- 2022 remains weaker because it depends on the 2021 fallback construction.

## Honest Judgment

**Fix Step 2 before Step 4.** Recommendation: **B. Repair Step 2 treatment construction first.**

Main warnings:

- Any-turnover county-year count differs from Drake by 173.
- Across-issuer turnover count differs from Drake by -88; current proxy likely under-detects across-insurer turnover.
- Treatment remains proxy-based; Step 2 does not prove household-specific net premiums, 125 percent FPL contribution, or non-EHB handling.

## Next 3 Tasks

1. Repair Step 2 treatment construction against Drake's exact 125 percent FPL, non-EHB, and current-year plan/default logic.
2. Investigate why any-turnover county-years remain 173 above Drake and across-insurer county-years remain 88 below Drake.
3. Rerun Step 3 after treatment repairs before starting Step 4 regressions.
