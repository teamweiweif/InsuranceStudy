# Data Dictionary

Clean data files are in `data/`.

- `state_policy_panel.parquet`: state-year policy timing, cohorts, planning grants, original demonstration exclusions, verified/missing start dates.
- `county_policy_panel.parquet`: county-year policy exposure inherited from state policy, with county CCBHC fields flagged as not constructed.
- `facility_service_panel.parquet`: N-SUMHSS facility-year records with state and selected binary service indicators.
- `county_capacity_panel.parquet`: ACS county covariates and explicit flags that N-SUMHSS county behavioral-health outcomes are unavailable in the PUF.
- `ccbhc_treatment_panel.parquet`: copy of the state-year treatment panel for direct treatment construction.
- `external_covariates_county.parquet`: county-year Census covariate extract used by the county analysis shell; in this build the API fallback supplies population and flags unavailable ACS socioeconomic fields.
- `analysis_main_county_year.parquet`: county-year analysis shell; not estimable for capacity outcomes in this build.
- `analysis_main_state_year.parquet`: state-year analysis panel with N-SUMHSS outcomes and policy treatment variables.
- `analysis_facility_year.parquet`: facility-year service panel merged to state policy.
- `service_category_state_year.parquet`: stacked service-category panel for triple-difference tests.

Key outcomes use counts per 100,000 ACS population: facility density, crisis intervention,
MOUD availability, integrated primary care, care coordination/case management, sliding-fee
or low-payment access, suicide prevention, telehealth, youth/adolescent services, and sign
language services as a weakly targeted placebo outcome.
