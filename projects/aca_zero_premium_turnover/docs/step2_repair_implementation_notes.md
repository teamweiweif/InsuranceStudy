# Step 2 Repair Implementation Notes

## What Changed

`scripts/03_build_drake_replication_dataset.py` has been updated and rerun against the local raw-data environment, producing the fields needed for closer Drake-style replication:

- Drake supplement eTable 3 county-exclusion flags.
- Drake-harmonized primary sample output.
- 2021 county enrollment weights from the 2021 OEP county PUF.
- Silver market controls: number of silver plans, number of silver issuers, lowest silver premium, second-lowest silver premium, and silver premium spread.
- Bronze controls: lowest bronze premium and bronze spread.

## Current Data Status

The current processed datasets have now been rebuilt from local raw files. The raw files remain outside GitHub and are linked locally into `data/raw/` from the adjacent workstation data folder.

Validation after rebuild:

- Drake-harmonized county count: 2,159 counties.
- `enrollment_2021_weight`: present, 99.9% nonmissing in the primary sample.
- `bronze_spread`: present, 100% nonmissing in the primary sample.
- `number_of_insurers`: present.
- Remaining major warnings: proxy-based zero-premium treatment and weaker 2023-to-2024 current-plan join rate.

## Why This Matters

Drake Table 2 and later regression replication use 2021 enrollment weights and market controls. Those fields are now present, but Step 4 should still wait because treatment prevalence and across-insurer turnover do not yet align closely enough with Drake.

## Rebuild Command

When local raw files are available or linked:

```bash
python scripts/03_build_drake_replication_dataset.py --include-nebraska-sensitivity --verbose
python scripts/04_validate_drake_replication_dataset.py
python scripts/05_descriptive_replication_checks.py --primary-sample --verbose
```

No causal models should be run until the rebuilt Step 2 data pass the Step 3 diagnostics.
