from __future__ import annotations

import numpy as np
import pandas as pd

from project_utils import DATA, RAW, STATE_NAME_TO_ABBR, append_audit, read_parquet, save_csv, save_parquet


POP_XLSX = RAW / "census" / "NST-EST2025-POP.xlsx"


def parse_census_population() -> pd.DataFrame:
    raw = pd.read_excel(POP_XLSX, sheet_name=0, header=None)
    rows = []
    for _, row in raw.iloc[4:].iterrows():
        area = row.iloc[0]
        if not isinstance(area, str) or not area.startswith("."):
            continue
        state_name = area.strip().lstrip(".")
        state = STATE_NAME_TO_ABBR.get(state_name)
        if state is None:
            continue
        for col, year in zip(range(2, 8), range(2020, 2026)):
            rows.append(
                {
                    "state": state,
                    "state_name": state_name,
                    "year": year,
                    "population": pd.to_numeric(row.iloc[col], errors="coerce"),
                    "population_source_year": year,
                    "population_carried_forward": False,
                }
            )
    pop = pd.DataFrame(rows).dropna(subset=["population"])
    pop["population"] = pop["population"].astype(float)
    return pop


def build_monthly_covariates(outcomes: pd.DataFrame, pop: pd.DataFrame) -> pd.DataFrame:
    grid = outcomes[["state", "month"]].drop_duplicates().copy()
    grid["year"] = grid["month"].dt.year
    grid["population_lookup_year"] = np.minimum(grid["year"], 2025)
    cov = grid.merge(
        pop.rename(columns={"year": "population_lookup_year"}),
        on=["state", "population_lookup_year"],
        how="left",
    )
    cov["population_carried_forward"] = cov["year"].gt(2025) & cov["population"].notna()
    cov["has_population_denominator"] = cov["population"].notna()
    cov["population_source_note"] = np.where(
        cov["population_carried_forward"],
        "Vintage 2025 Census July 1, 2025 estimate carried forward for 2026 months.",
        "Vintage 2025 Census annual state resident population estimate.",
    )
    return cov[
        [
            "state",
            "month",
            "year",
            "state_name",
            "population",
            "population_lookup_year",
            "population_carried_forward",
            "has_population_denominator",
            "population_source_note",
        ]
    ]


def build_mechanism_state_year(outcomes: pd.DataFrame, pop: pd.DataFrame) -> pd.DataFrame:
    revenue = read_parquet(DATA / "fcc_annual_fee_revenue_state_year.parquet")
    fee_schedule = read_parquet(DATA / "fee_schedule_state_month.parquet")

    outcome_annual = (
        outcomes.assign(year=outcomes["month"].dt.year)
        .groupby(["state", "year"], as_index=False)
        .agg(
            annual_routed_contacts=("routed_in_state", "sum"),
            annual_answered_contacts=("answered_in_state", "sum"),
            annual_mean_answer_rate=("in_state_answer_rate", "mean"),
            annual_mean_flowout_rate=("flowout_to_national_backup_rate", "mean"),
            annual_mean_asa_seconds=("average_speed_to_answer_seconds", "mean"),
            observed_months=("month", "nunique"),
        )
    )

    fee_annual = (
        fee_schedule.assign(year=fee_schedule["month"].dt.year)
        .groupby(["state", "year"], as_index=False)
        .agg(
            fee_active_months=("fee_collection_active", "sum"),
            operational_active_months=("operational_treatment_active", "sum"),
            mean_fee_cents_max=("fee_cents_max", "mean"),
            max_fee_cents=("fee_cents_max", "max"),
        )
    )
    states = sorted(outcomes["state"].unique())
    years = sorted(outcomes["month"].dt.year.unique())
    grid = pd.MultiIndex.from_product([states, years], names=["state", "year"]).to_frame(index=False)
    mech = grid.merge(outcome_annual, on=["state", "year"], how="left")
    mech = mech.merge(fee_annual, on=["state", "year"], how="left")
    mech = mech.merge(revenue, on=["state", "year"], how="left")
    mech = mech.merge(pop[["state", "year", "population"]], on=["state", "year"], how="left")
    latest_pop = pop.sort_values("year").drop_duplicates("state", keep="last")[["state", "population"]]
    mech = mech.merge(latest_pop.rename(columns={"population": "latest_population"}), on="state", how="left")
    mech["population_for_revenue"] = mech["population"].fillna(mech["latest_population"])
    mech["fee_revenue_observed"] = mech["fee_revenue_nominal"].notna()
    mech["fee_revenue_nominal_for_2021_2024"] = mech["fee_revenue_nominal"]
    mech.loc[mech["year"].between(2021, 2024) & mech["fee_revenue_nominal_for_2021_2024"].isna(), "fee_revenue_nominal_for_2021_2024"] = 0.0
    mech["fee_revenue_per_capita"] = mech["fee_revenue_nominal"] / mech["population_for_revenue"]
    mech["fee_revenue_per_100k"] = mech["fee_revenue_per_capita"] * 100000
    mech["fee_revenue_per_routed_contact"] = mech["fee_revenue_nominal"] / mech["annual_routed_contacts"]
    mech["routed_per_100k_annual"] = mech["annual_routed_contacts"] / mech["population_for_revenue"] * 100000
    mech["mechanism_observation_note"] = np.select(
        [
            mech["fee_revenue_observed"],
            mech["year"].gt(2024) & mech["fee_active_months"].fillna(0).gt(0),
            mech["fee_active_months"].fillna(0).eq(0),
        ],
        [
            "FCC annual fee revenue observed.",
            "Fee active after most recent FCC annual accountability report; revenue not yet observed in annual FCC reports.",
            "No fee collection active in this state-year.",
        ],
        default="Revenue unavailable or not separately reported.",
    )
    return mech


def main() -> None:
    outcomes = read_parquet(DATA / "outcomes_988_state_month.parquet")
    pop = parse_census_population()
    cov = build_monthly_covariates(outcomes, pop)
    mech = build_mechanism_state_year(outcomes, pop)

    save_parquet(pop, DATA / "state_population_state_year.parquet")
    save_csv(pop, DATA / "state_population_state_year.csv")
    save_parquet(cov, DATA / "covariates_state_month.parquet")
    save_csv(cov, DATA / "covariates_state_month.csv")
    save_parquet(mech, DATA / "mechanism_state_year.parquet")
    save_csv(mech, DATA / "mechanism_state_year.csv")

    missing_pop = int(cov["has_population_denominator"].eq(False).sum())
    append_audit(
        f"Built Census population covariates and FCC revenue mechanism file. "
        f"State-month rows without Census denominators: {missing_pop}."
    )


if __name__ == "__main__":
    main()

