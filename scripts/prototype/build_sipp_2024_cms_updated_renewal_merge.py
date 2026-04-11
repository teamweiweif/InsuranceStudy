from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SIPP_PARQUET = PROJECT_ROOT / "outputs" / "prototype" / "sipp_2024_person_month_flags.parquet"
HISTORICAL_HTML = (
    PROJECT_ROOT
    / "reference"
    / "external"
    / "feasibility_audit"
    / "medicaid_unwinding"
    / "monthly_data_reports_historical.html"
)
RAW_DOWNLOAD_DIR = PROJECT_ROOT / "data" / "raw" / "medicaid_unwinding" / "updated_renewal_outcomes"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "prototype"

STATE_MONTH_PARQUET = OUTPUT_DIR / "cms_updated_renewal_outcomes_state_month_2023.parquet"
MERGED_PARQUET = OUTPUT_DIR / "sipp_2024_cms_updated_renewal_outcomes_merged.parquet"
SUMMARY_JSON = OUTPUT_DIR / "sipp_2024_cms_updated_renewal_merge_summary.json"


MONTH_NAME_TO_NUM = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

STATE_FIPS_TO_ABBR = {
    "01": "AL",
    "02": "AK",
    "04": "AZ",
    "05": "AR",
    "06": "CA",
    "08": "CO",
    "09": "CT",
    "10": "DE",
    "11": "DC",
    "12": "FL",
    "13": "GA",
    "15": "HI",
    "16": "ID",
    "17": "IL",
    "18": "IN",
    "19": "IA",
    "20": "KS",
    "21": "KY",
    "22": "LA",
    "23": "ME",
    "24": "MD",
    "25": "MA",
    "26": "MI",
    "27": "MN",
    "28": "MS",
    "29": "MO",
    "30": "MT",
    "31": "NE",
    "32": "NV",
    "33": "NH",
    "34": "NJ",
    "35": "NM",
    "36": "NY",
    "37": "NC",
    "38": "ND",
    "39": "OH",
    "40": "OK",
    "41": "OR",
    "42": "PA",
    "44": "RI",
    "45": "SC",
    "46": "SD",
    "47": "TN",
    "48": "TX",
    "49": "UT",
    "50": "VT",
    "51": "VA",
    "53": "WA",
    "54": "WV",
    "55": "WI",
    "56": "WY",
}
VALID_STATE_ABBRS = set(STATE_FIPS_TO_ABBR.values())
VALID_STATE_OR_US = VALID_STATE_ABBRS | {"US"}


def parse_updated_renewal_entries() -> list[dict[str, object]]:
    soup = BeautifulSoup(HISTORICAL_HTML.read_text(encoding="utf-8"), "html.parser")

    updated_section = None
    for dt in soup.find_all("dt"):
        if dt.get_text(" ", strip=True) == "Updated Medicaid and CHIP Renewal Outcomes:":
            updated_section = dt.find_next_sibling("dd")
            break

    if updated_section is None:
        raise RuntimeError("Could not locate the updated renewal outcomes section in the local Medicaid HTML.")

    entries: list[dict[str, object]] = []
    for li in updated_section.find_all("li"):
        text = li.get_text(" ", strip=True)
        match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d{4}) Updated Medicaid and CHIP Renewal Outcomes", text)
        if not match:
            continue

        month_name = match.group(1)
        year = int(match.group(2))
        month_num = MONTH_NAME_TO_NUM[month_name]
        reporting_period = year * 100 + month_num

        links = li.find_all("a")
        if len(links) < 2:
            raise RuntimeError(f"Could not find both dataset and Excel links for: {text}")

        dataset_url = links[0].get("href")
        excel_href = links[1].get("href")
        if not dataset_url or not excel_href:
            raise RuntimeError(f"Missing href while parsing: {text}")

        if excel_href.startswith("/"):
            excel_url = f"https://www.medicaid.gov{excel_href}"
        else:
            excel_url = excel_href

        release_match = re.search(r"released ([A-Za-z]+ \d{4})", text)
        release_label = release_match.group(1) if release_match else None

        entries.append(
            {
                "reporting_period": reporting_period,
                "reporting_year": year,
                "reporting_month": month_num,
                "reporting_label": f"{year}-{month_num:02d}",
                "dataset_url": dataset_url,
                "excel_url": excel_url,
                "release_label": release_label,
                "text": text,
            }
        )

    entries.sort(key=lambda x: int(x["reporting_period"]))
    return entries


def download_with_curl(url: str, destination: Path) -> None:
    if destination.exists():
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "curl.exe",
            "-L",
            "--fail",
            "-sS",
            url,
            "-o",
            str(destination),
        ],
        check=True,
    )


def load_month_workbook(path: Path, reporting_period: int, release_label: str | None) -> pd.DataFrame:
    workbook = pd.ExcelFile(path)
    n_sheet = next((name for name in workbook.sheet_names if "Updated Renewals (N)" in name), None)
    pct_sheet = next((name for name in workbook.sheet_names if "Updated Renewals (%)" in name), None)

    if n_sheet is None or pct_sheet is None:
        raise RuntimeError(f"Unexpected workbook structure in {path.name}. Sheets: {workbook.sheet_names}")

    count_df = pd.read_excel(path, sheet_name=n_sheet, header=1)
    pct_df = pd.read_excel(path, sheet_name=pct_sheet, header=1)

    count_df = count_df.dropna(axis=1, how="all")
    pct_df = pct_df.dropna(axis=1, how="all")

    if count_df.shape[1] < 9 or pct_df.shape[1] < 9:
        raise RuntimeError(
            f"Unexpected column count in {path.name}. Got {count_df.shape[1]} count columns and {pct_df.shape[1]} percentage columns."
        )

    count_df = count_df.iloc[:, :9].copy()
    pct_df = pct_df.iloc[:, :9].copy()

    count_df = count_df[count_df["State"].isin(VALID_STATE_OR_US)].copy()
    pct_df = pct_df[pct_df["State"].isin(VALID_STATE_OR_US)].copy()

    if len(count_df) != 52 or len(pct_df) != 52:
        raise RuntimeError(
            f"Expected 52 rows (US + 50 states + DC) in {path.name}; got {len(count_df)} counts and {len(pct_df)} percentages."
        )

    count_df.columns = [
        "state_abbreviation",
        "cms_updated_renewal_due_n",
        "cms_updated_renewed_total_n",
        "cms_updated_renewed_ex_parte_n",
        "cms_updated_renewed_form_n",
        "cms_updated_terminated_total_n",
        "cms_updated_ineligible_form_n",
        "cms_updated_procedural_termination_n",
        "cms_updated_pending_n",
    ]
    pct_df.columns = [
        "state_abbreviation",
        "cms_updated_renewal_due_n_pctbase",
        "cms_updated_renewed_rate",
        "cms_updated_renewed_ex_parte_rate",
        "cms_updated_renewed_form_rate",
        "cms_updated_terminated_rate",
        "cms_updated_ineligible_rate",
        "cms_updated_procedural_rate",
        "cms_updated_pending_rate",
    ]

    merged = count_df.merge(
        pct_df.drop(columns=["cms_updated_renewal_due_n_pctbase"]),
        on="state_abbreviation",
        how="inner",
        validate="one_to_one",
    )

    numeric_columns = [col for col in merged.columns if col != "state_abbreviation"]
    for col in numeric_columns:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")

    merged["reporting_period"] = reporting_period
    merged["reporting_year"] = reporting_period // 100
    merged["reporting_month"] = reporting_period % 100
    merged["reporting_label"] = merged["reporting_year"].astype(str) + "-" + merged["reporting_month"].astype(str).str.zfill(2)
    merged["release_label"] = release_label

    merged["cms_updated_procedural_share_of_terminated"] = (
        merged["cms_updated_procedural_termination_n"] / merged["cms_updated_terminated_total_n"]
    )

    return merged


def build_state_month_table(entries: list[dict[str, object]]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for entry in entries:
        destination = RAW_DOWNLOAD_DIR / Path(str(entry["excel_url"])).name
        download_with_curl(str(entry["excel_url"]), destination)
        frames.append(
            load_month_workbook(
                destination,
                reporting_period=int(entry["reporting_period"]),
                release_label=entry["release_label"],
            )
        )

    state_month = pd.concat(frames, ignore_index=True)
    state_month = state_month.sort_values(["reporting_period", "state_abbreviation"]).reset_index(drop=True)

    return state_month


def build_merged_person_month(state_month: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    sipp = pd.read_parquet(SIPP_PARQUET)
    sipp["state_abbreviation"] = sipp["tehc_st_fips"].map(STATE_FIPS_TO_ABBR)
    sipp["cms_reporting_period"] = sipp["reference_year"] * 100 + sipp["MONTHCODE"].astype(int)

    cms_state_month = state_month[state_month["state_abbreviation"] != "US"].copy()
    cms_state_month = cms_state_month.rename(columns={"reporting_period": "cms_reporting_period"})

    merged = sipp.merge(
        cms_state_month,
        on=["state_abbreviation", "cms_reporting_period"],
        how="left",
        validate="many_to_one",
    )

    merged["cms_updated_renewal_match"] = merged["cms_updated_renewal_due_n"].notna()

    matched_rows = int(merged["cms_updated_renewal_match"].sum())
    total_rows = int(len(merged))
    unmatched_rows = total_rows - matched_rows

    month_match = (
        merged.groupby("MONTHCODE", dropna=False)["cms_updated_renewal_match"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "matched_rows", "count": "total_rows"})
    )
    month_match["matched_share"] = month_match["matched_rows"] / month_match["total_rows"]

    cms_coverage_by_month = (
        cms_state_month.groupby("cms_reporting_period")["cms_updated_renewal_due_n"]
        .apply(lambda s: int(s.notna().sum()))
        .to_dict()
    )
    cms_missing_states_by_month = {}
    for period, sub in cms_state_month.groupby("cms_reporting_period"):
        missing = sorted(sub.loc[sub["cms_updated_renewal_due_n"].isna(), "state_abbreviation"].tolist())
        cms_missing_states_by_month[str(int(period))] = missing

    matched_states = sorted(merged.loc[merged["cms_updated_renewal_match"], "state_abbreviation"].dropna().unique().tolist())
    unmatched_months = sorted(
        month_match.loc[month_match["matched_rows"] == 0, "MONTHCODE"].astype(int).tolist()
    )

    summary = {
        "cms_metric_family": "Updated Medicaid and CHIP Renewal Outcomes",
        "cms_dataset_page": "https://data.medicaid.gov/dataset/e6205a51-e6d7-4849-9882-4483b8a28c41",
        "local_historical_html": str(HISTORICAL_HTML.relative_to(PROJECT_ROOT)),
        "sipp_input_parquet": str(SIPP_PARQUET.relative_to(PROJECT_ROOT)),
        "cms_state_month_output_parquet": str(STATE_MONTH_PARQUET.relative_to(PROJECT_ROOT)),
        "merged_output_parquet": str(MERGED_PARQUET.relative_to(PROJECT_ROOT)),
        "reporting_periods_used": sorted(cms_state_month["cms_reporting_period"].dropna().astype(int).unique().tolist()),
        "cms_state_month_rows": int(len(cms_state_month)),
        "cms_unique_states": int(cms_state_month["state_abbreviation"].nunique()),
        "cms_unique_reporting_periods": int(cms_state_month["cms_reporting_period"].nunique()),
        "sipp_rows": total_rows,
        "matched_rows": matched_rows,
        "unmatched_rows": unmatched_rows,
        "matched_share": matched_rows / total_rows,
        "matched_states": matched_states,
        "matched_months": sorted(
            month_match.loc[month_match["matched_rows"] > 0, "MONTHCODE"].astype(int).tolist()
        ),
        "unmatched_months": unmatched_months,
        "matched_rows_by_month": {
            str(int(row.MONTHCODE)): int(row.matched_rows)
            for row in month_match.itertuples(index=False)
        },
        "total_rows_by_month": {
            str(int(row.MONTHCODE)): int(row.total_rows)
            for row in month_match.itertuples(index=False)
        },
        "matched_share_by_month": {
            str(int(row.MONTHCODE)): float(row.matched_share)
            for row in month_match.itertuples(index=False)
        },
        "cms_available_state_count_by_reporting_period": {
            str(int(period)): count for period, count in sorted(cms_coverage_by_month.items())
        },
        "cms_missing_states_by_reporting_period": cms_missing_states_by_month,
    }

    return merged, summary


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    entries = parse_updated_renewal_entries()
    entries_2023 = [entry for entry in entries if int(entry["reporting_year"]) == 2023]

    if not entries_2023:
        raise RuntimeError("No 2023 updated renewal outcome entries were found in the local Medicaid HTML.")

    state_month = build_state_month_table(entries_2023)
    state_month.to_parquet(STATE_MONTH_PARQUET, index=False)

    merged, summary = build_merged_person_month(state_month)
    merged.to_parquet(MERGED_PARQUET, index=False)

    summary["downloaded_files"] = sorted(path.name for path in RAW_DOWNLOAD_DIR.glob("*.xlsx"))

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
