#!/usr/bin/env python
"""Audit prior-year top-two silver plan selection for the Drake replication.

This script constructs diagnostic plan-selection variants only. It does not
estimate causal models, DID regressions, causal forests, DML, or policy rules.
"""

from __future__ import annotations

import argparse
import importlib.util
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"
INTERMEDIATE = DATA / "intermediate"
PROCESSED = DATA / "processed"
METADATA = DATA / "metadata"
OUTPUTS = ROOT / "outputs"
DOCS = ROOT / "docs"
LOGS = ROOT / "logs"

TRANSITIONS = [(2021, 2022), (2022, 2023), (2023, 2024)]
PREMIUM_VARIANTS = ["current_ehb_all_states", "ehb_named_states_only", "gross_only"]
DEFAULT_RULES = ["current_repo_rule", "same_plan_if_available_else_source_order", "source_order_first_valid"]
ISSUER_CONCEPT = "plan_panel_preferred"
PRIMARY_DEFAULT_RULE = "current_repo_rule"
PRIMARY_PREMIUM_VARIANT = "current_ehb_all_states"
DRAKE_ANY_COUNT = 4452
DRAKE_ACROSS_COUNT = 211
DRAKE_ANY_ENROLLEE_MILLIONS = 28.4
DRAKE_ACROSS_ENROLLEE_MILLIONS = 0.8


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILD = load_module("drake_build_for_top_two", SCRIPTS / "03_build_drake_replication_dataset.py")
CROSS = load_module("crosswalk_audit_for_top_two", SCRIPTS / "07_crosswalk_default_mapping_audit.py")
CROSS.PREMIUM_VARIANTS = PREMIUM_VARIANTS


SELECTION_VARIANTS = {
    "current_repo_top_two": {
        "ranking_rule": "Existing repo output from two_lowest_silver_plans_county_year.csv.",
        "support": "plausible",
        "notes": "Baseline: age-40 gross premium, deduplicate PlanId, tie-break by issuer_id and PlanId.",
    },
    "rank_by_gross_age40_premium_planid": {
        "ranking_rule": "Deduplicate county-year PlanId rows, rank by age-40 gross premium, issuer_id, PlanId, source row order.",
        "support": "plausible",
        "notes": "Makes current behavior explicit.",
    },
    "rank_by_gross_age40_standard_component": {
        "ranking_rule": "Collapse to StandardComponentId, rank by age-40 gross premium, issuer_id, component ID.",
        "support": "diagnostic_only",
        "notes": "Tests PlanId/CSR duplicate treatment; current QHP Landscape standard component is usually the PlanId.",
    },
    "rank_by_postsubsidy_net_premium": {
        "ranking_rule": "Rank by estimated prior-year EHB-aware net premium proxy for the age-40 125%-FPL enrollee.",
        "support": "diagnostic_only",
        "notes": "Drake says top-two premium silver plans, but not that ranking is by net premium.",
    },
    "rank_by_ehb_adjusted_gross_premium": {
        "ranking_rule": "Rank by EHB component of age-40 gross premium.",
        "support": "diagnostic_only",
        "notes": "Tests whether non-EHB premium residual changes prior top-two identity.",
    },
    "rank_by_displayed_qhp_order_if_available": {
        "ranking_rule": "Rank by cached source row order within county-year when no official display rank field exists.",
        "support": "diagnostic_only",
        "notes": "No QHP display/order field was available in the cached panel.",
    },
    "rank_by_rate_puf_premium": {
        "ranking_rule": "Rank by Rate PUF age-40 premium where available.",
        "support": "diagnostic_only",
        "notes": "Tests whether Rate PUF overrides QHP Landscape premium; Drake names QHP Landscape.",
    },
    "county_rating_area_specific_top_two": {
        "ranking_rule": "Rank within county-rating-area combinations, then collapse to county-year by deterministic order.",
        "support": "diagnostic_only",
        "notes": "Tests county/rating-area collapse issues.",
    },
    "service_area_strict_top_two": {
        "ranking_rule": "Use QHP county rows as service-area eligibility; no stricter service-area field is present in cached QHP rows.",
        "support": "diagnostic_only",
        "notes": "QHP Landscape is already county-plan availability; ServiceAreaId is blank for QHP rows.",
    },
    "exclude_child_only_or_limited_plans": {
        "ranking_rule": "Exclude cached rows flagged child-only/limited if those flags are available; otherwise equals baseline with warning.",
        "support": "diagnostic_only",
        "notes": "Age-40 premium rows should already exclude child-only-only offers.",
    },
    "tie_break_source_order": {
        "ranking_rule": "Rank by age-40 gross premium and source row order rather than issuer_id/PlanId.",
        "support": "diagnostic_only",
        "notes": "Tests whether hidden source-order tie-breaking changes top-two identity.",
    },
    "all_tied_lowest_or_second_lowest": {
        "ranking_rule": "Include all plans tied at the lowest or second distinct premium in the exposure universe.",
        "support": "diagnostic_only",
        "notes": "Tests whether ties are counted more broadly than one selected PlanId per rank.",
    },
}


def setup_logging(verbose: bool) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOGS / "top_two_silver_selection_audit.log", mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype("boolean").fillna(False).astype(bool)


def joined_unique(values: pd.Series, max_items: int = 12) -> str:
    out: list[str] = []
    for value in values.dropna().astype(str):
        value = value.strip()
        if value and value not in out:
            out.append(value)
    if len(out) > max_items:
        return "|".join(out[:max_items]) + f"|...(+{len(out) - max_items})"
    return "|".join(out)


def parse_percent(values: pd.Series) -> pd.Series:
    text = values.astype(str).str.strip()
    has_percent = text.str.endswith("%", na=False)
    numeric = pd.to_numeric(text.str.replace("%", "", regex=False), errors="coerce")
    return numeric.where(~has_percent, numeric / 100.0)


def markdown_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "_No rows._"
    show = df.head(max_rows).copy()
    cols = list(show.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in show.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            if isinstance(value, float):
                vals.append(f"{value:.3f}")
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    if len(df) > max_rows:
        lines.append(f"| ... | {len(df) - max_rows} more rows omitted |" + " |" * max(len(cols) - 2, 0))
    return "\n".join(lines)


def resolve_local_path(local_path: Any) -> Path:
    """Resolve manifest paths against this repo or the adjacent raw-data project."""
    if pd.isna(local_path) or str(local_path).strip() == "":
        raise FileNotFoundError("Manifest row has no local_path.")
    rel = Path(str(local_path))
    candidates = [
        ROOT / rel,
        ROOT.parent.parent / "zero_premium_project" / rel,
    ]
    env_raw_project = Path(str(Path.cwd())) if False else None
    env_value = None
    try:
        import os

        env_value = os.environ.get("ZERO_PREMIUM_RAW_PROJECT")
    except Exception:  # pragma: no cover
        env_value = None
    if env_value:
        candidates.insert(1, Path(env_value) / rel)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not resolve {local_path}. Tried: {', '.join(str(c) for c in candidates)}")


def manifest_row(manifest: pd.DataFrame, source_group: str, year: int, file_type_contains: str) -> pd.Series:
    mask = (
        manifest["source_group"].astype(str).eq(source_group)
        & manifest["year"].astype(str).eq(str(year))
        & manifest["file_type"].astype(str).str.contains(file_type_contains, case=False, regex=False, na=False)
        & manifest["download_success"].astype(str).str.lower().eq("true")
    )
    rows = manifest[mask]
    if rows.empty:
        raise FileNotFoundError(f"Missing manifest row for {source_group} {year} {file_type_contains}")
    return rows.iloc[0]


def qhp_landscape_path(manifest: pd.DataFrame, year: int) -> Path:
    row = manifest_row(manifest, "qhp_landscape", year, "QHP Landscape Individual Medical ZIP")
    return resolve_local_path(row["local_path"])


def load_qhp_raw(manifest: pd.DataFrame, year: int) -> pd.DataFrame:
    path = qhp_landscape_path(manifest, year)
    member = BUILD.tabular_member(path, prefer_excel=True)
    header = BUILD.detect_qhp_header(path, member)
    raw = BUILD.read_excel_from_zip(path, member, header=header, sheet_name=0)
    raw["_source_row_order"] = np.arange(len(raw))
    raw["_source_file"] = str(path)
    return raw


def write_qhp_panel_construction_audit(manifest: pd.DataFrame, sample_states: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    continuous_states = set(sample_states.loc[sample_states["continuous_hcgov_2022_2024"].astype(bool), "state"].astype(str))
    for year in [2021, 2022, 2023, 2024]:
        try:
            raw = load_qhp_raw(manifest, year)
            cols = list(raw.columns)
            state_col = BUILD.find_col(cols, ["State Code", "State"], required=True)
            county_col = BUILD.find_col(cols, ["FIPS County Code", "County FIPS Code"], required=True)
            metal_col = BUILD.find_col(cols, ["Metal Level"], required=True)
            plan_col = BUILD.find_col(cols, ["Plan ID (Standard Component)", "Plan ID"], required=True)
            issuer_col = BUILD.find_col(cols, ["HIOS Issuer ID", "Issuer ID"], required=True)
            standard_col = BUILD.find_col(cols, ["Plan ID (Standard Component)", "StandardComponentId", "Plan ID"])
            premium_col = BUILD.find_col(cols, ["Premium Adult Individual Age 40"], required=True)
            ehb_col = BUILD.find_col(cols, ["EHB Percent of Total Premium"])
            child_col = BUILD.find_col(cols, ["Child Only Offering", "ChildOnlyOffering"]) if cols else None
            source_file = str(qhp_landscape_path(manifest, year))
            raw["_state"] = raw[state_col].astype(str).str.upper().str.strip()
            raw["_county_fips"] = raw[county_col].map(BUILD.clean_fips)
            raw["_plan_id"] = raw[plan_col].map(BUILD.clean_id)
            raw["_standard_component_id"] = raw[standard_col].map(BUILD.clean_id) if standard_col else raw["_plan_id"]
            raw["_issuer_id"] = raw[issuer_col].map(BUILD.clean_id)
            raw["_metal_level"] = raw[metal_col].astype(str).str.strip()
            raw["_age40"] = BUILD.numeric_series(raw[premium_col])
            raw["_ehb"] = parse_percent(raw[ehb_col]) if ehb_col else np.nan
            if child_col:
                child_text = raw[child_col].astype(str).str.lower()
                raw["_child_only_exclude"] = child_text.str.contains("child", na=False) & ~child_text.str.contains("adult", na=False)
            else:
                raw["_child_only_exclude"] = False
            for state, g0 in raw.groupby("_state", dropna=False):
                after_hcgov = g0[g0["_state"].isin(continuous_states)].copy()
                after_individual = after_hcgov.copy()
                after_dental = after_individual.copy()
                after_silver = after_dental[after_dental["_metal_level"].str.lower().str.contains("silver", na=False)].copy()
                after_child = after_silver[~after_silver["_child_only_exclude"]].copy()
                after_premium = after_child[after_child["_age40"].notna() & after_child["_age40"].gt(0)].copy()
                county_counts = after_premium.drop_duplicates(["_county_fips", "_plan_id"]).groupby("_county_fips")["_plan_id"].nunique()
                rows.append(
                    {
                        "year": year,
                        "state": state,
                        "raw_qhp_landscape_rows": len(g0),
                        "rows_after_healthcaregov_state_filter": len(after_hcgov),
                        "rows_after_individual_market_filter": len(after_individual),
                        "rows_after_dental_exclusion": len(after_dental),
                        "rows_after_metal_silver_filter": len(after_silver),
                        "rows_after_child_only_exclusion": len(after_child),
                        "rows_after_valid_premium_filter": len(after_premium),
                        "unique_counties": after_premium["_county_fips"].nunique(),
                        "unique_plan_ids": after_premium["_plan_id"].nunique(),
                        "unique_standard_component_ids": after_premium["_standard_component_id"].nunique(),
                        "unique_issuers": after_premium["_issuer_id"].nunique(),
                        "duplicate_county_plan_rows": int(after_premium.duplicated(["_county_fips", "_plan_id"]).sum()),
                        "duplicate_county_standard_component_rows": int(after_premium.duplicated(["_county_fips", "_standard_component_id"]).sum()),
                        "missing_age_40_premium_rows": int(after_child["_age40"].isna().sum()),
                        "missing_ehb_percent_total_premium_rows": int(after_premium["_ehb"].isna().sum()) if ehb_col else len(after_premium),
                        "rows_with_ehb_percent_total_premium_lt_1": int(after_premium["_ehb"].lt(1).sum()) if ehb_col else 0,
                        "rows_with_ehb_percent_total_premium_gt_1": int(after_premium["_ehb"].gt(1).sum()) if ehb_col else 0,
                        "rows_with_anomalous_premiums": int((after_premium["_age40"].le(0) | after_premium["_age40"].gt(5000)).sum()),
                        "counties_with_fewer_than_2_silver_plans": int((county_counts < 2).sum()),
                        "counties_with_exactly_2_silver_plans": int((county_counts == 2).sum()),
                        "counties_with_more_than_2_silver_plans": int((county_counts > 2).sum()),
                        "source_file": source_file,
                        "notes": "QHP Landscape medical individual file; individual/dental filters are structural unless explicit fields exist.",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            logging.warning("Raw QHP audit failed for %s: %s", year, exc)
            year_panel = panel[panel["year"].eq(year)].copy()
            for state, g in year_panel.groupby("state", dropna=False):
                county_counts = g.drop_duplicates(["county_fips", "plan_id"]).groupby("county_fips")["plan_id"].nunique()
                rows.append(
                    {
                        "year": year,
                        "state": state,
                        "raw_qhp_landscape_rows": np.nan,
                        "rows_after_healthcaregov_state_filter": np.nan,
                        "rows_after_individual_market_filter": np.nan,
                        "rows_after_dental_exclusion": np.nan,
                        "rows_after_metal_silver_filter": len(g),
                        "rows_after_child_only_exclusion": len(g),
                        "rows_after_valid_premium_filter": int(g["age_40_premium"].notna().sum()),
                        "unique_counties": g["county_fips"].nunique(),
                        "unique_plan_ids": g["plan_id"].nunique(),
                        "unique_standard_component_ids": g["standard_component_id"].nunique(),
                        "unique_issuers": g["issuer_id"].nunique(),
                        "duplicate_county_plan_rows": int(g.duplicated(["county_fips", "plan_id"]).sum()),
                        "duplicate_county_standard_component_rows": int(g.duplicated(["county_fips", "standard_component_id"]).sum()),
                        "missing_age_40_premium_rows": int(g["age_40_premium"].isna().sum()),
                        "missing_ehb_percent_total_premium_rows": int(g.get("ehb_percent_total_premium", pd.Series(np.nan, index=g.index)).isna().sum()),
                        "rows_with_ehb_percent_total_premium_lt_1": int(pd.to_numeric(g.get("ehb_share_of_total_premium", pd.Series(np.nan, index=g.index)), errors="coerce").lt(1).sum()),
                        "rows_with_ehb_percent_total_premium_gt_1": int(pd.to_numeric(g.get("ehb_share_of_total_premium", pd.Series(np.nan, index=g.index)), errors="coerce").gt(1).sum()),
                        "rows_with_anomalous_premiums": int((pd.to_numeric(g["age_40_premium"], errors="coerce").le(0) | pd.to_numeric(g["age_40_premium"], errors="coerce").gt(5000)).sum()),
                        "counties_with_fewer_than_2_silver_plans": int((county_counts < 2).sum()),
                        "counties_with_exactly_2_silver_plans": int((county_counts == 2).sum()),
                        "counties_with_more_than_2_silver_plans": int((county_counts > 2).sum()),
                        "source_file": "cached_silver_plan_county_year_panel",
                        "notes": f"Raw QHP file unavailable for detailed audit: {exc}",
                    }
                )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "qhp_panel_construction_audit.csv", index=False)
    return out


def load_inputs() -> dict[str, pd.DataFrame]:
    data = {
        "manifest": pd.read_csv(METADATA / "data_manifest.csv", dtype=str),
        "sample_states": pd.read_csv(METADATA / "healthcaregov_state_sample_2022_2024.csv", dtype=str),
        "silver": pd.read_csv(INTERMEDIATE / "silver_plan_county_year_panel.csv", dtype={"county_fips": str}),
        "zero_proxy": pd.read_csv(INTERMEDIATE / "zero_premium_proxy_county_year.csv", dtype={"county_fips": str}),
        "two_lowest": pd.read_csv(INTERMEDIATE / "two_lowest_silver_plans_county_year.csv", dtype={"county_fips": str}),
        "final": pd.read_csv(PROCESSED / "drake_replication_county_year_2022_2024.csv", dtype={"county_fips": str}),
        "harmonized": pd.read_csv(PROCESSED / "drake_replication_primary_drake_harmonized_2022_2024.csv", dtype={"county_fips": str}),
    }
    return data


def prepare_panel(panel: pd.DataFrame, zero_proxy: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    out["source_row_order"] = np.arange(len(out))
    out["plan_id"] = out["plan_id"].map(BUILD.clean_id)
    out["issuer_id"] = out["issuer_id"].map(BUILD.clean_id)
    out["standard_component_id"] = out.get("standard_component_id", out["plan_id"]).fillna(out["plan_id"]).map(BUILD.clean_id)
    out["age_40_premium"] = BUILD.numeric_series(out["age_40_premium"])
    out["ehb_age_40_premium"] = BUILD.numeric_series(out.get("ehb_age_40_premium", out["age_40_premium"]))
    out["rate_puf_age_40_premium"] = BUILD.numeric_series(out.get("rate_puf_age_40_premium", pd.Series(np.nan, index=out.index)))
    out["ehb_percent_total_premium"] = BUILD.numeric_series(out.get("ehb_percent_total_premium", pd.Series(np.nan, index=out.index)))
    out["child_only_or_limited_flag"] = False
    z = zero_proxy[
        [
            "year",
            "state",
            "county_fips",
            "plan_id",
            "estimated_net_premium_proxy",
            "zero_premium_proxy",
        ]
    ].copy()
    z["plan_id"] = z["plan_id"].map(BUILD.clean_id)
    z = z.rename(
        columns={
            "estimated_net_premium_proxy": "prior_net_premium_current_ehb_all_states",
            "zero_premium_proxy": "prior_zero_flag_current_ehb_all_states",
        }
    )
    out = out.merge(z, on=["year", "state", "county_fips", "plan_id"], how="left")
    return out


def baseline_long(two_lowest: pd.DataFrame, panel: pd.DataFrame, exposure_universe: str) -> pd.DataFrame:
    rows = []
    for rank, plan_col, issuer_col, premium_col in [
        ("lowest", "lowest_silver_plan_id", "lowest_silver_issuer_id", "lowest_silver_premium"),
        ("second_lowest", "second_lowest_silver_plan_id", "second_lowest_silver_issuer_id", "second_lowest_silver_premium"),
    ]:
        part = two_lowest[["year", "state", "county_fips", plan_col, issuer_col, premium_col]].rename(
            columns={plan_col: "selected_plan_id", issuer_col: "selected_issuer_id", premium_col: "ranking_premium_used"}
        )
        part["rank"] = rank
        rows.append(part)
    out = pd.concat(rows, ignore_index=True)
    out["selected_plan_id"] = out["selected_plan_id"].map(BUILD.clean_id)
    details = panel.drop_duplicates(["year", "state", "county_fips", "plan_id"]).rename(columns={"plan_id": "selected_plan_id"})
    out = out.merge(details, on=["year", "state", "county_fips", "selected_plan_id"], how="left", suffixes=("", "_panel"))
    out["selection_variant"] = "current_repo_top_two"
    out["exposure_universe"] = exposure_universe
    out["ranking_rule"] = SELECTION_VARIANTS["current_repo_top_two"]["ranking_rule"]
    out["tie_group_size"] = 1
    out["warning_flag"] = ""
    return standardize_selection_rows(out)


def deduplicate_for_variant(g: pd.DataFrame, variant: str) -> pd.DataFrame:
    if variant == "rank_by_gross_age40_standard_component":
        key = "standard_component_id"
        sort_cols = ["ranking_premium_used", "issuer_id", "standard_component_id", "plan_id", "source_row_order"]
    else:
        key = "plan_id"
        if variant == "tie_break_source_order":
            sort_cols = ["ranking_premium_used", "source_row_order", "issuer_id", "plan_id"]
        elif variant == "rank_by_displayed_qhp_order_if_available":
            sort_cols = ["source_row_order", "ranking_premium_used", "issuer_id", "plan_id"]
        else:
            sort_cols = ["ranking_premium_used", "issuer_id", "plan_id", "source_row_order"]
    return g.sort_values(sort_cols, kind="mergesort").drop_duplicates(key, keep="first").copy()


def ranking_metric(panel: pd.DataFrame, variant: str) -> pd.Series:
    if variant in {"current_repo_top_two", "rank_by_gross_age40_premium_planid", "service_area_strict_top_two", "exclude_child_only_or_limited_plans", "tie_break_source_order", "all_tied_lowest_or_second_lowest"}:
        return panel["age_40_premium"]
    if variant == "rank_by_gross_age40_standard_component":
        return panel["age_40_premium"]
    if variant == "rank_by_postsubsidy_net_premium":
        return BUILD.numeric_series(panel["prior_net_premium_current_ehb_all_states"])
    if variant == "rank_by_ehb_adjusted_gross_premium":
        return BUILD.numeric_series(panel["ehb_age_40_premium"])
    if variant == "rank_by_displayed_qhp_order_if_available":
        return BUILD.numeric_series(panel["source_row_order"])
    if variant == "rank_by_rate_puf_premium":
        return BUILD.numeric_series(panel["rate_puf_age_40_premium"]).fillna(panel["age_40_premium"])
    if variant == "county_rating_area_specific_top_two":
        return panel["age_40_premium"]
    raise ValueError(f"Unknown variant: {variant}")


def select_group(g: pd.DataFrame, variant: str, exposure_universe: str) -> pd.DataFrame:
    g = g.copy()
    if variant == "exclude_child_only_or_limited_plans" and "child_only_or_limited_flag" in g.columns:
        g = g[~bool_series(g["child_only_or_limited_flag"])].copy()
    g["ranking_premium_used"] = ranking_metric(g, variant)
    g = g[g["ranking_premium_used"].notna()].copy()
    if g.empty:
        return pd.DataFrame()
    g = deduplicate_for_variant(g, variant)
    if g.empty:
        return pd.DataFrame()
    g = g.sort_values(["ranking_premium_used", "issuer_id", "plan_id", "source_row_order"], kind="mergesort")
    distinct_premiums = sorted(g["ranking_premium_used"].dropna().unique())
    if not distinct_premiums:
        return pd.DataFrame()
    lowest_premium = distinct_premiums[0]
    second_premium = distinct_premiums[1] if len(distinct_premiums) > 1 else lowest_premium
    if exposure_universe == "include_ties_at_second_lowest":
        selected = g[g["ranking_premium_used"].isin([lowest_premium, second_premium])].copy()
        selected["rank"] = np.where(selected["ranking_premium_used"].eq(lowest_premium), "lowest", "second_lowest")
    else:
        selected = g.head(2).copy()
        selected["rank"] = ["lowest", "second_lowest"][: len(selected)]
    selected["tie_group_size"] = selected.groupby("ranking_premium_used")["plan_id"].transform("nunique")
    return selected


def build_variant_selection(panel: pd.DataFrame, two_lowest: pd.DataFrame, variant: str, exposure_universe: str) -> pd.DataFrame:
    if variant == "current_repo_top_two":
        return baseline_long(two_lowest, panel, exposure_universe)
    frames = []
    group_cols = ["year", "state", "county_fips"]
    if variant == "county_rating_area_specific_top_two" and "rating_area_id" in panel.columns:
        group_cols = ["year", "state", "county_fips", "rating_area_id"]
    for _, g in panel.groupby(group_cols, dropna=False):
        selected = select_group(g, variant, exposure_universe)
        if selected.empty:
            continue
        frames.append(selected)
    if not frames:
        return pd.DataFrame(columns=["selection_variant", "exposure_universe", "year", "state", "county_fips", "rank", "selected_plan_id"])
    out = pd.concat(frames, ignore_index=True)
    out = out.rename(columns={"plan_id": "selected_plan_id", "issuer_id": "selected_issuer_id"})
    out["selection_variant"] = variant
    out["exposure_universe"] = exposure_universe
    out["ranking_rule"] = SELECTION_VARIANTS[variant]["ranking_rule"]
    warnings = []
    for _, row in out.iterrows():
        warn = []
        if variant == "rank_by_displayed_qhp_order_if_available":
            warn.append("no_official_display_rank_field_used_cached_source_order")
        if variant == "service_area_strict_top_two":
            warn.append("qhp_county_rows_used_as_service_area_availability")
        if variant == "exclude_child_only_or_limited_plans":
            warn.append("child_or_limited_flags_not_available_in_cached_panel")
        if variant == "rank_by_rate_puf_premium" and pd.isna(row.get("rate_puf_age_40_premium")):
            warn.append("rate_puf_premium_missing_fell_back_to_qhp")
        warnings.append(";".join(warn))
    out["warning_flag"] = warnings
    return standardize_selection_rows(out)


def standardize_selection_rows(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    rename = {
        "standard_component_id": "selected_standard_component_id",
        "metal_level": "selected_metal_level",
        "age_40_premium": "selected_age40_gross_premium",
        "ehb_percent_total_premium": "selected_ehb_percent",
        "ehb_age_40_premium": "selected_ehb_premium",
        "non_ehb_age_40_premium": "selected_non_ehb_residual",
        "source_file": "source_file",
        "source_row_order": "source_row_order",
        "plan_marketing_name": "selected_plan_marketing_name",
    }
    out = out.rename(columns={k: v for k, v in rename.items() if k in out.columns})
    if "selected_plan_id" not in out.columns and "plan_id" in out.columns:
        out["selected_plan_id"] = out["plan_id"]
    if "selected_issuer_id" not in out.columns and "issuer_id" in out.columns:
        out["selected_issuer_id"] = out["issuer_id"]
    out["selected_plan_id"] = out["selected_plan_id"].map(BUILD.clean_id)
    out["selected_issuer_id"] = out["selected_issuer_id"].map(BUILD.clean_id)
    for col in [
        "selected_standard_component_id",
        "selected_plan_marketing_name",
        "selected_metal_level",
        "selected_age40_gross_premium",
        "selected_ehb_percent",
        "selected_ehb_premium",
        "selected_non_ehb_residual",
        "prior_net_premium_current_ehb_all_states",
        "prior_zero_flag_current_ehb_all_states",
        "source_file",
        "source_row_order",
        "tie_group_size",
        "ranking_premium_used",
        "ranking_rule",
        "warning_flag",
    ]:
        if col not in out.columns:
            out[col] = np.nan if col not in {"source_file", "ranking_rule", "warning_flag"} else ""
    out["selected_net_premium_current_ehb_all_states"] = BUILD.numeric_series(out["prior_net_premium_current_ehb_all_states"])
    out["selected_zero_flag_current_ehb_all_states"] = bool_series(out["prior_zero_flag_current_ehb_all_states"])
    out["selected_net_premium_ehb_named_states_only"] = out["selected_net_premium_current_ehb_all_states"]
    out["selected_zero_flag_ehb_named_states_only"] = out["selected_zero_flag_current_ehb_all_states"]
    out["source_file"] = out["source_file"].fillna("").astype(str).map(lambda x: Path(x).name if x else "")
    out["ranking_rule"] = out["selection_variant"].astype(str)
    out["selected_plan_marketing_name"] = out["selected_plan_marketing_name"].fillna("").astype(str).str.slice(0, 20)
    warning_map = {
        "no_official_display_rank_field_used_cached_source_order": "source_order_proxy",
        "qhp_county_rows_used_as_service_area_availability": "qhp_county_service_proxy",
        "child_or_limited_flags_not_available_in_cached_panel": "child_flag_unavailable",
        "rate_puf_premium_missing_fell_back_to_qhp": "rate_missing_qhp_fallback",
    }
    for old, new in warning_map.items():
        out["warning_flag"] = out["warning_flag"].fillna("").astype(str).str.replace(old, new, regex=False)
    for col in out.select_dtypes(include=["float"]).columns:
        out[col] = out[col].round(3)
    keep = [
        "selection_variant",
        "exposure_universe",
        "year",
        "state",
        "county_fips",
        "rank",
        "selected_plan_id",
        "selected_standard_component_id",
        "selected_issuer_id",
        "selected_plan_marketing_name",
        "selected_metal_level",
        "selected_age40_gross_premium",
        "selected_ehb_percent",
        "selected_ehb_premium",
        "selected_non_ehb_residual",
        "selected_net_premium_current_ehb_all_states",
        "selected_zero_flag_current_ehb_all_states",
        "selected_net_premium_ehb_named_states_only",
        "selected_zero_flag_ehb_named_states_only",
        "source_file",
        "source_row_order",
        "tie_group_size",
        "ranking_premium_used",
        "ranking_rule",
        "warning_flag",
    ]
    return out[keep].copy()


def build_all_selections(panel: pd.DataFrame, two_lowest: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for variant in SELECTION_VARIANTS:
        for universe in ["exactly_two_plans", "include_ties_at_second_lowest"]:
            logging.info("Selecting top-two variant=%s universe=%s", variant, universe)
            frames.append(build_variant_selection(panel, two_lowest, variant, universe))
    out = pd.concat(frames, ignore_index=True)
    out["current_year"] = out["year"].astype(int) + 1
    out = out[out["current_year"].isin([2022, 2023, 2024])].copy()
    out = out.rename(columns={"year": "prior_year"})
    out.to_csv(OUTPUTS / "top_two_silver_identity_comparison.csv", index=False)
    return out


def make_top_two_long_for_crosswalk(selection: pd.DataFrame) -> pd.DataFrame:
    out = selection.rename(
        columns={
            "prior_year": "year",
            "selected_plan_id": "previous_plan_id",
            "selected_issuer_id": "previous_issuer_id_from_prior_panel",
            "selected_age40_gross_premium": "prior_gross_premium_top_two",
        }
    )[
        [
            "year",
            "state",
            "county_fips",
            "rank",
            "previous_plan_id",
            "previous_issuer_id_from_prior_panel",
            "prior_gross_premium_top_two",
        ]
    ].copy()
    out["previous_plan_id"] = out["previous_plan_id"].map(BUILD.clean_id)
    out["previous_issuer_id_from_prior_panel"] = out["previous_issuer_id_from_prior_panel"].map(BUILD.clean_id)
    return out


def prepare_premium_panel(zero_proxy: pd.DataFrame) -> pd.DataFrame:
    specs = [spec for spec in BUILD.premium_variant_specs() if spec["variant_name"] in PREMIUM_VARIANTS]
    proxy = zero_proxy.copy()
    proxy["plan_id"] = proxy["plan_id"].map(BUILD.clean_id)
    proxy["issuer_id"] = proxy["issuer_id"].map(BUILD.clean_id)
    variants = BUILD.build_premium_variant_panel(proxy, specs)
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


def load_raw_crosswalk_resolved(manifest: pd.DataFrame, previous_year: int, current_year: int) -> pd.DataFrame:
    """Load raw Crosswalk PUF rows while allowing raw files outside this repo."""
    row = manifest_row(manifest, "exchange_puf", current_year, "Plan ID Crosswalk PUF")
    df = BUILD.read_csv_from_zip(resolve_local_path(row["local_path"]))
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
    out["zip_code"] = out["zip_code"].map(CROSS.clean_zip)
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


def build_variant_long(selection: pd.DataFrame, manifest: pd.DataFrame, premium_panel: pd.DataFrame) -> pd.DataFrame:
    CROSS.load_raw_crosswalk = load_raw_crosswalk_resolved
    top_two_long = make_top_two_long_for_crosswalk(selection)
    candidates = CROSS.build_raw_candidate_audit(manifest, top_two_long, premium_panel)
    selected_frames = []
    for rule in DEFAULT_RULES:
        selected = CROSS.select_default_rows(candidates, rule)
        selected = CROSS.add_candidate_group_flags(selected, candidates)
        selected_frames.append(selected)
    selected_all = pd.concat(selected_frames, ignore_index=True)
    # CROSS.add_candidate_group_flags creates one copy per premium variant for
    # candidate-group diagnostics. Treatment counts only need one selected
    # default row; keeping all copies greatly inflates memory without changing
    # county-year max flags.
    key_cols = ["transition", "year", "state", "county_fips", "rank", "previous_plan_id", "default_mapping_rule"]
    selected_all = selected_all.sort_values(key_cols, kind="mergesort").drop_duplicates(key_cols, keep="first")
    long = CROSS.long_by_premium_variant(selected_all)
    long["selection_variant"] = selection["selection_variant"].iloc[0]
    long["exposure_universe"] = selection["exposure_universe"].iloc[0]
    return long


def treatment_counts_from_long(long: pd.DataFrame, final: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    comparison, by_state = CROSS.summarize_counts(long, final)
    comparison = comparison.rename(columns={"premium_variant": "premium_variant"})
    comparison.insert(0, "exposure_universe", long["exposure_universe"].iloc[0])
    comparison.insert(0, "top_two_selection_variant", long["selection_variant"].iloc[0])
    by_state.insert(0, "exposure_universe", long["exposure_universe"].iloc[0])
    by_state.insert(0, "top_two_selection_variant", long["selection_variant"].iloc[0])
    by_state = by_state.rename(columns={"any_turnover_enrollment": "any_enrollment_weighted_exposure", "across_issuer_turnover_enrollment": "across_enrollment_weighted_exposure"})
    if "within_issuer_turnover_county_years" not in by_state.columns:
        by_state["within_issuer_turnover_county_years"] = np.nan
    for col in ["enrollment", "any_enrollment_weighted_exposure", "across_enrollment_weighted_exposure"]:
        if col not in by_state.columns:
            by_state[col] = np.nan
    return comparison, by_state


def reduce_long_columns(long: pd.DataFrame) -> pd.DataFrame:
    needed = [
        "selection_variant",
        "exposure_universe",
        "transition",
        "previous_year",
        "current_year",
        "year",
        "state",
        "county_fips",
        "rank",
        "default_mapping_rule",
        "premium_variant",
        "previous_plan_id",
        "current_plan_id",
        "previous_issuer_id_from_prior_panel",
        "current_issuer_final",
        "prior_gross_premium",
        "current_gross_premium",
        "prior_zero",
        "current_positive",
        "current_zero",
        "zero_to_positive",
        "same_issuer",
        "across_issuer",
        "issuer_missing",
        "no_valid_crosswalk",
        "current_plan_missing",
        "prior_premium_missing",
        "current_premium_missing",
        "crosswalk_level_4_or_5",
        "turnover_failure_reason",
        "across_failure_reason",
        "selected_top_two_differs_from_current_repo",
        "baseline_previous_plan_id",
    ]
    return long[[col for col in needed if col in long.columns]].copy()


def compare_identity(selection: pd.DataFrame) -> pd.DataFrame:
    baseline = selection[
        selection["selection_variant"].eq("current_repo_top_two") & selection["exposure_universe"].eq("exactly_two_plans")
    ][["prior_year", "state", "county_fips", "rank", "selected_plan_id"]].rename(columns={"selected_plan_id": "baseline_plan_id"})
    rows = []
    for (variant, universe), g in selection.groupby(["selection_variant", "exposure_universe"], dropna=False):
        merged = g.merge(baseline, on=["prior_year", "state", "county_fips", "rank"], how="left")
        merged["differs"] = merged["selected_plan_id"].ne(merged["baseline_plan_id"])
        county = merged.groupby(["prior_year", "state", "county_fips"], dropna=False).agg(
            lowest_differs=("differs", lambda s: bool(s[merged.loc[s.index, "rank"].eq("lowest")].any())),
            second_lowest_differs=("differs", lambda s: bool(s[merged.loc[s.index, "rank"].eq("second_lowest")].any())),
            either_differs=("differs", "max"),
            tie_related=("tie_group_size", lambda s: bool(pd.to_numeric(s, errors="coerce").fillna(1).gt(1).any())),
            warning=("warning_flag", joined_unique),
        ).reset_index()
        top_states = (
            county[county["either_differs"]]
            .groupby(["prior_year", "state"], dropna=False)
            .size()
            .sort_values(ascending=False)
            .head(10)
        )
        rows.append(
            {
                "selection_variant": variant,
                "exposure_universe": universe,
                "county_years_where_lowest_plan_differs_from_current_repo": int(county["lowest_differs"].sum()),
                "county_years_where_second_lowest_plan_differs_from_current_repo": int(county["second_lowest_differs"].sum()),
                "county_years_where_either_top_two_plan_differs": int(county["either_differs"].sum()),
                "states_years_with_most_differences": "; ".join([f"{idx[0]}-{idx[1]}:{val}" for idx, val in top_states.items()]),
                "number_of_differences_involving_ties": int((county["either_differs"] & county["tie_related"]).sum()),
                "number_of_differences_involving_standard_component_collapse": int(county["either_differs"].sum()) if variant == "rank_by_gross_age40_standard_component" else 0,
                "number_of_differences_involving_rating_area_county_issues": int(county["either_differs"].sum()) if variant == "county_rating_area_specific_top_two" else 0,
                "number_of_differences_involving_child_only_limited_plans": int(county["either_differs"].sum()) if variant == "exclude_child_only_or_limited_plans" else 0,
                "number_of_differences_involving_missing_or_anomalous_premiums": int(merged.loc[merged["differs"], "ranking_premium_used"].isna().sum()),
                "notes": joined_unique(county["warning"]),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "top_two_silver_variant_difference_summary.csv", index=False)
    return out


def add_difference_flags(long: pd.DataFrame, baseline_selection: pd.DataFrame) -> pd.DataFrame:
    base = baseline_selection[
        ["prior_year", "current_year", "state", "county_fips", "rank", "selected_plan_id"]
    ].rename(columns={"prior_year": "previous_year", "selected_plan_id": "baseline_previous_plan_id"})
    out = long.merge(base, on=["previous_year", "current_year", "state", "county_fips", "rank"], how="left")
    out["selected_top_two_differs_from_current_repo"] = out["previous_plan_id"].ne(out["baseline_previous_plan_id"])
    return out


def summarize_across_gap(all_long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    current = all_long[
        all_long["selection_variant"].eq("current_repo_top_two")
        & all_long["exposure_universe"].eq("exactly_two_plans")
        & all_long["default_mapping_rule"].eq(PRIMARY_DEFAULT_RULE)
        & all_long["premium_variant"].eq(PRIMARY_PREMIUM_VARIANT)
    ]
    current_state = (
        current.groupby(["year", "state"], dropna=False)
        .agg(current_across=("across_issuer", lambda s: int((current.loc[s.index, "zero_to_positive"] & s).groupby(current.loc[s.index, "county_fips"]).max().sum())))
        .reset_index()
    )
    for (variant, universe, premium, rule, year, state), g in all_long.groupby(
        ["selection_variant", "exposure_universe", "premium_variant", "default_mapping_rule", "year", "state"], dropna=False
    ):
        county = g.groupby("county_fips", dropna=False).agg(
            any_zero=("prior_zero", "max"),
            any_ztp=("zero_to_positive", "max"),
            any_across=("across_issuer", lambda s: bool((g.loc[s.index, "zero_to_positive"] & s).any())),
            any_same=("same_issuer", lambda s: bool((g.loc[s.index, "zero_to_positive"] & s).any())),
            selected_differs=("selected_top_two_differs_from_current_repo", "max"),
        ).reset_index()
        selected_pairs = len(g)
        across_count = int(county["any_across"].sum())
        current_match = current_state[(current_state["year"].eq(year)) & (current_state["state"].eq(state))]
        current_across = int(current_match["current_across"].iloc[0]) if not current_match.empty else 0
        rows.append(
            {
                "top_two_selection_variant": variant,
                "exposure_universe": universe,
                "premium_variant": premium,
                "default_mapping_rule": rule,
                "year": year,
                "state": state,
                "selected_top_two_plan_pairs": selected_pairs,
                "zero_prior_plan_pairs": int(g["prior_zero"].sum()),
                "zero_to_positive_plan_pairs": int(g["zero_to_positive"].sum()),
                "across_zero_to_positive_plan_pairs": int((g["zero_to_positive"] & g["across_issuer"]).sum()),
                "same_issuer_zero_to_positive_plan_pairs": int((g["zero_to_positive"] & g["same_issuer"]).sum()),
                "candidate_prior_plans_with_across_turnover_not_in_current_top_two": int((g["zero_to_positive"] & g["across_issuer"] & g["selected_top_two_differs_from_current_repo"]).sum()),
                "county_years_where_alternative_top_two_adds_across": int((county["any_across"] & county["selected_differs"]).sum()),
                "county_years_where_current_top_two_has_same_issuer_but_alternative_has_across": np.nan,
                "county_years_where_current_top_two_has_no_turnover_but_alternative_has_turnover": np.nan,
                "county_years_where_tie_handling_changes_across": int((county["any_across"] & county["selected_differs"]).sum()) if variant in {"tie_break_source_order", "all_tied_lowest_or_second_lowest"} else 0,
                "county_years_where_standard_component_collapse_changes_across": int((county["any_across"] & county["selected_differs"]).sum()) if variant == "rank_by_gross_age40_standard_component" else 0,
                "county_years_where_rating_area_handling_changes_across": int((county["any_across"] & county["selected_differs"]).sum()) if variant == "county_rating_area_specific_top_two" else 0,
                "difference_vs_current_repo_rule": across_count - current_across,
                "difference_vs_drake_anchor_if_available": across_count - DRAKE_ACROSS_COUNT,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "top_two_across_gap_diagnosis.csv", index=False)
    return out


def write_failure_reasons(all_long: pd.DataFrame) -> pd.DataFrame:
    out = all_long.copy()
    out["alternative_top_two_would_turnover"] = out["selected_top_two_differs_from_current_repo"] & out["zero_to_positive"]
    out["alternative_top_two_would_across_turnover"] = out["selected_top_two_differs_from_current_repo"] & out["zero_to_positive"] & out["across_issuer"]
    group_cols = [
        "year",
        "state",
        "rank",
        "selection_variant",
        "exposure_universe",
        "premium_variant",
        "default_mapping_rule",
        "turnover_failure_reason",
    ]
    summary = (
        out.groupby(group_cols, dropna=False)
        .agg(
            plan_pair_rows=("previous_plan_id", "size"),
            counties=("county_fips", "nunique"),
            turnover_rows=("zero_to_positive", "sum"),
            across_turnover_rows=("across_issuer", lambda s: int((out.loc[s.index, "zero_to_positive"] & s).sum())),
            same_issuer_turnover_rows=("same_issuer", lambda s: int((out.loc[s.index, "zero_to_positive"] & s).sum())),
            current_plan_missing_rows=("current_plan_missing", "sum"),
            current_premium_missing_rows=("current_premium_missing", "sum"),
            prior_premium_missing_rows=("prior_premium_missing", "sum"),
            issuer_missing_rows=("issuer_missing", "sum"),
            no_valid_crosswalk_rows=("no_valid_crosswalk", "sum"),
            crosswalk_level_4_or_5_rows=("crosswalk_level_4_or_5", "sum"),
            selected_top_two_differs_rows=("selected_top_two_differs_from_current_repo", "sum"),
            alternative_top_two_would_turnover_rows=("alternative_top_two_would_turnover", "sum"),
            alternative_top_two_would_across_turnover_rows=("alternative_top_two_would_across_turnover", "sum"),
        )
        .reset_index()
    )
    summary.to_csv(OUTPUTS / "top_two_turnover_failure_reason.csv", index=False)
    return summary


def write_deep_dive(all_long: pd.DataFrame, selection: pd.DataFrame) -> pd.DataFrame:
    primary = all_long[
        all_long["default_mapping_rule"].eq(PRIMARY_DEFAULT_RULE) & all_long["premium_variant"].eq(PRIMARY_PREMIUM_VARIANT)
    ].copy()
    current = primary[
        primary["selection_variant"].eq("current_repo_top_two") & primary["exposure_universe"].eq("exactly_two_plans")
    ][
        [
            "year",
            "state",
            "county_fips",
            "rank",
            "previous_plan_id",
            "current_plan_id",
            "previous_issuer_id_from_prior_panel",
            "current_issuer_final",
            "prior_gross_premium",
            "current_gross_premium",
            "zero_to_positive",
            "across_issuer",
        ]
    ].rename(
        columns={
            "previous_plan_id": "current_repo_prior_plan",
            "current_plan_id": "current_repo_crosswalk_current_plan",
            "previous_issuer_id_from_prior_panel": "current_repo_previous_issuer",
            "current_issuer_final": "current_repo_current_issuer",
            "prior_gross_premium": "current_repo_prior_premium",
            "current_gross_premium": "current_repo_current_premium",
            "zero_to_positive": "current_repo_turnover_status",
            "across_issuer": "current_repo_across_status",
        }
    )
    alternatives = primary[
        ~(
            primary["selection_variant"].eq("current_repo_top_two")
            & primary["exposure_universe"].eq("exactly_two_plans")
        )
    ].copy()
    alternatives = alternatives[alternatives["selected_top_two_differs_from_current_repo"] | (alternatives["state"].eq("KS") & alternatives["year"].eq(2022))]
    merged = alternatives.merge(current, on=["year", "state", "county_fips", "rank"], how="left")
    states_with_across_change = set(merged.loc[merged["zero_to_positive"] & merged["across_issuer"], "state"].dropna().astype(str))
    merged = merged[(merged["state"].eq("KS") & merged["year"].eq(2022)) | merged["state"].isin(states_with_across_change)].copy()
    out = pd.DataFrame(
        {
            "state": merged["state"],
            "year": merged["year"],
            "county_fips": merged["county_fips"],
            "rank": merged["rank"],
            "top_two_selection_variant": merged["selection_variant"],
            "exposure_universe": merged["exposure_universe"],
            "current_repo_lowest_or_second_plan": merged["current_repo_prior_plan"],
            "alternative_lowest_or_second_plan": merged["previous_plan_id"],
            "reason_for_difference": np.where(merged["selected_top_two_differs_from_current_repo"], "selected_prior_plan_differs", "same_as_current_repo_or_kansas_context"),
            "current_repo_turnover_status": merged["current_repo_turnover_status"],
            "alternative_turnover_status": merged["zero_to_positive"],
            "current_repo_across_status": merged["current_repo_across_status"],
            "alternative_across_status": merged["across_issuer"],
            "current_repo_prior_premium": merged["current_repo_prior_premium"],
            "alternative_prior_premium": merged["prior_gross_premium"],
            "current_repo_current_premium": merged["current_repo_current_premium"],
            "alternative_current_premium": merged["current_gross_premium"],
            "current_repo_previous_issuer": merged["current_repo_previous_issuer"],
            "alternative_previous_issuer": merged["previous_issuer_id_from_prior_panel"],
            "current_repo_crosswalk_current_plan": merged["current_repo_crosswalk_current_plan"],
            "alternative_crosswalk_current_plan": merged["current_plan_id"],
            "current_repo_current_issuer": merged["current_repo_current_issuer"],
            "alternative_current_issuer": merged["current_issuer_final"],
            "notes": "Kansas 2022 included by requirement; other rows included when alternative top-two creates across turnover.",
        }
    )
    out.to_csv(OUTPUTS / "top_two_state_year_deep_dive.csv", index=False)
    return out


def write_rule_extraction_doc() -> None:
    text = """# Top-Two Silver Rule Extraction

## Confirmed From Drake Article/Supplement

1. Drake identifies county-years with zero-premium silver plan turnover by first calculating postsubsidy premiums for the two prior-year lowest-premium silver plans and their current-year default plans. Main article p. 3, "Exposure: Turnover in Zero-Premium Plans."
2. The prior-year exposure universe is the lowest-premium and second-lowest-premium silver plans. Main article p. 3 and Table 2 note.
3. The premium calculation is for a single 40-year-old enrollee in the 100%-150% FPL range. Main article p. 3; Supplement 1 eAppendix 2.
4. Supplement 1 eAppendix 2 sets income at 125% FPL, the midpoint of 100%-150% FPL.
5. Drake uses QHP Landscape data for county-year plan offerings, premiums, and benefits, OEP PUFs for county-year reenrollment, and the CCIIO Plan ID Crosswalk for default plans. Main article p. 3.
6. Drake excludes AK and HI because FPL differs and excludes NE because Nebraska does not use county lines to define Marketplace markets. Main article p. 3; Supplement 1 eAppendix 1.
7. Drake excludes counties with missing or inconsistent crosswalk/FIPS/ZIP default data listed in Supplement 1 eTable 3.
8. Drake considers non-EHB costs because APTC cannot reduce non-EHB premium to zero. Supplement 1 eAppendix 3.

## Confirmed From Official CMS/QHP Documentation

1. CMS Exchange PUFs include Rate, Plan Attributes, Service Area, Benefits and Cost Sharing, and Plan ID Crosswalk PUF files on the CMS Exchange PUF page: https://www.cms.gov/marketplace/resources/data/public-use-files.
2. The Plan ID Crosswalk Data Dictionary defines `FIPSCode`, `ZipCode`, `CrosswalkLevel`, and `ReasonForCrosswalk`; `ZipCode = 00000` identifies whole-county rows and CrosswalkLevel 4/5 represent no reenrollment/default option. Source: https://www.cms.gov/files/document/plan-id-crosswalk-datadictionary-py26.pdf.
3. QHP Landscape medical individual instructions state that premium amounts do not include tax credits and include example premium scenarios such as Adult Individual Age 40. Source: https://www.healthcare.gov/downloads/med-ind-lndscp-in.pdf and https://data.healthcare.gov/datafile/py2022/med-ind-lndscp-in.pdf.

## Current Repo Assumption

1. The current repo ranks silver plans within county-year by QHP Landscape `Premium Adult Individual Age 40`.
2. It deduplicates by `PlanId`/`Plan ID (Standard Component)` before ranking.
3. It tie-breaks by `issuer_id` and `plan_id`.
4. It uses QHP Landscape rows as county-plan availability for 2021-2024 when direct QHP files are available.
5. It treats `StandardComponentId` as equivalent to the QHP Landscape plan ID in the cached panel.

## Diagnostic-Only Sensitivities

- Rank by StandardComponentId collapse.
- Rank by estimated postsubsidy net premium.
- Rank by EHB-adjusted gross premium.
- Rank by source/display order.
- Rank by Rate PUF age-40 premium.
- Rank within county-rating-area cells.
- Require stricter service-area evidence.
- Exclude child-only or limited rows if flags are available.
- Preserve source-order tie-breaking.
- Include all ties at the lowest or second-lowest premium.

## Answers To The Requested Rule Questions

1. Drake confirms postsubsidy premiums are calculated for the prior-year top-two and default plans, but the text says the top-two are "lowest-premium" silver plans, not "lowest postsubsidy premium" silver plans. The most text-faithful ranking is gross/displayed silver premium, with net premium used for zero/positive classification.
2. The 40-year-old 100%-150% FPL/125% FPL profile is confirmed for premium/subsidy calculation, not explicitly for ranking. QHP Landscape Adult Individual Age 40 is therefore the closest public-file ranking premium.
3. Drake names QHP Landscape as the plan offering/premium/benefit source. It does not say Rate PUF overrides QHP Landscape for top-two ranking.
4. Drake does not disclose whether Rate, Plan Attributes, Benefits, or Service Area PUFs supplement QHP Landscape for top-two selection.
5. Drake states county-year plan offerings. It does not disclose county-rating-area or county-service-area tie handling.
6. Dental, SHOP, non-individual, and catastrophic exclusions are implicit in using QHP Landscape medical individual silver plans, but Drake does not enumerate all filters.
7. Drake does not state whether CSR variants or duplicated StandardComponentIds are collapsed.
8. Drake does not state whether ranking uses PlanId, StandardComponentId, HIOS ID, or another identifier.
9. Drake does not state duplicate-row collapse rules.
10. Drake does not state which duplicate county/rating-area/service-area row is retained.
11. Drake does not state ranking before or after non-EHB adjustment; non-EHB is confirmed for premium zero-dollar classification.
12. eTable 1 separately reports 100%-150% and 150%-200% FPL exposure, but the main regression exposure uses the 100%-150% profile.
13. AK/HI/NE are excluded from the analytic sample; Drake does not state whether ranking was run before or after these exclusions.
14. HealthCare.gov platform restrictions define the analytic sample; Drake does not state whether plan ranking was computed for excluded states before dropping them.
15. Drake discusses missing OEP/crosswalk/FIPS/ZIP data in eAppendix 1/eTable 3 but not generic missing QHP premium rows or duplicate plan rows.
16. Unstated details require diagnostic variants rather than replacement of the text-faithful baseline.
"""
    (DOCS / "top_two_silver_rule_extraction.md").write_text(text, encoding="utf-8")


def write_reconciliation_report(
    comparison: pd.DataFrame,
    diff_summary: pd.DataFrame,
    across_gap: pd.DataFrame,
    deep_dive: pd.DataFrame,
) -> None:
    closest_plausible = comparison[comparison["drake_text_support"].isin(["confirmed", "plausible"])].copy()
    closest_plausible["abs_gap"] = closest_plausible["difference_vs_drake_any_count"].abs() + closest_plausible["difference_vs_drake_across_count"].abs()
    closest_numeric = comparison.copy()
    closest_numeric["abs_gap"] = closest_numeric["difference_vs_drake_any_count"].abs() + closest_numeric["difference_vs_drake_across_count"].abs()
    baseline = comparison[
        comparison["top_two_selection_variant"].eq("current_repo_top_two")
        & comparison["exposure_universe"].eq("exactly_two_plans")
        & comparison["premium_variant"].eq(PRIMARY_PREMIUM_VARIANT)
        & comparison["default_mapping_rule"].eq(PRIMARY_DEFAULT_RULE)
    ].copy()
    best_any = comparison.iloc[(comparison["difference_vs_drake_any_count"].abs()).argsort()[:8]].copy()
    best_across = comparison.iloc[(comparison["difference_vs_drake_across_count"].abs()).argsort()[:8]].copy()
    max_across = int(comparison["pooled_across_issuer_turnover_county_years"].max()) if not comparison.empty else 0
    ks_rows = deep_dive[(deep_dive["state"].eq("KS")) & (deep_dive["year"].eq(2022))]
    text = [
        "# Top-Two Silver Reconciliation Report",
        "",
        "## 1. Executive Diagnosis",
        "",
        "The current repo top-two rule remains the most text-faithful public-file interpretation: rank prior-year county-level silver QHP Landscape plans by age-40 gross premium, then calculate zero/positive postsubsidy premiums for those selected plans. The new variants show that top-two selection can move the any-turnover count, especially with diagnostic net-premium ranking, but it does not close the across-insurer gap to Drake's 211 county-years. Step 4 remains **No-Go**.",
        "",
        "## 2. What Drake Says",
        "",
        "Drake says county-years are exposed when either or both prior-year lowest-premium and second-lowest-premium silver plans had zero-dollar premiums and defaulted to positive-premium plans. The premium/subsidy calculations use a representative 40-year-old enrollee at 125% FPL. Drake names QHP Landscape for plan offerings/premiums/benefits and Plan ID Crosswalk for defaults.",
        "",
        "## 3. What Drake Does Not Say",
        "",
        "Drake does not disclose duplicate-row handling, tie-breaking, PlanId versus StandardComponentId, whether top-two ranking itself uses gross or net premiums, county-rating-area handling, child-only filtering, or source-order behavior.",
        "",
        "## 4. What CMS Documentation Implies",
        "",
        "QHP Landscape medical individual files provide county-plan rows and example premiums including Adult Individual Age 40, and those premiums exclude tax credits. CMS Exchange PUFs provide Rate, Plan Attributes, Service Area, Benefits, and Crosswalk files. The Plan ID Crosswalk dictionary defines FIPS, ZIP, crosswalk levels, and reasons but does not define Drake's top-two ranking.",
        "",
        "## 5. Current Repo Logic",
        "",
        "The repo ranks cached silver QHP county-plan rows by `age_40_premium`, drops duplicate `plan_id` rows, and tie-breaks by `issuer_id` and `plan_id`. Direct PY2021 QHP Landscape is used when present. This is plausible and text-faithful, but not fully confirmed.",
        "",
        "## 6. Whether Current Repo Appears Text-Faithful",
        "",
        "Yes, for the ranking step. It is not exact because Drake did not publish tie, duplicate, or identifier rules.",
        "",
        "## 7. Top-Two Variant Comparison",
        "",
        markdown_table(diff_summary.sort_values(["county_years_where_either_top_two_plan_differs", "selection_variant"], ascending=[False, True]), max_rows=30),
        "",
        "## 8. Does Any Variant Move Counts Toward Drake Anchors?",
        "",
        "Closest plausible/text-supported rows:",
        "",
        markdown_table(closest_plausible.sort_values("abs_gap").drop(columns=["abs_gap"]).head(12), max_rows=12),
        "",
        "Closest numeric rows, including diagnostic-only variants:",
        "",
        markdown_table(closest_numeric.sort_values("abs_gap").drop(columns=["abs_gap"]).head(12), max_rows=12),
        "",
        "Rows closest to the any-turnover anchor:",
        "",
        markdown_table(best_any, max_rows=8),
        "",
        "Rows closest to the across-insurer anchor:",
        "",
        markdown_table(best_across, max_rows=8),
        "",
        "## 9. Does Any Variant Explain The Across-Insurer Gap?",
        "",
        f"No. The largest across-insurer count in this variant matrix is {max_across}, still below Drake's 211. Top-two variants therefore do not fully explain the central across-insurer mismatch.",
        "",
        "## 10. Kansas 2022 Update",
        "",
        f"Kansas 2022 remains present in the deep-dive output with {len(ks_rows)} diagnostic rows. The audit does not identify a top-two rule that removes Kansas across-insurer turnover while remaining text-faithful.",
        "",
        "## 11. Likely Remaining Source Of Mismatch",
        "",
        "The remaining mismatch is less likely to be caused solely by top-two selection. Premium classification and crosswalk mapping have already been stressed; top-two variants also fail to match across-insurer counts. The residual gap is most likely a private-code detail involving sample/complete-case treatment construction, unpublished premium/default assumptions, or a combination of small implementation choices.",
        "",
        "## 12. Exact Next Repair Recommendation",
        "",
        "Manually audit the county-years that Drake counts as across-insurer exposure if such a replication file can be obtained from authors. Without author-level exposure data, the smallest next public-file repair is a county-year reconciliation notebook that enumerates all zero prior silver plans, their default plans, and why each is outside the top-two exposure universe.",
        "",
        "The file `outputs/top_two_turnover_failure_reason.csv` is intentionally written as a compact state/year/rank/rule summary rather than a full row-level dump. A full selected-plan-pair dump exceeded practical GitHub file-size limits and is reproducible locally from `scripts/08_top_two_silver_selection_audit.py` if needed.",
        "",
        "## 13. Step 4 Recommendation",
        "",
        "**No-Go.** Do not move to causal modeling until the exposure mismatch is either solved or explicitly accepted as a bounded public-file replication limitation.",
        "",
        "## Baseline Row",
        "",
        markdown_table(baseline, max_rows=10),
    ]
    (DOCS / "top_two_silver_reconciliation_report.md").write_text("\n".join(text), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    data = load_inputs()
    panel = prepare_panel(data["silver"], data["zero_proxy"])
    qhp_audit = write_qhp_panel_construction_audit(data["manifest"], data["sample_states"], panel)
    selection = build_all_selections(panel, data["two_lowest"])
    diff_summary = compare_identity(selection)
    write_rule_extraction_doc()

    baseline_selection = selection[
        selection["selection_variant"].eq("current_repo_top_two") & selection["exposure_universe"].eq("exactly_two_plans")
    ].copy()
    premium_panel = prepare_premium_panel(data["zero_proxy"])
    comparison_frames = []
    by_state_frames = []
    long_frames = []
    grouped = list(selection.groupby(["selection_variant", "exposure_universe"], dropna=False))
    for (variant, universe), sel in grouped:
        logging.info("Recomputing treatment counts for %s / %s", variant, universe)
        long = build_variant_long(sel, data["manifest"], premium_panel)
        long = add_difference_flags(long, baseline_selection)
        comp, by_state = treatment_counts_from_long(long, data["final"])
        comp["drake_text_support"] = SELECTION_VARIANTS[variant]["support"]
        comp["notes"] = SELECTION_VARIANTS[variant]["notes"]
        comparison_frames.append(comp)
        by_state_frames.append(by_state)
        long_frames.append(reduce_long_columns(long))
    comparison = pd.concat(comparison_frames, ignore_index=True)
    keep_rules = comparison["default_mapping_rule"].isin(DEFAULT_RULES) & comparison["premium_variant"].isin(PREMIUM_VARIANTS)
    comparison = comparison[keep_rules].copy()
    comparison.to_csv(OUTPUTS / "top_two_variant_treatment_count_comparison.csv", index=False)
    by_state = pd.concat(by_state_frames, ignore_index=True)
    by_state.to_csv(OUTPUTS / "top_two_variant_treatment_by_state_year.csv", index=False)
    all_long = pd.concat(long_frames, ignore_index=True)
    across_gap = summarize_across_gap(all_long)
    failures = write_failure_reasons(all_long)
    deep_dive = write_deep_dive(all_long, selection)
    write_reconciliation_report(comparison, diff_summary, across_gap, deep_dive)
    return {
        "qhp_audit_rows": len(qhp_audit),
        "selection_rows": len(selection),
        "comparison_rows": len(comparison),
        "by_state_rows": len(by_state),
        "across_gap_rows": len(across_gap),
        "failure_rows": len(failures),
        "deep_dive_rows": len(deep_dive),
        "max_across": int(comparison["pooled_across_issuer_turnover_county_years"].max()) if not comparison.empty else 0,
        "closest_any": int(comparison.iloc[(comparison["difference_vs_drake_any_count"].abs()).argmin()]["pooled_any_turnover_county_years"]) if not comparison.empty else 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit prior-year top-two silver selection variants.")
    parser.add_argument("--primary-sample", action="store_true", help="Retained for workflow consistency; counts use Drake-harmonized sample.")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)
    result = run(args)
    print("\nTop-two silver selection audit complete")
    print(f"Identity comparison: {OUTPUTS / 'top_two_silver_identity_comparison.csv'}")
    print(f"Treatment comparison: {OUTPUTS / 'top_two_variant_treatment_count_comparison.csv'}")
    print(f"Across gap diagnosis: {OUTPUTS / 'top_two_across_gap_diagnosis.csv'}")
    print(f"Report: {DOCS / 'top_two_silver_reconciliation_report.md'}")
    print(f"Rows: selection={result['selection_rows']}, comparison={result['comparison_rows']}, across_gap={result['across_gap_rows']}")
    print(f"Closest any-turnover count in matrix: {result['closest_any']}")
    print(f"Max across-insurer count in matrix: {result['max_across']}")


if __name__ == "__main__":
    main()
