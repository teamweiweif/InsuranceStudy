# Treatment Construction Notes

The treatment of interest is Medicaid Demonstration entry and the associated
state certification/payment infrastructure, not ordinary SAMHSA CCBHC expansion
grants. The file `data/ccbhc_treatment_panel.parquet` separates:

- selection into the 2024 BSCA cohort;
- federal start-date windows;
- state-specific start dates when public state evidence was found;
- planning-grant status;
- original and CARES-added demonstration states;
- future 2026 cohort states.

State-specific start dates remain unverified for Alabama and New Mexico in this
first build, and low-confidence for Kansas and New Hampshire. Main models
therefore use 2024 selection/post as an early policy shock, while the final
judgment treats actual payment timing as unresolved.

County CCBHC exposure is not constructed. The N-SUMHSS public-use file includes
state but no county, FIPS, address, latitude, or longitude fields. County-level
site timing would require a verified public clinic list with dates or restricted
facility geography.
