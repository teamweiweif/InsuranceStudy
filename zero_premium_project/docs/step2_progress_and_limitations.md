# Step 2 Progress And Limitations

## Completed

- Built OEP county-year outcomes for 2022-2024.
- Built silver county-plan panel for 2021-2024.
- Built top-two silver plan file, zero-premium proxy file, crosswalk transition files, treatment files, and final county-year datasets.
- Applied primary sample restrictions: continuously HC.gov states, excluding AK, HI, and NE.
- Logged build steps to `logs/step2_build.log`.

## Partially Completed

- 2021 input is fallback-based because direct PY2021 QHP Landscape files were unavailable.
- Zero-premium status is an estimated benchmark proxy, not an exact observed net premium.
- Some mapped current-year plan joins are incomplete and flagged.

## Not Completed

- No exact household-specific APTC calculation was implemented.
- No individual-level retention or HTE dataset can be produced from these public PUFs.
- No causal models were run.

## Honest Feasibility Judgment

**Conditional Go**.

Step 3 update: descriptive replication has now been run using Drake supplement details. The raw 2,188-county Step 2 primary sample is preserved, but Step 3 applies the supplement eTable 3 county exclusions and produces a 2,159-county Drake-harmonized sample. Outcome descriptives match Drake closely. The updated judgment before Step 4 is **Fix Step 2 before Step 4**, mainly because the treatment proxy, across-insurer classification, non-EHB handling, and 2021 enrollment weights/control variables are not yet sufficiently replicated.

Repair-code update: `scripts/03_build_drake_replication_dataset.py` now includes code to generate 2021 enrollment weights, silver/bronze market controls, bronze spread, and Drake eTable 3 sample flags on the next raw-data rebuild. The committed processed CSVs have not yet been rebuilt from raw files in this pass because `data/raw/` is excluded from the repo.

## Immediate Next Actions

1. Review 2021 fallback panel and decide whether to keep 2021 to 2022 in the primary treatment set.
2. Investigate state-year crosswalk failures in `outputs/drake_replication_join_diagnostics.csv`.
3. Review Nebraska sensitivity before deciding whether NE can enter any analysis.
4. Compare treatment prevalence with Drake-style descriptive patterns before modeling.
5. Freeze the dataset version only after validation flags are reviewed.

Updated after Step 3:

1. Repair zero-premium treatment construction against Drake's 125 percent FPL and non-EHB details.
2. Reconcile across-insurer turnover counts with Drake's 211 county-year anchor.
3. Add or reconstruct 2021 enrollment weights, bronze spread, and insurer-count controls.
4. Rerun Step 3 before any Step 4 regression replication.
