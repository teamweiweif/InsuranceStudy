from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TEMP = ROOT / "temp"
REPORT = ROOT / "report"


OUTCOMES = [
    "weekend_total_nurse_hprd",
    "weekend_rn_hprd",
    "weekday_total_nurse_hprd",
    "weekday_rn_hprd",
    "weekend_minus_weekday_total_hprd",
    "weekday_minus_weekend_total_hprd",
    "total_nurse_hprd",
    "rn_share_total_hours",
    "contract_share_total_hours",
]


def zscore(s: pd.Series) -> pd.Series:
    sd = s.std(skipna=True)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.nan, index=s.index)
    return (s - s.mean(skipna=True)) / sd


def add_time_vars(df: pd.DataFrame, time_col: str = "month") -> pd.DataFrame:
    out = df.copy()
    if time_col == "month":
        period = pd.PeriodIndex(out["month"], freq="M")
        out["period"] = period.astype(str)
        out["period_date"] = period.to_timestamp()
        out["year"] = period.year
        out["month_num"] = period.month
        out["month_index"] = (period.year - 2019) * 12 + period.month
        out["rel_month_jan2022"] = (period.year - 2022) * 12 + (period.month - 1)
        out["rel_month_jul2022"] = (period.year - 2022) * 12 + (period.month - 7)
        out["post_jan2022"] = (out["rel_month_jan2022"] >= 0).astype(int)
        out["jan_to_jun2022"] = ((out["rel_month_jan2022"] >= 0) & (out["rel_month_jul2022"] < 0)).astype(int)
        out["post_jul2022"] = (out["rel_month_jul2022"] >= 0).astype(int)
        out["state_time"] = out["state"].astype(str) + "_" + out["period"].astype(str)
    else:
        period = pd.PeriodIndex(out["quarter"], freq="Q")
        out["period"] = period.astype(str)
        out["period_date"] = period.to_timestamp()
        out["year"] = period.year
        out["quarter_num"] = period.quarter
        out["quarter_index"] = (period.year - 2019) * 4 + period.quarter
        out["rel_quarter_jan2022"] = (period.year - 2022) * 4 + (period.quarter - 1)
        out["rel_quarter_jul2022"] = (period.year - 2022) * 4 + (period.quarter - 3)
        out["post_jan2022"] = (out["rel_quarter_jan2022"] >= 0).astype(int)
        out["jan_to_jun2022"] = ((out["rel_quarter_jan2022"] >= 0) & (out["rel_quarter_jul2022"] < 0)).astype(int)
        out["post_jul2022"] = (out["rel_quarter_jul2022"] >= 0).astype(int)
        out["state_time"] = out["state"].astype(str) + "_" + out["period"].astype(str)
    return out


def provider_baseline() -> pd.DataFrame:
    path = DATA / "baseline_provider_characteristics_pre2022.parquet"
    if not path.exists():
        return pd.DataFrame({"facility_id": []})
    p = pd.read_parquet(path)
    keep = [
        "facility_id",
        "ownership_type",
        "certified_beds",
        "avg_residents_per_day",
        "provider_type",
        "in_hospital",
        "special_focus_status",
        "overall_rating",
        "health_inspection_rating",
        "qm_rating",
        "staffing_rating",
        "rn_staffing_rating",
        "rating_cycle_1_total_health_deficiencies",
        "total_weighted_health_survey_score",
        "facility_reported_incidents",
        "substantiated_complaints",
    ]
    p = p[[c for c in keep if c in p.columns]].copy()
    own = p.get("ownership_type", pd.Series("", index=p.index)).astype(str).str.lower()
    p["ownership_for_profit"] = own.str.contains("for profit", na=False).astype(int)
    p["ownership_nonprofit"] = own.str.contains("non profit|non-profit", regex=True, na=False).astype(int)
    p["ownership_government"] = own.str.contains("government", na=False).astype(int)
    p["large_facility"] = (p["certified_beds"] >= p["certified_beds"].median(skipna=True)).astype(float)
    return p


def build_exposures(monthly: pd.DataFrame) -> pd.DataFrame:
    monthly = add_time_vars(monthly, "month")
    pre = monthly[(monthly["period_date"] >= "2019-01-01") & (monthly["period_date"] < "2022-01-01")].copy()
    base = (
        pre.groupby("facility_id")
        .agg(
            baseline_months=("month", "nunique"),
            baseline_weekend_total_hprd=("weekend_total_nurse_hprd", "mean"),
            baseline_weekend_rn_hprd=("weekend_rn_hprd", "mean"),
            baseline_weekday_total_hprd=("weekday_total_nurse_hprd", "mean"),
            baseline_weekday_rn_hprd=("weekday_rn_hprd", "mean"),
            baseline_gap_total=("weekday_minus_weekend_total_hprd", "mean"),
            baseline_gap_rn=("weekday_minus_weekend_rn_hprd", "mean"),
            baseline_total_hprd=("total_nurse_hprd", "mean"),
            baseline_rn_share=("rn_share_total_hours", "mean"),
            baseline_contract_share=("contract_share_total_hours", "mean"),
            baseline_resident_days=("resident_days", "sum"),
        )
        .reset_index()
    )
    base["low_baseline_weekend_total_hprd"] = (
        base["baseline_weekend_total_hprd"] <= base["baseline_weekend_total_hprd"].quantile(0.25)
    ).astype(int)
    base["low_baseline_weekend_rn_hprd"] = (
        base["baseline_weekend_rn_hprd"] <= base["baseline_weekend_rn_hprd"].quantile(0.25)
    ).astype(int)
    base["high_baseline_weekday_weekend_gap"] = (
        base["baseline_gap_total"] >= base["baseline_gap_total"].quantile(0.75)
    ).astype(int)
    base["low_baseline_total_hprd"] = (
        base["baseline_total_hprd"] <= base["baseline_total_hprd"].quantile(0.25)
    ).astype(int)
    base["exposure_low_weekend_total_z"] = -zscore(base["baseline_weekend_total_hprd"])
    base["exposure_low_weekend_rn_z"] = -zscore(base["baseline_weekend_rn_hprd"])
    base["exposure_gap_z"] = zscore(base["baseline_gap_total"])
    base["exposure_composite"] = base[
        ["exposure_low_weekend_total_z", "exposure_low_weekend_rn_z", "exposure_gap_z"]
    ].mean(axis=1)
    base["high_exposure_composite"] = (
        base["exposure_composite"] >= base["exposure_composite"].quantile(0.75)
    ).astype(int)

    pre2021 = pre[pre["year"] == 2021]
    base2021 = (
        pre2021.groupby("facility_id")
        .agg(
            baseline2021_months=("month", "nunique"),
            baseline2021_weekend_total_hprd=("weekend_total_nurse_hprd", "mean"),
            baseline2021_weekend_rn_hprd=("weekend_rn_hprd", "mean"),
            baseline2021_gap_total=("weekday_minus_weekend_total_hprd", "mean"),
        )
        .reset_index()
    )
    base2021["exposure2021_composite"] = (
        -zscore(base2021["baseline2021_weekend_total_hprd"])
        - zscore(base2021["baseline2021_weekend_rn_hprd"])
        + zscore(base2021["baseline2021_gap_total"])
    ) / 3.0
    base2021["high_exposure2021_composite"] = (
        base2021["exposure2021_composite"] >= base2021["exposure2021_composite"].quantile(0.75)
    ).astype(int)

    pre_no2020 = pre[pre["year"].isin([2019, 2021])]
    base_no2020 = (
        pre_no2020.groupby("facility_id")
        .agg(
            baseline_no2020_months=("month", "nunique"),
            baseline_no2020_weekend_total_hprd=("weekend_total_nurse_hprd", "mean"),
            baseline_no2020_weekend_rn_hprd=("weekend_rn_hprd", "mean"),
            baseline_no2020_gap_total=("weekday_minus_weekend_total_hprd", "mean"),
        )
        .reset_index()
    )
    base_no2020["exposure_no2020_composite"] = (
        -zscore(base_no2020["baseline_no2020_weekend_total_hprd"])
        - zscore(base_no2020["baseline_no2020_weekend_rn_hprd"])
        + zscore(base_no2020["baseline_no2020_gap_total"])
    ) / 3.0
    base_no2020["high_exposure_no2020_composite"] = (
        base_no2020["exposure_no2020_composite"] >= base_no2020["exposure_no2020_composite"].quantile(0.75)
    ).astype(int)

    base = base.merge(base2021, on="facility_id", how="left").merge(base_no2020, on="facility_id", how="left")
    base = base.merge(provider_baseline(), on="facility_id", how="left")
    return base


def attach_exposures(df: pd.DataFrame, exposures: pd.DataFrame, time_col: str) -> pd.DataFrame:
    out = add_time_vars(df, time_col)
    out = out.merge(exposures, on="facility_id", how="left")
    out["analysis_sample"] = (
        out["baseline_months"].ge(18)
        & out["high_exposure_composite"].notna()
        & out["weekend_total_nurse_hprd"].notna()
        & out["resident_days"].gt(0)
    ).astype(int)
    for col in [
        "high_exposure_composite",
        "low_baseline_weekend_total_hprd",
        "low_baseline_weekend_rn_hprd",
        "high_baseline_weekday_weekend_gap",
        "low_baseline_total_hprd",
        "high_exposure2021_composite",
        "high_exposure_no2020_composite",
    ]:
        if col in out.columns:
            out[col] = out[col].fillna(0).astype(int)
    return out


def write_data_dictionary() -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    text = """# Data Dictionary

Created by `script/03_construct_exposures_outcomes.py`.

## Identifiers

- `facility_id`: six-character CMS Certification Number / Federal Provider Number.
- `state`: provider state from PBJ daily staffing files.
- `month`, `quarter`: facility-time periods constructed from PBJ `WorkDate`.

## Staffing Outcomes

- `weekend_total_nurse_hprd`: weekend total nurse hours per resident day, calculated as weekend RN + LPN + nurse aide hours divided by weekend resident-days.
- `weekend_rn_hprd`: weekend RN hours per resident day, calculated from RN, RN admin, and RN director-of-nursing hours divided by weekend resident-days.
- `weekday_total_nurse_hprd`: weekday total nurse hours per resident day.
- `weekday_rn_hprd`: weekday RN hours per resident day.
- `weekend_minus_weekday_total_hprd`: weekend total nurse HPRD minus weekday total nurse HPRD.
- `weekday_minus_weekend_total_hprd`: weekday total nurse HPRD minus weekend total nurse HPRD. Larger values mean a larger weekday-weekend gap.
- `total_nurse_hprd`: total nurse hours per resident day across all days.
- `rn_share_total_hours`: RN hours divided by total nurse hours.
- `contract_share_total_hours`: contract nurse hours divided by total nurse hours, using PBJ employee/contract hour splits.

## Baseline Exposures

All main exposure variables use only pre-treatment PBJ data from January 2019 through December 2021.

- `baseline_weekend_total_hprd`: facility mean weekend total nurse HPRD in 2019-2021.
- `baseline_weekend_rn_hprd`: facility mean weekend RN HPRD in 2019-2021.
- `baseline_gap_total`: facility mean weekday-minus-weekend total nurse HPRD in 2019-2021.
- `low_baseline_weekend_total_hprd`: indicator for bottom quartile of baseline weekend total nurse HPRD.
- `low_baseline_weekend_rn_hprd`: indicator for bottom quartile of baseline weekend RN HPRD.
- `high_baseline_weekday_weekend_gap`: indicator for top quartile of baseline weekday-minus-weekend total nurse staffing gap.
- `exposure_composite`: average of standardized low weekend total staffing, low weekend RN staffing, and high weekday-weekend gap. Higher values mean greater pre-policy exposure to the weekend-staffing reporting shock.
- `high_exposure_composite`: top quartile of `exposure_composite`; the preferred binary exposure.
- `high_exposure2021_composite`: robustness exposure using 2021 only.
- `high_exposure_no2020_composite`: robustness exposure using 2019 and 2021, excluding 2020.

## Policy Timing

- `post_jan2022`: one from January 2022 onward.
- `jan_to_jun2022`: one from January through June 2022.
- `post_jul2022`: one from July 2022 onward.
- `rel_month_jan2022`: event time in months, where January 2022 equals 0.
- `rel_month_jul2022`: event time in months, where July 2022 equals 0.

## Provider Data Catalog Variables

Provider snapshot variables include ownership type, certified beds, average residents, star ratings, reported CMS staffing and turnover fields, penalties, and survey/deficiency measures extracted from archived nursing-home Provider Data Catalog ZIPs.
"""
    (REPORT / "data_dictionary.md").write_text(text, encoding="utf-8")


def main() -> None:
    monthly = pd.read_parquet(DATA / "pbj_facility_month.parquet")
    quarterly = pd.read_parquet(DATA / "pbj_facility_quarter.parquet")
    exposures = build_exposures(monthly)
    exposures.to_parquet(DATA / "facility_exposures.parquet", index=False)
    exposures.to_csv(DATA / "facility_exposures.csv", index=False)

    analysis_month = attach_exposures(monthly, exposures, "month")
    analysis_month.to_parquet(DATA / "analysis_facility_month.parquet", index=False)

    analysis_quarter = attach_exposures(quarterly, exposures, "quarter")
    analysis_quarter.to_parquet(DATA / "analysis_facility_quarter.parquet", index=False)

    write_data_dictionary()

    with (TEMP / "audit_log.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 3 Panel and Exposure Construction\n\n"
            f"- Constructed baseline exposures for {len(exposures):,} facilities with any 2019-2021 PBJ data.\n"
            f"- Preferred analysis month sample has {analysis_month['analysis_sample'].sum():,} facility-month observations.\n"
            "- Main high-exposure indicator is the top quartile of a pre-2022 composite of low weekend total staffing, low weekend RN staffing, and high weekday-weekend staffing gap.\n"
        )
    with (TEMP / "iteration_notes.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 3: Analysis-Ready Panel Construction\n\n"
            "Facility-month and facility-quarter panels were built from PBJ daily staffing. Exposures use only 2019-2021 PBJ staffing and are merged back to post-2022 outcomes. Provider archive characteristics are attached for baseline balance and heterogeneity when available.\n\n"
            "Self-question: Identifiers are stable enough for a facility-level panel after normalizing CMS Certification Numbers to six characters. Facility exits remain in the unbalanced panel; robustness checks must test whether results change in a balanced or active-facility sample.\n"
        )
        f.write(
            "\n## Phase 4: Outcome Construction\n\n"
            "Primary outcomes are policy-proximal staffing measures from PBJ daily records: weekend total nurse HPRD, weekend RN HPRD, weekday counterparts, weekend-weekday gaps, total HPRD, RN share, and contract share. Provider Data Catalog ratings and deficiencies are retained as secondary downstream outcomes.\n\n"
            "Self-question: Outcomes are valid for staffing behavior and ratings. Facility-level deficiencies are downstream quality signals, not resident-level health outcomes.\n"
        )

    print("Exposure and outcome construction complete.")


if __name__ == "__main__":
    main()
