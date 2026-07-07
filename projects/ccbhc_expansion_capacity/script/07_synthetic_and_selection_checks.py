from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from pipeline_utils import DATA, RESULT, append_note, fit_fe_ols, save_csv, smd


FEATURES = [
    "facility_per100k",
    "targeted_services_per100k",
    "crisis_intervention_per100k",
    "moud_any_per100k",
    "poverty_rate",
    "unemployment_rate",
]


def synth_weights(y_treated: np.ndarray, y_donors: np.ndarray) -> np.ndarray:
    n = y_donors.shape[0]
    if n == 0:
        return np.array([])
    def obj(w):
        return float(np.sum((y_treated - w @ y_donors) ** 2))
    cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    bounds = [(0, 1)] * n
    res = minimize(obj, np.ones(n) / n, bounds=bounds, constraints=cons, method="SLSQP", options={"maxiter": 1000})
    if not res.success:
        return np.ones(n) / n
    return res.x


def main() -> None:
    state = pd.read_parquet(DATA / "analysis_main_state_year.parquet")
    model = state[state["inclusion_flag_main_state_year"] == 1].copy()
    base = model[model["year"].between(2021, 2023)].groupby("state", as_index=False).agg(
        **{f"base_{c}": (c, "mean") for c in FEATURES if c in model.columns},
        treated_state_2024=("treated_state_2024", "max"),
        selected_2026_cohort=("selected_2026_cohort", "max"),
        original_demo_state=("original_demo_state", "max"),
        cares_added_demo_state=("cares_added_demo_state", "max"),
    )
    feature_cols = [
        c for c in base.columns
        if c.startswith("base_") and base[c].notna().sum() >= 10 and base[c].std(skipna=True) > 0
    ]
    base = base.dropna(subset=feature_cols)
    treated = base[base["treated_state_2024"] == 1]
    donors = base[(base["treated_state_2024"] == 0) & (base["original_demo_state"] == 0) & (base["cares_added_demo_state"] == 0)]

    scaler = StandardScaler()
    x_all = scaler.fit_transform(base[feature_cols])
    base_scaled = pd.DataFrame(x_all, columns=feature_cols, index=base.index)
    base_scaled["state"] = base["state"].values

    match_rows = []
    matched_states = set()
    for _, tr in treated.iterrows():
        donor_idx = donors.index
        donor_x = base_scaled.loc[donor_idx, feature_cols].to_numpy(dtype=float)
        treated_x = base_scaled.loc[tr.name, feature_cols].to_numpy(dtype=float)
        diffs = donor_x - treated_x
        dist = np.sqrt((diffs ** 2).sum(axis=1))
        nearest_i = donor_idx[int(np.argmin(dist))]
        nearest = base.loc[nearest_i]
        matched_states.add(nearest["state"])
        match_rows.append({"treated_state": tr["state"], "matched_state": nearest["state"], "distance": float(dist.min())})
    matches = pd.DataFrame(match_rows)
    save_csv(matches, RESULT / "matched_donor_states.csv")

    rows = []
    for var in feature_cols:
        rows.append({
            "variable": var,
            "all_control_smd": smd(treated[var], donors[var]),
            "matched_control_smd": smd(treated[var], base[base["state"].isin(matched_states)][var]),
            "treated_mean": treated[var].mean(),
            "all_control_mean": donors[var].mean(),
            "matched_control_mean": base[base["state"].isin(matched_states)][var].mean(),
        })
    save_csv(pd.DataFrame(rows), RESULT / "balance_table_matched_donors.csv")

    matched_panel = model[(model["treated_state_2024"] == 1) | (model["state"].isin(matched_states))].copy()
    did, meta = fit_fe_ols(matched_panel, "targeted_services_per100k", ["treated_post_selection_2024"], ["state", "year"], cluster_col="state")
    did["strategy"] = "nearest_neighbor_matched_donors"
    did["model_status"] = meta.get("status")
    save_csv(did, RESULT / "table_matched_did.csv")

    synth_rows = []
    weight_rows = []
    gap_rows = []
    years = [2021, 2022, 2023]
    outcome = "targeted_services_per100k"
    donor_states = donors["state"].tolist()
    donor_panel = model[model["state"].isin(donor_states)]
    for tr_state in treated["state"]:
        tr_series = model[(model["state"] == tr_state) & (model["year"].isin(years))].sort_values("year")[outcome].to_numpy(dtype=float)
        donor_matrix = []
        usable_donors = []
        for d in donor_states:
            vals = donor_panel[(donor_panel["state"] == d) & (donor_panel["year"].isin(years))].sort_values("year")[outcome].to_numpy(dtype=float)
            if len(vals) == len(years) and np.all(np.isfinite(vals)):
                donor_matrix.append(vals)
                usable_donors.append(d)
        if len(tr_series) != len(years) or not donor_matrix:
            continue
        donor_matrix = np.vstack(donor_matrix)
        w = synth_weights(tr_series, donor_matrix)
        synth_pre = w @ donor_matrix
        pre_rmspe = float(np.sqrt(np.mean((tr_series - synth_pre) ** 2)))
        tr_2024 = model[(model["state"] == tr_state) & (model["year"] == 2024)][outcome].mean()
        donor_2024 = []
        for d in usable_donors:
            donor_2024.append(model[(model["state"] == d) & (model["year"] == 2024)][outcome].mean())
        synth_2024 = float(w @ np.array(donor_2024))
        gap_2024 = float(tr_2024 - synth_2024)
        synth_rows.append({"treated_state": tr_state, "pre_rmspe": pre_rmspe, "actual_2024": tr_2024, "synthetic_2024": synth_2024, "gap_2024": gap_2024})
        for d, wi in zip(usable_donors, w):
            if wi > 0.001:
                weight_rows.append({"treated_state": tr_state, "donor_state": d, "weight": float(wi)})
        for yr, actual, synth in zip(years, tr_series, synth_pre):
            gap_rows.append({"treated_state": tr_state, "year": yr, "actual": float(actual), "synthetic": float(synth), "gap": float(actual - synth)})
        gap_rows.append({"treated_state": tr_state, "year": 2024, "actual": float(tr_2024), "synthetic": synth_2024, "gap": gap_2024})
    save_csv(pd.DataFrame(synth_rows), RESULT / "synthetic_control_state_summary.csv")
    save_csv(pd.DataFrame(weight_rows), RESULT / "synthetic_control_weights.csv")
    save_csv(pd.DataFrame(gap_rows), RESULT / "synthetic_control_gaps.csv")

    ps_rows = []
    try:
        ps_base = base.copy()
        x = ps_base[feature_cols].to_numpy(dtype=float)
        y = ps_base["treated_state_2024"].to_numpy()
        clf = LogisticRegression(max_iter=1000, random_state=20260707).fit(x, y)
        ps_base["propensity_score"] = clf.predict_proba(x)[:, 1]
        ps_rows = ps_base[["state", "treated_state_2024", "propensity_score"]]
        save_csv(ps_rows, RESULT / "propensity_overlap_scores.csv")
        panel = model.merge(ps_base[["state", "propensity_score"]], on="state", how="left")
        panel["ipw"] = np.where(panel["treated_state_2024"] == 1, 1, panel["propensity_score"] / (1 - panel["propensity_score"]))
        save_csv(panel[["state", "year", "treated_state_2024", "propensity_score", "ipw"]], RESULT / "ipw_state_weights.csv")
    except Exception as exc:
        save_csv(pd.DataFrame([{"status": f"propensity_failed: {exc}"}]), RESULT / "propensity_overlap_scores.csv")

    append_note("Phase 7: Synthetic and selection checks", [
        "Built nearest-neighbor matched donor states from 2021-2023 baseline outcomes and ACS covariates.",
        "Attempted state-level synthetic controls for targeted service density with 2021-2023 pre-fit and 2024 gaps.",
        "Logged propensity overlap scores as a selection-bias diagnostic.",
        "Synthetic-control evidence is weak by design because there are only three pre-years and one partial post-year.",
    ])


if __name__ == "__main__":
    main()
