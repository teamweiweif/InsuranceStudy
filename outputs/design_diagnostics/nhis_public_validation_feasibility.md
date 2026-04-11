# NHIS Public Validation Feasibility

## Purpose

This audit checks whether public-use NHIS adult files can support the planned state-period unwinding validation.

## Result

- Public-use NHIS keeps useful insurance and access variables.
- Public-use NHIS does not expose a state identifier in the adult files audited here.
- That means the current unwinding exposure stack cannot be merged into NHIS at the state-period level without restricted geography.

## What NHIS Still Can Do

- National descriptive validation of coverage or access patterns.
- Region-level descriptive checks, since `REGION` is present.
- Companion descriptive appendix work if the paper later needs another public survey voice.

## Why It Is Not the Main External Check Here

- The selected SIPP design depends on state-month exposure variation.
- Without public state geography, NHIS cannot provide the same kind of late-2023 state-period screen.
- For that reason, HPS remains the only lightweight external screen run in this round.

## Audited Years

| year | state_var_present | region_var_present | month_var_present | quarter_var_present | insurance_access_var_count | validation_use_case |
| --- | --- | --- | --- | --- | --- | --- |
| 2019 | False | True | False | True | 16 | national_or_region_descriptive_only |
| 2020 | False | True | True | True | 16 | national_or_region_descriptive_only |
| 2021 | False | True | True | True | 16 | national_or_region_descriptive_only |
| 2022 | False | True | True | True | 18 | national_or_region_descriptive_only |
| 2023 | False | True | True | True | 18 | national_or_region_descriptive_only |
| 2024 | False | True | True | True | 18 | national_or_region_descriptive_only |
