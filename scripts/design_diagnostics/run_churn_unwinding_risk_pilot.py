from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_STACK = OUTPUT_DIR / "sipp_unwinding_feature_stack_2021_2023.parquet"
GATE_JSON = OUTPUT_DIR / "second_round_gate_summary.json"
FEATURE_AUDIT_CSV = OUTPUT_DIR / "sipp_subgroup_candidate_audit.csv"

METRICS_CSV = OUTPUT_DIR / "risk_prediction_pilot_metrics.csv"
DECILES_CSV = OUTPUT_DIR / "risk_prediction_pilot_calibration_by_decile.csv"
GROUP_CAL_CSV = OUTPUT_DIR / "risk_prediction_pilot_group_calibration.csv"
SUMMARY_JSON = OUTPUT_DIR / "risk_prediction_pilot_summary.json"
PILOT_MD = OUTPUT_DIR / "risk_prediction_pilot.md"

CORE_MONTHS = [8, 9, 10, 11]
OUTCOMES = ["medicaid_exit_next", "medicaid_exit_to_uninsured_next"]
FEATURE_COLS = [
    "age_band",
    "female_group",
    "household_child_group",
    "pov_band",
    "snap_group",
    "foreign_born_group",
    "noncitizen_group",
]
PRIMARY_GROUPS = ["age_band", "pov_band", "snap_group"]


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


def load_inputs() -> tuple[pd.DataFrame, dict, list[str]]:
    stack = pd.read_parquet(FEATURE_STACK)
    gate = json.loads(GATE_JSON.read_text(encoding="utf-8"))
    audit = pd.read_csv(FEATURE_AUDIT_CSV)
    retained = (
        audit.loc[audit["retain_for_round2"] == True, "feature_family"].drop_duplicates().sort_values().tolist()
    )
    return stack, gate, retained


def build_model_frame(stack: pd.DataFrame) -> pd.DataFrame:
    df = stack.loc[
        stack["reference_year"].isin([2021, 2022, 2023])
        & stack["MONTHCODE"].isin(CORE_MONTHS)
        & (stack["eligible_medicaid_transition"] == True)
    ].copy()
    for col in FEATURE_COLS:
        df[col] = df[col].astype("string").fillna("missing")
    df["state_baseline_key"] = df["tehc_st_fips"].astype("string")
    return df


def add_state_baseline_scores(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    train = df.loc[df["reference_year"].isin([2021, 2022])].copy()
    test = df.loc[df["reference_year"] == 2023].copy()
    baseline = (
        train.groupby("state_baseline_key", sort=False)
        .apply(lambda g: weighted_rate(g[outcome], g["WPFINWGT"]))
        .rename("baseline_state_score")
        .reset_index()
    )
    return test.merge(baseline, on="state_baseline_key", how="left")


def build_design_matrices(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    X = pd.get_dummies(df[FEATURE_COLS], dummy_na=False, dtype=float)
    return X, df[FEATURE_COLS]


def fit_predict(train_df: pd.DataFrame, test_df: pd.DataFrame, outcome: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    y_train = train_df[outcome].astype(int)
    y_test = test_df[outcome].astype(int)
    w_train = train_df["WPFINWGT"].astype(float)
    w_test = test_df["WPFINWGT"].astype(float)

    X_train, _ = build_design_matrices(train_df)
    X_test, _ = build_design_matrices(test_df)
    X_train, X_test = X_train.align(X_test, join="outer", axis=1, fill_value=0.0)

    logistic = LogisticRegression(max_iter=2000, solver="lbfgs")
    logistic.fit(X_train, y_train, sample_weight=w_train)
    p_logit = logistic.predict_proba(X_test)[:, 1]

    tree = HistGradientBoostingClassifier(
        learning_rate=0.05,
        max_depth=4,
        max_iter=300,
        min_samples_leaf=200,
        random_state=42,
    )
    tree.fit(X_train, y_train, sample_weight=w_train)
    p_tree = tree.predict_proba(X_test)[:, 1]

    baseline_df = add_state_baseline_scores(df=pd.concat([train_df, test_df], ignore_index=True), outcome=outcome)
    preds = test_df[
        [
            "SSUID",
            "PNUM",
            "reference_year",
            "MONTHCODE",
            "WPFINWGT",
            outcome,
            *FEATURE_COLS,
        ]
    ].copy()
    preds["baseline_state_score"] = baseline_df["baseline_state_score"].to_numpy()
    preds["pred_logistic"] = p_logit
    preds["pred_tree"] = p_tree
    return preds, X_test


def score_model(y_true: pd.Series, y_score: pd.Series, weights: pd.Series) -> dict[str, float]:
    return {
        "auc": float(roc_auc_score(y_true, y_score, sample_weight=weights)),
        "pr_auc": float(average_precision_score(y_true, y_score, sample_weight=weights)),
        "brier": float(brier_score_loss(y_true, y_score, sample_weight=weights)),
    }


def top_decile_capture(y_true: pd.Series, y_score: pd.Series, weights: pd.Series) -> float:
    df = pd.DataFrame({"y": y_true, "score": y_score, "w": weights}).sort_values("score", ascending=False, kind="stable")
    total_weight = df["w"].sum()
    cutoff = 0.1 * total_weight
    df["cum_w"] = df["w"].cumsum()
    top = df.loc[df["cum_w"] <= cutoff].copy()
    total_events = float((df["y"] * df["w"]).sum())
    top_events = float((top["y"] * top["w"]).sum())
    if total_events == 0:
        return float("nan")
    return top_events / total_events


def build_decile_calibration(preds: pd.DataFrame, outcome: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model_name, col in [
        ("baseline_state", "baseline_state_score"),
        ("logistic", "pred_logistic"),
        ("tree", "pred_tree"),
    ]:
        ranked = preds[col].rank(method="first", pct=True)
        preds[f"{model_name}_decile"] = pd.qcut(ranked, q=10, labels=False) + 1
        for decile, g in preds.groupby(f"{model_name}_decile", sort=True):
            rows.append(
                {
                    "outcome": outcome,
                    "model": model_name,
                    "decile": int(decile),
                    "rows": int(len(g)),
                    "weight_sum": round(float(g["WPFINWGT"].sum()), 2),
                    "mean_pred": round(weighted_rate(g[col], g["WPFINWGT"]), 4),
                    "observed_rate": round(weighted_rate(g[outcome], g["WPFINWGT"]), 4),
                }
            )
    return pd.DataFrame(rows)


def build_group_calibration(preds: pd.DataFrame, outcome: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for group_col in PRIMARY_GROUPS:
        for group_label, g in preds.groupby(group_col, dropna=False):
            rows.append(
                {
                    "outcome": outcome,
                    "group_family": group_col,
                    "group_label": str(group_label),
                    "rows": int(len(g)),
                    "weight_sum": round(float(g["WPFINWGT"].sum()), 2),
                    "observed_rate": round(weighted_rate(g[outcome], g["WPFINWGT"]), 4),
                    "baseline_pred": round(weighted_rate(g["baseline_state_score"], g["WPFINWGT"]), 4),
                    "logistic_pred": round(weighted_rate(g["pred_logistic"], g["WPFINWGT"]), 4),
                    "tree_pred": round(weighted_rate(g["pred_tree"], g["WPFINWGT"]), 4),
                }
            )
    return pd.DataFrame(rows)


def df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def write_markdown(metrics: pd.DataFrame, deciles: pd.DataFrame, group_cal: pd.DataFrame, gate: dict) -> None:
    lines = [
        "# Churn / Unwinding Risk Prediction Pilot",
        "",
        "## Purpose",
        "",
        "This pilot was triggered because the second-round diagnostics gates all passed under the current rule set.",
        "",
        "The model is intentionally conservative:",
        "",
        "- train on `2021-2022` matched core months",
        "- test on `2023` core months",
        "- use retained person/household subgroup features only",
        "- compare against a naive `state baseline risk` score",
        "",
        f"- gate verdict at launch: `{gate['verdict']}`",
        "",
        "## Metrics",
        "",
        df_to_markdown(metrics),
        "",
        "## Calibration By Decile",
        "",
        df_to_markdown(deciles.head(24)),
        "",
        "## Major Group Calibration",
        "",
        df_to_markdown(group_cal.head(24)),
    ]
    PILOT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    stack, gate, retained = load_inputs()
    if not (gate.get("timing_gate") and gate.get("falsification_gate") and gate.get("stability_gate")):
        raise RuntimeError("Risk pilot is gated off because not all three second-round gates passed.")

    df = build_model_frame(stack)
    train_df = df.loc[df["reference_year"].isin([2021, 2022])].copy()
    test_df = df.loc[df["reference_year"] == 2023].copy()

    metric_rows: list[dict[str, object]] = []
    decile_frames: list[pd.DataFrame] = []
    group_frames: list[pd.DataFrame] = []

    for outcome in OUTCOMES:
        preds, _ = fit_predict(train_df, test_df, outcome)
        y_true = preds[outcome].astype(int)
        weights = preds["WPFINWGT"].astype(float)
        for model_name, col in [
            ("baseline_state", "baseline_state_score"),
            ("logistic", "pred_logistic"),
            ("tree", "pred_tree"),
        ]:
            scores = score_model(y_true, preds[col], weights)
            scores.update(
                {
                    "outcome": outcome,
                    "model": model_name,
                    "top_decile_capture": round(top_decile_capture(y_true, preds[col], weights), 4),
                    "rows_test": int(len(preds)),
                    "weight_sum_test": round(float(weights.sum()), 2),
                }
            )
            metric_rows.append(scores)
        decile_frames.append(build_decile_calibration(preds.copy(), outcome))
        group_frames.append(build_group_calibration(preds.copy(), outcome))

    metrics = pd.DataFrame(metric_rows)[
        ["outcome", "model", "auc", "pr_auc", "brier", "top_decile_capture", "rows_test", "weight_sum_test"]
    ]
    deciles = pd.concat(decile_frames, ignore_index=True)
    group_cal = pd.concat(group_frames, ignore_index=True)

    metrics.to_csv(METRICS_CSV, index=False)
    deciles.to_csv(DECILES_CSV, index=False)
    group_cal.to_csv(GROUP_CAL_CSV, index=False)

    summary = {
        "metrics_csv": str(METRICS_CSV.relative_to(PROJECT_ROOT)),
        "deciles_csv": str(DECILES_CSV.relative_to(PROJECT_ROOT)),
        "group_calibration_csv": str(GROUP_CAL_CSV.relative_to(PROJECT_ROOT)),
        "pilot_md": str(PILOT_MD.relative_to(PROJECT_ROOT)),
        "retained_feature_families": retained,
        "train_reference_years": [2021, 2022],
        "test_reference_year": 2023,
        "core_months": CORE_MONTHS,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(metrics, deciles, group_cal, gate)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
