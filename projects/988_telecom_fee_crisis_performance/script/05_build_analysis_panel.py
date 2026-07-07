from __future__ import annotations

import numpy as np
import pandas as pd

from project_utils import DATA, RESULT, FIPS_TO_ABBR, append_audit, read_parquet, save_csv, save_parquet


STATE_DC = set(FIPS_TO_ABBR.values()) - {"PR"}


def main() -> None:
    outcomes = read_parquet(DATA / "outcomes_988_state_month.parquet")
    fee = read_parquet(DATA / "fee_schedule_state_month.parquet")
    timing = read_parquet(DATA / "treatment_timing_state.parquet")
    cov = read_parquet(DATA / "covariates_state_month.parquet")
    mech = read_parquet(DATA / "mechanism_state_year.parquet")

    panel = outcomes.merge(fee, on=["state", "month"], how="left")
    panel = panel.merge(
        timing[
            [
                "state",
                "state_name",
                "primary_policy_group",
                "first_revenue_year",
                "fcc_confirmed_collection_by_2024",
                "date_confidence",
                "source_ids",
                "policy_note",
            ]
        ],
        on="state",
        how="left",
        suffixes=("", "_timing"),
    )
    if "state_name_timing" in panel.columns:
        panel["state_name"] = panel["state_name"].fillna(panel["state_name_timing"])
    panel = panel.drop(columns=[c for c in ["state_name_timing"] if c in panel.columns])
    panel = panel.merge(cov, on=["state", "month"], how="left", suffixes=("", "_cov"))
    panel["state_name"] = panel["state_name"].fillna(panel.get("state_name_cov"))
    panel = panel.drop(columns=[c for c in ["state_name_cov"] if c in panel.columns])
    panel["year"] = panel["month"].dt.year
    panel = panel.merge(
        mech[
            [
                "state",
                "year",
                "fee_revenue_nominal",
                "fee_revenue_nominal_for_2021_2024",
                "fee_revenue_per_capita",
                "fee_revenue_per_100k",
                "fee_revenue_per_routed_contact",
                "fee_active_months",
                "operational_active_months",
                "mechanism_observation_note",
            ]
        ],
        on=["state", "year"],
        how="left",
    )

    panel["month_id"] = panel["month"].dt.strftime("%Y-%m")
    panel["calendar_month"] = panel["month"].dt.month
    panel["post_988_launch"] = (panel["month"] >= pd.Timestamp("2022-07-01")).astype(int)
    panel["months_since_988_launch"] = (
        (panel["month"].dt.year - 2022) * 12 + panel["month"].dt.month - 7
    )
    panel["is_state_dc"] = panel["state"].isin(STATE_DC)
    panel["is_territory_or_pr"] = ~panel["is_state_dc"]
    panel["has_population_denominator"] = panel["has_population_denominator"].fillna(False)
    panel["answer_rate_pp"] = panel["in_state_answer_rate"] * 100
    panel["flowout_rate_pp"] = panel["flowout_to_national_backup_rate"] * 100
    panel["abandoned_rate_pp"] = panel["abandoned_in_state_rate"] * 100
    panel["routed_per_100k"] = panel["routed_in_state"] / panel["population"] * 100000
    panel["answered_per_100k"] = panel["answered_in_state"] / panel["population"] * 100000
    panel["log_routed_in_state"] = np.log1p(panel["routed_in_state"])
    panel["log_routed_per_100k"] = np.log1p(panel["routed_per_100k"])
    panel["asa_minutes"] = panel["average_speed_to_answer_seconds"] / 60
    panel["talk_minutes"] = panel["average_talk_time_seconds"] / 60
    panel["treated_ever_by_2024"] = panel["fcc_confirmed_collection_by_2024"].fillna(False)
    panel["ever_core_fee_collection"] = panel["ever_core_fee_collection"].fillna(False)
    panel["post2025_policy_monitor_active"] = panel["post2025_policy_monitor_active"].fillna(0).astype(int)
    panel["primary_analysis_sample"] = (
        panel["is_state_dc"]
        & panel["has_population_denominator"]
        & panel["routed_in_state"].notna()
        & panel["in_state_answer_rate"].notna()
        & panel["post2025_policy_monitor_active"].eq(0)
    )

    total_months = panel["month"].nunique()
    obs_counts = panel.groupby("state")["month"].nunique().rename("observed_month_count")
    panel = panel.merge(obs_counts, on="state", how="left")
    panel["balanced_full_window_state"] = panel["observed_month_count"].eq(total_months)

    baseline_window = panel["month"].between(pd.Timestamp("2021-07-01"), pd.Timestamp("2022-06-01"))
    baseline = (
        panel[baseline_window & panel["is_state_dc"]]
        .groupby("state", as_index=False)
        .agg(
            baseline_prelaunch_answer_rate=("in_state_answer_rate", "mean"),
            baseline_prelaunch_flowout_rate=("flowout_to_national_backup_rate", "mean"),
            baseline_prelaunch_asa_seconds=("average_speed_to_answer_seconds", "mean"),
            baseline_prelaunch_routed_per_100k=("routed_per_100k", "mean"),
            baseline_prelaunch_months=("month", "nunique"),
        )
    )
    panel = panel.merge(baseline, on="state", how="left")
    med_answer = baseline["baseline_prelaunch_answer_rate"].median()
    med_volume = baseline["baseline_prelaunch_routed_per_100k"].median()
    panel["low_baseline_answer_rate"] = panel["baseline_prelaunch_answer_rate"].le(med_answer)
    panel["high_baseline_volume"] = panel["baseline_prelaunch_routed_per_100k"].ge(med_volume)
    panel["baseline_answer_rate_centered"] = panel["baseline_prelaunch_answer_rate"] - med_answer
    panel["baseline_volume_centered"] = panel["baseline_prelaunch_routed_per_100k"] - med_volume

    save_parquet(panel, DATA / "analysis_panel_state_month.parquet")
    save_csv(panel, DATA / "analysis_panel_state_month.csv")

    summary = pd.DataFrame(
        [
            {"metric": "rows", "value": len(panel)},
            {"metric": "states_or_jurisdictions", "value": panel["state"].nunique()},
            {"metric": "months", "value": total_months},
            {"metric": "primary_sample_rows", "value": int(panel["primary_analysis_sample"].sum())},
            {"metric": "primary_sample_states", "value": panel.loc[panel["primary_analysis_sample"], "state"].nunique()},
            {"metric": "fcc_confirmed_fee_states_by_2024", "value": int(timing["fcc_confirmed_collection_by_2024"].sum())},
            {"metric": "earliest_month", "value": str(panel["month"].min().date())},
            {"metric": "latest_month", "value": str(panel["month"].max().date())},
        ]
    )
    save_csv(summary, RESULT / "analysis_panel_summary.csv")
    append_audit(
        f"Built analysis panel with {len(panel)} rows; primary state/DC sample has "
        f"{int(panel['primary_analysis_sample'].sum())} rows."
    )


if __name__ == "__main__":
    main()
