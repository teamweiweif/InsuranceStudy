from __future__ import annotations

import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DESIGN_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "feasibility_audit"

GATE_SUMMARY_PATH = DESIGN_DIR / "second_round_gate_summary.json"
STATE_MONTH_CELLS_PATH = DESIGN_DIR / "second_round_unwinding_state_month_cells.csv"

HPS_DIR = RAW_DIR / "hps" / "2023"
NHIS_DIR = RAW_DIR / "nhis"

HPS_STATE_WEEK_CSV = DESIGN_DIR / "hps_unwinding_crosscheck_state_week_cells.csv"
HPS_SUMMARY_CSV = DESIGN_DIR / "hps_unwinding_crosscheck_summary.csv"
HPS_MD = DESIGN_DIR / "hps_unwinding_crosscheck.md"

NHIS_FEASIBILITY_CSV = DESIGN_DIR / "nhis_public_validation_feasibility.csv"
NHIS_FEASIBILITY_MD = DESIGN_DIR / "nhis_public_validation_feasibility.md"


@dataclass(frozen=True)
class HpsWeekMeta:
    week: int
    start_date: str
    end_date: str
    reference_month: int


HPS_WEEKS = [
    HpsWeekMeta(60, "2023-07-26", "2023-08-07", 8),
    HpsWeekMeta(61, "2023-08-23", "2023-09-04", 9),
    HpsWeekMeta(62, "2023-09-20", "2023-10-02", 10),
    HpsWeekMeta(63, "2023-10-18", "2023-10-30", 10),
]

NHIS_YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
NHIS_INSURANCE_ACCESS_VARS = [
    "COVER_A",
    "NOTCOV_A",
    "MEDICAID_A",
    "PRIVATE_A",
    "HICOSTR1_A",
    "HICOSTR2_A",
    "USUALPL_A",
    "RSNHICOST_A",
    "HISTOPCOST_A",
    "PRDNCOV1_A",
    "PRDNCOV2_A",
    "PRRXCOV1_A",
    "PRRXCOV2_A",
    "MCDNCOV_A",
    "MCVSCOV_A",
    "SINCOVRX_A",
    "SINCOVVS_A",
    "SINCOVDE_A",
]
NHIS_GEOGRAPHY_CANDIDATES = [
    "STATE",
    "STATE_A",
    "STATEFIP",
    "STATEFIP_A",
    "REGION",
    "REGION_A",
    "INTV_MON",
    "INTV_QRT",
]


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna() & (weights > 0)
    if not mask.any():
        return math.nan
    v = values.loc[mask].astype(float)
    w = weights.loc[mask].astype(float)
    return float(np.average(v, weights=w))


def weighted_corr(x: pd.Series, y: pd.Series, w: pd.Series) -> float:
    mask = x.notna() & y.notna() & w.notna() & (w > 0)
    if mask.sum() < 3:
        return math.nan
    xv = x.loc[mask].astype(float).to_numpy()
    yv = y.loc[mask].astype(float).to_numpy()
    wv = w.loc[mask].astype(float).to_numpy()
    x_mean = np.average(xv, weights=wv)
    y_mean = np.average(yv, weights=wv)
    x_center = xv - x_mean
    y_center = yv - y_mean
    cov = np.average(x_center * y_center, weights=wv)
    x_var = np.average(x_center**2, weights=wv)
    y_var = np.average(y_center**2, weights=wv)
    if x_var <= 0 or y_var <= 0:
        return math.nan
    return float(cov / np.sqrt(x_var * y_var))


def hps_zip_for_week(week: int) -> Path:
    return HPS_DIR / f"HPS_Week{week}_PUF_CSV.zip"


def load_gate_choice() -> tuple[str, str, str]:
    gate = json.loads(GATE_SUMMARY_PATH.read_text(encoding="utf-8"))
    choice = gate["timing_choice"]
    return choice["exposure_family"], choice["exposure_variant"], choice["alignment"]


def load_state_month_exposure(exposure_variant: str, alignment: str) -> pd.DataFrame:
    exposure_col = f"{exposure_variant}_{alignment}"
    cols = ["tehc_st_fips", "reference_year", "MONTHCODE", "state_abbreviation", exposure_col]
    df = pd.read_csv(STATE_MONTH_CELLS_PATH, usecols=cols)
    df = df.loc[df["reference_year"] == 2023].copy()
    df["tehc_st_fips"] = pd.to_numeric(df["tehc_st_fips"], errors="coerce")
    df["MONTHCODE"] = pd.to_numeric(df["MONTHCODE"], errors="coerce")
    df = df.rename(columns={exposure_col: "chosen_exposure"})
    df = (
        df.dropna(subset=["tehc_st_fips", "MONTHCODE"])
        .drop_duplicates(subset=["tehc_st_fips", "MONTHCODE"])
        .sort_values(["tehc_st_fips", "MONTHCODE"])
        .reset_index(drop=True)
    )
    return df


def load_single_hps_week(meta: HpsWeekMeta) -> pd.DataFrame:
    usecols = ["EST_ST", "PWEIGHT", "TBIRTH_YEAR", "HLTHINS4", "PUBHLTH", "PRIVHLTH"]
    zip_path = hps_zip_for_week(meta.week)
    with zipfile.ZipFile(zip_path) as zf:
        csv_name = next(name for name in zf.namelist() if name.lower().endswith(".csv") and "repwgt" not in name.lower())
        with zf.open(csv_name) as handle:
            df = pd.read_csv(handle, usecols=usecols, low_memory=False)

    df["state_fips"] = pd.to_numeric(df["EST_ST"], errors="coerce")
    df["person_weight"] = pd.to_numeric(df["PWEIGHT"], errors="coerce")
    df["birth_year"] = pd.to_numeric(df["TBIRTH_YEAR"], errors="coerce")
    df["age"] = 2023 - df["birth_year"]
    df = df.loc[
        df["state_fips"].notna()
        & df["person_weight"].notna()
        & (df["person_weight"] > 0)
        & df["age"].between(18, 64, inclusive="both")
    ].copy()

    df["current_medicaid"] = pd.to_numeric(df["HLTHINS4"], errors="coerce").eq(1).astype(float)
    df["uninsured"] = (
        pd.to_numeric(df["PRIVHLTH"], errors="coerce").eq(2)
        & pd.to_numeric(df["PUBHLTH"], errors="coerce").eq(2)
    ).astype(float)
    df["public_coverage"] = pd.to_numeric(df["PUBHLTH"], errors="coerce").eq(1).astype(float)

    grouped = (
        df.groupby("state_fips", dropna=False)
        .apply(
            lambda g: pd.Series(
                {
                    "respondents": int(len(g)),
                    "respondent_weight_sum": float(g["person_weight"].sum()),
                    "current_medicaid_rate": weighted_mean(g["current_medicaid"], g["person_weight"]),
                    "uninsured_rate": weighted_mean(g["uninsured"], g["person_weight"]),
                    "public_coverage_rate": weighted_mean(g["public_coverage"], g["person_weight"]),
                }
            ),
            include_groups=False,
        )
        .reset_index()
    )
    grouped["week"] = meta.week
    grouped["start_date"] = meta.start_date
    grouped["end_date"] = meta.end_date
    grouped["reference_month"] = meta.reference_month
    return grouped


def load_hps_state_week_cells() -> pd.DataFrame:
    frames = [load_single_hps_week(meta) for meta in HPS_WEEKS]
    return pd.concat(frames, ignore_index=True)


def summarize_hps_crosscheck(
    state_week: pd.DataFrame,
    exposure_family: str,
    exposure_variant: str,
    alignment: str,
) -> pd.DataFrame:
    summary_rows: list[dict[str, object]] = []
    for outcome in ["current_medicaid_rate", "uninsured_rate", "public_coverage_rate"]:
        outcome_df = state_week.loc[state_week["chosen_exposure"].notna() & state_week[outcome].notna()].copy()
        if outcome_df.empty:
            continue
        corr = weighted_corr(outcome_df["chosen_exposure"], outcome_df[outcome], outcome_df["respondent_weight_sum"])
        tertile_codes = pd.qcut(
            outcome_df["chosen_exposure"].rank(method="first"),
            q=3,
            labels=["low", "mid", "high"],
        )
        outcome_df["exposure_tertile"] = tertile_codes.astype(str)
        low = outcome_df.loc[outcome_df["exposure_tertile"] == "low"]
        high = outcome_df.loc[outcome_df["exposure_tertile"] == "high"]
        low_rate = weighted_mean(low[outcome], low["respondent_weight_sum"])
        high_rate = weighted_mean(high[outcome], high["respondent_weight_sum"])
        summary_rows.append(
            {
                "dataset": "HPS",
                "reference_year": 2023,
                "window": "weeks_60_63_end_month_mapping",
                "exposure_family": exposure_family,
                "exposure_variant": exposure_variant,
                "alignment": alignment,
                "outcome": outcome,
                "support_rows": int(len(outcome_df)),
                "support_weight": float(outcome_df["respondent_weight_sum"].sum()),
                "estimate_or_contrast": corr,
                "direction_flag": "positive" if corr > 0 else ("negative" if corr < 0 else "zero"),
                "notes": "weighted_state_week_correlation",
            }
        )
        summary_rows.append(
            {
                "dataset": "HPS",
                "reference_year": 2023,
                "window": "weeks_60_63_end_month_mapping",
                "exposure_family": exposure_family,
                "exposure_variant": exposure_variant,
                "alignment": alignment,
                "outcome": outcome,
                "support_rows": int(len(outcome_df)),
                "support_weight": float(outcome_df["respondent_weight_sum"].sum()),
                "estimate_or_contrast": high_rate - low_rate,
                "direction_flag": "positive" if (high_rate - low_rate) > 0 else ("negative" if (high_rate - low_rate) < 0 else "zero"),
                "notes": "high_minus_low_exposure_tertile",
            }
        )
    return pd.DataFrame(summary_rows)


def write_hps_markdown(
    state_week: pd.DataFrame,
    summary_df: pd.DataFrame,
    exposure_family: str,
    exposure_variant: str,
    alignment: str,
) -> None:
    nonmissing = state_week["chosen_exposure"].notna().sum()
    lines = [
        "# HPS Unwinding Cross-Check",
        "",
        "## Purpose",
        "",
        "This is a deliberately lightweight external validation screen. It does not attempt to reproduce the SIPP transition design.",
        "",
        f"- chosen exposure from second-round gate: `{exposure_family} / {exposure_variant} / {alignment}`",
        "- HPS window used here: Weeks 60-63 in 2023",
        "- state-week outcomes are mapped to monthly CMS exposure using the survey end-month",
        "- weights: `PWEIGHT`",
        "- age restriction: adults 18-64",
        "",
        "Week-date mapping source: U.S. Census Bureau 2023 Household Pulse Survey Data Tables page.",
        "https://www.census.gov/data/tables/time-series/demo/hhp/2023.html",
        "",
        "## Support",
        "",
        f"- state-week cells: `{len(state_week)}`",
        f"- state-week cells with nonmissing exposure: `{nonmissing}`",
        f"- total respondent weight across kept cells: `{round(state_week['respondent_weight_sum'].sum(), 2)}`",
        "",
        "## Summary",
        "",
        "| outcome | statistic | value | sign |",
        "| --- | --- | --- | --- |",
    ]
    for _, row in summary_df.iterrows():
        lines.append(
            f"| {row['outcome']} | {row['notes']} | {round(float(row['estimate_or_contrast']), 4)} | {row['direction_flag']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `current_medicaid_rate` should move negative if higher manual-renewal burden is associated with more current coverage loss.",
            "- `uninsured_rate` should move positive if the same burden also shows up as loss into no coverage.",
            "- `public_coverage_rate` is included as a looser cross-check because HPS public coverage is broader than Medicaid.",
            "",
            "## Limits",
            "",
            "- HPS is a repeated cross-section, not a person-month panel.",
            "- This cross-check uses late-2023 weeks only, so support is much thinner than the SIPP design.",
            "- The month mapping is mechanical and should not be overinterpreted as a clean event-study alignment.",
            "- The validation is only meant to show whether the selected SIPP signal is completely isolated or has a rough echo in another public source.",
        ]
    )
    HPS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_nhis_header(year: int) -> list[str]:
    zip_path = NHIS_DIR / str(year) / f"adult{str(year)[-2:]}csv.zip"
    with zipfile.ZipFile(zip_path) as zf:
        csv_name = next(name for name in zf.namelist() if name.lower().endswith(".csv"))
        with zf.open(csv_name) as handle:
            header = handle.readline().decode("utf-8-sig").strip().split(",")
    return header


def build_nhis_feasibility() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for year in NHIS_YEARS:
        header = read_nhis_header(year)
        header_set = set(header)
        geography_present = [var for var in NHIS_GEOGRAPHY_CANDIDATES if var in header_set]
        insurance_present = [var for var in NHIS_INSURANCE_ACCESS_VARS if var in header_set]
        rows.append(
            {
                "dataset": "NHIS",
                "reference_year": year,
                "adult_zip": str(NHIS_DIR / str(year) / f"adult{str(year)[-2:]}csv.zip"),
                "column_count": len(header),
                "geography_vars_present": "; ".join(geography_present),
                "state_var_present": any(var in header_set for var in ["STATE", "STATE_A", "STATEFIP", "STATEFIP_A"]),
                "region_var_present": any(var in header_set for var in ["REGION", "REGION_A"]),
                "month_var_present": "INTV_MON" in header_set,
                "quarter_var_present": "INTV_QRT" in header_set,
                "insurance_access_vars_present": "; ".join(insurance_present),
                "insurance_access_var_count": len(insurance_present),
                "validation_use_case": (
                    "national_or_region_descriptive_only"
                    if not any(var in header_set for var in ["STATE", "STATE_A", "STATEFIP", "STATEFIP_A"])
                    else "state_period_merge_feasible"
                ),
            }
        )
    return pd.DataFrame(rows)


def write_nhis_markdown(feasibility_df: pd.DataFrame) -> None:
    lines = [
        "# NHIS Public Validation Feasibility",
        "",
        "## Purpose",
        "",
        "This audit checks whether public-use NHIS adult files can support the planned state-period unwinding validation.",
        "",
        "## Result",
        "",
        "- Public-use NHIS keeps useful insurance and access variables.",
        "- Public-use NHIS does not expose a state identifier in the adult files audited here.",
        "- That means the current unwinding exposure stack cannot be merged into NHIS at the state-period level without restricted geography.",
        "",
        "## What NHIS Still Can Do",
        "",
        "- National descriptive validation of coverage or access patterns.",
        "- Region-level descriptive checks, since `REGION` is present.",
        "- Companion descriptive appendix work if the paper later needs another public survey voice.",
        "",
        "## Why It Is Not the Main External Check Here",
        "",
        "- The selected SIPP design depends on state-month exposure variation.",
        "- Without public state geography, NHIS cannot provide the same kind of late-2023 state-period screen.",
        "- For that reason, HPS remains the only lightweight external screen run in this round.",
        "",
        "## Audited Years",
        "",
        "| year | state_var_present | region_var_present | month_var_present | quarter_var_present | insurance_access_var_count | validation_use_case |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, row in feasibility_df.iterrows():
        lines.append(
            f"| {row['reference_year']} | {row['state_var_present']} | {row['region_var_present']} | {row['month_var_present']} | {row['quarter_var_present']} | {row['insurance_access_var_count']} | {row['validation_use_case']} |"
        )
    NHIS_FEASIBILITY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    exposure_family, exposure_variant, alignment = load_gate_choice()
    exposure_df = load_state_month_exposure(exposure_variant, alignment)

    hps_state_week = load_hps_state_week_cells()
    hps_state_week = hps_state_week.merge(
        exposure_df,
        left_on=["state_fips", "reference_month"],
        right_on=["tehc_st_fips", "MONTHCODE"],
        how="left",
    )
    hps_summary = summarize_hps_crosscheck(hps_state_week, exposure_family, exposure_variant, alignment)
    HPS_STATE_WEEK_CSV.parent.mkdir(parents=True, exist_ok=True)
    hps_state_week.to_csv(HPS_STATE_WEEK_CSV, index=False)
    hps_summary.to_csv(HPS_SUMMARY_CSV, index=False)
    write_hps_markdown(hps_state_week, hps_summary, exposure_family, exposure_variant, alignment)

    nhis_feasibility = build_nhis_feasibility()
    nhis_feasibility.to_csv(NHIS_FEASIBILITY_CSV, index=False)
    write_nhis_markdown(nhis_feasibility)

    print(
        json.dumps(
            {
                "hps_state_week_csv": str(HPS_STATE_WEEK_CSV.relative_to(PROJECT_ROOT)),
                "hps_summary_csv": str(HPS_SUMMARY_CSV.relative_to(PROJECT_ROOT)),
                "hps_md": str(HPS_MD.relative_to(PROJECT_ROOT)),
                "nhis_feasibility_csv": str(NHIS_FEASIBILITY_CSV.relative_to(PROJECT_ROOT)),
                "nhis_feasibility_md": str(NHIS_FEASIBILITY_MD.relative_to(PROJECT_ROOT)),
                "chosen_exposure": {
                    "exposure_family": exposure_family,
                    "exposure_variant": exposure_variant,
                    "alignment": alignment,
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
