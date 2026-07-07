from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
RAW_HPS_DIR = PROJECT_ROOT / "data" / "raw" / "feasibility_audit" / "hps" / "2023"

SUMMARY_JSON = OUTPUT_DIR / "avoidable_churn_burden_summary.json"
STATE_MONTH_CSV = OUTPUT_DIR / "avoidable_churn_state_month_cells.csv"

STATE_WEEK_CSV = OUTPUT_DIR / "hps_avoidable_churn_crosscheck_state_week_cells.csv"
SUMMARY_CSV = OUTPUT_DIR / "hps_avoidable_churn_crosscheck_summary.csv"
MD_PATH = OUTPUT_DIR / "hps_avoidable_churn_crosscheck.md"


@dataclass(frozen=True)
class WeekMap:
    week: int
    start_date: str
    end_date: str
    reference_month: int


WEEK_MAPS = [
    WeekMap(60, "2023-07-26", "2023-08-07", 8),
    WeekMap(61, "2023-08-23", "2023-09-04", 9),
    WeekMap(62, "2023-09-20", "2023-10-02", 10),
    WeekMap(63, "2023-10-18", "2023-10-30", 10),
]


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna() & (weights > 0)
    if not mask.any():
        return float("nan")
    v = pd.to_numeric(values.loc[mask], errors="coerce").astype(float)
    w = pd.to_numeric(weights.loc[mask], errors="coerce").astype(float)
    return float(np.average(v, weights=w))


def weighted_corr(x: pd.Series, y: pd.Series, w: pd.Series) -> float:
    mask = x.notna() & y.notna() & w.notna() & (w > 0)
    if mask.sum() < 3:
        return float("nan")
    xv = pd.to_numeric(x.loc[mask], errors="coerce").astype(float).to_numpy()
    yv = pd.to_numeric(y.loc[mask], errors="coerce").astype(float).to_numpy()
    wv = pd.to_numeric(w.loc[mask], errors="coerce").astype(float).to_numpy()
    mx = np.average(xv, weights=wv)
    my = np.average(yv, weights=wv)
    cov = np.average((xv - mx) * (yv - my), weights=wv)
    vx = np.average((xv - mx) ** 2, weights=wv)
    vy = np.average((yv - my) ** 2, weights=wv)
    if vx <= 0 or vy <= 0:
        return float("nan")
    return float(cov / np.sqrt(vx * vy))


def df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def load_candidate() -> tuple[str, str]:
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    candidate = summary["candidate"]
    return candidate["exposure_variant"], candidate["alignment"]


def load_exposure(variant: str, alignment: str) -> pd.DataFrame:
    exp_col = f"{variant}_{alignment}"
    cols = ["reference_year", "tehc_st_fips", "state_abbreviation", "MONTHCODE", exp_col]
    df = pd.read_csv(STATE_MONTH_CSV, usecols=cols)
    df = df.loc[df["reference_year"].eq(2023)].copy()
    df = df.rename(columns={exp_col: "candidate_exposure"})
    df["tehc_st_fips"] = pd.to_numeric(df["tehc_st_fips"], errors="coerce")
    df["MONTHCODE"] = pd.to_numeric(df["MONTHCODE"], errors="coerce")
    return (
        df.dropna(subset=["tehc_st_fips", "MONTHCODE", "candidate_exposure"])
        .drop_duplicates(subset=["tehc_st_fips", "MONTHCODE"])
        .reset_index(drop=True)
    )


def load_hps_week(meta: WeekMap) -> pd.DataFrame:
    zip_path = RAW_HPS_DIR / f"HPS_Week{meta.week}_PUF_CSV.zip"
    with zipfile.ZipFile(zip_path) as zf:
        csv_name = next(n for n in zf.namelist() if n.lower().endswith(".csv") and "repwgt" not in n.lower())
        with zf.open(csv_name) as handle:
            df = pd.read_csv(
                handle,
                usecols=["EST_ST", "PWEIGHT", "TBIRTH_YEAR", "HLTHINS4", "PUBHLTH", "PRIVHLTH"],
                low_memory=False,
            )

    df["state_fips"] = pd.to_numeric(df["EST_ST"], errors="coerce")
    df["weight"] = pd.to_numeric(df["PWEIGHT"], errors="coerce")
    df["age"] = 2023 - pd.to_numeric(df["TBIRTH_YEAR"], errors="coerce")
    df = df.loc[
        df["state_fips"].notna()
        & df["weight"].notna()
        & (df["weight"] > 0)
        & df["age"].between(18, 64, inclusive="both")
    ].copy()

    df["current_medicaid"] = pd.to_numeric(df["HLTHINS4"], errors="coerce").eq(1).astype(float)
    df["uninsured"] = (
        pd.to_numeric(df["PRIVHLTH"], errors="coerce").eq(2)
        & pd.to_numeric(df["PUBHLTH"], errors="coerce").eq(2)
    ).astype(float)
    df["public_coverage"] = pd.to_numeric(df["PUBHLTH"], errors="coerce").eq(1).astype(float)

    rows: list[dict[str, object]] = []
    for state_fips, g in df.groupby("state_fips", sort=True):
        rows.append(
            {
                "state_fips": state_fips,
                "week": meta.week,
                "start_date": meta.start_date,
                "end_date": meta.end_date,
                "reference_month": meta.reference_month,
                "respondents": int(len(g)),
                "respondent_weight_sum": float(g["weight"].sum()),
                "current_medicaid_rate": weighted_mean(g["current_medicaid"], g["weight"]),
                "uninsured_rate": weighted_mean(g["uninsured"], g["weight"]),
                "public_coverage_rate": weighted_mean(g["public_coverage"], g["weight"]),
            }
        )
    return pd.DataFrame(rows)


def build_state_week_cells(exposure_df: pd.DataFrame) -> pd.DataFrame:
    frames = [load_hps_week(meta) for meta in WEEK_MAPS]
    state_week = pd.concat(frames, ignore_index=True)
    merged = state_week.merge(
        exposure_df,
        left_on=["state_fips", "reference_month"],
        right_on=["tehc_st_fips", "MONTHCODE"],
        how="left",
    )
    return merged


def build_summary(state_week: pd.DataFrame, variant: str, alignment: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    outcome_signs = {
        "current_medicaid_rate": -1,
        "uninsured_rate": 1,
        "public_coverage_rate": -1,
    }
    for outcome, expected_sign in outcome_signs.items():
        valid = state_week.loc[state_week["candidate_exposure"].notna() & state_week[outcome].notna()].copy()
        corr = weighted_corr(valid["candidate_exposure"], valid[outcome], valid["respondent_weight_sum"])
        tertile = pd.qcut(valid["candidate_exposure"].rank(method="first"), q=3, labels=["low", "mid", "high"])
        valid["exposure_tertile"] = tertile.astype("string")
        low = valid.loc[valid["exposure_tertile"].eq("low")]
        high = valid.loc[valid["exposure_tertile"].eq("high")]
        diff = weighted_mean(high[outcome], high["respondent_weight_sum"]) - weighted_mean(
            low[outcome], low["respondent_weight_sum"]
        )
        for metric_name, estimate in {
            "weighted_state_week_correlation": corr,
            "high_minus_low_exposure_tertile": diff,
        }.items():
            rows.append(
                {
                    "dataset": "HPS",
                    "reference_year": 2023,
                    "window": "weeks_60_63_end_month_mapping",
                    "exposure_variant": variant,
                    "alignment": alignment,
                    "outcome": outcome,
                    "support_rows": int(len(valid)),
                    "support_weight": round(float(valid["respondent_weight_sum"].sum()), 2),
                    "estimate_or_contrast": round(estimate, 4) if estimate == estimate else np.nan,
                    "direction_flag": (
                        "expected"
                        if estimate == estimate and np.sign(estimate) == np.sign(expected_sign)
                        else ("zero" if estimate == 0 else ("missing" if estimate != estimate else "unexpected"))
                    ),
                    "notes": metric_name,
                }
            )
    return pd.DataFrame(rows)


def write_markdown(state_week: pd.DataFrame, summary_df: pd.DataFrame, variant: str, alignment: str) -> None:
    lines = [
        "# HPS Avoidable Churn Cross-Check",
        "",
        "## Purpose",
        "",
        "This is a lightweight external cross-check for the candidate chosen in the avoidable-churn burden round.",
        "",
        f"- chosen candidate: `{variant} / {alignment}`",
        "- HPS window: Weeks 60-63 in 2023",
        "- state-week outcomes are mapped to state-month exposure using the survey end-month",
        "- age restriction: adults 18-64",
        "",
        "Week-date mapping source: U.S. Census Bureau 2023 Household Pulse Survey Data Tables page.",
        "https://www.census.gov/data/tables/time-series/demo/hhp/2023.html",
        "",
        "## Support",
        "",
        f"- state-week cells: `{len(state_week)}`",
        f"- nonmissing candidate exposure cells: `{int(state_week['candidate_exposure'].notna().sum())}`",
        f"- total respondent weight kept: `{round(float(state_week['respondent_weight_sum'].sum()), 2)}`",
        "",
        "## Summary",
        "",
        df_to_markdown(summary_df[["outcome", "notes", "estimate_or_contrast", "direction_flag"]]),
        "",
        "## Interpretation",
        "",
        "- For a burden candidate, lower current Medicaid and higher uninsured are the expected rough directions.",
        "- This is still a repeated-cross-section validation, not a person-level churn design.",
        "- The purpose is only to test whether the candidate exposure has a plausible external echo outside SIPP.",
    ]
    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    variant, alignment = load_candidate()
    exposure_df = load_exposure(variant, alignment)
    state_week = build_state_week_cells(exposure_df)
    summary_df = build_summary(state_week, variant, alignment)

    state_week.to_csv(STATE_WEEK_CSV, index=False)
    summary_df.to_csv(SUMMARY_CSV, index=False)
    write_markdown(state_week, summary_df, variant, alignment)

    print(
        json.dumps(
            {
                "candidate_variant": variant,
                "candidate_alignment": alignment,
                "state_week_csv": str(STATE_WEEK_CSV.relative_to(PROJECT_ROOT)),
                "summary_csv": str(SUMMARY_CSV.relative_to(PROJECT_ROOT)),
                "summary_md": str(MD_PATH.relative_to(PROJECT_ROOT)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
