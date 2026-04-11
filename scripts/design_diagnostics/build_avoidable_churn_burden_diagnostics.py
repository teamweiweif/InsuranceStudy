from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTCOME_LAYER = OUTPUT_DIR / "sipp_avoidable_churn_outcome_layer_2021_2023.parquet"

STATE_MONTH_CSV = OUTPUT_DIR / "avoidable_churn_state_month_cells.csv"
TIMING_CSV = OUTPUT_DIR / "avoidable_churn_burden_timing_matrix.csv"
HIGHLOW_CSV = OUTPUT_DIR / "avoidable_churn_burden_highlow_matrix.csv"
RANKING_CSV = OUTPUT_DIR / "avoidable_churn_burden_ranking.csv"
FALSIFICATION_CSV = OUTPUT_DIR / "avoidable_churn_burden_falsification_summary.csv"
SUMMARY_JSON = OUTPUT_DIR / "avoidable_churn_burden_summary.json"
DIAGNOSTICS_MD = OUTPUT_DIR / "avoidable_churn_burden_diagnostics.md"

WINDOWS = {
    "core_aug_oct_2023_h2": [8, 9, 10],
    "mature_jun_oct_2023_h2": [6, 7, 8, 9, 10],
}

OUTCOMES = {
    "medicaid_exit_to_uninsured_next": {
        "label": "legacy one-step uninsured exit",
        "outcome_direction": 1,
    },
    "persistent_uninsured_h2": {
        "label": "uninsured at t+1 and still uninsured at t+2",
        "outcome_direction": 1,
    },
    "broad_exit_resolved_insured_h2": {
        "label": "broad exit at t+1 but insured by t+2",
        "outcome_direction": -1,
    },
}

BASE_EXPOSURES = {
    "pending_rate": {
        "family": "pending_backlog_burden",
        "column": "cms_updated_pending_rate",
        "base_sign": 1,
        "kind": "single",
        "notes": "Higher pending rate should proxy heavier backlog strain.",
    },
    "renewal_form_rate": {
        "family": "manual_renewal_burden",
        "column": "cms_updated_renewed_form_rate",
        "base_sign": 1,
        "kind": "single",
        "notes": "Higher renewal-by-form rate should proxy heavier manual burden.",
    },
    "procedural_term_share": {
        "family": "procedural_termination_burden",
        "column": "cms_updated_procedural_share_of_terminated",
        "base_sign": 1,
        "kind": "single",
        "notes": "Higher procedural share should proxy stronger paperwork-driven terminations.",
    },
    "ex_parte_renewal_rate": {
        "family": "ex_parte_renewal_relief",
        "column": "cms_updated_renewed_ex_parte_rate",
        "base_sign": -1,
        "kind": "single",
        "notes": "Higher ex parte renewal should relieve administrative burden.",
    },
    "backlog_automation_index": {
        "family": "composite_burden_index",
        "column": "backlog_automation_index",
        "base_sign": 1,
        "kind": "composite",
        "notes": "Within-month composite of backlog pressure and low ex parte renewal.",
    },
    "backlog_form_index": {
        "family": "composite_burden_index",
        "column": "backlog_form_index",
        "base_sign": 1,
        "kind": "composite",
        "notes": "Within-month composite of backlog pressure and manual renewal burden.",
    },
    "full_burden_index": {
        "family": "composite_burden_index",
        "column": "full_burden_index",
        "base_sign": 1,
        "kind": "composite",
        "notes": "Within-month composite of backlog, form burden, procedural share, and low ex parte renewal.",
    },
}

ALIGNMENTS = {
    "same": 0,
    "lag1": 1,
    "lead1": -1,
    "lag2": 2,
}

MIN_MONTHLY_STATE_SUPPORT = 20
MIN_TOTAL_STATE_MONTH_SUPPORT = 100


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


def df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def mean_of_available(frame: pd.DataFrame) -> pd.Series:
    valid = frame.notna().sum(axis=1)
    total = frame.fillna(0).sum(axis=1)
    out = total / valid
    out.loc[valid == 0] = np.nan
    return out


def load_layer() -> pd.DataFrame:
    cols = [
        "reference_year",
        "MONTHCODE",
        "tehc_st_fips",
        "state_abbreviation",
        "cms_reporting_period",
        "reporting_label",
        "WPFINWGT",
        "eligible_medicaid_transition_h2",
        "medicaid_exit_to_uninsured_next",
        "persistent_uninsured_h2",
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


def build_state_month_cells(layer: pd.DataFrame) -> pd.DataFrame:
    df = layer.loc[layer["eligible_medicaid_transition_h2"].eq(True)].copy()
    rows: list[dict[str, object]] = []
    group_cols = [
        "reference_year",
        "tehc_st_fips",
        "state_abbreviation",
        "MONTHCODE",
        "cms_reporting_period",
        "reporting_label",
    ]
    for keys, g in df.groupby(group_cols, dropna=False, sort=True):
        row = dict(zip(group_cols, keys))
        row.update(
            {
                "dataset": "SIPP",
                "eligible_rows_h2": int(len(g)),
                "eligible_weight_h2": float(g["WPFINWGT"].sum()),
            }
        )
        for outcome in OUTCOMES:
            row[outcome] = weighted_rate(g[outcome], g["WPFINWGT"])
        for variant, meta in BASE_EXPOSURES.items():
            if meta["kind"] != "single":
                continue
            vals = g[meta["column"]].dropna()
            row[meta["column"]] = vals.iloc[0] if len(vals) else np.nan
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
        cell[zcol] = np.nan
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
    cell["full_burden_index"] = mean_of_available(
        pd.DataFrame(
            {
                "pending": cell["z_cms_updated_pending_rate"],
                "manual": cell["z_cms_updated_renewed_form_rate"],
                "procedural": cell["z_cms_updated_procedural_share_of_terminated"],
                "low_ex_parte": -cell["z_cms_updated_renewed_ex_parte_rate"],
            }
        )
    )

    for variant, meta in BASE_EXPOSURES.items():
        col = meta["column"]
        for alignment, shift in ALIGNMENTS.items():
            if shift == 0:
                cell[f"{variant}_{alignment}"] = cell[col]
            else:
                cell[f"{variant}_{alignment}"] = cell.groupby(
                    ["reference_year", "state_abbreviation"], sort=False
                )[col].shift(shift)

    return cell


def average_monthly_estimates(month_estimates: list[tuple[float, float]]) -> float:
    cleaned = [(est, wt) for est, wt in month_estimates if est == est and wt > 0]
    if not cleaned:
        return float("nan")
    return float(np.average([x for x, _ in cleaned], weights=[w for _, w in cleaned]))


def build_metric_matrices(cell: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cell_2023 = cell.loc[cell["reference_year"].eq(2023)].copy()
    timing_rows: list[dict[str, object]] = []
    highlow_rows: list[dict[str, object]] = []

    for window, months in WINDOWS.items():
        subset = cell_2023.loc[cell_2023["MONTHCODE"].isin(months)].copy()
        for variant, meta in BASE_EXPOSURES.items():
            for alignment in ALIGNMENTS:
                exp_col = f"{variant}_{alignment}"
                total_support_rows = 0
                total_support_weight = 0.0
                for outcome, outcome_meta in OUTCOMES.items():
                    monthly_corrs: list[tuple[float, float]] = []
                    monthly_diffs: list[tuple[float, float]] = []
                    used_months = 0
                    for month in months:
                        month_df = subset.loc[subset["MONTHCODE"].eq(month)].copy()
                        x = month_df[exp_col]
                        mask = x.notna() & month_df[outcome].notna() & month_df["eligible_weight_h2"].gt(0)
                        if int(mask.sum()) < MIN_MONTHLY_STATE_SUPPORT:
                            continue
                        used_months += 1
                        support_rows = int(mask.sum())
                        support_weight = float(month_df.loc[mask, "eligible_weight_h2"].sum())
                        total_support_rows += support_rows
                        total_support_weight += support_weight

                        corr = weighted_corr(
                            month_df.loc[mask, exp_col],
                            month_df.loc[mask, outcome],
                            month_df.loc[mask, "eligible_weight_h2"],
                        )
                        monthly_corrs.append((corr, support_weight))

                        month_valid = month_df.loc[mask].copy()
                        tertile = pd.qcut(
                            month_valid[exp_col].rank(method="first"),
                            q=3,
                            labels=["low", "mid", "high"],
                        )
                        month_valid["exposure_tertile"] = tertile.astype("string")
                        low = month_valid.loc[month_valid["exposure_tertile"].eq("low")]
                        high = month_valid.loc[month_valid["exposure_tertile"].eq("high")]
                        low_rate = weighted_rate(low[outcome], low["eligible_weight_h2"])
                        high_rate = weighted_rate(high[outcome], high["eligible_weight_h2"])
                        monthly_diffs.append((high_rate - low_rate, support_weight))

                    if total_support_rows < MIN_TOTAL_STATE_MONTH_SUPPORT or used_months == 0:
                        continue

                    expected_sign = meta["base_sign"] * outcome_meta["outcome_direction"]
                    corr_est = average_monthly_estimates(monthly_corrs)
                    diff_est = average_monthly_estimates(monthly_diffs)

                    timing_rows.append(
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
                            "months_used": used_months,
                            "estimate_or_contrast": round(corr_est, 4) if corr_est == corr_est else np.nan,
                            "direction_flag": (
                                "expected"
                                if corr_est == corr_est and np.sign(corr_est) == np.sign(expected_sign)
                                else ("zero" if corr_est == 0 else ("missing" if corr_est != corr_est else "unexpected"))
                            ),
                            "notes": meta["notes"],
                        }
                    )
                    highlow_rows.append(
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
                            "months_used": used_months,
                            "estimate_or_contrast": round(diff_est, 4) if diff_est == diff_est else np.nan,
                            "direction_flag": (
                                "expected"
                                if diff_est == diff_est and np.sign(diff_est) == np.sign(expected_sign)
                                else ("zero" if diff_est == 0 else ("missing" if diff_est != diff_est else "unexpected"))
                            ),
                            "notes": f"monthly high-minus-low tertile contrast. {meta['notes']}",
                        }
                    )

    return pd.DataFrame(timing_rows), pd.DataFrame(highlow_rows)


def build_ranking(timing: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for variant, meta in BASE_EXPOSURES.items():
        subset = timing.loc[timing["exposure_variant"].eq(variant)].copy()
        for window in WINDOWS:
            for alignment in ALIGNMENTS:
                g = subset.loc[subset["window"].eq(window) & subset["alignment"].eq(alignment)].copy()
                if g.empty:
                    continue
                signed = []
                harm_only = []
                for _, row in g.iterrows():
                    outcome_direction = OUTCOMES[row["outcome"]]["outcome_direction"]
                    base_sign = meta["base_sign"]
                    signed_val = float(row["estimate_or_contrast"]) * base_sign * outcome_direction
                    signed.append(signed_val)
                    if row["outcome"] in {"medicaid_exit_to_uninsured_next", "persistent_uninsured_h2"}:
                        harm_only.append(signed_val)
                rows.append(
                    {
                        "exposure_family": meta["family"],
                        "exposure_variant": variant,
                        "exposure_kind": meta["kind"],
                        "window": window,
                        "alignment": alignment,
                        "mean_signed_corr_all": round(float(np.nanmean(signed)), 4) if len(signed) else np.nan,
                        "mean_signed_corr_harm_only": round(float(np.nanmean(harm_only)), 4)
                        if len(harm_only)
                        else np.nan,
                        "all_expected_direction": bool((g["direction_flag"] == "expected").all()),
                        "outcomes_used": int(g["outcome"].nunique()),
                    }
                )
    ranking = pd.DataFrame(rows).sort_values(
        ["window", "mean_signed_corr_all"], ascending=[True, False], kind="stable"
    )
    return ranking.reset_index(drop=True)


def choose_candidate(ranking: pd.DataFrame) -> dict[str, object]:
    nonlead = ranking.loc[ranking["alignment"].isin(["same", "lag1"])].copy()
    candidates: list[dict[str, object]] = []
    for variant in nonlead["exposure_variant"].drop_duplicates():
        var = nonlead.loc[nonlead["exposure_variant"].eq(variant)].copy()
        core = var.loc[var["window"].eq("core_aug_oct_2023_h2")].sort_values(
            "mean_signed_corr_all", ascending=False, kind="stable"
        )
        mature = var.loc[var["window"].eq("mature_jun_oct_2023_h2")].sort_values(
            "mean_signed_corr_all", ascending=False, kind="stable"
        )
        if core.empty or mature.empty:
            continue
        best_core = core.iloc[0]
        best_mature = mature.iloc[0]
        if (
            best_core["alignment"] == best_mature["alignment"]
            and float(best_core["mean_signed_corr_all"]) > 0
            and float(best_mature["mean_signed_corr_all"]) > 0
        ):
            candidates.append(
                {
                    "exposure_family": best_core["exposure_family"],
                    "exposure_variant": variant,
                    "alignment": best_core["alignment"],
                    "core_score": float(best_core["mean_signed_corr_all"]),
                    "mature_score": float(best_mature["mean_signed_corr_all"]),
                    "score_floor": min(float(best_core["mean_signed_corr_all"]), float(best_mature["mean_signed_corr_all"])),
                }
            )

    if not candidates:
        return {"candidate_found": False}
    chosen = sorted(candidates, key=lambda x: x["score_floor"], reverse=True)[0]
    chosen["candidate_found"] = True
    return chosen


def build_falsification(cell: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    core_months = WINDOWS["core_aug_oct_2023_h2"]

    state_outcomes = []
    for reference_year in [2021, 2022, 2023]:
        year_df = cell.loc[cell["reference_year"].eq(reference_year) & cell["MONTHCODE"].isin(core_months)].copy()
        for state, g in year_df.groupby("state_abbreviation", sort=True):
            row = {
                "reference_year": reference_year,
                "state_abbreviation": state,
                "eligible_weight_h2": float(g["eligible_weight_h2"].sum()),
            }
            for outcome in OUTCOMES:
                row[outcome] = weighted_rate(g[outcome], g["eligible_weight_h2"])
            state_outcomes.append(row)
    state_outcomes_df = pd.DataFrame(state_outcomes)

    for variant, meta in BASE_EXPOSURES.items():
        for alignment in ALIGNMENTS:
            exp_col = f"{variant}_{alignment}"
            later = cell.loc[cell["reference_year"].eq(2023) & cell["MONTHCODE"].isin(core_months)].copy()
            later_state = (
                later.groupby("state_abbreviation", sort=True)
                .agg(
                    exposure_value=(exp_col, "mean"),
                    exposure_weight=("eligible_weight_h2", "sum"),
                )
                .reset_index()
            )
            later_state = later_state.loc[later_state["exposure_value"].notna()].copy()
            if len(later_state) < 20:
                continue
            later_state["later_exposure_tertile"] = pd.qcut(
                later_state["exposure_value"].rank(method="first"),
                q=3,
                labels=["low", "mid", "high"],
            ).astype("string")

            merged = state_outcomes_df.merge(
                later_state[["state_abbreviation", "later_exposure_tertile"]],
                on="state_abbreviation",
                how="inner",
            )
            for outcome, outcome_meta in OUTCOMES.items():
                year_contrasts: dict[int, float] = {}
                for reference_year in [2021, 2022, 2023]:
                    year_df = merged.loc[merged["reference_year"].eq(reference_year)].copy()
                    low = year_df.loc[year_df["later_exposure_tertile"].eq("low")]
                    high = year_df.loc[year_df["later_exposure_tertile"].eq("high")]
                    low_rate = weighted_rate(low[outcome], low["eligible_weight_h2"])
                    high_rate = weighted_rate(high[outcome], high["eligible_weight_h2"])
                    year_contrasts[reference_year] = high_rate - low_rate

                expected_sign = meta["base_sign"] * outcome_meta["outcome_direction"]
                unwinding = year_contrasts[2023]
                max_pre_abs = max(abs(year_contrasts[2021]), abs(year_contrasts[2022]))
                same_direction_big_pre = (
                    np.sign(year_contrasts[2021]) == np.sign(expected_sign)
                    and np.sign(year_contrasts[2022]) == np.sign(expected_sign)
                    and max_pre_abs >= abs(unwinding)
                )
                rows.append(
                    {
                        "exposure_family": meta["family"],
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


def build_summary(
    ranking: pd.DataFrame,
    candidate: dict[str, object],
    falsification: pd.DataFrame,
) -> dict[str, object]:
    verdict = "NO_CLEAR_UPGRADE"
    if candidate.get("candidate_found"):
        cand_fals = falsification.loc[
            (falsification["exposure_variant"].eq(candidate["exposure_variant"]))
            & (falsification["alignment"].eq(candidate["alignment"]))
            & (falsification["outcome"].eq("persistent_uninsured_h2"))
        ].copy()
        fals_pass = bool(cand_fals["falsification_pass_outcome"].all()) if not cand_fals.empty else False
        if fals_pass and candidate["score_floor"] >= 0.08:
            verdict = "PROMISING_H2_UPGRADE"
        elif candidate["score_floor"] > 0:
            verdict = "MIXED_BUT_PROMISING"

    return {
        "candidate": candidate,
        "verdict": verdict,
        "ranking_csv": str(RANKING_CSV.relative_to(PROJECT_ROOT)),
        "timing_csv": str(TIMING_CSV.relative_to(PROJECT_ROOT)),
        "highlow_csv": str(HIGHLOW_CSV.relative_to(PROJECT_ROOT)),
        "falsification_csv": str(FALSIFICATION_CSV.relative_to(PROJECT_ROOT)),
    }


def write_markdown(
    cell: pd.DataFrame,
    ranking: pd.DataFrame,
    candidate: dict[str, object],
    falsification: pd.DataFrame,
    summary: dict[str, object],
) -> None:
    top_core = ranking.loc[ranking["window"].eq("core_aug_oct_2023_h2")].head(8).copy()
    top_mature = ranking.loc[ranking["window"].eq("mature_jun_oct_2023_h2")].head(8).copy()
    fals_section = pd.DataFrame()
    if candidate.get("candidate_found"):
        fals_section = falsification.loc[
            (falsification["exposure_variant"].eq(candidate["exposure_variant"]))
            & (falsification["alignment"].eq(candidate["alignment"]))
        ].copy()

    support = (
        cell.loc[cell["reference_year"].eq(2023) & cell["MONTHCODE"].isin(WINDOWS["core_aug_oct_2023_h2"])]
        .groupby("MONTHCODE", as_index=False)
        .agg(
            state_cells=("state_abbreviation", "nunique"),
            eligible_rows_h2=("eligible_rows_h2", "sum"),
            eligible_weight_h2=("eligible_weight_h2", "sum"),
        )
    )

    lines = [
        "# Avoidable Churn Burden Diagnostics",
        "",
        "## Purpose",
        "",
        "This round tests whether short-horizon `avoidable churn` outcomes are more informative than the original one-step uninsured exit outcome.",
        "",
        "The main comparison is between:",
        "",
        "- `medicaid_exit_to_uninsured_next`",
        "- `persistent_uninsured_h2`",
        "- `broad_exit_resolved_insured_h2`",
        "",
        "and between:",
        "",
        "- single burden indicators",
        "- small composite burden indices",
        "",
        "## 2023 Core H2 Support",
        "",
        df_to_markdown(support),
        "",
        "## Top Ranking: Core Window",
        "",
        df_to_markdown(top_core),
        "",
        "## Top Ranking: Mature Window",
        "",
        df_to_markdown(top_mature),
        "",
        "## Candidate Selection",
        "",
        f"- verdict: `{summary['verdict']}`",
    ]

    if candidate.get("candidate_found"):
        lines.extend(
            [
                f"- chosen candidate: `{candidate['exposure_variant']} / {candidate['alignment']}`",
                f"- core score: `{round(candidate['core_score'], 4)}`",
                f"- mature score: `{round(candidate['mature_score'], 4)}`",
                "",
                "## Candidate Falsification Check",
                "",
                df_to_markdown(fals_section)
                if not fals_section.empty
                else "No falsification rows were available for the chosen candidate.",
            ]
        )
    else:
        lines.append("- no non-lead stable candidate was found across both windows.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- If a composite burden index stays positive on `persistent_uninsured_h2` and negative on `broad_exit_resolved_insured_h2`, that is better aligned with an avoidable-churn story than the original one-step screen.",
            "- `lead1` can still be informative, but this memo does not treat lead-driven wins as clean upgrades.",
            "- The main question is whether a same-month or lagged non-lead signal survives in both windows.",
        ]
    )
    DIAGNOSTICS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    layer = load_layer()
    cell = build_state_month_cells(layer)
    cell.to_csv(STATE_MONTH_CSV, index=False)

    timing, highlow = build_metric_matrices(cell)
    timing.to_csv(TIMING_CSV, index=False)
    highlow.to_csv(HIGHLOW_CSV, index=False)

    ranking = build_ranking(timing)
    ranking.to_csv(RANKING_CSV, index=False)

    falsification = build_falsification(cell)
    falsification.to_csv(FALSIFICATION_CSV, index=False)

    candidate = choose_candidate(ranking)
    summary = build_summary(ranking, candidate, falsification)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(cell, ranking, candidate, falsification, summary)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
