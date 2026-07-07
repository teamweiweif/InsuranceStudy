from __future__ import annotations

import zipfile

import numpy as np
import pandas as pd

from pipeline_utils import DATA, RAW, append_note, rate_per_100k, save_csv, save_parquet, yes_indicator


SERVICE_SPECS = {
    "mh_facility": ["INMH"],
    "su_facility": ["INSU"],
    "crisis_intervention": ["CRISISTEAM2", "PSYCHON", "PSYCHOFF"],
    "moud_any": ["OTXBUP", "OTXNAL", "OTXFEDOTP", "OPIOIDMAINT", "OPIOIDWDRAW"],
    "buprenorphine": ["OTXBUP"],
    "methadone_otp": ["OTXFEDOTP"],
    "naltrexone": ["OTXNAL"],
    "integrated_primary_care": ["PRIMARYCARE", "SRVCPRIMCARE"],
    "care_coordination_case_mgmt": ["MHCASEMGMT", "MHINTCASEMGMT", "COOCCASEMGMT", "SRVC49"],
    "consumer_peer_family_support": ["MHCONSUMER", "FAMPSYCHED"],
    "sliding_fee_or_low_payment": ["FEESCALE", "PAYASST", "DIRSFS"],
    "suicide_prevention": ["SRVCSUICIDEPREV", "MHSUICIDE"],
    "telehealth": ["TREATTELEMEDINCE", "TELEMEDOPIOID", "TELEMEDOTHSUB"],
    "youth_adolescent": ["ADOLES", "YNGCHLD", "CHILDREN"],
    "sign_language": ["SIGNLANG_SU", "SIGNLANG_MH"],
}


def read_nsumhss_zip(path, year: int) -> pd.DataFrame:
    wanted = {"MPRID", "LOCATIONSTATE"}
    for cols in SERVICE_SPECS.values():
        wanted.update(cols)
    with zipfile.ZipFile(path) as z:
        csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise RuntimeError(f"No CSV in {path}")
        with z.open(csv_names[0]) as f:
            header = pd.read_csv(f, nrows=0).columns.tolist()
        usecols = [c for c in header if c in wanted]
        with z.open(csv_names[0]) as f:
            df = pd.read_csv(f, usecols=usecols, dtype="string", low_memory=False)
    df["year"] = year
    if "LOCATIONSTATE" not in df.columns:
        raise RuntimeError(f"LOCATIONSTATE missing in {path}")
    df = df.rename(columns={"LOCATIONSTATE": "state", "MPRID": "facility_id"})
    df["state"] = df["state"].astype("string").str.strip()
    df["facility_id"] = df.get("facility_id", pd.Series(range(len(df)))).astype("string")
    for out_col, cols in SERVICE_SPECS.items():
        present = [c for c in cols if c in df.columns]
        if not present:
            df[out_col] = np.nan
            continue
        vals = pd.concat([yes_indicator(df[c]) for c in present], axis=1)
        df[out_col] = (vals.max(axis=1, skipna=True) == 1).astype(float)
        df.loc[vals.notna().sum(axis=1) == 0, out_col] = np.nan
    df["source_flags"] = f"N-SUMHSS_{year}_PUF"
    df["missingness_flags"] = np.where(df["state"].isna(), "missing_state", "")
    return df[["facility_id", "state", "year", "source_flags", "missingness_flags"] + list(SERVICE_SPECS.keys())]


def acs_state_population() -> pd.DataFrame:
    acs = pd.read_csv(RAW / "acs_county_covariates_2019_2024.csv", dtype={"state_fips": str, "county_fips": str})
    for col in ["poverty_count", "poverty_universe", "civilian_labor_force", "unemployed_count", "median_household_income"]:
        if col not in acs.columns:
            acs[col] = np.nan
        acs[col] = pd.to_numeric(acs[col], errors="coerce")
    state = acs.groupby(["state_fips", "year"], as_index=False).agg({
        "population": "sum",
        "poverty_count": "sum",
        "poverty_universe": "sum",
        "civilian_labor_force": "sum",
        "unemployed_count": "sum",
        "median_household_income": "median",
    })
    state["poverty_rate"] = np.where(state["poverty_universe"] > 0, state["poverty_count"] / state["poverty_universe"], np.nan)
    state["unemployment_rate"] = np.where(state["civilian_labor_force"] > 0, state["unemployed_count"] / state["civilian_labor_force"], np.nan)
    return state


def main() -> None:
    frames = []
    audit_rows = []
    for year in range(2021, 2025):
        matches = sorted(RAW.glob(f"N-SUMHSS-{year}-DS0001-bndl-data-csv*.zip"))
        if not matches:
            audit_rows.append({"year": year, "status": "missing_zip"})
            continue
        df = read_nsumhss_zip(matches[0], year)
        frames.append(df)
        audit_rows.append({
            "year": year,
            "status": "read",
            "rows": len(df),
            "columns": len(df.columns),
            "states": df["state"].nunique(dropna=True),
            "duplicate_facility_year": int(df.duplicated(["facility_id", "year"]).sum()),
        })
    facility = pd.concat(frames, ignore_index=True)
    save_parquet(facility, DATA / "facility_service_panel.parquet")
    save_csv(pd.DataFrame(audit_rows), DATA / "facility_service_panel_audit.csv")

    state_policy = pd.read_parquet(DATA / "state_policy_panel.parquet")[["state", "state_fips"]].drop_duplicates()
    pop = acs_state_population()
    state_year = facility.groupby(["state", "year"], as_index=False).agg(
        facility_count=("facility_id", "nunique"),
        **{f"{s}_count": (s, "sum") for s in SERVICE_SPECS}
    )
    state_year = state_year.merge(state_policy, on="state", how="left").merge(pop, on=["state_fips", "year"], how="left")
    for col in ["facility_count"] + [f"{s}_count" for s in SERVICE_SPECS]:
        state_year[f"{col.replace('_count', '')}_per100k"] = rate_per_100k(state_year[col], state_year["population"])
    targeted_cols = [
        "crisis_intervention_count", "moud_any_count", "integrated_primary_care_count",
        "care_coordination_case_mgmt_count", "sliding_fee_or_low_payment_count",
    ]
    state_year["targeted_service_count"] = state_year[targeted_cols].sum(axis=1)
    state_year["targeted_services_per100k"] = rate_per_100k(state_year["targeted_service_count"], state_year["population"])
    state_year["source_flags"] = "N-SUMHSS_PUF;ACS"
    state_year["missingness_flags"] = np.where(state_year["population"].isna(), "missing_population", "")
    state_year["inclusion_flag_state_capacity"] = 1
    save_parquet(state_year, DATA / "state_capacity_panel.parquet")

    acs = pd.read_csv(RAW / "acs_county_covariates_2019_2024.csv", dtype={"state_fips": str, "county_fips": str})
    county = acs.copy()
    county["n_sumhss_county_outcomes_available"] = 0
    county["facility_count"] = np.nan
    county["facility_per100k"] = np.nan
    county["source_flags"] = "ACS_only"
    county["missingness_flags"] = "n_sumhss_puf_lacks_county_geography"
    county["inclusion_flag_county_capacity"] = 0
    save_parquet(county, DATA / "county_capacity_panel.parquet")

    append_note("Phase 2: Data audit", [
        "Read N-SUMHSS 2021-2024 PUFs into a facility-year panel using state-level geography only.",
        "Created state-level capacity outcomes and ACS county/state covariates.",
        "Created county capacity files with explicit missing-outcome flags; no county behavioral-health outcomes are fabricated.",
    ])


if __name__ == "__main__":
    main()
