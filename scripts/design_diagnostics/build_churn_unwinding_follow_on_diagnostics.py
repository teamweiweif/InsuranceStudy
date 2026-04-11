from pathlib import Path
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "design_diagnostics"
OUT.mkdir(parents=True, exist_ok=True)

CORE_MONTHS = [8, 9, 10, 11]
EXPOSURE_FAMILIES = ["procedural_friction", "renewal_intensity", "pending_pressure"]


def weighted_mean(values, weights):
    values = pd.Series(values)
    weights = pd.Series(weights)
    mask = values.notna() & weights.notna() & (weights > 0)
    if not mask.any():
        return np.nan
    return float(np.average(values[mask], weights=weights[mask]))


def weighted_rate(df, outcome, weight="WPFINWGT"):
    sub = df[df[weight].notna() & (df[weight] > 0) & df[outcome].notna()]
    if sub.empty:
        return np.nan
    return float(np.average(sub[outcome].astype(float), weights=sub[weight]))


def assign_tertiles(series, labels=("low", "mid", "high")):
    ranked = series.rank(method="first")
    return pd.qcut(ranked, q=3, labels=labels)


def md_table(df):
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            if pd.isna(value):
                vals.append("")
            else:
                vals.append(str(value))
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep] + rows)


def state_month_aggregate(df):
    rows = []
    for (state_fips, state_abbr, monthcode), g in df.groupby(
        ["tehc_st_fips", "state_abbreviation", "MONTHCODE"], dropna=False
    ):
        rows.append(
            {
                "tehc_st_fips": state_fips,
                "state_abbreviation": state_abbr,
                "MONTHCODE": monthcode,
                "eligible_weight_sum": float(g["WPFINWGT"].sum()),
                "medicaid_exit_rate_w": weighted_rate(g, "medicaid_exit_next"),
                "exit_to_uninsured_rate_w": weighted_rate(g, "medicaid_exit_to_uninsured_next"),
                "procedural_friction": g["cms_updated_procedural_share_of_terminated"]
                .dropna()
                .iloc[0]
                if g["cms_updated_procedural_share_of_terminated"].notna().any()
                else np.nan,
                "renewal_intensity": g["cms_updated_renewal_due_n"].dropna().iloc[0]
                if g["cms_updated_renewal_due_n"].notna().any()
                else np.nan,
                "pending_pressure": g["cms_updated_pending_rate"].dropna().iloc[0]
                if g["cms_updated_pending_rate"].notna().any()
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def state_level_exposure(df):
    rows = []
    for (state_fips, state_abbr), g in df.groupby(["tehc_st_fips", "state_abbreviation"], dropna=False):
        rows.append(
            {
                "tehc_st_fips": state_fips,
                "state_abbreviation": state_abbr,
                "eligible_weight_sum": float(g["eligible_weight_sum"].sum()),
                "procedural_friction": weighted_mean(g["procedural_friction"], g["eligible_weight_sum"]),
                "renewal_intensity": weighted_mean(g["renewal_intensity"], g["eligible_weight_sum"]),
                "pending_pressure": weighted_mean(g["pending_pressure"], g["eligible_weight_sum"]),
            }
        )
    out = pd.DataFrame(rows)
    for fam in EXPOSURE_FAMILIES:
        out[f"{fam}_tertile"] = assign_tertiles(out[fam]).astype(str)
    return out


def pre_state_year_rates(df):
    rows = []
    for (reference_year, state_fips), g in df.groupby(["reference_year", "tehc_st_fips"], dropna=False):
        rows.append(
            {
                "reference_year": int(reference_year),
                "tehc_st_fips": state_fips,
                "eligible_weight_sum": float(g["WPFINWGT"].sum()),
                "weighted_exit_rate": weighted_rate(g, "medicaid_exit_next"),
                "weighted_exit_to_uninsured_rate": weighted_rate(g, "medicaid_exit_to_uninsured_next"),
            }
        )
    return pd.DataFrame(rows)


def grouped_weighted_summary(df, group_cols, weight_col="eligible_weight_sum"):
    rows = []
    for keys, g in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row.update(
            {
                "states": int(g["tehc_st_fips"].nunique()) if "tehc_st_fips" in g.columns else np.nan,
                "eligible_weight_sum": float(g[weight_col].sum()),
                "weighted_exit_rate": weighted_mean(g["weighted_exit_rate"], g[weight_col]),
                "weighted_exit_to_uninsured_rate": weighted_mean(
                    g["weighted_exit_to_uninsured_rate"], g[weight_col]
                ),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    pre_2021 = pq.read_table(
        ROOT / "outputs" / "prototype" / "sipp_2022_corrected_person_month_flags.parquet",
        columns=[
            "reference_year",
            "MONTHCODE",
            "tehc_st_fips",
            "WPFINWGT",
            "eligible_medicaid_transition",
            "medicaid_exit_next",
            "medicaid_exit_to_uninsured_next",
        ],
    ).to_pandas()
    pre_2022 = pq.read_table(
        ROOT / "outputs" / "prototype" / "sipp_2023_corrected_person_month_flags.parquet",
        columns=[
            "reference_year",
            "MONTHCODE",
            "tehc_st_fips",
            "WPFINWGT",
            "eligible_medicaid_transition",
            "medicaid_exit_next",
            "medicaid_exit_to_uninsured_next",
        ],
    ).to_pandas()
    merged_2023 = pq.read_table(
        ROOT / "outputs" / "prototype" / "sipp_2024_cms_updated_renewal_outcomes_merged.parquet",
        columns=[
            "reference_year",
            "MONTHCODE",
            "tehc_st_fips",
            "state_abbreviation",
            "WPFINWGT",
            "eligible_medicaid_transition",
            "medicaid_exit_next",
            "medicaid_exit_to_uninsured_next",
            "cms_updated_renewal_due_n",
            "cms_updated_pending_rate",
            "cms_updated_procedural_share_of_terminated",
        ],
    ).to_pandas()

    for df in (pre_2021, pre_2022, merged_2023):
        for col in ["MONTHCODE", "tehc_st_fips", "WPFINWGT", "reference_year"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    cur = merged_2023[
        merged_2023["MONTHCODE"].isin(CORE_MONTHS)
        & merged_2023["eligible_medicaid_transition"].fillna(False)
        & merged_2023["tehc_st_fips"].notna()
    ].copy()
    state_month = state_month_aggregate(cur)
    state_exposure = state_level_exposure(state_month)
    state_exposure.to_csv(OUT / "later_exposure_state_tertiles.csv", index=False)

    pre_all = pd.concat([pre_2021, pre_2022], ignore_index=True)
    pre_all = pre_all[
        pre_all["MONTHCODE"].isin(CORE_MONTHS)
        & pre_all["eligible_medicaid_transition"].fillna(False)
        & pre_all["tehc_st_fips"].notna()
    ].copy()
    pre_state_year = pre_state_year_rates(pre_all)

    falsification_parts = []
    for fam in EXPOSURE_FAMILIES:
        tert_col = f"{fam}_tertile"
        merged = pre_state_year.merge(state_exposure[["tehc_st_fips", tert_col]], on="tehc_st_fips", how="left")
        grouped = grouped_weighted_summary(merged, ["reference_year", tert_col]).rename(
            columns={tert_col: "tertile"}
        )
        grouped["exposure_family"] = fam
        falsification_parts.append(grouped)
        for year in sorted(grouped["reference_year"].dropna().unique()):
            subset = grouped[grouped["reference_year"] == year].set_index("tertile")
            if {"high", "low"}.issubset(subset.index):
                falsification_parts.append(
                    pd.DataFrame(
                        [
                            {
                                "reference_year": int(year),
                                "tertile": "high_minus_low",
                                "states": int(subset.loc["high", "states"] + subset.loc["low", "states"]),
                                "eligible_weight_sum": float(
                                    subset.loc["high", "eligible_weight_sum"]
                                    + subset.loc["low", "eligible_weight_sum"]
                                ),
                                "weighted_exit_rate": float(
                                    subset.loc["high", "weighted_exit_rate"]
                                    - subset.loc["low", "weighted_exit_rate"]
                                ),
                                "weighted_exit_to_uninsured_rate": float(
                                    subset.loc["high", "weighted_exit_to_uninsured_rate"]
                                    - subset.loc["low", "weighted_exit_to_uninsured_rate"]
                                ),
                                "exposure_family": fam,
                            }
                        ]
                    )
                )
    falsification = pd.concat(falsification_parts, ignore_index=True)
    falsification = falsification[
        [
            "reference_year",
            "exposure_family",
            "tertile",
            "states",
            "eligible_weight_sum",
            "weighted_exit_rate",
            "weighted_exit_to_uninsured_rate",
        ]
    ]
    falsification.to_csv(OUT / "preperiod_falsification_summary.csv", index=False)

    baseline_rows = []
    for state_fips, g in pre_all.groupby("tehc_st_fips", dropna=False):
        baseline_rows.append(
            {
                "tehc_st_fips": state_fips,
                "baseline_weight_sum": float(g["WPFINWGT"].sum()),
                "baseline_exit_rate": weighted_rate(g, "medicaid_exit_next"),
                "baseline_exit_to_uninsured_rate": weighted_rate(g, "medicaid_exit_to_uninsured_next"),
            }
        )
    baseline_state = pd.DataFrame(baseline_rows)
    baseline_state["baseline_exit_tertile"] = assign_tertiles(baseline_state["baseline_exit_rate"]).astype(str)
    baseline_state.to_csv(OUT / "baseline_state_risk_tertiles.csv", index=False)

    hetero_frames = []
    for df, label in [(pre_2021, "2021_pre"), (pre_2022, "2022_pre"), (merged_2023, "2023_unwinding")]:
        sub = df[
            df["MONTHCODE"].isin(CORE_MONTHS)
            & df["eligible_medicaid_transition"].fillna(False)
            & df["tehc_st_fips"].notna()
        ].copy()
        sub["source_label"] = label
        hetero_frames.append(sub)
    hetero_all = pd.concat(hetero_frames, ignore_index=True).merge(
        baseline_state[["tehc_st_fips", "baseline_exit_tertile"]], on="tehc_st_fips", how="left"
    )
    hetero_rows = []
    for (source_label, reference_year, tertile), g in hetero_all.groupby(
        ["source_label", "reference_year", "baseline_exit_tertile"], dropna=False
    ):
        hetero_rows.append(
            {
                "source_label": source_label,
                "reference_year": int(reference_year),
                "baseline_exit_tertile": tertile,
                "states": int(g["tehc_st_fips"].nunique()),
                "eligible_weight_sum": float(g["WPFINWGT"].sum()),
                "weighted_exit_rate": weighted_rate(g, "medicaid_exit_next"),
                "weighted_exit_to_uninsured_rate": weighted_rate(g, "medicaid_exit_to_uninsured_next"),
            }
        )
    hetero = pd.DataFrame(hetero_rows)
    extra_rows = []
    for label in hetero["source_label"].unique():
        subset = hetero[hetero["source_label"] == label].set_index("baseline_exit_tertile")
        if {"high", "low"}.issubset(subset.index):
            extra_rows.append(
                {
                    "source_label": label,
                    "reference_year": int(subset["reference_year"].dropna().iloc[0]),
                    "baseline_exit_tertile": "high_minus_low",
                    "states": int(subset.loc["high", "states"] + subset.loc["low", "states"]),
                    "eligible_weight_sum": float(
                        subset.loc["high", "eligible_weight_sum"] + subset.loc["low", "eligible_weight_sum"]
                    ),
                    "weighted_exit_rate": float(
                        subset.loc["high", "weighted_exit_rate"] - subset.loc["low", "weighted_exit_rate"]
                    ),
                    "weighted_exit_to_uninsured_rate": float(
                        subset.loc["high", "weighted_exit_to_uninsured_rate"]
                        - subset.loc["low", "weighted_exit_to_uninsured_rate"]
                    ),
                }
            )
    hetero = pd.concat([hetero, pd.DataFrame(extra_rows)], ignore_index=True)
    hetero = hetero[
        [
            "source_label",
            "reference_year",
            "baseline_exit_tertile",
            "states",
            "eligible_weight_sum",
            "weighted_exit_rate",
            "weighted_exit_to_uninsured_rate",
        ]
    ]
    hetero.to_csv(OUT / "heterogeneity_stability_summary.csv", index=False)

    fals_md = OUT / "churn_unwinding_preperiod_falsification.md"
    pre_fals_core = falsification[falsification["tertile"] == "high_minus_low"].copy()
    max_exit = float(pre_fals_core["weighted_exit_rate"].abs().max())
    max_unins = float(pre_fals_core["weighted_exit_to_uninsured_rate"].abs().max())
    with fals_md.open("w", encoding="utf-8") as f:
        f.write("# Churn / Unwinding Pre-Period Falsification Audit\n\n")
        f.write("Last updated: `2026-04-10`\n\n")
        f.write("## Purpose\n\n")
        f.write(
            "This note tests whether later `2023` unwinding-exposure rankings may simply be proxying for pre-existing baseline state churn differences.\n\n"
        )
        f.write("Method:\n\n")
        f.write("- classify states by their later `August-November 2023` exposure intensity\n")
        f.write(
            "- use corrected `reference year 2021` and `reference year 2022` core-window churn outcomes as untreated support years\n"
        )
        f.write("- compare weighted state-level churn rates across later exposure tertiles\n\n")
        f.write("## High-Minus-Low Summary\n\n")
        f.write(
            md_table(
                pre_fals_core.sort_values(["reference_year", "exposure_family"])[
                    [
                        "reference_year",
                        "exposure_family",
                        "weighted_exit_rate",
                        "weighted_exit_to_uninsured_rate",
                    ]
                ].round(4)
            )
        )
        f.write("\n\n## Full Summary\n\n")
        f.write(md_table(falsification.round(4)))
        f.write("\n\n## Reading Guide\n\n")
        f.write("- Large and stable `high_minus_low` pre-period gaps would weaken later unwinding interpretation.\n")
        f.write("- Small or mixed pre-period gaps do not prove identification, but they reduce one obvious falsification concern.\n")
        f.write("- This is a state-level falsification screen, not a final event-study test.\n\n")
        f.write("## Bottom Line\n\n")
        f.write(
            f"- Across the first falsification screen, the largest absolute pre-period `high_minus_low` difference is `{max_exit:.4f}` for `medicaid_exit_next` and `{max_unins:.4f}` for `exit_to_uninsured`.\n"
        )
        f.write(
            "- This means the project should still run later design diagnostics, but later exposure rankings do not automatically look like trivial proxies for pre-existing state churn levels.\n"
        )

    hetero_md = OUT / "churn_unwinding_heterogeneity_stability.md"
    hetero_hl = hetero[hetero["baseline_exit_tertile"] == "high_minus_low"].copy()
    with hetero_md.open("w", encoding="utf-8") as f:
        f.write("# Churn / Unwinding Heterogeneity Stability Screen\n\n")
        f.write("Last updated: `2026-04-10`\n\n")
        f.write("## Purpose\n\n")
        f.write(
            "This note runs a conservative first heterogeneity-stability screen using only subgroup dimensions already retained in the current corrected prototype files.\n\n"
        )
        f.write("Current subgroup design:\n\n")
        f.write("- state baseline-risk tertiles built from pooled corrected `reference years 2021-2022`\n")
        f.write(
            "- no broad demographic feature layer yet, because the current prototype files intentionally keep a narrow churn-focused variable set\n\n"
        )
        f.write("## High-Minus-Low Summary\n\n")
        f.write(
            md_table(
                hetero_hl.sort_values(["reference_year"])[
                    [
                        "source_label",
                        "reference_year",
                        "weighted_exit_rate",
                        "weighted_exit_to_uninsured_rate",
                    ]
                ].round(4)
            )
        )
        f.write("\n\n## Full Summary\n\n")
        f.write(md_table(hetero.round(4)))
        f.write("\n\n## Reading Guide\n\n")
        f.write(
            "- If high-baseline-risk states remain higher-risk in both pre-period years and the unwinding year, that supports stability of the risk ranking, not necessarily treatment identification.\n"
        )
        f.write("- If ordering flips wildly across years, later targeting logic becomes weaker.\n")
        f.write(
            "- This screen is intentionally conservative because the current prototype files do not yet carry the future high-dimensional targeting feature set.\n\n"
        )
        f.write("## Bottom Line\n\n")
        f.write("- The current heterogeneity screen is best read as a stability check on state-level baseline risk ordering.\n")
        f.write(
            "- It is useful for deciding whether later richer subgroup or `causal ML` work is worth building, but it is not itself a targeting result.\n"
        )

    summary = {
        "falsification_md": str(fals_md.relative_to(ROOT)).replace("\\", "/"),
        "heterogeneity_md": str(hetero_md.relative_to(ROOT)).replace("\\", "/"),
        "falsification_csv": "outputs/design_diagnostics/preperiod_falsification_summary.csv",
        "heterogeneity_csv": "outputs/design_diagnostics/heterogeneity_stability_summary.csv",
        "state_exposure_tertiles_csv": "outputs/design_diagnostics/later_exposure_state_tertiles.csv",
        "baseline_state_risk_tertiles_csv": "outputs/design_diagnostics/baseline_state_risk_tertiles.csv",
        "core_window_months": CORE_MONTHS,
        "notes": [
            "falsification screen uses later 2023 exposure tertiles mapped onto corrected 2021-2022 baseline churn rates",
            "heterogeneity stability screen currently uses only state baseline-risk tertiles because the current prototype files do not yet carry a richer feature layer",
        ],
    }
    with (OUT / "churn_unwinding_follow_on_diagnostics_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Wrote follow-on diagnostics artifacts to", OUT)
    print("\nPRE-FALS HIGH-LOW")
    print(
        pre_fals_core.sort_values(["reference_year", "exposure_family"])[
            [
                "reference_year",
                "exposure_family",
                "weighted_exit_rate",
                "weighted_exit_to_uninsured_rate",
            ]
        ]
        .round(4)
        .to_string(index=False)
    )
    print("\nHETERO HIGH-LOW")
    print(
        hetero_hl.sort_values(["reference_year"])[
            [
                "source_label",
                "reference_year",
                "weighted_exit_rate",
                "weighted_exit_to_uninsured_rate",
            ]
        ]
        .round(4)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
