from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MERGED_2024 = PROJECT_ROOT / "outputs" / "prototype" / "sipp_2024_cms_updated_renewal_outcomes_merged.parquet"
CORR_2023 = PROJECT_ROOT / "outputs" / "prototype" / "sipp_2023_corrected_person_month_flags.parquet"
CORR_2022 = PROJECT_ROOT / "outputs" / "prototype" / "sipp_2022_corrected_person_month_flags.parquet"

SUPPORT_MD = OUTPUT_DIR / "churn_unwinding_support_audit.md"
TIMING_MD = OUTPUT_DIR / "churn_unwinding_timing_sensitivity.md"
MECHANISM_MD = OUTPUT_DIR / "churn_unwinding_mechanism_screen.md"
SUMMARY_JSON = OUTPUT_DIR / "churn_unwinding_first_diagnostics_summary.json"
YEAR_SUMMARY_CSV = OUTPUT_DIR / "yearly_churn_support_summary.csv"
CELL_CSV = OUTPUT_DIR / "unwinding_state_month_transition_cells.csv"
SUPPORT_WINDOW_CSV = OUTPUT_DIR / "unwinding_window_support_summary.csv"
TIMING_CSV = OUTPUT_DIR / "unwinding_timing_sensitivity_summary.csv"
MECHANISM_CSV = OUTPUT_DIR / "unwinding_mechanism_screen_summary.csv"


EXPOSURE_MAP = {
    "procedural_friction": "cms_updated_procedural_share_of_terminated",
    "renewal_intensity": "cms_updated_renewal_due_n",
    "pending_pressure": "cms_updated_pending_rate",
}

WINDOWS = {
    "core_aug_nov_2023": [8, 9, 10, 11],
    "extended_mar_nov_2023": [3, 4, 5, 6, 7, 8, 9, 10, 11],
}


def weighted_rate(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna()
    if mask.sum() == 0:
        return float("nan")
    v = pd.to_numeric(values[mask], errors="coerce").astype(float)
    w = pd.to_numeric(weights[mask], errors="coerce").astype(float)
    denom = w.sum()
    if denom == 0:
        return float("nan")
    return float((v * w).sum() / denom)


def weighted_corr(x: pd.Series, y: pd.Series, w: pd.Series) -> float:
    mask = x.notna() & y.notna() & w.notna()
    if mask.sum() < 3:
        return float("nan")
    x_ = pd.to_numeric(x[mask], errors="coerce").astype(float).to_numpy()
    y_ = pd.to_numeric(y[mask], errors="coerce").astype(float).to_numpy()
    w_ = pd.to_numeric(w[mask], errors="coerce").astype(float).to_numpy()
    if np.allclose(w_.sum(), 0):
        return float("nan")
    mx = np.average(x_, weights=w_)
    my = np.average(y_, weights=w_)
    cov = np.average((x_ - mx) * (y_ - my), weights=w_)
    vx = np.average((x_ - mx) ** 2, weights=w_)
    vy = np.average((y_ - my) ** 2, weights=w_)
    if vx <= 0 or vy <= 0:
        return float("nan")
    return float(cov / np.sqrt(vx * vy))


def format_value(value: float | int | str | None, digits: int = 3) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "NA"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_parquet(MERGED_2024),
        pd.read_parquet(CORR_2023),
        pd.read_parquet(CORR_2022),
    )


def build_yearly_support_summary(df_2024: pd.DataFrame, df_2023: pd.DataFrame, df_2022: pd.DataFrame) -> pd.DataFrame:
    frames = [
        ("2021", df_2022, "2022 release corrected pilot"),
        ("2022", df_2023, "2023 release corrected pilot"),
        ("2023", df_2024, "2024 release merged prototype"),
    ]
    rows = []
    for reference_year, df, source_label in frames:
        eligible = df["eligible_medicaid_transition"] == True
        rows.append(
            {
                "reference_year": reference_year,
                "source": source_label,
                "rows": int(len(df)),
                "persons": int(df[["SSUID", "PNUM"]].drop_duplicates().shape[0]),
                "eligible_medicaid_transition_rows": int(eligible.sum()),
                "weighted_eligible_transition_sum": round(float(df.loc[eligible, "WPFINWGT"].sum()), 2),
                "weighted_medicaid_exit_rate": round(weighted_rate(df.loc[eligible, "medicaid_exit_next"], df.loc[eligible, "WPFINWGT"]), 4),
                "weighted_exit_to_uninsured_rate": round(weighted_rate(df.loc[eligible, "medicaid_exit_to_uninsured_next"], df.loc[eligible, "WPFINWGT"]), 4),
            }
        )
    return pd.DataFrame(rows)


def build_state_month_cells(df_2024: pd.DataFrame) -> pd.DataFrame:
    eligible = df_2024.loc[df_2024["eligible_medicaid_transition"] == True].copy()
    group_cols = ["state_abbreviation", "MONTHCODE", "cms_reporting_period", "reporting_label"]

    def first_non_null(series: pd.Series):
        series = series.dropna()
        return series.iloc[0] if len(series) else np.nan

    cell = (
        eligible.groupby(group_cols, dropna=False)
        .apply(
            lambda g: pd.Series(
                {
                    "eligible_rows": int(len(g)),
                    "eligible_weight_sum": float(g["WPFINWGT"].sum()),
                    "medicaid_exit_rate_w": weighted_rate(g["medicaid_exit_next"], g["WPFINWGT"]),
                    "exit_to_uninsured_rate_w": weighted_rate(g["medicaid_exit_to_uninsured_next"], g["WPFINWGT"]),
                    EXPOSURE_MAP["procedural_friction"]: first_non_null(g[EXPOSURE_MAP["procedural_friction"]]),
                    EXPOSURE_MAP["renewal_intensity"]: first_non_null(g[EXPOSURE_MAP["renewal_intensity"]]),
                    EXPOSURE_MAP["pending_pressure"]: first_non_null(g[EXPOSURE_MAP["pending_pressure"]]),
                }
            )
        )
        .reset_index()
    )

    cell = cell.sort_values(["state_abbreviation", "MONTHCODE"], kind="stable").reset_index(drop=True)
    for family, col in EXPOSURE_MAP.items():
        cell[f"{family}_same"] = cell[col]
        cell[f"{family}_lag1"] = cell.groupby("state_abbreviation", sort=False)[col].shift(1)
        cell[f"{family}_lead1"] = cell.groupby("state_abbreviation", sort=False)[col].shift(-1)

    return cell


def build_support_window_summary(cell: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for window_name, months in WINDOWS.items():
        subset = cell.loc[cell["MONTHCODE"].isin(months)].copy()
        for family, col in EXPOSURE_MAP.items():
            mask = subset[col].notna()
            exposed = subset.loc[mask]
            rows.append(
                {
                    "window": window_name,
                    "exposure_family": family,
                    "state_month_cells_total": int(len(subset)),
                    "state_month_cells_nonmissing": int(mask.sum()),
                    "unique_states_nonmissing": int(exposed["state_abbreviation"].nunique()),
                    "eligible_rows_sum": int(subset["eligible_rows"].sum()),
                    "eligible_weight_sum": round(float(subset["eligible_weight_sum"].sum()), 2),
                    "exposure_min": round(float(exposed[col].min()), 4) if len(exposed) else np.nan,
                    "exposure_median": round(float(exposed[col].median()), 4) if len(exposed) else np.nan,
                    "exposure_p90": round(float(exposed[col].quantile(0.9)), 4) if len(exposed) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def build_timing_sensitivity(cell: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for window_name, months in WINDOWS.items():
        subset = cell.loc[cell["MONTHCODE"].isin(months)].copy()
        for family in EXPOSURE_MAP:
            for alignment in ["same", "lag1", "lead1"]:
                x = subset[f"{family}_{alignment}"]
                w = subset["eligible_weight_sum"]
                rows.append(
                    {
                        "window": window_name,
                        "exposure_family": family,
                        "alignment": alignment,
                        "state_month_cells_used": int((x.notna() & w.notna()).sum()),
                        "weighted_corr_exit_rate": round(weighted_corr(x, subset["medicaid_exit_rate_w"], w), 4),
                        "weighted_corr_exit_to_uninsured_rate": round(weighted_corr(x, subset["exit_to_uninsured_rate_w"], w), 4),
                    }
                )
    return pd.DataFrame(rows)


def assign_tertiles(series: pd.Series) -> pd.Series:
    valid = series.dropna().rank(method="first", pct=True)
    tertile = pd.Series(pd.NA, index=series.index, dtype="object")
    tertile.loc[valid.index] = pd.cut(
        valid,
        bins=[0, 1 / 3, 2 / 3, 1],
        labels=["low", "mid", "high"],
        include_lowest=True,
    ).astype("string")
    return tertile


def build_mechanism_screen(cell: pd.DataFrame) -> pd.DataFrame:
    core = cell.loc[cell["MONTHCODE"].isin(WINDOWS["core_aug_nov_2023"])].copy()
    rows = []
    for family, col in EXPOSURE_MAP.items():
        subset = core.loc[core[col].notna()].copy()
        if subset.empty:
            continue
        subset["tertile"] = assign_tertiles(subset[col])
        tertile_stats = (
            subset.groupby("tertile", dropna=False)
            .apply(
                lambda g: pd.Series(
                    {
                        "cells": int(len(g)),
                        "eligible_weight_sum": float(g["eligible_weight_sum"].sum()),
                        "exit_rate_w": weighted_rate(g["medicaid_exit_rate_w"], g["eligible_weight_sum"]),
                        "exit_to_uninsured_rate_w": weighted_rate(g["exit_to_uninsured_rate_w"], g["eligible_weight_sum"]),
                    }
                )
            )
            .reset_index()
        )
        for _, row in tertile_stats.iterrows():
            rows.append(
                {
                    "exposure_family": family,
                    "tertile": row["tertile"],
                    "cells": int(row["cells"]),
                    "eligible_weight_sum": round(float(row["eligible_weight_sum"]), 2),
                    "weighted_exit_rate": round(float(row["exit_rate_w"]), 4),
                    "weighted_exit_to_uninsured_rate": round(float(row["exit_to_uninsured_rate_w"]), 4),
                }
            )
        if set(tertile_stats["tertile"]) >= {"low", "high"}:
            low = tertile_stats.loc[tertile_stats["tertile"] == "low"].iloc[0]
            high = tertile_stats.loc[tertile_stats["tertile"] == "high"].iloc[0]
            rows.append(
                {
                    "exposure_family": family,
                    "tertile": "high_minus_low",
                    "cells": int(high["cells"] + low["cells"]),
                    "eligible_weight_sum": round(float(high["eligible_weight_sum"] + low["eligible_weight_sum"]), 2),
                    "weighted_exit_rate": round(float(high["exit_rate_w"] - low["exit_rate_w"]), 4),
                    "weighted_exit_to_uninsured_rate": round(float(high["exit_to_uninsured_rate_w"] - low["exit_to_uninsured_rate_w"]), 4),
                }
            )
    return pd.DataFrame(rows)


def write_support_md(year_df: pd.DataFrame, window_df: pd.DataFrame) -> None:
    text = f"""# Churn / Unwinding Support Audit

Last updated: `2026-04-10`

## Purpose

This note records the first support and overlap audit for the unwinding-era diagnostics phase.

It combines:

- corrected pre-period support from the `2022` and `2023` releases
- the unwinding-era merged `2024` release
- state-month support checks for the first candidate exposure families

This is a diagnostics artifact, not an estimating result.

## Year-Level Support Summary

{df_to_markdown(year_df)}

Interpretation:

- `2022` and `2023` corrected releases now provide usable pre-period support years for baseline churn diagnostics.
- `2024` remains the unwinding-era main layer because it is the release already merged to CMS state-month data.
- The three-year stack is not being treated as one final estimating panel. It is being used as a diagnostics stack with distinct roles by reference year.

## State-Month Window Support

{df_to_markdown(window_df)}

Interpretation:

- Transition-based diagnostics require `eligible_medicaid_transition`, so the cleanest "core" window is `August-November 2023`, not `August-December 2023`.
- `December 2023` still matters for exposure coverage and reference-year interpretation, but not for next-month transition outcomes inside this file.
- The core window is therefore the first reliable transition-based diagnostics window.

## Bottom Line

- The diagnostics stack now has enough support to begin unwinding-era mechanism testing.
- The project no longer needs another automatic backfill step before opening the first diagnostics.
- The next design question is not whether support exists, but which exposure family and timing alignment behave most credibly.
"""
    SUPPORT_MD.write_text(text, encoding="utf-8")


def write_timing_md(timing_df: pd.DataFrame) -> None:
    text = f"""# Churn / Unwinding Timing Sensitivity

Last updated: `2026-04-10`

## Purpose

This note records the first timing-sensitivity check for the unwinding-era diagnostics phase.

It tests whether the relationship between the candidate CMS exposure families and the corrected churn outcomes looks more coherent under:

- same-month exposure
- one-month lag
- one-month lead

These are weighted state-month cell correlations.

They are diagnostics only.

## Timing Sensitivity Summary

{df_to_markdown(timing_df)}

## Reading Guide

- A stronger same-month signal would support a tighter contemporaneous state-month interpretation.
- A stronger lag or lead signal would mean the CMS reporting month may be shifted relative to observed person-month churn.
- These diagnostics do **not** identify causality. They only help decide which alignment is most credible for later design work.

## Bottom Line

- This table should be used to choose the first design window and alignment rule, not to make a treatment-effect claim.
- If the strongest signals are unstable across alignments, the project should remain in diagnostics mode rather than opening full `DiD / DML / causal ML`.
"""
    TIMING_MD.write_text(text, encoding="utf-8")


def write_mechanism_md(mech_df: pd.DataFrame) -> None:
    text = f"""# Churn / Unwinding Mechanism Screen

Last updated: `2026-04-10`

## Purpose

This note records the first mechanism screen for the unwinding-era diagnostics phase.

It compares the first three candidate exposure families in the `core_aug_nov_2023` transition window:

- `procedural friction`
- `renewal intensity`
- `pending pressure`

For each exposure family, state-month cells are split into low / mid / high terciles.

The reported outcome rates are weighted by the state-month eligible Medicaid-transition support.

## Mechanism Screen Summary

{df_to_markdown(mech_df)}

## Reading Guide

- A stronger `high_minus_low` contrast for `exit_to_uninsured` than for broad `medicaid_exit_next` is more consistent with an administrative-loss mechanism.
- A strong pattern for `procedural friction` is the most directly useful signal for the project's intended unwinding contribution.
- A signal that appears only for broader `renewal intensity` but not procedural friction would point to a weaker, more diffuse pressure story.

## Bottom Line

- This screen should be used to decide which mechanism family deserves the next serious empirical pass.
- It should not yet be treated as a final paper result.
"""
    MECHANISM_MD.write_text(text, encoding="utf-8")


def main() -> None:
    df_2024, df_2023, df_2022 = load_data()

    yearly_support = build_yearly_support_summary(df_2024, df_2023, df_2022)
    cell = build_state_month_cells(df_2024)
    support_window = build_support_window_summary(cell)
    timing = build_timing_sensitivity(cell)
    mechanism = build_mechanism_screen(cell)

    yearly_support.to_csv(YEAR_SUMMARY_CSV, index=False)
    cell.to_csv(CELL_CSV, index=False)
    support_window.to_csv(SUPPORT_WINDOW_CSV, index=False)
    timing.to_csv(TIMING_CSV, index=False)
    mechanism.to_csv(MECHANISM_CSV, index=False)

    write_support_md(yearly_support, support_window)
    write_timing_md(timing)
    write_mechanism_md(mechanism)

    summary = {
        "yearly_support_csv": str(YEAR_SUMMARY_CSV.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "state_month_cells_csv": str(CELL_CSV.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "support_window_csv": str(SUPPORT_WINDOW_CSV.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "timing_csv": str(TIMING_CSV.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "mechanism_csv": str(MECHANISM_CSV.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "support_md": str(SUPPORT_MD.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "timing_md": str(TIMING_MD.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "mechanism_md": str(MECHANISM_MD.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "core_window_months": WINDOWS["core_aug_nov_2023"],
        "extended_window_months": WINDOWS["extended_mar_nov_2023"],
        "exposure_map": EXPOSURE_MAP,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
