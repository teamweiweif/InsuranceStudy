from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline_utils import DATA, RESULT, append_note, fit_fe_ols, joint_wald, json_dump, save_csv


OUTCOMES = [
    "facility_per100k",
    "crisis_intervention_per100k",
    "moud_any_per100k",
    "integrated_primary_care_per100k",
    "care_coordination_case_mgmt_per100k",
    "sliding_fee_or_low_payment_per100k",
    "targeted_services_per100k",
]


def did_table(df: pd.DataFrame, label: str) -> pd.DataFrame:
    rows = []
    for y in OUTCOMES:
        if y not in df.columns:
            continue
        tab, meta = fit_fe_ols(df, y, ["treated_post_selection_2024"], ["state", "year"], cluster_col="state")
        tab["outcome"] = y
        tab["strategy"] = label
        tab["model_status"] = meta.get("status")
        tab["r2_resid"] = meta.get("r2_resid")
        rows.append(tab)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def event_study(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    work = df.copy()
    for k in [-3, -2, 0]:
        work[f"event_{k}"] = ((work["treated_state_2024"] == 1) & ((work["year"] - 2024) == k)).astype(int)
    tab, meta = fit_fe_ols(work, outcome, ["event_-3", "event_-2", "event_0"], ["state", "year"], cluster_col="state")
    tab["outcome"] = outcome
    tab["model_status"] = meta.get("status")
    pre = joint_wald(tab, ["event_-3", "event_-2"])
    tab["pretrend_wald"] = pre["wald"]
    tab["pretrend_p"] = pre["p"]
    return tab


def main() -> None:
    state = pd.read_parquet(DATA / "analysis_main_state_year.parquet")
    model = state[state["inclusion_flag_main_state_year"] == 1].copy()

    all_controls = model[(model["treated_state_2024"] == 1) | (model["eligible_all_non_original_control"] == 1)]
    planning = model[(model["treated_state_2024"] == 1) | (model["eligible_planning_control"] == 1)]
    not_yet = model[(model["treated_state_2024"] == 1) | (model["eligible_not_yet_control"] == 1)]
    did = pd.concat([
        did_table(all_controls, "all_non_original_non_2024_controls"),
        did_table(planning, "planning_grant_not_selected_controls"),
        did_table(not_yet, "not_yet_2026_controls"),
    ], ignore_index=True)
    save_csv(did, RESULT / "table_main_state_did.csv")

    es_rows = []
    for y in OUTCOMES:
        if y in all_controls.columns:
            es_rows.append(event_study(all_controls, y))
    es = pd.concat(es_rows, ignore_index=True)
    save_csv(es, RESULT / "table_event_study_state.csv")

    svc = pd.read_parquet(DATA / "service_category_state_year.parquet")
    svc = svc[svc["inclusion_flag_main_state_year"] == 1].dropna(subset=["service_per100k"])
    ddd, ddd_meta = fit_fe_ols(
        svc,
        "service_per100k",
        ["treated_post_targeted"],
        ["state_service", "year_service"],
        cluster_col="state",
    )
    ddd["model"] = "DDD: selected x post x directly targeted service"
    ddd["model_status"] = ddd_meta.get("status")
    save_csv(ddd, RESULT / "table_ddd_service_category.csv")

    placebo = did_table(all_controls, "placebo_outcome_sign_language")
    placebo = placebo[placebo["outcome"] == "sign_language_per100k"] if "outcome" in placebo else pd.DataFrame()
    if placebo.empty and "sign_language_per100k" in all_controls.columns:
        tab, meta = fit_fe_ols(all_controls, "sign_language_per100k", ["treated_post_selection_2024"], ["state", "year"], cluster_col="state")
        tab["outcome"] = "sign_language_per100k"
        tab["strategy"] = "placebo_outcome_sign_language"
        tab["model_status"] = meta.get("status")
        placebo = tab
    save_csv(placebo, RESULT / "table_placebo_outcome.csv")

    pre = all_controls[all_controls["year"].between(2021, 2023)].copy()
    pre["fake_post_2023"] = (pre["year"] >= 2023).astype(int)
    pre["fake_treated_post_2023"] = pre["treated_state_2024"] * pre["fake_post_2023"]
    placebo_year_rows = []
    for y in ["facility_per100k", "targeted_services_per100k", "crisis_intervention_per100k"]:
        tab, meta = fit_fe_ols(pre, y, ["fake_treated_post_2023"], ["state", "year"], cluster_col="state")
        tab["outcome"] = y
        tab["model_status"] = meta.get("status")
        placebo_year_rows.append(tab)
    save_csv(pd.concat(placebo_year_rows, ignore_index=True), RESULT / "table_placebo_year_2023.csv")

    loo_rows = []
    treated_states = sorted(all_controls.loc[all_controls["treated_state_2024"] == 1, "state"].unique())
    for dropped in treated_states:
        tmp = all_controls[all_controls["state"] != dropped]
        tab, meta = fit_fe_ols(tmp, "targeted_services_per100k", ["treated_post_selection_2024"], ["state", "year"], cluster_col="state")
        tab["dropped_treated_state"] = dropped
        tab["model_status"] = meta.get("status")
        loo_rows.append(tab)
    save_csv(pd.concat(loo_rows, ignore_index=True), RESULT / "table_leave_one_treated_out.csv")

    base = all_controls[all_controls["year"].between(2021, 2023)].groupby("state", as_index=False).agg(
        baseline_capacity=("facility_per100k", "mean"),
        baseline_poverty=("poverty_rate", "mean"),
    )
    base["low_baseline_capacity"] = (base["baseline_capacity"] <= base["baseline_capacity"].median()).astype(int)
    het = all_controls.merge(base[["state", "low_baseline_capacity", "baseline_poverty"]], on="state", how="left")
    het["treated_post_x_low_capacity"] = het["treated_post_selection_2024"] * het["low_baseline_capacity"]
    ht, meta = fit_fe_ols(
        het,
        "targeted_services_per100k",
        ["treated_post_selection_2024", "treated_post_x_low_capacity"],
        ["state", "year"],
        cluster_col="state",
    )
    ht["model_status"] = meta.get("status")
    save_csv(ht, RESULT / "table_heterogeneity_low_capacity.csv")

    json_dump({
        "state_did_rows": int(len(did)),
        "event_study_rows": int(len(es)),
        "ddd_status": ddd_meta,
        "main_warning": "Only one partial post-treatment N-SUMHSS year is available; estimates are diagnostic, not publishable causal evidence.",
    }, RESULT / "model_run_summary.json")

    append_note("Phase 6: Main models", [
        "Estimated state-year DID/event-study models for multiple N-SUMHSS capacity outcomes.",
        "Estimated DDD service-category model comparing directly targeted services to related/weakly targeted services.",
        "Ran placebo year, placebo outcome, leave-one-treated-state-out, and low-baseline-capacity heterogeneity diagnostics.",
        "All causal estimates are early and fragile because the observed post period is only 2024 and many demonstrations start in 2025.",
    ])


if __name__ == "__main__":
    main()
