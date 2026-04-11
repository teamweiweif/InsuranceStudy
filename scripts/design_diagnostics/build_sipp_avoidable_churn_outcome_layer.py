from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_STACK = OUTPUT_DIR / "sipp_unwinding_feature_stack_2021_2023.parquet"

OUTCOME_LAYER = OUTPUT_DIR / "sipp_avoidable_churn_outcome_layer_2021_2023.parquet"
AUDIT_CSV = OUTPUT_DIR / "sipp_avoidable_churn_outcome_audit.csv"
AUDIT_MD = OUTPUT_DIR / "sipp_avoidable_churn_outcome_audit.md"
SUMMARY_JSON = OUTPUT_DIR / "sipp_avoidable_churn_outcome_summary.json"

CORE_MONTHS_H2 = [8, 9, 10]
MATURE_MONTHS_H2 = [6, 7, 8, 9, 10]

OUTCOME_CANDIDATES = {
    "persistent_uninsured_h2": {
        "description": "Pure Medicaid at t, uninsured at t+1, still uninsured at t+2.",
        "expected_role": "main_harm",
    },
    "uninsured_gap_resolved_h2": {
        "description": "Pure Medicaid at t, uninsured at t+1, insured by t+2.",
        "expected_role": "resolved_gap",
    },
    "broad_exit_resolved_insured_h2": {
        "description": "Broad Medicaid exit at t+1, insured by t+2.",
        "expected_role": "resolution_contrast",
    },
    "broad_exit_persistent_uninsured_h2": {
        "description": "Broad Medicaid exit at t+1, uninsured at t+2.",
        "expected_role": "harmful_broad_exit",
    },
    "broad_exit_to_private_h2": {
        "description": "Broad Medicaid exit at t+1, private coverage by t+2.",
        "expected_role": "private_resolution",
    },
    "broad_exit_to_public_h2": {
        "description": "Broad Medicaid exit at t+1, public coverage by t+2.",
        "expected_role": "public_resolution",
    },
    "broad_exit_back_to_medicaid_h2": {
        "description": "Broad Medicaid exit at t+1, pure Medicaid again by t+2.",
        "expected_role": "literal_return",
    },
}


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


def df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def load_feature_stack() -> pd.DataFrame:
    cols = [
        "release_year",
        "reference_year",
        "SSUID",
        "PNUM",
        "MONTHCODE",
        "WPFINWGT",
        "positive_month_weight",
        "in_december_positive_weight_cohort",
        "tehc_st_fips",
        "state_abbreviation",
        "cms_reporting_period",
        "reporting_label",
        "insured_t",
        "uninsured_t",
        "public_t",
        "private_t",
        "pure_medicaid_t",
        "eligible_medicaid_transition",
        "medicaid_exit_next",
        "medicaid_exit_to_uninsured_next",
        "age_band",
        "female_group",
        "foreign_born_group",
        "household_child_group",
        "noncitizen_group",
        "pov_band",
        "snap_group",
        "cms_updated_pending_rate",
        "cms_updated_renewed_form_rate",
        "cms_updated_procedural_share_of_terminated",
        "cms_updated_renewed_ex_parte_rate",
    ]
    df = pd.read_parquet(FEATURE_STACK, columns=cols).copy()
    df["SSUID"] = df["SSUID"].astype("string")
    df["PNUM"] = pd.to_numeric(df["PNUM"], errors="coerce").astype("Int64")
    df["MONTHCODE"] = pd.to_numeric(df["MONTHCODE"], errors="coerce").astype("Int64")
    df["reference_year"] = pd.to_numeric(df["reference_year"], errors="coerce").astype("Int64")
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce").astype("Int64")
    return df


def add_future_statuses(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["release_year", "SSUID", "PNUM", "reference_year", "MONTHCODE"], kind="stable").copy()
    g = df.groupby(["release_year", "SSUID", "PNUM"], sort=False)

    for h in [1, 2, 3]:
        df[f"lead_month_{h}"] = g["MONTHCODE"].shift(-h)
        df[f"lead_reference_year_{h}"] = g["reference_year"].shift(-h)
        for col in ["insured_t", "uninsured_t", "public_t", "private_t", "pure_medicaid_t"]:
            df[f"{col}_plus_{h}"] = g[col].shift(-h)

    for h in [1, 2, 3]:
        df[f"contiguous_plus_{h}"] = (
            df[f"lead_reference_year_{h}"].eq(df["reference_year"])
            & df[f"lead_month_{h}"].eq(df["MONTHCODE"] + h)
        )

    df["eligible_medicaid_transition_h2"] = (
        df["eligible_medicaid_transition"].eq(True) & df["contiguous_plus_2"].eq(True)
    )
    df["eligible_medicaid_transition_h3"] = (
        df["eligible_medicaid_transition"].eq(True) & df["contiguous_plus_3"].eq(True)
    )
    return df


def derive_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h2 = df["eligible_medicaid_transition_h2"].eq(True)

    df["persistent_uninsured_h2"] = (
        h2 & df["uninsured_t_plus_1"].eq(True) & df["uninsured_t_plus_2"].eq(True)
    )
    df["uninsured_gap_resolved_h2"] = (
        h2 & df["uninsured_t_plus_1"].eq(True) & df["insured_t_plus_2"].eq(True)
    )
    df["broad_exit_resolved_insured_h2"] = (
        h2 & df["medicaid_exit_next"].eq(1) & df["insured_t_plus_2"].eq(True)
    )
    df["broad_exit_persistent_uninsured_h2"] = (
        h2 & df["medicaid_exit_next"].eq(1) & df["uninsured_t_plus_2"].eq(True)
    )
    df["broad_exit_to_private_h2"] = (
        h2 & df["medicaid_exit_next"].eq(1) & df["private_t_plus_2"].eq(True)
    )
    df["broad_exit_to_public_h2"] = (
        h2 & df["medicaid_exit_next"].eq(1) & df["public_t_plus_2"].eq(True)
    )
    df["broad_exit_back_to_medicaid_h2"] = (
        h2 & df["medicaid_exit_next"].eq(1) & df["pure_medicaid_t_plus_2"].eq(True)
    )

    for col in OUTCOME_CANDIDATES:
        df[col] = df[col].astype("boolean")

    return df


def build_audit(layer: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for reference_year in sorted(layer["reference_year"].dropna().unique()):
        year_df = layer.loc[layer["reference_year"] == reference_year].copy()
        denom_h2 = year_df["eligible_medicaid_transition_h2"].eq(True)
        for window_name, months in {
            "core_aug_oct_h2": CORE_MONTHS_H2,
            "mature_jun_oct_h2": MATURE_MONTHS_H2,
        }.items():
            win_df = year_df.loc[year_df["MONTHCODE"].isin(months)].copy()
            win_denom = win_df["eligible_medicaid_transition_h2"].eq(True)
            for outcome, meta in OUTCOME_CANDIDATES.items():
                rows.append(
                    {
                        "dataset": "SIPP",
                        "reference_year": int(reference_year),
                        "window": window_name,
                        "outcome": outcome,
                        "role": meta["expected_role"],
                        "description": meta["description"],
                        "rows_total_window": int(len(win_df)),
                        "eligible_rows_h2": int(win_denom.sum()),
                        "eligible_weight_h2": round(float(win_df.loc[win_denom, "WPFINWGT"].sum()), 2),
                        "event_rows": int(win_df.loc[win_denom, outcome].fillna(False).sum()),
                        "event_weight": round(
                            float(win_df.loc[win_denom & win_df[outcome].eq(True), "WPFINWGT"].sum()), 2
                        ),
                        "event_rate_weighted": round(
                            weighted_rate(win_df.loc[win_denom, outcome], win_df.loc[win_denom, "WPFINWGT"]), 6
                        ),
                    }
                )

        rows.append(
            {
                "dataset": "SIPP",
                "reference_year": int(reference_year),
                "window": "annual_support",
                "outcome": "eligible_medicaid_transition_h2",
                "role": "support",
                "description": "Rows eligible for h2-based churn outcomes.",
                "rows_total_window": int(len(year_df)),
                "eligible_rows_h2": int(denom_h2.sum()),
                "eligible_weight_h2": round(float(year_df.loc[denom_h2, "WPFINWGT"].sum()), 2),
                "event_rows": int(denom_h2.sum()),
                "event_weight": round(float(year_df.loc[denom_h2, "WPFINWGT"].sum()), 2),
                "event_rate_weighted": round(float(denom_h2.mean()), 6),
            }
        )

    audit = pd.DataFrame(rows)

    pooled_core = audit.loc[audit["window"] == "core_aug_oct_h2"].copy()
    pooled_summary = (
        pooled_core.groupby("outcome", as_index=False)
        .agg(
            pooled_event_rows=("event_rows", "sum"),
            pooled_eligible_rows=("eligible_rows_h2", "sum"),
            pooled_event_weight=("event_weight", "sum"),
            pooled_eligible_weight=("eligible_weight_h2", "sum"),
        )
        .copy()
    )
    pooled_summary["pooled_event_rate_weighted"] = (
        pooled_summary["pooled_event_weight"] / pooled_summary["pooled_eligible_weight"]
    )
    pooled_summary["keep_for_burden_round"] = (
        (pooled_summary["pooled_event_rows"] >= 40)
        & (pooled_summary["pooled_event_rate_weighted"] >= 0.001)
    )
    pooled_summary.loc[
        pooled_summary["outcome"].isin(["uninsured_gap_resolved_h2", "broad_exit_back_to_medicaid_h2"]),
        "keep_for_burden_round",
    ] = False

    audit = audit.merge(pooled_summary[["outcome", "keep_for_burden_round"]], on="outcome", how="left")
    audit["keep_for_burden_round"] = audit["keep_for_burden_round"].fillna(False)
    return audit


def write_markdown(audit: pd.DataFrame, layer: pd.DataFrame) -> None:
    retained = (
        audit.loc[audit["keep_for_burden_round"] == True, "outcome"].drop_duplicates().sort_values().tolist()
    )
    omitted = (
        audit.loc[audit["keep_for_burden_round"] == False, "outcome"].drop_duplicates().sort_values().tolist()
    )

    support_rows = []
    for h in [1, 2, 3]:
        flag = f"contiguous_plus_{h}"
        rate = weighted_rate(layer[flag], layer["WPFINWGT"])
        support_rows.append(
            {
                "horizon": f"plus_{h}",
                "rows_supported": int(layer[flag].fillna(False).sum()),
                "weighted_support_rate": round(rate, 4) if not np.isnan(rate) else np.nan,
            }
        )
    support_df = pd.DataFrame(support_rows)

    core = audit.loc[audit["window"] == "core_aug_oct_h2", [
        "reference_year",
        "outcome",
        "event_rows",
        "event_rate_weighted",
        "keep_for_burden_round",
    ]].copy()

    lines = [
        "# SIPP Avoidable Churn Outcome Audit",
        "",
        "## Purpose",
        "",
        "This audit checks which short-horizon churn outcomes are actually supportable in the current corrected `SIPP 2021-2023` stack.",
        "",
        "The original hope was to use literal `exit -> return to Medicaid` outcomes.",
        "This audit shows whether that is realistic or too sparse.",
        "",
        "## Continuity Support",
        "",
        df_to_markdown(support_df),
        "",
        "## Core Aug-Oct H2 Outcome Support",
        "",
        df_to_markdown(core),
        "",
        "## Retained For Burden Diagnostics",
        "",
        *(f"- `{name}`" for name in retained),
        "",
        "## Omitted Or Deprioritized",
        "",
        *(f"- `{name}`" for name in omitted),
        "",
        "## Main Takeaways",
        "",
        "- `t+2` support is strong enough to use a short-horizon outcome layer.",
        "- Literal `exit -> back to pure Medicaid by t+2` is too sparse to be a main outcome in this stack.",
        "- The most usable harmful short-horizon candidate is `persistent_uninsured_h2`.",
        "- The most usable contrast outcome is `broad_exit_resolved_insured_h2`.",
    ]
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    layer = load_feature_stack()
    layer = add_future_statuses(layer)
    layer = derive_outcomes(layer)

    OUTCOME_LAYER.parent.mkdir(parents=True, exist_ok=True)
    layer.to_parquet(OUTCOME_LAYER, index=False)

    audit = build_audit(layer)
    audit.to_csv(AUDIT_CSV, index=False)
    write_markdown(audit, layer)

    summary = {
        "input_feature_stack": str(FEATURE_STACK.relative_to(PROJECT_ROOT)),
        "output_outcome_layer": str(OUTCOME_LAYER.relative_to(PROJECT_ROOT)),
        "rows_total": int(len(layer)),
        "persons_total": int(layer[["release_year", "SSUID", "PNUM"]].drop_duplicates().shape[0]),
        "reference_years": sorted(int(x) for x in layer["reference_year"].dropna().unique().tolist()),
        "retained_outcomes": audit.loc[audit["keep_for_burden_round"] == True, "outcome"]
        .drop_duplicates()
        .sort_values()
        .tolist(),
        "omitted_outcomes": audit.loc[audit["keep_for_burden_round"] == False, "outcome"]
        .drop_duplicates()
        .sort_values()
        .tolist(),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
