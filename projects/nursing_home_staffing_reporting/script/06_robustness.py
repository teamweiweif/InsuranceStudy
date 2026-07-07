from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from docx import Document
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULT = ROOT / "result"
TEMP = ROOT / "temp"
TAB = RESULT / "tables"

ROBUST_OUTCOMES = [
    "weekend_total_nurse_hprd",
    "weekend_rn_hprd",
    "weekday_total_nurse_hprd",
    "weekday_minus_weekend_total_hprd",
    "total_nurse_hprd",
]


def save_table(df: pd.DataFrame, base: Path) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(base.with_suffix(".csv"), index=False)
    df.to_excel(base.with_suffix(".xlsx"), index=False)
    df.to_latex(base.with_suffix(".tex"), index=False, float_format="%.4f")
    try:
        base.with_suffix(".md").write_text(df.to_markdown(index=False), encoding="utf-8")
    except Exception:
        base.with_suffix(".md").write_text(df.to_csv(index=False), encoding="utf-8")
    doc = Document()
    table = doc.add_table(rows=1, cols=len(df.columns))
    for j, col in enumerate(df.columns):
        table.rows[0].cells[j].text = str(col)
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for j, col in enumerate(df.columns):
            val = row[col]
            cells[j].text = "" if pd.isna(val) else str(val)
    doc.save(base.with_suffix(".docx"))


def iterative_demean(mat: np.ndarray, groups: list[pd.Series], max_iter: int = 30, tol: float = 1e-8) -> np.ndarray:
    out = mat.astype(float, copy=True)
    out -= np.nanmean(out, axis=0, keepdims=True)
    for _ in range(max_iter):
        max_adjustment = 0.0
        for g in groups:
            means = pd.DataFrame(out).groupby(g.to_numpy(), sort=False).transform("mean").to_numpy()
            max_adjustment = max(max_adjustment, float(np.nanmax(np.abs(means))))
            out -= means
        if max_adjustment < tol:
            break
    return out


def fe_ols(df: pd.DataFrame, y_col: str, x_cols: list[str], fe_cols: list[str], cluster_col: str) -> dict:
    cols = list(dict.fromkeys([y_col] + x_cols + fe_cols + [cluster_col]))
    d = df[cols].replace([np.inf, -np.inf], np.nan).dropna().copy()
    y = d[y_col].to_numpy(float).reshape(-1, 1)
    X = d[x_cols].to_numpy(float)
    groups = [d[c].astype(str) for c in fe_cols]
    yr = iterative_demean(y, groups).ravel()
    Xr = iterative_demean(X, groups)
    keep = np.nanstd(Xr, axis=0) > 1e-10
    Xr = Xr[:, keep]
    x_kept = [x for x, k in zip(x_cols, keep) if k]
    if not x_kept:
        raise ValueError(f"No non-collinear regressors for {y_col}")
    xtx_inv = np.linalg.pinv(Xr.T @ Xr)
    beta = xtx_inv @ (Xr.T @ yr)
    resid = yr - Xr @ beta
    sums = pd.DataFrame(Xr * resid[:, None], columns=x_kept).groupby(
        d[cluster_col].astype(str).to_numpy(), sort=False
    ).sum()
    meat = sums.to_numpy().T @ sums.to_numpy()
    n, k, g = len(d), len(x_kept), sums.shape[0]
    correction = (g / (g - 1)) * ((n - 1) / max(n - k, 1)) if g > 1 else 1.0
    vcov = correction * (xtx_inv @ meat @ xtx_inv)
    se = np.sqrt(np.clip(np.diag(vcov), 0, np.inf))
    pval = 2 * (1 - stats.t.cdf(np.abs(beta / se), df=max(g - 1, 1)))
    return {
        "n": n,
        "n_clusters": g,
        "x_cols": x_kept,
        "beta": pd.Series(beta, index=x_kept),
        "se": pd.Series(se, index=x_kept),
        "pval": pd.Series(pval, index=x_kept),
    }


def post_rows(
    panel: pd.DataFrame,
    outcomes: list[str],
    exposure: str,
    label: str,
    fe_cols: list[str],
    sample_note: str,
) -> list[dict]:
    d = panel.copy()
    d["x_jan_to_jun2022"] = d[exposure] * d["jan_to_jun2022"]
    d["x_post_jul2022"] = d[exposure] * d["post_jul2022"]
    rows = []
    for outcome in outcomes:
        try:
            fit = fe_ols(d, outcome, ["x_jan_to_jun2022", "x_post_jul2022"], fe_cols, "facility_id")
        except Exception as exc:
            rows.append(
                {
                    "check": label,
                    "sample": sample_note,
                    "outcome": outcome,
                    "term": "ERROR",
                    "estimate": np.nan,
                    "std_error": np.nan,
                    "ci_low": np.nan,
                    "ci_high": np.nan,
                    "p_value": np.nan,
                    "n_obs": len(d),
                    "n_facilities": d["facility_id"].nunique(),
                    "fixed_effects": "+".join(fe_cols),
                    "exposure": exposure,
                    "note": str(exc),
                }
            )
            continue
        for term in fit["x_cols"]:
            b = fit["beta"][term]
            se = fit["se"][term]
            rows.append(
                {
                    "check": label,
                    "sample": sample_note,
                    "outcome": outcome,
                    "term": term,
                    "estimate": b,
                    "std_error": se,
                    "ci_low": b - 1.96 * se,
                    "ci_high": b + 1.96 * se,
                    "p_value": fit["pval"][term],
                    "n_obs": fit["n"],
                    "n_facilities": fit["n_clusters"],
                    "fixed_effects": "+".join(fe_cols),
                    "exposure": exposure,
                    "note": "",
                }
            )
    return rows


def placebo_rows(panel: pd.DataFrame) -> list[dict]:
    d = panel[(panel["period_date"] < pd.Timestamp("2022-01-01")) & (panel["period_date"] >= pd.Timestamp("2019-01-01"))].copy()
    d["placebo_jan_to_jun2021"] = (
        (d["period_date"] >= pd.Timestamp("2021-01-01")) & (d["period_date"] < pd.Timestamp("2021-07-01"))
    ).astype(int)
    d["placebo_post_jul2021"] = (d["period_date"] >= pd.Timestamp("2021-07-01")).astype(int)
    d["x_placebo_jan_to_jun2021"] = d["high_exposure_composite"] * d["placebo_jan_to_jun2021"]
    d["x_placebo_post_jul2021"] = d["high_exposure_composite"] * d["placebo_post_jul2021"]
    rows = []
    for outcome in ["weekend_total_nurse_hprd", "weekend_rn_hprd", "weekday_total_nurse_hprd"]:
        fit = fe_ols(
            d,
            outcome,
            ["x_placebo_jan_to_jun2021", "x_placebo_post_jul2021"],
            ["facility_id", "period"],
            "facility_id",
        )
        for term in fit["x_cols"]:
            b = fit["beta"][term]
            se = fit["se"][term]
            rows.append(
                {
                    "check": "placebo_2021_timing",
                    "sample": "pre_2022_only",
                    "outcome": outcome,
                    "term": term,
                    "estimate": b,
                    "std_error": se,
                    "ci_low": b - 1.96 * se,
                    "ci_high": b + 1.96 * se,
                    "p_value": fit["pval"][term],
                    "n_obs": fit["n"],
                    "n_facilities": fit["n_clusters"],
                    "fixed_effects": "facility_id+period",
                    "exposure": "high_exposure_composite",
                    "note": "Fake reform date one year before true policy.",
                }
            )
    return rows


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    month = pd.read_parquet(DATA / "analysis_facility_month.parquet")
    month = month[month["analysis_sample"] == 1].copy()
    month["period_date"] = pd.to_datetime(month["period_date"])
    month = month[(month["period_date"] >= "2019-01-01") & (month["period_date"] <= "2025-12-31")]

    rows = []
    exposure_specs = [
        ("high_exposure_composite", "preferred_composite"),
        ("low_baseline_weekend_total_hprd", "low_weekend_total"),
        ("low_baseline_weekend_rn_hprd", "low_weekend_rn"),
        ("high_baseline_weekday_weekend_gap", "high_weekday_weekend_gap"),
        ("high_exposure2021_composite", "baseline_2021_only"),
        ("high_exposure_no2020_composite", "baseline_exclude_2020"),
        ("exposure_composite", "continuous_composite"),
    ]
    for exposure, label in exposure_specs:
        rows += post_rows(month, ROBUST_OUTCOMES, exposure, label, ["facility_id", "period"], "all_months")

    no_covid = month[~((month["period_date"] >= "2020-03-01") & (month["period_date"] <= "2020-12-31"))].copy()
    rows += post_rows(
        no_covid,
        ROBUST_OUTCOMES,
        "high_exposure_composite",
        "exclude_mar_dec_2020",
        ["facility_id", "period"],
        "drop_2020m03_2020m12",
    )

    counts = month.groupby("facility_id")["period"].nunique()
    balanced_ids = counts[counts >= 80].index
    balanced = month[month["facility_id"].isin(balanced_ids)].copy()
    rows += post_rows(
        balanced,
        ROBUST_OUTCOMES,
        "high_exposure_composite",
        "balanced_panel_80_months",
        ["facility_id", "period"],
        "facilities_with_at_least_80_months",
    )

    if "ownership_for_profit" in month.columns:
        for val, label in [(1, "for_profit"), (0, "not_for_profit")]:
            sub = month[month["ownership_for_profit"] == val].copy()
            if sub["facility_id"].nunique() > 100:
                rows += post_rows(
                    sub,
                    ["weekend_total_nurse_hprd", "weekend_rn_hprd", "weekday_minus_weekend_total_hprd"],
                    "high_exposure_composite",
                    f"ownership_{label}",
                    ["facility_id", "period"],
                    label,
                )

    quarter = pd.read_parquet(DATA / "analysis_facility_quarter.parquet")
    quarter = quarter[quarter["analysis_sample"] == 1].copy()
    rows += post_rows(
        quarter,
        ROBUST_OUTCOMES,
        "high_exposure_composite",
        "facility_quarter_panel",
        ["facility_id", "period"],
        "quarterly_panel",
    )

    rows += placebo_rows(month)

    robust = pd.DataFrame(rows)
    robust.to_csv(RESULT / "robustness_results.csv", index=False)
    save_table(robust.round(5), TAB / "table5_robustness")

    with (TEMP / "audit_log.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 7 Robustness and Falsification\n\n"
            "- Ran alternative exposure definitions, 2021-only and no-2020 baselines, COVID-period exclusion, balanced-panel restriction, facility-quarter panel, ownership subsamples, and 2021 placebo timing tests.\n"
            f"- Wrote robustness results to `{(RESULT / 'robustness_results.csv').relative_to(ROOT)}`.\n"
        )
    with (TEMP / "iteration_notes.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 7: Robustness and Falsification\n\n"
            "Robustness checks test whether the preferred result is driven by exposure construction, the COVID-disrupted 2020 period, unbalanced facility panels, time aggregation, ownership composition, or fake pre-policy timing.\n\n"
            "Self-question: A result should be described as credible only if it has the same sign and similar magnitude across substantively reasonable exposure definitions and does not appear under placebo timing.\n"
        )

    print("Robustness checks complete.")


if __name__ == "__main__":
    main()
