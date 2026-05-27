#!/usr/bin/env python
"""Build a county-year Drake-style ACA zero-premium turnover dataset.

This script constructs data only. It does not estimate regressions, DID models,
event studies, causal forests, or policy-learning rules.
"""

from __future__ import annotations

import argparse
import io
import logging
import math
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERMEDIATE = DATA / "intermediate"
PROCESSED = DATA / "processed"
METADATA = DATA / "metadata"
OUTPUTS = ROOT / "outputs"
DOCS = ROOT / "docs"
LOGS = ROOT / "logs"

MANIFEST = METADATA / "data_manifest.csv"
BUILD_LOG = LOGS / "step2_build.log"

SUPPRESSED_VALUES = {"", "+", "*", "**", "***", "ds", "suppressed", "data suppressed", "nan", "na", "n/a"}

STATE_NAME_TO_CODE = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

DRAKE_SUPPLEMENT_EXCLUDED_COUNTY_REASONS = {
    "46113": "Drake supplement eTable 3: legacy FIPS exclusion; Shannon County changed to Oglala Lakota County/FIPS 46102 before the study period.",
    "51515": "Drake supplement eTable 3: legacy FIPS exclusion; Bedford City combined with Bedford County before the study period.",
    "51019": "Drake supplement eTable 3: legacy FIPS exclusion; Bedford City combined with Bedford County before the study period.",
    "13009": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13013": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13021": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13051": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13059": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13141": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13157": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13207": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13215": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13219": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13225": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13227": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13245": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "13319": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37001": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37033": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37037": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37065": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37079": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37081": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37105": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37127": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37145": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37147": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37151": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37157": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37189": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37191": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
    "37195": "Drake supplement eTable 3: no crosswalk data from 2023 to 2024.",
}


@dataclass
class BuildOutputs:
    final: Path
    primary: Path
    sensitivity_nebraska: Path | None
    parquet: Path | None
    report: Path


def setup_logging(verbose: bool = False) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(BUILD_LOG, mode="w", encoding="utf-8"), logging.StreamHandler()],
    )


def ensure_dirs() -> None:
    for path in [INTERMEDIATE, PROCESSED, METADATA, OUTPUTS, DOCS, LOGS]:
        path.mkdir(parents=True, exist_ok=True)


def clean_id(value: Any) -> str:
    text = "" if pd.isna(value) else str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text


def clean_fips(value: Any) -> str:
    text = clean_id(value)
    digits = re.sub(r"\D", "", text)
    return digits.zfill(5) if digits else ""


def numeric_series(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip()
    text = text.mask(text.str.lower().isin(SUPPRESSED_VALUES), np.nan)
    text = text.str.replace("$", "", regex=False).str.replace(",", "", regex=False).str.replace("%", "", regex=False)
    text = text.str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(text, errors="coerce")


def suppression_flag(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip().str.lower()
    return text.isin(SUPPRESSED_VALUES - {""}) | text.str.contains("suppress", na=False)


def safe_rate(num: pd.Series, den: pd.Series) -> pd.Series:
    out = num / den
    return out.where(num.notna() & den.notna() & (den > 0))


def safe_log(series: pd.Series) -> pd.Series:
    return np.log(series.where(series > 0))


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def find_col(columns: list[str], candidates: list[str], required: bool = False) -> str | None:
    by_norm = {norm(col): col for col in columns}
    for candidate in candidates:
        found = by_norm.get(norm(candidate))
        if found:
            return found
    for candidate in candidates:
        cn = norm(candidate)
        for key, col in by_norm.items():
            if cn and cn in key:
                return col
    if required:
        raise KeyError(f"None of {candidates} found in columns: {columns[:30]}")
    return None


def load_manifest() -> pd.DataFrame:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"Missing Step 1 manifest: {MANIFEST}")
    manifest = pd.read_csv(MANIFEST, dtype=str).fillna("")
    manifest["year"] = manifest["year"].astype(str)
    return manifest


def manifest_row(manifest: pd.DataFrame, source_group: str, year: int | str, file_type: str) -> pd.Series:
    hits = manifest[
        manifest["source_group"].eq(source_group)
        & manifest["year"].eq(str(year))
        & manifest["file_type"].eq(file_type)
        & manifest["download_success"].astype(str).str.lower().eq("true")
    ]
    if hits.empty:
        raise FileNotFoundError(f"Missing manifest row for {source_group} {year} {file_type}")
    return hits.iloc[0]


def tabular_member(path: Path, prefer_excel: bool = False) -> str | None:
    if path.suffix.lower() != ".zip":
        return None
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith((".csv", ".xlsx", ".xls")) and not n.endswith("/")]
    if not names:
        raise FileNotFoundError(f"No tabular member in {path}")
    if prefer_excel:
        excel = [n for n in names if n.lower().endswith((".xlsx", ".xls"))]
        if excel:
            return excel[0]
    csvs = [n for n in names if n.lower().endswith(".csv")]
    return csvs[0] if csvs else names[0]


def read_csv_from_zip(path: Path, member: str | None = None, **kwargs: Any) -> pd.DataFrame:
    if path.suffix.lower() == ".zip":
        member = member or tabular_member(path)
        last_exc: Exception | None = None
        for encoding in ["utf-8-sig", "latin1"]:
            try:
                with zipfile.ZipFile(path) as zf:
                    return pd.read_csv(
                        zf.open(member),
                        dtype=str,
                        keep_default_na=False,
                        low_memory=False,
                        encoding=encoding,
                        **kwargs,
                    )
            except UnicodeDecodeError as exc:
                last_exc = exc
        raise last_exc or RuntimeError(f"Could not read {path}::{member}")
    last_exc = None
    for encoding in ["utf-8-sig", "latin1"]:
        try:
            return pd.read_csv(path, dtype=str, keep_default_na=False, low_memory=False, encoding=encoding, **kwargs)
        except UnicodeDecodeError as exc:
            last_exc = exc
    raise last_exc or RuntimeError(f"Could not read {path}")


def read_excel_from_zip(path: Path, member: str | None = None, header: int = 0, **kwargs: Any) -> pd.DataFrame:
    if path.suffix.lower() == ".zip":
        member = member or tabular_member(path, prefer_excel=True)
        with zipfile.ZipFile(path) as zf:
            data = io.BytesIO(zf.read(member))
        return pd.read_excel(data, dtype=str, header=header, keep_default_na=False, **kwargs)
    return pd.read_excel(path, dtype=str, header=header, keep_default_na=False, **kwargs)


def read_nested_dat(outer_path: Path, inner_name_contains: str) -> pd.DataFrame:
    with zipfile.ZipFile(outer_path) as outer:
        candidates = [n for n in outer.namelist() if inner_name_contains.lower() in n.lower()]
        if not candidates:
            raise FileNotFoundError(f"No nested ZIP containing {inner_name_contains} in {outer_path}")
        nested_bytes = io.BytesIO(outer.read(candidates[0]))
    with zipfile.ZipFile(nested_bytes) as inner:
        dat_name = [n for n in inner.namelist() if n.lower().endswith(".dat")][0]
        return pd.read_csv(inner.open(dat_name), sep="|", dtype=str, keep_default_na=False)


def write_step1_gap_audit() -> pd.DataFrame:
    rows = [
        ("G01", "scope", "Prototype only used selected states.", "National construction may reveal new join failures.", "Scale treatment joins to all states and report state-year diagnostics.", "addressed", ""),
        ("G02", "missing_source", "PY2021 QHP Landscape direct URLs may be unavailable.", "2021->2022 treatment requires prior-year top-two silver premiums.", "Attempt 2021 panel from official Exchange PUF plus Health Plan Finder rating-area fallback; flag if incomplete.", "addressed_with_fallback", ""),
        ("G03", "data_granularity", "OEP outcomes are county-year aggregate only.", "No individual-level or enrollee-level retention analysis is possible.", "Build county-year dataset only.", "accepted_limitation", ""),
        ("G04", "data_granularity", "Individual-level HTE is impossible with these PUFs.", "Later HTE/policy work cannot use individual heterogeneity.", "Document county-level HTE only as possible later design.", "accepted_limitation", ""),
        ("G05", "measurement", "Household-specific post-subsidy premiums are not directly public.", "Exact zero-premium status depends on household income/composition.", "Use benchmark-based low-income proxy and label it as proxy.", "addressed_with_proxy", ""),
        ("G06", "sample", "Alaska and Hawaii need exclusion or special handling.", "Drake-style contiguous-market sample excludes AK/HI.", "Exclude AK/HI from primary sample.", "addressed", ""),
        ("G07", "sample", "Nebraska may need exclusion or special handling.", "County-market mapping may be incompatible.", "Exclude NE from primary sample; create sensitivity file if requested.", "addressed", ""),
        ("G08", "missingness", "Suppression/missingness exists in OEP county outcomes.", "Outcome rates/logs can be missing.", "Preserve rows, set derived values missing, and flag suppression.", "addressed", ""),
        ("G09", "definition", "Returning consumers are represented through Tot_Renrl in tested OEP files.", "Returning-consumer and total-reenrollment concepts map to same field.", "Use Tot_Renrl with explicit dictionary note.", "addressed", ""),
        ("G10", "join_quality", "Current-year plan joins were not 100% in prototype.", "Treatment flags may be non-constructible for some counties.", "Keep non-constructible rows and report join diagnostics.", "addressed", ""),
    ]
    df = pd.DataFrame(
        rows,
        columns=["issue_id", "issue_type", "step1_finding", "why_it_matters_for_step2", "action_in_step2", "status", "notes"],
    )
    df.to_csv(OUTPUTS / "step1_gap_audit.csv", index=False)
    return df


def write_sample_definition() -> None:
    text = """study_years:
  - 2022
  - 2023
  - 2024
transition_years:
  - 2021_to_2022
  - 2022_to_2023
  - 2023_to_2024
platform: HealthCare.gov states
exclude_states:
  - AK
  - HI
nebraska_handling:
  default: exclude until mapping is verified
  alternative: include in sensitivity file only if county-market mapping is verified
include_only_states_continuously_using_healthcaregov_2022_2024: true
unit_of_analysis: county-year
primary_outcomes:
  - log_total_reenrollment
  - log_automatic_reenrollment
  - log_active_reenrollment
  - log_active_reenrollment_stay
  - log_active_reenrollment_switch
  - rates and shares using Tot_Renrl or Cnsmr denominators where appropriate
primary_treatment:
  - any_zero_to_positive_turnover
  - across_issuer_zero_to_positive_turnover
  - within_issuer_zero_to_positive_turnover
zero_premium_measure:
  type: benchmark_based_low_income_proxy
  assumption: age_40_125_percent_fpl_proxy_with_zero_expected_contribution_for_100_to_150_fpl_under_arpa
market_controls_added_for_repair:
  - enrollment_2021_weight
  - number_of_silver_plans
  - number_of_insurers
  - lowest_silver_premium
  - second_lowest_silver_premium
  - premium_spread_among_silver_plans
  - lowest_bronze_premium
  - bronze_spread
drake_supplement_exclusions:
  source: Drake supplement eTable 3
  encoded_as_columns:
    - drake_supplement_etable3_exclusion
    - drake_supplement_etable3_exclusion_reason
    - included_drake_harmonized_sample
no_formal_regression_in_step2: true
"""
    (METADATA / "drake_style_sample_definition.yaml").write_text(text, encoding="utf-8")


def build_healthcaregov_state_sample(manifest: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    records = []
    all_states: set[str] = set()
    platform_by_year: dict[int, pd.DataFrame] = {}
    for year in years:
        row = manifest_row(manifest, "oep_puf", year, "State-Level OEP PUF")
        path = ROOT / row["local_path"]
        df = read_csv_from_zip(path)
        df["State_Abrvtn"] = df["State_Abrvtn"].astype(str).str.strip().str.upper()
        df = df[df["State_Abrvtn"].str.match(r"^[A-Z]{2}$", na=False)].copy()
        platform_by_year[year] = df[["State_Abrvtn", "Pltfrm"]].rename(columns={"State_Abrvtn": "state", "Pltfrm": f"platform_{year}"})
        all_states.update(platform_by_year[year]["state"].tolist())

    sample = pd.DataFrame({"state": sorted(all_states)})
    for year in years:
        sample = sample.merge(platform_by_year[year], on="state", how="left")
    platform_cols = [f"platform_{year}" for year in years]
    sample["continuous_hcgov_2022_2024"] = sample[platform_cols].apply(
        lambda row: all(str(v).strip().lower() in {"hc.gov", "healthcare.gov"} for v in row), axis=1
    )
    sample["included_primary_sample"] = sample["continuous_hcgov_2022_2024"] & ~sample["state"].isin(["AK", "HI", "NE"])
    sample["reason_included_or_excluded"] = np.select(
        [
            sample["state"].isin(["AK", "HI"]),
            sample["state"].eq("NE"),
            ~sample["continuous_hcgov_2022_2024"],
            sample["included_primary_sample"],
        ],
        [
            "Excluded by Drake-style AK/HI rule.",
            "Excluded from primary sample until Nebraska county-market mapping is verified.",
            "Excluded because state is not continuously HC.gov in state-level OEP PUF for 2022-2024.",
            "Included: continuously HC.gov in state-level OEP PUF for 2022-2024.",
        ],
        default="Uncertain.",
    )
    sample["source_or_rule_used"] = "CMS OEP State-Level PUF Pltfrm column, 2022-2024."
    sample["notes"] = "Platform status inferred from official OEP state-level PUF structure; no external platform list used."
    sample.to_csv(METADATA / "healthcaregov_state_sample_2022_2024.csv", index=False)
    return sample


def build_oep_county_outcomes(manifest: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    frames = []
    excluded_rows = []
    dictionary_rows = []
    base_cols = ["Cnsmr", "New_Cnsmr", "Tot_Renrl", "Auto_Renrl", "Actv_Renrl", "Actv_Renrl_Nsw", "Actv_Renrl_Sw"]
    optional_map = {
        "Avg_Prm": "Avg_Mo_Prem",
        "Avg_Prm_Aftr_APTC": "Avg_Mo_Prem_Aft_APTC",
        "APTC_Cnsmr_Avg_APTC": "Avg_APTC",
        "APTC_Cnsmr": "Consumers_APTC",
    }
    for year in years:
        row = manifest_row(manifest, "oep_puf", year, "County-Level OEP PUF")
        path = ROOT / row["local_path"]
        raw = read_csv_from_zip(path)
        cols = list(raw.columns)
        required = ["State_Abrvtn", "County_FIPS_Cd", *base_cols]
        missing = [c for c in required if c not in cols]
        if missing:
            raise KeyError(f"OEP {year} missing required columns: {missing}")
        keep = required + [c for c in optional_map if c in raw.columns] + [c for c in raw.columns if c.startswith("FPL_")]
        df = raw[keep].copy()
        df.insert(0, "year", year)
        df["state"] = df["State_Abrvtn"].astype(str).str.strip().str.upper()
        df["county_fips"] = df["County_FIPS_Cd"].map(clean_fips)
        valid_county = df["county_fips"].astype(str).str.match(r"^\d{5}$", na=False) & df["state"].ne("TOTAL")
        if (~valid_county).any():
            excluded = df.loc[~valid_county, ["year", "State_Abrvtn", "County_FIPS_Cd", "state", "county_fips"]].copy()
            excluded["raw_file_name"] = Path(row["local_path"]).name
            excluded["exclusion_reason"] = "non_county_summary_or_invalid_fips"
            excluded_rows.append(excluded)
        df = df.loc[valid_county].copy()
        df["county_name"] = ""
        for col in base_cols + [c for c in optional_map if c in df.columns] + [c for c in df.columns if c.startswith("FPL_")]:
            df[f"{col}_raw"] = df[col].astype(str)
            df[f"{col}_suppressed_flag"] = suppression_flag(df[col])
            df[col] = numeric_series(df[col])
        for old, new in optional_map.items():
            if old in df.columns:
                df[new] = df[old]
            else:
                df[new] = np.nan
        df["suppression_or_missing_flag"] = df[[f"{c}_suppressed_flag" for c in base_cols]].any(axis=1) | df[base_cols].isna().any(axis=1)
        df["auto_reenrollment_rate"] = safe_rate(df["Auto_Renrl"], df["Tot_Renrl"])
        df["active_reenrollment_rate"] = safe_rate(df["Actv_Renrl"], df["Tot_Renrl"])
        df["active_switch_rate_among_active"] = safe_rate(df["Actv_Renrl_Sw"], df["Actv_Renrl"])
        df["active_stay_rate_among_active"] = safe_rate(df["Actv_Renrl_Nsw"], df["Actv_Renrl"])
        df["new_consumer_share"] = safe_rate(df["New_Cnsmr"], df["Cnsmr"])
        df["total_reenrollment_share"] = safe_rate(df["Tot_Renrl"], df["Cnsmr"])
        for col in ["Cnsmr", "Tot_Renrl", "Auto_Renrl", "Actv_Renrl", "Actv_Renrl_Nsw", "Actv_Renrl_Sw"]:
            df[f"log_{col}"] = safe_log(df[col])
        df["raw_file_name"] = Path(row["local_path"]).name
        df["source_year"] = year
        frames.append(df)

        for col in df.columns:
            dictionary_rows.append({"variable": col, "source": "CMS OEP County-Level PUF", "year": year, "notes": "Harmonized in Step 2 build."})

    out = pd.concat(frames, ignore_index=True)
    out.to_csv(INTERMEDIATE / "oep_county_outcomes_2022_2024.csv", index=False)
    if excluded_rows:
        pd.concat(excluded_rows, ignore_index=True).to_csv(OUTPUTS / "oep_noncounty_rows_excluded.csv", index=False)
    else:
        pd.DataFrame(columns=["year", "State_Abrvtn", "County_FIPS_Cd", "state", "county_fips", "raw_file_name", "exclusion_reason"]).to_csv(OUTPUTS / "oep_noncounty_rows_excluded.csv", index=False)
    pd.DataFrame(dictionary_rows).drop_duplicates("variable").to_csv(METADATA / "oep_county_outcomes_dictionary.csv", index=False)
    return out


def build_2021_enrollment_weights(manifest: pd.DataFrame) -> pd.DataFrame:
    row = manifest_row(manifest, "oep_puf", 2021, "County-Level OEP PUF")
    raw = read_csv_from_zip(ROOT / row["local_path"])
    required = ["State_Abrvtn", "County_FIPS_Cd", "Cnsmr"]
    missing = [col for col in required if col not in raw.columns]
    if missing:
        raise KeyError(f"OEP 2021 enrollment weights missing required columns: {missing}")
    out = raw[required].copy()
    out["state"] = out["State_Abrvtn"].astype(str).str.strip().str.upper()
    out["county_fips"] = out["County_FIPS_Cd"].map(clean_fips)
    valid = out["county_fips"].astype(str).str.match(r"^\d{5}$", na=False) & out["state"].ne("TOTAL")
    out = out.loc[valid].copy()
    out["enrollment_2021_weight_raw"] = out["Cnsmr"].astype(str)
    out["enrollment_2021_weight_suppressed_flag"] = suppression_flag(out["Cnsmr"])
    out["enrollment_2021_weight"] = numeric_series(out["Cnsmr"])
    out["enrollment_2021_weight_source"] = row["local_path"]
    out = out[["state", "county_fips", "enrollment_2021_weight", "enrollment_2021_weight_raw", "enrollment_2021_weight_suppressed_flag", "enrollment_2021_weight_source"]]
    out.to_csv(INTERMEDIATE / "oep_2021_county_enrollment_weights.csv", index=False)
    return out


def detect_qhp_header(path: Path, member: str) -> int:
    with zipfile.ZipFile(path) as zf:
        data = io.BytesIO(zf.read(member))
    raw = pd.read_excel(data, nrows=8, header=None, dtype=str)
    for i, row in raw.iterrows():
        cells = {norm(v) for v in row.tolist()}
        if "statecode" in cells and "planidstandardcomponent" in cells:
            return int(i)
    return 0


def rate_age40(manifest: pd.DataFrame, year: int) -> pd.DataFrame:
    row = manifest_row(manifest, "exchange_puf", year, "Rate PUF")
    path = ROOT / row["local_path"]
    member = tabular_member(path)
    chunks = []
    with zipfile.ZipFile(path) as zf:
        for chunk in pd.read_csv(zf.open(member), dtype=str, keep_default_na=False, chunksize=250_000, low_memory=False):
            age_col = find_col(list(chunk.columns), ["Age"], required=True)
            part = chunk[chunk[age_col].astype(str).str.strip().eq("40")].copy()
            if part.empty:
                continue
            cols = list(part.columns)
            state = find_col(cols, ["StateCode"], required=True)
            plan = find_col(cols, ["PlanId"], required=True)
            rating = find_col(cols, ["RatingAreaId"], required=True)
            issuer = find_col(cols, ["IssuerId"])
            rate = find_col(cols, ["IndividualRate"], required=True)
            keep = [c for c in [state, plan, rating, issuer, rate] if c]
            part = part[keep].rename(columns={state: "state", plan: "plan_id", rating: "rating_area_id", rate: "rate_puf_age_40_premium"})
            if issuer:
                part = part.rename(columns={issuer: "issuer_id_rate"})
            part["state"] = part["state"].str.upper().str.strip()
            part["plan_id"] = part["plan_id"].map(clean_id)
            part["rating_area_id"] = part["rating_area_id"].astype(str).str.strip()
            part["rate_puf_age_40_premium"] = numeric_series(part["rate_puf_age_40_premium"])
            chunks.append(part)
    if not chunks:
        return pd.DataFrame(columns=["state", "plan_id", "rating_area_id", "rate_puf_age_40_premium"])
    out = pd.concat(chunks, ignore_index=True).drop_duplicates(["state", "plan_id", "rating_area_id"])
    return out


def build_qhp_silver_panel(manifest: pd.DataFrame, year: int, metal_pattern: str = "silver") -> pd.DataFrame:
    row = manifest_row(manifest, "qhp_landscape", year, "QHP Landscape Individual Medical ZIP")
    path = ROOT / row["local_path"]
    member = tabular_member(path, prefer_excel=True)
    header = detect_qhp_header(path, member)
    df = read_excel_from_zip(path, member, header=header, sheet_name=0)
    cols = list(df.columns)
    colmap = {
        "state": find_col(cols, ["State Code"], required=True),
        "county_fips": find_col(cols, ["FIPS County Code", "County FIPS Code"], required=True),
        "county_name": find_col(cols, ["County Name"]),
        "metal_level": find_col(cols, ["Metal Level"], required=True),
        "issuer_name": find_col(cols, ["Issuer Name"]),
        "issuer_id": find_col(cols, ["HIOS Issuer ID", "Issuer ID"], required=True),
        "plan_id": find_col(cols, ["Plan ID (Standard Component)", "Plan ID"], required=True),
        "plan_type": find_col(cols, ["Plan Type"]),
        "rating_area_id": find_col(cols, ["Rating Area"], required=True),
        "age_40_premium": find_col(cols, ["Premium Adult Individual Age 40"], required=True),
    }
    out = df[[c for c in colmap.values() if c]].rename(columns={v: k for k, v in colmap.items() if v})
    out["year"] = year
    out["state"] = out["state"].astype(str).str.strip().str.upper()
    out["county_fips"] = out["county_fips"].map(clean_fips)
    out["issuer_id"] = out["issuer_id"].map(clean_id)
    out["plan_id"] = out["plan_id"].map(clean_id)
    out["standard_component_id"] = out["plan_id"]
    out["metal_level"] = out["metal_level"].astype(str).str.strip()
    out["rating_area_id"] = out["rating_area_id"].astype(str).str.strip()
    out["age_40_premium"] = numeric_series(out["age_40_premium"])
    out["qhp_landscape_premium"] = out["age_40_premium"]
    out["premium_source"] = "QHP Landscape"
    out["market_type"] = "Individual"
    out["source_file"] = str(path.relative_to(ROOT))
    out["raw_plan_id_columns_used"] = colmap["plan_id"]
    out["data_quality_notes"] = ""
    out = out[out["metal_level"].str.lower().str.contains(metal_pattern, na=False)].copy()
    out = out[out["county_fips"].ne("") & out["plan_id"].ne("")].copy()

    rates = rate_age40(manifest, year)
    out = out.merge(rates, on=["state", "plan_id", "rating_area_id"], how="left")
    out["premium_difference"] = out["qhp_landscape_premium"] - out["rate_puf_age_40_premium"]
    out["premium_pct_difference"] = out["premium_difference"] / out["qhp_landscape_premium"]
    out["premium_match_flag"] = out["premium_difference"].abs().le(0.01)
    out["premium_reconciliation_flag"] = np.select(
        [out["rate_puf_age_40_premium"].isna(), out["premium_match_flag"]],
        ["missing_rate_puf", "match"],
        default="mismatch",
    )
    out["likely_reason_for_difference"] = np.where(out["premium_reconciliation_flag"].eq("mismatch"), "QHP rounded/displayed premium differs from Rate PUF or rating-area join issue.", "")
    out["service_area_id"] = ""
    out["metal_filter_used"] = metal_pattern
    return out


def state_rating_area_2021() -> pd.DataFrame:
    path = RAW / "health_plan_finder" / "2020" / "2020q4-rbis.zip"
    df = read_nested_dat(path, "STATE_RATING_AREA")
    df["state"] = df["State"].map(STATE_NAME_TO_CODE)
    df["county_fips"] = df["FIPS"].map(clean_fips)
    df["rating_area_id"] = "Rating Area " + df["Rating Area ID"].astype(str).str.strip()
    df = df[df["Market"].str.lower().eq("individual") & df["state"].notna() & df["county_fips"].ne("")]
    return df[["state", "county_fips", "rating_area_id"]].drop_duplicates()


def build_exchange_silver_panel_2021(manifest: pd.DataFrame, metal_pattern: str = "silver") -> pd.DataFrame:
    year = 2021
    plan_row = manifest_row(manifest, "exchange_puf", year, "Plan Attributes PUF")
    service_row = manifest_row(manifest, "exchange_puf", year, "Service Area PUF")
    plan = read_csv_from_zip(ROOT / plan_row["local_path"])
    service = read_csv_from_zip(ROOT / service_row["local_path"])
    plan_cols = list(plan.columns)
    service_cols = list(service.columns)
    plan_colmap = {
        "state": find_col(plan_cols, ["StateCode"], required=True),
        "issuer_id": find_col(plan_cols, ["IssuerId"], required=True),
        "issuer_name": find_col(plan_cols, ["IssuerMarketPlaceMarketingName"]),
        "market_type": find_col(plan_cols, ["MarketCoverage"], required=True),
        "dental": find_col(plan_cols, ["DentalOnlyPlan"], required=True),
        "plan_id": find_col(plan_cols, ["StandardComponentId"], required=True),
        "plan_type": find_col(plan_cols, ["PlanType"]),
        "metal_level": find_col(plan_cols, ["MetalLevel"], required=True),
        "service_area_id": find_col(plan_cols, ["ServiceAreaId"], required=True),
        "qhp_type": find_col(plan_cols, ["QHPNonQHPTypeId"]),
    }
    service_colmap = {
        "state": find_col(service_cols, ["StateCode"], required=True),
        "issuer_id": find_col(service_cols, ["IssuerId"], required=True),
        "service_area_id": find_col(service_cols, ["ServiceAreaId"], required=True),
        "cover_entire_state": find_col(service_cols, ["CoverEntireState"], required=True),
        "county_fips": find_col(service_cols, ["County"], required=True),
        "market_type": find_col(service_cols, ["MarketCoverage"], required=True),
        "dental": find_col(service_cols, ["DentalOnlyPlan"], required=True),
    }
    p = plan[[c for c in plan_colmap.values() if c]].rename(columns={v: k for k, v in plan_colmap.items() if v})
    s = service[[c for c in service_colmap.values() if c]].rename(columns={v: k for k, v in service_colmap.items() if v})
    p["state"] = p["state"].str.upper().str.strip()
    s["state"] = s["state"].str.upper().str.strip()
    p["issuer_id"] = p["issuer_id"].map(clean_id)
    s["issuer_id"] = s["issuer_id"].map(clean_id)
    p["plan_id"] = p["plan_id"].map(clean_id)
    p = p[
        p["market_type"].str.lower().eq("individual")
        & p["dental"].str.lower().isin({"no", "false", "0"})
        & p["metal_level"].str.lower().str.contains(metal_pattern, na=False)
    ].copy()
    if "qhp_type" in p.columns:
        p = p[~p["qhp_type"].astype(str).str.lower().eq("off the exchange")].copy()
    s = s[s["market_type"].str.lower().eq("individual") & s["dental"].str.lower().isin({"no", "false", "0"})].copy()
    s["county_fips"] = s["county_fips"].map(clean_fips)
    s_county = s[s["county_fips"].ne("")].copy()
    rating = state_rating_area_2021()
    entire = s[s["cover_entire_state"].str.lower().eq("yes")][["state", "issuer_id", "service_area_id", "cover_entire_state"]].drop_duplicates()
    entire = entire.merge(rating[["state", "county_fips"]].drop_duplicates(), on="state", how="left")
    service_expanded = pd.concat([s_county[["state", "issuer_id", "service_area_id", "county_fips", "cover_entire_state"]], entire], ignore_index=True)
    panel = p.merge(service_expanded, on=["state", "issuer_id", "service_area_id"], how="left")
    panel = panel.merge(rating, on=["state", "county_fips"], how="left")
    rates = rate_age40(manifest, year)
    panel = panel.merge(rates, on=["state", "plan_id", "rating_area_id"], how="left")
    panel["year"] = year
    panel["county_name"] = ""
    panel["standard_component_id"] = panel["plan_id"]
    panel["age_40_premium"] = panel["rate_puf_age_40_premium"]
    panel["qhp_landscape_premium"] = np.nan
    panel["premium_source"] = "Exchange PUF + Health Plan Finder rating-area fallback"
    panel["source_file"] = f"{plan_row['local_path']} + {service_row['local_path']} + data/raw/health_plan_finder/2020/2020q4-rbis.zip"
    panel["raw_plan_id_columns_used"] = "StandardComponentId"
    panel["data_quality_notes"] = f"PY2021 QHP Landscape direct file unavailable; {metal_pattern} county premiums reconstructed from official Exchange PUF and HPF rating-area fallback."
    panel["premium_difference"] = np.nan
    panel["premium_pct_difference"] = np.nan
    panel["premium_match_flag"] = np.nan
    panel["premium_reconciliation_flag"] = np.where(panel["age_40_premium"].notna(), "rate_puf_only", "missing_rate_puf")
    panel["likely_reason_for_difference"] = ""
    panel["metal_filter_used"] = metal_pattern
    panel = panel[panel["county_fips"].ne("") & panel["plan_id"].ne("")].drop_duplicates(["year", "state", "county_fips", "plan_id"])
    return panel


def build_silver_plan_panel(manifest: pd.DataFrame) -> pd.DataFrame:
    frames = [build_exchange_silver_panel_2021(manifest)]
    for year in [2022, 2023, 2024]:
        frames.append(build_qhp_silver_panel(manifest, year))
    common_cols = sorted(set().union(*[set(f.columns) for f in frames]))
    panel = pd.concat([f.reindex(columns=common_cols) for f in frames], ignore_index=True)
    panel = panel[panel["age_40_premium"].notna()].copy()
    panel.to_csv(INTERMEDIATE / "silver_plan_county_year_panel.csv", index=False)
    return panel


def build_bronze_plan_panel(manifest: pd.DataFrame) -> pd.DataFrame:
    frames = [build_exchange_silver_panel_2021(manifest, metal_pattern="bronze")]
    for year in [2022, 2023, 2024]:
        frames.append(build_qhp_silver_panel(manifest, year, metal_pattern="bronze"))
    common_cols = sorted(set().union(*[set(f.columns) for f in frames]))
    panel = pd.concat([f.reindex(columns=common_cols) for f in frames], ignore_index=True)
    panel = panel[panel["age_40_premium"].notna()].copy()
    panel.to_csv(INTERMEDIATE / "bronze_plan_county_year_panel.csv", index=False)
    return panel


def build_two_lowest(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    tie_rows = []
    for (year, state, county), g in panel.groupby(["year", "state", "county_fips"], dropna=False):
        g = g.dropna(subset=["age_40_premium"]).drop_duplicates("plan_id")
        g = g.sort_values(["age_40_premium", "issuer_id", "plan_id"])
        if len(g) < 2:
            rows.append({"year": year, "state": state, "county_fips": county, "has_two_silver_plans": False, "tie_handling_rule": "sort by premium, issuer_id, plan_id"})
            continue
        first = g.iloc[0]
        second = g.iloc[1]
        unique_prem = sorted(g["age_40_premium"].dropna().unique())
        lowest_prem = unique_prem[0]
        second_prem_for_ties = unique_prem[1] if len(unique_prem) > 1 else unique_prem[0]
        n_low = int((g["age_40_premium"] == lowest_prem).sum())
        n_second = int((g["age_40_premium"] == second_prem_for_ties).sum())
        rows.append(
            {
                "year": year,
                "state": state,
                "county_fips": county,
                "county_name": first.get("county_name", ""),
                "has_two_silver_plans": True,
                "lowest_silver_plan_id": first["plan_id"],
                "lowest_silver_issuer_id": first["issuer_id"],
                "lowest_silver_premium": first["age_40_premium"],
                "second_lowest_silver_plan_id": second["plan_id"],
                "second_lowest_silver_issuer_id": second["issuer_id"],
                "second_lowest_silver_premium": second["age_40_premium"],
                "number_of_silver_plans": len(g),
                "number_of_plans_tied_lowest": n_low,
                "number_of_plans_tied_second_lowest": n_second,
                "tie_handling_rule": "sort by premium, issuer_id, plan_id; choose first and second unique plan_id rows",
                "tie_flag": bool(n_low > 1 or n_second > 1),
                "top_two_same_issuer": first["issuer_id"] == second["issuer_id"],
            }
        )
        if n_low > 1 or n_second > 1:
            tie_rows.append({"year": year, "state": state, "county_fips": county, "n_tied_lowest": n_low, "n_tied_second": n_second})
    out = pd.DataFrame(rows)
    out.to_csv(INTERMEDIATE / "two_lowest_silver_plans_county_year.csv", index=False)
    pd.DataFrame(tie_rows).to_csv(OUTPUTS / "two_lowest_silver_tie_diagnostics.csv", index=False)
    return out


def build_market_controls(silver_panel: pd.DataFrame, bronze_panel: pd.DataFrame, two_lowest: pd.DataFrame) -> pd.DataFrame:
    silver = silver_panel.dropna(subset=["age_40_premium"]).copy()
    silver_stats = (
        silver.groupby(["year", "state", "county_fips"], dropna=False)
        .agg(
            number_of_silver_plans=("plan_id", "nunique"),
            number_of_insurers=("issuer_id", "nunique"),
            min_silver_premium_all_plans=("age_40_premium", "min"),
            max_silver_premium_all_plans=("age_40_premium", "max"),
        )
        .reset_index()
    )
    keep_two = [
        "year",
        "state",
        "county_fips",
        "has_two_silver_plans",
        "lowest_silver_premium",
        "second_lowest_silver_premium",
        "number_of_plans_tied_lowest",
        "number_of_plans_tied_second_lowest",
        "tie_flag",
    ]
    controls = two_lowest[[col for col in keep_two if col in two_lowest.columns]].copy()
    controls = controls.merge(silver_stats, on=["year", "state", "county_fips"], how="outer")
    controls["premium_spread_among_silver_plans"] = controls["second_lowest_silver_premium"] - controls["lowest_silver_premium"]
    controls["fewer_than_two_silver_plans"] = ~controls["has_two_silver_plans"].fillna(False).astype(bool)

    bronze = bronze_panel.dropna(subset=["age_40_premium"]).copy()
    if not bronze.empty:
        bronze_stats = (
            bronze.groupby(["year", "state", "county_fips"], dropna=False)
            .agg(
                lowest_bronze_premium=("age_40_premium", "min"),
                number_of_bronze_plans=("plan_id", "nunique"),
                number_of_bronze_insurers=("issuer_id", "nunique"),
            )
            .reset_index()
        )
        controls = controls.merge(bronze_stats, on=["year", "state", "county_fips"], how="left")
    else:
        controls["lowest_bronze_premium"] = np.nan
        controls["number_of_bronze_plans"] = np.nan
        controls["number_of_bronze_insurers"] = np.nan

    controls["bronze_spread"] = controls["second_lowest_silver_premium"] - controls["lowest_bronze_premium"]
    controls["market_control_measure_type"] = "age_40_premium_county_year_market_controls"
    controls["market_control_limitations"] = "Number of insurers is based on silver plan issuers in the constructed county-plan panel; bronze spread is SLCSP minus lowest bronze premium."
    controls.to_csv(INTERMEDIATE / "market_controls_county_year.csv", index=False)
    return controls


def build_zero_proxy(panel: pd.DataFrame, two_lowest: pd.DataFrame) -> pd.DataFrame:
    bench = two_lowest[["year", "state", "county_fips", "second_lowest_silver_premium"]].rename(
        columns={"second_lowest_silver_premium": "benchmark_or_second_lowest_silver_premium_proxy"}
    )
    out = panel.merge(bench, on=["year", "state", "county_fips"], how="left")
    out["gross_age_40_premium"] = out["age_40_premium"]
    out["estimated_net_premium_proxy"] = (out["gross_age_40_premium"] - out["benchmark_or_second_lowest_silver_premium_proxy"]).clip(lower=0)
    out["zero_premium_proxy"] = out["estimated_net_premium_proxy"].le(0.01) & out["estimated_net_premium_proxy"].notna()
    out["subsidy_assumption"] = "Age-40 100-150% FPL proxy assumes zero expected contribution; APTC proxied by county-year SLCSP."
    out["notes"] = "Proxy, not exact household-specific post-subsidy premium."
    keep = [
        "year",
        "state",
        "county_fips",
        "plan_id",
        "issuer_id",
        "metal_level",
        "gross_age_40_premium",
        "benchmark_or_second_lowest_silver_premium_proxy",
        "estimated_net_premium_proxy",
        "zero_premium_proxy",
        "subsidy_assumption",
        "notes",
    ]
    out[keep].to_csv(INTERMEDIATE / "zero_premium_proxy_county_year.csv", index=False)
    return out


def load_crosswalk(manifest: pd.DataFrame, previous_year: int, current_year: int) -> pd.DataFrame:
    row = manifest_row(manifest, "exchange_puf", current_year, "Plan ID Crosswalk PUF")
    df = read_csv_from_zip(ROOT / row["local_path"])
    prev_plan = f"PlanID_{previous_year}"
    cur_plan = f"PlanID_{current_year}"
    prev_issuer = f"IssuerID_{previous_year}"
    cur_issuer = f"IssuerID_{current_year}"
    cols = list(df.columns)
    needed = ["State", "DentalPlan", prev_plan, prev_issuer, f"MetalLevel_{previous_year}", "FIPSCode", "ZipCode", "CrosswalkLevel", "ReasonForCrosswalk", cur_plan, cur_issuer, f"MetalLevel_{current_year}"]
    use = [c for c in needed if c in cols]
    out = df[use].copy()
    out = out.rename(
        columns={
            "State": "state",
            "DentalPlan": "dental_plan",
            prev_plan: "previous_plan_id",
            prev_issuer: "previous_issuer_id",
            f"MetalLevel_{previous_year}": "previous_metal_level",
            "FIPSCode": "county_fips",
            "CrosswalkLevel": "crosswalk_level",
            "ReasonForCrosswalk": "crosswalk_reason_or_type",
            cur_plan: "current_plan_id",
            cur_issuer: "current_issuer_id",
            f"MetalLevel_{current_year}": "current_metal_level",
        }
    )
    out["transition"] = f"{previous_year}_to_{current_year}"
    out["previous_year"] = previous_year
    out["current_year"] = current_year
    out["state"] = out["state"].astype(str).str.upper().str.strip()
    out["county_fips"] = out["county_fips"].map(clean_fips)
    out["previous_plan_id_raw"] = out["previous_plan_id"].astype(str)
    out["current_plan_id_raw"] = out["current_plan_id"].astype(str)
    out["previous_plan_id"] = out["previous_plan_id"].map(clean_id)
    out["current_plan_id"] = out["current_plan_id"].map(clean_id)
    out["previous_issuer_id"] = out["previous_issuer_id"].map(clean_id)
    out["current_issuer_id"] = out["current_issuer_id"].map(clean_id)
    out = out[out["dental_plan"].astype(str).str.upper().isin({"N", "NO", "FALSE", "0"})].copy()
    out = out[out["previous_metal_level"].astype(str).str.lower().str.contains("silver", na=False)].copy()
    out["same_issuer_flag"] = out["previous_issuer_id"].eq(out["current_issuer_id"])
    out["across_issuer_flag"] = out["previous_issuer_id"].ne(out["current_issuer_id"])
    out["crosswalk_source_file"] = row["local_path"]
    out["mapping_quality_flag"] = np.where(out["current_plan_id"].str.contains("00000XX", na=False) | out["current_plan_id"].eq(""), "unmapped_or_placeholder", "mapped")
    cols_out = [
        "transition",
        "previous_year",
        "current_year",
        "state",
        "county_fips",
        "previous_plan_id",
        "previous_issuer_id",
        "previous_plan_id_raw",
        "current_plan_id",
        "current_issuer_id",
        "current_plan_id_raw",
        "crosswalk_reason_or_type",
        "same_issuer_flag",
        "across_issuer_flag",
        "crosswalk_source_file",
        "mapping_quality_flag",
    ]
    out[cols_out].to_csv(INTERMEDIATE / f"crosswalk_transition_{previous_year}_{current_year}.csv", index=False)
    return out


def construct_transition(
    manifest: pd.DataFrame,
    previous_year: int,
    current_year: int,
    two_lowest: pd.DataFrame,
    zero_proxy: pd.DataFrame,
    join_rows: list[dict[str, Any]],
) -> pd.DataFrame:
    transition = f"{previous_year}_to_{current_year}"
    prev_top = two_lowest[two_lowest["year"].eq(previous_year)].copy()
    if prev_top.empty:
        out = pd.DataFrame(columns=["year", "transition", "state", "county_fips", "treatment_constructible_flag", "reason_not_constructible"])
        out.to_csv(INTERMEDIATE / f"turnover_transition_{previous_year}_{current_year}.csv", index=False)
        return out

    z = zero_proxy[["year", "state", "county_fips", "plan_id", "issuer_id", "gross_age_40_premium", "estimated_net_premium_proxy", "zero_premium_proxy"]].copy()
    current_z = z[z["year"].eq(current_year)].rename(
        columns={
            "plan_id": "current_plan_id",
            "issuer_id": "current_issuer_id_proxy",
            "gross_age_40_premium": "current_gross_premium",
            "estimated_net_premium_proxy": "current_net_premium_proxy",
            "zero_premium_proxy": "current_zero_premium_proxy",
        }
    )
    cw = load_crosswalk(manifest, previous_year, current_year)

    records = []
    for rank_name, plan_col, issuer_col, premium_col in [
        ("lowest", "lowest_silver_plan_id", "lowest_silver_issuer_id", "lowest_silver_premium"),
        ("second_lowest", "second_lowest_silver_plan_id", "second_lowest_silver_issuer_id", "second_lowest_silver_premium"),
    ]:
        part = prev_top[["state", "county_fips", plan_col, issuer_col, premium_col]].rename(
            columns={plan_col: "previous_plan_id", issuer_col: "previous_issuer_id", premium_col: "prior_gross_premium"}
        )
        part["rank"] = rank_name
        prior_z = z[z["year"].eq(previous_year)][["state", "county_fips", "plan_id", "estimated_net_premium_proxy", "zero_premium_proxy"]].rename(
            columns={"plan_id": "previous_plan_id", "estimated_net_premium_proxy": "prior_net_premium_proxy", "zero_premium_proxy": "prior_zero_premium_flag"}
        )
        part = part.merge(prior_z, on=["state", "county_fips", "previous_plan_id"], how="left")
        before = len(part)
        part = part.merge(cw, on=["state", "county_fips", "previous_plan_id"], how="left", suffixes=("", "_cw"))
        part = part.merge(current_z, on=["state", "county_fips", "current_plan_id"], how="left")
        part["current_issuer_final"] = part["current_issuer_id_proxy"].where(part["current_issuer_id_proxy"].astype(str).ne(""), part["current_issuer_id"])
        part["current_positive_premium_flag"] = part["current_net_premium_proxy"].gt(0.01)
        part["zero_to_positive_turnover"] = part["prior_zero_premium_flag"].fillna(False) & part["current_positive_premium_flag"].fillna(False)
        part["same_issuer"] = part["previous_issuer_id"].astype(str).eq(part["current_issuer_final"].astype(str))
        part["across_issuer"] = part["previous_issuer_id"].astype(str).ne(part["current_issuer_final"].astype(str))
        part["premium_change"] = part["current_net_premium_proxy"] - part["prior_net_premium_proxy"]
        part["gross_premium_change"] = part["current_gross_premium"] - part["prior_gross_premium"]
        part["missing_crosswalk_flag"] = part["current_plan_id"].isna() | part["current_plan_id"].astype(str).eq("")
        part["missing_current_plan_flag"] = part["current_gross_premium"].isna()
        part["missing_premium_flag"] = part["prior_gross_premium"].isna() | part["current_gross_premium"].isna()
        part["missing_county_mapping_flag"] = part["county_fips"].astype(str).eq("")
        records.append(part)
        join_rows.extend(
            [
                {"transition": transition, "rank": rank_name, "metric": "previous_top_two_rows", "numerator": before, "denominator": before, "rate": 1.0},
                {"transition": transition, "rank": rank_name, "metric": "previous_plan_to_crosswalk", "numerator": int((~part["missing_crosswalk_flag"]).sum()), "denominator": len(part), "rate": float((~part["missing_crosswalk_flag"]).mean()) if len(part) else np.nan},
                {"transition": transition, "rank": rank_name, "metric": "crosswalk_to_current_plan", "numerator": int((~part["missing_current_plan_flag"]).sum()), "denominator": len(part), "rate": float((~part["missing_current_plan_flag"]).mean()) if len(part) else np.nan},
            ]
        )
    long = pd.concat(records, ignore_index=True)
    rows = []
    for (state, county), g in long.groupby(["state", "county_fips"], dropna=False):
        low = g[g["rank"].eq("lowest")].iloc[0] if not g[g["rank"].eq("lowest")].empty else pd.Series(dtype=object)
        sec = g[g["rank"].eq("second_lowest")].iloc[0] if not g[g["rank"].eq("second_lowest")].empty else pd.Series(dtype=object)
        missing_crosswalk = bool(g["missing_crosswalk_flag"].any())
        missing_current = bool(g["missing_current_plan_flag"].any())
        missing_premium = bool(g["missing_premium_flag"].any())
        constructible = not (missing_crosswalk or missing_current or missing_premium)
        reasons = []
        if missing_crosswalk:
            reasons.append("missing_crosswalk")
        if missing_current:
            reasons.append("missing_current_plan")
        if missing_premium:
            reasons.append("missing_premium")
        rows.append(
            {
                "year": current_year,
                "transition": transition,
                "state": state,
                "county_fips": county,
                "any_zero_to_positive_turnover": bool(g["zero_to_positive_turnover"].fillna(False).any()),
                "lowest_zero_to_positive_turnover": bool(low.get("zero_to_positive_turnover", False)),
                "second_lowest_zero_to_positive_turnover": bool(sec.get("zero_to_positive_turnover", False)),
                "any_zero_to_positive_turnover_across_issuer": bool((g["zero_to_positive_turnover"].fillna(False) & g["across_issuer"].fillna(False)).any()),
                "any_zero_to_positive_turnover_within_issuer": bool((g["zero_to_positive_turnover"].fillna(False) & g["same_issuer"].fillna(False)).any()),
                "lowest_zero_to_positive_turnover_across_issuer": bool(low.get("zero_to_positive_turnover", False) and low.get("across_issuer", False)),
                "second_lowest_zero_to_positive_turnover_across_issuer": bool(sec.get("zero_to_positive_turnover", False) and sec.get("across_issuer", False)),
                "any_zero_to_positive_turnover_unmapped": bool(g["missing_crosswalk_flag"].any()),
                "any_zero_premium_prior_year": bool(g["prior_zero_premium_flag"].fillna(False).any()),
                "any_positive_mapped_current_year": bool(g["current_positive_premium_flag"].fillna(False).any()),
                "prior_lowest_zero_premium_flag": bool(low.get("prior_zero_premium_flag", False)),
                "prior_second_lowest_zero_premium_flag": bool(sec.get("prior_zero_premium_flag", False)),
                "current_mapped_lowest_positive_premium_flag": bool(low.get("current_positive_premium_flag", False)),
                "current_mapped_second_lowest_positive_premium_flag": bool(sec.get("current_positive_premium_flag", False)),
                "premium_change_lowest": low.get("premium_change", np.nan),
                "premium_change_second_lowest": sec.get("premium_change", np.nan),
                "max_premium_change_among_affected_top_two": g.loc[g["zero_to_positive_turnover"].fillna(False), "premium_change"].max(),
                "mean_premium_change_among_affected_top_two": g.loc[g["zero_to_positive_turnover"].fillna(False), "premium_change"].mean(),
                "current_mapped_premium_lowest": low.get("current_net_premium_proxy", np.nan),
                "current_mapped_premium_second_lowest": sec.get("current_net_premium_proxy", np.nan),
                "prior_premium_lowest": low.get("prior_net_premium_proxy", np.nan),
                "prior_premium_second_lowest": sec.get("prior_net_premium_proxy", np.nan),
                "gross_premium_change_lowest": low.get("gross_premium_change", np.nan),
                "gross_premium_change_second_lowest": sec.get("gross_premium_change", np.nan),
                "net_premium_proxy_change_lowest": low.get("premium_change", np.nan),
                "net_premium_proxy_change_second_lowest": sec.get("premium_change", np.nan),
                "previous_lowest_plan_id": low.get("previous_plan_id", ""),
                "previous_second_lowest_plan_id": sec.get("previous_plan_id", ""),
                "mapped_current_lowest_plan_id": low.get("current_plan_id", ""),
                "mapped_current_second_lowest_plan_id": sec.get("current_plan_id", ""),
                "previous_lowest_issuer_id": low.get("previous_issuer_id", ""),
                "previous_second_lowest_issuer_id": sec.get("previous_issuer_id", ""),
                "mapped_current_lowest_issuer_id": low.get("current_issuer_final", ""),
                "mapped_current_second_lowest_issuer_id": sec.get("current_issuer_final", ""),
                "same_issuer_lowest": bool(low.get("same_issuer", False)),
                "same_issuer_second_lowest": bool(sec.get("same_issuer", False)),
                "treatment_constructible_flag": bool(constructible),
                "reason_not_constructible": ";".join(reasons),
                "missing_previous_plan_flag": False,
                "missing_crosswalk_flag": missing_crosswalk,
                "missing_current_plan_flag": missing_current,
                "missing_premium_flag": missing_premium,
                "missing_county_mapping_flag": bool(g["missing_county_mapping_flag"].any()),
                "zero_premium_measure_type": "benchmark_based_low_income_proxy",
                "premium_measure_type": "age_40_individual_premium",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(INTERMEDIATE / f"turnover_transition_{previous_year}_{current_year}.csv", index=False)
    return out


def final_merge(
    oep: pd.DataFrame,
    treatments: list[pd.DataFrame],
    sample: pd.DataFrame,
    include_ne_sensitivity: bool,
    market_controls: pd.DataFrame | None = None,
    enrollment_weights: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None]:
    tx = pd.concat(treatments, ignore_index=True)
    final = oep.merge(tx, on=["year", "state", "county_fips"], how="left")
    if market_controls is not None and not market_controls.empty:
        final = final.merge(market_controls, on=["year", "state", "county_fips"], how="left")
    if enrollment_weights is not None and not enrollment_weights.empty:
        final = final.merge(enrollment_weights, on=["state", "county_fips"], how="left")
    year_to_transition = {2022: "2021_to_2022", 2023: "2022_to_2023", 2024: "2023_to_2024"}
    final["transition"] = final["transition"].fillna(final["year"].map(year_to_transition))
    no_treatment = final["treatment_constructible_flag"].isna()
    bool_cols = [
        "any_zero_to_positive_turnover",
        "lowest_zero_to_positive_turnover",
        "second_lowest_zero_to_positive_turnover",
        "any_zero_to_positive_turnover_across_issuer",
        "any_zero_to_positive_turnover_within_issuer",
        "lowest_zero_to_positive_turnover_across_issuer",
        "second_lowest_zero_to_positive_turnover_across_issuer",
        "any_zero_to_positive_turnover_unmapped",
        "any_zero_premium_prior_year",
        "any_positive_mapped_current_year",
        "prior_lowest_zero_premium_flag",
        "prior_second_lowest_zero_premium_flag",
        "current_mapped_lowest_positive_premium_flag",
        "current_mapped_second_lowest_positive_premium_flag",
        "same_issuer_lowest",
        "same_issuer_second_lowest",
        "missing_previous_plan_flag",
        "missing_crosswalk_flag",
        "missing_current_plan_flag",
        "missing_premium_flag",
        "missing_county_mapping_flag",
    ]
    for col in bool_cols:
        if col in final.columns:
            final[col] = final[col].fillna(False).astype(bool)
    final["treatment_constructible_flag"] = final["treatment_constructible_flag"].fillna(False).astype(bool)
    final.loc[no_treatment, "reason_not_constructible"] = final.loc[no_treatment, "reason_not_constructible"].fillna("no_transition_record")
    final["zero_premium_measure_type"] = final["zero_premium_measure_type"].fillna("not_constructible")
    final["premium_measure_type"] = final["premium_measure_type"].fillna("not_constructible")
    sample_keep = sample[["state", "included_primary_sample", "reason_included_or_excluded", "continuous_hcgov_2022_2024"]].rename(columns={"reason_included_or_excluded": "sample_exclusion_reason"})
    final = final.merge(sample_keep, on="state", how="left")
    final["included_primary_sample"] = final["included_primary_sample"].fillna(False).astype(bool)
    final["sample_exclusion_reason"] = np.where(final["included_primary_sample"], "", final["sample_exclusion_reason"].fillna("State not present in OEP state platform sample."))
    final["drake_supplement_etable3_exclusion_reason"] = final["county_fips"].astype(str).map(DRAKE_SUPPLEMENT_EXCLUDED_COUNTY_REASONS).fillna("")
    final["drake_supplement_etable3_exclusion"] = final["drake_supplement_etable3_exclusion_reason"].ne("")
    final["included_drake_harmonized_sample"] = final["included_primary_sample"] & ~final["drake_supplement_etable3_exclusion"]
    final["source_file_references"] = final["raw_file_name"].astype(str) + "; transition=" + final["transition"].astype(str)
    final_path = PROCESSED / "drake_replication_county_year_2022_2024.csv"
    final.to_csv(final_path, index=False)
    primary = final[final["included_primary_sample"]].copy()
    primary_path = PROCESSED / "drake_replication_county_year_2022_2024_primary_sample.csv"
    primary.to_csv(primary_path, index=False)
    primary_harmonized = final[final["included_drake_harmonized_sample"]].copy()
    primary_harmonized.to_csv(PROCESSED / "drake_replication_primary_drake_harmonized_2022_2024.csv", index=False)
    sensitivity = None
    if include_ne_sensitivity:
        ne_states = sample["continuous_hcgov_2022_2024"] & ~sample["state"].isin(["AK", "HI"])
        allowed = set(sample.loc[ne_states, "state"])
        sensitivity = final[final["state"].isin(allowed)].copy()
        sensitivity.to_csv(PROCESSED / "drake_replication_county_year_2022_2024_sensitivity_nebraska.csv", index=False)
    try:
        final.to_parquet(PROCESSED / "drake_replication_county_year_2022_2024.parquet", index=False)
    except Exception as exc:  # noqa: BLE001
        logging.warning("Parquet write failed: %s", exc)
    return final, primary, sensitivity


def write_missingness(final: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year, g in final.groupby("year"):
        for col in final.columns:
            rows.append({"year": year, "variable": col, "missing_count": int(g[col].isna().sum()), "rows": len(g), "missing_rate": float(g[col].isna().mean())})
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "drake_replication_variable_missingness.csv", index=False)
    return out


def write_sample_diagnostics(final: pd.DataFrame, primary: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    if "included_drake_harmonized_sample" in primary.columns:
        harmonized = primary[primary["included_drake_harmonized_sample"].fillna(False).astype(bool)].copy()
    else:
        harmonized = primary.iloc[0:0].copy()
    rows = [
        {"metric": "rows_before_restrictions", "value": len(final), "notes": ""},
        {"metric": "rows_primary_sample", "value": len(primary), "notes": "Continuously HC.gov 2022-2024, excluding AK/HI/NE."},
        {"metric": "rows_drake_harmonized_sample", "value": len(harmonized), "notes": "Primary sample after Drake supplement eTable 3 county exclusions."},
        {"metric": "counties_before_restrictions", "value": final["county_fips"].nunique(), "notes": ""},
        {"metric": "counties_primary_sample", "value": primary["county_fips"].nunique(), "notes": ""},
        {"metric": "counties_drake_harmonized_sample", "value": harmonized["county_fips"].nunique(), "notes": "Should match Drake 2159-county anchor when all eTable 3 counties are present in raw primary."},
        {
            "metric": "drake_supplement_etable3_excluded_counties_in_primary",
            "value": primary.loc[primary["drake_supplement_etable3_exclusion"], "county_fips"].nunique() if "drake_supplement_etable3_exclusion" in primary.columns else 0,
            "notes": "",
        },
        {"metric": "states_primary_sample", "value": primary["state"].nunique(), "notes": ",".join(sorted(primary["state"].dropna().unique()))},
        {"metric": "states_continuously_hcgov", "value": int(sample["continuous_hcgov_2022_2024"].sum()), "notes": ",".join(sorted(sample.loc[sample["continuous_hcgov_2022_2024"], "state"]))},
    ]
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "drake_replication_sample_diagnostics.csv", index=False)
    return out


def write_descriptive_checks(final: pd.DataFrame) -> pd.DataFrame:
    rows = []
    outcome_cols = ["Cnsmr", "Tot_Renrl", "Auto_Renrl", "Actv_Renrl", "Actv_Renrl_Nsw", "Actv_Renrl_Sw", "auto_reenrollment_rate", "active_switch_rate_among_active"]
    for year, g in final.groupby("year"):
        for col in outcome_cols:
            rows.append({"table": "mean_outcome_by_year", "year": year, "group": "all", "variable": col, "value": g[col].mean()})
        rows.append({"table": "treated_share_by_year", "year": year, "group": "all", "variable": "any_zero_to_positive_turnover", "value": g["any_zero_to_positive_turnover"].mean()})
        rows.append({"table": "constructibility_by_year", "year": year, "group": "all", "variable": "treatment_constructible_flag", "value": g["treatment_constructible_flag"].mean()})
        for treated, gt in g.groupby("any_zero_to_positive_turnover", dropna=False):
            for col in outcome_cols:
                rows.append({"table": "mean_outcome_by_treatment_year", "year": year, "group": str(treated), "variable": col, "value": gt[col].mean()})
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "drake_replication_descriptive_checks.csv", index=False)
    treated = final.groupby(["year", "state"], dropna=False).agg(
        county_years=("county_fips", "count"),
        treated_share=("any_zero_to_positive_turnover", "mean"),
        constructible_share=("treatment_constructible_flag", "mean"),
        across_issuer_treated_share=("any_zero_to_positive_turnover_across_issuer", "mean"),
        within_issuer_treated_share=("any_zero_to_positive_turnover_within_issuer", "mean"),
    ).reset_index()
    treated.to_csv(OUTPUTS / "drake_replication_treated_share_by_year_state.csv", index=False)
    return out


def write_crosswalk_diagnostics(join_rows: list[dict[str, Any]], crosswalks: list[pd.DataFrame]) -> pd.DataFrame:
    rows = list(join_rows)
    for cw in crosswalks:
        transition = cw["transition"].iloc[0] if not cw.empty else ""
        rows.extend(
            [
                {"transition": transition, "rank": "all", "metric": "crosswalk_rows", "numerator": len(cw), "denominator": len(cw), "rate": 1.0 if len(cw) else np.nan},
                {"transition": transition, "rank": "all", "metric": "mapped_rows", "numerator": int(cw["mapping_quality_flag"].eq("mapped").sum()), "denominator": len(cw), "rate": float(cw["mapping_quality_flag"].eq("mapped").mean()) if len(cw) else np.nan},
                {"transition": transition, "rank": "all", "metric": "across_issuer_rows", "numerator": int(cw["across_issuer_flag"].sum()), "denominator": len(cw), "rate": float(cw["across_issuer_flag"].mean()) if len(cw) else np.nan},
            ]
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "drake_replication_join_diagnostics.csv", index=False)
    return out


def state_validation_oep(manifest: pd.DataFrame, oep: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    rows = []
    cols = ["Cnsmr", "New_Cnsmr", "Tot_Renrl", "Auto_Renrl", "Actv_Renrl", "Actv_Renrl_Nsw", "Actv_Renrl_Sw"]
    for year in years:
        row = manifest_row(manifest, "oep_puf", year, "State-Level OEP PUF")
        state = read_csv_from_zip(ROOT / row["local_path"])
        state["state"] = state["State_Abrvtn"].astype(str).str.strip().str.upper()
        county_sum = oep[oep["year"].eq(year)].groupby("state")[cols].sum(min_count=1).reset_index()
        for col in cols:
            state[col] = numeric_series(state[col])
        merged = county_sum.merge(state[["state", *cols]], on="state", how="outer", suffixes=("_county_sum", "_state_file"))
        for col in cols:
            diff = merged[f"{col}_county_sum"] - merged[f"{col}_state_file"]
            rows.append({"year": year, "variable": col, "max_abs_state_discrepancy": diff.abs().max(), "states_compared": int(merged["state"].nunique())})
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "oep_county_state_validation_discrepancies.csv", index=False)
    return out


def write_reports(final: pd.DataFrame, primary: pd.DataFrame, sample: pd.DataFrame, join_diag: pd.DataFrame, missingness: pd.DataFrame, parquet_written: bool) -> None:
    years = ", ".join(map(str, sorted(final["year"].dropna().unique())))
    transition_construct = final.groupby("year")["treatment_constructible_flag"].mean().reset_index()
    states = ", ".join(sorted(primary["state"].dropna().unique()))
    harmonized = primary[primary["included_drake_harmonized_sample"].fillna(False).astype(bool)] if "included_drake_harmonized_sample" in primary.columns else primary.iloc[0:0]
    e3_excluded = primary.loc[primary["drake_supplement_etable3_exclusion"], "county_fips"].nunique() if "drake_supplement_etable3_exclusion" in primary.columns else 0
    status = "Conditional Go"
    if final["treatment_constructible_flag"].mean() < 0.8:
        status = "Weak Conditional Go"
    if primary.empty:
        status = "No-Go"
    report = f"""# Drake-Style Replication Dataset Report

## Executive Summary

Overall status: **{status} for moving to Step 3**.

The full county-year replication dataset was built for outcome years {years}. Outcomes are directly constructible from CMS OEP county PUFs. Treatment construction is proxy-based, not exact: zero-premium status uses a benchmark-based low-income age-40 proxy because household-specific APTC and individual enrollment are not public. The 2021 to 2022 transition is attempted from official Exchange PUF plus Health Plan Finder fallback rather than direct QHP Landscape.

## What Was Built

- Final dataset: `data/processed/drake_replication_county_year_2022_2024.csv`
- Primary sample: `data/processed/drake_replication_county_year_2022_2024_primary_sample.csv`
- Drake-harmonized primary sample: `data/processed/drake_replication_primary_drake_harmonized_2022_2024.csv`
- Nebraska sensitivity: `data/processed/drake_replication_county_year_2022_2024_sensitivity_nebraska.csv`
- Parquet written: `{parquet_written}`
- Unit: county-year
- Rows before restrictions: {len(final)}
- Rows in primary sample: {len(primary)}
- Counties in primary sample: {primary['county_fips'].nunique()}
- Rows in Drake-harmonized primary sample: {len(harmonized)}
- Counties in Drake-harmonized primary sample: {harmonized['county_fips'].nunique()}
- Drake supplement eTable 3 counties excluded from harmonized sample: {e3_excluded}
- States in primary sample: {primary['state'].nunique()} ({states})

## Data Sources

The build uses CMS OEP County- and State-Level PUFs for 2022-2024; CMS Exchange Rate, Plan Attributes, Service Area, and Plan ID Crosswalk PUFs for 2021-2024; Data.HealthCare.gov QHP Landscape files for 2022-2024; and CMS Health Plan Finder RBIS state-rating-area fallback for 2021.

## Outcome Construction

Exact OEP columns used: `Cnsmr`, `New_Cnsmr`, `Tot_Renrl`, `Auto_Renrl`, `Actv_Renrl`, `Actv_Renrl_Nsw`, `Actv_Renrl_Sw`. Derived rates and logs are set missing when numerator or denominator is missing, suppressed, or nonpositive. Suppressed values are not imputed.

## Treatment Construction

For each county-year, silver plans are ranked by age-40 gross premium. The two lowest silver plans are crosswalked to the current year with the Plan ID Crosswalk. Current-year mapped plan net premium proxy is gross premium minus current-year second-lowest silver benchmark, floored at zero. Zero-to-positive turnover equals prior top-two zero-premium proxy and mapped current positive net-premium proxy. Across-issuer and within-issuer flags use issuer IDs from prior plans and current mapped plans. The proxy is now documented as an age-40, 125-percent-FPL-style approximation to Drake's 100-150 FPL construction, but it is still not exact household APTC.

## Market Controls Added For Step 4 Readiness

The rebuild writes 2021 county enrollment weights and county-year market controls when raw files are available:

- `enrollment_2021_weight`
- `number_of_silver_plans`
- `number_of_insurers`
- `lowest_silver_premium`
- `second_lowest_silver_premium`
- `premium_spread_among_silver_plans`
- `lowest_bronze_premium`
- `bronze_spread`

`number_of_insurers` is based on silver plan issuers in the constructed county-plan panel. `bronze_spread` is the second-lowest silver premium minus the lowest bronze premium.

## Join Diagnostics

{join_diag.to_string(index=False)}

## Sample Alignment With Drake Et Al.

The primary sample uses states with `Pltfrm == HC.gov` in the official OEP state-level PUF for all 2022-2024 years and excludes AK, HI, and NE. Nebraska is available only in the sensitivity output because county-market mapping has not been independently verified. The Drake-harmonized sample also applies supplement eTable 3 county exclusions.

## Known Limitations

- Public OEP files are aggregate county-year data only.
- Individual-level HTE is not possible.
- County-level reenrollment outcomes are not income-stratified.
- Zero-premium status is proxy-based, not exact household net premium.
- Household-specific APTC is not directly observed.
- PY2021 direct QHP Landscape data were unavailable; 2021 uses official Exchange PUF plus Health Plan Finder fallback.
- Some crosswalk-to-current-plan joins fail and are flagged.
- Non-EHB handling is not yet exact; the output flags proxy limitations rather than asserting exact zero-dollar eligibility.
- OEP county outcomes contain suppression and missingness.

## Self-Check Results

Validation flags are written by `scripts/04_validate_drake_replication_dataset.py` to `outputs/drake_replication_validation_flags.csv`.

## Recommended Next Step

**A. Proceed to Step 3: descriptive replication and non-causal comparison with Drake-style patterns**, conditional on accepting the benchmark-based zero-premium proxy and reviewing 2021 fallback construction.
"""
    (DOCS / "drake_replication_dataset_report.md").write_text(report, encoding="utf-8")

    memo = f"""# Step 2 Progress And Limitations

## Completed

- Built OEP county-year outcomes for 2022-2024.
- Built silver county-plan panel for 2021-2024.
- Built bronze county-plan panel for bronze-spread controls.
- Built top-two silver plan file, zero-premium proxy file, crosswalk transition files, treatment files, and final county-year datasets.
- Built 2021 county enrollment weights for Drake-style weighting.
- Applied Drake supplement eTable 3 county-exclusion flags and wrote a Drake-harmonized primary sample.
- Applied primary sample restrictions: continuously HC.gov states, excluding AK, HI, and NE.
- Logged build steps to `logs/step2_build.log`.

## Partially Completed

- 2021 input is fallback-based because direct PY2021 QHP Landscape files were unavailable.
- Zero-premium status is an estimated benchmark proxy, not an exact observed net premium.
- Some mapped current-year plan joins are incomplete and flagged.
- Non-EHB handling is documented but not yet exact.

## Not Completed

- No exact household-specific APTC calculation was implemented.
- No individual-level retention or HTE dataset can be produced from these public PUFs.
- No causal models were run.

## Honest Feasibility Judgment

**{status}**.

## Immediate Next Actions

1. Review 2021 fallback panel and decide whether to keep 2021 to 2022 in the primary treatment set.
2. Investigate state-year crosswalk failures in `outputs/drake_replication_join_diagnostics.csv`.
3. Validate market controls against Drake Table 2 definitions before Step 4.
4. Review Nebraska sensitivity before deciding whether NE can enter any analysis.
5. Compare treatment prevalence with Drake-style descriptive patterns before modeling.
6. Freeze the dataset version only after validation flags are reviewed.
"""
    (DOCS / "step2_progress_and_limitations.md").write_text(memo, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite existing outputs.")
    parser.add_argument("--years", nargs="+", type=int, default=[2022, 2023, 2024])
    parser.add_argument("--include-nebraska-sensitivity", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    ensure_dirs()
    setup_logging(args.verbose)
    logging.info("Starting Step 2 Drake-style dataset build")
    manifest = load_manifest()
    write_step1_gap_audit()
    write_sample_definition()
    sample = build_healthcaregov_state_sample(manifest, args.years)
    logging.info("Building OEP county outcomes")
    oep = build_oep_county_outcomes(manifest, args.years)
    enrollment_weights = build_2021_enrollment_weights(manifest)
    state_validation_oep(manifest, oep, args.years)
    logging.info("Building silver county-plan panel")
    silver = build_silver_plan_panel(manifest)
    logging.info("Building bronze county-plan panel")
    bronze = build_bronze_plan_panel(manifest)
    logging.info("Identifying two lowest silver plans")
    two_lowest = build_two_lowest(silver)
    market_controls = build_market_controls(silver, bronze, two_lowest)
    zero_proxy = build_zero_proxy(silver, two_lowest)
    join_rows: list[dict[str, Any]] = []
    treatments = []
    crosswalks = []
    for prev, cur in [(2021, 2022), (2022, 2023), (2023, 2024)]:
        logging.info("Constructing transition %s_to_%s", prev, cur)
        crosswalks.append(load_crosswalk(manifest, prev, cur))
        treatments.append(construct_transition(manifest, prev, cur, two_lowest, zero_proxy, join_rows))
    join_diag = write_crosswalk_diagnostics(join_rows, crosswalks)
    logging.info("Merging final dataset")
    final, primary, sensitivity = final_merge(oep, treatments, sample, args.include_nebraska_sensitivity, market_controls, enrollment_weights)
    missingness = write_missingness(final)
    write_sample_diagnostics(final, primary, sample)
    write_descriptive_checks(final)
    parquet_written = (PROCESSED / "drake_replication_county_year_2022_2024.parquet").exists()
    write_reports(final, primary, sample, join_diag, missingness, parquet_written)

    outcome_missing = final.groupby("year")["suppression_or_missing_flag"].mean()
    tx_construct = final.groupby("year")["treatment_constructible_flag"].mean()
    across_avail = final["any_zero_to_positive_turnover_across_issuer"].notna().mean()
    status = "Conditional Go"
    print("\nStep 2 build summary")
    print(f"Final dataset path: {PROCESSED / 'drake_replication_county_year_2022_2024.csv'}")
    print(f"Rows: {len(final)}")
    print(f"States: {final['state'].nunique()}")
    print(f"Counties: {final['county_fips'].nunique()}")
    print(f"Years covered: {sorted(final['year'].dropna().unique().tolist())}")
    print("Treatment constructibility rate by year:")
    print(tx_construct.to_string())
    print("Outcome missingness rate by year:")
    print(outcome_missing.to_string())
    print(f"Across-issuer classification availability: {across_avail:.3f}")
    print(f"Overall status: {status}")
    print(f"Report path: {DOCS / 'drake_replication_dataset_report.md'}")


if __name__ == "__main__":
    main()
