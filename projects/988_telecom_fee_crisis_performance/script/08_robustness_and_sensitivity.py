from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model_utils import fit_fe_ols
from project_utils import DATA, RESULT, append_audit, read_parquet, save_csv


ROBUST_OUTCOMES = ["in_state_answer_rate", "flowout_to_national_backup_rate", "average_speed_to_answer_seconds"]


def fit_one(df: pd.DataFrame, outcome: str, term: str, spec: str) -> dict:
    res = fit_fe_ols(df, outcome, [term], ["state", "month_id"], "state", spec)
    row = res.table[res.table["term"].eq(term)].iloc[0].to_dict()
    row["states"] = df["state"].nunique()
    return row


def robustness_specs(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    main = panel[panel["primary_analysis_sample"]].copy()
    treated_states = sorted(main.loc[main["treated_ever_by_2024"], "state"].unique())
    spec_masks = {
        "main_operational": main.index == main.index,
        "drop_988_launch_transition_2022h2": ~main["month"].between(pd.Timestamp("2022-07-01"), pd.Timestamp("2022-12-01")),
        "drop_early_adopters_va_wa": ~main["state"].isin(["VA", "WA"]),
        "balanced_full_window_states": main["balanced_full_window_state"],
        "through_2024_only": main["year"].le(2024),
        "drop_2021_startup_months": main["month"].ge(pd.Timestamp("2022-01-01")),
    }
    for spec, mask in spec_masks.items():
        d = main[mask].copy()
        if d["operational_treatment_active"].nunique() < 2:
            continue
        for outcome in ROBUST_OUTCOMES:
            rows.append(fit_one(d, outcome, "operational_treatment_active", spec))

    all_state_dc = panel[
        panel["is_state_dc"] & panel["has_population_denominator"] & panel["routed_in_state"].notna()
    ].copy()
    for outcome in ROBUST_OUTCOMES:
        rows.append(fit_one(all_state_dc, outcome, "operational_treatment_active", "include_post2025_monitor_rows"))

    for state in treated_states:
        d = main[~main["state"].eq(state)].copy()
        if d["operational_treatment_active"].nunique() < 2:
            continue
        rows.append(fit_one(d, "in_state_answer_rate", "operational_treatment_active", f"leave_out_{state}"))
    return pd.DataFrame(rows)


def placebo_distribution(panel: pd.DataFrame, n_draws: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(988)
    main = panel[panel["primary_analysis_sample"]].copy()
    treated_timing = (
        main[main["treated_ever_by_2024"]]
        .drop_duplicates("state")[["state", "operational_start"]]
        .dropna()
        .sort_values("state")
    )
    starts = treated_timing["operational_start"].tolist()
    control_states = sorted(
        main.loc[
            ~main["treated_ever_by_2024"]
            & ~main["ever_core_fee_collection"]
            & main["state"].notna(),
            "state",
        ].unique()
    )
    rows = []
    for draw in range(n_draws):
        chosen = rng.choice(control_states, size=len(starts), replace=False)
        assigned = dict(zip(chosen, starts))
        d = main.copy()
        d["placebo_operational_active"] = 0
        for state, start in assigned.items():
            d.loc[d["state"].eq(state) & d["month"].ge(start), "placebo_operational_active"] = 1
        try:
            row = fit_one(d, "in_state_answer_rate", "placebo_operational_active", "placebo_operational")
            row["draw"] = draw
            row["assigned_states"] = ";".join(chosen)
            rows.append(row)
        except Exception:
            continue
    return pd.DataFrame(rows)


def plot_placebo(placebo: pd.DataFrame, actual: float) -> None:
    if placebo.empty:
        return
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.hist(placebo["estimate"], bins=24, color="#bdbdbd", edgecolor="white")
    ax.axvline(actual, color="#d62728", linewidth=2, label="Actual estimate")
    ax.axvline(0, color="black", linewidth=1)
    ax.set_title("Placebo Timing Distribution: In-State Answer Rate")
    ax.set_xlabel("Placebo TWFE coefficient")
    ax.set_ylabel("Draws")
    ax.legend()
    fig.savefig(RESULT / "fig_placebo_timing_answer_rate.png", dpi=220, bbox_inches="tight")
    fig.savefig(RESULT / "fig_placebo_timing_answer_rate.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    panel = read_parquet(DATA / "analysis_panel_state_month.parquet")
    robust = robustness_specs(panel)
    save_csv(robust, RESULT / "robustness_summary.csv")

    placebo = placebo_distribution(panel)
    save_csv(placebo, RESULT / "placebo_timing_distribution.csv")
    main_model = pd.read_csv(RESULT / "main_twfe_models.csv")
    actual = main_model[
        main_model["outcome"].eq("in_state_answer_rate")
        & main_model["model"].eq("twfe_operational_start")
    ]["estimate"].iloc[0]
    plot_placebo(placebo, actual)
    p_emp = float((placebo["estimate"].abs() >= abs(actual)).mean()) if not placebo.empty else np.nan
    pd.DataFrame(
        [
            {
                "actual_answer_rate_twfe": actual,
                "placebo_abs_p_value": p_emp,
                "placebo_draws": len(placebo),
                "interpretation_note": "Empirical p-value compares absolute placebo coefficients to the actual operational-start TWFE coefficient.",
            }
        ]
    ).to_csv(RESULT / "placebo_timing_summary.csv", index=False)

    append_audit("Estimated robustness specifications, leave-one-treated-out checks, and placebo timing distribution.")


if __name__ == "__main__":
    main()

