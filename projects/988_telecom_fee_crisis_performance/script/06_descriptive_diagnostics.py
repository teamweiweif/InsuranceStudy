from __future__ import annotations

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from project_utils import DATA, PDF_CHECKS, REPORT, RESULT, append_audit, read_parquet, save_csv


OUTCOMES = [
    "in_state_answer_rate",
    "flowout_to_national_backup_rate",
    "abandoned_in_state_rate",
    "average_speed_to_answer_seconds",
    "routed_per_100k",
]


def save_figure(fig: plt.Figure, stem: str) -> None:
    RESULT.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULT / f"{stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(RESULT / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def build_table1(panel: pd.DataFrame) -> pd.DataFrame:
    baseline = panel[
        panel["primary_analysis_sample"]
        & panel["month"].between(pd.Timestamp("2021-07-01"), pd.Timestamp("2022-06-01"))
    ].copy()
    baseline["group"] = baseline["treated_ever_by_2024"].map({True: "Fee states by 2024", False: "No fee by 2024"})
    rows = []
    for group, g in baseline.groupby("group"):
        rows.append(
            {
                "group": group,
                "states": g["state"].nunique(),
                "state_months": len(g),
                "answer_rate_mean": g["in_state_answer_rate"].mean(),
                "flowout_rate_mean": g["flowout_to_national_backup_rate"].mean(),
                "abandoned_rate_mean": g["abandoned_in_state_rate"].mean(),
                "asa_seconds_mean": g["average_speed_to_answer_seconds"].mean(),
                "routed_per_100k_mean": g["routed_per_100k"].mean(),
            }
        )
    out = pd.DataFrame(rows)
    numeric = out.select_dtypes("number").columns
    out[numeric] = out[numeric].round(4)
    return out


def plot_outcome_trends(panel: pd.DataFrame) -> None:
    work = panel[panel["primary_analysis_sample"]].copy()
    work["group"] = work["treated_ever_by_2024"].map({True: "Fee states by 2024", False: "No fee by 2024"})
    trend = (
        work.groupby(["month", "group"], as_index=False)
        .agg(
            answer_rate=("in_state_answer_rate", "mean"),
            flowout_rate=("flowout_to_national_backup_rate", "mean"),
            asa_seconds=("average_speed_to_answer_seconds", "mean"),
            routed_per_100k=("routed_per_100k", "mean"),
        )
    )
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
    specs = [
        ("answer_rate", "In-state answer rate"),
        ("flowout_rate", "Flowout to national backup rate"),
        ("asa_seconds", "Average speed to answer (seconds)"),
        ("routed_per_100k", "Routed contacts per 100,000"),
    ]
    for ax, (col, title) in zip(axes.flat, specs):
        sns.lineplot(data=trend, x="month", y=col, hue="group", ax=ax, linewidth=1.8)
        ax.set_title(title)
        ax.set_xlabel("")
        ax.grid(alpha=0.25)
        ax.legend_.set_title("")
    for ax in axes[-1, :]:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.suptitle("988 KPI Trends by Fee-Adoption Status", y=1.02, fontsize=13)
    save_figure(fig, "fig_outcome_trends_by_fee_status")


def plot_policy_rollout(timing: pd.DataFrame) -> None:
    treated = timing[timing["actual_collection_start"].notna()].sort_values("actual_collection_start").copy()
    fig, ax = plt.subplots(figsize=(10, 4.8))
    y = range(len(treated))
    ax.scatter(treated["actual_collection_start"], y, label="Collection start", s=55)
    ax.scatter(treated["operational_start"], y, label="Operational timing (+3 months)", marker="s", s=45)
    for yi, (_, row) in zip(y, treated.iterrows()):
        ax.plot([row["actual_collection_start"], row["operational_start"]], [yi, yi], color="0.65", linewidth=1)
    ax.set_yticks(list(y))
    ax.set_yticklabels(treated["state"])
    ax.set_title("988 Telecom Fee Timing")
    ax.set_xlabel("")
    ax.grid(axis="x", alpha=0.25)
    ax.legend()
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save_figure(fig, "fig_policy_rollout")


def plot_pdf_coverage() -> None:
    cov = pd.read_csv(PDF_CHECKS / "coverage_by_month.csv")
    cov["month"] = pd.to_datetime(cov["year_month"] + "-01")
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(cov["month"], cov["states"], marker="o", linewidth=1.5)
    ax.set_title("Parsed Jurisdiction Coverage by Monthly KPI PDF")
    ax.set_ylabel("Jurisdictions parsed")
    ax.grid(alpha=0.25)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save_figure(fig, "fig_pdf_parse_coverage")


def plot_revenue(revenue: pd.DataFrame) -> None:
    work = revenue[revenue["fee_revenue_nominal"].gt(0)].copy()
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(data=work, x="state", y="fee_revenue_nominal", hue="year", ax=ax)
    ax.set_title("FCC-Reported Annual 988 Fee Revenue")
    ax.set_ylabel("Nominal dollars")
    ax.set_xlabel("")
    ax.grid(axis="y", alpha=0.25)
    save_figure(fig, "fig_fcc_fee_revenue")


def main() -> None:
    panel = read_parquet(DATA / "analysis_panel_state_month.parquet")
    timing = read_parquet(DATA / "treatment_timing_state.parquet")
    revenue = read_parquet(DATA / "fcc_annual_fee_revenue_state_year.parquet")

    table1 = build_table1(panel)
    save_csv(table1, RESULT / "table1_baseline_balance.csv")
    (REPORT / "table1_baseline_balance.md").write_text(
        "# Baseline Balance\n\n"
        "Baseline window: July 2021 through June 2022, before nationwide 988 launch.\n\n"
        + markdown_table(table1)
        + "\n",
        encoding="utf-8",
    )
    plot_outcome_trends(panel)
    plot_policy_rollout(timing)
    plot_pdf_coverage()
    plot_revenue(revenue)

    append_audit("Wrote baseline balance table and descriptive diagnostics figures to result/.")


if __name__ == "__main__":
    main()

