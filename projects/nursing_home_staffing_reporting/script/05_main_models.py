from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docx import Document
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULT = ROOT / "result"
TEMP = ROOT / "temp"
FIG = RESULT / "figures"
TAB = RESULT / "tables"

MAIN_OUTCOMES = [
    "weekend_total_nurse_hprd",
    "weekend_rn_hprd",
    "weekday_total_nurse_hprd",
    "weekday_rn_hprd",
    "weekday_minus_weekend_total_hprd",
    "total_nurse_hprd",
    "rn_share_total_hours",
    "contract_share_total_hours",
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


def fe_ols(
    df: pd.DataFrame,
    y_col: str,
    x_cols: list[str],
    fe_cols: list[str],
    cluster_col: str = "facility_id",
) -> dict:
    cols = list(dict.fromkeys([y_col] + x_cols + fe_cols + [cluster_col]))
    d = df[cols].replace([np.inf, -np.inf], np.nan).dropna().copy()
    y = d[y_col].to_numpy(float).reshape(-1, 1)
    X = d[x_cols].to_numpy(float)
    groups = [d[c].astype(str) for c in fe_cols]
    yr = iterative_demean(y, groups).ravel()
    Xr = iterative_demean(X, groups)
    keep = np.nanstd(Xr, axis=0) > 1e-10
    dropped = [x for x, k in zip(x_cols, keep) if not k]
    Xr = Xr[:, keep]
    x_kept = [x for x, k in zip(x_cols, keep) if k]
    if len(x_kept) == 0:
        raise ValueError(f"No non-collinear regressors left for {y_col}")

    xtx = Xr.T @ Xr
    xtx_inv = np.linalg.pinv(xtx)
    beta = xtx_inv @ (Xr.T @ yr)
    resid = yr - Xr @ beta
    xu = Xr * resid[:, None]
    sums = pd.DataFrame(xu, columns=x_kept).groupby(d[cluster_col].astype(str).to_numpy(), sort=False).sum()
    meat = sums.to_numpy().T @ sums.to_numpy()
    n = len(d)
    k = len(x_kept)
    g = sums.shape[0]
    correction = (g / (g - 1)) * ((n - 1) / max(n - k, 1)) if g > 1 else 1.0
    vcov = correction * (xtx_inv @ meat @ xtx_inv)
    se = np.sqrt(np.clip(np.diag(vcov), 0, np.inf))
    tstat = beta / se
    pval = 2 * (1 - stats.t.cdf(np.abs(tstat), df=max(g - 1, 1)))
    return {
        "n": n,
        "n_clusters": g,
        "x_cols": x_kept,
        "dropped": dropped,
        "beta": pd.Series(beta, index=x_kept),
        "se": pd.Series(se, index=x_kept),
        "pval": pd.Series(pval, index=x_kept),
        "vcov": pd.DataFrame(vcov, index=x_kept, columns=x_kept),
        "resid": resid,
    }


def post_model_rows(panel: pd.DataFrame, exposure: str = "high_exposure_composite", state_time: bool = False) -> list[dict]:
    rows = []
    d = panel.copy()
    d["exposure_x_jan_to_jun2022"] = d[exposure] * d["jan_to_jun2022"]
    d["exposure_x_post_jul2022"] = d[exposure] * d["post_jul2022"]
    fe = ["facility_id", "state_time"] if state_time else ["facility_id", "period"]
    for outcome in MAIN_OUTCOMES:
        fit = fe_ols(
            d,
            outcome,
            ["exposure_x_jan_to_jun2022", "exposure_x_post_jul2022"],
            fe,
            "facility_id",
        )
        for term in fit["x_cols"]:
            b = fit["beta"][term]
            se = fit["se"][term]
            rows.append(
                {
                    "outcome": outcome,
                    "term": term,
                    "estimate": b,
                    "std_error": se,
                    "ci_low": b - 1.96 * se,
                    "ci_high": b + 1.96 * se,
                    "p_value": fit["pval"][term],
                    "n_obs": fit["n"],
                    "n_facilities": fit["n_clusters"],
                    "fixed_effects": "+".join(fe),
                    "exposure": exposure,
                }
            )
    return rows


def event_study(panel: pd.DataFrame, outcome: str, exposure: str = "high_exposure_composite") -> tuple[pd.DataFrame, dict]:
    d = panel.copy()
    d["event_bin"] = d["rel_month_jan2022"].clip(lower=-24, upper=36)
    event_times = [k for k in range(-24, 37) if k != -1]
    x_cols = []
    for k in event_times:
        name = f"event_{k:+d}".replace("+", "p").replace("-", "m")
        d[name] = d[exposure] * (d["event_bin"] == k).astype(int)
        x_cols.append(name)
    fit = fe_ols(d, outcome, x_cols, ["facility_id", "period"], "facility_id")
    rows = []
    for k in event_times:
        name = f"event_{k:+d}".replace("+", "p").replace("-", "m")
        if name not in fit["x_cols"]:
            continue
        b = fit["beta"][name]
        se = fit["se"][name]
        rows.append(
            {
                "outcome": outcome,
                "event_time": k,
                "estimate": b,
                "std_error": se,
                "ci_low": b - 1.96 * se,
                "ci_high": b + 1.96 * se,
                "p_value": fit["pval"][name],
                "n_obs": fit["n"],
                "n_facilities": fit["n_clusters"],
            }
        )
    res = pd.DataFrame(rows)
    pre_names = [
        f"event_{k:+d}".replace("+", "p").replace("-", "m")
        for k in event_times
        if k < 0 and k != -1 and f"event_{k:+d}".replace("+", "p").replace("-", "m") in fit["x_cols"]
    ]
    if pre_names:
        b = fit["beta"].loc[pre_names].to_numpy()
        v = fit["vcov"].loc[pre_names, pre_names].to_numpy()
        wald = float(b.T @ np.linalg.pinv(v) @ b)
        pval = float(1 - stats.chi2.cdf(wald, len(pre_names)))
    else:
        wald, pval = np.nan, np.nan
    pretest = {
        "outcome": outcome,
        "test": "joint_pre_2022_event_coefficients_equal_zero",
        "wald_chi2": wald,
        "df": len(pre_names),
        "p_value": pval,
        "n_obs": fit["n"],
        "n_facilities": fit["n_clusters"],
    }
    return res, pretest


def plot_event(df: pd.DataFrame, outcome: str) -> None:
    d = df[df["outcome"] == outcome].sort_values("event_time")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(
        d["event_time"],
        d["estimate"],
        yerr=[d["estimate"] - d["ci_low"], d["ci_high"] - d["estimate"]],
        fmt="o",
        ms=3.5,
        color="#26547c",
        ecolor="#7f8fa6",
        capsize=2,
    )
    ax.axhline(0, color="black", linestyle="--", lw=1)
    ax.axvline(0, color="black", linestyle=":", lw=1)
    ax.axvline(6, color="gray", linestyle=":", lw=1.2)
    ax.set_xlabel("Months relative to January 2022")
    ax.set_ylabel("High exposure differential")
    ax.set_title(outcome.replace("_", " ").title())
    fig.tight_layout()
    fig.savefig(FIG / f"event_study_jan2022_{outcome}.png", dpi=300)
    fig.savefig(FIG / f"event_study_jan2022_{outcome}.pdf")
    plt.close(fig)


def plot_post_coefficients(results: pd.DataFrame) -> None:
    d = results[
        (results["fixed_effects"] == "facility_id+period")
        & (results["term"] == "exposure_x_post_jul2022")
        & results["outcome"].isin(MAIN_OUTCOMES)
    ].copy()
    d = d.sort_values("estimate")
    fig, ax = plt.subplots(figsize=(7, 5))
    y = np.arange(len(d))
    ax.errorbar(
        d["estimate"],
        y,
        xerr=[d["estimate"] - d["ci_low"], d["ci_high"] - d["estimate"]],
        fmt="o",
        color="#c23b22",
        ecolor="#b0b0b0",
        capsize=2,
    )
    ax.axvline(0, color="black", linestyle="--", lw=1)
    ax.set_yticks(y)
    ax.set_yticklabels(d["outcome"].str.replace("_", " ").str.title())
    ax.set_xlabel("High exposure x post-July 2022 coefficient")
    fig.tight_layout()
    fig.savefig(FIG / "main_post_july_coefficients.png", dpi=300)
    fig.savefig(FIG / "main_post_july_coefficients.pdf")
    plt.close(fig)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)

    panel = pd.read_parquet(DATA / "analysis_facility_month.parquet")
    panel = panel[panel["analysis_sample"] == 1].copy()
    panel["period_date"] = pd.to_datetime(panel["period_date"])
    # Keep a common window so event-study bins and post models share the same sample.
    panel = panel[(panel["period_date"] >= "2019-01-01") & (panel["period_date"] <= "2025-12-31")]

    rows = post_model_rows(panel, "high_exposure_composite", state_time=False)
    rows += post_model_rows(panel, "high_exposure_composite", state_time=True)
    main_results = pd.DataFrame(rows)
    save_table(main_results.round(5), TAB / "table2_main_panel_models")
    main_results.to_csv(RESULT / "main_model_results.csv", index=False)

    event_frames = []
    pretests = []
    for outcome in ["weekend_total_nurse_hprd", "weekend_rn_hprd", "weekday_total_nurse_hprd", "weekday_minus_weekend_total_hprd"]:
        es, pre = event_study(panel, outcome, "high_exposure_composite")
        event_frames.append(es)
        pretests.append(pre)
    event_df = pd.concat(event_frames, ignore_index=True)
    event_df.to_csv(RESULT / "main_eventstudy_coefficients.csv", index=False)
    pretest_df = pd.DataFrame(pretests)
    save_table(pretest_df.round(5), TAB / "pretrend_tests")

    for outcome in event_df["outcome"].unique():
        plot_event(event_df, outcome)
    plot_post_coefficients(main_results)

    with (TEMP / "audit_log.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 6 Main Models\n\n"
            f"- Estimated main facility-month panel models for {len(MAIN_OUTCOMES)} outcomes with facility and month fixed effects, plus a specification with facility and state-by-month fixed effects.\n"
            "- Estimated January 2022 event-study models with facility and month fixed effects and facility-clustered standard errors.\n"
            f"- Wrote main model results to `{(RESULT / 'main_model_results.csv').relative_to(ROOT)}` and event-study coefficients to `{(RESULT / 'main_eventstudy_coefficients.csv').relative_to(ROOT)}`.\n"
        )
    with (TEMP / "iteration_notes.md").open("a", encoding="utf-8") as f:
        worst_pre = pretest_df.sort_values("p_value").head(1)
        msg = ""
        if not worst_pre.empty:
            msg = f" Lowest pre-trend p-value is {worst_pre['p_value'].iloc[0]:.4f} for {worst_pre['outcome'].iloc[0]}."
        f.write(
            "\n## Phase 6: Main Models\n\n"
            "Main panel and event-study models were estimated using high pre-policy exposure interacted with January-June 2022 and post-July 2022 indicators, plus dynamic event-time interactions around January 2022. Standard errors are clustered by facility." + msg + "\n\n"
            "Self-question: Causal interpretation depends on acceptable pre-trends. The final go/no-go judgment must treat small or systematic pre-period event coefficients as a design weakness.\n"
        )

    print("Main models complete.")


if __name__ == "__main__":
    main()
