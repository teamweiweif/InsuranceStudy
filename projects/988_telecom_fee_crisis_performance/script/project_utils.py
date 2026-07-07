from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCRIPT = ROOT / "script"
RESULT = ROOT / "result"
REPORT = ROOT / "report"
TEMP = ROOT / "temp"

RAW = TEMP / "raw_downloads"
SNAP = TEMP / "source_snapshots"
PDF_CHECKS = TEMP / "pdf_extraction_checks"
HAND = TEMP / "hand_validation"
SCRATCH = TEMP / "model_scratch"

SOURCE_INVENTORY = TEMP / "source_inventory.csv"
AUDIT_LOG = TEMP / "audit_log.md"
ITER_NOTES = TEMP / "iteration_notes.md"


SOURCE_COLUMNS = [
    "source_id",
    "source_name",
    "source_type",
    "official_or_secondary",
    "url_or_access_path",
    "download_date",
    "publication_date",
    "coverage_start",
    "coverage_end",
    "unit",
    "geography",
    "file_format",
    "raw_file_path",
    "row_count",
    "column_count",
    "checksum",
    "status",
    "notes",
    "citation_text",
]


STATE_NAME_TO_ABBR = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "Puerto Rico": "PR",
}

ABBR_TO_STATE_NAME = {v: k for k, v in STATE_NAME_TO_ABBR.items()}
ABBR_TO_STATE_NAME.update(
    {
        "AS": "American Samoa",
        "GU": "Guam",
        "MP": "Northern Mariana Islands",
        "VI": "U.S. Virgin Islands",
    }
)

STATE_CODES = set(ABBR_TO_STATE_NAME)

FIPS_TO_ABBR = {
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
    "72": "PR",
}


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def ensure_dirs() -> None:
    for path in [DATA, SCRIPT, RESULT, REPORT, TEMP, RAW, SNAP, PDF_CHECKS, HAND, SCRATCH]:
        path.mkdir(parents=True, exist_ok=True)
    (RAW / "988_state_monthly_reports").mkdir(parents=True, exist_ok=True)
    (RAW / "fcc_988_fee_reports").mkdir(parents=True, exist_ok=True)
    (RAW / "census").mkdir(parents=True, exist_ok=True)
    (RAW / "state_policy_sources").mkdir(parents=True, exist_ok=True)


def browser_headers() -> dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
        )
    }


def today_iso() -> str:
    return date.today().isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def append_audit(message: str) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n- {today_iso()}: {message}\n")


def append_iteration(phase: str, message: str) -> None:
    ITER_NOTES.parent.mkdir(parents=True, exist_ok=True)
    with ITER_NOTES.open("a", encoding="utf-8") as f:
        f.write(f"\n## {phase} - {today_iso()}\n\n{message}\n")


def ensure_source_inventory() -> None:
    if not SOURCE_INVENTORY.exists():
        SOURCE_INVENTORY.parent.mkdir(parents=True, exist_ok=True)
        with SOURCE_INVENTORY.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=SOURCE_COLUMNS).writeheader()


def append_source(row: dict[str, Any]) -> None:
    ensure_source_inventory()
    clean = {col: row.get(col, "") for col in SOURCE_COLUMNS}
    with SOURCE_INVENTORY.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=SOURCE_COLUMNS).writerow(clean)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def parse_month_label(label: str) -> pd.Timestamp:
    m = re.search(r"([A-Za-z]+)\s+(\d{4})", label)
    if not m:
        raise ValueError(f"Cannot parse month label: {label}")
    month = MONTHS[m.group(1).lower()]
    year = int(m.group(2))
    return pd.Timestamp(year=year, month=month, day=1)


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def json_dump(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")


def money_to_float(value: str | float | int | None) -> float | None:
    if value is None or value == "":
        return None
    s = str(value).replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None

