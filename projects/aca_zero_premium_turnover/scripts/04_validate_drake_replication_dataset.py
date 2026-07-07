#!/usr/bin/env python
"""Validate the Step 2 Drake-style replication county-year dataset.

This script performs integrity and descriptive validation only. It does not run
causal regressions, DID, event studies, causal forests, or policy learning.
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
DOCS = ROOT / "docs"
LOGS = ROOT / "logs"
VALIDATION_LOG = LOGS / "step2_validation.log"


def setup_logging(verbose: bool = False) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(VALIDATION_LOG, mode="w", encoding="utf-8"), logging.StreamHandler()],
    )


def read_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing input dataset: {path}")
    return pd.read_csv(path, dtype={"county_fips": str})


def flag(status: str, check: str, details: str, metric: Any = "", threshold: Any = "") -> dict[str, Any]:
    return {"status": status, "check": check, "metric": metric, "threshold": threshold, "details": details}


def validate(input_path: Path, verbose: bool = False) -> pd.DataFrame:
    setup_logging(verbose)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    df = read_dataset(input_path)
    flags: list[dict[str, Any]] = []

    logging.info("Validating row integrity")
    dup_count = int(df.duplicated(["year", "county_fips"]).sum())
    flags.append(flag("PASS" if dup_count == 0 else "FAIL", "unique county-year rows", f"Duplicate county-year rows: {dup_count}", dup_count, 0))
    years = sorted(df["year"].dropna().astype(int).unique().tolist())
    flags.append(flag("PASS" if years == [2022, 2023, 2024] else "FAIL", "expected year coverage", f"Years present: {years}", ",".join(map(str, years)), "2022,2023,2024"))
    missing_fips = int(df["county_fips"].isna().sum() + df["county_fips"].astype(str).str.strip().eq("").sum())
    invalid_fips = int((~df["county_fips"].astype(str).str.match(r"^\d{5}$", na=False)).sum())
    flags.append(flag("PASS" if missing_fips == 0 else "FAIL", "missing county_fips", f"Missing county_fips rows: {missing_fips}", missing_fips, 0))
    flags.append(flag("PASS" if invalid_fips == 0 else "WARN", "county_fips validity", f"Invalid FIPS-like rows: {invalid_fips}", invalid_fips, 0))

    logging.info("Validating sample restrictions")
    primary = df[df["included_primary_sample"].fillna(False).astype(bool)]
    ak_hi_ne_primary = sorted(set(primary.loc[primary["state"].isin(["AK", "HI", "NE"]), "state"]))
    flags.append(flag("PASS" if "AK" not in ak_hi_ne_primary else "FAIL", "AK excluded from primary sample", f"Primary states among AK/HI/NE: {ak_hi_ne_primary}"))
    flags.append(flag("PASS" if "HI" not in ak_hi_ne_primary else "FAIL", "HI excluded from primary sample", f"Primary states among AK/HI/NE: {ak_hi_ne_primary}"))
    flags.append(flag("PASS" if "NE" not in ak_hi_ne_primary else "WARN", "NE excluded or explicitly handled", f"Primary states among AK/HI/NE: {ak_hi_ne_primary}"))
    not_hcgov_primary = int((~primary["continuous_hcgov_2022_2024"].fillna(False).astype(bool)).sum()) if "continuous_hcgov_2022_2024" in primary.columns else len(primary)
    flags.append(flag("PASS" if not_hcgov_primary == 0 else "FAIL", "HealthCare.gov state sample applied", f"Primary rows not continuously HC.gov: {not_hcgov_primary}"))
    if "included_drake_harmonized_sample" in df.columns:
        harmonized = df[df["included_drake_harmonized_sample"].fillna(False).astype(bool)]
        h_counties = int(harmonized["county_fips"].nunique())
        flags.append(flag("PASS" if h_counties == 2159 else "WARN", "Drake eTable 3 harmonized county count", f"Harmonized counties: {h_counties}", h_counties, 2159))
    else:
        flags.append(flag("WARN", "Drake eTable 3 harmonized sample flags", "Repaired Step 2 flags are absent from this processed dataset.", "", "present"))

    logging.info("Validating OEP outcomes")
    outcome_cols = ["Cnsmr", "New_Cnsmr", "Tot_Renrl", "Auto_Renrl", "Actv_Renrl", "Actv_Renrl_Nsw", "Actv_Renrl_Sw"]
    outcome_missing = df.groupby("year")[outcome_cols].apply(lambda g: g.isna().mean()).reset_index()
    outcome_missing.to_csv(OUTPUTS / "drake_replication_outcome_missingness_by_year.csv", index=False)
    max_outcome_missing = float(df[outcome_cols].isna().mean().max())
    flags.append(flag("PASS" if max_outcome_missing < 0.05 else "WARN", "OEP outcomes constructible for 2022-2024", f"Maximum missingness across core outcomes: {max_outcome_missing:.3f}", max_outcome_missing, "<0.05"))
    rate_cols = ["auto_reenrollment_rate", "active_reenrollment_rate", "active_switch_rate_among_active", "active_stay_rate_among_active", "new_consumer_share", "total_reenrollment_share"]
    impossible_rates = int(sum(((df[col] < 0) | (df[col] > 1)).sum() for col in rate_cols if col in df.columns))
    flags.append(flag("PASS" if impossible_rates == 0 else "FAIL", "impossible rates", f"Rate values outside [0,1]: {impossible_rates}", impossible_rates, 0))
    bad_logs = int(sum((df[col].notna() & ~np.isfinite(df[col])).sum() for col in df.columns if col.startswith("log_")))
    flags.append(flag("PASS" if bad_logs == 0 else "FAIL", "log variables finite when present", f"Nonfinite log values: {bad_logs}", bad_logs, 0))

    logging.info("Validating treatment integrity")
    construct_by_year = df.groupby("year")["treatment_constructible_flag"].mean().reset_index(name="constructible_rate")
    construct_by_state_year = df.groupby(["year", "state"])["treatment_constructible_flag"].mean().reset_index(name="constructible_rate")
    construct_by_year.to_csv(OUTPUTS / "drake_replication_treatment_constructibility_by_year.csv", index=False)
    construct_by_state_year.to_csv(OUTPUTS / "drake_replication_treatment_constructibility_by_state_year.csv", index=False)
    min_construct = float(construct_by_year["constructible_rate"].min())
    treatment_status = "PASS" if min_construct >= 0.95 else "WARN" if min_construct >= 0.70 else "FAIL"
    flags.append(flag(treatment_status, "binary turnover treatment constructible", f"Minimum constructibility by year: {min_construct:.3f}. 2022 depends on the 2021-to-2022 transition and should be audited against Drake treatment anchors.", min_construct, ">=0.95"))
    across_missing = float(df["any_zero_to_positive_turnover_across_issuer"].isna().mean()) if "any_zero_to_positive_turnover_across_issuer" in df.columns else 1.0
    flags.append(flag("PASS" if across_missing == 0 else "WARN", "across-issuer vs within-issuer distinction constructible", f"Across-issuer flag missingness: {across_missing:.3f}", across_missing, 0))
    zero_measure = set(df.get("zero_premium_measure_type", pd.Series(dtype=str)).dropna().unique())
    flags.append(flag("WARN", "zero-premium proxy quality", f"Zero-premium measure types: {sorted(zero_measure)}. This is proxy-based, not exact.", ",".join(sorted(zero_measure)), "exact preferred"))

    logging.info("Validating repaired Step 2 market controls")
    required_repair_cols = [
        "enrollment_2021_weight",
        "number_of_silver_plans",
        "number_of_insurers",
        "lowest_silver_premium",
        "second_lowest_silver_premium",
        "premium_spread_among_silver_plans",
        "lowest_bronze_premium",
        "bronze_spread",
    ]
    missing_repair_cols = [col for col in required_repair_cols if col not in df.columns]
    flags.append(
        flag(
            "PASS" if not missing_repair_cols else "WARN",
            "Step 2 repair market-control columns present",
            "Missing repair columns: " + ", ".join(missing_repair_cols) if missing_repair_cols else "All repaired market-control columns are present.",
            len(missing_repair_cols),
            0,
        )
    )
    if "enrollment_2021_weight" in df.columns:
        primary_weight_nonmissing = float(primary["enrollment_2021_weight"].notna().mean()) if len(primary) else 0.0
        flags.append(flag("PASS" if primary_weight_nonmissing >= 0.95 else "WARN", "2021 enrollment weights available in primary sample", f"Nonmissing rate: {primary_weight_nonmissing:.3f}", primary_weight_nonmissing, ">=0.95"))
    if "bronze_spread" in df.columns:
        primary_bronze_nonmissing = float(primary["bronze_spread"].notna().mean()) if len(primary) else 0.0
        flags.append(flag("PASS" if primary_bronze_nonmissing >= 0.95 else "WARN", "bronze spread available in primary sample", f"Nonmissing rate: {primary_bronze_nonmissing:.3f}", primary_bronze_nonmissing, ">=0.95"))

    logging.info("Drake-style comparison diagnostics")
    comparison_rows = [
        {"metric": "county_year_rows_before_restrictions", "value": len(df)},
        {"metric": "county_year_rows_primary_sample", "value": len(primary)},
        {"metric": "counties_primary_sample", "value": primary["county_fips"].nunique()},
        {"metric": "states_primary_sample", "value": primary["state"].nunique()},
    ]
    for year, g in df.groupby("year"):
        comparison_rows.append({"metric": f"treated_share_{year}", "value": g["any_zero_to_positive_turnover"].mean()})
        comparison_rows.append({"metric": f"across_issuer_treated_share_{year}", "value": g["any_zero_to_positive_turnover_across_issuer"].mean()})
        comparison_rows.append({"metric": f"within_issuer_treated_share_{year}", "value": g["any_zero_to_positive_turnover_within_issuer"].mean()})
        comparison_rows.append({"metric": f"missing_outcome_share_{year}", "value": g[outcome_cols].isna().any(axis=1).mean()})
        comparison_rows.append({"metric": f"missing_treatment_share_{year}", "value": (~g["treatment_constructible_flag"].astype(bool)).mean()})
    pd.DataFrame(comparison_rows).to_csv(OUTPUTS / "drake_replication_comparison_diagnostics.csv", index=False)

    logging.info("Comparing to Step 1 prototype")
    join_path = OUTPUTS / "drake_replication_join_diagnostics.csv"
    prototype_path = OUTPUTS / "prototype_join_diagnostics.csv"
    if join_path.exists() and prototype_path.exists():
        join = pd.read_csv(join_path)
        proto = pd.read_csv(prototype_path)
        current_2324 = join[
            join["transition"].eq("2023_to_2024") & join["metric"].eq("crosswalk_to_current_plan")
        ]["rate"].mean()
        proto_2324 = proto[proto["metric"].eq("crosswalk to current-year QHP Landscape")]["rate"].mean()
        comparison = pd.DataFrame(
            [
                {
                    "metric": "2023_to_2024_current_plan_join_rate",
                    "step1_prototype_rate": proto_2324,
                    "step2_national_rate": current_2324,
                    "change": current_2324 - proto_2324,
                    "notes": "Step 2 average is across lowest and second-lowest rows nationally.",
                }
            ]
        )
        comparison.to_csv(OUTPUTS / "drake_replication_step1_comparison.csv", index=False)
        flags.append(flag("PASS" if current_2324 >= 0.95 else "WARN", "Step 1 97.4 percent current-year join comparison", f"Step 1: {proto_2324:.3f}; Step 2 2023->2024: {current_2324:.3f}", current_2324, ">=0.95"))
    else:
        flags.append(flag("WARN", "Step 1 prototype comparison", "Prototype or Step 2 join diagnostics file missing."))

    sample_align_status = "PASS" if len(primary) > 0 and not ak_hi_ne_primary else "WARN"
    flags.append(flag(sample_align_status, "sample roughly aligns with Drake et al.", f"Primary sample rows: {len(primary)}; states: {primary['state'].nunique()}"))
    ready_desc = "PASS" if dup_count == 0 and max_outcome_missing < 0.05 and len(primary) > 0 else "WARN"
    flags.append(flag(ready_desc, "dataset ready for descriptive replication", "Ready if uniqueness, OEP outcomes, and primary sample checks pass."))
    ready_causal = "WARN" if treatment_status != "FAIL" else "FAIL"
    flags.append(flag(ready_causal, "dataset ready for causal modeling later", "Step 2 does not authorize causal modeling; the 2021-to-2022 transition and proxy treatment require review."))

    flag_df = pd.DataFrame(flags)
    flag_df.to_csv(OUTPUTS / "drake_replication_validation_flags.csv", index=False)

    append_validation_summary(flag_df)
    logging.info("Validation complete")
    print("\nStep 2 validation summary")
    print(flag_df.to_string(index=False))
    print(f"\nValidation flags: {OUTPUTS / 'drake_replication_validation_flags.csv'}")
    print(f"Validation log: {VALIDATION_LOG}")
    return flag_df


def append_validation_summary(flag_df: pd.DataFrame) -> None:
    report = DOCS / "drake_replication_dataset_report.md"
    if not report.exists():
        return
    counts = flag_df["status"].value_counts().to_dict()
    table = flag_df.to_markdown(index=False) if _has_tabulate() else _markdown_table(flag_df)
    text = report.read_text(encoding="utf-8")
    marker = "\n## Validation Summary\n"
    section = f"""{marker}
Validation flags after running `scripts/04_validate_drake_replication_dataset.py`:

- PASS: {counts.get('PASS', 0)}
- WARN: {counts.get('WARN', 0)}
- FAIL: {counts.get('FAIL', 0)}

{table}
"""
    if marker in text:
        text = text.split(marker)[0].rstrip() + section
    else:
        text = text.rstrip() + "\n" + section
    report.write_text(text, encoding="utf-8")


def _has_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401

        return True
    except Exception:  # noqa: BLE001
        return False


def _markdown_table(df: pd.DataFrame) -> str:
    shown = df.fillna("")
    cols = list(shown.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in shown.iterrows():
        lines.append("| " + " | ".join(str(row[c]).replace("|", "\\|").replace("\n", " ") for c in cols) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/processed/drake_replication_county_year_2022_2024.csv")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    validate(ROOT / args.input, verbose=args.verbose)


if __name__ == "__main__":
    main()
