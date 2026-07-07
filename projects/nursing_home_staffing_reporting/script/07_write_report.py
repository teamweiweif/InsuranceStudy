from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULT = ROOT / "result"
REPORT = ROOT / "report"
TEMP = ROOT / "temp"


POLICY_LINKS = {
    "qso": "https://www.cms.gov/files/document/qso-22-08-nh.pdf",
    "july_fact_sheet": "https://www.cms.gov/newsroom/fact-sheets/updates-care-compare-website-july-2022",
    "july_press": "https://www.cms.gov/newsroom/press-releases/cms-enhances-nursing-home-rating-system-staffing-turnover-data",
    "cms_data": "https://data.cms.gov/",
    "pdc_archive": "https://data.cms.gov/provider-data/archived-data/nursing-homes",
    "minimum_staffing_2024": "https://www.cms.gov/newsroom/fact-sheets/medicare-and-medicaid-programs-minimum-staffing-standards-long-term-care-facilities-and-medicaid-0",
    "oig_2020": "https://oig.hhs.gov/reports/all/2020/some-nursing-homes-reported-staffing-levels-in-2018-raise-concerns-consumer-transparency-could-be-increased/",
    "oig_2021": "https://oig.hhs.gov/reports/all/2021/cms-use-of-data-on-nursing-home-staffing-progress-and-opportunities-to-do-more/",
}


def fmt(x: float, digits: int = 3) -> str:
    if x is None or pd.isna(x):
        return "NA"
    return f"{x:.{digits}f}"


def read_csv_if(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def main_line(main: pd.DataFrame, outcome: str, term: str = "exposure_x_post_jul2022") -> str:
    if main.empty:
        return "Model output unavailable."
    d = main[
        (main["outcome"] == outcome)
        & (main["term"] == term)
        & (main["fixed_effects"] == "facility_id+period")
    ]
    if d.empty:
        return f"No estimate available for {outcome}."
    r = d.iloc[0]
    return (
        f"{outcome}: beta={fmt(r['estimate'])}, SE={fmt(r['std_error'])}, "
        f"95% CI [{fmt(r['ci_low'])}, {fmt(r['ci_high'])}], p={fmt(r['p_value'])}, "
        f"N={int(r['n_obs']):,}."
    )


def go_no_go(main: pd.DataFrame, pre: pd.DataFrame, robust: pd.DataFrame) -> tuple[str, str]:
    reasons = []
    status = "provisional_go"

    primary_pre = pre[pre["outcome"].isin(["weekend_total_nurse_hprd", "weekend_rn_hprd"])]
    if not primary_pre.empty and (primary_pre["p_value"] < 0.05).any():
        status = "weak_design"
        reasons.append("At least one primary staffing outcome rejects the joint pre-trend null at the 5% level.")
    elif not primary_pre.empty and (primary_pre["p_value"] < 0.10).any():
        status = "caution"
        reasons.append("At least one primary staffing outcome has a marginal pre-trend test.")
    else:
        reasons.append("Primary pre-trend tests do not reject at conventional levels.")

    main_primary = main[
        (main["fixed_effects"] == "facility_id+period")
        & (main["term"] == "exposure_x_post_jul2022")
        & (main["outcome"].isin(["weekend_total_nurse_hprd", "weekend_rn_hprd"]))
    ]
    if main_primary.empty:
        status = "weak_design"
        reasons.append("Primary post-July estimates are missing.")
    elif (main_primary["ci_low"] <= 0).all() and (main_primary["ci_high"] >= 0).all():
        if status == "provisional_go":
            status = "caution"
        reasons.append("Primary post-July confidence intervals include zero.")
    else:
        reasons.append("At least one primary post-July staffing estimate excludes zero.")

    placebo = robust[(robust["check"] == "placebo_2021_timing") & robust["term"].str.contains("post", na=False)]
    if not placebo.empty and (placebo["p_value"] < 0.05).any():
        status = "weak_design"
        reasons.append("A placebo 2021 timing test is statistically significant, which weakens causal interpretation.")
    elif not placebo.empty:
        reasons.append("Placebo 2021 timing tests do not show strong evidence of false effects.")
    else:
        reasons.append("Placebo timing results are unavailable.")

    label = {
        "provisional_go": "Provisional go for a staffing-behavior paper",
        "caution": "Proceed with caution",
        "weak_design": "Weak causal design under current specification",
    }[status]
    return label, " ".join(reasons)


def write_readme() -> None:
    text = f"""# Nursing Home Staffing Reporting Project

This workspace builds a reproducible empirical pipeline for:

**Transparency or Labeling? The Effect of CMS Weekend Staffing and Turnover Reporting on U.S. Nursing Homes.**

## Reproduction

From the project root, run:

```bash
bash script/run_all.sh
```

Equivalent Python sequence:

```bash
python script/00_setup.py
python script/01_acquire_sources.py
python script/02_build_analysis_data.py
python script/03_construct_exposures_outcomes.py
python script/04_descriptive_diagnostics.py
python script/05_main_models.py
python script/06_robustness.py
python script/07_write_report.py
```

The PBJ daily nurse staffing files are streamed from official CMS CSV URLs recorded in `temp/pbj_daily_sources.csv`. Provider Data Catalog nursing-home archive ZIPs are cached under `temp/raw_downloads/provider_archives/`.

## Directory Map

- `data/`: clean analysis-ready Parquet and CSV extracts.
- `script/`: reusable reproduction scripts.
- `result/`: tables, figures, model outputs, diagnostics.
- `report/`: clean human-readable documentation and final report.
- `temp/`: raw downloads, source snapshots, manifests, audit logs, and iteration notes.

## Official Source Families

- CMS Payroll Based Journal Daily Nurse Staffing: {POLICY_LINKS['cms_data']}
- CMS Provider Data Catalog nursing-home archive: {POLICY_LINKS['pdc_archive']}
- CMS QSO-22-08-NH policy memo: {POLICY_LINKS['qso']}
- CMS July 2022 Care Compare/Five-Star updates: {POLICY_LINKS['july_fact_sheet']}

## Notes

The lower-exposure group is not untreated. All Medicare/Medicaid-certified nursing homes were exposed to the national 2022 reporting regime; identification comes from differential exposure intensity measured before 2022.
"""
    (REPORT / "README.md").write_text(text, encoding="utf-8")


def write_policy_timeline() -> None:
    text = f"""# Policy Timeline

## Main Exposure

**January 2022: Care Compare transparency shock.** CMS QSO-22-08-NH announced that CMS would begin posting weekend staffing levels and staff turnover information on Care Compare in the January 2022 refresh. This is the first public-reporting shock for the project. Source: {POLICY_LINKS['qso']}.

**July 27, 2022: Five-Star rating shock.** CMS announced updates to Care Compare and the Five-Star Quality Rating System that incorporated weekend staffing and staff turnover measures into nursing-home staffing ratings. This is the second, rating-salience shock. Sources: {POLICY_LINKS['july_fact_sheet']} and {POLICY_LINKS['july_press']}.

## Later Context, Not Main Exposure

**April 2024: federal minimum staffing final rule.** CMS finalized minimum nurse staffing standards for long-term care facilities. This occurs after the 2022 transparency/rating shocks and is treated as later context, not the main exposure. Source: {POLICY_LINKS['minimum_staffing_2024']}.

## Policy-Salience Documentation

HHS OIG reports before and after the 2022 updates document concerns about nursing-home staffing transparency and CMS use of PBJ staffing data. These reports support policy salience but are not primary outcome data. Sources: {POLICY_LINKS['oig_2020']} and {POLICY_LINKS['oig_2021']}.
"""
    (REPORT / "policy_timeline.md").write_text(text, encoding="utf-8")


def write_identification(main: pd.DataFrame, pre: pd.DataFrame, robust: pd.DataFrame) -> tuple[str, str]:
    label, reason = go_no_go(main, pre, robust)
    if pre.empty:
        pre_md = "No pretrend tests available."
    else:
        try:
            pre_md = pre.to_markdown(index=False)
        except Exception:
            pre_md = "```\n" + pre.to_csv(index=False) + "```"
    text = f"""# Identification Audit

## Strategy

The policy is national, so the design does not compare treated facilities with untreated facilities. It compares facilities with higher pre-policy exposure to the reporting and rating measures against lower-exposure comparison facilities under the same national reform.

The preferred model is:

`Y_it = facility FE + time FE + high_exposure_i x Jan-Jun 2022 + high_exposure_i x post-Jul 2022 + error_it`

The event-study version replaces the post indicators with high-exposure interactions for monthly event time around January 2022. Standard errors are clustered at the facility level.

## Exposure

The preferred exposure is the top quartile of a pre-2022 composite index combining:

- low baseline weekend total nurse HPRD;
- low baseline weekend RN HPRD;
- high baseline weekday-minus-weekend total nurse staffing gap.

All components use PBJ staffing records from January 2019 through December 2021.

## Assumptions

- Higher- and lower-exposure facilities would have followed parallel trends in the absence of the 2022 reporting/rating changes.
- Pre-2022 exposure is not mechanically constructed from post-2022 outcomes.
- Facility exits and missing reports do not differentially create the estimated post-2022 divergence.
- No other contemporaneous policy shock differentially affects high-exposure facilities exactly through the same timing and outcome channels.

## Threats

- COVID-era staffing shocks could create nonparallel pre-trends or change baseline exposure measurement.
- Facilities may strategically reallocate staffing from weekdays to weekends rather than increase total staffing.
- Ratings and deficiencies are downstream and partly endogenous to survey timing, so they should not be overinterpreted as resident health effects.
- Provider Data Catalog turnover fields are not consistently available before the January 2022 reporting change, so turnover exposure is documented but not preferred for the January transparency design.

## Pre-Trend Tests

{pre_md}

## Go/No-Go

**{label}.** {reason}
"""
    (REPORT / "identification_audit.md").write_text(text, encoding="utf-8")
    return label, reason


def write_final_report(main: pd.DataFrame, pre: pd.DataFrame, robust: pd.DataFrame) -> None:
    label, reason = go_no_go(main, pre, robust)
    panel = pd.read_parquet(DATA / "analysis_facility_month.parquet")
    panel = panel[panel["analysis_sample"] == 1]
    facilities = panel["facility_id"].nunique()
    months = panel["period"].nunique()
    rows = len(panel)

    lines = [
        "# Final Report",
        "",
        "## Executive Summary",
        "",
        f"This project estimates whether CMS's 2022 public reporting and Five-Star rating inclusion of weekend staffing and staff turnover changed nursing-home staffing behavior. The analysis uses {rows:,} facility-month observations from {facilities:,} facilities over {months} months. The preferred design compares facilities with high pre-2022 weekend-staffing exposure to lower-exposure facilities, with facility and month fixed effects. The current empirical judgment is: **{label}**. {reason}",
        "",
        "## Policy Background",
        "",
        "CMS began public reporting of weekend staffing and staff turnover information on Care Compare in January 2022. In July 2022, CMS incorporated weekend staffing and turnover measures into the Five-Star staffing-domain methodology. The 2024 minimum staffing rule is later context, not the exposure studied here.",
        "",
        "## Data Sources and Coverage",
        "",
        "- PBJ Daily Nurse Staffing provides facility-day staffing hours and resident census. The pipeline aggregates these data to facility-month and facility-quarter panels from 2019 Q1 through 2025 Q4.",
        "- Provider Data Catalog nursing-home archive snapshots provide facility characteristics, ratings, survey outcomes, penalties, and reported turnover/weekend staffing fields when available.",
        "- HHS OIG reports are used only as policy-salience documentation.",
        "",
        "## Outcomes",
        "",
        "Primary outcomes are weekend total nurse HPRD, weekend RN HPRD, weekday counterparts, weekend-weekday gaps, total nurse HPRD, RN share, and contract staff share. Ratings and deficiencies are secondary downstream outcomes.",
        "",
        "## Exposure and Comparison",
        "",
        "High exposure is the top quartile of a pre-2022 composite index based on low weekend total nurse HPRD, low weekend RN HPRD, and a large weekday-weekend staffing gap. Lower-exposure facilities are comparison facilities, not untreated controls.",
        "",
        "## Main Results",
        "",
        "- " + main_line(main, "weekend_total_nurse_hprd"),
        "- " + main_line(main, "weekend_rn_hprd"),
        "- " + main_line(main, "weekday_total_nurse_hprd"),
        "- " + main_line(main, "weekday_minus_weekend_total_hprd"),
        "- " + main_line(main, "total_nurse_hprd"),
        "",
        "The event-study coefficients and raw trend figures are saved under `result/figures/`. Main coefficient tables are saved under `result/tables/`.",
        "",
        "## Robustness and Falsification",
        "",
        "The robustness battery tests alternative exposure definitions, 2021-only baselines, baselines excluding 2020, COVID-period exclusion, balanced-panel restrictions, facility-quarter aggregation, ownership subsamples, and fake 2021 intervention dates. See `result/robustness_results.csv` and `result/tables/table5_robustness.*`.",
        "",
        "## Limitations",
        "",
        "- The design is differential exposure within a national reform. It cannot estimate the absolute national effect without stronger assumptions.",
        "- Turnover exposure is not the preferred January 2022 exposure because turnover fields became publicly visible with the reform; PBJ-derived weekend staffing exposure is cleaner.",
        "- Quality outcomes from ratings and deficiencies are facility-level administrative signals. They should not be interpreted as resident-level clinical outcomes.",
        "- Late post-period estimates may be affected by later staffing-policy debates and the 2024 minimum staffing rule context.",
        "",
        "## Final Go/No-Go Judgment",
        "",
        f"**{label}.** {reason}",
        "",
        "## Manuscript Next Steps",
        "",
        "1. Inspect the event-study figures and pre-trend table before writing causal claims.",
        "2. If primary staffing outcomes survive robustness and placebo checks, frame the paper as a staffing-behavior response to transparency and rating incentives.",
        "3. If weekend gains are offset by weekday losses, frame the result as staffing reallocation rather than overall improvement.",
        "4. Treat downstream ratings and deficiency results as secondary and descriptive unless their timing and robustness are strong.",
    ]
    (REPORT / "final_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    main_results = read_csv_if(RESULT / "main_model_results.csv")
    pretests = read_csv_if(RESULT / "tables" / "pretrend_tests.csv")
    robust = read_csv_if(RESULT / "robustness_results.csv")

    write_readme()
    write_policy_timeline()
    write_identification(main_results, pretests, robust)
    write_final_report(main_results, pretests, robust)

    with (TEMP / "iteration_notes.md").open("a", encoding="utf-8") as f:
        label, reason = go_no_go(main_results, pretests, robust)
        f.write(
            "\n## Phase 8: Final Interpretation and Report\n\n"
            f"The report uses economics-writing guidance: lead with the empirical judgment, state the exact exposure and comparison, report concrete coefficients, and separate limitations from claims. Final judgment: {label}. {reason}\n\n"
            "Self-question: Claims are limited to staffing behavior and administrative downstream measures. The report does not claim resident-level health effects.\n"
        )
    print("Reports written.")


if __name__ == "__main__":
    main()
