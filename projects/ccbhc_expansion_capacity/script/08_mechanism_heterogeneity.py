from __future__ import annotations

import pandas as pd

from pipeline_utils import DATA, REPORT, RESULT, TEMP, append_note, fit_fe_ols, save_csv, write_text


def main() -> None:
    state = pd.read_parquet(DATA / "analysis_main_state_year.parquet")
    model = state[state["inclusion_flag_main_state_year"] == 1].copy()
    base = model[model["year"].between(2021, 2023)].groupby("state", as_index=False).agg(
        baseline_capacity=("facility_per100k", "mean"),
        baseline_poverty=("poverty_rate", "mean"),
        baseline_moud=("moud_any_per100k", "mean"),
        baseline_crisis=("crisis_intervention_per100k", "mean"),
    )
    base["high_poverty"] = (base["baseline_poverty"] >= base["baseline_poverty"].median()).astype(int)
    base["low_moud"] = (base["baseline_moud"] <= base["baseline_moud"].median()).astype(int)
    base["low_crisis"] = (base["baseline_crisis"] <= base["baseline_crisis"].median()).astype(int)
    work = model.merge(base, on="state", how="left")
    rows = []
    for mod in ["high_poverty", "low_moud", "low_crisis"]:
        work[f"treated_post_x_{mod}"] = work["treated_post_selection_2024"] * work[mod]
        tab, meta = fit_fe_ols(
            work,
            "targeted_services_per100k",
            ["treated_post_selection_2024", f"treated_post_x_{mod}"],
            ["state", "year"],
            cluster_col="state",
        )
        tab["moderator"] = mod
        tab["model_status"] = meta.get("status")
        rows.append(tab)
    save_csv(pd.concat(rows, ignore_index=True), RESULT / "table_mechanism_heterogeneity.csv")

    mechanism = """# Mechanism Chain

The hypothesized chain is:

1. BSCA demonstration selection.
2. State certification and PPS infrastructure.
3. Clinic entry or conversion into CCBHCs.
4. Increases in targeted service capacity: crisis services, MOUD, primary-care integration, care coordination, and low-barrier access.
5. Changes in admissions and crisis-system pressure.
6. Possible longer-run overdose or suicide effects.

What this first build can test:

- Step 1 to step 4 at the state-year level using N-SUMHSS 2021-2024 service-capacity measures.
- Whether directly targeted services move differently from related or weakly targeted service categories using a service-line DDD panel.
- Whether early changes are larger in high-poverty, low-MOUD, or low-crisis-capacity states.

What this first build cannot yet test credibly:

- Demonstration entry to county CCBHC site density, because a public historical county site panel was not found and N-SUMHSS PUF suppresses county geography.
- CCBHC site density as a mediator, because current CCBHC locators mix demonstration clinics, independent state CCBHCs, and expansion grantees and are not historical.
- Admissions or mortality effects, because public TEDS-A and mortality files do not provide a meaningful 2025 post period for this policy shock.

Mediation is therefore not interpreted causally. The mechanism evidence is a layer of consistency checks, not a proof of mediation.
"""
    write_text(REPORT / "mechanism_chain.md", mechanism)

    rejected = """# Rejected Designs

## County-year DID

Rejected for this build. N-SUMHSS public-use files include state but not county,
FIPS, address, latitude, or longitude. Current CCBHC locator lists are not enough
to reconstruct historical county treatment timing.

## Facility-level CCBHC conversion design

Rejected for this build. N-SUMHSS PUF does not identify CCBHC demonstration status,
CCBHC grantee status, certification date, or payment status.

## TEDS-A admissions as an early post outcome

Rejected for main models. Public files are available through 2023 in this build,
so there is no post-selection admissions outcome.

## Mortality as a main outcome

Rejected. Overdose and suicide mortality are downstream, slow-moving outcomes;
the post period is too short and current public releases do not support a causal
claim for the 2024 CCBHC expansion.

## Causal ML targeting

Rejected. The main identification evidence is not credible enough yet. Policy
learning would optimize noise from one partial post year and unverified county
exposure.
"""
    write_text(TEMP / "rejected_designs.md", rejected)
    append_note("Phase 8: Mechanism and heterogeneity", [
        "Tested state-level heterogeneity for high poverty, low baseline MOUD, and low baseline crisis capacity.",
        "Framed DDD and heterogeneity as mechanism consistency checks, not causal mediation.",
        "Rejected county DID, facility conversion, TEDS-A early post, mortality main outcome, and causal ML for documented data/design reasons.",
    ])


if __name__ == "__main__":
    main()
