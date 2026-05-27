# Step 3 Progress And Limitations

## Completed

- Verified that processed Step 2 datasets are readable and nonempty.
- Applied Drake supplement eTable 3 county exclusions and wrote a Drake-harmonized Step 3 dataset.
- Produced sample-alignment diagnostics, Table 1-style reenrollment descriptives, treatment prevalence, exposure/count comparisons, Table 2-style descriptive comparisons, sign checks, weakness audits, and sensitivity datasets.
- Rebuilt Step 2 from the local raw-data environment and retained 2021 enrollment weights, bronze spread, silver/bronze plan counts, and insurer-count controls.
- Wrote `docs/step3_descriptive_replication_report.md`.

## Partially Completed

- Treatment prevalence is EHB-aware and 125 percent-FPL-style, but still only partially comparable to Drake exposure tables.
- Treatment-definition sensitivity now compares gross-only, all-state EHB-aware, and IL/OR-only EHB variants.
- Across-insurer turnover remains under-detected relative to Drake.

## Not Completed

- No causal regressions, causal forests, policy learning, or formal Step 4 models were run.
- No exact household-specific APTC, income-stratified OEP outcome, or individual-level retention dataset was created.

## Main Findings In Plain English

- The 29-county sample gap is explained by Drake supplement eTable 3; after excluding those counties, the sample matches Drake's county anchors.
- The outcome data very closely reproduce the public OEP reenrollment structure.
- Any-turnover prevalence is sensitive to non-EHB handling: gross-only overcounts county-years while all-state EHB-aware undercounts them.
- Across-insurer turnover is too low relative to Drake under the strict zero-to-positive definition.
- 2022 still deserves scrutiny because it depends on the 2021-to-2022 treatment transition; direct PY2021 QHP Landscape is used when available locally.

## Honest Judgment

**Fix Step 2 before Step 4.** Recommendation: **B. Repair Step 2 treatment construction first.**

Main warnings:

- Any-turnover county-year count differs from Drake by -264.
- Across-issuer turnover count differs from Drake by -104; current proxy likely under-detects across-insurer turnover.
- Enrollment-weighted any-turnover exposure differs from Drake 100-150 FPL exposure by up to 6.5 pp.
- Treatment remains proxy-based; Step 2 does not prove household-specific net premiums, 125 percent FPL contribution, or non-EHB handling.

## Next 3 Tasks

1. Reconcile Drake's exact non-EHB treatment with public EHB percent fields; current EHB-aware, IL/OR-only, and gross-only variants do not jointly match all Drake treatment anchors.
2. Investigate why across-insurer county-years remain below Drake under all strict zero-to-positive definitions.
3. Rerun Step 3 after treatment repairs before starting Step 4 regressions.
