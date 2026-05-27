# Step 2 Repair Implementation Notes

## What Changed

`scripts/03_build_drake_replication_dataset.py` has been updated so the next full Step 2 rebuild can produce the fields needed for closer Drake-style replication:

- Drake supplement eTable 3 county-exclusion flags.
- Drake-harmonized primary sample output.
- 2021 county enrollment weights from the 2021 OEP county PUF.
- Silver market controls: number of silver plans, number of silver issuers, lowest silver premium, second-lowest silver premium, and silver premium spread.
- Bronze controls: lowest bronze premium and bronze spread.

## Current Data Status

The current committed processed datasets were not rebuilt from raw files in this pass because `data/raw/` is not present in the working tree. Step 3 was rerun from the existing processed data, so it still correctly reports that the current processed data lack `bronze_spread`, `number_of_insurers`, and `enrollment_2021_weight`.

## Why This Matters

Drake Table 2 and later regression replication use 2021 enrollment weights and market controls. The current outcome replication is strong, but Step 4 should wait until the repaired Step 2 build is run from raw source files and validated.

## Next Build Command

After raw files are restored or downloaded:

```bash
python scripts/03_build_drake_replication_dataset.py --include-nebraska-sensitivity --verbose
python scripts/04_validate_drake_replication_dataset.py
python scripts/05_descriptive_replication_checks.py --primary-sample --verbose
```

No causal models should be run until the rebuilt Step 2 data pass the Step 3 diagnostics.
