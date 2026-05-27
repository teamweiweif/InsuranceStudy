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

## Immediate Next Actions

1. Review 2021 fallback panel and decide whether to keep 2021 to 2022 in the primary treatment set.
2. Investigate state-year crosswalk failures in `outputs/drake_replication_join_diagnostics.csv`.
3. Review Nebraska sensitivity before deciding whether NE can enter any analysis.
4. Compare treatment prevalence with Drake-style descriptive patterns before modeling.
5. Freeze the dataset version only after validation flags are reviewed.
