from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "design_diagnostics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RAW_SIPP = {
    2022: PROJECT_ROOT / "data" / "raw" / "feasibility_audit" / "sipp" / "2022" / "pu2022_csv.zip",
    2023: PROJECT_ROOT / "data" / "raw" / "feasibility_audit" / "sipp" / "2023" / "pu2023_csv.zip",
    2024: PROJECT_ROOT / "data" / "raw" / "feasibility_audit" / "sipp" / "2024" / "pu2024_csv.zip",
}

PROTOTYPES = {
    2022: PROJECT_ROOT / "outputs" / "prototype" / "sipp_2022_corrected_person_month_flags.parquet",
    2023: PROJECT_ROOT / "outputs" / "prototype" / "sipp_2023_corrected_person_month_flags.parquet",
    2024: PROJECT_ROOT / "outputs" / "prototype" / "sipp_2024_cms_updated_renewal_outcomes_merged.parquet",
}

RAW_USECOLS = [
    "SSUID",
    "PNUM",
    "MONTHCODE",
    "SHHADID",
    "TAGE",
    "ESEX",
    "TFINCPOVT2",
    "RMWKWJB",
    "EDISABL",
    "RSNAP_MNYN",
    "EBORNUS",
    "ECITIZEN",
    "EEDUC",
    "EHISPAN",
    "ERACE",
]

STACK_PARQUET = OUTPUT_DIR / "sipp_unwinding_feature_stack_2021_2023.parquet"
AUDIT_CSV = OUTPUT_DIR / "sipp_subgroup_candidate_audit.csv"
AUDIT_MD = OUTPUT_DIR / "sipp_subgroup_candidate_audit.md"
SUMMARY_JSON = OUTPUT_DIR / "sipp_unwinding_feature_stack_summary.json"

EXPOSURE_COLUMNS_2024 = [
    "state_abbreviation",
    "cms_reporting_period",
    "cms_updated_renewal_due_n",
    "cms_updated_renewed_total_n",
    "cms_updated_renewed_ex_parte_n",
    "cms_updated_renewed_form_n",
    "cms_updated_terminated_total_n",
    "cms_updated_ineligible_form_n",
    "cms_updated_procedural_termination_n",
    "cms_updated_pending_n",
    "cms_updated_renewed_rate",
    "cms_updated_renewed_ex_parte_rate",
    "cms_updated_renewed_form_rate",
    "cms_updated_terminated_rate",
    "cms_updated_ineligible_rate",
    "cms_updated_procedural_rate",
    "cms_updated_pending_rate",
    "reporting_year",
    "reporting_month",
    "reporting_label",
    "release_label",
    "cms_updated_procedural_share_of_terminated",
    "cms_updated_renewal_match",
]

BASE_COLUMNS = [
    "SSUID",
    "PNUM",
    "MONTHCODE",
    "release_year",
    "reference_year",
    "tehc_st_fips",
    "WPFINWGT",
    "positive_month_weight",
    "in_december_positive_weight_cohort",
    "insured_t",
    "uninsured_t",
    "public_t",
    "private_t",
    "pure_medicaid_t",
    "eligible_medicaid_transition",
    "medicaid_exit_next",
    "medicaid_exit_to_uninsured_next",
]


def load_raw_subset(path: Path) -> pd.DataFrame:
    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(
        path,
        compression="zip",
        sep="|",
        usecols=RAW_USECOLS,
        dtype={"SSUID": "string", "SHHADID": "string"},
        chunksize=100_000,
        engine="python",
    ):
        for col in [c for c in RAW_USECOLS if c not in {"SSUID", "SHHADID"}]:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
        chunks.append(chunk)
    out = pd.concat(chunks, ignore_index=True)
    out["PNUM"] = out["PNUM"].astype("Int64")
    out["MONTHCODE"] = out["MONTHCODE"].astype("Int64")
    return out


def load_prototype(path: Path, release_year: int) -> pd.DataFrame:
    columns = BASE_COLUMNS + (EXPOSURE_COLUMNS_2024 if release_year == 2024 else [])
    df = pd.read_parquet(path, columns=columns).copy()
    df["SSUID"] = df["SSUID"].astype("string")
    df["PNUM"] = pd.to_numeric(df["PNUM"], errors="coerce").astype("Int64")
    df["MONTHCODE"] = pd.to_numeric(df["MONTHCODE"], errors="coerce").astype("Int64")
    return df


def age_band(series: pd.Series) -> pd.Series:
    return pd.cut(
        series,
        bins=[-np.inf, 17, 25, 44, 64, np.inf],
        labels=["age_0_17", "age_18_25", "age_26_44", "age_45_64", "age_65_plus"],
    ).astype("string")


def pov_band(series: pd.Series) -> pd.Series:
    return pd.cut(
        series,
        bins=[-np.inf, 1, 2, 4, np.inf],
        labels=["pov_lt_1", "pov_1_2", "pov_2_4", "pov_4_plus"],
        right=False,
    ).astype("string")


def bool_to_string(series: pd.Series, yes_label: str, no_label: str) -> pd.Series:
    out = pd.Series(pd.NA, index=series.index, dtype="string")
    out.loc[series == True] = yes_label
    out.loc[series == False] = no_label
    return out


def derive_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["age_years"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["female"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df.loc[df["ESEX"] == 2, "female"] = True
    df.loc[df["ESEX"] == 1, "female"] = False

    df["monthly_pov_ratio"] = pd.to_numeric(df["TFINCPOVT2"], errors="coerce")
    df["weeks_with_job_month"] = pd.to_numeric(df["RMWKWJB"], errors="coerce")

    df["work_limiting_disability"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df.loc[df["EDISABL"] == 1, "work_limiting_disability"] = True
    df.loc[df["EDISABL"] == 2, "work_limiting_disability"] = False

    df["snap_month"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df.loc[df["RSNAP_MNYN"] == 1, "snap_month"] = True
    df.loc[df["RSNAP_MNYN"] == 2, "snap_month"] = False

    df["foreign_born"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df.loc[df["EBORNUS"] == 2, "foreign_born"] = True
    df.loc[df["EBORNUS"] == 1, "foreign_born"] = False

    df["noncitizen"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df.loc[df["ECITIZEN"] == 2, "noncitizen"] = True
    df.loc[df["ECITIZEN"] == 1, "noncitizen"] = False

    df["age_band"] = age_band(df["age_years"])
    df["pov_band"] = pov_band(df["monthly_pov_ratio"])

    df["employed_month"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df.loc[df["weeks_with_job_month"].notna(), "employed_month"] = df.loc[
        df["weeks_with_job_month"].notna(), "weeks_with_job_month"
    ] > 0

    child_mask = df["age_years"] < 18
    hh_child = (
        df.assign(_child=child_mask.fillna(False))
        .groupby(["release_year", "reference_year", "SSUID", "SHHADID", "MONTHCODE"], sort=False)["_child"]
        .transform("max")
    )
    df["household_has_child"] = hh_child.astype("boolean")

    df["female_group"] = bool_to_string(df["female"], "female", "male")
    df["employed_group"] = bool_to_string(df["employed_month"], "employed", "not_employed")
    df["disability_group"] = bool_to_string(
        df["work_limiting_disability"], "disability_limit", "no_disability_limit"
    )
    df["snap_group"] = bool_to_string(df["snap_month"], "snap_yes", "snap_no")
    df["household_child_group"] = bool_to_string(
        df["household_has_child"], "household_has_child", "household_no_child"
    )
    df["foreign_born_group"] = bool_to_string(df["foreign_born"], "foreign_born", "us_born")
    df["noncitizen_group"] = bool_to_string(df["noncitizen"], "noncitizen", "citizen")

    return df


def build_stack_for_release(release_year: int) -> pd.DataFrame:
    prototype = load_prototype(PROTOTYPES[release_year], release_year)
    raw = load_raw_subset(RAW_SIPP[release_year])

    merged = prototype.merge(
        raw,
        on=["SSUID", "PNUM", "MONTHCODE"],
        how="left",
        validate="one_to_one",
    )
    merged = derive_features(merged)
    merged["dataset"] = "SIPP"
    return merged


def common_missing_rate(series: pd.Series, weight: pd.Series | None = None) -> float:
    mask = series.isna()
    if weight is None:
        return float(mask.mean()) if len(series) else float("nan")
    valid = weight.notna() & (weight > 0)
    if valid.sum() == 0:
        return float("nan")
    return float(weight.loc[valid & mask].sum() / weight.loc[valid].sum())


def build_candidate_audit(stack: pd.DataFrame) -> pd.DataFrame:
    candidate_map = {
        "age_band": "age_band",
        "female_group": "female_group",
        "household_child_group": "household_child_group",
        "pov_band": "pov_band",
        "employed_group": "employed_group",
        "disability_group": "disability_group",
        "snap_group": "snap_group",
        "foreign_born_group": "foreign_born_group",
        "noncitizen_group": "noncitizen_group",
    }

    rows: list[dict[str, object]] = []
    for reference_year in sorted(stack["reference_year"].dropna().unique()):
        df = stack.loc[stack["reference_year"] == reference_year].copy()
        eligible = df["eligible_medicaid_transition"] == True
        for family, col in candidate_map.items():
            vals = df[col]
            vals_eligible = df.loc[eligible, col]
            weights = df["WPFINWGT"]
            eligible_weights = df.loc[eligible, "WPFINWGT"]
            rows.append(
                {
                    "dataset": "SIPP",
                    "reference_year": int(reference_year),
                    "feature_family": family,
                    "source_column": col,
                    "rows_total": int(len(df)),
                    "eligible_rows": int(eligible.sum()),
                    "missing_rate_all": round(common_missing_rate(vals), 4),
                    "missing_rate_all_weighted": round(common_missing_rate(vals, weights), 4),
                    "missing_rate_eligible": round(common_missing_rate(vals_eligible), 4),
                    "missing_rate_eligible_weighted": round(common_missing_rate(vals_eligible, eligible_weights), 4),
                    "nonmissing_groups_eligible": int(vals_eligible.dropna().nunique()),
                    "top_groups_eligible": "; ".join(
                        vals_eligible.value_counts(dropna=True).head(4).index.astype(str).tolist()
                    ),
                }
            )

    audit = pd.DataFrame(rows).sort_values(["feature_family", "reference_year"], kind="stable").reset_index(drop=True)
    summary = (
        audit.groupby("feature_family", sort=False)
        .agg(
            max_missing_rate_eligible=("missing_rate_eligible", "max"),
            years_present=("reference_year", "nunique"),
            min_nonmissing_groups_eligible=("nonmissing_groups_eligible", "min"),
        )
        .reset_index()
    )
    summary["retain_for_round2"] = (
        (summary["max_missing_rate_eligible"] <= 0.2)
        & (summary["years_present"] == audit["reference_year"].nunique())
        & (summary["min_nonmissing_groups_eligible"] >= 2)
    )
    audit = audit.merge(summary, on="feature_family", how="left", validate="many_to_one")
    return audit


def df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def write_audit_markdown(audit: pd.DataFrame, stack: pd.DataFrame) -> None:
    retained = (
        audit.loc[audit["retain_for_round2"], "feature_family"].drop_duplicates().sort_values().tolist()
    )
    dropped = (
        audit.loc[~audit["retain_for_round2"], "feature_family"].drop_duplicates().sort_values().tolist()
    )
    year_rows: list[dict[str, object]] = []
    for reference_year in sorted(stack["reference_year"].dropna().unique()):
        df = stack.loc[stack["reference_year"] == reference_year].copy()
        eligible = df["eligible_medicaid_transition"] == True
        year_rows.append(
            {
                "reference_year": int(reference_year),
                "rows": int(len(df)),
                "persons": int(df[["SSUID", "PNUM"]].drop_duplicates().shape[0]),
                "eligible_rows": int(eligible.sum()),
                "eligible_weight_sum": round(float(df.loc[eligible, "WPFINWGT"].sum()), 2),
            }
        )
    by_year = pd.DataFrame(year_rows)

    top = audit[
        [
            "feature_family",
            "reference_year",
            "missing_rate_eligible",
            "nonmissing_groups_eligible",
            "retain_for_round2",
            "top_groups_eligible",
        ]
    ]

    lines = [
        "# SIPP Subgroup Candidate Audit",
        "",
        "## Purpose",
        "",
        "This note audits the minimum person/household subgroup feature layer for the second-round churn/unwinding diagnostics.",
        "",
        "It checks whether candidate subgroup families are present, interpretable, and low-missing enough across:",
        "",
        "- `reference year 2021` from the corrected `2022` release",
        "- `reference year 2022` from the corrected `2023` release",
        "- `reference year 2023` from the merged `2024` release",
        "",
        "## Stack Summary",
        "",
        df_to_markdown(by_year),
        "",
        "## Retained For Round 2",
        "",
        *(f"- `{name}`" for name in retained),
        "",
        "## Dropped For Round 2",
        "",
        *(f"- `{name}`" for name in dropped),
        "",
        "## Detailed Candidate Table",
        "",
        df_to_markdown(top),
    ]
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    frames = [build_stack_for_release(year) for year in [2022, 2023, 2024]]
    stack = pd.concat(frames, ignore_index=True)

    keep_columns = BASE_COLUMNS + [
        "dataset",
        "SHHADID",
        "TAGE",
        "ESEX",
        "TFINCPOVT2",
        "RMWKWJB",
        "EDISABL",
        "RSNAP_MNYN",
        "EBORNUS",
        "ECITIZEN",
        "EEDUC",
        "EHISPAN",
        "ERACE",
        "age_years",
        "age_band",
        "female",
        "female_group",
        "monthly_pov_ratio",
        "pov_band",
        "weeks_with_job_month",
        "employed_month",
        "employed_group",
        "work_limiting_disability",
        "disability_group",
        "snap_month",
        "snap_group",
        "household_has_child",
        "household_child_group",
        "foreign_born",
        "foreign_born_group",
        "noncitizen",
        "noncitizen_group",
    ] + EXPOSURE_COLUMNS_2024
    keep_columns = [c for c in keep_columns if c in stack.columns]
    stack = stack[keep_columns].copy()
    stack.to_parquet(STACK_PARQUET, index=False)

    audit = build_candidate_audit(stack)
    audit.to_csv(AUDIT_CSV, index=False)
    write_audit_markdown(audit, stack)

    retained = audit.loc[audit["retain_for_round2"], "feature_family"].drop_duplicates().sort_values().tolist()
    summary = {
        "stack_parquet": str(STACK_PARQUET.relative_to(PROJECT_ROOT)),
        "audit_csv": str(AUDIT_CSV.relative_to(PROJECT_ROOT)),
        "audit_md": str(AUDIT_MD.relative_to(PROJECT_ROOT)),
        "reference_years": sorted(int(x) for x in stack["reference_year"].dropna().unique()),
        "rows_total": int(len(stack)),
        "persons_total": int(stack[["SSUID", "PNUM"]].drop_duplicates().shape[0]),
        "eligible_transition_rows_total": int((stack["eligible_medicaid_transition"] == True).sum()),
        "retained_feature_families": retained,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
