from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_ZIP = PROJECT_ROOT / "data" / "raw" / "feasibility_audit" / "sipp" / "2022" / "pu2022_csv.zip"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "prototype"
OUTPUT_PARQUET = OUTPUT_DIR / "sipp_2022_corrected_person_month_flags.parquet"
OUTPUT_SUMMARY = OUTPUT_DIR / "sipp_2022_correction_pilot_summary.json"


USECOLS = [
    "SSUID",
    "PNUM",
    "MONTHCODE",
    "SPANEL",
    "SWAVE",
    "TEHC_ST",
    "TST_INTV",
    "TMOVER",
    "WPFINWGT",
    "RHLTHMTH",
    "RPUBMTH",
    "RPRIMTH",
    "RPUBTYPE2",
    "EMDMTH",
    "EOTMTH",
    "EMD_BMONTH",
    "EMD_EMONTH",
    "AMD_BMONTH",
    "AMD_EMONTH",
    "EOT_BMONTH",
    "EOT_EMONTH",
    "AOT_BMONTH",
    "AOT_EMONTH",
    "EOTHCOVTYPE",
    "EMC_EMONTH",
    "EMCPART1",
    "EMCPART2",
    "EMCPART3",
    "EMCPART4",
    "EMCPART5",
    "EMILITYPE",
    "EHEMPLY1",
    "EHEMPLY2",
    "RHICOVANN",
    "RPRIVANN",
    "RPUBANN",
    "RMEDCAREANN",
    "RMCAIDANN",
]


def load_2022_file() -> pd.DataFrame:
    int_columns = [col for col in USECOLS if col not in {"SSUID", "WPFINWGT"}]
    chunks: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        INPUT_ZIP,
        compression="zip",
        sep="|",
        usecols=USECOLS,
        dtype={"SSUID": "string"},
        chunksize=100_000,
        low_memory=False,
    ):
        for col in int_columns:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce").astype("Int16")
        chunk["WPFINWGT"] = pd.to_numeric(chunk["WPFINWGT"], errors="coerce")
        chunks.append(chunk)

    return pd.concat(chunks, ignore_index=True)


def _overrun_mask(end_month: pd.Series, monthcode: pd.Series) -> pd.Series:
    return end_month.notna() & monthcode.notna() & (end_month < monthcode)


def _rebuild_private_month(df: pd.DataFrame) -> pd.Series:
    return (
        (df["EHEMPLY1"] == 1)
        | (df["EHEMPLY2"] == 1)
        | (df["corr_EMCPART3"] == 1)
        | (df["EMILITYPE"] == 1)
    )


def _rebuild_public_month(df: pd.DataFrame) -> pd.Series:
    return (
        (df["corr_EMCPART1"] == 1)
        | (df["corr_EMCPART2"] == 1)
        | (df["corr_EMCPART4"] == 1)
        | (df["corr_EMDMTH"] == 1)
        | (df["EMILITYPE"].isin([2, 3]))
        | (df["corr_EOTHCOVTYPE"] == 1)
    )


def build_corrected_flags(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    raw_rows = int(len(df))
    raw_persons = int(df[["SSUID", "PNUM"]].drop_duplicates().shape[0])

    valid_state_mask = df["TEHC_ST"].between(1, 56, inclusive="both")
    excluded_state_rows = int((~valid_state_mask).sum())
    excluded_state_persons = int(
        df.loc[~valid_state_mask, ["SSUID", "PNUM"]].drop_duplicates().shape[0]
    )
    df = df.loc[valid_state_mask].copy()

    df["release_year"] = 2022
    df["reference_year"] = 2021
    df["tehc_st_fips"] = df["TEHC_ST"].astype("Int64").astype(str).str.zfill(2)
    df["positive_month_weight"] = df["WPFINWGT"] > 0

    dec_positive = (
        df.assign(dec_positive=(df["MONTHCODE"] == 12) & (df["WPFINWGT"] > 0))
        .groupby(["SSUID", "PNUM"], sort=False)["dec_positive"]
        .max()
        .rename("in_december_positive_weight_cohort")
    )
    df = df.merge(dec_positive, on=["SSUID", "PNUM"], how="left")

    df = df.sort_values(["SSUID", "PNUM", "MONTHCODE"], kind="stable").reset_index(drop=True)

    # 2022-specific Medicaid end-month repair: if begin month exceeds end month,
    # reset end month to the observed max MONTHCODE for that spell.
    df["medicaid_begin_gt_end"] = (
        df["EMD_BMONTH"].notna()
        & df["EMD_EMONTH"].notna()
        & (df["EMD_BMONTH"] > df["EMD_EMONTH"])
    )
    medicaid_spell_max = (
        df.groupby(["SSUID", "PNUM", "EMD_BMONTH"], dropna=False, sort=False)["MONTHCODE"]
        .transform("max")
        .astype("Int16")
    )
    df["base_EMD_EMONTH"] = df["EMD_EMONTH"].where(~df["medicaid_begin_gt_end"], medicaid_spell_max).astype("Int16")

    df["medicare_spell_overrun"] = _overrun_mask(df["EMC_EMONTH"], df["MONTHCODE"])
    df["medicaid_spell_overrun"] = _overrun_mask(df["base_EMD_EMONTH"], df["MONTHCODE"])
    df["other_spell_overrun"] = _overrun_mask(df["EOT_EMONTH"], df["MONTHCODE"])

    for part in [1, 2, 3, 4, 5]:
        source = f"EMCPART{part}"
        target = f"corr_EMCPART{part}"
        df[target] = df[source].where(~df["medicare_spell_overrun"], pd.NA).astype("Int16")

    df["corr_EMD_BMONTH"] = df["EMD_BMONTH"].where(~df["medicaid_spell_overrun"], pd.NA).astype("Int16")
    df["corr_EMD_EMONTH"] = df["base_EMD_EMONTH"].where(~df["medicaid_spell_overrun"], pd.NA).astype("Int16")
    df["corr_AMD_BMONTH"] = df["AMD_BMONTH"].where(df["corr_EMD_BMONTH"].notna(), 0).astype("Int16")
    df["corr_AMD_EMONTH"] = df["AMD_EMONTH"].where(df["corr_EMD_EMONTH"].notna(), 0).astype("Int16")
    df["corr_EMDMTH"] = df["EMDMTH"].where(~df["medicaid_spell_overrun"], 2).astype("Int16")

    df["raw_EOTHCOVTYPE"] = df["EOTHCOVTYPE"]
    df["corr_EOT_BMONTH"] = df["EOT_BMONTH"].where(~df["other_spell_overrun"], pd.NA).astype("Int16")
    df["corr_EOT_EMONTH"] = df["EOT_EMONTH"].where(~df["other_spell_overrun"], pd.NA).astype("Int16")
    df["corr_AOT_BMONTH"] = df["AOT_BMONTH"].where(df["corr_EOT_BMONTH"].notna(), 0).astype("Int16")
    df["corr_AOT_EMONTH"] = df["AOT_EMONTH"].where(df["corr_EOT_EMONTH"].notna(), 0).astype("Int16")
    df["corr_EOTHCOVTYPE"] = df["EOTHCOVTYPE"].where(~df["other_spell_overrun"], pd.NA).astype("Int16")
    df["corr_EOTMTH"] = df["EOTMTH"].where(~df["other_spell_overrun"], 2).astype("Int16")

    df["corr_RPUBTYPE2"] = df["RPUBTYPE2"].copy()
    rpubtype2_reset = df["medicaid_spell_overrun"] | (
        df["other_spell_overrun"] & (df["raw_EOTHCOVTYPE"] == 1)
    )
    df.loc[rpubtype2_reset, "corr_RPUBTYPE2"] = 2
    df["corr_RPUBTYPE2"] = df["corr_RPUBTYPE2"].astype("Int16")

    raw_private_formula = pd.Series(2, index=df.index, dtype="Int16")
    raw_private_formula.loc[_rebuild_private_month(df)] = 1
    raw_public_formula = pd.Series(2, index=df.index, dtype="Int16")
    raw_public_formula.loc[_rebuild_public_month(df)] = 1
    raw_insured_formula = pd.Series(2, index=df.index, dtype="Int16")
    raw_insured_formula.loc[(raw_private_formula == 1) | (raw_public_formula == 1)] = 1

    df["corr_RPRIMTH"] = df["RPRIMTH"].astype("Int16")

    df["corr_RPUBMTH"] = pd.Series(2, index=df.index, dtype="Int16")
    public_yes = _rebuild_public_month(df)
    df.loc[public_yes, "corr_RPUBMTH"] = 1

    df["corr_RHLTHMTH"] = pd.Series(2, index=df.index, dtype="Int16")
    insured_yes = (df["corr_RPRIMTH"] == 1) | (df["corr_RPUBMTH"] == 1)
    df.loc[insured_yes, "corr_RHLTHMTH"] = 1

    group = df.groupby(["SSUID", "PNUM"], sort=False)
    df["next_monthcode"] = group["MONTHCODE"].shift(-1).astype("Int16")
    df["next_corr_RHLTHMTH"] = group["corr_RHLTHMTH"].shift(-1).astype("Int16")
    df["next_corr_EMDMTH"] = group["corr_EMDMTH"].shift(-1).astype("Int16")

    df["insured_t"] = df["corr_RHLTHMTH"] == 1
    df["uninsured_t"] = df["corr_RHLTHMTH"] == 2
    df["public_t"] = df["corr_RPUBMTH"] == 1
    df["private_t"] = df["corr_RPRIMTH"] == 1
    df["pure_medicaid_t"] = df["corr_EMDMTH"] == 1
    df["broad_public_assistance_non_medicaid_t"] = (df["corr_RPUBTYPE2"] == 1) & (df["corr_EMDMTH"] != 1)
    df["other_coverage_t"] = df["corr_EOTMTH"] == 1

    df["has_consecutive_next_month"] = df["next_monthcode"] == (df["MONTHCODE"] + 1)
    df["eligible_medicaid_transition"] = df["pure_medicaid_t"] & df["has_consecutive_next_month"]

    medicaid_next = (df["next_corr_EMDMTH"] == 1).astype("boolean")
    uninsured_next = (df["next_corr_RHLTHMTH"] == 2).astype("boolean")
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

    change_counts = {
        "EMD_BMONTH": int((df["corr_EMD_BMONTH"] != df["EMD_BMONTH"]).fillna(False).sum()),
        "EMD_EMONTH": int((df["corr_EMD_EMONTH"] != df["EMD_EMONTH"]).fillna(False).sum()),
        "AMD_BMONTH": int((df["corr_AMD_BMONTH"] != df["AMD_BMONTH"]).fillna(False).sum()),
        "AMD_EMONTH": int((df["corr_AMD_EMONTH"] != df["AMD_EMONTH"]).fillna(False).sum()),
        "EMDMTH": int((df["corr_EMDMTH"] != df["EMDMTH"]).fillna(False).sum()),
        "EOT_BMONTH": int((df["corr_EOT_BMONTH"] != df["EOT_BMONTH"]).fillna(False).sum()),
        "EOT_EMONTH": int((df["corr_EOT_EMONTH"] != df["EOT_EMONTH"]).fillna(False).sum()),
        "AOT_BMONTH": int((df["corr_AOT_BMONTH"] != df["AOT_BMONTH"]).fillna(False).sum()),
        "AOT_EMONTH": int((df["corr_AOT_EMONTH"] != df["AOT_EMONTH"]).fillna(False).sum()),
        "EOTHCOVTYPE": int((df["corr_EOTHCOVTYPE"] != df["raw_EOTHCOVTYPE"]).fillna(False).sum()),
        "EOTMTH": int((df["corr_EOTMTH"] != df["EOTMTH"]).fillna(False).sum()),
        "RPUBTYPE2": int((df["corr_RPUBTYPE2"] != df["RPUBTYPE2"]).fillna(False).sum()),
        "RPRIMTH": int((df["corr_RPRIMTH"] != df["RPRIMTH"]).fillna(False).sum()),
        "RPUBMTH": int((df["corr_RPUBMTH"] != df["RPUBMTH"]).fillna(False).sum()),
        "RHLTHMTH": int((df["corr_RHLTHMTH"] != df["RHLTHMTH"]).fillna(False).sum()),
    }

    raw_counts = {
        "insured_t": int((df["RHLTHMTH"] == 1).sum()),
        "uninsured_t": int((df["RHLTHMTH"] == 2).sum()),
        "public_t": int((df["RPUBMTH"] == 1).sum()),
        "private_t": int((df["RPRIMTH"] == 1).sum()),
        "pure_medicaid_t": int((df["EMDMTH"] == 1).sum()),
        "broad_public_assistance_non_medicaid_t": int(((df["RPUBTYPE2"] == 1) & (df["EMDMTH"] != 1)).sum()),
        "other_coverage_t": int((df["EOTMTH"] == 1).sum()),
    }
    corrected_counts = {
        "insured_t": int(df["insured_t"].sum()),
        "uninsured_t": int(df["uninsured_t"].sum()),
        "public_t": int(df["public_t"].sum()),
        "private_t": int(df["private_t"].sum()),
        "pure_medicaid_t": int(df["pure_medicaid_t"].sum()),
        "broad_public_assistance_non_medicaid_t": int(df["broad_public_assistance_non_medicaid_t"].sum()),
        "other_coverage_t": int(df["other_coverage_t"].sum()),
    }

    raw_pure_medicaid = df["EMDMTH"] == 1
    raw_has_next = df["next_monthcode"] == (df["MONTHCODE"] + 1)
    raw_eligible = raw_pure_medicaid & raw_has_next
    raw_medicaid_next = pd.Series(pd.NA, index=df.index, dtype="boolean")
    raw_uninsured_next = pd.Series(pd.NA, index=df.index, dtype="boolean")
    raw_medicaid_next.loc[raw_has_next] = (group["EMDMTH"].shift(-1) == 1).astype("boolean")[raw_has_next]
    raw_uninsured_next.loc[raw_has_next] = (group["RHLTHMTH"].shift(-1) == 2).astype("boolean")[raw_has_next]
    raw_transition_counts = {
        "has_consecutive_next_month": int(raw_has_next.sum()),
        "eligible_medicaid_transition": int(raw_eligible.sum()),
        "medicaid_exit_next": int((~raw_medicaid_next.loc[raw_eligible]).astype("Int8").sum()),
        "medicaid_exit_to_uninsured_next": int(raw_uninsured_next.loc[raw_eligible].astype("Int8").sum()),
    }
    corrected_transition_counts = {
        "has_consecutive_next_month": int(df["has_consecutive_next_month"].sum()),
        "eligible_medicaid_transition": int(df["eligible_medicaid_transition"].sum()),
        "medicaid_exit_next": int(df["medicaid_exit_next"].fillna(0).sum()),
        "medicaid_exit_to_uninsured_next": int(df["medicaid_exit_to_uninsured_next"].fillna(0).sum()),
    }

    annual_person = (
        df.loc[df["in_december_positive_weight_cohort"]]
        .sort_values(["SSUID", "PNUM", "MONTHCODE"], kind="stable")
        .groupby(["SSUID", "PNUM"], sort=False)
        .agg(
            any_insured_month=("insured_t", "max"),
            any_public_month=("public_t", "max"),
            any_private_month=("private_t", "max"),
            any_medicaid_month=("pure_medicaid_t", "max"),
            RHICOVANN=("RHICOVANN", "first"),
            RPUBANN=("RPUBANN", "first"),
            RPRIVANN=("RPRIVANN", "first"),
            RMCAIDANN=("RMCAIDANN", "first"),
        )
        .reset_index()
    )
    annual_checks = {}
    for monthly_col, annual_col in [
        ("any_insured_month", "RHICOVANN"),
        ("any_public_month", "RPUBANN"),
        ("any_private_month", "RPRIVANN"),
        ("any_medicaid_month", "RMCAIDANN"),
    ]:
        annual_yes = annual_person[annual_col] == 1
        monthly_yes = annual_person[monthly_col]
        annual_checks[annual_col] = {
            "persons_compared": int(len(annual_person)),
            "annual_yes_monthly_no": int((annual_yes & ~monthly_yes).sum()),
            "annual_no_monthly_yes": int((~annual_yes & monthly_yes).sum()),
            "exact_match_count": int((annual_yes == monthly_yes).sum()),
        }

    summary = {
        "input_zip": str(INPUT_ZIP.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "release_year": 2022,
        "reference_year": 2021,
        "raw_rows": raw_rows,
        "raw_unique_persons": raw_persons,
        "filtered_rows_valid_state_scope": int(len(df)),
        "filtered_unique_persons_valid_state_scope": int(df[["SSUID", "PNUM"]].drop_duplicates().shape[0]),
        "excluded_non_state_rows": excluded_state_rows,
        "excluded_non_state_persons": excluded_state_persons,
        "duplicate_person_month_keys_after_filter": duplicate_keys,
        "distinct_monthcodes_after_filter": sorted(df["MONTHCODE"].dropna().astype(int).unique().tolist()),
        "distinct_spanels_after_filter": sorted(df["SPANEL"].dropna().astype(int).unique().tolist()),
        "correction_trigger_counts": {
            "medicare_spell_overrun_rows": int(df["medicare_spell_overrun"].sum()),
            "medicaid_begin_gt_end_rows": int(df["medicaid_begin_gt_end"].sum()),
            "medicaid_spell_overrun_rows": int(df["medicaid_spell_overrun"].sum()),
            "other_spell_overrun_rows": int(df["other_spell_overrun"].sum()),
        },
        "change_counts": change_counts,
        "formula_diagnostics_against_raw_recodes": {
            "raw_private_formula_diff_count": int((raw_private_formula != df["RPRIMTH"]).sum()),
            "raw_public_formula_diff_count": int((raw_public_formula != df["RPUBMTH"]).sum()),
            "raw_insured_formula_diff_count": int((raw_insured_formula != df["RHLTHMTH"]).sum()),
        },
        "raw_category_counts": raw_counts,
        "corrected_category_counts": corrected_counts,
        "raw_transition_counts": raw_transition_counts,
        "corrected_transition_counts": corrected_transition_counts,
        "annual_recode_diagnostics_december_positive_cohort": annual_checks,
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
        "medicare_spell_overrun",
        "medicaid_begin_gt_end",
        "medicaid_spell_overrun",
        "other_spell_overrun",
        "RHLTHMTH",
        "RPUBMTH",
        "RPRIMTH",
        "RPUBTYPE2",
        "EMDMTH",
        "EOTMTH",
        "RHICOVANN",
        "RPRIVANN",
        "RPUBANN",
        "RMCAIDANN",
        "corr_RHLTHMTH",
        "corr_RPUBMTH",
        "corr_RPRIMTH",
        "corr_RPUBTYPE2",
        "corr_EMDMTH",
        "corr_EOTMTH",
        "corr_EMD_BMONTH",
        "corr_EMD_EMONTH",
        "corr_AMD_BMONTH",
        "corr_AMD_EMONTH",
        "corr_EOT_BMONTH",
        "corr_EOT_EMONTH",
        "corr_AOT_BMONTH",
        "corr_AOT_EMONTH",
        "corr_EOTHCOVTYPE",
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
    df = load_2022_file()
    flags, summary = build_corrected_flags(df)
    flags.to_parquet(OUTPUT_PARQUET, index=False)
    OUTPUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
