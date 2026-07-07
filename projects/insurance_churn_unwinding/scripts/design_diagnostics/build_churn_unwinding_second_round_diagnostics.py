from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_STACK = OUTPUT_DIR / "sipp_unwinding_feature_stack_2021_2023.parquet"
FEATURE_AUDIT_CSV = OUTPUT_DIR / "sipp_subgroup_candidate_audit.csv"

TIMING_LONG_CSV = OUTPUT_DIR / "second_round_timing_matrix_long.csv"
HIGHLOW_LONG_CSV = OUTPUT_DIR / "second_round_highlow_matrix_long.csv"
FALSIFICATION_LONG_CSV = OUTPUT_DIR / "second_round_falsification_matrix_long.csv"
FALSIFICATION_SUMMARY_CSV = OUTPUT_DIR / "second_round_falsification_summary.csv"
SUBGROUP_RATES_CSV = OUTPUT_DIR / "second_round_subgroup_rates.csv"
SUBGROUP_STABILITY_CSV = OUTPUT_DIR / "second_round_subgroup_stability_summary.csv"
OMITTED_VARIANTS_CSV = OUTPUT_DIR / "second_round_omitted_exposure_variants.csv"
STATE_MONTH_CELL_CSV = OUTPUT_DIR / "second_round_unwinding_state_month_cells.csv"
RANKING_CSV = OUTPUT_DIR / "second_round_alignment_ranking.csv"
GATE_JSON = OUTPUT_DIR / "second_round_gate_summary.json"
DIAGNOSTICS_MD = OUTPUT_DIR / "churn_unwinding_second_round_diagnostics.md"

WINDOWS = {
    "core_aug_nov_2023": [8, 9, 10, 11],
    "extended_mar_nov_2023": [3, 4, 5, 6, 7, 8, 9, 10, 11],
}

OUTCOME_MAP = {
    "medicaid_exit_rate_w": "medicaid_exit_next",
    "exit_to_uninsured_rate_w": "medicaid_exit_to_uninsured_next",
}

EXPOSURE_VARIANTS = {
    "procedural_term_count": {
        "family": "procedural_termination_burden",
        "column": "cms_updated_procedural_termination_n",
        "expected_sign": 1,
        "notes": "Raw count of procedural terminations; useful descriptively but size-loaded.",
        "gate_eligible": False,
    },
    "procedural_term_share": {
        "family": "procedural_termination_burden",
        "column": "cms_updated_procedural_share_of_terminated",
        "expected_sign": 1,
        "notes": "Procedural terminations as a share of all terminations.",
        "gate_eligible": True,
    },
    "renewal_due_count": {
        "family": "renewal_workload_burden",
        "column": "cms_updated_renewal_due_n",
        "expected_sign": 1,
        "notes": "Raw renewal-due count; useful descriptively but size-loaded.",
        "gate_eligible": False,
    },
    "pending_count": {
        "family": "pending_backlog_burden",
        "column": "cms_updated_pending_n",
        "expected_sign": 1,
        "notes": "Raw pending count; useful descriptively but size-loaded.",
        "gate_eligible": False,
    },
    "pending_rate": {
        "family": "pending_backlog_burden",
        "column": "cms_updated_pending_rate",
        "expected_sign": 1,
        "notes": "Pending renewals as a rate-type backlog measure.",
        "gate_eligible": True,
    },
    "ex_parte_renewal_rate": {
        "family": "ex_parte_renewal_relief",
        "column": "cms_updated_renewed_ex_parte_rate",
        "expected_sign": -1,
        "notes": "Higher ex parte renewal should relieve administrative burden.",
        "gate_eligible": True,
    },
    "renewal_form_rate": {
        "family": "manual_renewal_burden",
        "column": "cms_updated_renewed_form_rate",
        "expected_sign": 1,
        "notes": "More renewal-by-form should proxy heavier manual paperwork burden.",
        "gate_eligible": True,
    },
    "ineligible_rate": {
        "family": "formal_ineligibility_channel",
        "column": "cms_updated_ineligible_rate",
        "expected_sign": 1,
        "notes": "Contrast mechanism: likely reflects true ineligibility rather than procedural loss alone.",
        "gate_eligible": False,
    },
}

OMITTED_VARIANTS = [
    {
        "exposure_variant": "renewal_due_rate",
        "family": "renewal_workload_burden",
        "reason": "Not added because the staged CMS updated-renewal files do not expose a clean, shared denominator for a stable renewal-due rate beyond the raw count itself.",
    }
]


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


def sign_flag(value: float, expected_sign: int) -> str:
    if value is None or np.isnan(value):
        return "missing"
    if value == 0:
        return "zero"
    if np.sign(value) == np.sign(expected_sign):
        return "expected"
    return "unexpected"


def assign_tertiles(series: pd.Series) -> pd.Series:
    ranked = series.rank(method="first")
    return pd.qcut(ranked, q=3, labels=["low", "mid", "high"])


def simple_spearman(x: pd.Series, y: pd.Series) -> float:
    xy = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(xy) < 2:
        return float("nan")
    xr = xy["x"].rank(method="average")
    yr = xy["y"].rank(method="average")
    if xr.nunique() < 2 or yr.nunique() < 2:
        return float("nan")
    return float(np.corrcoef(xr, yr)[0, 1])


def df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    stack = pd.read_parquet(FEATURE_STACK)
    audit = pd.read_csv(FEATURE_AUDIT_CSV)
    return stack, audit


def build_state_month_cells(stack: pd.DataFrame) -> pd.DataFrame:
    df = stack.loc[
        (stack["reference_year"] == 2023)
        & (stack["eligible_medicaid_transition"] == True)
        & stack["tehc_st_fips"].notna()
    ].copy()

    group_cols = [
        "tehc_st_fips",
        "state_abbreviation",
        "MONTHCODE",
        "cms_reporting_period",
        "reporting_label",
    ]

    rows: list[dict[str, object]] = []
    for keys, g in df.groupby(group_cols, dropna=False, sort=True):
        row = dict(zip(group_cols, keys))
        row.update(
            {
                "dataset": "SIPP",
                "reference_year": 2023,
                "eligible_rows": int(len(g)),
                "eligible_weight_sum": float(g["WPFINWGT"].sum()),
                "persons": int(g[["SSUID", "PNUM"]].drop_duplicates().shape[0]),
                "medicaid_exit_rate_w": weighted_rate(g["medicaid_exit_next"], g["WPFINWGT"]),
                "exit_to_uninsured_rate_w": weighted_rate(g["medicaid_exit_to_uninsured_next"], g["WPFINWGT"]),
            }
        )
        for meta in EXPOSURE_VARIANTS.values():
            col = meta["column"]
            valid = g[col].dropna()
            row[col] = valid.iloc[0] if len(valid) else np.nan
        rows.append(row)

    cell = pd.DataFrame(rows).sort_values(["state_abbreviation", "MONTHCODE"], kind="stable").reset_index(drop=True)
    for variant, meta in EXPOSURE_VARIANTS.items():
        col = meta["column"]
        cell[f"{variant}_same"] = cell[col]
        cell[f"{variant}_lag1"] = cell.groupby("state_abbreviation", sort=False)[col].shift(1)
        cell[f"{variant}_lead1"] = cell.groupby("state_abbreviation", sort=False)[col].shift(-1)
        cell[f"{variant}_lag2"] = cell.groupby("state_abbreviation", sort=False)[col].shift(2)
    return cell


def build_timing_matrix(cell: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for window, months in WINDOWS.items():
        subset = cell.loc[cell["MONTHCODE"].isin(months)].copy()
        for variant, meta in EXPOSURE_VARIANTS.items():
            for alignment in ["same", "lag1", "lead1", "lag2"]:
                x = subset[f"{variant}_{alignment}"]
                mask = x.notna() & subset["eligible_weight_sum"].notna()
                support_rows = int(mask.sum())
                if alignment == "lag2" and support_rows < 100:
                    continue
                support_weight = float(subset.loc[mask, "eligible_weight_sum"].sum())
                for outcome_col, outcome_name in OUTCOME_MAP.items():
                    est = weighted_corr(x, subset[outcome_col], subset["eligible_weight_sum"])
                    rows.append(
                        {
                            "dataset": "SIPP",
                            "reference_year": 2023,
                            "window": window,
                            "metric_type": "weighted_corr",
                            "exposure_family": meta["family"],
                            "exposure_variant": variant,
                            "alignment": alignment,
                            "outcome": outcome_name,
                            "support_rows": support_rows,
                            "support_weight": round(support_weight, 2),
                            "estimate_or_contrast": round(est, 4) if not np.isnan(est) else np.nan,
                            "direction_flag": sign_flag(est, meta["expected_sign"]),
                            "notes": meta["notes"],
                        }
                    )
    return pd.DataFrame(rows)


def build_highlow_matrix(cell: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for window, months in WINDOWS.items():
        subset = cell.loc[cell["MONTHCODE"].isin(months)].copy()
        for variant, meta in EXPOSURE_VARIANTS.items():
            for alignment in ["same", "lag1", "lead1", "lag2"]:
                xcol = f"{variant}_{alignment}"
                available = subset.loc[subset[xcol].notna()].copy()
                if alignment == "lag2" and len(available) < 100:
                    continue
                if len(available) < 9:
                    continue
                available["tertile"] = assign_tertiles(available[xcol])
                low = available.loc[available["tertile"] == "low"].copy()
                high = available.loc[available["tertile"] == "high"].copy()
                support_rows = int(len(low) + len(high))
                support_weight = float(low["eligible_weight_sum"].sum() + high["eligible_weight_sum"].sum())
                for outcome_col, outcome_name in OUTCOME_MAP.items():
                    est = weighted_rate(high[outcome_col], high["eligible_weight_sum"]) - weighted_rate(
                        low[outcome_col], low["eligible_weight_sum"]
                    )
                    rows.append(
                        {
                            "dataset": "SIPP",
                            "reference_year": 2023,
                            "window": window,
                            "metric_type": "high_minus_low",
                            "exposure_family": meta["family"],
                            "exposure_variant": variant,
                            "alignment": alignment,
                            "outcome": outcome_name,
                            "support_rows": support_rows,
                            "support_weight": round(support_weight, 2),
                            "estimate_or_contrast": round(est, 4) if not np.isnan(est) else np.nan,
                            "direction_flag": sign_flag(est, meta["expected_sign"]),
                            "notes": meta["notes"],
                        }
                    )
    return pd.DataFrame(rows)


def build_state_level_core_exposure(cell: pd.DataFrame) -> pd.DataFrame:
    core = cell.loc[cell["MONTHCODE"].isin(WINDOWS["core_aug_nov_2023"])].copy()
    rows: list[dict[str, object]] = []
    for (tehc_st_fips, state_abbreviation), g in core.groupby(["tehc_st_fips", "state_abbreviation"], dropna=False):
        row = {"tehc_st_fips": tehc_st_fips, "state_abbreviation": state_abbreviation}
        for variant in EXPOSURE_VARIANTS:
            for alignment in ["same", "lag1", "lead1", "lag2"]:
                series = g[f"{variant}_{alignment}"]
                mask = series.notna() & g["eligible_weight_sum"].notna()
                if alignment == "lag2" and int(mask.sum()) < 2:
                    row[f"{variant}_{alignment}"] = np.nan
                else:
                    row[f"{variant}_{alignment}"] = weighted_rate(series[mask], g.loc[mask, "eligible_weight_sum"])
        rows.append(row)
    return pd.DataFrame(rows)


def build_state_year_outcomes(stack: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for reference_year in [2021, 2022, 2023]:
        df = stack.loc[
            (stack["reference_year"] == reference_year)
            & (stack["MONTHCODE"].isin(WINDOWS["core_aug_nov_2023"]))
            & (stack["eligible_medicaid_transition"] == True)
            & stack["tehc_st_fips"].notna()
        ].copy()
        for tehc_st_fips, g in df.groupby("tehc_st_fips", dropna=False):
            rows.append(
                {
                    "reference_year": int(reference_year),
                    "tehc_st_fips": tehc_st_fips,
                    "eligible_weight_sum": float(g["WPFINWGT"].sum()),
                    "weighted_exit_rate": weighted_rate(g["medicaid_exit_next"], g["WPFINWGT"]),
                    "weighted_exit_to_uninsured_rate": weighted_rate(
                        g["medicaid_exit_to_uninsured_next"], g["WPFINWGT"]
                    ),
                }
            )
    return pd.DataFrame(rows)


def build_falsification(
    stack: pd.DataFrame,
    cell: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    later_exposure = build_state_level_core_exposure(cell)
    state_year = build_state_year_outcomes(stack)
    long_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for variant, meta in EXPOSURE_VARIANTS.items():
        for alignment in ["same", "lag1", "lead1", "lag2"]:
            value_col = f"{variant}_{alignment}"
            exposure_state = later_exposure[["tehc_st_fips", value_col]].copy()
            exposure_state = exposure_state.loc[exposure_state[value_col].notna()].copy()
            if alignment == "lag2" and len(exposure_state) < 25:
                continue
            if len(exposure_state) < 9:
                continue
            exposure_state["tertile"] = assign_tertiles(exposure_state[value_col])
            merged = state_year.merge(exposure_state[["tehc_st_fips", "tertile"]], on="tehc_st_fips", how="inner")

            outcome_pairs = [
                ("weighted_exit_rate", "medicaid_exit_next"),
                ("weighted_exit_to_uninsured_rate", "medicaid_exit_to_uninsured_next"),
            ]
            for stat_col, outcome_name in outcome_pairs:
                year_contrasts: dict[int, float] = {}
                for reference_year in [2021, 2022, 2023]:
                    year_df = merged.loc[merged["reference_year"] == reference_year].copy()
                    grouped = {}
                    for tertile, g in year_df.groupby("tertile", dropna=False):
                        grouped[str(tertile)] = {
                            "states": int(g["tehc_st_fips"].nunique()),
                            "weight": float(g["eligible_weight_sum"].sum()),
                            "rate": weighted_rate(g[stat_col], g["eligible_weight_sum"]),
                        }
                    if {"low", "high"}.issubset(grouped):
                        contrast = grouped["high"]["rate"] - grouped["low"]["rate"]
                        year_contrasts[reference_year] = float(contrast)
                        long_rows.append(
                            {
                                "dataset": "SIPP",
                                "reference_year": reference_year,
                                "window": "matched_aug_nov_state_precheck",
                                "metric_type": "high_minus_low",
                                "exposure_family": meta["family"],
                                "exposure_variant": variant,
                                "alignment": alignment,
                                "outcome": outcome_name,
                                "support_rows": int(grouped["high"]["states"] + grouped["low"]["states"]),
                                "support_weight": round(grouped["high"]["weight"] + grouped["low"]["weight"], 2),
                                "estimate_or_contrast": round(float(contrast), 4),
                                "direction_flag": sign_flag(float(contrast), meta["expected_sign"]),
                                "notes": "Later 2023 state exposure tertiles applied to matched-month state-level rates.",
                            }
                        )

                if {2021, 2022, 2023}.issubset(year_contrasts):
                    unwinding = year_contrasts[2023]
                    pre_max = max(abs(year_contrasts[2021]), abs(year_contrasts[2022]))
                    same_direction_big_pre = (
                        unwinding != 0
                        and np.sign(year_contrasts[2021]) == np.sign(unwinding)
                        and np.sign(year_contrasts[2022]) == np.sign(unwinding)
                        and abs(year_contrasts[2021]) >= 0.75 * abs(unwinding)
                        and abs(year_contrasts[2022]) >= 0.75 * abs(unwinding)
                    )
                    summary_rows.append(
                        {
                            "exposure_family": meta["family"],
                            "exposure_variant": variant,
                            "alignment": alignment,
                            "outcome": outcome_name,
                            "pre_2021_contrast": round(year_contrasts[2021], 4),
                            "pre_2022_contrast": round(year_contrasts[2022], 4),
                            "unwinding_2023_contrast": round(unwinding, 4),
                            "max_pre_abs_contrast": round(pre_max, 4),
                            "same_direction_big_pre": bool(same_direction_big_pre),
                            "falsification_pass_outcome": bool(
                                (abs(unwinding) > 0) and (pre_max < abs(unwinding)) and (not same_direction_big_pre)
                            ),
                        }
                    )

    return pd.DataFrame(long_rows), pd.DataFrame(summary_rows)


def build_feature_group_rates(stack: pd.DataFrame, retained_families: list[str]) -> pd.DataFrame:
    family_to_col = {
        "age_band": "age_band",
        "female_group": "female_group",
        "household_child_group": "household_child_group",
        "pov_band": "pov_band",
        "snap_group": "snap_group",
        "foreign_born_group": "foreign_born_group",
        "noncitizen_group": "noncitizen_group",
    }
    rows: list[dict[str, object]] = []
    subset = stack.loc[
        stack["reference_year"].isin([2021, 2022, 2023])
        & stack["MONTHCODE"].isin(WINDOWS["core_aug_nov_2023"])
        & (stack["eligible_medicaid_transition"] == True)
    ].copy()

    for family in retained_families:
        col = family_to_col[family]
        for reference_year in [2021, 2022, 2023]:
            year_df = subset.loc[subset["reference_year"] == reference_year].copy()
            year_df = year_df.loc[year_df[col].notna()].copy()
            for group_label, g in year_df.groupby(col, dropna=False):
                rows.append(
                    {
                        "feature_family": family,
                        "group_label": str(group_label),
                        "reference_year": reference_year,
                        "rows": int(len(g)),
                        "weight_sum": float(g["WPFINWGT"].sum()),
                        "weighted_exit_rate": weighted_rate(g["medicaid_exit_next"], g["WPFINWGT"]),
                        "weighted_exit_to_uninsured_rate": weighted_rate(
                            g["medicaid_exit_to_uninsured_next"], g["WPFINWGT"]
                        ),
                    }
                )
    return pd.DataFrame(rows)


def build_state_baseline_tertile_summary(stack: pd.DataFrame) -> pd.DataFrame:
    pre = stack.loc[
        stack["reference_year"].isin([2021, 2022])
        & stack["MONTHCODE"].isin(WINDOWS["core_aug_nov_2023"])
        & (stack["eligible_medicaid_transition"] == True)
        & stack["tehc_st_fips"].notna()
    ].copy()
    base_rows: list[dict[str, object]] = []
    for tehc_st_fips, g in pre.groupby("tehc_st_fips", dropna=False):
        base_rows.append(
            {
                "tehc_st_fips": tehc_st_fips,
                "baseline_exit_rate": weighted_rate(g["medicaid_exit_next"], g["WPFINWGT"]),
            }
        )
    base = pd.DataFrame(base_rows)
    base["baseline_tertile"] = assign_tertiles(base["baseline_exit_rate"])

    core = stack.loc[
        stack["reference_year"].isin([2021, 2022, 2023])
        & stack["MONTHCODE"].isin(WINDOWS["core_aug_nov_2023"])
        & (stack["eligible_medicaid_transition"] == True)
        & stack["tehc_st_fips"].notna()
    ].copy()
    merged = core.merge(base[["tehc_st_fips", "baseline_tertile"]], on="tehc_st_fips", how="left")

    rows: list[dict[str, object]] = []
    for reference_year in [2021, 2022, 2023]:
        year_df = merged.loc[merged["reference_year"] == reference_year].copy()
        for tertile, g in year_df.groupby("baseline_tertile", dropna=False):
            rows.append(
                {
                    "feature_family": "state_baseline_tertile",
                    "group_label": str(tertile),
                    "reference_year": reference_year,
                    "rows": int(len(g)),
                    "weight_sum": float(g["WPFINWGT"].sum()),
                    "weighted_exit_rate": weighted_rate(g["medicaid_exit_next"], g["WPFINWGT"]),
                    "weighted_exit_to_uninsured_rate": weighted_rate(
                        g["medicaid_exit_to_uninsured_next"], g["WPFINWGT"]
                    ),
                }
            )
    return pd.DataFrame(rows)


def build_subgroup_stability(stack: pd.DataFrame, retained_families: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_rates = build_feature_group_rates(stack, retained_families)
    state_rates = build_state_baseline_tertile_summary(stack)
    all_rates = pd.concat([feature_rates, state_rates], ignore_index=True)

    summary_rows: list[dict[str, object]] = []
    for family in all_rates["feature_family"].drop_duplicates():
        fam = all_rates.loc[all_rates["feature_family"] == family].copy()
        pre = (
            fam.loc[fam["reference_year"].isin([2021, 2022])]
            .groupby("group_label", sort=False)
            .agg(
                pre_weight=("weight_sum", "sum"),
                pre_exit_rate=("weighted_exit_rate", lambda s: weighted_rate(s, fam.loc[s.index, "weight_sum"])),
                pre_exit_to_uninsured_rate=(
                    "weighted_exit_to_uninsured_rate",
                    lambda s: weighted_rate(s, fam.loc[s.index, "weight_sum"]),
                ),
            )
            .reset_index()
        )
        cur = (
            fam.loc[fam["reference_year"] == 2023]
            .groupby("group_label", sort=False)
            .agg(
                unwinding_weight=("weight_sum", "sum"),
                unwinding_exit_rate=("weighted_exit_rate", lambda s: weighted_rate(s, fam.loc[s.index, "weight_sum"])),
                unwinding_exit_to_uninsured_rate=(
                    "weighted_exit_to_uninsured_rate",
                    lambda s: weighted_rate(s, fam.loc[s.index, "weight_sum"]),
                ),
            )
            .reset_index()
        )
        merged = pre.merge(cur, on="group_label", how="inner")
        if len(merged) < 2:
            continue
        for pre_col, cur_col, outcome_name in [
            ("pre_exit_rate", "unwinding_exit_rate", "medicaid_exit_next"),
            ("pre_exit_to_uninsured_rate", "unwinding_exit_to_uninsured_rate", "medicaid_exit_to_uninsured_next"),
        ]:
            spearman = simple_spearman(merged[pre_col], merged[cur_col])
            top_pre = merged.sort_values(pre_col, ascending=False, kind="stable")["group_label"].iloc[0]
            top_cur = merged.sort_values(cur_col, ascending=False, kind="stable")["group_label"].iloc[0]
            summary_rows.append(
                {
                    "feature_family": family,
                    "outcome": outcome_name,
                    "groups_compared": int(len(merged)),
                    "pre_top_group": str(top_pre),
                    "unwinding_top_group": str(top_cur),
                    "spearman_rank_corr": round(spearman, 4) if not np.isnan(spearman) else np.nan,
                    "top_group_match": bool(top_pre == top_cur),
                    "stable_flag": bool((not np.isnan(spearman)) and (spearman >= 0.5) and (top_pre == top_cur)),
                }
            )
    return all_rates, pd.DataFrame(summary_rows)


def build_alignment_ranking(timing_long: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for meta_key, meta in EXPOSURE_VARIANTS.items():
        subset = timing_long.loc[timing_long["exposure_variant"] == meta_key].copy()
        for window in WINDOWS:
            for alignment in sorted(subset["alignment"].dropna().unique()):
                g = subset.loc[(subset["window"] == window) & (subset["alignment"] == alignment)].copy()
                if g.empty:
                    continue
                signed = pd.to_numeric(g["estimate_or_contrast"], errors="coerce") * meta["expected_sign"]
                rows.append(
                    {
                        "exposure_family": meta["family"],
                        "exposure_variant": meta_key,
                        "gate_eligible": meta["gate_eligible"],
                        "window": window,
                        "alignment": alignment,
                        "mean_signed_corr": round(float(signed.mean()), 4) if len(signed.dropna()) else np.nan,
                        "all_expected_direction": bool((g["direction_flag"] == "expected").all()),
                        "outcomes_used": int(g["outcome"].nunique()),
                    }
                )
    ranking = pd.DataFrame(rows)
    return ranking.sort_values(
        ["gate_eligible", "window", "mean_signed_corr"], ascending=[False, True, False], kind="stable"
    ).reset_index(drop=True)


def evaluate_gates(
    falsification_summary: pd.DataFrame,
    subgroup_summary: pd.DataFrame,
    ranking: pd.DataFrame,
) -> dict[str, object]:
    timing_pass_variants: list[str] = []
    timing_choice = None

    gate_ranking = ranking.loc[ranking["gate_eligible"] == True].copy()
    for variant in gate_ranking["exposure_variant"].drop_duplicates():
        var = gate_ranking.loc[gate_ranking["exposure_variant"] == variant].copy()
        core = var.loc[var["window"] == "core_aug_nov_2023"].sort_values("mean_signed_corr", ascending=False)
        ext = var.loc[var["window"] == "extended_mar_nov_2023"].sort_values("mean_signed_corr", ascending=False)
        if core.empty or ext.empty:
            continue
        core_best = core.iloc[0]
        ext_best = ext.iloc[0]
        if (
            core_best["alignment"] == ext_best["alignment"]
            and core_best["alignment"] in {"same", "lag1"}
            and float(core_best["mean_signed_corr"]) > 0
            and float(ext_best["mean_signed_corr"]) > 0
        ):
            timing_pass_variants.append(variant)
    if timing_pass_variants:
        candidates = gate_ranking.loc[gate_ranking["exposure_variant"].isin(timing_pass_variants)].copy()
        picked = (
            candidates.groupby(["exposure_family", "exposure_variant", "alignment"], sort=False)["mean_signed_corr"]
            .min()
            .reset_index()
            .sort_values("mean_signed_corr", ascending=False, kind="stable")
            .iloc[0]
        )
        timing_choice = {
            "exposure_family": picked["exposure_family"],
            "exposure_variant": picked["exposure_variant"],
            "alignment": picked["alignment"],
        }
    else:
        fallback = gate_ranking.loc[gate_ranking["alignment"].isin(["same", "lag1"])].copy()
        if not fallback.empty:
            picked = fallback.sort_values("mean_signed_corr", ascending=False, kind="stable").iloc[0]
            timing_choice = {
                "exposure_family": picked["exposure_family"],
                "exposure_variant": picked["exposure_variant"],
                "alignment": picked["alignment"],
            }

    timing_gate = len(timing_pass_variants) > 0
    falsification_gate = False
    falsification_details: list[dict[str, object]] = []
    if timing_choice is not None:
        fals = falsification_summary.loc[
            (falsification_summary["exposure_variant"] == timing_choice["exposure_variant"])
            & (falsification_summary["alignment"] == timing_choice["alignment"])
        ].copy()
        if not fals.empty:
            falsification_details = fals.to_dict(orient="records")
            falsification_gate = bool(fals["falsification_pass_outcome"].all())

    stability_gate = False
    stability_supporting_families: list[str] = []
    comparator_mean = np.nan
    if not subgroup_summary.empty:
        comparator = subgroup_summary.loc[subgroup_summary["feature_family"] == "state_baseline_tertile"].copy()
        comparator_mean = float(pd.to_numeric(comparator["spearman_rank_corr"], errors="coerce").mean())
        for family in subgroup_summary["feature_family"].drop_duplicates():
            if family == "state_baseline_tertile":
                continue
            fam = subgroup_summary.loc[subgroup_summary["feature_family"] == family].copy()
            mean_spearman = float(pd.to_numeric(fam["spearman_rank_corr"], errors="coerce").mean())
            primary = fam.loc[fam["outcome"] == "medicaid_exit_to_uninsured_next"].copy()
            primary_top_match = bool(primary["top_group_match"].all()) if not primary.empty else False
            if mean_spearman >= max(0.5, comparator_mean + 0.1) and primary_top_match:
                stability_supporting_families.append(family)
        stability_gate = len(stability_supporting_families) >= 2

    if timing_gate and falsification_gate and stability_gate:
        verdict = "GO_RISK_ONLY"
    elif timing_gate and (falsification_gate or stability_gate):
        verdict = "GO_DIAGNOSTICS_PLUS"
    elif (not timing_gate) and (not falsification_gate) and (not stability_gate):
        verdict = "PIVOT_RECOMMENDED"
    else:
        verdict = "NO_GO_CAUSAL_ESCALATION"

    return {
        "timing_gate": timing_gate,
        "timing_pass_variants": timing_pass_variants,
        "timing_choice": timing_choice,
        "falsification_gate": falsification_gate,
        "falsification_details": falsification_details,
        "stability_gate": stability_gate,
        "stability_supporting_families": stability_supporting_families,
        "state_baseline_mean_spearman": round(comparator_mean, 4) if not np.isnan(comparator_mean) else None,
        "verdict": verdict,
    }


def write_markdown(
    timing_long: pd.DataFrame,
    highlow_long: pd.DataFrame,
    falsification_summary: pd.DataFrame,
    subgroup_summary: pd.DataFrame,
    gate_summary: dict[str, object],
) -> None:
    top_timing = (
        timing_long.loc[timing_long["direction_flag"] == "expected"]
        .sort_values("estimate_or_contrast", ascending=False, kind="stable")
        .head(12)
        .copy()
    )
    top_highlow = (
        highlow_long.loc[highlow_long["direction_flag"] == "expected"]
        .sort_values("estimate_or_contrast", ascending=False, kind="stable")
        .head(12)
        .copy()
    )
    subgroup_top = subgroup_summary.sort_values("spearman_rank_corr", ascending=False, kind="stable").head(12)

    lines = [
        "# Churn / Unwinding Second-Round Diagnostics",
        "",
        "## Purpose",
        "",
        "This note extends the first diagnostics pass into a fuller exposure-by-timing matrix, matched-month falsification screen, and subgroup-stability screen.",
        "",
        "The working theory frame is now `administrative renewal burden`, not a single-mechanism bet on procedural friction alone.",
        "",
        "## Gate Verdict",
        "",
        f"- final verdict: `{gate_summary['verdict']}`",
        f"- timing gate: `{gate_summary['timing_gate']}`",
        f"- falsification gate: `{gate_summary['falsification_gate']}`",
        f"- stability gate: `{gate_summary['stability_gate']}`",
        f"- chosen variant for gate evaluation: `{gate_summary['timing_choice']}`",
        "",
        "## Top Timing Signals",
        "",
        df_to_markdown(
            top_timing[
                [
                    "window",
                    "exposure_variant",
                    "alignment",
                    "outcome",
                    "support_rows",
                    "estimate_or_contrast",
                    "direction_flag",
                ]
            ]
        ),
        "",
        "## Top High-Low Contrasts",
        "",
        df_to_markdown(
            top_highlow[
                [
                    "window",
                    "exposure_variant",
                    "alignment",
                    "outcome",
                    "support_rows",
                    "estimate_or_contrast",
                    "direction_flag",
                ]
            ]
        ),
        "",
        "## Falsification Summary",
        "",
        df_to_markdown(
            falsification_summary[
                [
                    "exposure_variant",
                    "alignment",
                    "outcome",
                    "pre_2021_contrast",
                    "pre_2022_contrast",
                    "unwinding_2023_contrast",
                    "max_pre_abs_contrast",
                    "same_direction_big_pre",
                    "falsification_pass_outcome",
                ]
            ].head(18)
        ),
        "",
        "## Subgroup Stability Leaders",
        "",
        df_to_markdown(subgroup_top),
        "",
        "## Notes",
        "",
        "- `renewal_due_rate` remains omitted because the staged CMS updated-renewal files do not expose a clean shared denominator for that rate.",
        "- Raw count variants are retained for breadth, but they remain size-loaded and are excluded from the gate choice.",
        "- `lag2` is only retained where support remains large enough.",
    ]
    DIAGNOSTICS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    stack, audit = load_inputs()
    retained_families = (
        audit.loc[audit["retain_for_round2"] == True, "feature_family"].drop_duplicates().sort_values().tolist()
    )

    cell = build_state_month_cells(stack)
    cell.to_csv(STATE_MONTH_CELL_CSV, index=False)

    timing_long = build_timing_matrix(cell)
    timing_long.to_csv(TIMING_LONG_CSV, index=False)

    highlow_long = build_highlow_matrix(cell)
    highlow_long.to_csv(HIGHLOW_LONG_CSV, index=False)

    fals_long, fals_summary = build_falsification(stack, cell)
    fals_long.to_csv(FALSIFICATION_LONG_CSV, index=False)
    fals_summary.to_csv(FALSIFICATION_SUMMARY_CSV, index=False)

    subgroup_rates, subgroup_summary = build_subgroup_stability(stack, retained_families)
    subgroup_rates.to_csv(SUBGROUP_RATES_CSV, index=False)
    subgroup_summary.to_csv(SUBGROUP_STABILITY_CSV, index=False)

    pd.DataFrame(OMITTED_VARIANTS).to_csv(OMITTED_VARIANTS_CSV, index=False)

    ranking = build_alignment_ranking(timing_long)
    ranking.to_csv(RANKING_CSV, index=False)

    gate_summary = evaluate_gates(fals_summary, subgroup_summary, ranking)
    gate_summary.update(
        {
            "inputs": {
                "feature_stack": str(FEATURE_STACK.relative_to(PROJECT_ROOT)),
                "feature_audit_csv": str(FEATURE_AUDIT_CSV.relative_to(PROJECT_ROOT)),
            },
            "outputs": {
                "timing_long_csv": str(TIMING_LONG_CSV.relative_to(PROJECT_ROOT)),
                "highlow_long_csv": str(HIGHLOW_LONG_CSV.relative_to(PROJECT_ROOT)),
                "falsification_long_csv": str(FALSIFICATION_LONG_CSV.relative_to(PROJECT_ROOT)),
                "falsification_summary_csv": str(FALSIFICATION_SUMMARY_CSV.relative_to(PROJECT_ROOT)),
                "subgroup_rates_csv": str(SUBGROUP_RATES_CSV.relative_to(PROJECT_ROOT)),
                "subgroup_stability_csv": str(SUBGROUP_STABILITY_CSV.relative_to(PROJECT_ROOT)),
                "alignment_ranking_csv": str(RANKING_CSV.relative_to(PROJECT_ROOT)),
                "diagnostics_md": str(DIAGNOSTICS_MD.relative_to(PROJECT_ROOT)),
            },
            "retained_feature_families": retained_families,
        }
    )
    GATE_JSON.write_text(json.dumps(gate_summary, indent=2), encoding="utf-8")
    write_markdown(timing_long, highlow_long, fals_summary, subgroup_summary, gate_summary)
    print(json.dumps(gate_summary, indent=2))


if __name__ == "__main__":
    main()
