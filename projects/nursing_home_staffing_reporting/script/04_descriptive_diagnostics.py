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


BALANCE_VARS = [
    "baseline_weekend_total_hprd",
    "baseline_weekend_rn_hprd",
    "baseline_gap_total",
    "baseline_total_hprd",
    "baseline_rn_share",
    "baseline_contract_share",
    "certified_beds",
    "avg_residents_per_day",
    "overall_rating",
    "staffing_rating",
    "health_inspection_rating",
    "rating_cycle_1_total_health_deficiencies",
    "total_weighted_health_survey_score",
    "ownership_for_profit",
    "ownership_nonprofit",
    "ownership_government",
]

TREND_OUTCOMES = [
    "weekend_total_nurse_hprd",
    "weekend_rn_hprd",
    "weekday_total_nurse_hprd",
    "weekday_minus_weekend_total_hprd",
    "total_nurse_hprd",
    "rn_share_total_hours",
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


def balance_table(exposures: pd.DataFrame) -> pd.DataFrame:
    d = exposures.copy()
    rows = []
    for v in BALANCE_VARS:
        if v not in d.columns:
            continue
        g1 = pd.to_numeric(d.loc[d["high_exposure_composite"] == 1, v], errors="coerce")
        g0 = pd.to_numeric(d.loc[d["high_exposure_composite"] == 0, v], errors="coerce")
        if g1.notna().sum() == 0 or g0.notna().sum() == 0:
            continue
        diff = g1.mean() - g0.mean()
        pooled_sd = np.sqrt((g1.var(skipna=True) + g0.var(skipna=True)) / 2.0)
        smd = diff / pooled_sd if pooled_sd and np.isfinite(pooled_sd) else np.nan
        try:
            pval = stats.ttest_ind(g1.dropna(), g0.dropna(), equal_var=False).pvalue
        except Exception:
            pval = np.nan
        rows.append(
            {
                "variable": v,
                "high_exposure_mean": g1.mean(),
                "lower_exposure_mean": g0.mean(),
                "difference": diff,
                "smd": smd,
                "p_value": pval,
                "n_high": int(g1.notna().sum()),
                "n_lower": int(g0.notna().sum()),
            }
        )
    return pd.DataFrame(rows)


def save_trend_plot(df: pd.DataFrame, outcome: str) -> None:
    g = (
        df.groupby(["period_date", "high_exposure_composite"])[outcome]
        .mean()
        .reset_index()
        .pivot(index="period_date", columns="high_exposure_composite", values=outcome)
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if 0 in g.columns:
        ax.plot(g.index, g[0], label="Lower exposure", color="#26547c", lw=1.8)
    if 1 in g.columns:
        ax.plot(g.index, g[1], label="High exposure", color="#c23b22", lw=1.8)
    ax.axvline(pd.Timestamp("2022-01-01"), color="black", linestyle="--", lw=1, label="Jan 2022")
    ax.axvline(pd.Timestamp("2022-07-01"), color="gray", linestyle=":", lw=1.2, label="Jul 2022")
    ax.set_title(outcome.replace("_", " ").title())
    ax.set_xlabel("Month")
    ax.set_ylabel("Mean")
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / f"trend_{outcome}.png", dpi=300)
    fig.savefig(FIG / f"trend_{outcome}.pdf")
    plt.close(fig)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)

    panel = pd.read_parquet(DATA / "analysis_facility_month.parquet")
    exposures = pd.read_parquet(DATA / "facility_exposures.parquet")
    panel = panel[panel["analysis_sample"] == 1].copy()
    panel["period_date"] = pd.to_datetime(panel["period_date"])

    bal = balance_table(exposures[exposures["baseline_months"].ge(18)].copy())
    save_table(bal.round(4), TAB / "table1_balance_high_vs_lower_exposure")

    coverage = (
        panel.groupby("period")
        .agg(
            n_facilities=("facility_id", "nunique"),
            n_rows=("facility_id", "size"),
            mean_weekend_total_hprd=("weekend_total_nurse_hprd", "mean"),
            mean_weekend_rn_hprd=("weekend_rn_hprd", "mean"),
            missing_weekend_total_hprd=("weekend_total_nurse_hprd", lambda s: float(s.isna().mean())),
        )
        .reset_index()
    )
    save_table(coverage.round(4), TAB / "coverage_by_month")

    missing = []
    for c in TREND_OUTCOMES + ["baseline_weekend_total_hprd", "baseline_gap_total", "exposure_composite"]:
        if c in panel.columns:
            missing.append({"variable": c, "missing_share": float(panel[c].isna().mean())})
    save_table(pd.DataFrame(missing).round(4), TAB / "missingness_core_variables")

    exp = exposures[exposures["baseline_months"].ge(18)].copy()
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    plot_vars = [
        "baseline_weekend_total_hprd",
        "baseline_weekend_rn_hprd",
        "baseline_gap_total",
        "exposure_composite",
    ]
    for ax, v in zip(axes.flat, plot_vars):
        ax.hist(exp[v].dropna(), bins=40, color="#4c78a8", edgecolor="white")
        ax.axvline(exp[v].quantile(0.25), color="black", linestyle="--", lw=1)
        ax.axvline(exp[v].quantile(0.75), color="gray", linestyle=":", lw=1)
        ax.set_title(v.replace("_", " ").title())
    fig.tight_layout()
    fig.savefig(FIG / "exposure_distributions.png", dpi=300)
    fig.savefig(FIG / "exposure_distributions.pdf")
    plt.close(fig)

    for outcome in TREND_OUTCOMES:
        save_trend_plot(panel, outcome)

    pre = panel[panel["period_date"] < pd.Timestamp("2022-01-01")]
    pre_diff = (
        pre.groupby(["period_date", "high_exposure_composite"])["weekend_total_nurse_hprd"]
        .mean()
        .reset_index()
        .pivot(index="period_date", columns="high_exposure_composite", values="weekend_total_nurse_hprd")
    )
    if 0 in pre_diff.columns and 1 in pre_diff.columns:
        pre_diff["high_minus_lower"] = pre_diff[1] - pre_diff[0]
        pre_diff.reset_index().to_csv(TAB / "raw_pretrend_high_minus_lower_weekend_total.csv", index=False)
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(pre_diff.index, pre_diff["high_minus_lower"], color="#6f4e7c", lw=1.8)
        ax.axhline(0, color="black", linestyle="--", lw=1)
        ax.set_title("Pre-2022 Raw Difference: Weekend Total Nurse HPRD")
        ax.set_xlabel("Month")
        ax.set_ylabel("High exposure minus lower exposure")
        fig.tight_layout()
        fig.savefig(FIG / "raw_pretrend_high_minus_lower_weekend_total.png", dpi=300)
        fig.savefig(FIG / "raw_pretrend_high_minus_lower_weekend_total.pdf")
        plt.close(fig)

    with (TEMP / "audit_log.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 4 Descriptive Diagnostics\n\n"
            f"- Wrote balance, coverage, missingness, exposure distribution, and raw trend diagnostics to `{TAB.relative_to(ROOT)}` and `{FIG.relative_to(ROOT)}`.\n"
            f"- Analysis sample for descriptive diagnostics contains {panel['facility_id'].nunique():,} facilities and {len(panel):,} facility-month observations.\n"
        )
    with (TEMP / "iteration_notes.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 5: Exposure and Comparison Construction\n\n"
            "The preferred comparison is high exposure versus lower exposure, where high exposure is the top quartile of the pre-2022 composite index. Balance and raw trend diagnostics were exported before model estimation. The comparison group remains exposed to the national policy and is not described as untreated.\n\n"
            "Self-question: The most credible construction depends on pre-trends. Main models will test dynamic pre-policy coefficients and robustness will compare alternative exposure definitions.\n"
        )

    print("Descriptive diagnostics complete.")


if __name__ == "__main__":
    main()
