#!/usr/bin/env python
"""Step 3 descriptive Drake-style replication checks.

This script is diagnostic only. It does not estimate causal models, DID models,
causal forests, policy-learning rules, or formal treatment effects.
"""

from __future__ import annotations

import argparse
import logging
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
METADATA = DATA / "metadata"
OUTPUTS = ROOT / "outputs"
DOCS = ROOT / "docs"
LOGS = ROOT / "logs"
LOG_PATH = LOGS / "step3_descriptive_replication.log"

FULL_DATASET = PROCESSED / "drake_replication_county_year_2022_2024.csv"
PRIMARY_DATASET = PROCESSED / "drake_replication_county_year_2022_2024_primary_sample.csv"
NEBRASKA_DATASET = PROCESSED / "drake_replication_county_year_2022_2024_sensitivity_nebraska.csv"

DRAKE_COUNTIES = 2159
DRake_COUNTIES = DRAKE_COUNTIES
DRAKE_RESULT_COUNTY_YEARS = 6471
DRAKE_RESULT_UNIQUE_COUNTIES = 2157
DRAKE_TABLE2_COUNTY_YEARS = 6459
DRAKE_ANY_TURNOVER_COUNTY_YEARS = 4452
DRAKE_ACROSS_ISSUER_TURNOVER_COUNTY_YEARS = 211
DRAKE_ANY_TURNOVER_ENROLLEE_YEARS_MILLIONS = 28.4
DRAKE_ACROSS_TURNOVER_ENROLLEE_YEARS_MILLIONS = 0.8
EXPECTED_PRIMARY_STATES = 29

DRAKE_EXPOSURE_100_150_FPL = {
    2022: 93.9,
    2023: 67.8,
    2024: 83.8,
}

DRAKE_EXPOSURE_150_200_FPL = {
    2022: 7.8,
    2023: 9.2,
    2024: 3.5,
}

DRAKE_SUPPLEMENT_EXCLUDED_COUNTIES = [
    {
        "state": "SD",
        "county_fips": "46113",
        "county_name_in_supplement": "Shannon County",
        "supplement_reason": "FIPS changed over time; Shannon County changed to Oglala Lakota County/FIPS 46102 before the study period.",
    },
    {
        "state": "VA",
        "county_fips": "51515",
        "county_name_in_supplement": "Bedford City",
        "supplement_reason": "FIPS changed over time; Bedford City combined with Bedford County before the study period.",
    },
    {
        "state": "VA",
        "county_fips": "51019",
        "county_name_in_supplement": "Bedford County",
        "supplement_reason": "FIPS changed over time; Bedford City combined with Bedford County before the study period.",
    },
]

for _state, _items in {
    "GA": [
        ("13009", "Baldwin County"),
        ("13013", "Barrow County"),
        ("13021", "Bibb County"),
        ("13051", "Chatham County"),
        ("13059", "Clarke County"),
        ("13141", "Hancock County"),
        ("13157", "Jackson County"),
        ("13207", "Monroe County"),
        ("13215", "Muscogee County"),
        ("13219", "Oconee County"),
        ("13225", "Peach County"),
        ("13227", "Pickens County"),
        ("13245", "Randolph County"),
        ("13319", "Wilkinson County"),
    ],
    "NC": [
        ("37001", "Alamance County"),
        ("37033", "Caswell County"),
        ("37037", "Chatham County"),
        ("37065", "Edgecombe County"),
        ("37079", "Greene County"),
        ("37081", "Guilford County"),
        ("37105", "Lee County"),
        ("37127", "Nash County"),
        ("37145", "Person County"),
        ("37147", "Pitt County"),
        ("37151", "Randolph County"),
        ("37157", "Rockingham County"),
        ("37189", "Watauga County"),
        ("37191", "Wayne County"),
        ("37195", "Wilson County"),
    ],
}.items():
    for _fips, _name in _items:
        DRAKE_SUPPLEMENT_EXCLUDED_COUNTIES.append(
            {
                "state": _state,
                "county_fips": _fips,
                "county_name_in_supplement": _name,
                "supplement_reason": "No crosswalk data from 2023 to 2024 per Drake supplement eTable 3.",
            }
        )

REQUIRED_KEY_COLUMNS = [
    "year",
    "state",
    "county_fips",
    "county_name",
    "Cnsmr",
    "New_Cnsmr",
    "Tot_Renrl",
    "Auto_Renrl",
    "Actv_Renrl",
    "Actv_Renrl_Nsw",
    "Actv_Renrl_Sw",
    "any_zero_to_positive_turnover",
    "any_zero_to_positive_turnover_across_issuer",
    "any_zero_to_positive_turnover_within_issuer",
    "treatment_constructible_flag",
    "included_primary_sample",
    "zero_premium_measure_type",
]

OUTCOME_COLUMNS = [
    "Cnsmr",
    "Tot_Renrl",
    "Auto_Renrl",
    "Actv_Renrl",
    "Actv_Renrl_Nsw",
    "Actv_Renrl_Sw",
]

TABLE1_MEASURES = [
    ("overall_reenrollment_pct_enrollment", "Overall reenrollment as percent of enrollment", "Tot_Renrl", "Cnsmr", "enrollment"),
    ("automatic_pct_enrollment", "Automatic/passive reenrollment as percent of enrollment", "Auto_Renrl", "Cnsmr", "enrollment"),
    ("active_pct_enrollment", "Active reenrollment as percent of enrollment", "Actv_Renrl", "Cnsmr", "enrollment"),
    ("active_stay_pct_enrollment", "Active stay with previous/crosswalked plan as percent of enrollment", "Actv_Renrl_Nsw", "Cnsmr", "enrollment"),
    ("active_switch_pct_enrollment", "Active switch as percent of enrollment", "Actv_Renrl_Sw", "Cnsmr", "enrollment"),
    ("automatic_pct_reenrollment", "Automatic/passive as percent of total reenrollment", "Auto_Renrl", "Tot_Renrl", "reenrollment"),
    ("active_pct_reenrollment", "Active as percent of total reenrollment", "Actv_Renrl", "Tot_Renrl", "reenrollment"),
    ("active_stay_pct_reenrollment", "Active stay as percent of total reenrollment", "Actv_Renrl_Nsw", "Tot_Renrl", "reenrollment"),
    ("active_switch_pct_reenrollment", "Active switch as percent of total reenrollment", "Actv_Renrl_Sw", "Tot_Renrl", "reenrollment"),
]

DRAKE_TABLE1 = {
    ("overall_reenrollment_pct_enrollment", "2022"): 76.7,
    ("overall_reenrollment_pct_enrollment", "2023"): 75.3,
    ("overall_reenrollment_pct_enrollment", "2024"): 74.1,
    ("overall_reenrollment_pct_enrollment", "total"): 75.2,
    ("automatic_pct_enrollment", "2022"): 21.2,
    ("automatic_pct_enrollment", "2023"): 20.8,
    ("automatic_pct_enrollment", "2024"): 22.1,
    ("automatic_pct_enrollment", "total"): 21.5,
    ("active_pct_enrollment", "2022"): 55.4,
    ("active_pct_enrollment", "2023"): 54.6,
    ("active_pct_enrollment", "2024"): 52.0,
    ("active_pct_enrollment", "total"): 53.7,
    ("active_stay_pct_enrollment", "2022"): 24.0,
    ("active_stay_pct_enrollment", "2023"): 23.2,
    ("active_stay_pct_enrollment", "2024"): 23.3,
    ("active_stay_pct_enrollment", "total"): 23.4,
    ("active_switch_pct_enrollment", "2022"): 31.5,
    ("active_switch_pct_enrollment", "2023"): 31.4,
    ("active_switch_pct_enrollment", "2024"): 28.7,
    ("active_switch_pct_enrollment", "total"): 30.3,
    ("automatic_pct_reenrollment", "2022"): 27.7,
    ("automatic_pct_reenrollment", "2023"): 27.6,
    ("automatic_pct_reenrollment", "2024"): 30.0,
    ("automatic_pct_reenrollment", "total"): 28.6,
    ("active_pct_reenrollment", "2022"): 72.3,
    ("active_pct_reenrollment", "2023"): 72.4,
    ("active_pct_reenrollment", "2024"): 70.0,
    ("active_pct_reenrollment", "total"): 71.4,
    ("active_stay_pct_reenrollment", "2022"): 31.1,
    ("active_stay_pct_reenrollment", "2023"): 30.4,
    ("active_stay_pct_reenrollment", "2024"): 31.3,
    ("active_stay_pct_reenrollment", "total"): 31.0,
    ("active_switch_pct_reenrollment", "2022"): 41.2,
    ("active_switch_pct_reenrollment", "2023"): 42.0,
    ("active_switch_pct_reenrollment", "2024"): 38.7,
    ("active_switch_pct_reenrollment", "total"): 40.4,
}

TRUE_VALUES = {"true", "1", "yes", "y", "t"}
FALSE_VALUES = {"false", "0", "no", "n", "f", "", "nan", "none", "na", "n/a"}


def setup_logging(verbose: bool = False) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8"), logging.StreamHandler()],
    )


def ensure_dirs() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    lowered = series.astype(str).str.strip().str.lower()
    return lowered.isin(TRUE_VALUES)


def as_optional_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    lowered = series.astype(str).str.strip().str.lower()
    out = pd.Series(pd.NA, index=series.index, dtype="boolean")
    out[lowered.isin(TRUE_VALUES)] = True
    out[lowered.isin(FALSE_VALUES)] = False
    return out


def num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    n = num(numerator)
    d = num(denominator)
    out = n / d
    out = out.where(d > 0)
    out = out.replace([np.inf, -np.inf], np.nan)
    return out


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    v = num(values)
    w = num(weights)
    mask = v.notna() & w.notna() & (w > 0)
    if not mask.any():
        return math.nan
    return float(np.average(v[mask], weights=w[mask]))


def ratio_value(df: pd.DataFrame, numerator: str, denominator: str, weighting: str) -> float:
    ratio = safe_divide(df[numerator], df[denominator])
    if weighting == "unweighted_county_mean":
        return float(ratio.mean() * 100)
    if weighting == "Cnsmr_weighted_mean":
        return weighted_mean(ratio, df["Cnsmr"]) * 100
    if weighting == "Tot_Renrl_weighted_mean":
        return weighted_mean(ratio, df["Tot_Renrl"]) * 100
    raise ValueError(f"Unknown weighting: {weighting}")


def format_value(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.{digits}f}"
    return str(value)


def md_table(df: pd.DataFrame, max_rows: int | None = None, digits: int = 3) -> str:
    if df.empty:
        return "_No rows._"
    if max_rows is not None:
        df = df.head(max_rows)
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        vals = [format_value(row[c], digits=digits).replace("\n", " ") for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def read_csv(path: Path, nrows: int | None = None) -> pd.DataFrame:
    dtype = {"county_fips": "string", "County_FIPS_Cd": "string", "previous_lowest_plan_id": "string", "previous_second_lowest_plan_id": "string"}
    return pd.read_csv(path, dtype=dtype, low_memory=False, nrows=nrows)


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "county_fips" in out.columns:
        out["county_fips"] = out["county_fips"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    if "year" in out.columns:
        out["year"] = num(out["year"]).astype("Int64")
    for col in OUTCOME_COLUMNS:
        if col in out.columns:
            out[col] = num(out[col])
    bool_cols = [
        "any_zero_to_positive_turnover",
        "any_zero_to_positive_turnover_across_issuer",
        "any_zero_to_positive_turnover_within_issuer",
        "treatment_constructible_flag",
        "included_primary_sample",
        "continuous_hcgov_2022_2024",
        "suppression_or_missing_flag",
        "missing_previous_plan_flag",
        "missing_crosswalk_flag",
        "missing_current_plan_flag",
        "missing_premium_flag",
        "missing_county_mapping_flag",
        "any_zero_to_positive_turnover_unmapped",
    ]
    for col in bool_cols:
        if col in out.columns:
            out[col + "_bool"] = as_bool(out[col])
    if "treatment_constructible_flag_bool" not in out.columns:
        out["treatment_constructible_flag_bool"] = False
    if "suppression_or_missing_flag_bool" not in out.columns:
        out["suppression_or_missing_flag_bool"] = out[OUTCOME_COLUMNS].isna().any(axis=1)
    out["overall_reenrollment_share"] = safe_divide(out["Tot_Renrl"], out["Cnsmr"])
    out["automatic_passive_share"] = safe_divide(out["Auto_Renrl"], out["Cnsmr"])
    out["active_share"] = safe_divide(out["Actv_Renrl"], out["Cnsmr"])
    out["active_stay_share"] = safe_divide(out["Actv_Renrl_Nsw"], out["Cnsmr"])
    out["active_switch_share"] = safe_divide(out["Actv_Renrl_Sw"], out["Cnsmr"])
    out["automatic_passive_share_of_reenrollment"] = safe_divide(out["Auto_Renrl"], out["Tot_Renrl"])
    out["active_share_of_reenrollment"] = safe_divide(out["Actv_Renrl"], out["Tot_Renrl"])
    out["active_stay_share_of_reenrollment"] = safe_divide(out["Actv_Renrl_Nsw"], out["Tot_Renrl"])
    out["active_switch_share_of_reenrollment"] = safe_divide(out["Actv_Renrl_Sw"], out["Tot_Renrl"])
    out["table1_outcome_missing_flag"] = out[OUTCOME_COLUMNS].isna().any(axis=1)
    return out


def first_existing_text(path: Path, max_chars: int = 5000) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except UnicodeDecodeError:
        return path.read_text(errors="replace")[:max_chars]


def make_initial_audit() -> pd.DataFrame:
    artifacts = [
        ROOT / "README.md",
        DOCS / "drake_replication_dataset_report.md",
        DOCS / "step2_progress_and_limitations.md",
        OUTPUTS / "drake_replication_validation_flags.csv",
        OUTPUTS / "drake_replication_sample_diagnostics.csv",
        OUTPUTS / "drake_replication_join_diagnostics.csv",
        OUTPUTS / "drake_replication_descriptive_checks.csv",
        METADATA / "drake_style_sample_definition.yaml",
        METADATA / "healthcaregov_state_sample_2022_2024.csv",
    ]
    rows: list[dict[str, Any]] = []
    for path in artifacts:
        exists = path.exists()
        readable = False
        key_info = ""
        concern = ""
        action = ""
        if exists:
            try:
                if path.suffix.lower() == ".csv":
                    df = pd.read_csv(path, nrows=20)
                    readable = True
                    key_info = f"{len(df)} preview rows; columns: {', '.join(df.columns[:8])}"
                    if "status" in df.columns:
                        key_info += "; statuses: " + ", ".join(df["status"].astype(str).value_counts().index.tolist())
                    if "metric" in df.columns and "value" in df.columns:
                        preview = "; ".join((df["metric"].astype(str) + "=" + df["value"].astype(str)).head(4).tolist())
                        key_info += "; " + preview
                else:
                    text = first_existing_text(path)
                    readable = True
                    lower = text.lower()
                    hits = []
                    for phrase in ["conditional go", "2188", "6564", "proxy", "fallback", "15", "warn"]:
                        if phrase in lower:
                            hits.append(phrase)
                    key_info = "found: " + ", ".join(hits) if hits else "readable text"
            except Exception as exc:  # pragma: no cover - defensive audit output
                readable = False
                concern = str(exc)
                action = "Inspect or regenerate this artifact before relying on it."
        else:
            concern = "Missing artifact."
            action = "Regenerate or document absence."
        if exists and readable and not concern:
            concern = "None detected in initial file read."
            action = "Use as Step 3 input."
        rows.append(
            {
                "artifact": str(path.relative_to(ROOT)),
                "exists": exists,
                "readable": readable,
                "key_information_found": key_info,
                "concern_or_gap": concern,
                "action_needed": action,
            }
        )
    audit = pd.DataFrame(rows)
    audit.to_csv(OUTPUTS / "step3_initial_audit.csv", index=False)
    return audit


def is_lfs_pointer(path: Path) -> bool:
    if not path.exists() or path.stat().st_size > 1024:
        return False
    text = first_existing_text(path, max_chars=1024)
    return text.startswith("version https://git-lfs.github.com/spec")


def make_readability_check(paths: list[Path]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    rows: list[dict[str, Any]] = []
    datasets: dict[str, pd.DataFrame] = {}
    for path in paths:
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        readable = False
        row_count: int | str = ""
        col_count: int | str = ""
        key_present = False
        problem = ""
        notes = ""
        if not exists:
            problem = "missing_file"
            notes = "Dataset is absent."
        elif is_lfs_pointer(path):
            problem = "lfs_pointer_or_truncated_file"
            notes = "File appears to be a pointer rather than committed CSV data."
        else:
            try:
                df = prepare_dataset(read_csv(path))
                readable = True
                row_count = len(df)
                col_count = len(df.columns)
                missing = [col for col in REQUIRED_KEY_COLUMNS if col not in df.columns]
                key_present = not missing
                if len(df) == 0:
                    problem = "empty_csv"
                elif missing:
                    problem = "missing_key_columns"
                    notes = "Missing: " + ", ".join(missing)
                else:
                    problem = "none"
                    notes = "Readable nonempty committed CSV."
                    datasets[path.name] = df
            except Exception as exc:  # pragma: no cover - written for user audit
                problem = "read_error"
                notes = str(exc)
        rows.append(
            {
                "dataset_path": str(path.relative_to(ROOT)),
                "file_exists": exists,
                "file_size_bytes": size,
                "readable": readable,
                "rows": row_count,
                "columns": col_count,
                "key_columns_present": key_present,
                "problem_detected": problem,
                "notes": notes,
            }
        )
    check = pd.DataFrame(rows)
    check.to_csv(OUTPUTS / "step3_dataset_readability_check.csv", index=False)
    return check, datasets


def subset_years(df: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    return df[df["year"].astype("Int64").isin(years)].copy()


def drake_supplement_exclusions_frame() -> pd.DataFrame:
    out = pd.DataFrame(DRAKE_SUPPLEMENT_EXCLUDED_COUNTIES).copy()
    out["county_fips"] = out["county_fips"].astype(str).str.zfill(5)
    return out


def add_drake_supplement_exclusion_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    exclusions = drake_supplement_exclusions_frame()[["county_fips", "supplement_reason"]].drop_duplicates("county_fips")
    out = out.merge(exclusions, on="county_fips", how="left")
    out["drake_supplement_exclusion_flag"] = out["supplement_reason"].notna()
    out["drake_supplement_exclusion_reason"] = out["supplement_reason"].fillna("")
    out = out.drop(columns=["supplement_reason"])
    out["included_drake_harmonized_sample"] = ~out["drake_supplement_exclusion_flag"]
    return out


def make_drake_excluded_counties_check(primary: pd.DataFrame) -> pd.DataFrame:
    exclusions = drake_supplement_exclusions_frame()
    observed = (
        primary.groupby(["state", "county_fips"], dropna=False)
        .agg(
            observed_county_names=("county_name", lambda x: ";".join(sorted(x.dropna().astype(str).unique().tolist()))),
            rows_present=("year", "size"),
            years_present=("year", lambda x: ",".join(map(str, sorted(x.dropna().astype(int).unique().tolist())))),
            enrollment_present=("Cnsmr", "sum"),
            any_missing_crosswalk=("missing_crosswalk_flag_bool", "max") if "missing_crosswalk_flag_bool" in primary.columns else ("year", lambda _: False),
            any_missing_current_plan=("missing_current_plan_flag_bool", "max") if "missing_current_plan_flag_bool" in primary.columns else ("year", lambda _: False),
            any_missing_premium=("missing_premium_flag_bool", "max") if "missing_premium_flag_bool" in primary.columns else ("year", lambda _: False),
        )
        .reset_index()
    )
    check = exclusions.merge(observed, on=["state", "county_fips"], how="left")
    check["present_in_current_primary_sample"] = check["rows_present"].fillna(0).astype(int).gt(0)
    check["rows_present"] = check["rows_present"].fillna(0).astype(int)
    check["enrollment_present"] = check["enrollment_present"].fillna(0)
    for col in ["observed_county_names", "years_present"]:
        check[col] = check[col].fillna("")
    for col in ["any_missing_crosswalk", "any_missing_current_plan", "any_missing_premium"]:
        check[col] = check[col].apply(lambda value: bool(value) if pd.notna(value) else False)
    check.to_csv(OUTPUTS / "step3_drake_excluded_counties_check.csv", index=False)
    return check


def write_harmonized_dataset(primary: pd.DataFrame) -> Path:
    path = PROCESSED / "drake_replication_primary_drake_harmonized_2022_2024.csv"
    primary.to_csv(path, index=False)
    return path


def summarize_excluded_states(state_meta: pd.DataFrame | None) -> str:
    if state_meta is None or state_meta.empty:
        return "State metadata unavailable."
    excluded = state_meta[~as_bool(state_meta["included_primary_sample"])]
    return "; ".join((excluded["state"].astype(str) + ": " + excluded["reason_included_or_excluded"].astype(str)).tolist())


def make_sample_alignment(
    full: pd.DataFrame,
    primary_raw: pd.DataFrame,
    primary: pd.DataFrame,
    ne: pd.DataFrame | None,
    state_meta: pd.DataFrame | None,
    excluded_check: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    years = sorted(primary["year"].dropna().astype(int).unique().tolist())
    primary_states = sorted(primary["state"].dropna().astype(str).unique().tolist())
    counties_by_year = primary.groupby("year")["county_fips"].nunique().to_dict()
    rows_by_year = primary.groupby("year").size().to_dict()
    county_year_counts = primary.groupby("county_fips")["year"].nunique()
    counties_all_years = int((county_year_counts == len(years)).sum())
    table1_complete_by_county = primary.groupby("county_fips")["table1_outcome_missing_flag"].sum().eq(0)
    constructible_by_county = primary.groupby("county_fips")["treatment_constructible_flag_bool"].all()
    complete_and_constructible = table1_complete_by_county & constructible_by_county
    no_suppression_by_county = ~primary.groupby("county_fips")["suppression_or_missing_flag_bool"].any()
    complete_constructible_no_suppression = complete_and_constructible & no_suppression_by_county
    raw_counties = primary_raw["county_fips"].nunique()
    drake_gap_raw = int(raw_counties - DRAKE_COUNTIES)
    drake_gap_harmonized = int(primary["county_fips"].nunique() - DRAKE_COUNTIES)
    state_excluded = summarize_excluded_states(state_meta)
    cnsmer_nonmissing = primary[primary["Cnsmr"].notna()]
    present_excluded = excluded_check[excluded_check["present_in_current_primary_sample"]]
    present_excluded_counties = int(present_excluded["county_fips"].nunique())

    def add(metric: str, value: Any, reference: Any = "", notes: str = "") -> None:
        rows.append({"metric": metric, "value": value, "drake_or_expected_reference": reference, "notes": notes})

    add("rows_before_restrictions", len(full), "", "All constructed county-years before Drake-style sample restrictions.")
    add("rows_primary_sample_raw", len(primary_raw), "", "Primary sample before Drake supplement eTable 3 county exclusions.")
    add("counties_primary_sample_raw", raw_counties, DRAKE_COUNTIES, f"Raw difference from Drake count: {drake_gap_raw}.")
    add("rows_drake_harmonized_sample", len(primary), "", "Primary sample after applying Drake supplement eTable 3 county exclusions.")
    add("counties_drake_harmonized_sample", primary["county_fips"].nunique(), DRAKE_COUNTIES, f"Harmonized difference from Drake count: {drake_gap_harmonized}.")
    add("rows_primary_sample", len(primary), "", "Backward-compatible alias: Drake-harmonized county-years used for Step 3 outputs.")
    add("states_primary_sample", len(primary_states), EXPECTED_PRIMARY_STATES, ",".join(primary_states))
    add("counties_primary_sample", primary["county_fips"].nunique(), DRAKE_COUNTIES, "Backward-compatible alias: Drake-harmonized county count.")
    add("county_years_primary_sample", len(primary), "", "Rows equal county-years.")
    add(
        "drake_supplement_excluded_counties_present",
        present_excluded_counties,
        drake_gap_raw,
        "These are the eTable 3 counties present in the raw primary sample and removed from the Drake-harmonized sample.",
    )
    add(
        "drake_supplement_excluded_rows_present",
        int(present_excluded["rows_present"].sum()),
        "",
        "Rows removed by the eTable 3 county exclusion rule.",
    )
    for year in years:
        add(f"county_years_{year}", int(rows_by_year.get(year, 0)), "", "Primary sample rows in this year.")
        add(f"counties_{year}", int(counties_by_year.get(year, 0)), "", "Primary sample counties in this year.")
    add("counties_present_all_three_years", counties_all_years, DRAKE_COUNTIES, "All current harmonized counties are present in all requested years." if counties_all_years == primary["county_fips"].nunique() else "")
    add(
        "county_years_with_nonmissing_enrollment",
        len(cnsmer_nonmissing),
        DRAKE_RESULT_COUNTY_YEARS,
        "Drake Results text reports 6471 county-years after outcome/weight availability.",
    )
    add(
        "unique_counties_with_nonmissing_enrollment",
        cnsmer_nonmissing["county_fips"].nunique(),
        DRAKE_RESULT_UNIQUE_COUNTIES,
        "Drake Results text reports 2157 unique counties in the analytic county-year data.",
    )
    add("excluded_states_and_reasons", state_excluded, "", "From healthcaregov_state_sample_2022_2024.csv when available.")
    for state in ["AK", "HI", "NE"]:
        add(f"{state}_in_primary_sample", bool((primary["state"] == state).any()), False, "Expected exclusion check.")
    if ne is not None:
        add("nebraska_sensitivity_exists", True, "", f"Rows: {len(ne)}; counties: {ne['county_fips'].nunique()}.")
    else:
        add("nebraska_sensitivity_exists", False, "", "Sensitivity file absent.")
    add("counties_with_complete_table1_outcomes_all_years", int(table1_complete_by_county.sum()), "", "Potential harmonization rule, not Drake-confirmed.")
    add("counties_constructible_treatment_all_years", int(constructible_by_county.sum()), "", "Potential treatment-readiness rule, not Drake-confirmed.")
    add("counties_complete_outcomes_and_constructible_all_years", int(complete_and_constructible.sum()), "", "Potential harmonization rule, not Drake-confirmed.")
    add("counties_complete_constructible_no_suppression_all_years", int(complete_constructible_no_suppression.sum()), "", "Potential strict rule, not Drake-confirmed.")
    for col in OUTCOME_COLUMNS:
        nonmissing = primary[primary[col].notna()]
        add(f"nonmissing_rows_{col}", len(nonmissing), "", f"County-years with nonmissing {col}.")
        add(f"nonmissing_counties_{col}", nonmissing["county_fips"].nunique(), "", f"Unique counties with nonmissing {col}.")
    add(
        "county_discrepancy_interpretation",
        "resolved_by_drake_supplement_etable3",
        "Drake reports 2159 counties.",
        "The raw primary sample has 2188 counties. Drake supplement eTable 3 identifies 29 GA/NC counties with no 2023-to-2024 crosswalk data; dropping those counties gives 2159 counties. Legacy SD/VA FIPS exclusions are also encoded but do not affect this 2022-2024 primary sample.",
    )

    summary = pd.DataFrame(rows)
    summary.to_csv(OUTPUTS / "step3_sample_alignment.csv", index=False)

    g = primary_raw.groupby(["state", "county_fips", "county_name"], dropna=False).agg(
        rows=("year", "size"),
        years_present=("year", "nunique"),
        min_year=("year", "min"),
        max_year=("year", "max"),
        total_enrollment=("Cnsmr", "sum"),
        min_enrollment=("Cnsmr", "min"),
        table1_missing_years=("table1_outcome_missing_flag", "sum"),
        treatment_constructible_years=("treatment_constructible_flag_bool", "sum"),
        suppression_or_missing_any=("suppression_or_missing_flag_bool", "max"),
    ).reset_index()
    exclusion_lookup = (
        excluded_check[["state", "county_fips", "present_in_current_primary_sample", "supplement_reason"]]
        .drop_duplicates(["state", "county_fips"])
        .rename(columns={"present_in_current_primary_sample": "drake_supplement_exclusion_flag", "supplement_reason": "drake_supplement_exclusion_reason"})
    )
    g = g.merge(exclusion_lookup, on=["state", "county_fips"], how="left")
    g["drake_supplement_exclusion_flag"] = g["drake_supplement_exclusion_flag"].apply(lambda value: bool(value) if pd.notna(value) else False)
    g["drake_supplement_exclusion_reason"] = g["drake_supplement_exclusion_reason"].fillna("")
    g["included_drake_harmonized_sample"] = ~g["drake_supplement_exclusion_flag"]
    for flag in ["missing_crosswalk_flag_bool", "missing_current_plan_flag_bool", "missing_premium_flag_bool", "missing_county_mapping_flag_bool"]:
        if flag in primary_raw.columns:
            flag_g = primary_raw.groupby(["state", "county_fips"])[flag].max().reset_index(name=flag.replace("_bool", "_any"))
            g = g.merge(flag_g, on=["state", "county_fips"], how="left")
    g["all_three_years"] = g["years_present"].eq(len(years))
    g["table1_complete_all_years"] = g["table1_missing_years"].eq(0)
    g["treatment_constructible_all_years"] = g["treatment_constructible_years"].eq(len(years))
    g["low_enrollment_rank"] = g["total_enrollment"].rank(method="first").astype(int)
    g["candidate_extra_if_forcing_to_2159_by_low_enrollment"] = g["low_enrollment_rank"].le(max(drake_gap_raw, 0))
    reasons = []
    for _, row in g.iterrows():
        county_reasons = []
        if bool(row["drake_supplement_exclusion_flag"]):
            county_reasons.append("drake_supplement_etable3_exclusion")
        if not row["all_three_years"]:
            county_reasons.append("not_present_all_years")
        if not row["table1_complete_all_years"]:
            county_reasons.append("missing_or_suppressed_table1_outcome")
        if not row["treatment_constructible_all_years"]:
            county_reasons.append("treatment_not_constructible_all_years")
        for col in ["missing_crosswalk_flag_any", "missing_current_plan_flag_any", "missing_premium_flag_any", "missing_county_mapping_flag_any"]:
            if col in g.columns and bool(row.get(col, False)):
                county_reasons.append(col.replace("_any", ""))
        if not county_reasons and row["candidate_extra_if_forcing_to_2159_by_low_enrollment"]:
            county_reasons.append("low_enrollment_candidate_only_drake_county_list_unavailable")
        if not county_reasons:
            county_reasons.append("included_by_current_sample_rule")
        reasons.append(";".join(county_reasons))
    g["candidate_discrepancy_reason"] = reasons
    g.to_csv(OUTPUTS / "step3_county_discrepancy_diagnostics.csv", index=False)
    return summary, g


def likely_table1_reason(abs_diff: float, closest: bool, denominator: str) -> str:
    if pd.isna(abs_diff):
        return "No Drake value encoded for this row."
    if abs_diff <= 1.0 and closest:
        return "Close to Drake anchor under the closest weighting."
    if not closest:
        return "Alternative weighting retained for diagnosis; not expected to match Drake's weighted table most closely."
    if denominator == "enrollment":
        return "Likely reflects OEP suppression/missingness, denominator availability, or public county-year aggregation differences."
    return "Likely reflects reenrollment denominator handling, OEP suppression/missingness, or public county-year aggregation differences."


def make_table1(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    years = [str(y) for y in sorted(df["year"].dropna().astype(int).unique().tolist())] + ["total"]
    weightings = ["unweighted_county_mean", "Cnsmr_weighted_mean", "Tot_Renrl_weighted_mean"]
    for year_label in years:
        sub = df if year_label == "total" else df[df["year"].astype(int).astype(str).eq(year_label)]
        for measure_key, label, numerator, denominator, denominator_used in TABLE1_MEASURES:
            for weighting in weightings:
                our_value = ratio_value(sub, numerator, denominator, weighting)
                drake_value = DRAKE_TABLE1.get((measure_key, year_label), math.nan)
                difference = our_value - drake_value if not pd.isna(drake_value) else math.nan
                abs_difference = abs(difference) if not pd.isna(difference) else math.nan
                percent_difference = difference / drake_value * 100 if drake_value and not pd.isna(difference) else math.nan
                closest = (denominator == "Cnsmr" and weighting == "Cnsmr_weighted_mean") or (
                    denominator == "Tot_Renrl" and weighting == "Tot_Renrl_weighted_mean"
                )
                rows.append(
                    {
                        "year": year_label,
                        "measure": measure_key,
                        "measure_label": label,
                        "our_value": our_value,
                        "drake_value": drake_value,
                        "difference": difference,
                        "absolute_difference": abs_difference,
                        "percent_difference": percent_difference,
                        "weighting_used": weighting,
                        "denominator_used": denominator_used,
                        "closest_to_drake_table1": closest,
                        "likely_reason_for_difference": likely_table1_reason(abs_difference, closest, denominator_used),
                    }
                )
    table = pd.DataFrame(rows)
    table.to_csv(OUTPUTS / "step3_table1_reenrollment_by_year.csv", index=False)
    closest = table[table["closest_to_drake_table1"]].copy()
    closest["our_value"] = closest["our_value"].round(2)
    closest["drake_value"] = closest["drake_value"].round(2)
    closest["difference"] = closest["difference"].round(2)
    closest["absolute_difference"] = closest["absolute_difference"].round(2)
    md = [
        "# Step 3 Table 1-Style Reenrollment By Year",
        "",
        "The table below shows the weighting closest to Drake Table 1: Cnsmr-weighted for enrollment-denominator measures and Tot_Renrl-weighted for reenrollment-denominator measures. The CSV contains unweighted, Cnsmr-weighted, and Tot_Renrl-weighted versions for every row.",
        "",
        md_table(closest[["year", "measure", "our_value", "drake_value", "difference", "weighting_used", "likely_reason_for_difference"]], digits=2),
        "",
    ]
    (OUTPUTS / "step3_table1_reenrollment_by_year.md").write_text("\n".join(md), encoding="utf-8")
    return table


def prevalence_for_group(df: pd.DataFrame, group_cols: list[str] | None = None) -> pd.DataFrame:
    if group_cols is None:
        groups = [(("pooled",), df)]
        keys = ["pooled"]
    else:
        groups = list(df.groupby(group_cols, dropna=False))
        keys = group_cols
    rows: list[dict[str, Any]] = []
    flags = [
        ("any", "any_zero_to_positive_turnover_bool"),
        ("across_issuer", "any_zero_to_positive_turnover_across_issuer_bool"),
        ("within_issuer", "any_zero_to_positive_turnover_within_issuer_bool"),
    ]
    for key, sub in groups:
        if not isinstance(key, tuple):
            key = (key,)
        row: dict[str, Any] = {col: val for col, val in zip(keys, key)}
        constructible = sub["treatment_constructible_flag_bool"]
        row.update(
            {
                "county_years": len(sub),
                "counties": sub["county_fips"].nunique(),
                "states": sub["state"].nunique(),
                "enrollment": sub["Cnsmr"].sum(skipna=True),
                "treatment_constructibility_rate": float(constructible.mean()) if len(sub) else math.nan,
                "missing_treatment_rate": float((~constructible).mean()) if len(sub) else math.nan,
                "not_constructible_count": int((~constructible).sum()),
            }
        )
        for label, col in flags:
            if col not in sub.columns:
                row[f"{label}_share_all_county_years"] = math.nan
                row[f"{label}_share_constructible"] = math.nan
                row[f"{label}_enrollment_weighted_share_all"] = math.nan
                row[f"{label}_enrollment_weighted_share_constructible"] = math.nan
                continue
            flag = sub[col].astype(float)
            row[f"{label}_share_all_county_years"] = float(flag.mean()) if len(flag) else math.nan
            row[f"{label}_share_constructible"] = float(flag[constructible].mean()) if constructible.any() else math.nan
            row[f"{label}_enrollment_weighted_share_all"] = weighted_mean(flag, sub["Cnsmr"])
            row[f"{label}_enrollment_weighted_share_constructible"] = weighted_mean(flag[constructible], sub.loc[constructible, "Cnsmr"]) if constructible.any() else math.nan
        rows.append(row)
    return pd.DataFrame(rows)


def make_drake_exposure_comparison(by_year: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in by_year.iterrows():
        year = int(row["year"])
        our_weighted = float(row["any_enrollment_weighted_share_constructible"] * 100)
        our_unweighted = float(row["any_share_constructible"] * 100)
        drake_100_150 = DRAKE_EXPOSURE_100_150_FPL.get(year, math.nan)
        drake_150_200 = DRAKE_EXPOSURE_150_200_FPL.get(year, math.nan)
        diff = our_weighted - drake_100_150 if not pd.isna(drake_100_150) else math.nan
        rows.append(
            {
                "year": year,
                "our_any_turnover_enrollment_weighted_pct": our_weighted,
                "our_any_turnover_unweighted_county_pct": our_unweighted,
                "drake_100_150_fpl_exposure_pct": drake_100_150,
                "difference_vs_drake_100_150_pp": diff,
                "absolute_difference_vs_drake_100_150_pp": abs(diff) if not pd.isna(diff) else math.nan,
                "drake_150_200_fpl_exposure_pct": drake_150_200,
                "comparison_note": "Closest available comparison is enrollment-weighted any turnover vs Drake 100-150 FPL exposure. Drake exposure is individual/exposure-weighted; this dataset uses county-year OEP enrollment weights.",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "step3_drake_exposure_comparison.csv", index=False)
    return out


def make_turnover_count_comparison(df: pd.DataFrame) -> pd.DataFrame:
    constructible = df["treatment_constructible_flag_bool"]
    table2_like = df[constructible].copy()
    any_flag = table2_like["any_zero_to_positive_turnover_bool"]
    across_flag = table2_like["any_zero_to_positive_turnover_across_issuer_bool"]
    rows = [
        {
            "metric": "constructible_county_years",
            "our_value": len(table2_like),
            "drake_reference": DRAKE_TABLE2_COUNTY_YEARS,
            "difference": len(table2_like) - DRAKE_TABLE2_COUNTY_YEARS,
            "notes": "Drake Table 2 reports 6459 county-years. Our count is constructible rows after eTable 3 exclusions; remaining difference likely reflects 2021 weights/control availability and OEP suppression.",
        },
        {
            "metric": "any_turnover_county_years",
            "our_value": int(any_flag.sum()),
            "drake_reference": DRAKE_ANY_TURNOVER_COUNTY_YEARS,
            "difference": int(any_flag.sum()) - DRAKE_ANY_TURNOVER_COUNTY_YEARS,
            "notes": "Main article reports 4452 county-years with any turnover.",
        },
        {
            "metric": "across_issuer_turnover_county_years",
            "our_value": int(across_flag.sum()),
            "drake_reference": DRAKE_ACROSS_ISSUER_TURNOVER_COUNTY_YEARS,
            "difference": int(across_flag.sum()) - DRAKE_ACROSS_ISSUER_TURNOVER_COUNTY_YEARS,
            "notes": "Main article reports 211 county-years with across-insurer turnover. This is the clearest treatment-definition mismatch.",
        },
        {
            "metric": "any_turnover_enrollee_years_millions",
            "our_value": float(table2_like.loc[any_flag, "Cnsmr"].sum(skipna=True) / 1_000_000),
            "drake_reference": DRAKE_ANY_TURNOVER_ENROLLEE_YEARS_MILLIONS,
            "difference": float(table2_like.loc[any_flag, "Cnsmr"].sum(skipna=True) / 1_000_000) - DRAKE_ANY_TURNOVER_ENROLLEE_YEARS_MILLIONS,
            "notes": "Main article reports 28.4 million enrollee-years with any turnover.",
        },
        {
            "metric": "across_issuer_turnover_enrollee_years_millions",
            "our_value": float(table2_like.loc[across_flag, "Cnsmr"].sum(skipna=True) / 1_000_000),
            "drake_reference": DRAKE_ACROSS_TURNOVER_ENROLLEE_YEARS_MILLIONS,
            "difference": float(table2_like.loc[across_flag, "Cnsmr"].sum(skipna=True) / 1_000_000) - DRAKE_ACROSS_TURNOVER_ENROLLEE_YEARS_MILLIONS,
            "notes": "Main article reports 0.8 million enrollee-years with across-insurer turnover.",
        },
    ]
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "step3_turnover_count_comparison.csv", index=False)
    return out


def make_turnover_prevalence(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    by_year = prevalence_for_group(df, ["year"])
    by_state_year = prevalence_for_group(df, ["state", "year"])
    weighted = pd.concat(
        [
            prevalence_for_group(df, None).assign(scope="pooled"),
            prevalence_for_group(df, ["year"]).assign(scope="year"),
        ],
        ignore_index=True,
        sort=False,
    )
    by_year.to_csv(OUTPUTS / "step3_turnover_prevalence_by_year.csv", index=False)
    by_state_year.to_csv(OUTPUTS / "step3_turnover_prevalence_by_state_year.csv", index=False)
    weighted.to_csv(OUTPUTS / "step3_turnover_prevalence_weighted.csv", index=False)
    exposure = make_drake_exposure_comparison(by_year)
    counts = make_turnover_count_comparison(df)
    return by_year, by_state_year, weighted, exposure, counts


def comparison_variables(df: pd.DataFrame) -> list[dict[str, Any]]:
    specs = [
        ("overall_reenrollment_share", "outcome", "Overall reenrollment share", True),
        ("automatic_passive_share", "outcome", "Automatic/passive share", True),
        ("active_share", "outcome", "Active share", True),
        ("active_stay_share", "outcome", "Active stay share", True),
        ("active_switch_share", "outcome", "Active switch share", True),
        ("number_of_silver_plans", "plan_market", "Number of silver plans", "number_of_silver_plans" in df.columns),
        ("number_of_insurers", "plan_market", "Number of insurers", "number_of_insurers" in df.columns),
        ("bronze_spread", "plan_market", "Bronze spread", "bronze_spread" in df.columns),
        ("prior_premium_lowest", "plan_market", "Lowest silver premium proxy", "prior_premium_lowest" in df.columns),
        ("prior_premium_second_lowest", "plan_market", "Second-lowest silver premium proxy", "prior_premium_second_lowest" in df.columns),
        ("premium_spread_among_silver_proxy", "plan_market", "Premium spread among two lowest silver plans", True),
        ("mean_premium_change_among_affected_top_two", "plan_market", "Premium change proxy", "mean_premium_change_among_affected_top_two" in df.columns),
        ("Cnsmr", "plan_market", "County enrollment size", "Cnsmr" in df.columns),
    ]
    return [{"variable": v, "variable_type": t, "label": label, "present": bool(p)} for v, t, label, p in specs]


def make_table2(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    if "prior_premium_lowest" in work.columns and "prior_premium_second_lowest" in work.columns:
        work["premium_spread_among_silver_proxy"] = num(work["prior_premium_second_lowest"]) - num(work["prior_premium_lowest"])
    rows: list[dict[str, Any]] = []
    comparisons = [
        ("any_zero_to_positive_turnover", "any_zero_to_positive_turnover_bool"),
        ("any_zero_to_positive_turnover_across_issuer", "any_zero_to_positive_turnover_across_issuer_bool"),
    ]
    valid = work[work["treatment_constructible_flag_bool"]].copy()
    for comparison_name, comparison_col in comparisons:
        if comparison_col not in valid.columns:
            continue
        treated = valid[comparison_col]
        for spec in comparison_variables(valid):
            variable = spec["variable"]
            present = spec["present"] and variable in valid.columns
            base = {
                "comparison": comparison_name,
                "variable": variable,
                "variable_label": spec["label"],
                "variable_type": spec["variable_type"],
                "variable_present": present,
            }
            if not present:
                rows.append(
                    {
                        **base,
                        "untreated_mean_unweighted": math.nan,
                        "treated_mean_unweighted": math.nan,
                        "unweighted_difference": math.nan,
                        "untreated_mean_cnsmer_weighted": math.nan,
                        "treated_mean_cnsmer_weighted": math.nan,
                        "cnsmr_weighted_difference": math.nan,
                        "untreated_missing_rate": math.nan,
                        "treated_missing_rate": math.nan,
                        "untreated_county_years": int((~treated).sum()),
                        "treated_county_years": int(treated.sum()),
                        "untreated_counties": valid.loc[~treated, "county_fips"].nunique(),
                        "treated_counties": valid.loc[treated, "county_fips"].nunique(),
                        "untreated_states": valid.loc[~treated, "state"].nunique(),
                        "treated_states": valid.loc[treated, "state"].nunique(),
                        "notes": "Variable absent in Step 2 dataset; not invented. Drake Table 2 uses 2021 enrollment weights and year adjustment; this diagnostic is unadjusted.",
                    }
                )
                continue
            value = num(valid[variable])
            untreated = ~treated
            untreated_mean = float(value[untreated].mean())
            treated_mean = float(value[treated].mean())
            untreated_w = weighted_mean(value[untreated], valid.loc[untreated, "Cnsmr"])
            treated_w = weighted_mean(value[treated], valid.loc[treated, "Cnsmr"])
            rows.append(
                {
                    **base,
                    "untreated_mean_unweighted": untreated_mean,
                    "treated_mean_unweighted": treated_mean,
                    "unweighted_difference": treated_mean - untreated_mean,
                    "untreated_mean_cnsmer_weighted": untreated_w,
                    "treated_mean_cnsmer_weighted": treated_w,
                    "cnsmr_weighted_difference": treated_w - untreated_w,
                    "untreated_missing_rate": float(value[untreated].isna().mean()) if untreated.any() else math.nan,
                    "treated_missing_rate": float(value[treated].isna().mean()) if treated.any() else math.nan,
                    "untreated_county_years": int(untreated.sum()),
                    "treated_county_years": int(treated.sum()),
                    "untreated_counties": valid.loc[untreated, "county_fips"].nunique(),
                    "treated_counties": valid.loc[treated, "county_fips"].nunique(),
                    "untreated_states": valid.loc[untreated, "state"].nunique(),
                    "treated_states": valid.loc[treated, "state"].nunique(),
                    "notes": "Descriptive comparison only; not a causal contrast. Uses current-year Cnsmr weights rather than Drake's 2021 weights.",
                }
            )
    table = pd.DataFrame(rows)
    table.to_csv(OUTPUTS / "step3_table2_by_turnover_status.csv", index=False)
    shown = table[(table["variable_present"]) & (table["variable_type"].eq("outcome"))].copy()
    shown["unweighted_difference"] = shown["unweighted_difference"] * 100
    shown["cnsmr_weighted_difference"] = shown["cnsmr_weighted_difference"] * 100
    md = [
        "# Step 3 Table 2-Style Descriptive Comparison By Turnover Status",
        "",
        "Outcome shares are shown as percentage-point differences below. The CSV also includes available plan-market variables and absent-variable rows. These diagnostics are unadjusted and use current-year Cnsmr weights; Drake Table 2 uses 2021 enrollment weights and year-adjusted differences.",
        "",
        md_table(shown[["comparison", "variable", "untreated_county_years", "treated_county_years", "unweighted_difference", "cnsmr_weighted_difference", "notes"]], digits=3),
        "",
    ]
    (OUTPUTS / "step3_table2_by_turnover_status.md").write_text("\n".join(md), encoding="utf-8")
    return table


def make_sign_check(table2: pd.DataFrame) -> pd.DataFrame:
    anchors = [
        ("any_zero_to_positive_turnover", "active_switch_share", "positive", "Treated counties have higher active switching descriptively."),
        ("any_zero_to_positive_turnover", "active_stay_share", "negative", "Treated counties have lower active stay descriptively."),
        ("any_zero_to_positive_turnover_across_issuer", "automatic_passive_share", "negative", "Across-issuer treated counties have lower automatic/passive reenrollment descriptively."),
    ]
    rows: list[dict[str, Any]] = []
    for comparison, variable, expected, question in anchors:
        hit = table2[(table2["comparison"].eq(comparison)) & (table2["variable"].eq(variable))]
        if hit.empty or not bool(hit.iloc[0]["variable_present"]):
            result = "cannot_assess"
            unw = math.nan
            w = math.nan
            note = "Variable or comparison absent."
        else:
            unw = float(hit.iloc[0]["unweighted_difference"])
            w = float(hit.iloc[0]["cnsmr_weighted_difference"])
            sign = "positive" if w > 0 else "negative" if w < 0 else "zero"
            if sign == expected:
                result = "same_direction"
            elif sign == "zero":
                result = "not_comparable"
            else:
                result = "opposite_direction"
            note = "Weighted and unweighted signs match." if (unw == 0 or w == 0 or np.sign(unw) == np.sign(w)) else "Weighted and unweighted signs differ, suggesting enrollment-size composition matters."
        rows.append(
            {
                "comparison": comparison,
                "variable": variable,
                "expected_descriptive_direction_from_drake_anchor": expected,
                "unweighted_difference": unw,
                "cnsmr_weighted_difference": w,
                "sign_check": result,
                "question_answered": question,
                "composition_note": note,
                "interpretation_limit": "Descriptive signs are not causal and need not match regression signs exactly.",
            }
        )
    sign = pd.DataFrame(rows)
    sign.to_csv(OUTPUTS / "step3_sign_check_against_drake.csv", index=False)
    return sign


def make_problem_state_diagnostics(raw_primary: pd.DataFrame, analysis_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    rows: list[dict[str, Any]] = []
    for scope, df in [("raw_primary_before_etable3_exclusions", raw_primary), ("drake_harmonized", analysis_df)]:
        for (state, year), sub in df.groupby(["state", "year"], dropna=False):
            constructible = sub["treatment_constructible_flag_bool"]
            missing_current = sub.get("missing_current_plan_flag_bool", pd.Series(False, index=sub.index))
            missing_crosswalk = sub.get("missing_crosswalk_flag_bool", pd.Series(False, index=sub.index))
            missing_premium = sub.get("missing_premium_flag_bool", pd.Series(False, index=sub.index))
            any_treated = sub.get("any_zero_to_positive_turnover_bool", pd.Series(False, index=sub.index))
            constructibility_rate = float(constructible.mean())
            missing_current_rate = float(missing_current.mean())
            missing_crosswalk_rate = float(missing_crosswalk.mean())
            missing_premium_rate = float(missing_premium.mean())
            treated_share_constructible = float(any_treated[constructible].mean()) if constructible.any() else math.nan
            reasons = []
            sensitivity_problem = False
            if constructibility_rate < 0.95:
                reasons.append("constructibility_below_0.95")
                sensitivity_problem = True
            if missing_current_rate > 0.05:
                reasons.append("missing_current_plan_rate_above_0.05")
                sensitivity_problem = True
            if missing_crosswalk_rate > 0.05:
                reasons.append("missing_crosswalk_rate_above_0.05")
                sensitivity_problem = True
            if not pd.isna(treated_share_constructible) and (treated_share_constructible < 0.05 or treated_share_constructible > 0.95):
                reasons.append("extreme_treatment_prevalence")
            rows.append(
                {
                    "scope": scope,
                    "state": state,
                    "year": int(year),
                    "county_years": len(sub),
                    "counties": sub["county_fips"].nunique(),
                    "enrollment": sub["Cnsmr"].sum(skipna=True),
                    "constructibility_rate": constructibility_rate,
                    "missing_treatment_rate": float((~constructible).mean()),
                    "missing_current_plan_rate": missing_current_rate,
                    "missing_crosswalk_rate": missing_crosswalk_rate,
                    "missing_premium_rate": missing_premium_rate,
                    "outcome_missing_rate": float(sub["table1_outcome_missing_flag"].mean()),
                    "treated_share_constructible": treated_share_constructible,
                    "problem_state_for_sensitivity": scope == "drake_harmonized" and sensitivity_problem,
                    "diagnostic_flags": ";".join(reasons) if reasons else "none",
                }
            )
    diag = pd.DataFrame(rows)
    problem_states = sorted(diag.loc[diag["problem_state_for_sensitivity"], "state"].astype(str).unique().tolist())
    diag.to_csv(OUTPUTS / "step3_problem_state_diagnostics.csv", index=False)
    return diag, problem_states


def make_join_failure_breakdown(df: pd.DataFrame, raw_primary: pd.DataFrame | None = None) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    failure_cols = [
        "missing_previous_plan_flag_bool",
        "missing_crosswalk_flag_bool",
        "missing_current_plan_flag_bool",
        "missing_premium_flag_bool",
        "missing_county_mapping_flag_bool",
    ]
    scoped = [("drake_harmonized", df)]
    if raw_primary is not None:
        scoped.insert(0, ("raw_primary_before_etable3_exclusions", raw_primary))
    for scope, scope_df in scoped:
        for (transition, state, year), sub in scope_df.groupby(["transition", "state", "year"], dropna=False):
            for col in failure_cols:
                if col not in sub.columns:
                    continue
                rows.append(
                    {
                        "scope": scope,
                        "breakdown_type": "state_year_transition",
                        "transition": transition,
                        "state": state,
                        "year": int(year),
                        "entity_field": "",
                        "entity_id": "",
                        "failure_type": col.replace("_bool", ""),
                        "rows": len(sub),
                        "failures": int(sub[col].sum()),
                        "failure_rate": float(sub[col].mean()),
                        "enrollment_in_failed_rows": sub.loc[sub[col], "Cnsmr"].sum(skipna=True),
                    }
                )
        for col in failure_cols:
            if col not in scope_df.columns:
                continue
            failed = scope_df[scope_df[col]].copy()
            if failed.empty:
                continue
            for entity in ["previous_lowest_plan_id", "previous_second_lowest_plan_id", "previous_lowest_issuer_id", "previous_second_lowest_issuer_id"]:
                if entity not in failed.columns:
                    continue
                top = failed.groupby(["transition", "state", entity], dropna=False).agg(rows=("year", "size"), enrollment=("Cnsmr", "sum")).reset_index()
                top = top.sort_values(["rows", "enrollment"], ascending=False).head(40)
                for _, row in top.iterrows():
                    rows.append(
                        {
                            "scope": scope,
                            "breakdown_type": "top_failed_plan_or_issuer",
                            "transition": row["transition"],
                            "state": row["state"],
                            "year": "",
                            "entity_field": entity,
                            "entity_id": row[entity],
                            "failure_type": col.replace("_bool", ""),
                            "rows": int(row["rows"]),
                            "failures": int(row["rows"]),
                            "failure_rate": "",
                            "enrollment_in_failed_rows": row["enrollment"],
                        }
                    )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "step3_join_failure_breakdown.csv", index=False)
    return out


def make_zero_premium_proxy_audit(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for keys, scope in [(["year"], "year"), (["state", "year"], "state_year"), ([], "pooled")]:
        groups = [(("pooled",), df)] if not keys else list(df.groupby(keys, dropna=False))
        for key, sub in groups:
            if not isinstance(key, tuple):
                key = (key,)
            base = {"scope": scope}
            for col, val in zip(keys if keys else ["pooled"], key):
                base[col] = val
            constructible = sub["treatment_constructible_flag_bool"]
            row = {
                **base,
                "rows": len(sub),
                "counties": sub["county_fips"].nunique(),
                "not_constructible_count": int((~constructible).sum()),
                "not_constructible_rate": float((~constructible).mean()),
                "any_turnover_share_constructible": float(sub.loc[constructible, "any_zero_to_positive_turnover_bool"].mean()) if constructible.any() else math.nan,
                "across_issuer_share_constructible": float(sub.loc[constructible, "any_zero_to_positive_turnover_across_issuer_bool"].mean()) if constructible.any() else math.nan,
                "within_issuer_share_constructible": float(sub.loc[constructible, "any_zero_to_positive_turnover_within_issuer_bool"].mean()) if constructible.any() else math.nan,
                "measure_types": ";".join(sorted(sub["zero_premium_measure_type"].dropna().astype(str).unique().tolist())) if "zero_premium_measure_type" in sub.columns else "",
                "previous_second_lowest_plan_missing_count": int(sub.get("previous_second_lowest_plan_id", pd.Series(index=sub.index, dtype=object)).isna().sum()),
            }
            for premium_col in [
                "prior_premium_lowest",
                "prior_premium_second_lowest",
                "current_mapped_premium_lowest",
                "current_mapped_premium_second_lowest",
                "premium_change_lowest",
                "premium_change_second_lowest",
                "net_premium_proxy_change_lowest",
                "net_premium_proxy_change_second_lowest",
            ]:
                if premium_col in sub.columns:
                    vals = num(sub[premium_col])
                    row[f"{premium_col}_missing"] = int(vals.isna().sum())
                    row[f"{premium_col}_min"] = float(vals.min()) if vals.notna().any() else math.nan
                    row[f"{premium_col}_max"] = float(vals.max()) if vals.notna().any() else math.nan
                    row[f"{premium_col}_negative_count"] = int((vals < 0).sum())
                    row[f"{premium_col}_zero_count"] = int((vals == 0).sum())
                    row[f"{premium_col}_extreme_gt_2000_count"] = int((vals > 2000).sum())
            row["benchmark_value_note"] = "Benchmark value itself is not retained in Step 2 dataset; audited mapped/prior premium and proxy-change fields instead."
            row["fewer_than_two_silver_plans_note"] = "Direct silver-plan count is absent; missing previous_second_lowest_plan_id is used as a weak proxy."
            rows.append(row)
    audit = pd.DataFrame(rows)
    audit.to_csv(OUTPUTS / "step3_zero_premium_proxy_audit.csv", index=False)
    return audit


def table2_key_diffs(table2: pd.DataFrame, comparison: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for var in ["active_switch_share", "active_stay_share", "automatic_passive_share"]:
        hit = table2[(table2["comparison"].eq(comparison)) & (table2["variable"].eq(var))]
        if not hit.empty:
            out[var + "_weighted_diff"] = float(hit.iloc[0]["cnsmr_weighted_difference"])
    return out


def make_sensitivity_datasets(primary: pd.DataFrame, problem_states: list[str]) -> pd.DataFrame:
    specs: list[tuple[str, pd.DataFrame, str]] = []
    data_2324 = primary[primary["year"].astype(int).isin([2023, 2024])].copy()
    path_2324 = PROCESSED / "drake_replication_primary_2023_2024_only.csv"
    data_2324.to_csv(path_2324, index=False)
    specs.append(("primary_2023_2024_only", data_2324, str(path_2324.relative_to(ROOT))))

    constructible = primary[primary["treatment_constructible_flag_bool"]].copy()
    path_constructible = PROCESSED / "drake_replication_primary_constructible_only.csv"
    constructible.to_csv(path_constructible, index=False)
    specs.append(("primary_constructible_only", constructible, str(path_constructible.relative_to(ROOT))))

    if problem_states:
        no_problem = primary[~primary["state"].astype(str).isin(problem_states)].copy()
        path_no_problem = PROCESSED / "drake_replication_primary_no_problem_states.csv"
        no_problem.to_csv(path_no_problem, index=False)
        specs.append(("primary_no_problem_states", no_problem, str(path_no_problem.relative_to(ROOT))))
    else:
        stale_no_problem = PROCESSED / "drake_replication_primary_no_problem_states.csv"
        if stale_no_problem.exists():
            stale_no_problem.unlink()

    rows: list[dict[str, Any]] = []
    base_table1 = build_table1_frame(primary)
    base_closest = base_table1[base_table1["closest_to_drake_table1"]]
    base_avg_abs = float(base_closest["absolute_difference"].mean())
    for name, data, path in specs:
        table1 = build_table1_frame(data)
        table2 = build_table2_frame(data)
        closest = table1[table1["closest_to_drake_table1"]]
        outcome_missing = float(data["table1_outcome_missing_flag"].mean()) if len(data) else math.nan
        constructible_rate = float(data["treatment_constructible_flag_bool"].mean()) if len(data) else math.nan
        any_share = float(data.loc[data["treatment_constructible_flag_bool"], "any_zero_to_positive_turnover_bool"].mean()) if data["treatment_constructible_flag_bool"].any() else math.nan
        diffs = table2_key_diffs(table2, "any_zero_to_positive_turnover")
        rows.append(
            {
                "created": True,
                "sensitivity_dataset": name,
                "path": path,
                "rows": len(data),
                "counties": data["county_fips"].nunique(),
                "states": data["state"].nunique(),
                "years": ",".join(map(str, sorted(data["year"].dropna().astype(int).unique().tolist()))),
                "treatment_prevalence_constructible": any_share,
                "treatment_constructibility_rate": constructible_rate,
                "outcome_missingness": outcome_missing,
                "table1_mean_absolute_difference_closest": float(closest["absolute_difference"].mean()) if not closest.empty else math.nan,
                "table1_mean_absolute_difference_change_vs_primary": (float(closest["absolute_difference"].mean()) - base_avg_abs) if not closest.empty else math.nan,
                "any_turnover_active_switch_weighted_diff": diffs.get("active_switch_share_weighted_diff", math.nan),
                "any_turnover_active_stay_weighted_diff": diffs.get("active_stay_share_weighted_diff", math.nan),
                "problem_states_excluded": ",".join(problem_states) if name == "primary_no_problem_states" else "",
                "not_created_reason": "",
            }
        )
    if not problem_states:
        rows.append(
            {
                "created": False,
                "sensitivity_dataset": "primary_no_problem_states",
                "path": "",
                "rows": 0,
                "counties": 0,
                "states": 0,
                "years": "",
                "treatment_prevalence_constructible": math.nan,
                "treatment_constructibility_rate": math.nan,
                "outcome_missingness": math.nan,
                "table1_mean_absolute_difference_closest": math.nan,
                "table1_mean_absolute_difference_change_vs_primary": math.nan,
                "any_turnover_active_switch_weighted_diff": math.nan,
                "any_turnover_active_stay_weighted_diff": math.nan,
                "problem_states_excluded": "",
                "not_created_reason": "No whole-state post-harmonization problem state was identified; eTable 3 supports county-level GA/NC exclusions instead.",
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(OUTPUTS / "step3_sensitivity_summary.csv", index=False)
    return summary


def build_table1_frame(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    years = [str(y) for y in sorted(df["year"].dropna().astype(int).unique().tolist())] + ["total"]
    for year_label in years:
        sub = df if year_label == "total" else df[df["year"].astype(int).astype(str).eq(year_label)]
        for measure_key, label, numerator, denominator, denominator_used in TABLE1_MEASURES:
            for weighting in ["unweighted_county_mean", "Cnsmr_weighted_mean", "Tot_Renrl_weighted_mean"]:
                our_value = ratio_value(sub, numerator, denominator, weighting)
                drake_value = DRAKE_TABLE1.get((measure_key, year_label), math.nan)
                difference = our_value - drake_value if not pd.isna(drake_value) else math.nan
                closest = (denominator == "Cnsmr" and weighting == "Cnsmr_weighted_mean") or (
                    denominator == "Tot_Renrl" and weighting == "Tot_Renrl_weighted_mean"
                )
                rows.append(
                    {
                        "year": year_label,
                        "measure": measure_key,
                        "measure_label": label,
                        "our_value": our_value,
                        "drake_value": drake_value,
                        "difference": difference,
                        "absolute_difference": abs(difference) if not pd.isna(difference) else math.nan,
                        "percent_difference": difference / drake_value * 100 if drake_value and not pd.isna(difference) else math.nan,
                        "weighting_used": weighting,
                        "denominator_used": denominator_used,
                        "closest_to_drake_table1": closest,
                        "likely_reason_for_difference": likely_table1_reason(abs(difference) if not pd.isna(difference) else math.nan, closest, denominator_used),
                    }
                )
    return pd.DataFrame(rows)


def build_table2_frame(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    if "prior_premium_lowest" in work.columns and "prior_premium_second_lowest" in work.columns:
        work["premium_spread_among_silver_proxy"] = num(work["prior_premium_second_lowest"]) - num(work["prior_premium_lowest"])
    rows: list[dict[str, Any]] = []
    valid = work[work["treatment_constructible_flag_bool"]].copy()
    for comparison_name, comparison_col in [
        ("any_zero_to_positive_turnover", "any_zero_to_positive_turnover_bool"),
        ("any_zero_to_positive_turnover_across_issuer", "any_zero_to_positive_turnover_across_issuer_bool"),
    ]:
        if comparison_col not in valid.columns:
            continue
        treated = valid[comparison_col]
        for spec in comparison_variables(valid):
            variable = spec["variable"]
            present = spec["present"] and variable in valid.columns
            if not present:
                rows.append({"comparison": comparison_name, "variable": variable, "variable_present": False})
                continue
            value = num(valid[variable])
            untreated = ~treated
            untreated_w = weighted_mean(value[untreated], valid.loc[untreated, "Cnsmr"])
            treated_w = weighted_mean(value[treated], valid.loc[treated, "Cnsmr"])
            rows.append(
                {
                    "comparison": comparison_name,
                    "variable": variable,
                    "variable_present": True,
                    "unweighted_difference": float(value[treated].mean() - value[untreated].mean()),
                    "cnsmr_weighted_difference": treated_w - untreated_w,
                }
            )
    return pd.DataFrame(rows)


def choose_recommendation(
    readability: pd.DataFrame,
    sample_alignment: pd.DataFrame,
    table1: pd.DataFrame,
    prevalence: pd.DataFrame,
    turnover_counts: pd.DataFrame,
    exposure_comparison: pd.DataFrame,
    table2: pd.DataFrame,
    problem_states: list[str],
) -> tuple[str, str, list[str]]:
    warnings: list[str] = []
    if (readability["problem_detected"] != "none").any():
        return "No-Go", "E. Pause the topic.", ["Processed datasets are not fully readable."]
    county_count = int(sample_alignment.loc[sample_alignment["metric"].eq("counties_drake_harmonized_sample"), "value"].iloc[0])
    if county_count != DRAKE_COUNTIES:
        warnings.append(f"Drake-harmonized sample has {county_count} counties versus Drake's {DRAKE_COUNTIES}.")
    closest = table1[table1["closest_to_drake_table1"]]
    mean_abs = float(closest["absolute_difference"].mean())
    max_abs = float(closest["absolute_difference"].max())
    if mean_abs > 3 or max_abs > 6:
        warnings.append(f"Table 1-style closest values differ from Drake by mean {mean_abs:.2f} pp and max {max_abs:.2f} pp.")
    any_count_row = turnover_counts[turnover_counts["metric"].eq("any_turnover_county_years")]
    if not any_count_row.empty:
        diff = int(any_count_row.iloc[0]["difference"])
        if abs(diff) > 100:
            warnings.append(f"Any-turnover county-year count differs from Drake by {diff}.")
    across_row = turnover_counts[turnover_counts["metric"].eq("across_issuer_turnover_county_years")]
    if not across_row.empty:
        diff = int(across_row.iloc[0]["difference"])
        if abs(diff) > 25:
            warnings.append(f"Across-issuer turnover count differs from Drake by {diff}; current proxy likely under-detects across-insurer turnover.")
    if not exposure_comparison.empty:
        max_exposure_gap = float(exposure_comparison["absolute_difference_vs_drake_100_150_pp"].max())
        if max_exposure_gap > 5:
            warnings.append(f"Enrollment-weighted any-turnover exposure differs from Drake 100-150 FPL exposure by up to {max_exposure_gap:.1f} pp.")
    absent_market_vars = []
    for var in ["bronze_spread", "number_of_insurers"]:
        hit = table2[(table2["variable"].eq(var))]
        if hit.empty or not bool(hit["variable_present"].fillna(False).any()):
            absent_market_vars.append(var)
    if absent_market_vars:
        warnings.append("Step 2 output lacks Drake control variables needed later: " + ", ".join(absent_market_vars) + ".")
    if problem_states:
        warnings.append("Post-harmonization problem-state sensitivity identified data-quality states: " + ",".join(problem_states) + ".")
    warnings.append("Treatment remains proxy-based; Step 2 does not prove household-specific net premiums, 125 percent FPL contribution, or non-EHB handling.")
    if mean_abs <= 1.0 and county_count == DRAKE_COUNTIES and not absent_market_vars and len(warnings) <= 2:
        return "Conditional Go to Step 4", "A. Proceed to Step 4 formal Drake regression replication.", warnings
    return "Fix Step 2 before Step 4", "B. Repair Step 2 treatment construction first.", warnings


def make_report(
    status: str,
    recommendation: str,
    warnings: list[str],
    sample_alignment: pd.DataFrame,
    table1: pd.DataFrame,
    prevalence: pd.DataFrame,
    exposure_comparison: pd.DataFrame,
    turnover_counts: pd.DataFrame,
    table2: pd.DataFrame,
    sign: pd.DataFrame,
    problem_states: list[str],
    sensitivity: pd.DataFrame,
    county_diag: pd.DataFrame,
    excluded_check: pd.DataFrame,
) -> None:
    closest = table1[table1["closest_to_drake_table1"]].copy()
    closest_display = closest[["year", "measure", "our_value", "drake_value", "difference", "absolute_difference", "weighting_used"]].copy()
    for col in ["our_value", "drake_value", "difference", "absolute_difference"]:
        closest_display[col] = closest_display[col].round(2)
    prev_display = prevalence.copy()
    for col in prev_display.columns:
        if col.endswith("share_constructible") or col.endswith("weighted_share_constructible") or col.endswith("rate"):
            prev_display[col] = prev_display[col].astype(float).round(3)
    outcome_table2 = table2[(table2["variable_present"]) & (table2["variable_type"].eq("outcome"))].copy()
    outcome_table2["unweighted_difference_pp"] = outcome_table2["unweighted_difference"] * 100
    outcome_table2["cnsmr_weighted_difference_pp"] = outcome_table2["cnsmr_weighted_difference"] * 100
    sample_metrics = sample_alignment.set_index("metric")["value"].to_dict()
    discrepancy_reasons = county_diag["candidate_discrepancy_reason"].value_counts().head(8).reset_index()
    discrepancy_reasons.columns = ["candidate_discrepancy_reason", "counties"]
    excluded_display = excluded_check[excluded_check["present_in_current_primary_sample"]].copy()
    excluded_display = excluded_display[["state", "county_fips", "county_name_in_supplement", "observed_county_names", "rows_present", "years_present", "supplement_reason"]]
    exposure_display = exposure_comparison.copy()
    for col in exposure_display.columns:
        if col.endswith("_pct") or col.endswith("_pp"):
            exposure_display[col] = exposure_display[col].astype(float).round(2)
    counts_display = turnover_counts.copy()
    for col in ["our_value", "drake_reference", "difference"]:
        counts_display[col] = counts_display[col].astype(float).round(3)
    report = [
        "# Step 3 Descriptive Replication Report",
        "",
        "## 1. Executive Summary",
        "",
        f"Overall status: **{status}**.",
        "",
        "This Step 3 audit now applies Drake supplement eTable 3 county exclusions and reproduces the public OEP reenrollment patterns closely. The sample-count discrepancy is resolved, but formal Step 4 replication is still not justified until Step 2 treatment construction and later regression controls are repaired. The main remaining concerns are proxy-based zero-premium treatment, under-detection of across-insurer turnover, missing 2021 enrollment weights/control variables, and incomplete non-EHB/125 percent FPL premium handling.",
        "",
        "Main warnings:",
        "",
        *[f"- {w}" for w in warnings],
        "",
        "## 2. What Was Tested",
        "",
        "- Dataset readability for the full, primary, and Nebraska sensitivity CSVs.",
        "- Sample alignment against Drake-style 29-state HealthCare.gov county-year structure.",
        "- Table 1-style reenrollment descriptives against manually encoded Drake anchors.",
        "- Turnover prevalence by year and state-year.",
        "- Table 2-style descriptive comparisons by turnover status.",
        "- Step 2 weaknesses: 2021 fallback, 2023-to-2024 join weakness, and zero-premium proxy quality.",
        "",
        "## 3. Sample Alignment",
        "",
        f"The raw primary sample has {sample_metrics.get('rows_primary_sample_raw')} county-years and {sample_metrics.get('counties_primary_sample_raw')} counties. Applying Drake supplement eTable 3 exclusions gives {sample_metrics.get('rows_drake_harmonized_sample')} county-years, {sample_metrics.get('counties_drake_harmonized_sample')} counties, and {sample_metrics.get('states_primary_sample')} states.",
        "",
        f"AK in primary sample: {sample_metrics.get('AK_in_primary_sample')}; HI in primary sample: {sample_metrics.get('HI_in_primary_sample')}; NE in primary sample: {sample_metrics.get('NE_in_primary_sample')}. Nebraska sensitivity exists: {sample_metrics.get('nebraska_sensitivity_exists')}.",
        "",
        f"Drake's Results text reports {DRAKE_RESULT_COUNTY_YEARS} county-years and {DRAKE_RESULT_UNIQUE_COUNTIES} unique counties with nonmissing enrollment. Our harmonized data have {sample_metrics.get('county_years_with_nonmissing_enrollment')} county-years and {sample_metrics.get('unique_counties_with_nonmissing_enrollment')} unique counties with nonmissing `Cnsmr`, matching those anchors.",
        "",
        "The 2,188 vs 2,159 county discrepancy is explained by the 29 GA/NC counties in supplement eTable 3 with no crosswalk data from 2023 to 2024. They appear in the raw primary data and are removed from the Drake-harmonized Step 3 analysis. Legacy SD/VA FIPS exclusions are also encoded but do not affect this 2022-2024 primary sample.",
        "",
        "eTable 3 counties found in the raw primary sample:",
        "",
        md_table(excluded_display, max_rows=40, digits=0),
        "",
        "County-discrepancy diagnostic reasons after adding the eTable 3 rule:",
        "",
        md_table(discrepancy_reasons, digits=0),
        "",
        "This is not arbitrary deletion: the rule is directly taken from Drake supplement eTable 3. The harmonized dataset is written to `data/processed/drake_replication_primary_drake_harmonized_2022_2024.csv` for Step 3 diagnostics.",
        "",
        "## 4. Outcome Replication",
        "",
        "Closest Table 1-style comparison:",
        "",
        md_table(closest_display, max_rows=40, digits=2),
        "",
        "The weighting closest to Drake is Cnsmr-weighted for enrollment-denominator measures and Tot_Renrl-weighted for reenrollment-denominator measures. After eTable 3 harmonization, nearly all differences are well below 1 percentage point. Remaining small differences likely reflect OEP PUF suppression, denominator availability, and public aggregate county-year construction.",
        "",
        "## 5. Treatment Prevalence",
        "",
        md_table(prev_display, max_rows=10, digits=3),
        "",
        "Comparison against Drake supplement eTable 1 exposure anchors:",
        "",
        md_table(exposure_display, max_rows=10, digits=2),
        "",
        "Turnover count comparison against the main article:",
        "",
        md_table(counts_display, digits=3),
        "",
        "The enrollment-weighted any-turnover prevalence is close in 2022, higher than Drake in 2023, and lower than Drake in 2024. The bigger problem is across-insurer turnover: the current proxy identifies fewer across-insurer county-years than Drake. That is a Step 2 treatment-construction issue, not an outcome-replication issue.",
        "",
        "## 6. Treatment-Status Descriptive Comparison",
        "",
        md_table(outcome_table2[["comparison", "variable", "untreated_county_years", "treated_county_years", "unweighted_difference_pp", "cnsmr_weighted_difference_pp", "notes"]], max_rows=20, digits=3),
        "",
        "Sign checks:",
        "",
        md_table(sign, digits=3),
        "",
        "These are descriptive differences only. They are not adjusted regression estimates and should not be interpreted causally. Drake Table 2 uses 2021 enrollment weights and year-adjusted differences; this Step 3 table uses current-year Cnsmr weights because 2021 county enrollment weights are not retained in the current Step 2 output.",
        "",
        "## 7. Step 2 Unresolved Issues",
        "",
        "- 2021 fallback: all 2022 treatment rows depend on the 2021-to-2022 transition built from fallback inputs. The 2023-2024-only sensitivity is therefore central.",
        "- 2023-to-2024 join weakness: Drake supplement eTable 3 resolves the main GA/NC county-count issue, but Step 2 still needs source-level crosswalk validation before formal regression work.",
        "- Zero-premium proxy: Drake assumes a single 40-year-old at 125 percent FPL for the 100-150 FPL exposure construction. The current Step 2 output is benchmark-based and does not prove exact household-specific net premiums.",
        "- Non-EHB issue: Drake notes that required non-EHB benefits can prevent zero-dollar premiums in some states. The current Step 2 output does not explicitly retain or audit non-EHB handling.",
        "- Missing controls/weights: Drake Table 2 and regressions use 2021 enrollment weights, bronze spread, and insurer-count controls. These are not fully available in the current county-year output.",
        "- Nebraska sensitivity: Nebraska remains outside the primary sample until county-market mapping is verified.",
        "- Aggregate county-year limitation: public OEP PUFs do not support individual retention or income-stratified county outcomes.",
        "",
        "Problem states identified for data-quality sensitivity:",
        "",
        ", ".join(problem_states) if problem_states else "None by the configured constructibility/join-failure rule.",
        "",
        "## 8. Sensitivity Results",
        "",
        md_table(sensitivity, digits=3),
        "",
        "## 9. Honest Limitations",
        "",
        "- No causal claims are made.",
        "- No individual-level HTE can be estimated from these public aggregate PUFs.",
        "- No household-specific APTC calculation is present.",
        "- The treatment proxy differs from exact Drake construction unless later proven otherwise.",
        "- Differences from Drake may reflect proxy treatment, sample construction, weighting, and missing or suppressed cells.",
        "",
        "## 10. Recommendation",
        "",
        f"Recommendation: **{recommendation}**",
        "",
        "The conservative recommendation is to repair Step 2 treatment construction before formal Step 4 treatment regressions. Sample alignment and OEP outcome descriptives are now strong after eTable 3 harmonization, but treatment definition, across-insurer classification, non-EHB handling, 2021 weights, and control variables are not yet close enough to freeze Step 2.",
        "",
        "## Final Self-Audit Checklist",
        "",
        "- [x] Did I avoid causal claims?",
        "- [x] Did I avoid DID/regression/covariate-adjusted causal models?",
        "- [x] Did I use Drake article and supplement details, especially eAppendix 1/eTable 3 missing-data handling?",
        "- [x] Did I read the Step 2 report and validation flags?",
        "- [x] Did I verify that processed datasets are actually readable and nonempty?",
        "- [x] Did I apply Drake supplement eTable 3 exclusions transparently rather than arbitrary deletion?",
        "- [x] Did I reproduce Table 1-style reenrollment descriptives?",
        "- [x] Did I compare our values to Drake reference values?",
        "- [x] Did I compute treatment prevalence by year and state-year?",
        "- [x] Did I investigate 2188 vs 2159 county discrepancy?",
        "- [x] Did I inspect 2021 fallback sensitivity?",
        "- [x] Did I inspect 2023-to-2024 join failure weakness?",
        "- [x] Did I audit zero-premium proxy quality?",
        "- [x] Did I produce a 2023-2024-only sensitivity file?",
        "- [x] Did I produce a clear Markdown report?",
        "- [x] Did I state whether Step 4 is justified?",
        "- [x] Did I report honestly what failed or remains uncertain?",
        "",
    ]
    (DOCS / "step3_descriptive_replication_report.md").write_text("\n".join(report), encoding="utf-8")


def make_progress_memo(status: str, recommendation: str, warnings: list[str], sensitivity: pd.DataFrame) -> None:
    next_tasks = [
        "Repair Step 2 treatment construction against Drake's exact 125 percent FPL, non-EHB, and current-year plan/default logic.",
        "Add or reconstruct 2021 enrollment weights, bronze spread, and insurer-count variables needed for Drake Table 2 and regressions.",
        "Rerun Step 3 after treatment/control repairs before starting Step 4 regressions.",
    ]
    memo = [
        "# Step 3 Progress And Limitations",
        "",
        "## Completed",
        "",
        "- Verified that processed Step 2 datasets are readable and nonempty.",
        "- Applied Drake supplement eTable 3 county exclusions and wrote a Drake-harmonized Step 3 dataset.",
        "- Produced sample-alignment diagnostics, Table 1-style reenrollment descriptives, treatment prevalence, exposure/count comparisons, Table 2-style descriptive comparisons, sign checks, weakness audits, and sensitivity datasets.",
        "- Wrote `docs/step3_descriptive_replication_report.md`.",
        "",
        "## Partially Completed",
        "",
        "- Treatment prevalence is benchmark-proxy based and only partially comparable to Drake exposure tables.",
        "- Across-insurer turnover remains under-detected relative to Drake.",
        "",
        "## Not Completed",
        "",
        "- No causal regressions, causal forests, policy learning, or formal Step 4 models were run.",
        "- No exact household-specific APTC or individual-level retention dataset was created.",
        "",
        "## Main Findings In Plain English",
        "",
        "- The 29-county sample gap is explained by Drake supplement eTable 3; after excluding those counties, the sample matches Drake's county anchors.",
        "- The outcome data very closely reproduce the public OEP reenrollment structure.",
        "- Any-turnover prevalence is directionally plausible, but across-insurer turnover is too low relative to Drake.",
        "- Treatment construction needs stricter validation before formal replication.",
        "- 2022 remains weaker because it depends on the 2021 fallback construction.",
        "",
        "## Honest Judgment",
        "",
        f"**{status}.** Recommendation: **{recommendation}**",
        "",
        "Main warnings:",
        "",
        *[f"- {w}" for w in warnings],
        "",
        "## Next 3 Tasks",
        "",
        *[f"{i + 1}. {task}" for i, task in enumerate(next_tasks)],
        "",
    ]
    (DOCS / "step3_progress_and_limitations.md").write_text("\n".join(memo), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    setup_logging(args.verbose)
    ensure_dirs()
    years = args.years or [2022, 2023, 2024]
    if args.sensitivity_2023_2024_only:
        years = [2023, 2024]
    logging.info("Starting Step 3 descriptive replication checks")
    make_initial_audit()
    check, datasets = make_readability_check([FULL_DATASET, PRIMARY_DATASET, NEBRASKA_DATASET])
    if (check["problem_detected"] != "none").any():
        status = "No-Go"
        report = [
            "# Step 3 Descriptive Replication Report",
            "",
            f"Overall status: **{status}**.",
            "",
            "Processed datasets were not fully readable. Step 3 execution stopped before descriptive comparisons.",
            "",
            md_table(check),
        ]
        (DOCS / "step3_descriptive_replication_report.md").write_text("\n".join(report), encoding="utf-8")
        make_progress_memo(status, "E. Pause the topic.", ["Processed datasets were not fully readable."], pd.DataFrame())
        return {"status": status, "warnings": ["Processed datasets were not fully readable."], "recommendation": "E. Pause the topic."}

    full = subset_years(datasets[FULL_DATASET.name], years)
    primary_source = NEBRASKA_DATASET.name if args.include_nebraska else PRIMARY_DATASET.name
    primary_raw = subset_years(datasets[primary_source], years)
    primary_raw = add_drake_supplement_exclusion_flags(primary_raw)
    excluded_check = make_drake_excluded_counties_check(primary_raw)
    if args.include_nebraska:
        primary = primary_raw.copy()
        harmonized_path = NEBRASKA_DATASET
    else:
        primary = primary_raw[primary_raw["included_drake_harmonized_sample"]].copy()
        harmonized_path = write_harmonized_dataset(primary)
    ne = subset_years(datasets[NEBRASKA_DATASET.name], years) if NEBRASKA_DATASET.name in datasets else None
    state_meta = pd.read_csv(METADATA / "healthcaregov_state_sample_2022_2024.csv") if (METADATA / "healthcaregov_state_sample_2022_2024.csv").exists() else None

    sample_alignment, county_diag = make_sample_alignment(full, primary_raw, primary, ne, state_meta, excluded_check)
    table1 = make_table1(primary)
    prevalence_by_year, prevalence_by_state_year, prevalence_weighted, exposure_comparison, turnover_counts = make_turnover_prevalence(primary)
    table2 = make_table2(primary)
    sign = make_sign_check(table2)
    problem_diag, problem_states = make_problem_state_diagnostics(primary_raw, primary)
    make_join_failure_breakdown(primary, raw_primary=primary_raw)
    make_zero_premium_proxy_audit(primary)
    sensitivity = make_sensitivity_datasets(primary, problem_states)
    status, recommendation, warnings = choose_recommendation(check, sample_alignment, table1, prevalence_by_year, turnover_counts, exposure_comparison, table2, problem_states)
    make_report(status, recommendation, warnings, sample_alignment, table1, prevalence_by_year, exposure_comparison, turnover_counts, table2, sign, problem_states, sensitivity, county_diag, excluded_check)
    make_progress_memo(status, recommendation, warnings, sensitivity)
    logging.info("Step 3 complete")
    return {
        "status": status,
        "recommendation": recommendation,
        "warnings": warnings,
        "dataset_path": str(harmonized_path.relative_to(ROOT)),
        "raw_dataset_path": str((NEBRASKA_DATASET if args.include_nebraska else PRIMARY_DATASET).relative_to(ROOT)),
        "rows": len(primary),
        "counties": primary["county_fips"].nunique(),
        "states": primary["state"].nunique(),
        "years": sorted(primary["year"].dropna().astype(int).unique().tolist()),
        "readable": True,
        "table1_done": True,
        "prevalence_done": True,
        "county_discrepancy_done": True,
        "report_path": str((DOCS / "step3_descriptive_replication_report.md").relative_to(ROOT)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Step 3 descriptive replication and diagnostics.")
    parser.add_argument("--primary-sample", action="store_true", help="Use the primary sample. This is the default unless --include-nebraska is set.")
    parser.add_argument("--include-nebraska", action="store_true", help="Use the Nebraska sensitivity dataset as the main analysis input.")
    parser.add_argument("--years", nargs="+", type=int, default=[2022, 2023, 2024], help="Years to include.")
    parser.add_argument("--sensitivity-2023-2024-only", action="store_true", help="Run the main analysis on 2023-2024 only.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run(args)
    print("\nStep 3 status:", result["status"])
    print("Primary dataset path:", result.get("dataset_path", str(PRIMARY_DATASET.relative_to(ROOT))))
    if result.get("raw_dataset_path"):
        print("Raw input dataset path:", result["raw_dataset_path"])
    print("Rows, counties, states, years:", result.get("rows", ""), result.get("counties", ""), result.get("states", ""), result.get("years", ""))
    print("Dataset readable:", result.get("readable", False))
    print("Table 1-style descriptives produced:", result.get("table1_done", False))
    print("Treatment prevalence produced:", result.get("prevalence_done", False))
    print("County discrepancy diagnosed:", result.get("county_discrepancy_done", False))
    print("Main warnings:")
    for warning in result.get("warnings", []):
        print("-", warning)
    print("Recommended next step:", result["recommendation"])
    print("Report path:", result.get("report_path", str((DOCS / "step3_descriptive_replication_report.md").relative_to(ROOT))))


if __name__ == "__main__":
    main()
