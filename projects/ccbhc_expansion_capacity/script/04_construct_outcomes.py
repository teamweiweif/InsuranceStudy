from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline_utils import DATA, REPORT, append_note, save_parquet, write_text


SERVICE_CATEGORIES = {
    "crisis_intervention_per100k": ("directly_targeted", "Crisis intervention services"),
    "moud_any_per100k": ("directly_targeted", "MOUD availability"),
    "integrated_primary_care_per100k": ("directly_targeted", "Integrated primary care"),
    "care_coordination_case_mgmt_per100k": ("directly_targeted", "Care coordination/case management"),
    "sliding_fee_or_low_payment_per100k": ("directly_targeted", "Low-barrier payment access"),
    "suicide_prevention_per100k": ("related", "Suicide prevention"),
    "telehealth_per100k": ("related", "Telehealth"),
    "youth_adolescent_per100k": ("related", "Youth/adolescent services"),
    "sign_language_per100k": ("weakly_targeted", "Sign language services"),
}


def main() -> None:
    policy = pd.read_parquet(DATA / "state_policy_panel.parquet")
    cap = pd.read_parquet(DATA / "state_capacity_panel.parquet")
    state = policy.merge(cap, on=["state", "state_fips", "year"], how="left", suffixes=("", "_cap"))
    state["analysis_post_available"] = (state["year"] == 2024).astype(int)
    state["analysis_window"] = np.where(state["year"].between(2021, 2024), "N-SUMHSS observed", "policy only")
    state["inclusion_flag_main_state_year"] = (
        state["year"].between(2021, 2024)
        & state["facility_count"].notna()
        & (state["original_demo_state"] == 0)
        & (state["cares_added_demo_state"] == 0)
    ).astype(int)
    save_parquet(state, DATA / "analysis_main_state_year.parquet")

    county_policy = pd.read_parquet(DATA / "county_policy_panel.parquet")
    county_cap = pd.read_parquet(DATA / "county_capacity_panel.parquet")
    county = county_policy.merge(
        county_cap,
        on=["county_fips", "state_fips", "year", "NAME"],
        how="left",
        suffixes=("", "_cap"),
    )
    county["inclusion_flag_main_county_year"] = 0
    county["county_analysis_status"] = "not_estimable_no_county_behavioral_health_outcome"
    save_parquet(county, DATA / "analysis_main_county_year.parquet")
    covar_cols = [
        "county_fips", "state_fips", "year", "NAME", "population", "poverty_rate",
        "unemployment_rate", "median_household_income", "source_flags", "missingness_flags",
    ]
    save_parquet(county[[c for c in covar_cols if c in county.columns]].copy(), DATA / "external_covariates_county.parquet")

    facility = pd.read_parquet(DATA / "facility_service_panel.parquet")
    facility = facility.merge(policy, on=["state", "year"], how="left")
    facility["inclusion_flag_facility_year"] = facility["year"].between(2021, 2024).astype(int)
    save_parquet(facility, DATA / "analysis_facility_year.parquet")

    service_rows = []
    for col, (cat, label) in SERVICE_CATEGORIES.items():
        if col not in state.columns:
            continue
        tmp = state[["state", "state_fips", "year", "treated_state_2024", "treated_post_selection_2024", "post_selection_2024", "inclusion_flag_main_state_year", col]].copy()
        tmp = tmp.rename(columns={col: "service_per100k"})
        tmp["service"] = col.replace("_per100k", "")
        tmp["service_category"] = cat
        tmp["service_label"] = label
        tmp["directly_targeted_service"] = int(cat == "directly_targeted")
        service_rows.append(tmp)
    service_panel = pd.concat(service_rows, ignore_index=True)
    service_panel["state_service"] = service_panel["state"] + "_" + service_panel["service"]
    service_panel["year_service"] = service_panel["year"].astype(str) + "_" + service_panel["service"]
    service_panel["treated_post_targeted"] = service_panel["treated_post_selection_2024"] * service_panel["directly_targeted_service"]
    save_parquet(service_panel, DATA / "service_category_state_year.parquet")

    dictionary = """# Data Dictionary

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
"""
    write_text(REPORT / "data_dictionary.md", dictionary)
    append_note("Phase 4: Outcome construction", [
        "Built state-year and state-year-service outcomes from observed N-SUMHSS services.",
        "Classified directly targeted, related, and weakly targeted service lines for DDD.",
        "Kept downstream TEDS-A and mortality out of the main outcome stack because no credible post-treatment window is public yet.",
    ])


if __name__ == "__main__":
    main()
