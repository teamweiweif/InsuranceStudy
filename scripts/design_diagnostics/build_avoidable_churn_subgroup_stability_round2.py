from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTCOME_LAYER = OUTPUT_DIR / "sipp_avoidable_churn_outcome_layer_2021_2023.parquet"
OLD_STABILITY_CSV = OUTPUT_DIR / "second_round_subgroup_stability_summary.csv"

REPORT_MD = OUTPUT_DIR / "avoidable_churn_subgroup_stability_round2.md"
SUMMARY_CSV = OUTPUT_DIR / "avoidable_churn_subgroup_stability_round2_summary.csv"
ORDERING_CSV = OUTPUT_DIR / "avoidable_churn_subgroup_ordering_tables.csv"
SUMMARY_JSON = OUTPUT_DIR / "avoidable_churn_subgroup_stability_round2_summary.json"

SUBGROUPS = [
    "age_band",
    "female_group",
    "foreign_born_group",
    "household_child_group",
    "noncitizen_group",
    "pov_band",
    "snap_group",
]

OUTCOMES = {
    "persistent_uninsured_h2": {
        "role": "primary_harm",
        "eligible_flag": "eligible_medicaid_transition_h2",
        "description": "Pure Medicaid at t, uninsured at both t+1 and t+2.",
    },
    "broad_exit_persistent_uninsured_h2": {
        "role": "primary_harm",
        "eligible_flag": "eligible_medicaid_transition_h2",
        "description": "Broad Medicaid exit at t+1, uninsured at t+2.",
    },
    "broad_exit_resolved_insured_h2": {
        "role": "contrast_resolution",
        "eligible_flag": "eligible_medicaid_transition_h2",
        "description": "Broad Medicaid exit at t+1, insured again by t+2.",
    },
    "medicaid_exit_to_uninsured_next": {
        "role": "benchmark_harm",
        "eligible_flag": "eligible_medicaid_transition",
        "description": "Pure Medicaid at t, uninsured at t+1.",
    },
}

WINDOWS = {
    "core_aug_oct_2023": {
        "months": [8, 9, 10],
        "role": "primary",
        "description": "Core h2-compatible unwinding window.",
    },
    "mature_jun_oct_2023": {
        "months": [6, 7, 8, 9, 10],
        "role": "sensitivity",
        "description": "Longer mature window used as a sensitivity check.",
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


def simple_spearman(x: pd.Series, y: pd.Series) -> float:
    xy = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(xy) < 2:
        return float("nan")
    xr = xy["x"].rank(method="average")
    yr = xy["y"].rank(method="average")
    if xr.nunique() < 2 or yr.nunique() < 2:
        return float("nan")
    return float(np.corrcoef(xr, yr)[0, 1])


def rnd(x: float, digits: int = 4) -> float:
    return round(float(x), digits) if x == x else np.nan


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "No rows available."
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        out.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(out)


def load_layer() -> pd.DataFrame:
    cols = [
        "reference_year",
        "MONTHCODE",
        "WPFINWGT",
        "eligible_medicaid_transition",
        "eligible_medicaid_transition_h2",
        "medicaid_exit_to_uninsured_next",
        "persistent_uninsured_h2",
        "broad_exit_persistent_uninsured_h2",
        "broad_exit_resolved_insured_h2",
        *SUBGROUPS,
    ]
    df = pd.read_parquet(OUTCOME_LAYER, columns=cols).copy()
    df["reference_year"] = pd.to_numeric(df["reference_year"], errors="coerce").astype("Int64")
    df["MONTHCODE"] = pd.to_numeric(df["MONTHCODE"], errors="coerce").astype("Int64")
    return df


def group_rates_for_period(
    df: pd.DataFrame,
    subgroup: str,
    outcome: str,
    eligible_flag: str,
    years: list[int],
    months: list[int],
) -> pd.DataFrame:
    subset = df.loc[
        df["reference_year"].isin(years)
        & df["MONTHCODE"].isin(months)
        & df[eligible_flag].eq(True)
        & df[subgroup].notna()
        & df["WPFINWGT"].notna()
        & (df["WPFINWGT"] > 0)
    ].copy()
    rows: list[dict[str, object]] = []
    for group_label, g in subset.groupby(subgroup, dropna=False, sort=True):
        rows.append(
            {
                "group_label": str(group_label),
                "rows": int(len(g)),
                "weight_sum": float(g["WPFINWGT"].sum()),
                "event_rate": weighted_rate(g[outcome], g["WPFINWGT"]),
                "event_weight": float((g[outcome].astype(float) * g["WPFINWGT"]).sum()),
            }
        )
    return pd.DataFrame(rows)


def rank_desc(series: pd.Series) -> pd.Series:
    return series.rank(method="min", ascending=False).astype("Int64")


def build_ordering_tables(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for window, wmeta in WINDOWS.items():
        months = wmeta["months"]
        for subgroup in SUBGROUPS:
            for outcome, ometa in OUTCOMES.items():
                pre = group_rates_for_period(
                    df=df,
                    subgroup=subgroup,
                    outcome=outcome,
                    eligible_flag=ometa["eligible_flag"],
                    years=[2021, 2022],
                    months=months,
                ).rename(
                    columns={
                        "rows": "pre_rows",
                        "weight_sum": "pre_weight",
                        "event_rate": "pre_rate",
                        "event_weight": "pre_event_weight",
                    }
                )
                cur = group_rates_for_period(
                    df=df,
                    subgroup=subgroup,
                    outcome=outcome,
                    eligible_flag=ometa["eligible_flag"],
                    years=[2023],
                    months=months,
                ).rename(
                    columns={
                        "rows": "unwinding_rows",
                        "weight_sum": "unwinding_weight",
                        "event_rate": "unwinding_rate",
                        "event_weight": "unwinding_event_weight",
                    }
                )
                merged = pre.merge(cur, on="group_label", how="inner")
                if merged.empty:
                    continue
                merged["pre_rank_high"] = rank_desc(merged["pre_rate"])
                merged["unwinding_rank_high"] = rank_desc(merged["unwinding_rate"])
                merged["rank_delta"] = merged["unwinding_rank_high"].astype(float) - merged["pre_rank_high"].astype(float)
                merged["rate_change"] = merged["unwinding_rate"] - merged["pre_rate"]
                merged.insert(0, "window", window)
                merged.insert(1, "window_role", wmeta["role"])
                merged.insert(2, "feature_family", subgroup)
                merged.insert(3, "outcome", outcome)
                merged.insert(4, "outcome_role", ometa["role"])
                rows.append(merged)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def summarize_ordering(ordering: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    group_cols = ["window", "window_role", "feature_family", "outcome", "outcome_role"]
    for keys, g in ordering.groupby(group_cols, sort=False):
        window, window_role, feature_family, outcome, outcome_role = keys
        if len(g) < 2:
            continue
        pre_top = g.sort_values(["pre_rate", "group_label"], ascending=[False, True], kind="stable").iloc[0]
        cur_top = g.sort_values(["unwinding_rate", "group_label"], ascending=[False, True], kind="stable").iloc[0]
        spearman = simple_spearman(g["pre_rate"], g["unwinding_rate"])
        top_match = str(pre_top["group_label"]) == str(cur_top["group_label"])
        stable = bool(top_match and (spearman == spearman) and spearman >= 0.5)
        rows.append(
            {
                "window": window,
                "window_role": window_role,
                "feature_family": feature_family,
                "outcome": outcome,
                "outcome_role": outcome_role,
                "groups_compared": int(len(g)),
                "pre_top_group": str(pre_top["group_label"]),
                "unwinding_top_group": str(cur_top["group_label"]),
                "pre_top_rate": rnd(pre_top["pre_rate"], 6),
                "unwinding_top_rate": rnd(cur_top["unwinding_rate"], 6),
                "pre_unwinding_spearman": rnd(spearman, 4),
                "top_group_match": bool(top_match),
                "stable_flag": stable,
                "pre_total_weight": round(float(g["pre_weight"].sum()), 2),
                "unwinding_total_weight": round(float(g["unwinding_weight"].sum()), 2),
            }
        )
    return pd.DataFrame(rows)


def load_old_benchmark() -> pd.DataFrame:
    if not OLD_STABILITY_CSV.exists():
        return pd.DataFrame()
    old = pd.read_csv(OLD_STABILITY_CSV)
    old = old.loc[
        old["feature_family"].isin(SUBGROUPS)
        & old["outcome"].eq("medicaid_exit_to_uninsured_next")
    ].copy()
    return old


def evaluate(summary: pd.DataFrame, old: pd.DataFrame) -> dict[str, object]:
    core = summary.loc[summary["window"].eq("core_aug_oct_2023")].copy()
    mature = summary.loc[summary["window"].eq("mature_jun_oct_2023")].copy()
    harm_core = core.loc[core["outcome_role"].eq("primary_harm")].copy()
    persistent_core = core.loc[core["outcome"].eq("persistent_uninsured_h2")].copy()
    broad_core = core.loc[core["outcome"].eq("broad_exit_persistent_uninsured_h2")].copy()

    persistent_stable = set(persistent_core.loc[persistent_core["stable_flag"], "feature_family"])
    broad_stable = set(broad_core.loc[broad_core["stable_flag"], "feature_family"])
    robust_harm_stable = sorted(persistent_stable.intersection(broad_stable))
    any_harm_stable = sorted(persistent_stable.union(broad_stable))

    mature_persistent_stable = set(
        mature.loc[
            mature["outcome"].eq("persistent_uninsured_h2") & mature["stable_flag"],
            "feature_family",
        ]
    )

    old_stable = set(old.loc[old["stable_flag"].astype(bool), "feature_family"]) if not old.empty else set()
    old_mean = (
        float(pd.to_numeric(old["spearman_rank_corr"], errors="coerce").mean())
        if not old.empty
        else float("nan")
    )
    new_primary_mean = float(
        pd.to_numeric(persistent_core["pre_unwinding_spearman"], errors="coerce").mean()
    )

    improves_stable_count = len(persistent_stable) > len(old_stable)
    improves_mean_spearman = (new_primary_mean == new_primary_mean) and (
        old_mean != old_mean or new_primary_mean > old_mean
    )
    improves_relative_old = bool(improves_stable_count or improves_mean_spearman)

    repeatable_family_count = len(robust_harm_stable)
    usable_family_count = len(any_harm_stable)

    if repeatable_family_count >= 2 and improves_relative_old:
        verdict = "SUBGROUP_STABILITY_ROUND2_SUPPORTS_RISK_RANKING"
        step3_unlocked = True
    elif usable_family_count >= 2 or (len(persistent_stable) >= 2 and improves_mean_spearman):
        verdict = "SUBGROUP_STABILITY_ROUND2_MIXED_WITH_CAVEAT"
        step3_unlocked = True
    else:
        verdict = "SUBGROUP_STABILITY_ROUND2_FAILS_TO_IMPROVE"
        step3_unlocked = False

    return {
        "verdict": verdict,
        "step3_unlocked": step3_unlocked,
        "core_persistent_stable_families": sorted(persistent_stable),
        "core_broad_harm_stable_families": sorted(broad_stable),
        "core_robust_harm_stable_families": robust_harm_stable,
        "core_any_harm_stable_families": any_harm_stable,
        "mature_persistent_stable_families": sorted(mature_persistent_stable),
        "old_medicaid_exit_to_uninsured_stable_families": sorted(old_stable),
        "old_stable_family_count": len(old_stable),
        "new_persistent_stable_family_count": len(persistent_stable),
        "new_robust_harm_stable_family_count": repeatable_family_count,
        "old_mean_spearman": rnd(old_mean, 4),
        "new_persistent_mean_spearman_core": rnd(new_primary_mean, 4),
        "improves_stable_count": bool(improves_stable_count),
        "improves_mean_spearman": bool(improves_mean_spearman),
        "improves_relative_old": improves_relative_old,
    }


def build_comparison_table(summary: pd.DataFrame, old: pd.DataFrame) -> pd.DataFrame:
    core = summary.loc[summary["window"].eq("core_aug_oct_2023")].copy()
    persistent = core.loc[core["outcome"].eq("persistent_uninsured_h2")][
        ["feature_family", "pre_unwinding_spearman", "top_group_match", "stable_flag", "pre_top_group", "unwinding_top_group"]
    ].rename(
        columns={
            "pre_unwinding_spearman": "new_persistent_spearman",
            "top_group_match": "new_persistent_top_match",
            "stable_flag": "new_persistent_stable",
            "pre_top_group": "new_persistent_pre_top",
            "unwinding_top_group": "new_persistent_2023_top",
        }
    )
    broad = core.loc[core["outcome"].eq("broad_exit_persistent_uninsured_h2")][
        ["feature_family", "pre_unwinding_spearman", "top_group_match", "stable_flag", "pre_top_group", "unwinding_top_group"]
    ].rename(
        columns={
            "pre_unwinding_spearman": "new_broad_harm_spearman",
            "top_group_match": "new_broad_harm_top_match",
            "stable_flag": "new_broad_harm_stable",
            "pre_top_group": "new_broad_harm_pre_top",
            "unwinding_top_group": "new_broad_harm_2023_top",
        }
    )
    compare = persistent.merge(broad, on="feature_family", how="outer")
    if not old.empty:
        old_small = old[
            ["feature_family", "spearman_rank_corr", "top_group_match", "stable_flag", "pre_top_group", "unwinding_top_group"]
        ].rename(
            columns={
                "spearman_rank_corr": "old_exit_to_uninsured_spearman",
                "top_group_match": "old_exit_to_uninsured_top_match",
                "stable_flag": "old_exit_to_uninsured_stable",
                "pre_top_group": "old_exit_to_uninsured_pre_top",
                "unwinding_top_group": "old_exit_to_uninsured_2023_top",
            }
        )
        compare = compare.merge(old_small, on="feature_family", how="left")
    return compare.sort_values("feature_family", kind="stable").reset_index(drop=True)


def write_report(
    summary: pd.DataFrame,
    ordering: pd.DataFrame,
    comparison: pd.DataFrame,
    evaluation: dict[str, object],
) -> None:
    core = summary.loc[summary["window"].eq("core_aug_oct_2023")].copy()
    harm_core = core.loc[core["outcome_role"].eq("primary_harm")].copy()
    contrast_core = core.loc[core["outcome"].eq("broad_exit_resolved_insured_h2")].copy()
    top_harm = harm_core.sort_values(
        ["stable_flag", "pre_unwinding_spearman"], ascending=[False, False], kind="stable"
    )[
        [
            "feature_family",
            "outcome",
            "groups_compared",
            "pre_top_group",
            "unwinding_top_group",
            "pre_unwinding_spearman",
            "top_group_match",
            "stable_flag",
        ]
    ]
    contrast_table = contrast_core.sort_values(
        ["stable_flag", "pre_unwinding_spearman"], ascending=[False, False], kind="stable"
    )[
        [
            "feature_family",
            "groups_compared",
            "pre_top_group",
            "unwinding_top_group",
            "pre_unwinding_spearman",
            "top_group_match",
            "stable_flag",
        ]
    ]

    robust = evaluation["core_robust_harm_stable_families"]
    any_harm = evaluation["core_any_harm_stable_families"]
    old = evaluation["old_medicaid_exit_to_uninsured_stable_families"]

    lines = [
        "# Avoidable Churn Subgroup Stability Round 2",
        "",
        "Last updated: `2026-04-26`",
        "",
        "## Purpose",
        "",
        "This file records Step 2 from `docs/churn_unwinding_operational_plan_2026-04-11.md`.",
        "",
        "It re-tests subgroup ordering stability using the upgraded avoidable harmful churn outcomes. It remains a risk-ranking and subgroup-stability diagnostic, not DID, DML, causal forest, event-study, or causal targeting work.",
        "",
        "## Result 1: Primary Harmful Outcome Ordering",
        "",
        "### Question",
        "",
        "Do retained person/household subgroup families show repeatable high-risk ordering from the pre-period into the unwinding year when the outcome is upgraded to persistent uninsured churn?",
        "",
        "### Sample / Unit",
        "",
        "- Data: corrected `SIPP 2021-2023` avoidable-churn outcome layer.",
        "- Unit: person-month observations summarized into subgroup-period weighted rates.",
        "- Pre-period: pooled `2021-2022`.",
        "- Unwinding-year comparison: `2023`.",
        "- Primary window: `core_aug_oct_2023`.",
        "",
        "### Outcome",
        "",
        "- `persistent_uninsured_h2`: pure Medicaid at `t`, uninsured at both `t+1` and `t+2`.",
        "- `broad_exit_persistent_uninsured_h2`: broad Medicaid exit at `t+1`, uninsured at `t+2`.",
        "",
        "### Treatment / Exposure",
        "",
        "No causal treatment is estimated in this step. The diagnostic exposure is subgroup membership, used only to assess whether high-risk ordering is repeatable across periods.",
        "",
        "### Purpose",
        "",
        "The purpose is to test whether the avoidable-churn outcome upgrade creates a more stable subgroup basis for later bounded risk ranking.",
        "",
        "### Numerical Result",
        "",
        f"- stable families on `persistent_uninsured_h2`: `{', '.join(evaluation['core_persistent_stable_families']) or 'none'}`",
        f"- stable families on `broad_exit_persistent_uninsured_h2`: `{', '.join(evaluation['core_broad_harm_stable_families']) or 'none'}`",
        f"- stable on both harmful outcomes: `{', '.join(robust) or 'none'}`",
        "",
        md_table(top_harm),
        "",
        "### Interpretation",
        "",
        "The upgraded harmful outcome layer produces several repeatable subgroup orderings. Families stable on both harmful outcomes are the most defensible candidates for later risk ranking; families stable on only one harmful outcome should be treated as weaker supporting evidence.",
        "",
        "### Evaluation",
        "",
        f"- repeatable high-risk families on at least one harmful outcome: `{len(any_harm)}`",
        f"- repeatable high-risk families on both harmful outcomes: `{len(robust)}`",
        "",
        "### Caveat",
        "",
        "The event rates remain low, and subgroup ordering is descriptive. This step does not estimate causal heterogeneity or prove that administrative burden caused the subgroup differences.",
        "",
        "## Result 2: Improvement Relative To The Earlier Subgroup Round",
        "",
        "### Question",
        "",
        "Does the upgraded avoidable-churn outcome layer improve stability relative to the earlier narrower `medicaid_exit_to_uninsured_next` subgroup screen?",
        "",
        "### Sample / Unit",
        "",
        "- New comparison: `core_aug_oct_2023`, pooled pre-period `2021-2022` against `2023`.",
        "- Earlier comparison: existing second-round subgroup-stability summary for `medicaid_exit_to_uninsured_next`.",
        "",
        "### Outcome",
        "",
        "- New primary outcome: `persistent_uninsured_h2`.",
        "- Earlier benchmark outcome: `medicaid_exit_to_uninsured_next`.",
        "",
        "### Treatment / Exposure",
        "",
        "No treatment is estimated. This is a comparison of subgroup ordering stability across outcome definitions.",
        "",
        "### Purpose",
        "",
        "The purpose is to decide whether the avoidable-churn outcome upgrade strengthens the case for bounded risk-ranking work.",
        "",
        "### Numerical Result",
        "",
        f"- old stable family count on `medicaid_exit_to_uninsured_next`: `{evaluation['old_stable_family_count']}` (`{', '.join(old) or 'none'}`)",
        f"- new stable family count on `persistent_uninsured_h2`: `{evaluation['new_persistent_stable_family_count']}`",
        f"- old mean Spearman: `{evaluation['old_mean_spearman']}`",
        f"- new `persistent_uninsured_h2` mean Spearman: `{evaluation['new_persistent_mean_spearman_core']}`",
        f"- improves stable count: `{evaluation['improves_stable_count']}`",
        f"- improves mean Spearman: `{evaluation['improves_mean_spearman']}`",
        "",
        md_table(comparison),
        "",
        "### Interpretation",
        "",
        "The new outcome layer is more useful if it increases the number of stable families or improves the average pre-to-2023 rank correlation relative to the earlier narrow outcome.",
        "",
        "### Evaluation",
        "",
        f"- outcome-layer stability improvement relative to earlier round: `{evaluation['improves_relative_old']}`",
        "",
        "### Caveat",
        "",
        "This is not a perfectly matched comparison because the old round used the earlier outcome layer and its own diagnostic window. The comparison is best read as a directional check, not a formal statistical test.",
        "",
        "## Result 3: Resolution Contrast Check",
        "",
        "### Question",
        "",
        "Does the contrast outcome `broad_exit_resolved_insured_h2` show stable ordering that should change the interpretation of harmful subgroup risk?",
        "",
        "### Sample / Unit",
        "",
        "- Same `SIPP 2021-2023` subgroup-period setup.",
        "- Primary window: `core_aug_oct_2023`.",
        "",
        "### Outcome",
        "",
        "`broad_exit_resolved_insured_h2`: broad Medicaid exit at `t+1`, insured again by `t+2`.",
        "",
        "### Treatment / Exposure",
        "",
        "No causal treatment is estimated. The contrast is used to avoid mistaking all exits for harmful churn.",
        "",
        "### Purpose",
        "",
        "The purpose is to check whether groups with harmful persistent uninsured churn are simply groups with more exits of all types, including resolved insured exits.",
        "",
        "### Numerical Result",
        "",
        md_table(contrast_table),
        "",
        "### Interpretation",
        "",
        "The contrast outcome helps separate harmful persistence from resolved coverage transitions. It should be used as context for risk-ranking claims, not as a main harm endpoint.",
        "",
        "### Evaluation",
        "",
        "The contrast check is useful as a guardrail but does not by itself unlock stronger causal or targeting language.",
        "",
        "### Caveat",
        "",
        "The contrast outcome is still built from short-horizon SIPP monthly reports, so it shares the same monthly reporting and support limitations as the harmful outcomes.",
        "",
        "## Closure Test",
        "",
        f"- at least one or two subgroup families now show repeatable high-risk ordering: `{len(any_harm) >= 2}`",
        f"- the new outcome layer improves stability relative to the earlier round: `{evaluation['improves_relative_old']}`",
        f"- evidence supports a stronger but bounded risk-ranking interpretation: `{evaluation['step3_unlocked']}`",
        f"- explicit Step 2 verdict: `{evaluation['verdict']}`",
        f"- Step 3 unlocked: `{evaluation['step3_unlocked']}`",
        "",
        "## Main Caveat",
        "",
        "This remains subgroup-stability and risk-ranking evidence. It does not establish that state-month administrative burden caused the subgroup ordering, and it does not unlock DID, DML, causal forest, event-study, or causal targeting work.",
        "",
        "## Artifacts",
        "",
        "- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2_summary.csv`",
        "- `outputs/design_diagnostics/avoidable_churn_subgroup_ordering_tables.csv`",
        "- `scripts/design_diagnostics/build_avoidable_churn_subgroup_stability_round2.py`",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = load_layer()
    ordering = build_ordering_tables(df)
    summary = summarize_ordering(ordering)
    old = load_old_benchmark()
    comparison = build_comparison_table(summary, old)
    evaluation = evaluate(summary, old)

    ordering_out = ordering.copy()
    for col in [
        "pre_rate",
        "unwinding_rate",
        "rate_change",
        "pre_weight",
        "unwinding_weight",
        "pre_event_weight",
        "unwinding_event_weight",
    ]:
        if col in ordering_out:
            ordering_out[col] = pd.to_numeric(ordering_out[col], errors="coerce").round(8)
    ordering_out.to_csv(ORDERING_CSV, index=False)

    summary.to_csv(SUMMARY_CSV, index=False)
    SUMMARY_JSON.write_text(json.dumps(evaluation, indent=2), encoding="utf-8")
    write_report(summary=summary, ordering=ordering, comparison=comparison, evaluation=evaluation)
    print(json.dumps(evaluation, indent=2))


if __name__ == "__main__":
    main()
