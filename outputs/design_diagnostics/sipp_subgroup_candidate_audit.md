# SIPP Subgroup Candidate Audit

## Purpose

This note audits the minimum person/household subgroup feature layer for the second-round churn/unwinding diagnostics.

It checks whether candidate subgroup families are present, interpretable, and low-missing enough across:

- `reference year 2021` from the corrected `2022` release
- `reference year 2022` from the corrected `2023` release
- `reference year 2023` from the merged `2024` release

## Stack Summary

| reference_year | rows | persons | eligible_rows | eligible_weight_sum |
| --- | --- | --- | --- | --- |
| 2021.0 | 486618.0 | 41040.0 | 89010.0 | 745757305.63 |
| 2022.0 | 475772.0 | 40245.0 | 87733.0 | 775530922.51 |
| 2023.0 | 436237.0 | 36901.0 | 81207.0 | 772917077.33 |

## Retained For Round 2

- `age_band`
- `female_group`
- `foreign_born_group`
- `household_child_group`
- `noncitizen_group`
- `pov_band`
- `snap_group`

## Dropped For Round 2

- `disability_group`
- `employed_group`

## Detailed Candidate Table

| feature_family | reference_year | missing_rate_eligible | nonmissing_groups_eligible | retain_for_round2 | top_groups_eligible |
| --- | --- | --- | --- | --- | --- |
| age_band | 2021 | 0.0 | 5 | True | age_0_17; age_26_44; age_45_64; age_65_plus |
| age_band | 2022 | 0.0 | 5 | True | age_0_17; age_26_44; age_45_64; age_65_plus |
| age_band | 2023 | 0.0 | 5 | True | age_0_17; age_45_64; age_26_44; age_65_plus |
| disability_group | 2021 | 0.3322 | 2 | False | no_disability_limit; disability_limit |
| disability_group | 2022 | 0.3121 | 2 | False | no_disability_limit; disability_limit |
| disability_group | 2023 | 0.297 | 2 | False | no_disability_limit; disability_limit |
| employed_group | 2021 | 0.3273 | 2 | False | not_employed; employed |
| employed_group | 2022 | 0.3049 | 2 | False | not_employed; employed |
| employed_group | 2023 | 0.29 | 2 | False | not_employed; employed |
| female_group | 2021 | 0.0 | 2 | True | female; male |
| female_group | 2022 | 0.0 | 2 | True | female; male |
| female_group | 2023 | 0.0 | 2 | True | female; male |
| foreign_born_group | 2021 | 0.0 | 2 | True | us_born; foreign_born |
| foreign_born_group | 2022 | 0.0 | 2 | True | us_born; foreign_born |
| foreign_born_group | 2023 | 0.0 | 2 | True | us_born; foreign_born |
| household_child_group | 2021 | 0.0 | 2 | True | household_has_child; household_no_child |
| household_child_group | 2022 | 0.0 | 2 | True | household_has_child; household_no_child |
| household_child_group | 2023 | 0.0 | 2 | True | household_has_child; household_no_child |
| noncitizen_group | 2021 | 0.0 | 2 | True | citizen; noncitizen |
| noncitizen_group | 2022 | 0.0 | 2 | True | citizen; noncitizen |
| noncitizen_group | 2023 | 0.0 | 2 | True | citizen; noncitizen |
| pov_band | 2021 | 0.0057 | 4 | True | pov_lt_1; pov_1_2; pov_2_4; pov_4_plus |
| pov_band | 2022 | 0.0035 | 4 | True | pov_lt_1; pov_1_2; pov_2_4; pov_4_plus |
| pov_band | 2023 | 0.004 | 4 | True | pov_lt_1; pov_1_2; pov_2_4; pov_4_plus |
| snap_group | 2021 | 0.0016 | 2 | True | snap_no; snap_yes |
| snap_group | 2022 | 0.0009 | 2 | True | snap_no; snap_yes |
| snap_group | 2023 | 0.001 | 2 | True | snap_no; snap_yes |
