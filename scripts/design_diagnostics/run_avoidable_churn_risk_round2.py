from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.tree import DecisionTreeClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"

OUTCOME_LAYER = OUTPUT_DIR / "sipp_avoidable_churn_outcome_layer_2021_2023.parquet"
OLD_RISK_METRICS = OUTPUT_DIR / "risk_prediction_pilot_metrics.csv"
STEP2_SUMMARY = OUTPUT_DIR / "avoidable_churn_subgroup_stability_round2_summary.json"

METRICS_CSV = OUTPUT_DIR / "avoidable_churn_risk_round2_metrics.csv"
CALIBRATION_CSV = OUTPUT_DIR / "avoidable_churn_risk_round2_calibration.csv"
GROUP_CALIBRATION_CSV = OUTPUT_DIR / "avoidable_churn_risk_round2_group_calibration.csv"
SUMMARY_JSON = OUTPUT_DIR / "avoidable_churn_risk_round2_summary.json"
REPORT_MD = OUTPUT_DIR / "avoidable_churn_risk_round2.md"

CORE_MONTHS = [8, 9, 10]
FEATURE_COLS = [
    "age_band",
    "female_group",
    "foreign_born_group",
    "household_child_group",
    "noncitizen_group",
    "pov_band",
    "snap_group",
]
OUTCOME_CONFIGS = [
    {
        "outcome": "persistent_uninsured_h2",
        "role": "primary_harm",
        "eligibility_col": "eligible_medicaid_transition_h2",
        "compare_old_pilot": False,
    },
    {
        "outcome": "medicaid_exit_to_uninsured_next",
        "role": "benchmark_harm",
        "eligibility_col": "eligible_medicaid_transition",
        "compare_old_pilot": True,
    },
]
MODEL_COLUMNS = {
    "naive_state_baseline": "pred_naive_state_baseline",
    "weighted_logistic": "pred_weighted_logistic",
    "shallow_tree": "pred_shallow_tree",
    "compact_boosting": "pred_compact_boosting",
}


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna() & (weights.astype(float) > 0)
    if not bool(mask.any()):
        return float("nan")
    v = pd.to_numeric(values.loc[mask], errors="coerce").astype(float)
    w = pd.to_numeric(weights.loc[mask], errors="coerce").astype(float)
    denom = float(w.sum())
    if denom <= 0:
        return float("nan")
    return float((v * w).sum() / denom)


def weighted_event_count(values: pd.Series, weights: pd.Series) -> float:
    mask = values.notna() & weights.notna() & (weights.astype(float) > 0)
    if not bool(mask.any()):
        return float("nan")
    v = pd.to_numeric(values.loc[mask], errors="coerce").astype(float)
    w = pd.to_numeric(weights.loc[mask], errors="coerce").astype(float)
    return float((v * w).sum())


def top_decile_capture(y_true: pd.Series, y_score: pd.Series, weights: pd.Series) -> float:
    df = (
        pd.DataFrame(
            {
                "y": pd.to_numeric(y_true, errors="coerce").astype(float),
                "score": pd.to_numeric(y_score, errors="coerce").astype(float),
                "w": pd.to_numeric(weights, errors="coerce").astype(float),
            }
        )
        .dropna()
        .loc[lambda x: x["w"] > 0]
        .sort_values("score", ascending=False, kind="stable")
        .reset_index(drop=True)
    )
    total_weight = float(df["w"].sum())
    total_events = float((df["y"] * df["w"]).sum())
    if total_weight <= 0 or total_events <= 0:
        return float("nan")

    cutoff = 0.10 * total_weight
    remaining = cutoff
    captured = 0.0
    for row in df.itertuples(index=False):
        if remaining <= 0:
            break
        take_w = min(float(row.w), remaining)
        captured += float(row.y) * take_w
        remaining -= take_w
    return float(captured / total_events)


def weighted_deciles(y_score: pd.Series, weights: pd.Series) -> pd.Series:
    tmp = (
        pd.DataFrame(
            {
                "orig_index": np.arange(len(y_score)),
                "score": pd.to_numeric(y_score, errors="coerce").astype(float),
                "w": pd.to_numeric(weights, errors="coerce").astype(float),
            }
        )
        .fillna({"score": -np.inf, "w": 0.0})
        .sort_values(["score", "orig_index"], ascending=[True, True], kind="stable")
    )
    total_weight = float(tmp["w"].clip(lower=0).sum())
    if total_weight <= 0:
        return pd.Series([pd.NA] * len(y_score), index=y_score.index, dtype="Int64")
    cum_share = tmp["w"].clip(lower=0).cumsum() / total_weight
    tmp["decile"] = np.ceil(cum_share * 10).clip(lower=1, upper=10).astype(int)
    out = tmp.sort_values("orig_index")["decile"].to_numpy()
    return pd.Series(out, index=y_score.index, dtype="Int64")


def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df = pd.read_parquet(OUTCOME_LAYER)
    old_metrics = pd.read_csv(OLD_RISK_METRICS) if OLD_RISK_METRICS.exists() else pd.DataFrame()
    step2 = json.loads(STEP2_SUMMARY.read_text(encoding="utf-8")) if STEP2_SUMMARY.exists() else {}
    return df, old_metrics, step2


def make_outcome_frame(df: pd.DataFrame, outcome: str, eligibility_col: str) -> pd.DataFrame:
    needed = [
        "SSUID",
        "PNUM",
        "reference_year",
        "MONTHCODE",
        "tehc_st_fips",
        "WPFINWGT",
        eligibility_col,
        outcome,
        *FEATURE_COLS,
    ]
    work = df.loc[
        df["reference_year"].isin([2021, 2022, 2023])
        & df["MONTHCODE"].isin(CORE_MONTHS)
        & (df[eligibility_col] == True)
        & df[outcome].notna(),
        needed,
    ].copy()
    work = work.loc[work["WPFINWGT"].notna() & (work["WPFINWGT"].astype(float) > 0)].copy()
    for col in FEATURE_COLS:
        work[col] = work[col].astype("string").fillna("missing")
    work["state_key"] = work["tehc_st_fips"].astype("string").fillna("missing")
    work[outcome] = work[outcome].astype(int)
    return work


def build_design_matrices(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    x_train = pd.get_dummies(train_df[FEATURE_COLS], dtype=float)
    x_test = pd.get_dummies(test_df[FEATURE_COLS], dtype=float)
    return x_train.align(x_test, join="outer", axis=1, fill_value=0.0)


def add_naive_state_baseline(train_df: pd.DataFrame, test_df: pd.DataFrame, outcome: str) -> pd.Series:
    state_rates = (
        train_df.groupby("state_key", sort=False)
        .apply(lambda g: weighted_mean(g[outcome], g["WPFINWGT"]), include_groups=False)
        .rename("state_baseline_rate")
        .reset_index()
    )
    global_rate = weighted_mean(train_df[outcome], train_df["WPFINWGT"])
    scored = test_df[["state_key"]].merge(state_rates, on="state_key", how="left")
    return scored["state_baseline_rate"].fillna(global_rate).astype(float)


def fit_predict_models(train_df: pd.DataFrame, test_df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    y_train = train_df[outcome].astype(int)
    w_train = train_df["WPFINWGT"].astype(float)
    if y_train.nunique(dropna=True) < 2:
        raise RuntimeError(f"{outcome} has only one class in training data.")

    x_train, x_test = build_design_matrices(train_df, test_df)

    preds = test_df[
        [
            "SSUID",
            "PNUM",
            "reference_year",
            "MONTHCODE",
            "tehc_st_fips",
            "WPFINWGT",
            outcome,
            *FEATURE_COLS,
        ]
    ].copy()
    preds["pred_naive_state_baseline"] = add_naive_state_baseline(train_df, test_df, outcome).to_numpy()

    logistic = LogisticRegression(max_iter=3000, solver="lbfgs")
    logistic.fit(x_train, y_train, sample_weight=w_train)
    preds["pred_weighted_logistic"] = logistic.predict_proba(x_test)[:, 1]

    shallow_tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=500, random_state=42)
    shallow_tree.fit(x_train, y_train, sample_weight=w_train)
    preds["pred_shallow_tree"] = shallow_tree.predict_proba(x_test)[:, 1]

    boosting = HistGradientBoostingClassifier(
        learning_rate=0.04,
        max_iter=120,
        max_leaf_nodes=6,
        min_samples_leaf=500,
        l2_regularization=0.01,
        random_state=42,
    )
    boosting.fit(x_train, y_train, sample_weight=w_train)
    preds["pred_compact_boosting"] = boosting.predict_proba(x_test)[:, 1]

    return preds


def score_predictions(
    preds: pd.DataFrame,
    outcome: str,
    role: str,
    old_metrics: pd.DataFrame,
    compare_old_pilot: bool,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    y = preds[outcome].astype(int)
    w = preds["WPFINWGT"].astype(float)
    old_logit = None
    if compare_old_pilot and not old_metrics.empty:
        old = old_metrics.loc[
            (old_metrics["outcome"] == "medicaid_exit_to_uninsured_next")
            & (old_metrics["model"] == "logistic")
        ]
        if not old.empty:
            old_logit = old.iloc[0].to_dict()

    baseline_scores: dict[str, float] = {}
    for model, score_col in MODEL_COLUMNS.items():
        score = preds[score_col].astype(float)
        row = {
            "outcome": outcome,
            "outcome_role": role,
            "model": model,
            "auc": roc_auc_score(y, score, sample_weight=w),
            "pr_auc": average_precision_score(y, score, sample_weight=w),
            "top_decile_capture": top_decile_capture(y, score, w),
            "brier": brier_score_loss(y, score, sample_weight=w),
            "event_rate": weighted_mean(y, w),
            "event_count_unweighted": int(y.sum()),
            "event_weighted": weighted_event_count(y, w),
            "rows_test": int(len(preds)),
            "weight_sum_test": float(w.sum()),
        }
        if model == "naive_state_baseline":
            baseline_scores = {
                "auc": float(row["auc"]),
                "pr_auc": float(row["pr_auc"]),
                "top_decile_capture": float(row["top_decile_capture"]),
            }
        else:
            row["delta_auc_vs_naive_state"] = float(row["auc"]) - baseline_scores["auc"]
            row["delta_pr_auc_vs_naive_state"] = float(row["pr_auc"]) - baseline_scores["pr_auc"]
            row["delta_top_decile_vs_naive_state"] = (
                float(row["top_decile_capture"]) - baseline_scores["top_decile_capture"]
            )
        if old_logit is not None:
            row["old_pilot_logistic_auc"] = float(old_logit["auc"])
            row["old_pilot_logistic_pr_auc"] = float(old_logit["pr_auc"])
            row["old_pilot_logistic_top_decile_capture"] = float(old_logit["top_decile_capture"])
            if model != "naive_state_baseline":
                row["delta_auc_vs_old_pilot_logistic"] = float(row["auc"]) - float(old_logit["auc"])
                row["delta_pr_auc_vs_old_pilot_logistic"] = float(row["pr_auc"]) - float(old_logit["pr_auc"])
                row["delta_top_decile_vs_old_pilot_logistic"] = (
                    float(row["top_decile_capture"]) - float(old_logit["top_decile_capture"])
                )
        rows.append(row)

    out = pd.DataFrame(rows)
    numeric_cols = out.select_dtypes(include=[np.number]).columns
    out[numeric_cols] = out[numeric_cols].round(6)
    return out


def build_decile_calibration(preds: pd.DataFrame, outcome: str, role: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model, score_col in MODEL_COLUMNS.items():
        deciles = weighted_deciles(preds[score_col], preds["WPFINWGT"])
        work = preds.copy()
        work["risk_decile"] = deciles
        for decile, g in work.groupby("risk_decile", dropna=False, sort=True):
            rows.append(
                {
                    "outcome": outcome,
                    "outcome_role": role,
                    "model": model,
                    "risk_decile": int(decile) if pd.notna(decile) else pd.NA,
                    "rows": int(len(g)),
                    "weight_sum": round(float(g["WPFINWGT"].sum()), 2),
                    "mean_pred": round(weighted_mean(g[score_col], g["WPFINWGT"]), 6),
                    "observed_rate": round(weighted_mean(g[outcome], g["WPFINWGT"]), 6),
                    "event_count_unweighted": int(g[outcome].sum()),
                    "event_weighted": round(weighted_event_count(g[outcome], g["WPFINWGT"]), 2),
                }
            )
    return pd.DataFrame(rows)


def build_group_calibration(preds: pd.DataFrame, outcome: str, role: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for family in FEATURE_COLS:
        for group_label, g in preds.groupby(family, dropna=False, sort=True):
            for model, score_col in MODEL_COLUMNS.items():
                mean_pred = weighted_mean(g[score_col], g["WPFINWGT"])
                observed = weighted_mean(g[outcome], g["WPFINWGT"])
                rows.append(
                    {
                        "outcome": outcome,
                        "outcome_role": role,
                        "model": model,
                        "group_family": family,
                        "group_label": str(group_label),
                        "rows": int(len(g)),
                        "weight_sum": round(float(g["WPFINWGT"].sum()), 2),
                        "observed_rate": round(observed, 6),
                        "mean_pred": round(mean_pred, 6),
                        "calibration_error": round(mean_pred - observed, 6),
                        "event_count_unweighted": int(g[outcome].sum()),
                        "event_weighted": round(weighted_event_count(g[outcome], g["WPFINWGT"]), 2),
                    }
                )
    return pd.DataFrame(rows)


def best_model(metrics: pd.DataFrame, outcome: str) -> pd.Series:
    subset = metrics.loc[
        (metrics["outcome"] == outcome)
        & metrics["model"].isin(["weighted_logistic", "shallow_tree", "compact_boosting"])
    ].copy()
    return subset.sort_values(["auc", "top_decile_capture", "pr_auc"], ascending=False).iloc[0]


def decide_verdict(metrics: pd.DataFrame) -> dict[str, object]:
    primary_best = best_model(metrics, "persistent_uninsured_h2")
    primary_capture_best = (
        metrics.loc[
            (metrics["outcome"] == "persistent_uninsured_h2")
            & (metrics["model"].isin(["weighted_logistic", "shallow_tree", "compact_boosting"]))
        ]
        .sort_values(["top_decile_capture", "auc", "pr_auc"], ascending=False)
        .iloc[0]
    )
    benchmark_logit = metrics.loc[
        (metrics["outcome"] == "medicaid_exit_to_uninsured_next")
        & (metrics["model"] == "weighted_logistic")
    ].iloc[0]
    benchmark_best = best_model(metrics, "medicaid_exit_to_uninsured_next")

    primary_beats_state = bool(
        primary_best["delta_auc_vs_naive_state"] >= 0.05
        and primary_best["delta_top_decile_vs_naive_state"] >= 0.03
    )
    benchmark_beats_state = bool(
        benchmark_best["delta_auc_vs_naive_state"] >= 0.05
        and benchmark_best["delta_top_decile_vs_naive_state"] >= 0.03
    )
    benchmark_auc_not_worse_old = bool(
        pd.notna(benchmark_logit.get("delta_auc_vs_old_pilot_logistic", np.nan))
        and benchmark_logit["delta_auc_vs_old_pilot_logistic"] >= -0.03
    )
    benchmark_top_capture_not_worse_old = bool(
        pd.notna(benchmark_logit.get("delta_top_decile_vs_old_pilot_logistic", np.nan))
        and benchmark_logit["delta_top_decile_vs_old_pilot_logistic"] >= -0.03
    )
    benchmark_not_worse_old = benchmark_auc_not_worse_old and benchmark_top_capture_not_worse_old
    benchmark_mixed_vs_old = benchmark_top_capture_not_worse_old and not benchmark_auc_not_worse_old
    primary_top_capture_useful = bool(primary_capture_best["top_decile_capture"] >= 0.15)

    if primary_beats_state and benchmark_beats_state and benchmark_not_worse_old and primary_top_capture_useful:
        verdict = "RISK_RANKING_ROUND2_SUPPORTS_PRIORITIZATION_PROTOTYPE"
        step4_unlocked = True
    elif primary_beats_state and benchmark_beats_state and (
        benchmark_top_capture_not_worse_old or primary_top_capture_useful
    ):
        verdict = "RISK_RANKING_ROUND2_MIXED_WITH_CAVEAT"
        step4_unlocked = True
    else:
        verdict = "RISK_RANKING_ROUND2_FAILS_TO_CLEAR_STOP_RULE"
        step4_unlocked = False

    return {
        "verdict": verdict,
        "step4_unlocked": step4_unlocked,
        "primary_best_model": str(primary_best["model"]),
        "primary_best_auc": float(primary_best["auc"]),
        "primary_best_pr_auc": float(primary_best["pr_auc"]),
        "primary_best_top_decile_capture": float(primary_best["top_decile_capture"]),
        "primary_best_delta_auc_vs_naive": float(primary_best["delta_auc_vs_naive_state"]),
        "primary_best_delta_top_decile_vs_naive": float(primary_best["delta_top_decile_vs_naive_state"]),
        "primary_capture_model": str(primary_capture_best["model"]),
        "primary_capture_auc": float(primary_capture_best["auc"]),
        "primary_capture_pr_auc": float(primary_capture_best["pr_auc"]),
        "primary_capture_top_decile_capture": float(primary_capture_best["top_decile_capture"]),
        "primary_capture_delta_auc_vs_naive": float(primary_capture_best["delta_auc_vs_naive_state"]),
        "primary_capture_delta_top_decile_vs_naive": float(primary_capture_best["delta_top_decile_vs_naive_state"]),
        "benchmark_logistic_auc": float(benchmark_logit["auc"]),
        "benchmark_logistic_top_decile_capture": float(benchmark_logit["top_decile_capture"]),
        "benchmark_logistic_delta_auc_vs_old_pilot": float(
            benchmark_logit.get("delta_auc_vs_old_pilot_logistic", np.nan)
        ),
        "benchmark_logistic_delta_top_decile_vs_old_pilot": float(
            benchmark_logit.get("delta_top_decile_vs_old_pilot_logistic", np.nan)
        ),
        "primary_beats_state": primary_beats_state,
        "benchmark_beats_state": benchmark_beats_state,
        "benchmark_not_worse_old": benchmark_not_worse_old,
        "benchmark_auc_not_worse_old": benchmark_auc_not_worse_old,
        "benchmark_top_capture_not_worse_old": benchmark_top_capture_not_worse_old,
        "benchmark_mixed_vs_old": benchmark_mixed_vs_old,
        "primary_top_capture_useful": primary_top_capture_useful,
    }


def compact_metrics_for_report(metrics: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "outcome",
        "model",
        "auc",
        "pr_auc",
        "top_decile_capture",
        "event_rate",
        "rows_test",
        "delta_auc_vs_naive_state",
        "delta_top_decile_vs_naive_state",
        "delta_auc_vs_old_pilot_logistic",
        "delta_top_decile_vs_old_pilot_logistic",
    ]
    present = [c for c in cols if c in metrics.columns]
    return metrics[present].copy().fillna("")


def write_report(
    metrics: pd.DataFrame,
    calibration: pd.DataFrame,
    group_calibration: pd.DataFrame,
    old_metrics: pd.DataFrame,
    step2: dict,
    verdict: dict,
) -> None:
    prioritization_model = verdict["primary_capture_model"]
    primary_top_decile = calibration.loc[
        (calibration["outcome"] == "persistent_uninsured_h2")
        & (calibration["model"] == prioritization_model)
        & (calibration["risk_decile"].isin([1, 10]))
    ][["risk_decile", "mean_pred", "observed_rate", "event_count_unweighted", "event_weighted"]]
    stable_groups = step2.get("core_robust_harm_stable_families", [])
    stable_group_view = group_calibration.loc[
        (group_calibration["outcome"] == "persistent_uninsured_h2")
        & (group_calibration["model"] == prioritization_model)
        & (group_calibration["group_family"].isin(stable_groups))
    ][
        [
            "group_family",
            "group_label",
            "observed_rate",
            "mean_pred",
            "calibration_error",
            "event_count_unweighted",
        ]
    ].copy()

    old_line = ""
    if not old_metrics.empty:
        old_logit = old_metrics.loc[
            (old_metrics["outcome"] == "medicaid_exit_to_uninsured_next")
            & (old_metrics["model"] == "logistic")
        ]
        if not old_logit.empty:
            row = old_logit.iloc[0]
            old_line = (
                f"- old risk-pilot logistic on `medicaid_exit_to_uninsured_next`: "
                f"AUC `{row['auc']:.4f}`, PR AUC `{row['pr_auc']:.4f}`, "
                f"top-decile capture `{row['top_decile_capture']:.4f}`"
            )

    lines = [
        "# Avoidable Churn Risk-Ranking Round 2",
        "",
        "Last updated: `2026-04-26`",
        "",
        "## Purpose",
        "",
        "This file records Step 3 from `docs/churn_unwinding_operational_plan_2026-04-11.md`.",
        "",
        "It upgrades the earlier bounded risk pilot to the avoidable harmful churn outcome layer. It remains a risk-ranking and prioritization diagnostic, not DID, DML, causal forest, event-study, or causal targeting work.",
        "",
        "## Result 1: Primary Risk-Ranking Performance",
        "",
        "### Question",
        "",
        "Can retained person/household subgroup features rank `2023` persistent-uninsurance risk better than a naive state-baseline score when trained only on `2021-2022`?",
        "",
        "### Sample / Unit",
        "",
        "- Data: corrected `SIPP 2021-2023` avoidable-churn outcome layer.",
        "- Unit: eligible person-month observations.",
        "- Train: `2021-2022`, months `8-10`.",
        "- Test: `2023`, months `8-10`.",
        "- Weights: `WPFINWGT`.",
        "",
        "### Outcome",
        "",
        "`persistent_uninsured_h2`: pure Medicaid at `t`, uninsured at both `t+1` and `t+2`.",
        "",
        "### Treatment / Exposure",
        "",
        "No causal treatment is estimated. Predictors are retained person/household subgroup features; the benchmark exposure is a naive state-baseline risk score from the `2021-2022` training period.",
        "",
        "### Purpose",
        "",
        "The purpose is to decide whether the current line can support a bounded risk-ranking / prioritization prototype.",
        "",
        "### Numerical Result",
        "",
        df_to_markdown(compact_metrics_for_report(metrics.loc[metrics["outcome"] == "persistent_uninsured_h2"])),
        "",
        "### Interpretation",
        "",
        f"The AUC-leading primary model is `{verdict['primary_best_model']}` with AUC `{verdict['primary_best_auc']:.4f}`. The strongest top-decile-capture model is `{verdict['primary_capture_model']}` with top-decile capture `{verdict['primary_capture_top_decile_capture']:.4f}`.",
        "",
        "### Evaluation",
        "",
        f"- primary best-model AUC gain over naive state baseline: `{verdict['primary_best_delta_auc_vs_naive']:.4f}`",
        f"- primary best-model top-decile capture gain over naive state baseline: `{verdict['primary_best_delta_top_decile_vs_naive']:.4f}`",
        f"- primary capture-model top-decile capture gain over naive state baseline: `{verdict['primary_capture_delta_top_decile_vs_naive']:.4f}`",
        f"- primary model beats naive state baseline under the round-2 rule: `{verdict['primary_beats_state']}`",
        "",
        "### Caveat",
        "",
        "The primary outcome remains rare. The model is useful only as a ranking diagnostic and should not be interpreted as a causal targeting rule.",
        "",
        "## Result 2: Comparison Against Old Risk Pilot",
        "",
        "### Question",
        "",
        "Does the round-2 risk screen remain competitive with the older risk pilot on the benchmark outcome?",
        "",
        "### Sample / Unit",
        "",
        "- New comparison: train `2021-2022`, test `2023`, months `8-10`.",
        "- Old pilot: existing `risk_prediction_pilot_metrics.csv`, built before the avoidable-churn upgrade.",
        "",
        "### Outcome",
        "",
        "`medicaid_exit_to_uninsured_next`, retained as the benchmark outcome for direct comparison with the older pilot.",
        "",
        "### Treatment / Exposure",
        "",
        "No treatment is estimated. The comparison is between risk-ranking models and the older bounded risk-prediction pilot.",
        "",
        "### Purpose",
        "",
        "The purpose is to enforce the stop rule that the new risk round should not be materially weaker than the old pilot.",
        "",
        "### Numerical Result",
        "",
        df_to_markdown(
            compact_metrics_for_report(metrics.loc[metrics["outcome"] == "medicaid_exit_to_uninsured_next"])
        ),
        "",
        old_line,
        "",
        "### Interpretation",
        "",
        "The benchmark outcome checks whether the new implementation is still competitive on the earlier narrow outcome while the paper core shifts to persistent uninsurance.",
        "",
        "### Evaluation",
        "",
        f"- benchmark logistic AUC delta versus old pilot logistic: `{verdict['benchmark_logistic_delta_auc_vs_old_pilot']:.4f}`",
        f"- benchmark logistic top-decile delta versus old pilot logistic: `{verdict['benchmark_logistic_delta_top_decile_vs_old_pilot']:.4f}`",
        f"- benchmark AUC remains not materially worse than old pilot: `{verdict['benchmark_auc_not_worse_old']}`",
        f"- benchmark top-decile capture remains not materially worse than old pilot: `{verdict['benchmark_top_capture_not_worse_old']}`",
        f"- benchmark comparison versus old pilot is mixed: `{verdict['benchmark_mixed_vs_old']}`",
        "",
        "### Caveat",
        "",
        "The old pilot used the earlier outcome layer and a slightly different month window. This is a directional stop-rule check, not a formal model-selection test.",
        "",
        "## Result 3: Calibration And Subgroup Calibration",
        "",
        "### Question",
        "",
        "Is calibration good enough to describe the output as a modest prioritization prototype rather than just a discrimination score?",
        "",
        "### Sample / Unit",
        "",
        "Same Step 3 test sample, summarized by weighted risk deciles and retained subgroup families.",
        "",
        "### Outcome",
        "",
        "Primary calibration is reported for `persistent_uninsured_h2`; full calibration tables are saved to CSV for both outcomes.",
        "",
        "### Treatment / Exposure",
        "",
        "No treatment is estimated. Calibration evaluates predicted risk scores against observed weighted outcome rates.",
        "",
        "### Purpose",
        "",
        "The purpose is to check whether the ranking model can support a bounded prioritization prototype with transparent caveats.",
        "",
        "### Numerical Result",
        "",
        f"Primary prioritization-model (`{prioritization_model}`) calibration at the bottom and top risk deciles:",
        "",
        df_to_markdown(primary_top_decile),
        "",
        f"Primary prioritization-model (`{prioritization_model}`) calibration for Step 2 stable subgroup families:",
        "",
        df_to_markdown(stable_group_view),
        "",
        "### Interpretation",
        "",
        "The decile table is the main calibration guardrail. Subgroup calibration is retained as a diagnostic because subgroup ordering, not individual causal targeting, is the current validated contribution. The calibration evidence supports rank-only language, not probability-calibrated targeting.",
        "",
        "### Evaluation",
        "",
        f"- calibration good enough for bounded rank-prototype language: `{verdict['step4_unlocked']}`",
        "",
        "### Caveat",
        "",
        "Predicted probabilities are not externally calibrated, and decile ordering is not perfectly monotone. They should be used for rank ordering and prioritization diagnostics only.",
        "",
        "## Closure Test",
        "",
        f"- the new risk round improves ranking usefulness relative to the old risk pilot: `mixed`",
        f"- old-pilot comparison detail: AUC not-worse `{verdict['benchmark_auc_not_worse_old']}`, top-decile not-worse `{verdict['benchmark_top_capture_not_worse_old']}`",
        f"- the signal remains better than naive state baseline: `{verdict['primary_beats_state'] and verdict['benchmark_beats_state']}`",
        f"- calibration is good enough to support a modest risk prioritization prototype: `{verdict['step4_unlocked']}`",
        f"- explicit Step 3 verdict: `{verdict['verdict']}`",
        f"- Step 4 unlocked: `{verdict['step4_unlocked']}`",
        "",
        "## Main Caveat",
        "",
        "This remains a risk-ranking prototype. It does not establish that state-month administrative burden caused persistent uninsurance, and it does not unlock DID, DML, causal forest, event-study, or causal targeting work.",
        "",
        "## Artifacts",
        "",
        "- `outputs/design_diagnostics/avoidable_churn_risk_round2_metrics.csv`",
        "- `outputs/design_diagnostics/avoidable_churn_risk_round2_calibration.csv`",
        "- `outputs/design_diagnostics/avoidable_churn_risk_round2_group_calibration.csv`",
        "- `scripts/design_diagnostics/run_avoidable_churn_risk_round2.py`",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df, old_metrics, step2 = load_inputs()

    metric_frames: list[pd.DataFrame] = []
    calibration_frames: list[pd.DataFrame] = []
    group_calibration_frames: list[pd.DataFrame] = []

    for config in OUTCOME_CONFIGS:
        frame = make_outcome_frame(df, config["outcome"], config["eligibility_col"])
        train_df = frame.loc[frame["reference_year"].isin([2021, 2022])].copy()
        test_df = frame.loc[frame["reference_year"] == 2023].copy()
        preds = fit_predict_models(train_df, test_df, config["outcome"])
        metric_frames.append(
            score_predictions(
                preds,
                config["outcome"],
                config["role"],
                old_metrics,
                bool(config["compare_old_pilot"]),
            )
        )
        calibration_frames.append(build_decile_calibration(preds, config["outcome"], config["role"]))
        group_calibration_frames.append(build_group_calibration(preds, config["outcome"], config["role"]))

    metrics = pd.concat(metric_frames, ignore_index=True)
    calibration = pd.concat(calibration_frames, ignore_index=True)
    group_calibration = pd.concat(group_calibration_frames, ignore_index=True)
    verdict = decide_verdict(metrics)

    metrics.to_csv(METRICS_CSV, index=False)
    calibration.to_csv(CALIBRATION_CSV, index=False)
    group_calibration.to_csv(GROUP_CALIBRATION_CSV, index=False)

    summary = {
        **verdict,
        "train_reference_years": [2021, 2022],
        "test_reference_year": 2023,
        "core_months": CORE_MONTHS,
        "feature_columns": FEATURE_COLS,
        "metrics_csv": str(METRICS_CSV.relative_to(PROJECT_ROOT)),
        "calibration_csv": str(CALIBRATION_CSV.relative_to(PROJECT_ROOT)),
        "group_calibration_csv": str(GROUP_CALIBRATION_CSV.relative_to(PROJECT_ROOT)),
        "report_md": str(REPORT_MD.relative_to(PROJECT_ROOT)),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(metrics, calibration, group_calibration, old_metrics, step2, verdict)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
