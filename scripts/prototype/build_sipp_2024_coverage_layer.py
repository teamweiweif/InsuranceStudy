from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_ZIP = PROJECT_ROOT / "data" / "raw" / "feasibility_audit" / "sipp" / "2024" / "pu2024_csv.zip"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "prototype"
OUTPUT_PARQUET = OUTPUT_DIR / "sipp_2024_person_month_flags.parquet"
OUTPUT_SUMMARY = OUTPUT_DIR / "sipp_2024_coverage_layer_summary.json"


USECOLS = [
    "SSUID",
    "PNUM",
    "MONTHCODE",
    "SPANEL",
    "SWAVE",
    "TEHC_ST",
    "TST_INTV",
    "TMOVER",
    "RHLTHMTH",
    "RPUBMTH",
    "RPRIMTH",
    "RPUBTYPE2",
    "EMDMTH",
    "EOTMTH",
    "WPFINWGT",
]


def load_2024_file() -> pd.DataFrame:
    df = pd.read_csv(
        INPUT_ZIP,
        compression="zip",
        sep="|",
        usecols=USECOLS,
        dtype={"SSUID": "string"},
        low_memory=False,
    )

    int_columns = [
        "PNUM",
        "MONTHCODE",
        "SPANEL",
        "SWAVE",
        "TEHC_ST",
        "TST_INTV",
        "TMOVER",
        "RHLTHMTH",
        "RPUBMTH",
        "RPRIMTH",
        "RPUBTYPE2",
        "EMDMTH",
        "EOTMTH",
    ]
    for col in int_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int16")

    df["WPFINWGT"] = pd.to_numeric(df["WPFINWGT"], errors="coerce")
    return df


def build_flags(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    raw_rows = int(len(df))
    raw_persons = int(df[["SSUID", "PNUM"]].drop_duplicates().shape[0])

    valid_state_mask = df["TEHC_ST"].between(1, 56, inclusive="both")
    excluded_state_rows = int((~valid_state_mask).sum())
    excluded_state_persons = int(
        df.loc[~valid_state_mask, ["SSUID", "PNUM"]].drop_duplicates().shape[0]
    )

    df = df.loc[valid_state_mask].copy()
    df["tehc_st_fips"] = df["TEHC_ST"].astype("Int64").astype(str).str.zfill(2)
    df["release_year"] = 2024
    df["reference_year"] = 2023
    df["positive_month_weight"] = df["WPFINWGT"] > 0

    dec_positive = (
        df.assign(dec_positive=(df["MONTHCODE"] == 12) & (df["WPFINWGT"] > 0))
        .groupby(["SSUID", "PNUM"], sort=False)["dec_positive"]
        .max()
        .rename("in_december_positive_weight_cohort")
    )
    df = df.merge(dec_positive, on=["SSUID", "PNUM"], how="left")

    df = df.sort_values(["SSUID", "PNUM", "MONTHCODE"], kind="stable").reset_index(drop=True)

    group = df.groupby(["SSUID", "PNUM"], sort=False)
    df["next_monthcode"] = group["MONTHCODE"].shift(-1).astype("Int16")
    df["next_rhlthmth"] = group["RHLTHMTH"].shift(-1).astype("Int16")
    df["next_emdmth"] = group["EMDMTH"].shift(-1).astype("Int16")

    df["insured_t"] = df["RHLTHMTH"] == 1
    df["uninsured_t"] = df["RHLTHMTH"] == 2
    df["public_t"] = df["RPUBMTH"] == 1
    df["private_t"] = df["RPRIMTH"] == 1
    df["pure_medicaid_t"] = df["EMDMTH"] == 1
    df["broad_public_assistance_non_medicaid_t"] = (df["RPUBTYPE2"] == 1) & (df["EMDMTH"] != 1)
    df["other_coverage_t"] = df["EOTMTH"] == 1

    df["has_consecutive_next_month"] = df["next_monthcode"] == (df["MONTHCODE"] + 1)
    df["eligible_medicaid_transition"] = df["pure_medicaid_t"] & df["has_consecutive_next_month"]

    medicaid_next = (df["next_emdmth"] == 1).astype("boolean")
    uninsured_next = (df["next_rhlthmth"] == 2).astype("boolean")
    df["medicaid_t_plus_1"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df["uninsured_t_plus_1"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df.loc[df["has_consecutive_next_month"], "medicaid_t_plus_1"] = medicaid_next[df["has_consecutive_next_month"]]
    df.loc[df["has_consecutive_next_month"], "uninsured_t_plus_1"] = uninsured_next[df["has_consecutive_next_month"]]

    df["medicaid_exit_next"] = pd.Series(pd.NA, index=df.index, dtype="Int8")
    df["medicaid_exit_to_uninsured_next"] = pd.Series(pd.NA, index=df.index, dtype="Int8")

    eligible = df["eligible_medicaid_transition"]
    df.loc[eligible, "medicaid_exit_next"] = (~df.loc[eligible, "medicaid_t_plus_1"]).astype("Int8")
    df.loc[eligible, "medicaid_exit_to_uninsured_next"] = df.loc[eligible, "uninsured_t_plus_1"].astype("Int8")

    duplicate_keys = int(df.duplicated(["SSUID", "PNUM", "MONTHCODE"]).sum())
    if duplicate_keys != 0:
        raise ValueError(f"Duplicate person-month keys found after filtering: {duplicate_keys}")

    summary = {
        "input_zip": str(INPUT_ZIP.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "raw_rows": raw_rows,
        "raw_unique_persons": raw_persons,
        "filtered_rows_valid_state_scope": int(len(df)),
        "filtered_unique_persons_valid_state_scope": int(df[["SSUID", "PNUM"]].drop_duplicates().shape[0]),
        "excluded_non_state_rows": excluded_state_rows,
        "excluded_non_state_persons": excluded_state_persons,
        "duplicate_person_month_keys_after_filter": duplicate_keys,
        "distinct_monthcodes_after_filter": sorted(df["MONTHCODE"].dropna().astype(int).unique().tolist()),
        "distinct_spanels_after_filter": sorted(df["SPANEL"].dropna().astype(int).unique().tolist()),
        "category_counts": {
            "insured_t": int(df["insured_t"].sum()),
            "uninsured_t": int(df["uninsured_t"].sum()),
            "public_t": int(df["public_t"].sum()),
            "private_t": int(df["private_t"].sum()),
            "pure_medicaid_t": int(df["pure_medicaid_t"].sum()),
            "broad_public_assistance_non_medicaid_t": int(df["broad_public_assistance_non_medicaid_t"].sum()),
            "other_coverage_t": int(df["other_coverage_t"].sum()),
        },
        "transition_counts": {
            "has_consecutive_next_month": int(df["has_consecutive_next_month"].sum()),
            "eligible_medicaid_transition": int(df["eligible_medicaid_transition"].sum()),
            "medicaid_exit_next": int(df["medicaid_exit_next"].fillna(0).sum()),
            "medicaid_exit_to_uninsured_next": int(df["medicaid_exit_to_uninsured_next"].fillna(0).sum()),
        },
        "december_positive_weight_cohort": {
            "persons": int(
                df.loc[df["in_december_positive_weight_cohort"], ["SSUID", "PNUM"]]
                .drop_duplicates()
                .shape[0]
            ),
            "rows": int(df["in_december_positive_weight_cohort"].sum()),
        },
        "output_parquet": str(OUTPUT_PARQUET.relative_to(PROJECT_ROOT)).replace("\\", "/"),
    }

    output_columns = [
        "SSUID",
        "PNUM",
        "SPANEL",
        "SWAVE",
        "release_year",
        "reference_year",
        "MONTHCODE",
        "TEHC_ST",
        "tehc_st_fips",
        "TST_INTV",
        "TMOVER",
        "WPFINWGT",
        "positive_month_weight",
        "in_december_positive_weight_cohort",
        "RHLTHMTH",
        "RPUBMTH",
        "RPRIMTH",
        "RPUBTYPE2",
        "EMDMTH",
        "EOTMTH",
        "insured_t",
        "uninsured_t",
        "public_t",
        "private_t",
        "pure_medicaid_t",
        "broad_public_assistance_non_medicaid_t",
        "other_coverage_t",
        "has_consecutive_next_month",
        "eligible_medicaid_transition",
        "medicaid_t_plus_1",
        "uninsured_t_plus_1",
        "medicaid_exit_next",
        "medicaid_exit_to_uninsured_next",
    ]
    return df[output_columns], summary


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_2024_file()
    flags, summary = build_flags(df)
    flags.to_parquet(OUTPUT_PARQUET, index=False)
    OUTPUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
