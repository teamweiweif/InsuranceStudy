from __future__ import annotations

import importlib.util
import logging
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUTPUTS = ROOT / "outputs"
DOCS = ROOT / "docs"
INTERMEDIATE = ROOT / "data" / "intermediate"
PROCESSED = ROOT / "data" / "processed"
METADATA = ROOT / "data" / "metadata"
LOGS = ROOT / "logs"


def load_build_module() -> Any:
    spec = importlib.util.spec_from_file_location("drake_build", SCRIPTS / "03_build_drake_replication_dataset.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Step 2 build module.")
    module = importlib.util.module_from_spec(spec)
    sys.modules["drake_build"] = module
    spec.loader.exec_module(module)
    return module


BUILD = load_build_module()

DRAKE_ANCHORS = BUILD.DRAKE_TREATMENT_ANCHORS
TRANSITIONS = [(2021, 2022), (2022, 2023), (2023, 2024)]
PREMIUM_VARIANTS = ["current_ehb_all_states", "ehb_named_states_only"]
DEFAULT_RULES = [
    "current_repo_rule",
    "no_same_issuer_priority",
    "source_order_first_valid",
    "lowest_crosswalk_level",
    "same_plan_if_available_else_source_order",
    "same_plan_if_available_else_lowest_level",
    "whole_county_00000_only",
    "county_any_zip_turnover",
    "county_any_zip_across_turnover",
    "reason8_priority",
    "exclude_level4_5",
    "include_level4_5_as_missing_current",
]
DEFAULT_RULE_SUPPORT = {
    "current_repo_rule": ("plausible", "Existing repo rule: mapped current plan, current silver, same issuer, lowest CrosswalkLevel, lexical tie-breaks."),
    "no_same_issuer_priority": ("diagnostic_only", "Removes repo same-issuer priority to test whether it suppresses across-insurer turnover."),
    "source_order_first_valid": ("diagnostic_only", "First valid raw PUF row in source order; CMS dictionary does not state that file order is the default hierarchy."),
    "lowest_crosswalk_level": ("diagnostic_only", "Lowest numeric CrosswalkLevel among valid rows; tests whether level hierarchy matters."),
    "same_plan_if_available_else_source_order": ("plausible", "Article wording says a plan defaults to itself if available, otherwise to a similar plan; synthetic only when same plan is available in the current county panel."),
    "same_plan_if_available_else_lowest_level": ("plausible", "Same-plan-if-available, then lowest CrosswalkLevel among valid rows."),
    "whole_county_00000_only": ("diagnostic_only", "CMS says ZipCode 00000 covers the entire county; Drake does not say to prefer it over ZIP-level rows."),
    "county_any_zip_turnover": ("diagnostic_only", "County-year treated if any ZIP-level candidate is zero-to-positive."),
    "county_any_zip_across_turnover": ("diagnostic_only", "County-year across treated if any ZIP-level candidate is zero-to-positive and across issuer."),
    "reason8_priority": ("diagnostic_only", "Prioritizes ReasonForCrosswalk=8 different-issuer rows; CMS defines reason 8 but Drake does not state this priority."),
    "exclude_level4_5": ("plausible", "Treats CrosswalkLevel 4/5 as no valid reenrollment/default option."),
    "include_level4_5_as_missing_current": ("diagnostic_only", "Keeps CrosswalkLevel 4/5 in audit but classifies as missing current default."),
}


def setup_logging() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOGS / "crosswalk_default_mapping_audit.log", mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def clean_zip(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text == "":
        return ""
    try:
        if reinterpretable_float(text):
            return f"{int(float(text)):05d}"
    except Exception:
        pass
    text = text.split(".")[0] if text.endswith(".0") else text
    return text.zfill(5) if text.isdigit() else text


def reinterpretable_float(text: str) -> bool:
    if text.count(".") > 1:
        return False
    stripped = text.replace(".", "", 1)
    return stripped.isdigit()


def joined_unique(values: pd.Series, max_items: int = 30) -> str:
    clean = []
    for value in values.dropna().astype(str):
        value = value.strip()
        if value and value not in clean:
            clean.append(value)
    if len(clean) > max_items:
        return "|".join(clean[:max_items]) + f"|...(+{len(clean) - max_items})"
    return "|".join(clean)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        values = []
        for col in cols:
            value = row[col]
            if isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def load_raw_crosswalk(manifest: pd.DataFrame, previous_year: int, current_year: int) -> pd.DataFrame:
    row = BUILD.manifest_row(manifest, "exchange_puf", current_year, "Plan ID Crosswalk PUF")
    df = BUILD.read_csv_from_zip(ROOT / row["local_path"])
    df["source_row_order"] = np.arange(len(df), dtype=int)
    prev_plan = f"PlanID_{previous_year}"
    cur_plan = f"PlanID_{current_year}"
    prev_issuer = f"IssuerID_{previous_year}"
    cur_issuer = f"IssuerID_{current_year}"
    needed = [
        "source_row_order",
        "State",
        "DentalPlan",
        prev_plan,
        prev_issuer,
        f"MetalLevel_{previous_year}",
        "FIPSCode",
        "ZipCode",
        "CrosswalkLevel",
        "ReasonForCrosswalk",
        cur_plan,
        cur_issuer,
        f"MetalLevel_{current_year}",
    ]
    out = df[[col for col in needed if col in df.columns]].copy()
    out = out.rename(
        columns={
            "State": "state",
            "DentalPlan": "dental_plan",
            prev_plan: "previous_plan_id",
            prev_issuer: "previous_issuer_id_from_crosswalk",
            f"MetalLevel_{previous_year}": "previous_metal_level",
            "FIPSCode": "county_fips",
            "ZipCode": "zip_code",
            "CrosswalkLevel": "crosswalk_level",
            "ReasonForCrosswalk": "reason_for_crosswalk",
            cur_plan: "current_plan_id",
            cur_issuer: "current_issuer_id_from_crosswalk",
            f"MetalLevel_{current_year}": "current_metal_level",
        }
    )
    for col in [
        "state",
        "dental_plan",
        "previous_plan_id",
        "previous_issuer_id_from_crosswalk",
        "previous_metal_level",
        "county_fips",
        "zip_code",
        "crosswalk_level",
        "reason_for_crosswalk",
        "current_plan_id",
        "current_issuer_id_from_crosswalk",
        "current_metal_level",
    ]:
        if col not in out.columns:
            out[col] = ""
    out["transition"] = f"{previous_year}_to_{current_year}"
    out["previous_year"] = previous_year
    out["current_year"] = current_year
    out["year"] = current_year
    out["state"] = out["state"].astype(str).str.upper().str.strip()
    out["county_fips"] = out["county_fips"].map(BUILD.clean_fips)
    out["zip_code"] = out["zip_code"].map(clean_zip)
    out["previous_plan_id_raw"] = out["previous_plan_id"].astype(str)
    out["current_plan_id_raw"] = out["current_plan_id"].astype(str)
    out["previous_plan_id"] = out["previous_plan_id"].map(BUILD.clean_id)
    out["current_plan_id"] = out["current_plan_id"].map(BUILD.clean_id)
    out["previous_issuer_id_from_crosswalk"] = out["previous_issuer_id_from_crosswalk"].map(BUILD.clean_id)
    out["current_issuer_id_from_crosswalk"] = out["current_issuer_id_from_crosswalk"].map(BUILD.clean_id)
    out = out[out["dental_plan"].astype(str).str.upper().isin({"N", "NO", "FALSE", "0"})].copy()
    out = out[out["previous_metal_level"].astype(str).str.lower().str.contains("silver", na=False)].copy()
    out["crosswalk_level_num"] = pd.to_numeric(out["crosswalk_level"], errors="coerce")
    out["reason_for_crosswalk_num"] = pd.to_numeric(out["reason_for_crosswalk"], errors="coerce")
    out["mapping_quality_flag"] = np.where(
        out["current_plan_id"].str.contains("00000XX", na=False) | out["current_plan_id"].eq(""),
        "unmapped_or_placeholder",
        "mapped",
    )
    out["valid_mapped_candidate"] = out["mapping_quality_flag"].eq("mapped") & ~out["crosswalk_level_num"].isin([4, 5])
    out["zip_00000_candidate"] = out["zip_code"].eq("00000")
    out["reason8_candidate"] = out["reason_for_crosswalk_num"].eq(8)
    out["level3_zip_candidate"] = out["crosswalk_level_num"].eq(3)
    out["level4_or_5_no_reenrollment_candidate"] = out["crosswalk_level_num"].isin([4, 5])
    return out


def make_top_two_long(two_lowest: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rank, plan_col, issuer_col, premium_col in [
        ("lowest", "lowest_silver_plan_id", "lowest_silver_issuer_id", "lowest_silver_premium"),
        ("second_lowest", "second_lowest_silver_plan_id", "second_lowest_silver_issuer_id", "second_lowest_silver_premium"),
    ]:
        part = two_lowest[
            ["year", "state", "county_fips", plan_col, issuer_col, premium_col]
        ].rename(
            columns={
                plan_col: "previous_plan_id",
                issuer_col: "previous_issuer_id_from_prior_panel",
                premium_col: "prior_gross_premium_top_two",
            }
        )
        part["rank"] = rank
        rows.append(part)
    out = pd.concat(rows, ignore_index=True)
    out["previous_plan_id"] = out["previous_plan_id"].map(BUILD.clean_id)
    out["previous_issuer_id_from_prior_panel"] = out["previous_issuer_id_from_prior_panel"].map(BUILD.clean_id)
    return out


def prepare_premium_panel(zero_proxy: pd.DataFrame) -> pd.DataFrame:
    specs = [spec for spec in BUILD.premium_variant_specs() if spec["variant_name"] in PREMIUM_VARIANTS]
    zero_proxy = zero_proxy.copy()
    zero_proxy["plan_id"] = zero_proxy["plan_id"].map(BUILD.clean_id)
    zero_proxy["issuer_id"] = zero_proxy["issuer_id"].map(BUILD.clean_id)
    variants = BUILD.build_premium_variant_panel(zero_proxy, specs)
    keep = [
        "year",
        "state",
        "county_fips",
        "plan_id",
        "issuer_id",
        "issuer_name",
        "plan_marketing_name",
        "metal_level",
        "gross_age_40_premium",
        "ehb_percent_total_premium",
        "non_ehb_age_40_premium",
    ]
    for name in PREMIUM_VARIANTS:
        keep.extend([f"net_premium__{name}", f"zero_flag__{name}", f"positive_flag__{name}"])
    return variants[[col for col in keep if col in variants.columns]].copy()


def build_raw_candidate_audit(manifest: pd.DataFrame, top_two_long: pd.DataFrame, premium_panel: pd.DataFrame) -> pd.DataFrame:
    frames = []
    current_keys = set(
        zip(
            premium_panel["year"].astype(int),
            premium_panel["state"].astype(str),
            premium_panel["county_fips"].astype(str),
            premium_panel["plan_id"].astype(str),
        )
    )
    current_lookup = premium_panel.set_index(["year", "state", "county_fips", "plan_id"], drop=False)
    for previous_year, current_year in TRANSITIONS:
        logging.info("Loading raw crosswalk candidates for %s_to_%s", previous_year, current_year)
        raw = load_raw_crosswalk(manifest, previous_year, current_year)
        prior_top = top_two_long[top_two_long["year"].eq(previous_year)].copy()
        prior_top = prior_top.rename(columns={"year": "previous_top_two_year"})
        part = prior_top.merge(raw, on=["state", "county_fips", "previous_plan_id"], how="left")
        part["transition"] = part["transition"].fillna(f"{previous_year}_to_{current_year}")
        part["previous_year"] = previous_year
        part["current_year"] = current_year
        part["year"] = current_year
        part["mapping_quality_flag"] = part["mapping_quality_flag"].fillna("no_candidate")
        part["source_row_order"] = pd.to_numeric(part["source_row_order"], errors="coerce")
        part["previous_plan_available_as_current_plan_in_same_county"] = [
            (current_year, state, county, plan) in current_keys
            for state, county, plan in zip(part["state"], part["county_fips"], part["previous_plan_id"])
        ]

        prior = premium_panel[premium_panel["year"].eq(previous_year)].rename(
            columns={
                "plan_id": "previous_plan_id",
                "issuer_id": "previous_issuer_id_from_premium_panel",
                "issuer_name": "prior_issuer_name",
                "plan_marketing_name": "prior_plan_marketing_name",
                "metal_level": "prior_metal_level",
                "gross_age_40_premium": "prior_gross_premium",
                "ehb_percent_total_premium": "prior_ehb_percent",
                "non_ehb_age_40_premium": "prior_non_ehb_residual",
            }
        )
        current = premium_panel[premium_panel["year"].eq(current_year)].rename(
            columns={
                "plan_id": "current_plan_id",
                "issuer_id": "current_issuer_id_from_plan_panel",
                "issuer_name": "current_issuer_name",
                "plan_marketing_name": "current_plan_marketing_name",
                "metal_level": "current_metal_level_from_plan_panel",
                "gross_age_40_premium": "current_gross_premium",
                "ehb_percent_total_premium": "current_ehb_percent",
                "non_ehb_age_40_premium": "current_non_ehb_residual",
            }
        )
        for name in PREMIUM_VARIANTS:
            prior = prior.rename(
                columns={
                    f"net_premium__{name}": f"prior_net_{name}",
                    f"zero_flag__{name}": f"prior_zero_under_{name}",
                    f"positive_flag__{name}": f"prior_positive_under_{name}",
                }
            )
            current = current.rename(
                columns={
                    f"net_premium__{name}": f"current_net_{name}",
                    f"zero_flag__{name}": f"current_zero_under_{name}",
                    f"positive_flag__{name}": f"current_positive_under_{name}",
                }
            )
        prior_cols = [
            "year",
            "state",
            "county_fips",
            "previous_plan_id",
            "previous_issuer_id_from_premium_panel",
            "prior_issuer_name",
            "prior_plan_marketing_name",
            "prior_metal_level",
            "prior_gross_premium",
            "prior_ehb_percent",
            "prior_non_ehb_residual",
        ]
        current_cols = [
            "year",
            "state",
            "county_fips",
            "current_plan_id",
            "current_issuer_id_from_plan_panel",
            "current_issuer_name",
            "current_plan_marketing_name",
            "current_metal_level_from_plan_panel",
            "current_gross_premium",
            "current_ehb_percent",
            "current_non_ehb_residual",
        ]
        for name in PREMIUM_VARIANTS:
            prior_cols.extend([f"prior_net_{name}", f"prior_zero_under_{name}", f"prior_positive_under_{name}"])
            current_cols.extend([f"current_net_{name}", f"current_zero_under_{name}", f"current_positive_under_{name}"])
        part = part.merge(
            prior[[col for col in prior_cols if col in prior.columns]].rename(columns={"year": "previous_year"}),
            on=["previous_year", "state", "county_fips", "previous_plan_id"],
            how="left",
        )
        part = part.merge(
            current[[col for col in current_cols if col in current.columns]],
            on=["year", "state", "county_fips", "current_plan_id"],
            how="left",
        )
        if "current_metal_level" not in part.columns:
            part["current_metal_level"] = ""
        part["current_metal_level"] = part["current_metal_level_from_plan_panel"].fillna(part["current_metal_level"])
        part["current_issuer_final"] = part["current_issuer_id_from_plan_panel"].fillna("").astype(str).where(
            part["current_issuer_id_from_plan_panel"].fillna("").astype(str).ne(""),
            part["current_issuer_id_from_crosswalk"].fillna("").astype(str),
        )
        part["current_issuer_final"] = part["current_issuer_final"].map(BUILD.clean_id)
        part["current_issuer_id_from_plan_panel"] = part["current_issuer_id_from_plan_panel"].map(BUILD.clean_id)
        part["current_issuer_id_from_crosswalk"] = part["current_issuer_id_from_crosswalk"].map(BUILD.clean_id)
        part["previous_issuer_id_from_crosswalk"] = part["previous_issuer_id_from_crosswalk"].fillna("")
        part["previous_issuer_id_from_prior_panel"] = part["previous_issuer_id_from_prior_panel"].map(BUILD.clean_id)
        prior_issuer = part["previous_issuer_id_from_prior_panel"].fillna("").astype(str)
        current_issuer = part["current_issuer_final"].fillna("").astype(str)
        part["same_plan_id_candidate"] = part["previous_plan_id"].fillna("").astype(str).eq(part["current_plan_id"].fillna("").astype(str))
        part["same_issuer_candidate"] = prior_issuer.ne("") & current_issuer.ne("") & prior_issuer.eq(current_issuer)
        part["across_issuer_candidate"] = prior_issuer.ne("") & current_issuer.ne("") & prior_issuer.ne(current_issuer)
        part["reason8_candidate"] = part["reason_for_crosswalk_num"].eq(8).fillna(False)
        part["level3_zip_candidate"] = part["crosswalk_level_num"].eq(3).fillna(False)
        part["level4_or_5_no_reenrollment_candidate"] = part["crosswalk_level_num"].isin([4, 5]).fillna(False)
        for name in PREMIUM_VARIANTS:
            part[f"prior_zero_under_{name}"] = part[f"prior_zero_under_{name}"].astype("boolean")
            part[f"current_positive_under_{name}"] = part[f"current_positive_under_{name}"].astype("boolean")
            part[f"zero_to_positive_under_{name}"] = (
                part[f"prior_zero_under_{name}"].fillna(False).astype(bool)
                & part[f"current_positive_under_{name}"].fillna(False).astype(bool)
            )
        frames.append(part)
    out = pd.concat(frames, ignore_index=True)
    return out


def add_synthetic_same_plan_candidates(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    key_cols = ["transition", "year", "state", "county_fips", "rank", "previous_plan_id"]
    for _, g in candidates.groupby(key_cols, dropna=False):
        rows.append(g)
        has_same_raw = bool(g["same_plan_id_candidate"].fillna(False).any())
        available = bool(g["previous_plan_available_as_current_plan_in_same_county"].fillna(False).any())
        if available and not has_same_raw:
            base = g.iloc[[0]].copy()
            base["current_plan_id"] = base["previous_plan_id"]
            base["current_plan_id_raw"] = base["previous_plan_id"]
            base["current_issuer_id_from_crosswalk"] = ""
            base["crosswalk_level"] = "synthetic_same_plan_available"
            base["crosswalk_level_num"] = -1
            base["reason_for_crosswalk"] = "synthetic_same_plan_available"
            base["reason_for_crosswalk_num"] = np.nan
            base["zip_code"] = "synthetic"
            base["source_row_order"] = -1
            base["mapping_quality_flag"] = "synthetic_same_plan_available"
            base["valid_mapped_candidate"] = True
            base["same_plan_id_candidate"] = True
            base["level4_or_5_no_reenrollment_candidate"] = False
            rows.append(base)
    return pd.concat(rows, ignore_index=True)


def select_default_rows(candidates: pd.DataFrame, rule: str) -> pd.DataFrame:
    if rule in {"same_plan_if_available_else_source_order", "same_plan_if_available_else_lowest_level"}:
        candidates = add_synthetic_same_plan_candidates(candidates)
    if rule in {"county_any_zip_turnover", "county_any_zip_across_turnover"}:
        out = candidates.copy()
        out["default_mapping_rule"] = rule
        out["selected_valid_current_plan"] = out["valid_mapped_candidate"].astype("boolean").fillna(False).astype(bool)
        return out

    c = candidates.copy()
    c["_valid"] = c["valid_mapped_candidate"].astype("boolean").fillna(False).astype(bool)
    c["_source_order_sort"] = pd.to_numeric(c["source_row_order"], errors="coerce").fillna(10**12)
    c["_level_sort"] = pd.to_numeric(c["crosswalk_level_num"], errors="coerce").fillna(9999)
    c["_mapped_sort"] = np.where(c["mapping_quality_flag"].eq("mapped") | c["mapping_quality_flag"].eq("synthetic_same_plan_available"), 0, 1)
    c["_silver_sort"] = np.where(c["current_metal_level"].astype(str).str.lower().str.contains("silver", na=False), 0, 1)
    c["_same_sort"] = np.where(c["same_issuer_candidate"].fillna(False), 0, 1)
    c["_same_plan_sort"] = np.where(c["same_plan_id_candidate"].fillna(False), 0, 1)
    c["_reason8_sort"] = np.where(c["reason8_candidate"].fillna(False), 0, 1)
    c["_zip00000_sort"] = np.where(c["zip_00000_candidate"].astype("boolean").fillna(False).astype(bool), 0, 1) if "zip_00000_candidate" in c.columns else 1
    c["_valid_not45_sort"] = np.where(c["_valid"] & ~c["crosswalk_level_num"].isin([4, 5]), 0, 1)
    if rule == "current_repo_rule":
        sort_cols = ["_mapped_sort", "_silver_sort", "_same_sort", "_level_sort", "current_plan_id", "current_issuer_final"]
    elif rule == "no_same_issuer_priority":
        sort_cols = ["_mapped_sort", "_silver_sort", "_level_sort", "_source_order_sort", "current_plan_id"]
    elif rule == "source_order_first_valid":
        sort_cols = ["_mapped_sort", "_source_order_sort"]
    elif rule == "lowest_crosswalk_level":
        sort_cols = ["_mapped_sort", "_level_sort", "_source_order_sort"]
    elif rule == "same_plan_if_available_else_source_order":
        sort_cols = ["_same_plan_sort", "_mapped_sort", "_source_order_sort"]
    elif rule == "same_plan_if_available_else_lowest_level":
        sort_cols = ["_same_plan_sort", "_mapped_sort", "_level_sort", "_source_order_sort"]
    elif rule == "whole_county_00000_only":
        sort_cols = ["_zip00000_sort", "_mapped_sort", "_source_order_sort"]
    elif rule == "reason8_priority":
        sort_cols = ["_mapped_sort", "_reason8_sort", "_source_order_sort"]
    elif rule == "exclude_level4_5":
        sort_cols = ["_valid_not45_sort", "_level_sort", "_source_order_sort"]
    elif rule == "include_level4_5_as_missing_current":
        c["_level45_sort"] = np.where(c["crosswalk_level_num"].isin([4, 5]), 0, 1)
        sort_cols = ["_level45_sort", "_mapped_sort", "_source_order_sort"]
    else:
        raise ValueError(f"Unknown default mapping rule: {rule}")

    key_cols = ["transition", "year", "state", "county_fips", "rank", "previous_plan_id"]
    selected = c.sort_values([*key_cols, *sort_cols], kind="mergesort").drop_duplicates(key_cols, keep="first").copy()
    selected["default_mapping_rule"] = rule
    selected["selected_valid_current_plan"] = selected["_valid"].fillna(False)
    if rule == "include_level4_5_as_missing_current":
        level45 = selected["crosswalk_level_num"].isin([4, 5])
        selected.loc[level45, "selected_valid_current_plan"] = False
    selected = selected.drop(columns=[col for col in selected.columns if col.startswith("_")], errors="ignore")
    return selected


def add_candidate_group_flags(selected: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    key_cols = ["transition", "year", "state", "county_fips", "rank", "previous_plan_id"]
    rows = []
    for name in PREMIUM_VARIANTS:
        temp = candidates.copy()
        temp["ztp"] = temp[f"zero_to_positive_under_{name}"].fillna(False).astype(bool)
        temp["ztp_across"] = temp["ztp"] & temp["across_issuer_candidate"].fillna(False).astype(bool)
        temp["ztp_same"] = temp["ztp"] & temp["same_issuer_candidate"].fillna(False).astype(bool)
        temp["reason8_ztp"] = temp["ztp"] & temp["reason8_candidate"].fillna(False).astype(bool)
        temp["level3_ztp"] = temp["ztp"] & temp["level3_zip_candidate"].fillna(False).astype(bool)
        summary = (
            temp.groupby(key_cols, dropna=False)
            .agg(
                raw_candidate_rows=("current_plan_id", "size"),
                raw_candidate_across_exists=("across_issuer_candidate", "max"),
                raw_candidate_same_exists=("same_issuer_candidate", "max"),
                zero_to_positive_candidate_exists=("ztp", "max"),
                zero_to_positive_across_candidate_exists=("ztp_across", "max"),
                zero_to_positive_same_candidate_exists=("ztp_same", "max"),
                reason8_candidate_exists=("reason8_candidate", "max"),
                reason8_zero_to_positive_exists=("reason8_ztp", "max"),
                zip_level_candidate_exists=("level3_zip_candidate", "max"),
                zip_level_zero_to_positive_exists=("level3_ztp", "max"),
                level4_or_5_candidate_exists=("level4_or_5_no_reenrollment_candidate", "max"),
            )
            .reset_index()
        )
        summary["premium_variant"] = name
        rows.append(summary)
    flags = pd.concat(rows, ignore_index=True)
    out = selected.merge(flags, on=key_cols, how="left")
    return out


def long_by_premium_variant(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name in PREMIUM_VARIANTS:
        temp = selected.copy()
        temp["premium_variant"] = name
        temp["prior_zero"] = temp[f"prior_zero_under_{name}"].fillna(False).astype(bool)
        temp["current_positive"] = temp[f"current_positive_under_{name}"].fillna(False).astype(bool)
        temp["current_zero"] = temp.get(f"current_zero_under_{name}", pd.Series(False, index=temp.index)).astype("boolean").fillna(False).astype(bool)
        temp["prior_premium_missing"] = temp[f"prior_net_{name}"].isna()
        temp["current_premium_missing"] = temp[f"current_net_{name}"].isna()
        temp["zero_to_positive"] = temp["prior_zero"] & temp["current_positive"]
        temp["same_issuer"] = temp["same_issuer_candidate"].fillna(False).astype(bool)
        temp["across_issuer"] = temp["across_issuer_candidate"].fillna(False).astype(bool)
        temp["issuer_missing"] = temp["zero_to_positive"] & ~(temp["same_issuer"] | temp["across_issuer"])
        temp["no_valid_crosswalk"] = ~temp["selected_valid_current_plan"].fillna(False).astype(bool)
        temp["current_plan_missing"] = temp["current_plan_id"].fillna("").astype(str).eq("") | temp["mapping_quality_flag"].isin(["unmapped_or_placeholder", "no_candidate"])
        temp["crosswalk_level_4_or_5"] = temp["crosswalk_level_num"].isin([4, 5]).fillna(False)
        temp["turnover_failure_reason"] = np.select(
            [
                temp["zero_to_positive"],
                temp["crosswalk_level_4_or_5"],
                temp["no_valid_crosswalk"],
                temp["current_plan_missing"],
                temp["prior_premium_missing"],
                temp["current_premium_missing"],
                (~temp["prior_zero"]) & temp["current_positive"],
                temp["prior_zero"] & temp["current_zero"],
                temp["prior_zero"] & ~temp["current_positive"],
            ],
            [
                "turnover",
                "crosswalk_level_4_or_5",
                "no_valid_crosswalk",
                "current_plan_missing",
                "prior_premium_missing",
                "current_premium_missing",
                "both_positive",
                "both_zero",
                "current_not_positive",
            ],
            default="prior_not_zero",
        )
        temp["across_failure_reason"] = np.select(
            [
                temp["zero_to_positive"] & temp["across_issuer"],
                temp["zero_to_positive"] & temp["same_issuer"] & temp["zero_to_positive_across_candidate_exists"].fillna(False).astype(bool),
                temp["zero_to_positive"] & temp["same_issuer"],
                temp["zero_to_positive"] & temp["issuer_missing"],
                (~temp["zero_to_positive"]) & temp["zero_to_positive_across_candidate_exists"].fillna(False).astype(bool),
                temp["reason8_candidate_exists"].fillna(False).astype(bool),
                temp["zip_level_candidate_exists"].fillna(False).astype(bool) & temp["raw_candidate_across_exists"].fillna(False).astype(bool),
            ],
            [
                "across_turnover",
                "selected_same_issuer_candidate",
                "zero_to_positive_but_same_issuer",
                "zero_to_positive_but_issuer_missing",
                "across_candidate_exists_but_not_selected",
                "reason8_candidate_exists",
                "zip_level_across_candidate_exists",
            ],
            default=temp["turnover_failure_reason"],
        )
        rows.append(temp)
    return pd.concat(rows, ignore_index=True)


def summarize_counts(long: pd.DataFrame, final: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    final_key = final[
        ["year", "state", "county_fips", "Cnsmr", "included_drake_harmonized_sample"]
    ].copy()
    final_key = final_key[final_key["included_drake_harmonized_sample"].fillna(False).astype(bool)].copy()
    rows = []
    state_rows = []
    for (rule, premium), g in long.groupby(["default_mapping_rule", "premium_variant"], dropna=False):
        rank_valid = (
            g.groupby(["year", "state", "county_fips", "rank"], dropna=False)
            .agg(
                rank_has_valid=("selected_valid_current_plan", "max"),
                rank_prior_premium_missing=("prior_premium_missing", "max"),
                rank_current_premium_missing=("current_premium_missing", "max"),
                rank_turnover=("zero_to_positive", "max"),
                rank_across=("across_issuer", lambda s: bool((g.loc[s.index, "zero_to_positive"] & s).any())),
                rank_within=("same_issuer", lambda s: bool((g.loc[s.index, "zero_to_positive"] & s).any())),
            )
            .reset_index()
        )
        county = (
            rank_valid.groupby(["year", "state", "county_fips"], dropna=False)
            .agg(
                rank_count=("rank", "nunique"),
                all_ranks_valid=("rank_has_valid", "min"),
                any_prior_premium_missing=("rank_prior_premium_missing", "max"),
                any_current_premium_missing=("rank_current_premium_missing", "max"),
                any_zero_to_positive_turnover=("rank_turnover", "max"),
                any_zero_to_positive_turnover_across_issuer=("rank_across", "max"),
                any_zero_to_positive_turnover_within_issuer=("rank_within", "max"),
            )
            .reset_index()
        )
        merged = final_key.merge(county, on=["year", "state", "county_fips"], how="left")
        merged["rank_count"] = merged["rank_count"].fillna(0).astype(int)
        for col in [
            "all_ranks_valid",
            "any_prior_premium_missing",
            "any_current_premium_missing",
            "any_zero_to_positive_turnover",
            "any_zero_to_positive_turnover_across_issuer",
            "any_zero_to_positive_turnover_within_issuer",
        ]:
            merged[col] = merged[col].astype("boolean").fillna(False).astype(bool)
        constructible = (
            merged["rank_count"].ge(2)
            & merged["all_ranks_valid"]
            & ~merged["any_prior_premium_missing"]
            & ~merged["any_current_premium_missing"]
        )
        analytic = merged[constructible].copy()
        by_year = analytic.groupby("year", dropna=False).agg(
            any_count=("any_zero_to_positive_turnover", "sum"),
            across_count=("any_zero_to_positive_turnover_across_issuer", "sum"),
        )
        pooled_any = int(analytic["any_zero_to_positive_turnover"].sum())
        pooled_across = int(analytic["any_zero_to_positive_turnover_across_issuer"].sum())
        pooled_within = int(analytic["any_zero_to_positive_turnover_within_issuer"].sum())
        any_enrollee = float(analytic.loc[analytic["any_zero_to_positive_turnover"], "Cnsmr"].sum(skipna=True) / 1_000_000)
        across_enrollee = float(analytic.loc[analytic["any_zero_to_positive_turnover_across_issuer"], "Cnsmr"].sum(skipna=True) / 1_000_000)
        support, notes = DEFAULT_RULE_SUPPORT[rule]
        rows.append(
            {
                "default_mapping_rule": rule,
                "premium_variant": premium,
                "issuer_concept": "plan_panel_preferred",
                "pooled_any_turnover_county_years": pooled_any,
                "pooled_across_issuer_turnover_county_years": pooled_across,
                "pooled_within_issuer_turnover_county_years": pooled_within,
                "pooled_any_turnover_enrollee_years_millions": any_enrollee,
                "pooled_across_issuer_enrollee_years_millions": across_enrollee,
                "difference_vs_drake_any_count": pooled_any - DRAKE_ANCHORS["any_turnover_county_years"],
                "difference_vs_drake_across_count": pooled_across - DRAKE_ANCHORS["across_issuer_turnover_county_years"],
                "difference_vs_drake_any_enrollee_millions": any_enrollee - DRAKE_ANCHORS["any_turnover_enrollee_years_millions"],
                "difference_vs_drake_across_enrollee_millions": across_enrollee - DRAKE_ANCHORS["across_issuer_enrollee_years_millions"],
                "by_year_2022_any": int(by_year.loc[2022, "any_count"]) if 2022 in by_year.index else 0,
                "by_year_2023_any": int(by_year.loc[2023, "any_count"]) if 2023 in by_year.index else 0,
                "by_year_2024_any": int(by_year.loc[2024, "any_count"]) if 2024 in by_year.index else 0,
                "by_year_2022_across": int(by_year.loc[2022, "across_count"]) if 2022 in by_year.index else 0,
                "by_year_2023_across": int(by_year.loc[2023, "across_count"]) if 2023 in by_year.index else 0,
                "by_year_2024_across": int(by_year.loc[2024, "across_count"]) if 2024 in by_year.index else 0,
                "constructible_county_years": int(len(analytic)),
                "drake_text_support": support,
                "notes": notes,
            }
        )
        by_state = (
            analytic.groupby(["year", "state"], dropna=False)
            .agg(
                county_years=("county_fips", "size"),
                any_turnover_county_years=("any_zero_to_positive_turnover", "sum"),
                across_issuer_turnover_county_years=("any_zero_to_positive_turnover_across_issuer", "sum"),
                within_issuer_turnover_county_years=("any_zero_to_positive_turnover_within_issuer", "sum"),
                enrollment=("Cnsmr", "sum"),
                any_enrollment=("Cnsmr", lambda s: float(s[analytic.loc[s.index, "any_zero_to_positive_turnover"]].sum(skipna=True))),
                across_enrollment=("Cnsmr", lambda s: float(s[analytic.loc[s.index, "any_zero_to_positive_turnover_across_issuer"]].sum(skipna=True))),
            )
            .reset_index()
        )
        by_state["default_mapping_rule"] = rule
        by_state["premium_variant"] = premium
        by_state["issuer_concept"] = "plan_panel_preferred"
        by_state["any_enrollment_weighted_exposure"] = by_state["any_enrollment"] / by_state["enrollment"]
        by_state["across_enrollment_weighted_exposure"] = by_state["across_enrollment"] / by_state["enrollment"]
        state_rows.extend(
            by_state[
                [
                    "default_mapping_rule",
                    "premium_variant",
                    "issuer_concept",
                    "year",
                    "state",
                    "county_years",
                    "any_turnover_county_years",
                    "across_issuer_turnover_county_years",
                    "within_issuer_turnover_county_years",
                    "enrollment",
                    "any_enrollment_weighted_exposure",
                    "across_enrollment_weighted_exposure",
                ]
            ].to_dict("records")
        )
    return pd.DataFrame(rows), pd.DataFrame(state_rows)


def write_failure_reason_outputs(long: pd.DataFrame) -> None:
    turnover = (
        long.groupby(["year", "state", "rank", "premium_variant", "default_mapping_rule", "turnover_failure_reason"], dropna=False)
        .size()
        .reset_index(name="plan_pair_rows")
    )
    turnover["turnover_rows"] = np.where(turnover["turnover_failure_reason"].eq("turnover"), turnover["plan_pair_rows"], 0)
    turnover["non_turnover_rows"] = np.where(~turnover["turnover_failure_reason"].eq("turnover"), turnover["plan_pair_rows"], 0)
    turnover.to_csv(OUTPUTS / "turnover_failure_reason_by_variant.csv", index=False)

    across = (
        long.groupby(["year", "state", "rank", "premium_variant", "default_mapping_rule", "across_failure_reason"], dropna=False)
        .size()
        .reset_index(name="plan_pair_rows")
    )
    across["across_turnover_rows"] = np.where(across["across_failure_reason"].eq("across_turnover"), across["plan_pair_rows"], 0)
    across["non_across_rows"] = np.where(~across["across_failure_reason"].eq("across_turnover"), across["plan_pair_rows"], 0)
    across.to_csv(OUTPUTS / "across_issuer_failure_reason_by_variant.csv", index=False)


def write_across_gap_diagnosis(long: pd.DataFrame, comparison: pd.DataFrame) -> pd.DataFrame:
    rows = []
    current = comparison[
        comparison["default_mapping_rule"].eq("current_repo_rule")
    ][["premium_variant", "pooled_across_issuer_turnover_county_years"]].rename(
        columns={"pooled_across_issuer_turnover_county_years": "current_rule_across_count"}
    )
    for (year, state, rule, premium), g in long.groupby(["year", "state", "default_mapping_rule", "premium_variant"], dropna=False):
        county = (
            g.groupby(["county_fips"], dropna=False)
            .agg(
                selected_across=("across_issuer", lambda s: bool((g.loc[s.index, "zero_to_positive"] & s).any())),
                raw_candidate_across=("raw_candidate_across_exists", "max"),
                ztp_across_candidate=("zero_to_positive_across_candidate_exists", "max"),
                selected_same_but_across_candidate=("same_issuer", lambda s: bool((g.loc[s.index, "zero_to_positive"] & s & g.loc[s.index, "zero_to_positive_across_candidate_exists"].fillna(False).astype(bool)).any())),
                selected_nonturnover_but_turnover_candidate=("zero_to_positive_candidate_exists", lambda s: bool((~g.loc[s.index, "zero_to_positive"] & s.fillna(False).astype(bool)).any())),
                reason8_candidate=("reason8_candidate_exists", "max"),
                reason8_zero_to_positive=("reason8_zero_to_positive_exists", "max"),
                level3_zip_candidate=("zip_level_candidate_exists", "max"),
                level3_zip_zero_to_positive=("zip_level_zero_to_positive_exists", "max"),
                county_any_zip_across=("zero_to_positive_across_candidate_exists", "max"),
            )
            .reset_index()
        )
        rows.append(
            {
                "year": year,
                "state": state,
                "default_mapping_rule": rule,
                "premium_variant": premium,
                "selected_across_count": int(county["selected_across"].sum()),
                "raw_candidate_across_count": int(county["raw_candidate_across"].sum()),
                "zero_to_positive_across_candidate_count": int(county["ztp_across_candidate"].sum()),
                "selected_same_but_across_candidate_exists_count": int(county["selected_same_but_across_candidate"].sum()),
                "selected_nonturnover_but_turnover_candidate_exists_count": int(county["selected_nonturnover_but_turnover_candidate"].sum()),
                "reason8_candidate_count": int(county["reason8_candidate"].sum()),
                "reason8_zero_to_positive_count": int(county["reason8_zero_to_positive"].sum()),
                "level3_zip_candidate_count": int(county["level3_zip_candidate"].sum()),
                "level3_zip_zero_to_positive_count": int(county["level3_zip_zero_to_positive"].sum()),
                "county_any_zip_across_count": int(county["county_any_zip_across"].sum()),
            }
        )
    out = pd.DataFrame(rows)
    current_state = out[out["default_mapping_rule"].eq("current_repo_rule")][
        ["year", "state", "premium_variant", "selected_across_count"]
    ].rename(columns={"selected_across_count": "current_rule_selected_across_count"})
    out = out.merge(current_state, on=["year", "state", "premium_variant"], how="left")
    out["difference_vs_current_rule"] = out["selected_across_count"] - out["current_rule_selected_across_count"]
    yearly_anchor = {2022: np.nan, 2023: np.nan, 2024: np.nan}
    out["difference_vs_drake_anchor_if_available"] = out["year"].map(yearly_anchor)
    out.to_csv(OUTPUTS / "crosswalk_across_gap_diagnosis.csv", index=False)
    return out


def write_reason_level_distribution(candidates: pd.DataFrame, long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    raw = candidates.copy()
    for col, label in [("crosswalk_level", "raw_candidates_by_crosswalk_level"), ("reason_for_crosswalk", "raw_candidates_by_reason")]:
        temp = raw.groupby([col], dropna=False).size().reset_index(name="rows")
        for _, row in temp.iterrows():
            rows.append({"scope": label, "default_mapping_rule": "raw", "premium_variant": "", "crosswalk_level": row.get("crosswalk_level", ""), "reason_for_crosswalk": row.get("reason_for_crosswalk", ""), "rows": int(row["rows"])})
    for (rule, premium), g in long.groupby(["default_mapping_rule", "premium_variant"], dropna=False):
        for _, row in g.groupby(["crosswalk_level", "reason_for_crosswalk"], dropna=False).agg(
            selected_rows=("rank", "size"),
            zero_to_positive_rows=("zero_to_positive", "sum"),
            across_rows=("across_issuer", lambda s: int((g.loc[s.index, "zero_to_positive"] & s).sum())),
            reason8_rows=("reason8_candidate", "sum"),
        ).reset_index().iterrows():
            rows.append(
                {
                    "scope": "selected_rows_by_level_reason",
                    "default_mapping_rule": rule,
                    "premium_variant": premium,
                    "crosswalk_level": row["crosswalk_level"],
                    "reason_for_crosswalk": row["reason_for_crosswalk"],
                    "rows": int(row["selected_rows"]),
                    "zero_to_positive_rows": int(row["zero_to_positive_rows"]),
                    "across_rows": int(row["across_rows"]),
                    "reason8_rows": int(row["reason8_rows"]),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "crosswalk_reason_level_distribution.csv", index=False)
    return out


def write_kansas_audit(long: pd.DataFrame) -> pd.DataFrame:
    ks = long[
        long["state"].eq("KS")
        & long["year"].eq(2022)
        & long["premium_variant"].eq("current_ehb_all_states")
    ].copy()
    rows = []
    for (county, rank, prev_plan), g in ks.groupby(["county_fips", "rank", "previous_plan_id"], dropna=False):
        row: dict[str, Any] = {
            "county_fips": county,
            "rank": rank,
            "previous_plan_id": prev_plan,
            "previous_issuer_id": joined_unique(g["previous_issuer_id_from_prior_panel"]),
            "prior_plan_marketing_name": joined_unique(g["prior_plan_marketing_name"]),
            "all_candidate_current_plan_ids": joined_unique(g["current_plan_id"]),
            "all_candidate_current_issuer_ids": joined_unique(g["current_issuer_final"]),
            "all_candidate_zip_codes": joined_unique(g["zip_code"]),
            "all_candidate_crosswalk_levels": joined_unique(g["crosswalk_level"]),
            "all_candidate_reasons": joined_unique(g["reason_for_crosswalk"]),
        }
        current_rule = g[g["default_mapping_rule"].eq("current_repo_rule")]
        row["current_repo_selected_plan"] = joined_unique(current_rule["current_plan_id"])
        for rule in DEFAULT_RULES:
            rg = g[g["default_mapping_rule"].eq(rule)]
            row[f"selected_plan__{rule}"] = joined_unique(rg["current_plan_id"])
            row[f"selected_issuer__{rule}"] = joined_unique(rg["current_issuer_final"])
            row[f"across_issuer__{rule}"] = bool((rg["zero_to_positive"] & rg["across_issuer"]).any())
            row[f"zero_to_positive__{rule}"] = bool(rg["zero_to_positive"].any())
            row[f"same_issuer__{rule}"] = bool((rg["zero_to_positive"] & rg["same_issuer"]).any())
            row[f"differs_from_current_repo__{rule}"] = row[f"selected_plan__{rule}"] != row["current_repo_selected_plan"]
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "kansas_2021_2022_crosswalk_default_audit.csv", index=False)
    return out


def write_raw_candidate_audit(candidates: pd.DataFrame) -> None:
    keep = [
        "transition",
        "previous_year",
        "current_year",
        "year",
        "state",
        "county_fips",
        "zip_code",
        "rank",
        "previous_plan_id",
        "previous_issuer_id_from_prior_panel",
        "previous_issuer_id_from_crosswalk",
        "previous_metal_level",
        "current_plan_id",
        "current_issuer_id_from_crosswalk",
        "current_plan_id_raw",
        "current_metal_level",
        "crosswalk_level",
        "crosswalk_level_num",
        "reason_for_crosswalk",
        "mapping_quality_flag",
        "source_row_order",
        "previous_plan_available_as_current_plan_in_same_county",
        "same_plan_id_candidate",
        "same_issuer_candidate",
        "across_issuer_candidate",
        "reason8_candidate",
        "level3_zip_candidate",
        "level4_or_5_no_reenrollment_candidate",
    ]
    for name in PREMIUM_VARIANTS:
        keep.extend([f"prior_zero_under_{name}", f"current_positive_under_{name}", f"zero_to_positive_under_{name}"])
    out = candidates[[col for col in keep if col in candidates.columns]].copy()
    out.to_csv(OUTPUTS / "crosswalk_raw_candidate_audit.csv", index=False)


def write_rule_extraction_doc() -> None:
    text = """# Crosswalk Default Mapping Rule Extraction

## Confirmed From Drake

- Drake describes defaulting through the CCIIO Plan ID Crosswalk: if available, a plan defaults to itself; if not, a similar plan becomes the default.
- Drake defines treatment using the prior-year lowest and second-lowest silver plans and their current-year default plans.
- Drake defines across-insurer turnover when the default current-year plan is offered by a different insurer.
- Drake does not state how duplicate Crosswalk rows are resolved.
- Drake does not state how ZIP-level Crosswalk rows are collapsed to county-year treatment.
- Drake does not state that any ZIP-level default change is sufficient to treat a county-year.
- Drake does not state special handling for ReasonForCrosswalk = 8.
- Drake does not state whether CrosswalkLevel 4/5 rows are excluded or treated as nonconstructible.

## Confirmed From CMS Documentation

- CMS Plan ID Crosswalk PUF is an Exchange PUF data product available from the CMS Exchange PUF page.
- CMS Plan ID Crosswalk Data Dictionary defines `FIPSCode` as the county FIPS field and `ZipCode` as ZIP-level geography.
- CMS documentation says `ZipCode = 00000` means the issuer did not split the county into ZIP codes and the entire county is covered.
- CrosswalkLevel values identify default mapping level: 0 same Plan ID, 1 Plan ID level, 2 Plan ID plus county coverage level, 3 ZIP-code level, 4 no reenrollment option, and 5 withdrawn/no enrollment option.
- ReasonForCrosswalk values include 0, 1, 2, 3, 6, 7, 8, and 10; Reason 8 means crosswalk to a different issuer determined by CMS, not the existing issuer.

CMS sources used:
- https://www.cms.gov/marketplace/resources/data/public-use-files
- https://www.cms.gov/files/document/plan-id-crosswalk-datadictionary-py26.pdf

## Repo Assumptions

- The current repo rule selects one row per state/county/prior plan after filtering dental plans and prior silver plans.
- The current repo rule prioritizes mapped current plans, current silver metal, same issuer, lowest numeric CrosswalkLevel, then lexical current plan/issuer IDs.
- County-year treatment is true if either prior top-two silver plan has selected zero-to-positive turnover.

## Diagnostic-Only Sensitivities

- Removing same-issuer priority.
- Using raw source order.
- Selecting the lowest CrosswalkLevel.
- Preferring county-wide `00000` rows.
- Treating any ZIP-level candidate as enough to classify county-year turnover.
- Prioritizing ReasonForCrosswalk = 8.
"""
    (DOCS / "crosswalk_default_mapping_rule_extraction.md").write_text(text, encoding="utf-8")


def write_reconciliation_report(comparison: pd.DataFrame, gap: pd.DataFrame, ks: pd.DataFrame, candidates: pd.DataFrame) -> None:
    baseline = comparison[
        comparison["default_mapping_rule"].eq("current_repo_rule")
        & comparison["premium_variant"].eq("current_ehb_all_states")
    ]
    plausible = comparison[comparison["drake_text_support"].isin(["confirmed", "plausible"])].copy()
    plausible["abs_gap"] = plausible["difference_vs_drake_any_count"].abs() + plausible["difference_vs_drake_across_count"].abs()
    closest_plausible = plausible.sort_values("abs_gap").head(8)
    all_rules = comparison.copy()
    all_rules["abs_gap"] = all_rules["difference_vs_drake_any_count"].abs() + all_rules["difference_vs_drake_across_count"].abs()
    closest_numeric = all_rules.sort_values("abs_gap").head(8)
    ks_summary = []
    for rule in DEFAULT_RULES:
        col = f"across_issuer__{rule}"
        if col in ks.columns:
            ks_summary.append({"default_mapping_rule": rule, "ks_counties_with_across": int(ks.loc[ks[col].astype(bool), "county_fips"].nunique())})
    ks_table = pd.DataFrame(ks_summary)
    candidate_group_count = candidates.groupby(["transition", "state", "county_fips", "rank", "previous_plan_id"], dropna=False).ngroups
    duplicate_candidate_groups = int(
        (candidates.groupby(["transition", "state", "county_fips", "rank", "previous_plan_id"], dropna=False).size() > 1).sum()
    )
    raw_candidate_rows = len(candidates)
    display_cols = [
        "default_mapping_rule",
        "premium_variant",
        "pooled_any_turnover_county_years",
        "pooled_across_issuer_turnover_county_years",
        "pooled_any_turnover_enrollee_years_millions",
        "pooled_across_issuer_enrollee_years_millions",
        "difference_vs_drake_any_count",
        "difference_vs_drake_across_count",
        "drake_text_support",
    ]
    text = [
        "# Crosswalk Default Mapping Reconciliation Report",
        "",
        "## 1. Executive Diagnosis",
        "",
        "Premium variants did not close the Drake treatment gap, so this audit tests Plan ID Crosswalk default-row selection. The current repo rule remains a plausible but not fully confirmed implementation. No tested default mapping rule simultaneously reproduces Drake's 4452 any-turnover county-years and 211 across-insurer county-years with text support. Step 4 remains **No-Go**.",
        "",
        f"Key diagnostic result: among prior top-two silver plan pairs, the raw candidate audit found {raw_candidate_rows} joined candidate rows across {candidate_group_count} plan-pair groups, with {duplicate_candidate_groups} groups having more than one raw candidate row. In this constructed public-file sample, duplicate/default-row choice does not move the treatment counts.",
        "",
        "## 2. What Drake Says About Default Mapping",
        "",
        "Drake states that prior-year top-two silver plans default through the Plan ID Crosswalk: if the same plan is available it defaults to itself; otherwise a similar plan becomes the new default. Drake does not disclose duplicate-row resolution, ZIP-to-county aggregation, ReasonForCrosswalk priority, or CrosswalkLevel 4/5 handling.",
        "",
        "## 3. What CMS Plan ID Crosswalk Documentation Says",
        "",
        "CMS defines FIPSCode, ZipCode, CrosswalkLevel, and ReasonForCrosswalk in the Plan ID Crosswalk Data Dictionary. `ZipCode = 00000` means the county was not split into ZIP rows. CrosswalkLevel 0-3 identify same-plan, plan-level, county-coverage, and ZIP-level mappings; levels 4 and 5 indicate no reenrollment/default option. ReasonForCrosswalk = 8 is a CMS-determined crosswalk to a different issuer.",
        "",
        "## 4. Current Repo Default Mapping Rule",
        "",
        "The current repo selects one row per state/county/prior plan after filtering to nondental prior silver rows. It prioritizes mapped current plans, current silver metal, same issuer, lowest CrosswalkLevel, then current plan/issuer IDs.",
        "",
        "## 5. Same-Issuer Priority",
        "",
        "Same-issuer priority can suppress across-insurer rows when a same-issuer and across-issuer candidate coexist. The diagnostic variants remove this priority and directly measure whether across-insurer counts increase.",
        "",
        "In the current joined prior-top-two universe, no plan-pair group has multiple raw candidates, so removing same-issuer priority does not change any Drake-harmonized treatment count.",
        "",
        "## 6. ZIP-Level Versus County-Level Aggregation",
        "",
        "`county_any_zip_turnover` and `county_any_zip_across_turnover` test whether any ZIP-level candidate is enough to classify a county-year. These are diagnostic only because Drake does not say that ZIP-level candidate existence alone defines county-year treatment.",
        "",
        "In this audit, ZIP-level and any-ZIP diagnostic rules do not change the pooled Drake-harmonized counts. The across-insurer gap is therefore not explained by county aggregation of alternative ZIP-level candidate rows.",
        "",
        "## 7. Default Mapping Variant Comparison",
        "",
        markdown_table(comparison[display_cols].sort_values(["premium_variant", "default_mapping_rule"]).head(80)),
        "",
        "Closest plausible/text-supported rows:",
        "",
        markdown_table(closest_plausible[display_cols]),
        "",
        "Closest numeric rows, including diagnostic-only rules:",
        "",
        markdown_table(closest_numeric[display_cols]),
        "",
        "## 8. Across-Insurer Gap Diagnosis",
        "",
        "The across-gap file reports, by state-year and rule, whether raw across candidates exist but are not selected, whether Reason 8 candidates exist, and whether ZIP-level candidates could explain the gap. In this run, none of the default-row rules changes the pooled across-insurer count. That means the remaining across-insurer mismatch is not fixed by same-issuer priority, Reason 8 priority, CrosswalkLevel priority, or ZIP-level candidate aggregation in the joined public-file Crosswalk rows.",
        "",
        "## 9. Kansas 2022 Conclusion",
        "",
        markdown_table(ks_table),
        "",
        "Kansas 2022 is not primarily a premium-calculation artifact. This audit checks whether it persists under source-order, lowest-level, same-plan, ZIP, and Reason 8 rules. A rule that removes Kansas solely by diagnostic priority is not automatically more faithful.",
        "",
        "## 10. Whether Any Rule Matches Drake Anchors",
        "",
        "No tested text-supported rule exactly matches both Drake anchors. No diagnostic-only default-row rule moves the pooled Drake-harmonized anchors either. The crosswalk default-row rule does not appear to be the main remaining source of the treatment mismatch in the current public-file construction.",
        "",
        "## 11. Recommended Rule Going Forward",
        "",
        "Keep `current_repo_rule` as the baseline until a more exact Drake rule is documented. Treat same-plan-if-available variants as plausible sensitivities and any-ZIP/Reason 8 variants as diagnostics.",
        "",
        "## 12. Step 4 Recommendation",
        "",
        "**No-Go for Step 4.** The project should continue Step 2 treatment repair until the crosswalk/default-row rule is either reproduced from Drake's implementation or the remaining mismatch is explicitly bounded and justified.",
        "",
    ]
    (DOCS / "crosswalk_default_mapping_reconciliation_report.md").write_text("\n".join(text), encoding="utf-8")


def main() -> None:
    setup_logging()
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(METADATA / "data_manifest.csv")
    two_lowest = pd.read_csv(INTERMEDIATE / "two_lowest_silver_plans_county_year.csv", dtype={"county_fips": str})
    zero_proxy = pd.read_csv(INTERMEDIATE / "zero_premium_proxy_county_year.csv", dtype={"county_fips": str})
    final = pd.read_csv(PROCESSED / "drake_replication_county_year_2022_2024.csv", dtype={"county_fips": str})
    top_two_long = make_top_two_long(two_lowest)
    premium_panel = prepare_premium_panel(zero_proxy)
    candidates = build_raw_candidate_audit(manifest, top_two_long, premium_panel)
    write_raw_candidate_audit(candidates)
    selected_frames = []
    for rule in DEFAULT_RULES:
        logging.info("Selecting default rows under rule: %s", rule)
        selected = select_default_rows(candidates, rule)
        selected = add_candidate_group_flags(selected, candidates)
        selected_frames.append(selected)
    selected_all = pd.concat(selected_frames, ignore_index=True)
    long = long_by_premium_variant(selected_all)
    comparison, by_state = summarize_counts(long, final)
    comparison.to_csv(OUTPUTS / "crosswalk_default_rule_count_comparison.csv", index=False)
    by_state.to_csv(OUTPUTS / "crosswalk_default_rule_by_state_year.csv", index=False)
    write_failure_reason_outputs(long)
    gap = write_across_gap_diagnosis(long, comparison)
    write_reason_level_distribution(candidates, long)
    ks = write_kansas_audit(long)
    write_rule_extraction_doc()
    write_reconciliation_report(comparison, gap, ks, candidates)
    logging.info("Crosswalk default mapping audit complete")
    print("\nCrosswalk default mapping audit complete")
    print(f"Comparison: {OUTPUTS / 'crosswalk_default_rule_count_comparison.csv'}")
    print(f"Report: {DOCS / 'crosswalk_default_mapping_reconciliation_report.md'}")
    print(f"Failure reasons rows: turnover={len(pd.read_csv(OUTPUTS / 'turnover_failure_reason_by_variant.csv'))}, across={len(pd.read_csv(OUTPUTS / 'across_issuer_failure_reason_by_variant.csv'))}")


if __name__ == "__main__":
    main()
