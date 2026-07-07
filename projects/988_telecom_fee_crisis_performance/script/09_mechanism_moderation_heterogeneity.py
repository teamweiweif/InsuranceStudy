from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from model_utils import fit_fe_ols
from project_utils import DATA, RESULT, append_audit, read_parquet, save_csv


OUTCOMES = ["in_state_answer_rate", "flowout_to_national_backup_rate", "average_speed_to_answer_seconds"]


def moderation_models(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel[panel["primary_analysis_sample"]].copy()
    d["active_x_low_baseline_answer"] = d["operational_treatment_active"] * d["low_baseline_answer_rate"].astype(int)
    d["active_x_high_baseline_volume"] = d["operational_treatment_active"] * d["high_baseline_volume"].astype(int)
    d["active_x_baseline_answer_centered"] = d["operational_treatment_active"] * d["baseline_answer_rate_centered"]
    d["active_x_baseline_volume_centered"] = d["operational_treatment_active"] * d["baseline_volume_centered"]

    specs = [
        ("baseline_answer_binary", ["operational_treatment_active", "active_x_low_baseline_answer"]),
        ("baseline_volume_binary", ["operational_treatment_active", "active_x_high_baseline_volume"]),
        ("baseline_answer_continuous", ["operational_treatment_active", "active_x_baseline_answer_centered"]),
        ("baseline_volume_continuous", ["operational_treatment_active", "active_x_baseline_volume_centered"]),
    ]
    rows = []
    for outcome in OUTCOMES:
        for name, terms in specs:
            res = fit_fe_ols(d, outcome, terms, ["state", "month_id"], "state", f"heterogeneity_{name}")
            rows.append(res.table[res.table["term"].isin(terms)])
    return pd.concat(rows, ignore_index=True)


def mechanism_dose_models(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel[panel["primary_analysis_sample"] & panel["year"].between(2021, 2024)].copy()
    d["fee_revenue_per_capita_observed"] = d["fee_revenue_nominal_for_2021_2024"] / d["population"]
    d["fee_revenue_per_capita_observed"] = d["fee_revenue_per_capita_observed"].fillna(0)
    d["active_x_revenue_per_capita"] = d["operational_treatment_active"] * d["fee_revenue_per_capita_observed"]
    rows = []
    for outcome in OUTCOMES:
        res = fit_fe_ols(
            d,
            outcome,
            ["operational_treatment_active", "active_x_revenue_per_capita"],
            ["state", "month_id"],
            "state",
            "mechanism_revenue_intensity",
        )
        rows.append(res.table[res.table["term"].isin(["operational_treatment_active", "active_x_revenue_per_capita"])])
    return pd.concat(rows, ignore_index=True)


def mechanism_chain_table(panel: pd.DataFrame) -> pd.DataFrame:
    treated = (
        panel[panel["ever_core_fee_collection"] & panel["actual_collection_start"].notna()]
        .drop_duplicates("state")[["state", "state_name", "actual_collection_start", "operational_start", "primary_policy_group"]]
        .copy()
    )
    rows = []
    for row in treated.itertuples(index=False):
        state_panel = panel[panel["state"].eq(row.state)].copy()
        pre = state_panel[state_panel["month"].lt(row.operational_start)]
        post = state_panel[state_panel["month"].ge(row.operational_start)]
        rev = (
            state_panel[["year", "fee_revenue_nominal", "fee_revenue_per_capita"]]
            .dropna(subset=["fee_revenue_nominal"])
            .drop_duplicates()
        )
        rows.append(
            {
                "state": row.state,
                "state_name": row.state_name,
                "primary_policy_group": row.primary_policy_group,
                "actual_collection_start": row.actual_collection_start,
                "operational_start": row.operational_start,
                "observed_fee_revenue_total_2021_2024": rev["fee_revenue_nominal"].sum(),
                "max_observed_fee_revenue_per_capita": rev["fee_revenue_per_capita"].max(),
                "pre_answer_rate": pre["in_state_answer_rate"].mean(),
                "post_answer_rate": post["in_state_answer_rate"].mean(),
                "delta_answer_rate": post["in_state_answer_rate"].mean() - pre["in_state_answer_rate"].mean(),
                "pre_flowout_rate": pre["flowout_to_national_backup_rate"].mean(),
                "post_flowout_rate": post["flowout_to_national_backup_rate"].mean(),
                "delta_flowout_rate": post["flowout_to_national_backup_rate"].mean() - pre["flowout_to_national_backup_rate"].mean(),
                "pre_asa_seconds": pre["average_speed_to_answer_seconds"].mean(),
                "post_asa_seconds": post["average_speed_to_answer_seconds"].mean(),
                "delta_asa_seconds": post["average_speed_to_answer_seconds"].mean() - pre["average_speed_to_answer_seconds"].mean(),
            }
        )
    out = pd.DataFrame(rows)
    return out


def plot_mechanism(chain: pd.DataFrame) -> None:
    work = chain[chain["observed_fee_revenue_total_2021_2024"].gt(0)].copy()
    if work.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=work,
        x="max_observed_fee_revenue_per_capita",
        y="delta_answer_rate",
        hue="state",
        s=80,
        ax=ax,
    )
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("Fee Revenue Intensity and Within-State Answer-Rate Change")
    ax.set_xlabel("Max observed annual fee revenue per capita")
    ax.set_ylabel("Post minus pre operational answer rate")
    ax.grid(alpha=0.25)
    fig.savefig(RESULT / "fig_mechanism_revenue_answer_change.png", dpi=220, bbox_inches="tight")
    fig.savefig(RESULT / "fig_mechanism_revenue_answer_change.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    panel = read_parquet(DATA / "analysis_panel_state_month.parquet")
    moderation = moderation_models(panel)
    dose = mechanism_dose_models(panel)
    chain = mechanism_chain_table(panel)

    save_csv(moderation, RESULT / "heterogeneity_moderation_models.csv")
    save_csv(dose, RESULT / "mechanism_revenue_intensity_models.csv")
    save_csv(chain, RESULT / "mechanism_chain_table.csv")
    plot_mechanism(chain)
    append_audit("Estimated moderation, revenue-intensity mechanism models, and mechanism-chain table.")


if __name__ == "__main__":
    main()

