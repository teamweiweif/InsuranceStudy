from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model_utils import event_name, fit_fe_ols, month_diff, state_block_bootstrap
from project_utils import DATA, RESULT, append_audit, read_parquet, save_csv


OUTCOMES = [
    "in_state_answer_rate",
    "flowout_to_national_backup_rate",
    "abandoned_in_state_rate",
    "average_speed_to_answer_seconds",
    "log_routed_per_100k",
]


def weighted_mean(df: pd.DataFrame, value: str, weight: str) -> float:
    ok = df[value].notna() & df[weight].gt(0)
    if not ok.any():
        return np.nan
    return float(np.average(df.loc[ok, value], weights=df.loc[ok, weight]))


def compute_att_gt(panel: pd.DataFrame, outcome: str, timing_col: str = "operational_start") -> tuple[pd.DataFrame, pd.DataFrame]:
    d = panel[panel["primary_analysis_sample"]].copy()
    d = d[d[outcome].notna()].copy()
    d[timing_col] = pd.to_datetime(d[timing_col], errors="coerce")
    timings = d.groupby("state")[timing_col].agg(lambda s: s.iloc[0])
    months = sorted(d["month"].dropna().unique())
    pivot = d.pivot_table(index="state", columns="month", values=outcome, aggfunc="mean")

    rows = []
    treated_starts = sorted(t for t in timings.dropna().unique() if t in months)
    for g in treated_starts:
        treated_states = timings[timings.eq(g)].index.tolist()
        pre = g - pd.DateOffset(months=1)
        if pre not in pivot.columns:
            continue
        for t in months:
            t = pd.Timestamp(t)
            et = month_diff(t, g)
            if et == -1 or et < -12 or et > 30:
                continue
            control_states = timings[timings.isna() | timings.gt(t)].index.tolist()
            if not control_states:
                continue
            valid_treated = [s for s in treated_states if s in pivot.index and pd.notna(pivot.loc[s, t]) and pd.notna(pivot.loc[s, pre])]
            valid_controls = [s for s in control_states if s in pivot.index and pd.notna(pivot.loc[s, t]) and pd.notna(pivot.loc[s, pre])]
            if not valid_treated or len(valid_controls) < 5:
                continue
            treated_delta = (pivot.loc[valid_treated, t] - pivot.loc[valid_treated, pre]).mean()
            control_delta = (pivot.loc[valid_controls, t] - pivot.loc[valid_controls, pre]).mean()
            rows.append(
                {
                    "outcome": outcome,
                    "timing": timing_col,
                    "cohort_start": g,
                    "month": t,
                    "event_time": et,
                    "period": "post" if et >= 0 else "pre",
                    "att": float(treated_delta - control_delta),
                    "treated_delta": float(treated_delta),
                    "control_delta": float(control_delta),
                    "n_treated_states": len(valid_treated),
                    "n_control_states": len(valid_controls),
                }
            )

    att = pd.DataFrame(rows)
    if att.empty:
        overall = pd.DataFrame(
            [{"outcome": outcome, "timing": timing_col, "overall_att": np.nan, "pre_mean_abs_att": np.nan, "att_cells": 0}]
        )
        return att, overall
    post = att[att["event_time"].ge(0)]
    pre = att[att["event_time"].between(-12, -2)]
    overall = pd.DataFrame(
        [
            {
                "outcome": outcome,
                "timing": timing_col,
                "overall_att": weighted_mean(post, "att", "n_treated_states"),
                "pre_mean_abs_att": float(pre["att"].abs().mean()) if not pre.empty else np.nan,
                "att_cells": len(post),
                "treated_cohorts": att["cohort_start"].nunique(),
            }
        ]
    )
    return att, overall


def add_bootstrap_se(panel: pd.DataFrame, overall: pd.DataFrame, n_boot: int = 120) -> pd.DataFrame:
    rows = []
    for row in overall.itertuples(index=False):
        outcome = row.outcome

        def stat(sample: pd.DataFrame) -> float:
            _, boot_overall = compute_att_gt(sample, outcome, "operational_start")
            return boot_overall["overall_att"].iloc[0]

        boots = state_block_bootstrap(panel[panel["primary_analysis_sample"]].copy(), stat, n_boot=n_boot, seed=988)
        boots = boots[np.isfinite(boots)]
        se = float(np.std(boots, ddof=1)) if len(boots) > 2 else np.nan
        ci_low = float(np.quantile(boots, 0.025)) if len(boots) > 10 else np.nan
        ci_high = float(np.quantile(boots, 0.975)) if len(boots) > 10 else np.nan
        r = row._asdict()
        r.update({"bootstrap_se": se, "bootstrap_ci_low": ci_low, "bootstrap_ci_high": ci_high, "bootstrap_draws": len(boots)})
        rows.append(r)
    return pd.DataFrame(rows)


def fit_twfe_models(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel[panel["primary_analysis_sample"]].copy()
    rows = []
    for outcome in OUTCOMES:
        for term, model_name in [
            ("operational_treatment_active", "twfe_operational_start"),
            ("fee_collection_active", "twfe_collection_start"),
        ]:
            res = fit_fe_ols(d, outcome, [term], ["state", "month_id"], "state", model_name)
            rows.append(res.table[res.table["term"].eq(term)])
    return pd.concat(rows, ignore_index=True)


def fit_dose_response(panel: pd.DataFrame) -> pd.DataFrame:
    d = panel[panel["primary_analysis_sample"] & panel["year"].between(2021, 2024)].copy()
    d["fee_revenue_per_100k_observed"] = d["fee_revenue_nominal_for_2021_2024"] / d["population"] * 100000
    d["fee_revenue_per_100k_observed"] = d["fee_revenue_per_100k_observed"].fillna(0)
    rows = []
    for outcome in OUTCOMES:
        for term, name in [
            ("fee_cents_max", "dose_fee_cents"),
            ("fee_revenue_per_100k_observed", "dose_revenue_per_100k_2021_2024"),
        ]:
            res = fit_fe_ols(d, outcome, [term], ["state", "month_id"], "state", name)
            rows.append(res.table[res.table["term"].eq(term)])
    return pd.concat(rows, ignore_index=True)


def build_twfe_event_study(panel: pd.DataFrame, outcome: str = "in_state_answer_rate") -> pd.DataFrame:
    d = panel[panel["primary_analysis_sample"]].copy()
    d["operational_start"] = pd.to_datetime(d["operational_start"], errors="coerce")
    d["event_time_raw"] = np.nan
    valid = d["operational_start"].notna()
    d.loc[valid, "event_time_raw"] = (
        (d.loc[valid, "month"].dt.year - d.loc[valid, "operational_start"].dt.year) * 12
        + d.loc[valid, "month"].dt.month
        - d.loc[valid, "operational_start"].dt.month
    )
    event_terms = []
    for et in range(-12, 25):
        if et == -1:
            continue
        name = event_name(et)
        d[name] = (d["event_time_raw"].eq(et)).astype(int)
        event_terms.append(name)
    res = fit_fe_ols(d, outcome, event_terms, ["state", "month_id"], "state", "twfe_event_study_operational")
    out = res.table[res.table["term"].isin(event_terms)].copy()
    out["event_time"] = out["term"].map(lambda x: int(x.replace("event_m", "-").replace("event_p", "")))
    return out.sort_values("event_time")


def plot_twfe_event(event: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    event = event.sort_values("event_time")
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(-1, color="0.5", linestyle="--", linewidth=1)
    ax.errorbar(
        event["event_time"],
        event["estimate"],
        yerr=1.96 * event["std_error_cluster"],
        fmt="o",
        color="#1f77b4",
        ecolor="#9ecae1",
        capsize=2,
    )
    ax.set_title("TWFE Event Study: In-State Answer Rate")
    ax.set_xlabel("Months relative to operational treatment start")
    ax.set_ylabel("Coefficient")
    ax.grid(alpha=0.25)
    fig.savefig(RESULT / "fig_event_study_answer_rate_twfe.png", dpi=220, bbox_inches="tight")
    fig.savefig(RESULT / "fig_event_study_answer_rate_twfe.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_cs_event(att: pd.DataFrame) -> None:
    work = att[att["outcome"].eq("in_state_answer_rate")].copy()
    if work.empty:
        return
    agg = (
        work.groupby("event_time", as_index=False)
        .apply(lambda g: pd.Series({"att": weighted_mean(g, "att", "n_treated_states"), "cells": len(g)}), include_groups=False)
        .reset_index(drop=True)
    )
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(-1, color="0.5", linestyle="--", linewidth=1)
    ax.plot(agg["event_time"], agg["att"], marker="o", linewidth=1.5, color="#2ca02c")
    ax.set_title("Not-Yet-Treated Event-Time ATT: In-State Answer Rate")
    ax.set_xlabel("Months relative to operational treatment start")
    ax.set_ylabel("ATT")
    ax.grid(alpha=0.25)
    fig.savefig(RESULT / "fig_cs_event_study_answer_rate.png", dpi=220, bbox_inches="tight")
    fig.savefig(RESULT / "fig_cs_event_study_answer_rate.pdf", bbox_inches="tight")
    plt.close(fig)
    save_csv(agg, RESULT / "cs_event_study_answer_rate.csv")


def main() -> None:
    panel = read_parquet(DATA / "analysis_panel_state_month.parquet")

    twfe = fit_twfe_models(panel)
    save_csv(twfe, RESULT / "main_twfe_models.csv")

    dose = fit_dose_response(panel)
    save_csv(dose, RESULT / "dose_response_models.csv")

    att_rows = []
    overall_rows = []
    for outcome in OUTCOMES:
        att, overall = compute_att_gt(panel, outcome, "operational_start")
        att_rows.append(att)
        overall_rows.append(overall)
    att_all = pd.concat(att_rows, ignore_index=True)
    overall = pd.concat(overall_rows, ignore_index=True)
    overall = add_bootstrap_se(panel, overall)
    save_csv(att_all, RESULT / "cs_att_gt.csv")
    save_csv(overall, RESULT / "cs_overall_att.csv")

    event = build_twfe_event_study(panel)
    save_csv(event, RESULT / "event_study_twfe_coefficients.csv")
    plot_twfe_event(event)
    plot_cs_event(att_all)

    append_audit("Estimated main DID, event-study, not-yet-treated ATT, and dose-response models.")


if __name__ == "__main__":
    main()

