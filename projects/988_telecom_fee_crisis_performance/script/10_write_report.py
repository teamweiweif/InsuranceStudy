from __future__ import annotations

from pathlib import Path

import pandas as pd

from project_utils import DATA, REPORT, RESULT, TEMP, append_audit, read_parquet


SOURCE_LINKS = {
    "988 Lifeline State-based Monthly Reports": "https://988lifeline.org/professionals/our-network/state-based-monthly-reports/",
    "SAMHSA 988 Performance Metrics": "https://www.samhsa.gov/mental-health/988/performance-metrics",
    "FCC 988 Fee Reports and Reporting": "https://www.fcc.gov/988-fee-reports-and-reporting",
    "Census state resident population estimates": "https://www.census.gov/data/tables/time-series/demo/popest/2020s-state-total.html",
}


def fmt_num(x, digits: int = 3) -> str:
    if pd.isna(x):
        return "NA"
    return f"{float(x):.{digits}f}"


def fmt_pct_point(x) -> str:
    if pd.isna(x):
        return "NA"
    return f"{float(x) * 100:.2f} pp"


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_readme(panel_summary: pd.DataFrame) -> None:
    metrics = dict(zip(panel_summary["metric"], panel_summary["value"]))
    source_lines = "\n".join(f"- [{name}]({url})" for name, url in SOURCE_LINKS.items())
    text = f"""# 988 Telecom Fee Crisis-Line Performance

This workspace evaluates whether state 988 telecom fee funding is associated with improved 988 crisis-line performance using official state-month KPI PDFs, FCC 988 fee accountability reports, and Census denominators.

## Reproduce

From this folder:

```powershell
powershell -ExecutionPolicy Bypass -File script/run_all.ps1
```

Or run the Python scripts in order from `script/00_setup.py` through `script/10_write_report.py`.

## Current Data Coverage

- KPI source months parsed: {metrics.get("months")} monthly PDFs, {metrics.get("earliest_month")} through {metrics.get("latest_month")}. The source index snapshot did not list February 2025.
- Jurisdictions in raw KPI panel: {metrics.get("states_or_jurisdictions")}.
- Primary state/DC sample rows: {metrics.get("primary_sample_rows")} across {metrics.get("primary_sample_states")} jurisdictions.
- FCC-confirmed state fee collectors by calendar 2024: {metrics.get("fcc_confirmed_fee_states_by_2024")}.

## Official Sources

{source_lines}

## Key Outputs

- `data/analysis_panel_state_month.parquet`: merged analysis panel.
- `data/treatment_timing_state.csv`: policy timing audit.
- `result/main_twfe_models.csv`: fixed-effect treatment checks.
- `result/cs_overall_att.csv`: not-yet-treated cohort ATT estimates.
- `report/final_report.md`: empirical write-up.
- `report/go_no_go_assessment.md`: decision assessment.
"""
    (REPORT / "README.md").write_text(text, encoding="utf-8")


def write_policy_timeline(timing: pd.DataFrame, revenue: pd.DataFrame) -> None:
    policy = timing[timing["primary_policy_group"].ne("never_or_no_fee_reported")].copy()
    for col in ["actual_collection_start", "operational_start"]:
        policy[col] = pd.to_datetime(policy[col], errors="coerce").dt.strftime("%Y-%m-%d").fillna("")
    policy = policy[
        [
            "state",
            "state_name",
            "primary_policy_group",
            "actual_collection_start",
            "operational_start",
            "date_confidence",
            "policy_note",
        ]
    ]
    rev = revenue.copy()
    rev["fee_revenue_nominal"] = rev["fee_revenue_nominal"].map(lambda x: f"${x:,.0f}" if pd.notna(x) else "")
    text = "# Policy Timeline\n\n"
    text += "Treatment timing separates observed collection starts from the preferred operational timing, which lags collection by three months.\n\n"
    text += markdown_table(policy) + "\n\n"
    text += "## FCC Annual Fee Revenue\n\n"
    text += markdown_table(rev[["state", "year", "fee_revenue_nominal", "source_id", "revenue_note"]]) + "\n"
    (REPORT / "policy_timeline.md").write_text(text, encoding="utf-8")


def write_data_dictionary() -> None:
    files = [
        DATA / "outcomes_988_state_month.parquet",
        DATA / "treatment_timing_state.parquet",
        DATA / "fee_schedule_state_month.parquet",
        DATA / "state_population_state_year.parquet",
        DATA / "covariates_state_month.parquet",
        DATA / "mechanism_state_year.parquet",
        DATA / "analysis_panel_state_month.parquet",
    ]
    parts = ["# Data Dictionary\n"]
    for path in files:
        df = read_parquet(path)
        cols = pd.DataFrame({"column": df.columns, "dtype": [str(df[c].dtype) for c in df.columns]})
        parts.append(f"## {path.name}\n")
        parts.append(markdown_table(cols))
        parts.append("")
    (REPORT / "data_dictionary.md").write_text("\n".join(parts), encoding="utf-8")


def write_identification_audit(cs: pd.DataFrame, twfe: pd.DataFrame, placebo: pd.DataFrame) -> None:
    ans = cs[cs["outcome"].eq("in_state_answer_rate")].iloc[0]
    tw = twfe[
        twfe["outcome"].eq("in_state_answer_rate") & twfe["model"].eq("twfe_operational_start")
    ].iloc[0]
    p_placebo = placebo["placebo_abs_p_value"].iloc[0] if not placebo.empty else pd.NA
    text = f"""# Identification Audit

## Target Parameter

The preferred estimand is the average post-operational-start change in state 988 KPI performance for states that adopted telecom fee funding, compared with not-yet-treated or never-treated state/DC controls.

## Treatment

The primary treatment is FCC-confirmed state 988 telecom fee collection. The preferred operational start is three months after fee collection starts. Actual collection and operational timing are both retained in `data/fee_schedule_state_month.csv`.

## Estimators

- Not-yet-treated cohort/event-time ATT: preferred descriptive causal design for staggered adoption.
- TWFE with state and month fixed effects: diagnostic check, not the headline design.
- Dose-response models: fee cents and FCC-observed annual revenue intensity for 2021-2024.
- Robustness: launch-transition exclusion, early-adopter exclusion, leave-one-treated-state-out, placebo timing.

## Core Diagnostic Facts

- Not-yet-treated answer-rate ATT: {fmt_pct_point(ans["overall_att"])}; bootstrap 95% interval [{fmt_pct_point(ans["bootstrap_ci_low"])}, {fmt_pct_point(ans["bootstrap_ci_high"])}].
- TWFE operational-start answer-rate coefficient: {fmt_pct_point(tw["estimate"])}; clustered SE {fmt_pct_point(tw["std_error_cluster"])}; p={fmt_num(tw["p_value"], 3)}.
- Placebo timing p-value for the TWFE answer-rate coefficient: {fmt_num(p_placebo, 3)}.

## Main Threats

- Fee adoption is not random; high-need or better-organized states may adopt earlier.
- Public monthly staffing/capacity measures are incomplete, so the funding-to-capacity mechanism is proxied by fee revenue and baseline load.
- Nationwide 988 launch and later routing/georouting changes are absorbed by month fixed effects but may have heterogeneous state impacts.
- Treatment timing after 2024 is less well observed because the latest FCC annual fee report covers calendar year 2024.
- February 2025 was absent from the 988 source index snapshot used here.

## Bottom Line

The cohort ATT estimates are policy-relevant and point toward better in-state performance after fee funding, but the TWFE and placebo diagnostics do not support a strong standalone causal headline.
"""
    (REPORT / "identification_audit.md").write_text(text, encoding="utf-8")


def write_mechanism_chain(chain: pd.DataFrame, dose: pd.DataFrame) -> None:
    display = chain.copy()
    for col in ["actual_collection_start", "operational_start"]:
        display[col] = pd.to_datetime(display[col], errors="coerce").dt.strftime("%Y-%m-%d")
    for col in [
        "observed_fee_revenue_total_2021_2024",
        "max_observed_fee_revenue_per_capita",
        "pre_answer_rate",
        "post_answer_rate",
        "delta_answer_rate",
        "delta_flowout_rate",
        "delta_asa_seconds",
    ]:
        display[col] = display[col].map(lambda x: fmt_num(x, 3))
    text = "# Mechanism Chain\n\n"
    text += "The observable mechanism is fee funding intensity. Public state-month staffing/capacity data were not available from a consistent official source, so capacity is not directly estimated.\n\n"
    text += markdown_table(
        display[
            [
                "state",
                "actual_collection_start",
                "operational_start",
                "observed_fee_revenue_total_2021_2024",
                "max_observed_fee_revenue_per_capita",
                "delta_answer_rate",
                "delta_flowout_rate",
                "delta_asa_seconds",
            ]
        ]
    )
    text += "\n\n## Revenue-Intensity Model Rows\n\n"
    slim = dose[["outcome", "term", "estimate", "std_error_cluster", "p_value"]].copy()
    for col in ["estimate", "std_error_cluster", "p_value"]:
        slim[col] = slim[col].map(lambda x: fmt_num(x, 4))
    text += markdown_table(slim)
    (REPORT / "mechanism_chain.md").write_text(text, encoding="utf-8")


def write_final_report(
    panel_summary: pd.DataFrame,
    table1: pd.DataFrame,
    cs: pd.DataFrame,
    twfe: pd.DataFrame,
    robust: pd.DataFrame,
    placebo: pd.DataFrame,
) -> None:
    metrics = dict(zip(panel_summary["metric"], panel_summary["value"]))
    ans = cs[cs["outcome"].eq("in_state_answer_rate")].iloc[0]
    flo = cs[cs["outcome"].eq("flowout_to_national_backup_rate")].iloc[0]
    abd = cs[cs["outcome"].eq("abandoned_in_state_rate")].iloc[0]
    asa = cs[cs["outcome"].eq("average_speed_to_answer_seconds")].iloc[0]
    tw_ans = twfe[
        twfe["outcome"].eq("in_state_answer_rate") & twfe["model"].eq("twfe_operational_start")
    ].iloc[0]
    tw_asa = twfe[
        twfe["outcome"].eq("average_speed_to_answer_seconds") & twfe["model"].eq("twfe_operational_start")
    ].iloc[0]
    placebo_p = placebo["placebo_abs_p_value"].iloc[0] if not placebo.empty else pd.NA

    robust_ans = robust[
        robust["outcome"].eq("in_state_answer_rate") & robust["model"].isin(["drop_early_adopters_va_wa", "through_2024_only", "include_post2025_monitor_rows"])
    ][["model", "estimate", "std_error_cluster", "p_value"]].copy()
    for col in ["estimate", "std_error_cluster"]:
        robust_ans[col] = robust_ans[col].map(fmt_pct_point)
    robust_ans["p_value"] = robust_ans["p_value"].map(lambda x: fmt_num(x, 3))

    text = f"""# Do 988 Telecom Fees Improve Crisis-Line Performance?

## Summary

This audit builds a reproducible state-month panel from official 988 Lifeline KPI PDFs and FCC 988 fee accountability reports. The analysis covers {metrics.get("months")} source months from {metrics.get("earliest_month")} through {metrics.get("latest_month")} and uses a primary state/DC sample of {metrics.get("primary_sample_rows")} rows.

The evidence is mixed. The preferred not-yet-treated cohort comparison suggests improvements after fee funding: answer rates rise by {fmt_pct_point(ans["overall_att"])} with a bootstrap interval of [{fmt_pct_point(ans["bootstrap_ci_low"])}, {fmt_pct_point(ans["bootstrap_ci_high"])}], flowout falls by {fmt_pct_point(flo["overall_att"])}, and abandonment falls by {fmt_pct_point(abd["overall_att"])}. Average speed to answer improves by {fmt_num(asa["overall_att"], 2)} seconds, but its interval includes zero.

The simpler TWFE diagnostic is much weaker: the operational-start answer-rate coefficient is {fmt_pct_point(tw_ans["estimate"])} with clustered SE {fmt_pct_point(tw_ans["std_error_cluster"])} and p={fmt_num(tw_ans["p_value"], 3)}. A placebo timing exercise for that TWFE coefficient has empirical p={fmt_num(placebo_p, 3)}.

## Data

The outcome panel is parsed from official 988 Lifeline state-based monthly reports. Outcomes include in-state routed contacts, answered contacts, answer rate, abandoned contacts, flowout to national backup, speed to answer, and talk time. Treatment timing comes from FCC annual 988 fee reports and official state policy sources. Population denominators come from Census Vintage 2025 state resident population estimates.

## Empirical Strategy

The preferred design compares treated cohorts with not-yet-treated or never-treated states around each operational treatment start. Operational start is coded three months after fee collection begins. The fixed-effect checks include state and month fixed effects with state-clustered standard errors.

## Main Results

| Outcome | Not-yet-treated ATT | Bootstrap 95% interval |
| --- | --- | --- |
| In-state answer rate | {fmt_pct_point(ans["overall_att"])} | [{fmt_pct_point(ans["bootstrap_ci_low"])}, {fmt_pct_point(ans["bootstrap_ci_high"])}] |
| Flowout to national backup | {fmt_pct_point(flo["overall_att"])} | [{fmt_pct_point(flo["bootstrap_ci_low"])}, {fmt_pct_point(flo["bootstrap_ci_high"])}] |
| Abandoned rate | {fmt_pct_point(abd["overall_att"])} | [{fmt_pct_point(abd["bootstrap_ci_low"])}, {fmt_pct_point(abd["bootstrap_ci_high"])}] |
| Average speed to answer | {fmt_num(asa["overall_att"], 2)} sec | [{fmt_num(asa["bootstrap_ci_low"], 2)}, {fmt_num(asa["bootstrap_ci_high"], 2)}] sec |

## Robustness Snapshot

{markdown_table(robust_ans)}

## Interpretation

The cohort design points toward operationally meaningful improvements after fee adoption, especially higher in-state answer rates and lower flowout. However, the diagnostic TWFE estimates are small and statistically weak, and placebo timing does not reject chance timing patterns for that specification. The safest claim is that fee-funded states improved relative to not-yet-treated comparisons in the preferred event-time design, not that telecom fees are conclusively causal on their own.

## Limitations

- Fee adoption is policy-selected, not randomized.
- Public monthly staffing/capacity data are incomplete, limiting mechanism tests.
- The 988 source index did not include February 2025 in the snapshot used here.
- Post-2024 policy changes are not fully covered by FCC annual fee revenue reports.
- Manual validation sample rows remain marked for human audit in `temp/pdf_extraction_checks/validation_sample.csv`.
"""
    (REPORT / "final_report.md").write_text(text, encoding="utf-8")


def write_go_no_go(cs: pd.DataFrame, twfe: pd.DataFrame, placebo: pd.DataFrame) -> None:
    ans = cs[cs["outcome"].eq("in_state_answer_rate")].iloc[0]
    tw_ans = twfe[
        twfe["outcome"].eq("in_state_answer_rate") & twfe["model"].eq("twfe_operational_start")
    ].iloc[0]
    placebo_p = placebo["placebo_abs_p_value"].iloc[0] if not placebo.empty else pd.NA
    decision = "CONDITIONAL GO for an exploratory/policy-audit paper; NO-GO for a strong causal headline."
    text = f"""# Go/No-Go Assessment

## Decision

{decision}

## Rationale

- Data acquisition and reproducibility: GO. The workspace downloads official sources, parses PDFs, builds analysis panels, and regenerates reports.
- Policy timing audit: GO with documented assumptions. Actual collection and operational timing are separate.
- Preferred cohort ATT evidence: GO with caution. Answer-rate ATT is {fmt_pct_point(ans["overall_att"])} with bootstrap interval [{fmt_pct_point(ans["bootstrap_ci_low"])}, {fmt_pct_point(ans["bootstrap_ci_high"])}].
- TWFE/placebo diagnostics: CAUTION. TWFE answer-rate coefficient is {fmt_pct_point(tw_ans["estimate"])} with p={fmt_num(tw_ans["p_value"], 3)}; placebo timing p={fmt_num(placebo_p, 3)}.
- Mechanism evidence: CAUTION. Fee revenue is observed, but staffing/capacity is not measured consistently in public monthly data.

## Recommended Claim

States adopting 988 telecom fee funding show improved in-state performance in not-yet-treated event-time comparisons, but the current evidence should be framed as suggestive rather than definitive causal proof.

## Next Validation Steps

- Manually verify the sampled PDF extraction rows.
- Add official state response appendices if FCC releases machine-readable submissions.
- Add direct staffing/capacity measures if a consistent public source becomes available.
- Re-estimate after the next FCC annual fee report covers 2025 revenue.
"""
    (REPORT / "go_no_go_assessment.md").write_text(text, encoding="utf-8")


def main() -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    panel_summary = pd.read_csv(RESULT / "analysis_panel_summary.csv")
    timing = read_parquet(DATA / "treatment_timing_state.parquet")
    revenue = read_parquet(DATA / "fcc_annual_fee_revenue_state_year.parquet")
    table1 = pd.read_csv(RESULT / "table1_baseline_balance.csv")
    cs = pd.read_csv(RESULT / "cs_overall_att.csv")
    twfe = pd.read_csv(RESULT / "main_twfe_models.csv")
    robust = pd.read_csv(RESULT / "robustness_summary.csv")
    placebo = pd.read_csv(RESULT / "placebo_timing_summary.csv") if (RESULT / "placebo_timing_summary.csv").exists() else pd.DataFrame()
    chain = pd.read_csv(RESULT / "mechanism_chain_table.csv")
    dose = pd.read_csv(RESULT / "mechanism_revenue_intensity_models.csv")

    write_readme(panel_summary)
    write_policy_timeline(timing, revenue)
    write_data_dictionary()
    write_identification_audit(cs, twfe, placebo)
    write_mechanism_chain(chain, dose)
    write_final_report(panel_summary, table1, cs, twfe, robust, placebo)
    write_go_no_go(cs, twfe, placebo)

    (TEMP / "rejected_designs.md").write_text(
        "# Rejected Designs\n\n"
        "- Naive post-only treated-versus-control comparison: rejected because treated states differ in baseline demand and performance.\n"
        "- Single TWFE coefficient as headline estimate: rejected because staggered timing can induce misleading weights and the diagnostic estimate is weak.\n"
        "- Treating all 2025 policy mentions as fee treatment: rejected because FCC annual revenue data only cover calendar year 2024 and some 2025 laws are not clearly telecom fee collection starts.\n"
        "- Direct staffing mechanism model: rejected for now because no consistent official state-month staffing panel was found.\n",
        encoding="utf-8",
    )
    append_audit("Regenerated final reports and go/no-go assessment from result tables.")


if __name__ == "__main__":
    main()

