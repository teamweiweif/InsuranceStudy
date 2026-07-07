from __future__ import annotations

import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from pipeline_utils import COHORT_2024, COHORT_2026, DATA, RESULT, append_note, save_csv, smd


sns.set_theme(style="whitegrid")


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(RESULT / f"{name}.png", dpi=300)
    plt.savefig(RESULT / f"{name}.pdf")
    plt.close()


def cohort_tilemap(state: pd.DataFrame) -> None:
    coords = {
        "AK": (0, 0), "HI": (0, 1), "WA": (1, 0), "OR": (2, 0), "CA": (3, 0), "ID": (2, 1),
        "NV": (3, 1), "AZ": (4, 1), "MT": (1, 2), "WY": (2, 2), "UT": (3, 2), "CO": (4, 2),
        "NM": (5, 2), "ND": (1, 3), "SD": (2, 3), "NE": (3, 3), "KS": (4, 3), "OK": (5, 3),
        "TX": (6, 3), "MN": (1, 4), "IA": (2, 4), "MO": (3, 4), "AR": (4, 4), "LA": (5, 4),
        "WI": (1, 5), "IL": (2, 5), "KY": (3, 5), "TN": (4, 5), "MS": (5, 5), "AL": (6, 5),
        "MI": (1, 6), "IN": (2, 6), "OH": (3, 6), "WV": (4, 6), "GA": (5, 6), "FL": (6, 6),
        "NY": (1, 7), "PA": (2, 7), "VA": (3, 7), "NC": (4, 7), "SC": (5, 7),
        "VT": (0, 8), "NH": (1, 8), "ME": (0, 9), "MA": (2, 8), "RI": (3, 8), "CT": (4, 8),
        "NJ": (2, 9), "DE": (3, 9), "MD": (4, 9), "DC": (5, 9),
    }
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = {"2024 cohort": "#2b8cbe", "2026 cohort": "#f03b20", "other": "#d9d9d9"}
    for st, (r, c) in coords.items():
        label = "2024 cohort" if st in COHORT_2024 else ("2026 cohort" if st in COHORT_2026 else "other")
        ax.add_patch(plt.Rectangle((c, -r), 0.9, 0.9, facecolor=colors[label], edgecolor="white"))
        ax.text(c + 0.45, -r + 0.45, st, ha="center", va="center", fontsize=9, color="black")
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-7.5, 1.2)
    ax.axis("off")
    handles = [plt.Rectangle((0, 0), 1, 1, color=v) for v in colors.values()]
    ax.legend(handles, list(colors.keys()), loc="lower right")
    ax.set_title("CCBHC Medicaid Demonstration Expansion Cohorts")
    savefig("map_expansion_states_tile")


def main() -> None:
    state = pd.read_parquet(DATA / "analysis_main_state_year.parquet")
    svc = pd.read_parquet(DATA / "service_category_state_year.parquet")
    model = state[state["inclusion_flag_main_state_year"] == 1].copy()

    cohort_tilemap(state)

    trend_outcomes = [
        ("facility_per100k", "Facilities per 100,000"),
        ("crisis_intervention_per100k", "Crisis services per 100,000"),
        ("moud_any_per100k", "MOUD facilities per 100,000"),
        ("targeted_services_per100k", "Targeted service-lines per 100,000"),
    ]
    for col, label in trend_outcomes:
        if col not in model:
            continue
        tmp = model.groupby(["year", "treated_state_2024"], as_index=False)[col].mean()
        tmp["group"] = np.where(tmp["treated_state_2024"] == 1, "2024 selected", "comparison")
        plt.figure(figsize=(7, 4))
        sns.lineplot(data=tmp, x="year", y=col, hue="group", marker="o")
        plt.axvline(2024, color="black", ls="--", lw=1)
        plt.ylabel(label)
        plt.xlabel("")
        plt.title(f"Raw Trends: {label}")
        savefig(f"raw_trend_{col}")

    baseline = model[model["year"].between(2021, 2023)].groupby("state", as_index=False).agg(
        baseline_facility_per100k=("facility_per100k", "mean"),
        treated_state_2024=("treated_state_2024", "max"),
        planning_control=("eligible_planning_control", "max"),
        not_yet_2026=("selected_2026_cohort", "max"),
        poverty_rate=("poverty_rate", "mean"),
        unemployment_rate=("unemployment_rate", "mean"),
        targeted_services_per100k=("targeted_services_per100k", "mean"),
    )
    plt.figure(figsize=(8, 4))
    sns.histplot(data=baseline, x="baseline_facility_per100k", hue="treated_state_2024", bins=20)
    plt.title("Baseline State Facility Density Distribution, 2021-2023")
    savefig("distribution_baseline_facility_density")

    plt.figure(figsize=(9, 4))
    order = baseline.sort_values("baseline_facility_per100k", ascending=False)
    sns.barplot(data=order, x="state", y="baseline_facility_per100k", hue="treated_state_2024", dodge=False)
    plt.xticks(rotation=90)
    plt.title("Baseline State Behavioral-Health Facility Density")
    savefig("map_baseline_capacity_state_proxy")

    missing = model[["state", "year"] + [c for c, _ in trend_outcomes]].isna().groupby("year").mean(numeric_only=True)
    save_csv(missing.reset_index(), RESULT / "missingness_summary.csv")
    plt.figure(figsize=(7, 3))
    sns.heatmap(missing.T, cmap="mako_r", cbar_kws={"label": "Missing share"})
    plt.title("Missingness by Main State-Year Outcome")
    savefig("missingness_heatmap_state")

    rows = []
    vars_for_balance = ["baseline_facility_per100k", "targeted_services_per100k", "poverty_rate", "unemployment_rate"]
    strategies = {
        "all_non_original_non_2024": baseline["treated_state_2024"].eq(0),
        "planning_grant_not_selected": baseline["planning_control"].eq(1),
        "not_yet_2026": baseline["not_yet_2026"].eq(1),
    }
    treated = baseline[baseline["treated_state_2024"] == 1]
    for strat, mask in strategies.items():
        controls = baseline[mask]
        for var in vars_for_balance:
            rows.append({
                "strategy": strat,
                "variable": var,
                "treated_mean": treated[var].mean(),
                "control_mean": controls[var].mean(),
                "smd": smd(treated[var], controls[var]),
                "n_treated": len(treated),
                "n_control": len(controls),
            })
    save_csv(pd.DataFrame(rows), RESULT / "balance_table_control_strategies.csv")

    coverage = state.groupby("year", as_index=False).agg(
        states_with_nsumhss=("facility_count", lambda s: int(s.notna().sum())),
        facilities=("facility_count", "sum"),
    )
    save_csv(coverage, RESULT / "data_coverage_by_year.csv")

    plt.figure(figsize=(7, 4))
    sns.boxplot(data=svc[svc["year"] == 2024], x="service_category", y="service_per100k")
    plt.title("2024 Service Density by Service Category")
    plt.xlabel("")
    plt.ylabel("Service-lines per 100,000")
    savefig("outcome_distribution_service_categories_2024")

    county = pd.read_parquet(DATA / "analysis_main_county_year.parquet")
    county_summary = county.groupby("year", as_index=False).agg(
        counties=("county_fips", "nunique"),
        county_outcome_available=("n_sumhss_county_outcomes_available", "max"),
    )
    save_csv(county_summary, RESULT / "county_capacity_coverage_summary.csv")

    append_note("Phase 5: Control construction/descriptives", [
        "Produced raw trends, balance diagnostics, missingness, data coverage, service distributions, and cohort tile map.",
        "Planning-grant and not-yet-treated controls are available at the state level; county matched controls are not estimable without county outcomes.",
        "Baseline balance is diagnostic only because selection into demonstration is non-random and pre-period is short.",
    ])


if __name__ == "__main__":
    main()
