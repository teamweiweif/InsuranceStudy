# Drake-Style Replication Dataset Report

## Executive Summary

Overall status: **Conditional Go for moving to Step 3**.

The full county-year replication dataset was built for outcome years 2022, 2023, 2024. Outcomes are directly constructible from CMS OEP county PUFs. Treatment construction is proxy-based, not exact: zero-premium status uses a benchmark-based low-income age-40 proxy because household-specific APTC and individual enrollment are not public. The 2021 to 2022 transition is attempted from official Exchange PUF plus Health Plan Finder fallback rather than direct QHP Landscape.

**Step 3 update after reading Drake et al. supplement:** this Step 2 report describes the raw constructed dataset. Step 3 now applies Drake supplement eTable 3 county exclusions. The raw primary sample has 6,564 county-years / 2,188 counties; the Drake-harmonized Step 3 sample has 6,477 county-years / 2,159 counties and matches Drake's 6,471 county-years / 2,157 unique counties with nonmissing enrollment. The current Step 3 recommendation is **Fix Step 2 before Step 4**, because treatment construction and later regression controls still require repair.

## What Was Built

- Final dataset: `data/processed/drake_replication_county_year_2022_2024.csv`
- Primary sample: `data/processed/drake_replication_county_year_2022_2024_primary_sample.csv`
- Nebraska sensitivity: `data/processed/drake_replication_county_year_2022_2024_sensitivity_nebraska.csv`
- Parquet written: `True`
- Unit: county-year
- Rows before restrictions: 7211
- Rows in primary sample: 6564
- Counties in primary sample: 2188
- States in primary sample: 29 (AL, AR, AZ, DE, FL, GA, IA, IL, IN, KS, LA, MI, MO, MS, MT, NC, ND, NH, OH, OK, OR, SC, SD, TN, TX, UT, WI, WV, WY)
- Drake-harmonized Step 3 sample after eTable 3 county exclusions: `data/processed/drake_replication_primary_drake_harmonized_2022_2024.csv`
- Rows in Drake-harmonized Step 3 sample: 6477
- Counties in Drake-harmonized Step 3 sample: 2159

## Data Sources

The build uses CMS OEP County- and State-Level PUFs for 2022-2024; CMS Exchange Rate, Plan Attributes, Service Area, and Plan ID Crosswalk PUFs for 2021-2024; Data.HealthCare.gov QHP Landscape files for 2022-2024; and CMS Health Plan Finder RBIS state-rating-area fallback for 2021.

## Outcome Construction

Exact OEP columns used: `Cnsmr`, `New_Cnsmr`, `Tot_Renrl`, `Auto_Renrl`, `Actv_Renrl`, `Actv_Renrl_Nsw`, `Actv_Renrl_Sw`. Derived rates and logs are set missing when numerator or denominator is missing, suppressed, or nonpositive. Suppressed values are not imputed.

## Treatment Construction

For each county-year, silver plans are ranked by age-40 gross premium. The two lowest silver plans are crosswalked to the current year with the Plan ID Crosswalk. Current-year mapped plan net premium proxy is gross premium minus current-year second-lowest silver benchmark, floored at zero. Zero-to-positive turnover equals prior top-two zero-premium proxy and mapped current positive net-premium proxy. Across-issuer and within-issuer flags use issuer IDs from prior plans and current mapped plans.

## Join Diagnostics

  transition          rank                     metric  numerator  denominator     rate
2021_to_2022        lowest      previous_top_two_rows       2588         2588 1.000000
2021_to_2022        lowest previous_plan_to_crosswalk       2418         2588 0.934312
2021_to_2022        lowest  crosswalk_to_current_plan       2418         2588 0.934312
2021_to_2022 second_lowest      previous_top_two_rows       2588         2588 1.000000
2021_to_2022 second_lowest previous_plan_to_crosswalk       2418         2588 0.934312
2021_to_2022 second_lowest  crosswalk_to_current_plan       2418         2588 0.934312
2022_to_2023        lowest      previous_top_two_rows       2449         2449 1.000000
2022_to_2023        lowest previous_plan_to_crosswalk       2449         2449 1.000000
2022_to_2023        lowest  crosswalk_to_current_plan       2449         2449 1.000000
2022_to_2023 second_lowest      previous_top_two_rows       2449         2449 1.000000
2022_to_2023 second_lowest previous_plan_to_crosswalk       2449         2449 1.000000
2022_to_2023 second_lowest  crosswalk_to_current_plan       2449         2449 1.000000
2023_to_2024        lowest      previous_top_two_rows       2449         2449 1.000000
2023_to_2024        lowest previous_plan_to_crosswalk       2421         2449 0.988567
2023_to_2024        lowest  crosswalk_to_current_plan       2288         2449 0.934259
2023_to_2024 second_lowest      previous_top_two_rows       2449         2449 1.000000
2023_to_2024 second_lowest previous_plan_to_crosswalk       2423         2449 0.989383
2023_to_2024 second_lowest  crosswalk_to_current_plan       2290         2449 0.935076
2021_to_2022           all             crosswalk_rows      30722        30722 1.000000
2021_to_2022           all                mapped_rows      30722        30722 1.000000
2021_to_2022           all         across_issuer_rows       1170        30722 0.038083
2022_to_2023           all             crosswalk_rows      43514        43514 1.000000
2022_to_2023           all                mapped_rows      43514        43514 1.000000
2022_to_2023           all         across_issuer_rows       2595        43514 0.059636
2023_to_2024           all             crosswalk_rows      47555        47555 1.000000
2023_to_2024           all                mapped_rows      45937        47555 0.965976
2023_to_2024           all         across_issuer_rows       2699        47555 0.056755

## Sample Alignment With Drake Et Al.

The primary sample uses states with `Pltfrm == HC.gov` in the official OEP state-level PUF for all 2022-2024 years and excludes AK, HI, and NE. Nebraska is available only in the sensitivity output because county-market mapping has not been independently verified.

Step 3 resolved the 2,188 vs 2,159 county discrepancy by applying Drake supplement eTable 3. The 29 raw-sample counties removed are GA/NC counties with no crosswalk data from 2023 to 2024. Legacy SD/VA FIPS exclusions from the supplement were encoded, but they do not affect this 2022-2024 primary sample because those county FIPS are not present in the raw primary sample.

## Known Limitations

- Public OEP files are aggregate county-year data only.
- Individual-level HTE is not possible.
- County-level reenrollment outcomes are not income-stratified.
- Zero-premium status is proxy-based, not exact household net premium.
- Household-specific APTC is not directly observed.
- PY2021 direct QHP Landscape data were unavailable; 2021 uses official Exchange PUF plus Health Plan Finder fallback.
- Some crosswalk-to-current-plan joins fail and are flagged.
- OEP county outcomes contain suppression and missingness.

## Self-Check Results

Validation flags are written by `scripts/04_validate_drake_replication_dataset.py` to `outputs/drake_replication_validation_flags.csv`.

## Recommended Next Step

**A. Proceed to Step 3: descriptive replication and non-causal comparison with Drake-style patterns**, conditional on accepting the benchmark-based zero-premium proxy and reviewing 2021 fallback construction.

Step 3 has now been run. The updated recommendation is **B. Repair Step 2 treatment construction first** before Step 4 formal replication/regression. See `docs/step3_descriptive_replication_report.md`.

## Validation Summary

Validation flags after running `scripts/04_validate_drake_replication_dataset.py`:

- PASS: 15
- WARN: 3
- FAIL: 0

| status | check | metric | threshold | details |
| --- | --- | --- | --- | --- |
| PASS | unique county-year rows | 0 | 0 | Duplicate county-year rows: 0 |
| PASS | expected year coverage | 2022,2023,2024 | 2022,2023,2024 | Years present: [2022, 2023, 2024] |
| PASS | missing county_fips | 0 | 0 | Missing county_fips rows: 0 |
| PASS | county_fips validity | 0 | 0 | Invalid FIPS-like rows: 0 |
| PASS | AK excluded from primary sample |  |  | Primary states among AK/HI/NE: [] |
| PASS | HI excluded from primary sample |  |  | Primary states among AK/HI/NE: [] |
| PASS | NE excluded or explicitly handled |  |  | Primary states among AK/HI/NE: [] |
| PASS | HealthCare.gov state sample applied |  |  | Primary rows not continuously HC.gov: 0 |
| PASS | OEP outcomes constructible for 2022-2024 | 0.026625988073776176 | <0.05 | Maximum missingness across core outcomes: 0.027 |
| PASS | impossible rates | 0 | 0 | Rate values outside [0,1]: 0 |
| PASS | log variables finite when present | 0 | 0 | Nonfinite log values: 0 |
| PASS | binary turnover treatment constructible | 0.9873366013071896 | >=0.95 | Minimum constructibility by year: 0.987. 2022 is expected to be weak if 2021 fallback is incomplete. |
| PASS | across-issuer vs within-issuer distinction constructible | 0.0 | 0 | Across-issuer flag missingness: 0.000 |
| WARN | zero-premium proxy quality | benchmark_based_low_income_proxy,not_constructible | exact preferred | Zero-premium measure types: ['benchmark_based_low_income_proxy', 'not_constructible']. This is proxy-based, not exact. |
| WARN | Step 1 97.4 percent current-year join comparison | 0.9346672111065741 | >=0.95 | Step 1: 0.974; Step 2 2023->2024: 0.935 |
| PASS | sample roughly aligns with Drake et al. |  |  | Primary sample rows: 6564; states: 29 |
| PASS | dataset ready for descriptive replication |  |  | Ready if uniqueness, OEP outcomes, and primary sample checks pass. |
| WARN | dataset ready for causal modeling later |  |  | Step 2 does not authorize causal modeling; 2021 fallback and proxy treatment require review. |
