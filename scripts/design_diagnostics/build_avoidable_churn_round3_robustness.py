from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTCOME_LAYER = OUTPUT_DIR / "sipp_avoidable_churn_outcome_layer_2021_2023.parquet"

STATE_MONTH_CELL_CSV = OUTPUT_DIR / "avoidable_churn_round3_state_month_cells.csv"
OUTCOME_AUDIT_CSV = OUTPUT_DIR / "avoidable_churn_outcome_robustness_audit.csv"
OUTCOME_TIMING_CSV = OUTPUT_DIR / "avoidable_churn_outcome_robustness_timing.csv"
OUTCOME_FALSIFICATION_CSV = OUTPUT_DIR / "avoidable_churn_outcome_robustness_falsification.csv"
EXPOSURE_TIMING_CSV = OUTPUT_DIR / "avoidable_churn_exposure_decomposition_timing.csv"
EXPOSURE_RANKING_CSV = OUTPUT_DIR / "avoidable_churn_exposure_decomposition_ranking.csv"
EXPOSURE_FALSIFICATION_CSV = OUTPUT_DIR / "avoidable_churn_exposure_decomposition_falsification.csv"
SUMMARY_JSON = OUTPUT_DIR / "avoidable_churn_round3_robustness_summary.json"
DIAGNOSTICS_MD = OUTPUT_DIR / "avoidable_churn_round3_robustness.md"

WINDOWS = {
    "core_aug_oct_2023": [8, 9, 10],
    "mature_jun_oct_2023": [6, 7, 8, 9, 10],
}

ALIGNMENTS = {
    "same": 0,
    "lag1": 1,
    "lead1": -1,
    "lag2": 2,
}

OUTCOME_SPECS = {
    "medicaid_exit_to_uninsured_next": {
        "label": "pure Medicaid at t, uninsured at t+1",
        "eligible_flag": "eligible_medicaid_transition",
        "outcome_direction": 1,
        "kind": "harm",
    },
    "persistent_uninsured_h2": {
        "label": "pure Medicaid at t, uninsured at t+1 and t+2",
        "eligible_flag": "eligible_medicaid_transition_h2",
        "outcome_direction": 1,
        "kind": "harm",
    },
    "broad_exit_persistent_uninsured_h2": {
        "label": "broad Medicaid exit at t+1, uninsured at t+2",
        "eligible_flag": "eligible_medicaid_transition_h2",
        "outcome_direction": 1,
        "kind": "harm",
    },
    "persistent_uninsured_h3": {
        "label": "pure Medicaid at t, uninsured through t+3",
        "eligible_flag": "eligible_medicaid_transition_h3",
        "outcome_direction": 1,
        "kind": "harm",
    },
    "broad_exit_resolved_insured_h2": {
        "label": "broad Medicaid exit at t+1, insured by t+2",
        "eligible_flag": "eligible_medicaid_transition_h2",
        "outcome_direction": -1,
        "kind": "contrast",
    },
}

DECOMP_EXPOSURES = {
    "pending_rate": {
        "family": "pending_backlog_component",
        "column": "cms_updated_pending_rate",
        "base_sign": 1,
        "kind": "component",
        "notes": "Higher pending rate means heavier backlog strain.",
    },
    "ex_parte_renewal_rate": {
        "family": "ex_parte_component",
        "column": "cms_updated_renewed_ex_parte_rate",
        "base_sign": -1,
        "kind": "component",
        "notes": "Higher ex parte renewal should relieve administrative burden.",
    },
    "backlog_automation_index": {
        "family": "backlog_automation_composite",
        "column": "backlog_automation_index",
        "base_sign": 1,
        "kind": "composite_z",
        "notes": "Equal-weight within-month z-score composite of pending burden and low ex parte renewal.",
    },
    "backlog_automation_rank_index": {
        "family": "backlog_automation_composite",
        "column": "backlog_automation_rank_index",
        "base_sign": 1,
        "kind": "composite_rank",
        "notes": "Equal-weight within-month rank-based composite of pending burden and low ex parte renewal.",
    },
    "backlog_form_index": {
        "family": "manual_burden_comparison",
        "column": "backlog_form_index",
        "base_sign": 1,
        "kind": "secondary_composite",
        "notes": "Comparison composite of pending burden and manual renewal burden.",
    },
}

OUTCOME_ROBUSTNESS_EXPOSURE = "backlog_automation_index"
MIN_MONTHLY_STATE_SUPPORT = 20
MIN_TOTAL_SUPPORT = 100


def weighted_rate(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna() & (weights > 0)
    if not mask.any():
        return float("nan")
    v = pd.to_numeric(values.loc[mask], errors="coerce").astype(float)
    w = pd.to_numeric(weights.loc[mask], errors="coerce").astype(float)
    denom = w.sum()
    if denom <= 0:
        return float("nan")
    return float((v * w).sum() / denom)


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


def mean_of_available(frame: pd.DataFrame) -> pd.Series:
    valid = frame.notna().sum(axis=1)
    total = frame.fillna(0).sum(axis=1)
    out = total / valid
    out.loc[valid == 0] = np.nan
    return out


def df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def average_monthly_estimates(month_estimates: list[tuple[float, float]]) -> float:
    cleaned = [(est, wt) for est, wt in month_estimates if est == est and wt > 0]
    if not cleaned:
        return float("nan")
    return float(np.average([x for x, _ in cleaned], weights=[w for _, w in cleaned]))


def load_layer() -> pd.DataFrame:
    cols = [
        "reference_year",
        "MONTHCODE",
        "tehc_st_fips",
        "state_abbreviation",
        "cms_reporting_period",
        "reporting_label",
        "WPFINWGT",
        "eligible_medicaid_transition",
        "eligible_medicaid_transition_h2",
        "eligible_medicaid_transition_h3",
        "medicaid_exit_next",
        "medicaid_exit_to_uninsured_next",
        "uninsured_t_plus_1",
        "uninsured_t_plus_2",
        "uninsured_t_plus_3",
        "insured_t_plus_2",
        "persistent_uninsured_h2",
        "broad_exit_persistent_uninsured_h2",
        "broad_exit_resolved_insured_h2",
        "cms_updated_pending_rate",
        "cms_updated_renewed_form_rate",
        "cms_updated_procedural_share_of_terminated",
        "cms_updated_renewed_ex_parte_rate",
    ]
    df = pd.read_parquet(OUTCOME_LAYER, columns=cols).copy()
    df["reference_year"] = pd.to_numeric(df["reference_year"], errors="coerce").astype("Int64")
    df["MONTHCODE"] = pd.to_numeric(df["MONTHCODE"], errors="coerce").astype("Int64")
    return df


def derive_additional_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["persistent_uninsured_h3"] = (
        df["eligible_medicaid_transition_h3"].eq(True)
        & df["uninsured_t_plus_1"].eq(True)
        & df["uninsured_t_plus_2"].eq(True)
        & df["uninsured_t_plus_3"].eq(True)
    )
    return df


def build_state_month_cells(df: pd.DataFrame) -> pd.DataFrame:
    group_cols = [
        "reference_year",
        "tehc_st_fips",
        "state_abbreviation",
        "MONTHCODE",
        "cms_reporting_period",
        "reporting_label",
    ]

    rows: list[dict[str, object]] = []
    for keys, g in df.groupby(group_cols, dropna=False, sort=True):
        row = dict(zip(group_cols, keys))
        row["dataset"] = "SIPP"
        row["row_count"] = int(len(g))
        row["total_weight"] = float(g["WPFINWGT"].sum())

        for col in [
            "cms_updated_pending_rate",
            "cms_updated_renewed_form_rate",
            "cms_updated_procedural_share_of_terminated",
            "cms_updated_renewed_ex_parte_rate",
        ]:
            vals = g[col].dropna()
            row[col] = vals.iloc[0] if len(vals) else np.nan

        for outcome, spec in OUTCOME_SPECS.items():
            flag = spec["eligible_flag"]
            denom = g[flag].eq(True)
            row[f"{outcome}__support_rows"] = int(denom.sum())
            row[f"{outcome}__support_weight"] = float(g.loc[denom, "WPFINWGT"].sum())
            row[f"{outcome}__rate"] = weighted_rate(g.loc[denom, outcome], g.loc[denom, "WPFINWGT"])

        rows.append(row)

    cell = pd.DataFrame(rows).sort_values(
        ["reference_year", "state_abbreviation", "MONTHCODE"], kind="stable"
    ).reset_index(drop=True)

    crosswalk = (
        cell.loc[cell["state_abbreviation"].notna() & cell["tehc_st_fips"].notna(), ["tehc_st_fips", "state_abbreviation"]]
        .drop_duplicates()
        .groupby("tehc_st_fips", as_index=False)
        .agg(state_abbreviation_filled=("state_abbreviation", "first"))
    )
    cell = cell.merge(crosswalk, on="tehc_st_fips", how="left")
    cell["state_abbreviation"] = cell["state_abbreviation"].fillna(cell["state_abbreviation_filled"])
    cell = cell.drop(columns=["state_abbreviation_filled"])
    cell = cell.sort_values(["reference_year", "state_abbreviation", "MONTHCODE"], kind="stable").reset_index(drop=True)

    single_cols = [
        "cms_updated_pending_rate",
        "cms_updated_renewed_form_rate",
        "cms_updated_procedural_share_of_terminated",
        "cms_updated_renewed_ex_parte_rate",
    ]
    for col in single_cols:
        zcol = f"z_{col}"
        rankcol = f"rank_{col}"
        cell[zcol] = np.nan
        cell[rankcol] = np.nan
        mask_2023 = cell["reference_year"].eq(2023)
        cell.loc[mask_2023, zcol] = (
            cell.loc[mask_2023]
            .groupby("MONTHCODE", sort=False)[col]
            .transform(
                lambda s: (s - s.mean()) / s.std(ddof=0)
                if s.notna().sum() > 1 and s.std(ddof=0) > 0
                else np.nan
            )
        )
        cell.loc[mask_2023, rankcol] = (
            cell.loc[mask_2023]
            .groupby("MONTHCODE", sort=False)[col]
            .transform(lambda s: s.rank(method="average", pct=True))
        )

    cell["backlog_automation_index"] = mean_of_available(
        pd.DataFrame(
            {
                "pending": cell["z_cms_updated_pending_rate"],
                "low_ex_parte": -cell["z_cms_updated_renewed_ex_parte_rate"],
            }
        )
    )
    cell["backlog_form_index"] = mean_of_available(
        pd.DataFrame(
            {
                "pending": cell["z_cms_updated_pending_rate"],
                "manual": cell["z_cms_updated_renewed_form_rate"],
            }
        )
    )
    cell["backlog_automation_rank_index"] = mean_of_available(
        pd.DataFrame(
            {
                "pending_rank": cell["rank_cms_updated_pending_rate"],
                "low_ex_parte_rank": 1 - cell["rank_cms_updated_renewed_ex_parte_rate"],
            }
        )
    )

    for variant, meta in DECOMP_EXPOSURES.items():
        col = meta["column"]
        for alignment, shift in ALIGNMENTS.items():
            if shift == 0:
                cell[f"{variant}_{alignment}"] = cell[col]
            else:
                cell[f"{variant}_{alignment}"] = cell.groupby(
                    ["reference_year", "state_abbreviation"], sort=False
                )[col].shift(shift)

    return cell


def build_outcome_audit(cell: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for outcome, spec in OUTCOME_SPECS.items():
        for reference_year in [2021, 2022, 2023]:
            for window, months in WINDOWS.items():
                subset = cell.loc[
                    cell["reference_year"].eq(reference_year) & cell["MONTHCODE"].isin(months)
                ].copy()
                support_rows = int(subset[f"{outcome}__support_rows"].sum())
                support_weight = float(subset[f"{outcome}__support_weight"].sum())
                event_weight = float(
                    (subset[f"{outcome}__rate"] * subset[f"{outcome}__support_weight"]).fillna(0).sum()
                )
                rate = event_weight / support_weight if support_weight > 0 else np.nan
                rows.append(
                    {
                        "dataset": "SIPP",
                        "reference_year": reference_year,
                        "window": window,
                        "outcome": outcome,
                        "label": spec["label"],
                        "outcome_kind": spec["kind"],
                        "support_rows": support_rows,
                        "support_weight": round(support_weight, 2),
                        "event_weight": round(event_weight, 2),
                        "event_rate_weighted": round(rate, 6) if rate == rate else np.nan,
                    }
                )
    return pd.DataFrame(rows)


def build_outcome_timing(cell: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    subset_2023 = cell.loc[cell["reference_year"].eq(2023)].copy()
    variant = OUTCOME_ROBUSTNESS_EXPOSURE
    meta = DECOMP_EXPOSURES[variant]

    for outcome, spec in OUTCOME_SPECS.items():
        for window, months in WINDOWS.items():
            subset = subset_2023.loc[subset_2023["MONTHCODE"].isin(months)].copy()
            for alignment in ALIGNMENTS:
                exp_col = f"{variant}_{alignment}"
                monthly_corrs: list[tuple[float, float]] = []
                monthly_diffs: list[tuple[float, float]] = []
                total_support_rows = 0
                total_support_weight = 0.0
                months_used = 0
                for month in months:
                    month_df = subset.loc[subset["MONTHCODE"].eq(month)].copy()
                    support_col = f"{outcome}__support_rows"
                    weight_col = f"{outcome}__support_weight"
                    rate_col = f"{outcome}__rate"
                    mask = (
                        month_df[exp_col].notna()
                        & month_df[rate_col].notna()
                        & month_df[support_col].ge(1)
                        & month_df[weight_col].gt(0)
                    )
                    if int(mask.sum()) < MIN_MONTHLY_STATE_SUPPORT:
                        continue
                    months_used += 1
                    support_rows = int(month_df.loc[mask, support_col].sum())
                    support_weight = float(month_df.loc[mask, weight_col].sum())
                    total_support_rows += support_rows
                    total_support_weight += support_weight

                    corr = weighted_corr(
                        month_df.loc[mask, exp_col],
                        month_df.loc[mask, rate_col],
                        month_df.loc[mask, weight_col],
                    )
                    monthly_corrs.append((corr, support_weight))

                    valid = month_df.loc[mask].copy()
                    tertile = pd.qcut(
                        valid[exp_col].rank(method="first"),
                        q=3,
                        labels=["low", "mid", "high"],
                    )
                    valid["exposure_tertile"] = tertile.astype("string")
                    low = valid.loc[valid["exposure_tertile"].eq("low")]
                    high = valid.loc[valid["exposure_tertile"].eq("high")]
                    low_rate = weighted_rate(low[rate_col], low[weight_col])
                    high_rate = weighted_rate(high[rate_col], high[weight_col])
                    monthly_diffs.append((high_rate - low_rate, support_weight))

                if total_support_rows < MIN_TOTAL_SUPPORT or months_used == 0:
                    continue

                corr_est = average_monthly_estimates(monthly_corrs)
                diff_est = average_monthly_estimates(monthly_diffs)
                expected_sign = meta["base_sign"] * spec["outcome_direction"]

                rows.append(
                    {
                        "dataset": "SIPP",
                        "reference_year": 2023,
                        "window": window,
                        "exposure_family": meta["family"],
                        "exposure_variant": variant,
                        "alignment": alignment,
                        "outcome": outcome,
                        "support_rows": total_support_rows,
                        "support_weight": round(total_support_weight, 2),
                        "months_used": months_used,
                        "weighted_corr": round(corr_est, 4) if corr_est == corr_est else np.nan,
                        "high_minus_low": round(diff_est, 4) if diff_est == diff_est else np.nan,
                        "direction_flag": (
                            "expected"
                            if corr_est == corr_est and np.sign(corr_est) == np.sign(expected_sign)
                            else ("zero" if corr_est == 0 else ("missing" if corr_est != corr_est else "unexpected"))
                        ),
                        "label": spec["label"],
                    }
                )
    return pd.DataFrame(rows)


def build_outcome_falsification(cell: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    variant = OUTCOME_ROBUSTNESS_EXPOSURE
    alignment = "same"
    exp_col = f"{variant}_{alignment}"
    core_months = WINDOWS["core_aug_oct_2023"]

    later = cell.loc[cell["reference_year"].eq(2023) & cell["MONTHCODE"].isin(core_months)].copy()
    later_state = (
        later.groupby("state_abbreviation", sort=True)
        .agg(exposure_value=(exp_col, "mean"), exposure_weight=("total_weight", "sum"))
        .reset_index()
    )
    later_state = later_state.loc[later_state["exposure_value"].notna()].copy()
    later_state["later_exposure_tertile"] = pd.qcut(
        later_state["exposure_value"].rank(method="first"),
        q=3,
        labels=["low", "mid", "high"],
    ).astype("string")

    state_rows = []
    for reference_year in [2021, 2022, 2023]:
        year_df = cell.loc[cell["reference_year"].eq(reference_year) & cell["MONTHCODE"].isin(core_months)].copy()
        for state, g in year_df.groupby("state_abbreviation", sort=True):
            row = {
                "reference_year": reference_year,
                "state_abbreviation": state,
            }
            for outcome in OUTCOME_SPECS:
                sw = float(g[f"{outcome}__support_weight"].sum())
                ew = float((g[f"{outcome}__rate"] * g[f"{outcome}__support_weight"]).fillna(0).sum())
                row[f"{outcome}__support_weight"] = sw
                row[f"{outcome}__state_rate"] = ew / sw if sw > 0 else np.nan
            state_rows.append(row)
    state_df = pd.DataFrame(state_rows)
    merged = state_df.merge(
        later_state[["state_abbreviation", "later_exposure_tertile"]],
        on="state_abbreviation",
        how="inner",
    )

    for outcome, spec in OUTCOME_SPECS.items():
        year_contrasts: dict[int, float] = {}
        for reference_year in [2021, 2022, 2023]:
            year_df = merged.loc[merged["reference_year"].eq(reference_year)].copy()
            rate_col = f"{outcome}__state_rate"
            weight_col = f"{outcome}__support_weight"
            low = year_df.loc[year_df["later_exposure_tertile"].eq("low")]
            high = year_df.loc[year_df["later_exposure_tertile"].eq("high")]
            low_rate = weighted_rate(low[rate_col], low[weight_col])
            high_rate = weighted_rate(high[rate_col], high[weight_col])
            year_contrasts[reference_year] = high_rate - low_rate

        expected_sign = DECOMP_EXPOSURES[variant]["base_sign"] * spec["outcome_direction"]
        unwinding = year_contrasts[2023]
        max_pre_abs = max(abs(year_contrasts[2021]), abs(year_contrasts[2022]))
        same_direction_big_pre = (
            np.sign(year_contrasts[2021]) == np.sign(expected_sign)
            and np.sign(year_contrasts[2022]) == np.sign(expected_sign)
            and max_pre_abs >= abs(unwinding)
        )
        rows.append(
            {
                "exposure_variant": variant,
                "alignment": alignment,
                "outcome": outcome,
                "pre_2021_contrast": round(year_contrasts[2021], 4) if year_contrasts[2021] == year_contrasts[2021] else np.nan,
                "pre_2022_contrast": round(year_contrasts[2022], 4) if year_contrasts[2022] == year_contrasts[2022] else np.nan,
                "unwinding_2023_contrast": round(unwinding, 4) if unwinding == unwinding else np.nan,
                "max_pre_abs_contrast": round(max_pre_abs, 4) if max_pre_abs == max_pre_abs else np.nan,
                "same_direction_big_pre": bool(same_direction_big_pre),
                "falsification_pass_outcome": bool((abs(unwinding) > max_pre_abs) and not same_direction_big_pre),
            }
        )
    return pd.DataFrame(rows)


def build_exposure_decomposition(cell: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    fals_rows: list[dict[str, object]] = []
    subset_2023 = cell.loc[cell["reference_year"].eq(2023)].copy()
    outcomes_for_decomp = [
        "medicaid_exit_to_uninsured_next",
        "persistent_uninsured_h2",
        "broad_exit_resolved_insured_h2",
    ]

    for variant, meta in DECOMP_EXPOSURES.items():
        for window, months in WINDOWS.items():
            subset = subset_2023.loc[subset_2023["MONTHCODE"].isin(months)].copy()
            for alignment in ALIGNMENTS:
                exp_col = f"{variant}_{alignment}"
                for outcome in outcomes_for_decomp:
                    spec = OUTCOME_SPECS[outcome]
                    monthly_corrs: list[tuple[float, float]] = []
                    total_support_rows = 0
                    total_support_weight = 0.0
                    months_used = 0
                    for month in months:
                        month_df = subset.loc[subset["MONTHCODE"].eq(month)].copy()
                        support_col = f"{outcome}__support_rows"
                        weight_col = f"{outcome}__support_weight"
                        rate_col = f"{outcome}__rate"
                        mask = (
                            month_df[exp_col].notna()
                            & month_df[rate_col].notna()
                            & month_df[support_col].ge(1)
                            & month_df[weight_col].gt(0)
                        )
                        if int(mask.sum()) < MIN_MONTHLY_STATE_SUPPORT:
                            continue
                        months_used += 1
                        support_rows = int(month_df.loc[mask, support_col].sum())
                        support_weight = float(month_df.loc[mask, weight_col].sum())
                        total_support_rows += support_rows
                        total_support_weight += support_weight
                        corr = weighted_corr(
                            month_df.loc[mask, exp_col],
                            month_df.loc[mask, rate_col],
                            month_df.loc[mask, weight_col],
                        )
                        monthly_corrs.append((corr, support_weight))

                    if total_support_rows < MIN_TOTAL_SUPPORT or months_used == 0:
                        continue

                    corr_est = average_monthly_estimates(monthly_corrs)
                    expected_sign = meta["base_sign"] * spec["outcome_direction"]
                    rows.append(
                        {
                            "dataset": "SIPP",
                            "reference_year": 2023,
                            "window": window,
                            "exposure_family": meta["family"],
                            "exposure_variant": variant,
                            "exposure_kind": meta["kind"],
                            "alignment": alignment,
                            "outcome": outcome,
                            "support_rows": total_support_rows,
                            "support_weight": round(total_support_weight, 2),
                            "months_used": months_used,
                            "estimate_or_contrast": round(corr_est, 4) if corr_est == corr_est else np.nan,
                            "direction_flag": (
                                "expected"
                                if corr_est == corr_est and np.sign(corr_est) == np.sign(expected_sign)
                                else ("zero" if corr_est == 0 else ("missing" if corr_est != corr_est else "unexpected"))
                            ),
                            "notes": meta["notes"],
                        }
                    )

        core_months = WINDOWS["core_aug_oct_2023"]
        later = cell.loc[cell["reference_year"].eq(2023) & cell["MONTHCODE"].isin(core_months)].copy()
        later_state = (
            later.groupby("state_abbreviation", sort=True)
            .agg(exposure_value=(f"{variant}_same", "mean"), exposure_weight=("total_weight", "sum"))
            .reset_index()
        )
        later_state = later_state.loc[later_state["exposure_value"].notna()].copy()
        if len(later_state) >= 20:
            later_state["later_exposure_tertile"] = pd.qcut(
                later_state["exposure_value"].rank(method="first"),
                q=3,
                labels=["low", "mid", "high"],
            ).astype("string")
            outcome = "persistent_uninsured_h2"
            state_rows = []
            for reference_year in [2021, 2022, 2023]:
                year_df = cell.loc[cell["reference_year"].eq(reference_year) & cell["MONTHCODE"].isin(core_months)].copy()
                for state, g in year_df.groupby("state_abbreviation", sort=True):
                    sw = float(g[f"{outcome}__support_weight"].sum())
                    ew = float((g[f"{outcome}__rate"] * g[f"{outcome}__support_weight"]).fillna(0).sum())
                    state_rows.append(
                        {
                            "reference_year": reference_year,
                            "state_abbreviation": state,
                            "support_weight": sw,
                            "state_rate": ew / sw if sw > 0 else np.nan,
                        }
                    )
            state_df = pd.DataFrame(state_rows)
            merged = state_df.merge(
                later_state[["state_abbreviation", "later_exposure_tertile"]],
                on="state_abbreviation",
                how="inner",
            )
            year_contrasts: dict[int, float] = {}
            for reference_year in [2021, 2022, 2023]:
                year_df = merged.loc[merged["reference_year"].eq(reference_year)].copy()
                low = year_df.loc[year_df["later_exposure_tertile"].eq("low")]
                high = year_df.loc[year_df["later_exposure_tertile"].eq("high")]
                low_rate = weighted_rate(low["state_rate"], low["support_weight"])
                high_rate = weighted_rate(high["state_rate"], high["support_weight"])
                year_contrasts[reference_year] = high_rate - low_rate
            max_pre_abs = max(abs(year_contrasts[2021]), abs(year_contrasts[2022]))
            fals_rows.append(
                {
                    "exposure_variant": variant,
                    "alignment": "same",
                    "outcome": outcome,
                    "pre_2021_contrast": round(year_contrasts[2021], 4) if year_contrasts[2021] == year_contrasts[2021] else np.nan,
                    "pre_2022_contrast": round(year_contrasts[2022], 4) if year_contrasts[2022] == year_contrasts[2022] else np.nan,
                    "unwinding_2023_contrast": round(year_contrasts[2023], 4) if year_contrasts[2023] == year_contrasts[2023] else np.nan,
                    "max_pre_abs_contrast": round(max_pre_abs, 4) if max_pre_abs == max_pre_abs else np.nan,
                    "falsification_pass_outcome": bool(abs(year_contrasts[2023]) > max_pre_abs),
                }
            )

    timing = pd.DataFrame(rows)
    ranking_rows: list[dict[str, object]] = []
    for variant, meta in DECOMP_EXPOSURES.items():
        subset = timing.loc[timing["exposure_variant"].eq(variant)].copy()
        for window in WINDOWS:
            for alignment in ALIGNMENTS:
                g = subset.loc[subset["window"].eq(window) & subset["alignment"].eq(alignment)].copy()
                if g.empty:
                    continue
                signed_vals = []
                for _, row in g.iterrows():
                    outcome_direction = OUTCOME_SPECS[row["outcome"]]["outcome_direction"]
                    signed_vals.append(float(row["estimate_or_contrast"]) * meta["base_sign"] * outcome_direction)
                ranking_rows.append(
                    {
                        "exposure_family": meta["family"],
                        "exposure_variant": variant,
                        "exposure_kind": meta["kind"],
                        "window": window,
                        "alignment": alignment,
                        "mean_signed_corr_all": round(float(np.nanmean(signed_vals)), 4) if len(signed_vals) else np.nan,
                        "all_expected_direction": bool((g["direction_flag"] == "expected").all()),
                        "outcomes_used": int(g["outcome"].nunique()),
                    }
                )
    ranking = pd.DataFrame(ranking_rows).sort_values(
        ["window", "mean_signed_corr_all"], ascending=[True, False], kind="stable"
    ).reset_index(drop=True)
    falsification = pd.DataFrame(fals_rows)
    return timing, ranking, falsification


def build_summary(
    outcome_timing: pd.DataFrame,
    outcome_falsification: pd.DataFrame,
    decomp_ranking: pd.DataFrame,
    decomp_falsification: pd.DataFrame,
) -> dict[str, object]:
    robust_outcomes = []
    for outcome in OUTCOME_SPECS:
        subset = outcome_timing.loc[
            outcome_timing["outcome"].eq(outcome) & outcome_timing["alignment"].isin(["same", "lag1"])
        ].copy()
        if subset.empty:
            continue
        core = subset.loc[subset["window"].eq("core_aug_oct_2023")].sort_values("weighted_corr", ascending=False)
        mature = subset.loc[subset["window"].eq("mature_jun_oct_2023")].sort_values("weighted_corr", ascending=False)
        if core.empty or mature.empty:
            continue
        best_core = core.iloc[0]
        best_mature = mature.iloc[0]
        if (
            best_core["alignment"] == best_mature["alignment"]
            and float(best_core["weighted_corr"]) > 0
            and float(best_mature["weighted_corr"]) > 0
            and best_core["direction_flag"] == "expected"
            and best_mature["direction_flag"] == "expected"
        ):
            robust_outcomes.append(
                {
                    "outcome": outcome,
                    "alignment": best_core["alignment"],
                    "core_corr": float(best_core["weighted_corr"]),
                    "mature_corr": float(best_mature["weighted_corr"]),
                }
            )

    decomp_pick = decomp_ranking.loc[decomp_ranking["alignment"].isin(["same", "lag1"])].copy()
    top_core = decomp_pick.loc[decomp_pick["window"].eq("core_aug_oct_2023")].head(3).to_dict("records")
    top_mature = decomp_pick.loc[decomp_pick["window"].eq("mature_jun_oct_2023")].head(3).to_dict("records")

    def get_fals_pass(name: str) -> bool:
        row = decomp_falsification.loc[decomp_falsification["exposure_variant"].eq(name)]
        return bool(row["falsification_pass_outcome"].all()) if not row.empty else False

    composite_fals = get_fals_pass("backlog_automation_index")
    pending_fals = get_fals_pass("pending_rate")
    exparte_fals = get_fals_pass("ex_parte_renewal_rate")

    verdict = "MIXED_ROUND3"
    if len(robust_outcomes) >= 2 and composite_fals:
        verdict = "ROUND3_SUPPORTS_CONTINUATION"
    elif len(robust_outcomes) >= 1:
        verdict = "ROUND3_PARTIAL_SUPPORT"

    return {
        "verdict": verdict,
        "robust_outcomes": robust_outcomes,
        "outcome_exposure_used": OUTCOME_ROBUSTNESS_EXPOSURE,
        "top_core_nonlead_exposures": top_core,
        "top_mature_nonlead_exposures": top_mature,
        "composite_falsification_pass": composite_fals,
        "pending_falsification_pass": pending_fals,
        "exparte_falsification_pass": exparte_fals,
        "artifacts": {
            "outcome_audit_csv": str(OUTCOME_AUDIT_CSV.relative_to(PROJECT_ROOT)),
            "outcome_timing_csv": str(OUTCOME_TIMING_CSV.relative_to(PROJECT_ROOT)),
            "outcome_falsification_csv": str(OUTCOME_FALSIFICATION_CSV.relative_to(PROJECT_ROOT)),
            "exposure_timing_csv": str(EXPOSURE_TIMING_CSV.relative_to(PROJECT_ROOT)),
            "exposure_ranking_csv": str(EXPOSURE_RANKING_CSV.relative_to(PROJECT_ROOT)),
            "exposure_falsification_csv": str(EXPOSURE_FALSIFICATION_CSV.relative_to(PROJECT_ROOT)),
        },
    }


def write_markdown(
    outcome_audit: pd.DataFrame,
    outcome_timing: pd.DataFrame,
    outcome_falsification: pd.DataFrame,
    decomp_ranking: pd.DataFrame,
    decomp_falsification: pd.DataFrame,
    summary: dict[str, object],
) -> None:
    audit_2023 = outcome_audit.loc[
        (outcome_audit["reference_year"].eq(2023)) & (outcome_audit["window"].eq("core_aug_oct_2023"))
    ][["outcome", "support_rows", "support_weight", "event_rate_weighted"]].copy()

    outcome_nonlead = outcome_timing.loc[outcome_timing["alignment"].isin(["same", "lag1"])].copy()
    outcome_best = outcome_nonlead.sort_values(
        ["outcome", "window", "weighted_corr"], ascending=[True, True, False], kind="stable"
    ).groupby(["outcome", "window"], as_index=False).head(1)

    top_core = decomp_ranking.loc[decomp_ranking["window"].eq("core_aug_oct_2023")].head(5).copy()
    top_mature = decomp_ranking.loc[decomp_ranking["window"].eq("mature_jun_oct_2023")].head(5).copy()

    lines = [
        "# Avoidable Churn Round-3 Robustness",
        "",
        "## Purpose",
        "",
        "This round advances the next locked testing order:",
        "",
        "1. outcome robustness around persistence definitions",
        "2. exposure decomposition around the leading burden candidate",
        "",
        "The goal is to test whether the current `avoidable churn` branch remains coherent under nearby outcome definitions and whether the leading composite candidate still earns its place when compared with its components.",
        "",
        "## 2023 Core Outcome Support",
        "",
        df_to_markdown(audit_2023),
        "",
        "## Outcome Robustness: Best Nonlead Alignment By Outcome",
        "",
        df_to_markdown(
            outcome_best[["outcome", "window", "alignment", "weighted_corr", "high_minus_low", "direction_flag"]]
        ),
        "",
        "## Outcome Robustness: Falsification For `backlog_automation_index / same`",
        "",
        df_to_markdown(outcome_falsification),
        "",
        "## Exposure Decomposition: Top Nonlead Rankings In Core Window",
        "",
        df_to_markdown(top_core),
        "",
        "## Exposure Decomposition: Top Nonlead Rankings In Mature Window",
        "",
        df_to_markdown(top_mature),
        "",
        "## Exposure Decomposition: Falsification On `persistent_uninsured_h2`",
        "",
        df_to_markdown(decomp_falsification),
        "",
        "## Interpretation",
        "",
        "- Outcome robustness is better if at least two harmful persistence-style outcomes retain an expected-sign `same` or `lag1` signal across both windows.",
        "- Exposure decomposition is better if the backlog-automation composite stays competitive relative to `pending_rate` and `ex_parte_renewal_rate`, rather than collapsing once it is unpacked.",
        "- This round still treats `lead1` as informative but not sufficient for a clean upgrade.",
        "",
        "## Summary Verdict",
        "",
        f"- verdict: `{summary['verdict']}`",
        f"- outcome exposure used for robustness: `{summary['outcome_exposure_used']}`",
        f"- robust harmful outcomes found: `{len(summary['robust_outcomes'])}`",
        f"- composite falsification pass on `persistent_uninsured_h2`: `{summary['composite_falsification_pass']}`",
        f"- pending-only falsification pass on `persistent_uninsured_h2`: `{summary['pending_falsification_pass']}`",
        f"- ex-parte-only falsification pass on `persistent_uninsured_h2`: `{summary['exparte_falsification_pass']}`",
    ]
    DIAGNOSTICS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    layer = load_layer()
    layer = derive_additional_outcomes(layer)

    cell = build_state_month_cells(layer)
    cell.to_csv(STATE_MONTH_CELL_CSV, index=False)

    outcome_audit = build_outcome_audit(cell)
    outcome_timing = build_outcome_timing(cell)
    outcome_falsification = build_outcome_falsification(cell)
    decomp_timing, decomp_ranking, decomp_falsification = build_exposure_decomposition(cell)

    outcome_audit.to_csv(OUTCOME_AUDIT_CSV, index=False)
    outcome_timing.to_csv(OUTCOME_TIMING_CSV, index=False)
    outcome_falsification.to_csv(OUTCOME_FALSIFICATION_CSV, index=False)
    decomp_timing.to_csv(EXPOSURE_TIMING_CSV, index=False)
    decomp_ranking.to_csv(EXPOSURE_RANKING_CSV, index=False)
    decomp_falsification.to_csv(EXPOSURE_FALSIFICATION_CSV, index=False)

    summary = build_summary(
        outcome_timing=outcome_timing,
        outcome_falsification=outcome_falsification,
        decomp_ranking=decomp_ranking,
        decomp_falsification=decomp_falsification,
    )
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(
        outcome_audit=outcome_audit,
        outcome_timing=outcome_timing,
        outcome_falsification=outcome_falsification,
        decomp_ranking=decomp_ranking,
        decomp_falsification=decomp_falsification,
        summary=summary,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
