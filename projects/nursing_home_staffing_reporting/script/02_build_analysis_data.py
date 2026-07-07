from __future__ import annotations

import csv
import re
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TEMP = ROOT / "temp"
RAW = TEMP / "raw_downloads"
INTERMEDIATE = TEMP / "intermediate"

PBJ_SOURCE_FILE = TEMP / "pbj_daily_sources.csv"
PROVIDER_SELECTION_FILE = TEMP / "provider_archive_selection.csv"
SOURCE_INVENTORY = TEMP / "source_inventory.csv"


PBJ_BASE_COLS = {
    "provnum",
    "state",
    "cy_qtr",
    "workdate",
    "mdscensus",
    "hrs_rndon",
    "hrs_rnadmin",
    "hrs_rn",
    "hrs_lpnadmin",
    "hrs_lpn",
    "hrs_cna",
    "hrs_natrn",
    "hrs_medaide",
    "hrs_rndon_emp",
    "hrs_rnadmin_emp",
    "hrs_rn_emp",
    "hrs_lpnadmin_emp",
    "hrs_lpn_emp",
    "hrs_cna_emp",
    "hrs_natrn_emp",
    "hrs_medaide_emp",
    "hrs_rndon_ctr",
    "hrs_rnadmin_ctr",
    "hrs_rn_ctr",
    "hrs_lpnadmin_ctr",
    "hrs_lpn_ctr",
    "hrs_cna_ctr",
    "hrs_natrn_ctr",
    "hrs_medaide_ctr",
}

RN_COLS = ["hrs_rndon", "hrs_rnadmin", "hrs_rn"]
LPN_COLS = ["hrs_lpnadmin", "hrs_lpn"]
AIDE_COLS = ["hrs_cna", "hrs_natrn", "hrs_medaide"]
EMP_COLS = [
    "hrs_rndon_emp",
    "hrs_rnadmin_emp",
    "hrs_rn_emp",
    "hrs_lpnadmin_emp",
    "hrs_lpn_emp",
    "hrs_cna_emp",
    "hrs_natrn_emp",
    "hrs_medaide_emp",
]
CTR_COLS = [
    "hrs_rndon_ctr",
    "hrs_rnadmin_ctr",
    "hrs_rn_ctr",
    "hrs_lpnadmin_ctr",
    "hrs_lpn_ctr",
    "hrs_cna_ctr",
    "hrs_natrn_ctr",
    "hrs_medaide_ctr",
]


def norm_col(c: str) -> str:
    c = c.strip().lower()
    c = c.replace("%", "percent")
    c = re.sub(r"[^a-z0-9]+", "_", c)
    return re.sub(r"_+", "_", c).strip("_")


def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def zfill_ccn(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.zfill(6)


def read_inventory() -> list[dict]:
    if not SOURCE_INVENTORY.exists() or SOURCE_INVENTORY.stat().st_size == 0:
        return []
    with SOURCE_INVENTORY.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_inventory(rows: list[dict]) -> None:
    fieldnames = [
        "source_name",
        "official_source",
        "download_access_date",
        "file_period",
        "row_count",
        "column_count",
        "checksum",
        "status",
    ]
    with SOURCE_INVENTORY.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def append_inventory(new_rows: list[dict]) -> None:
    rows = read_inventory()
    rows.extend(new_rows)
    if rows:
        df = pd.DataFrame(rows)
        df = df.drop_duplicates(
            subset=["source_name", "official_source", "file_period", "status"],
            keep="last",
        )
        rows = df.to_dict("records")
    write_inventory(rows)


def pbj_usecols(url: str) -> tuple[list[str], dict[str, str]]:
    header = pd.read_csv(url, nrows=0, encoding="cp1252", encoding_errors="replace")
    mapping = {c: norm_col(c) for c in header.columns}
    usecols = [c for c, nc in mapping.items() if nc in PBJ_BASE_COLS]
    return usecols, mapping


def aggregate_pbj_daily() -> tuple[pd.DataFrame, list[dict]]:
    sources = pd.read_csv(PBJ_SOURCE_FILE)
    grouped_parts = []
    source_rows = []
    for _, src in sources.iterrows():
        url = src["download_url"]
        temporal = src["temporal"]
        print(f"Streaming PBJ daily nurse staffing {temporal}")
        usecols, mapping = pbj_usecols(url)
        row_count = 0
        col_count = len(usecols)
        for chunk in pd.read_csv(
            url,
            usecols=usecols,
            dtype=str,
            chunksize=250_000,
            encoding="cp1252",
            encoding_errors="replace",
        ):
            row_count += len(chunk)
            chunk = chunk.rename(columns={c: mapping[c] for c in chunk.columns})
            for c in PBJ_BASE_COLS:
                if c not in chunk.columns:
                    chunk[c] = np.nan
            chunk["facility_id"] = zfill_ccn(chunk["provnum"])
            chunk["state"] = chunk["state"].astype(str).str.strip().str.upper()
            chunk["workdate"] = pd.to_datetime(chunk["workdate"], errors="coerce")
            chunk = chunk.dropna(subset=["facility_id", "workdate"])
            chunk["month"] = chunk["workdate"].dt.to_period("M").astype(str)
            chunk["quarter"] = chunk["workdate"].dt.to_period("Q").astype(str)
            chunk["is_weekend"] = chunk["workdate"].dt.weekday.ge(5).astype(int)
            for c in ["mdscensus"] + RN_COLS + LPN_COLS + AIDE_COLS + EMP_COLS + CTR_COLS:
                chunk[c] = to_num(chunk[c]).fillna(0.0)
            chunk["rn_hours"] = chunk[RN_COLS].sum(axis=1)
            chunk["lpn_hours"] = chunk[LPN_COLS].sum(axis=1)
            chunk["aide_hours"] = chunk[AIDE_COLS].sum(axis=1)
            chunk["total_nurse_hours"] = chunk["rn_hours"] + chunk["lpn_hours"] + chunk["aide_hours"]
            chunk["employee_nurse_hours"] = chunk[EMP_COLS].sum(axis=1)
            chunk["contract_nurse_hours"] = chunk[CTR_COLS].sum(axis=1)
            agg = (
                chunk.groupby(["facility_id", "state", "month", "quarter", "is_weekend"], dropna=False)
                .agg(
                    days=("workdate", "nunique"),
                    resident_days=("mdscensus", "sum"),
                    rn_hours=("rn_hours", "sum"),
                    lpn_hours=("lpn_hours", "sum"),
                    aide_hours=("aide_hours", "sum"),
                    total_nurse_hours=("total_nurse_hours", "sum"),
                    employee_nurse_hours=("employee_nurse_hours", "sum"),
                    contract_nurse_hours=("contract_nurse_hours", "sum"),
                )
                .reset_index()
            )
            grouped_parts.append(agg)
        source_rows.append(
            {
                "source_name": "Payroll Based Journal Daily Nurse Staffing",
                "official_source": url,
                "download_access_date": date.today().isoformat(),
                "file_period": temporal,
                "row_count": row_count,
                "column_count": col_count,
                "checksum": "",
                "status": "streamed and aggregated to facility-month",
            }
        )
        print(f"  rows: {row_count:,}")

    daily_grouped = pd.concat(grouped_parts, ignore_index=True)
    daily_grouped = (
        daily_grouped.groupby(["facility_id", "state", "month", "quarter", "is_weekend"], dropna=False)
        .sum(numeric_only=True)
        .reset_index()
    )
    return daily_grouped, source_rows


def make_month_panel(grouped: pd.DataFrame) -> pd.DataFrame:
    key_cols = ["facility_id", "state", "month", "quarter"]
    wk = grouped[grouped["is_weekend"] == 1].drop(columns=["is_weekend"]).copy()
    wd = grouped[grouped["is_weekend"] == 0].drop(columns=["is_weekend"]).copy()
    wk = wk.rename(columns={c: f"weekend_{c}" for c in wk.columns if c not in key_cols})
    wd = wd.rename(columns={c: f"weekday_{c}" for c in wd.columns if c not in key_cols})
    out = pd.merge(wd, wk, on=key_cols, how="outer")
    for c in out.columns:
        if c.startswith("weekend_") or c.startswith("weekday_"):
            out[c] = out[c].fillna(0.0)
    out["days"] = out["weekday_days"] + out["weekend_days"]
    out["resident_days"] = out["weekday_resident_days"] + out["weekend_resident_days"]
    for prefix in ["weekday", "weekend"]:
        denom = out[f"{prefix}_resident_days"].replace(0, np.nan)
        out[f"{prefix}_rn_hprd"] = out[f"{prefix}_rn_hours"] / denom
        out[f"{prefix}_lpn_hprd"] = out[f"{prefix}_lpn_hours"] / denom
        out[f"{prefix}_aide_hprd"] = out[f"{prefix}_aide_hours"] / denom
        out[f"{prefix}_total_nurse_hprd"] = out[f"{prefix}_total_nurse_hours"] / denom
    denom_all = out["resident_days"].replace(0, np.nan)
    out["rn_hprd"] = (out["weekday_rn_hours"] + out["weekend_rn_hours"]) / denom_all
    out["lpn_hprd"] = (out["weekday_lpn_hours"] + out["weekend_lpn_hours"]) / denom_all
    out["aide_hprd"] = (out["weekday_aide_hours"] + out["weekend_aide_hours"]) / denom_all
    out["total_nurse_hprd"] = (
        out["weekday_total_nurse_hours"] + out["weekend_total_nurse_hours"]
    ) / denom_all
    out["rn_share_total_hours"] = (
        out["weekday_rn_hours"] + out["weekend_rn_hours"]
    ) / (out["weekday_total_nurse_hours"] + out["weekend_total_nurse_hours"]).replace(0, np.nan)
    out["contract_share_total_hours"] = (
        out["weekday_contract_nurse_hours"] + out["weekend_contract_nurse_hours"]
    ) / (out["weekday_total_nurse_hours"] + out["weekend_total_nurse_hours"]).replace(0, np.nan)
    out["weekend_minus_weekday_total_hprd"] = out["weekend_total_nurse_hprd"] - out["weekday_total_nurse_hprd"]
    out["weekend_minus_weekday_rn_hprd"] = out["weekend_rn_hprd"] - out["weekday_rn_hprd"]
    out["weekday_minus_weekend_total_hprd"] = -out["weekend_minus_weekday_total_hprd"]
    out["weekday_minus_weekend_rn_hprd"] = -out["weekend_minus_weekday_rn_hprd"]
    out["month_date"] = pd.PeriodIndex(out["month"], freq="M").to_timestamp()
    return out.sort_values(["facility_id", "month"]).reset_index(drop=True)


def quarter_panel(monthly: pd.DataFrame) -> pd.DataFrame:
    sum_cols = [
        "weekday_days",
        "weekend_days",
        "weekday_resident_days",
        "weekend_resident_days",
        "weekday_rn_hours",
        "weekend_rn_hours",
        "weekday_lpn_hours",
        "weekend_lpn_hours",
        "weekday_aide_hours",
        "weekend_aide_hours",
        "weekday_total_nurse_hours",
        "weekend_total_nurse_hours",
        "weekday_contract_nurse_hours",
        "weekend_contract_nurse_hours",
    ]
    q = monthly.groupby(["facility_id", "state", "quarter"], dropna=False)[sum_cols].sum().reset_index()
    q["days"] = q["weekday_days"] + q["weekend_days"]
    q["resident_days"] = q["weekday_resident_days"] + q["weekend_resident_days"]
    for prefix in ["weekday", "weekend"]:
        denom = q[f"{prefix}_resident_days"].replace(0, np.nan)
        q[f"{prefix}_rn_hprd"] = q[f"{prefix}_rn_hours"] / denom
        q[f"{prefix}_lpn_hprd"] = q[f"{prefix}_lpn_hours"] / denom
        q[f"{prefix}_aide_hprd"] = q[f"{prefix}_aide_hours"] / denom
        q[f"{prefix}_total_nurse_hprd"] = q[f"{prefix}_total_nurse_hours"] / denom
    denom_all = q["resident_days"].replace(0, np.nan)
    q["rn_hprd"] = (q["weekday_rn_hours"] + q["weekend_rn_hours"]) / denom_all
    q["total_nurse_hprd"] = (q["weekday_total_nurse_hours"] + q["weekend_total_nurse_hours"]) / denom_all
    q["rn_share_total_hours"] = (q["weekday_rn_hours"] + q["weekend_rn_hours"]) / (
        q["weekday_total_nurse_hours"] + q["weekend_total_nurse_hours"]
    ).replace(0, np.nan)
    q["contract_share_total_hours"] = (
        q["weekday_contract_nurse_hours"] + q["weekend_contract_nurse_hours"]
    ) / (q["weekday_total_nurse_hours"] + q["weekend_total_nurse_hours"]).replace(0, np.nan)
    q["weekend_minus_weekday_total_hprd"] = q["weekend_total_nurse_hprd"] - q["weekday_total_nurse_hprd"]
    q["weekend_minus_weekday_rn_hprd"] = q["weekend_rn_hprd"] - q["weekday_rn_hprd"]
    q["weekday_minus_weekend_total_hprd"] = -q["weekend_minus_weekday_total_hprd"]
    q["weekday_minus_weekend_rn_hprd"] = -q["weekend_minus_weekday_rn_hprd"]
    q["quarter_start"] = pd.PeriodIndex(q["quarter"], freq="Q").to_timestamp()
    return q.sort_values(["facility_id", "quarter"]).reset_index(drop=True)


def zip_member(pattern: str, names: list[str]) -> str | None:
    matches = [n for n in names if re.search(pattern, n, flags=re.IGNORECASE) and n.lower().endswith(".csv")]
    if not matches:
        return None
    matches.sort(key=len)
    return matches[0]


def read_zip_csv(z: zipfile.ZipFile, member: str, nrows: int | None = None) -> pd.DataFrame:
    with z.open(member) as f:
        return pd.read_csv(f, encoding="cp1252", encoding_errors="replace", low_memory=False, nrows=nrows)


def pick(df: pd.DataFrame, names: list[str]) -> pd.Series:
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series([np.nan] * len(df), index=df.index)


def process_provider_archives() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict]]:
    selection = pd.read_csv(PROVIDER_SELECTION_FILE)
    provider_frames = []
    survey_frames = []
    citation_frames = []
    inventory_rows = []
    staffing_tags = {"0725", "725", "0726", "726", "0727", "727", "0728", "728", "0732", "732"}
    severe_letters = set("GHIJKL")

    for _, row in selection.iterrows():
        zip_path = ROOT / row["local_path"]
        snapshot_date = row["date"]
        print(f"Parsing provider archive {snapshot_date}")
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            provider_member = zip_member(r"(NH_ProviderInfo|ProviderInfo)", names)
            survey_member = zip_member(r"(NH_SurveySummary|SurveySummary)", names)
            citation_member = zip_member(r"(NH_Health(Citations|Deficiencies)|HealthDeficiencies)", names)

            if provider_member:
                df = read_zip_csv(z, provider_member)
                raw_cols = len(df.columns)
                df = df.rename(columns={c: norm_col(c) for c in df.columns})
                out = pd.DataFrame(
                    {
                        "facility_id": zfill_ccn(
                            pick(df, ["federal_provider_number", "cms_certification_number_ccn"])
                        ),
                        "snapshot_date": pd.to_datetime(snapshot_date),
                        "processing_date": pd.to_datetime(
                            pick(df, ["processing_date", "processed_date"]), errors="coerce"
                        ),
                        "provider_name": pick(df, ["provider_name"]),
                        "state": pick(df, ["provider_state", "state"]),
                        "ownership_type": pick(df, ["ownership_type"]),
                        "certified_beds": to_num(
                            pick(df, ["number_of_certified_beds", "certified_beds"])
                        ),
                        "avg_residents_per_day": to_num(
                            pick(df, ["average_number_of_residents_per_day"])
                        ),
                        "provider_type": pick(df, ["provider_type"]),
                        "in_hospital": pick(df, ["provider_resides_in_hospital"]),
                        "special_focus_status": pick(df, ["special_focus_status"]),
                        "overall_rating": to_num(pick(df, ["overall_rating"])),
                        "health_inspection_rating": to_num(pick(df, ["health_inspection_rating"])),
                        "qm_rating": to_num(pick(df, ["qm_rating"])),
                        "staffing_rating": to_num(pick(df, ["staffing_rating"])),
                        "rn_staffing_rating": to_num(pick(df, ["rn_staffing_rating"])),
                        "reported_total_nurse_hprd": to_num(
                            pick(df, ["reported_total_nurse_staffing_hours_per_resident_per_day"])
                        ),
                        "reported_rn_hprd": to_num(
                            pick(df, ["reported_rn_staffing_hours_per_resident_per_day"])
                        ),
                        "adjusted_total_nurse_hprd": to_num(
                            pick(df, ["adjusted_total_nurse_staffing_hours_per_resident_per_day"])
                        ),
                        "adjusted_rn_hprd": to_num(
                            pick(df, ["adjusted_rn_staffing_hours_per_resident_per_day"])
                        ),
                        "reported_weekend_total_nurse_hprd": to_num(
                            pick(
                                df,
                                [
                                    "total_number_of_nurse_staff_hours_per_resident_per_day_on_the_weekend",
                                    "total_nurse_staffing_hours_per_resident_per_day_on_the_weekend",
                                ],
                            )
                        ),
                        "reported_weekend_rn_hprd": to_num(
                            pick(
                                df,
                                [
                                    "registered_nurse_hours_per_resident_per_day_on_the_weekend",
                                    "rn_hours_per_resident_per_day_on_the_weekend",
                                ],
                            )
                        ),
                        "total_nursing_staff_turnover": to_num(
                            pick(df, ["total_nursing_staff_turnover"])
                        ),
                        "rn_turnover": to_num(pick(df, ["registered_nurse_turnover"])),
                        "administrator_turnover": to_num(pick(df, ["administrator_turnover"])),
                        "rating_cycle_1_total_health_deficiencies": to_num(
                            pick(df, ["rating_cycle_1_total_number_of_health_deficiencies"])
                        ),
                        "rating_cycle_1_health_deficiency_score": to_num(
                            pick(df, ["rating_cycle_1_health_deficiency_score"])
                        ),
                        "total_weighted_health_survey_score": to_num(
                            pick(df, ["total_weighted_health_survey_score"])
                        ),
                        "facility_reported_incidents": to_num(
                            pick(df, ["number_of_facility_reported_incidents"])
                        ),
                        "substantiated_complaints": to_num(
                            pick(df, ["number_of_substantiated_complaints"])
                        ),
                        "infection_control_citations": to_num(
                            pick(df, ["number_of_citations_from_infection_control_inspections"])
                        ),
                        "number_of_fines": to_num(pick(df, ["number_of_fines"])),
                        "total_fines_dollars": to_num(pick(df, ["total_amount_of_fines_in_dollars"])),
                        "total_penalties": to_num(pick(df, ["total_number_of_penalties"])),
                    }
                )
                provider_frames.append(out)
                inventory_rows.append(
                    {
                        "source_name": "Provider Information archive file",
                        "official_source": row["url"],
                        "download_access_date": date.today().isoformat(),
                        "file_period": snapshot_date,
                        "row_count": len(df),
                        "column_count": raw_cols,
                        "checksum": row.get("sha256", ""),
                        "status": f"parsed {provider_member}",
                    }
                )

            if survey_member:
                sdf = read_zip_csv(z, survey_member)
                raw_cols = len(sdf.columns)
                sdf = sdf.rename(columns={c: norm_col(c) for c in sdf.columns})
                sout = pd.DataFrame(
                    {
                        "facility_id": zfill_ccn(
                            pick(sdf, ["federal_provider_number", "cms_certification_number_ccn"])
                        ),
                        "snapshot_date": pd.to_datetime(snapshot_date),
                        "inspection_cycle": to_num(pick(sdf, ["inspection_cycle"])),
                        "health_survey_date": pd.to_datetime(
                            pick(sdf, ["health_survey_date"]), errors="coerce"
                        ),
                        "total_health_deficiencies": to_num(
                            pick(sdf, ["total_number_of_health_deficiencies"])
                        ),
                        "total_fire_safety_deficiencies": to_num(
                            pick(sdf, ["total_number_of_fire_safety_deficiencies"])
                        ),
                        "total_complaint_deficiencies": to_num(
                            pick(sdf, ["total_number_of_complaint_health_deficiencies"])
                        ),
                    }
                )
                survey_frames.append(sout)
                inventory_rows.append(
                    {
                        "source_name": "Survey Summary archive file",
                        "official_source": row["url"],
                        "download_access_date": date.today().isoformat(),
                        "file_period": snapshot_date,
                        "row_count": len(sdf),
                        "column_count": raw_cols,
                        "checksum": row.get("sha256", ""),
                        "status": f"parsed {survey_member}",
                    }
                )

            if citation_member:
                cdf = read_zip_csv(z, citation_member)
                raw_cols = len(cdf.columns)
                cdf = cdf.rename(columns={c: norm_col(c) for c in cdf.columns})
                ccn = zfill_ccn(pick(cdf, ["federal_provider_number", "cms_certification_number_ccn"]))
                tag = pick(cdf, ["deficiency_tag_number"]).astype(str).str.extract(r"(\d+)")[0].fillna("")
                scope = pick(cdf, ["scope_severity_code", "scope_severity"]).astype(str).str.upper().str[0]
                desc = (
                    pick(cdf, ["deficiency_description"]).astype(str)
                    + " "
                    + pick(cdf, ["deficiency_category"]).astype(str)
                ).str.lower()
                tmp = pd.DataFrame(
                    {
                        "facility_id": ccn,
                        "severe": scope.isin(severe_letters).astype(int),
                        "staffing_related": (
                            tag.str.zfill(4).isin(staffing_tags)
                            | tag.isin(staffing_tags)
                            | desc.str.contains("staff|nursing services|registered nurse", regex=True, na=False)
                        ).astype(int),
                    }
                )
                cout = (
                    tmp.groupby("facility_id")
                    .agg(
                        health_citation_count=("facility_id", "size"),
                        severe_health_citation_count=("severe", "sum"),
                        staffing_related_citation_count=("staffing_related", "sum"),
                    )
                    .reset_index()
                )
                cout["snapshot_date"] = pd.to_datetime(snapshot_date)
                citation_frames.append(cout)
                inventory_rows.append(
                    {
                        "source_name": "Health Citations archive file",
                        "official_source": row["url"],
                        "download_access_date": date.today().isoformat(),
                        "file_period": snapshot_date,
                        "row_count": len(cdf),
                        "column_count": raw_cols,
                        "checksum": row.get("sha256", ""),
                        "status": f"parsed {citation_member}",
                    }
                )

    provider_panel = pd.concat(provider_frames, ignore_index=True) if provider_frames else pd.DataFrame()
    survey_panel = pd.concat(survey_frames, ignore_index=True) if survey_frames else pd.DataFrame()
    citation_panel = pd.concat(citation_frames, ignore_index=True) if citation_frames else pd.DataFrame()
    return provider_panel, survey_panel, citation_panel, inventory_rows


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    INTERMEDIATE.mkdir(parents=True, exist_ok=True)

    grouped_path = INTERMEDIATE / "pbj_grouped_weekend_flag.parquet"
    if grouped_path.exists():
        print(f"Using cached PBJ aggregate: {grouped_path.relative_to(ROOT)}")
        grouped = pd.read_parquet(grouped_path)
        pbj_inventory = []
    else:
        grouped, pbj_inventory = aggregate_pbj_daily()
        grouped.to_parquet(grouped_path, index=False)

    monthly = make_month_panel(grouped)
    monthly.to_parquet(DATA / "pbj_facility_month.parquet", index=False)
    monthly.to_csv(DATA / "pbj_facility_month_extract.csv", index=False)

    quarterly = quarter_panel(monthly)
    quarterly.to_parquet(DATA / "pbj_facility_quarter.parquet", index=False)

    provider_panel, survey_panel, citation_panel, provider_inventory = process_provider_archives()
    provider_panel.to_parquet(DATA / "provider_snapshot_panel.parquet", index=False)
    survey_panel.to_parquet(DATA / "survey_summary_snapshot_panel.parquet", index=False)
    citation_panel.to_parquet(DATA / "health_citation_snapshot_panel.parquet", index=False)

    # Nearest pre-policy provider characteristics for baseline balance.
    if not provider_panel.empty:
        pre = provider_panel[provider_panel["snapshot_date"] < pd.Timestamp("2022-01-01")].copy()
        if not pre.empty:
            pre = pre.sort_values(["facility_id", "snapshot_date"]).groupby("facility_id").tail(1)
            pre.to_parquet(DATA / "baseline_provider_characteristics_pre2022.parquet", index=False)

    append_inventory(pbj_inventory + provider_inventory)

    with (TEMP / "audit_log.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 2 Raw Data and Schema Audit\n\n"
            f"- PBJ daily nurse staffing aggregated to {len(monthly):,} facility-month rows and {len(quarterly):,} facility-quarter rows.\n"
            f"- Provider archive snapshots parsed to {len(provider_panel):,} provider rows, {len(survey_panel):,} survey-summary rows, and {len(citation_panel):,} facility-snapshot health-citation summaries.\n"
            "- PBJ facility identifier is `PROVNUM`, normalized to six-character `facility_id`.\n"
            "- Provider Data Catalog facility identifier is Federal Provider Number / CMS Certification Number, normalized to the same six-character `facility_id`.\n"
        )
    with (TEMP / "iteration_notes.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 2: Raw Data Acquisition and Schema Audit\n\n"
            "The data cover 2019 Q1 through 2025 Q4 for PBJ daily staffing. Provider Data Catalog snapshots were cached quarterly from 2019 through 2025, with the July 27, 2022 release included. Facility identifiers are normalized consistently across PBJ and Provider Data Catalog files.\n\n"
            "Self-question: The data cover a long pre-period and post-period. PBJ Q1 2020 remains COVID-disrupted and should be excluded in a robustness check rather than silently dropped from all analyses.\n"
        )

    print("Analysis data construction complete.")


if __name__ == "__main__":
    main()
