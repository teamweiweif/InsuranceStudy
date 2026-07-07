from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
TEMP = ROOT / "temp"
RAW = TEMP / "raw_downloads"
POLICY = RAW / "policy_docs"
PROVIDER_ARCHIVES = RAW / "provider_archives"

CMS_DATA_JSON = "https://data.cms.gov/data.json"
PDC_API = "https://data.cms.gov/provider-data/api/1"
PDC_ARCHIVE_NH = f"{PDC_API}/archive/aggregate/theme/nursing-homes"
PDC_CURRENT_NH = f"{PDC_API}/archive/aggregate/current/theme/nursing-homes"

POLICY_SOURCES = [
    {
        "name": "CMS QSO-22-08-NH Nursing Home Staff Turnover and Weekend Staffing Levels",
        "url": "https://www.cms.gov/files/document/qso-22-08-nh.pdf",
    },
    {
        "name": "CMS Updates to the Care Compare Website July 2022",
        "url": "https://www.cms.gov/newsroom/fact-sheets/updates-care-compare-website-july-2022",
    },
    {
        "name": "CMS Press Release Staffing and Turnover Data Five-Star",
        "url": "https://www.cms.gov/newsroom/press-releases/cms-enhances-nursing-home-rating-system-staffing-turnover-data",
    },
    {
        "name": "HHS OIG 2020 Nursing Home Staffing Transparency",
        "url": "https://oig.hhs.gov/reports/all/2020/some-nursing-homes-reported-staffing-levels-in-2018-raise-concerns-consumer-transparency-could-be-increased/",
    },
    {
        "name": "HHS OIG 2021 CMS Use of Nursing Home Staffing Data",
        "url": "https://oig.hhs.gov/reports/all/2021/cms-use-of-data-on-nursing-home-staffing-progress-and-opportunities-to-do-more/",
    },
    {
        "name": "HHS OIG 2025 CMS Use of Staffing Data for State Oversight",
        "url": "https://oig.hhs.gov/reports/all/2025/cms-use-of-staffing-data-to-inform-state-oversight-of-nursing-homes/",
    },
]

CURRENT_DATASETS = {
    "Provider Information": "4pq5-n9py",
    "Health Deficiencies": "r5ix-sfxw",
    "Survey Summary": "tbry-pc2d",
    "Ownership": "y2hd-n93e",
}


def request_json(url: str) -> dict:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    return response.json()


def safe_name(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip())
    return text.strip("_")[:180]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest: Path, overwrite: bool = False) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not overwrite:
        return {
            "path": str(dest),
            "bytes": dest.stat().st_size,
            "sha256": sha256_file(dest),
            "downloaded": False,
        }
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, timeout=180, stream=True) as r:
        r.raise_for_status()
        with tmp.open("wb") as f:
            shutil.copyfileobj(r.raw, f)
    tmp.replace(dest)
    return {
        "path": str(dest),
        "bytes": dest.stat().st_size,
        "sha256": sha256_file(dest),
        "downloaded": True,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def title_dataset(catalog: dict, title: str) -> dict:
    matches = [d for d in catalog["dataset"] if d.get("title") == title]
    if not matches:
        raise ValueError(f"CMS data.json title not found: {title}")
    return matches[0]


def select_pbj_sources(catalog: dict, title: str, start_year: int, end_year: int) -> list[dict]:
    ds = title_dataset(catalog, title)
    rows = []
    for dist in ds.get("distribution", []):
        if dist.get("mediaType") != "text/csv":
            continue
        temporal = dist.get("temporal", "")
        year = int(temporal[:4]) if re.match(r"^\d{4}", temporal) else None
        if year is None or not (start_year <= year <= end_year):
            continue
        rows.append(
            {
                "source_name": title,
                "title": dist.get("title", ""),
                "temporal": temporal,
                "download_url": dist.get("downloadURL", ""),
                "dataset_identifier_latest": ds.get("identifier", ""),
                "modified": ds.get("modified", ""),
            }
        )
    rows.sort(key=lambda r: r["temporal"])
    return rows


def select_provider_archives(items: list[dict], start_year: int, end_year: int) -> list[dict]:
    snapshots = [x for x in items if x.get("type") == "theme" and x.get("theme") == "nursing-homes"]
    by_year_month: dict[tuple[int, int], dict] = {}
    for item in snapshots:
        d = datetime.strptime(item["date"], "%Y-%m-%d").date()
        if not (start_year <= d.year <= end_year):
            continue
        # Keep quarterly snapshots plus all July 2022 release information.
        if d.month not in {1, 4, 7, 10} and d != date(2022, 7, 27):
            continue
        key = (d.year, d.month)
        # Prefer the latest available snapshot within the month.
        if key not in by_year_month or d > datetime.strptime(by_year_month[key]["date"], "%Y-%m-%d").date():
            by_year_month[key] = item
    selected = list(by_year_month.values())
    selected.sort(key=lambda x: x["date"])
    return selected


def main() -> None:
    for p in [RAW, POLICY, PROVIDER_ARCHIVES, TEMP / "intermediate"]:
        p.mkdir(parents=True, exist_ok=True)

    access_date = date.today().isoformat()
    catalog = request_json(CMS_DATA_JSON)
    catalog_path = RAW / f"cms_data_json_{access_date}.json"
    catalog_path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")

    archive = request_json(PDC_ARCHIVE_NH)
    archive_path = RAW / f"provider_archive_nursing_homes_manifest_{access_date}.json"
    archive_path.write_text(json.dumps(archive, indent=2), encoding="utf-8")

    current_archive = request_json(PDC_CURRENT_NH)
    (RAW / f"provider_current_nursing_homes_manifest_{access_date}.json").write_text(
        json.dumps(current_archive, indent=2), encoding="utf-8"
    )

    pbj_daily = select_pbj_sources(catalog, "Payroll Based Journal Daily Nurse Staffing", 2019, 2025)
    write_csv(TEMP / "pbj_daily_sources.csv", pbj_daily)

    pbj_employee = select_pbj_sources(
        catalog, "Payroll Based Journal Employee Detail Nursing Home Staffing", 2019, 2025
    )
    write_csv(TEMP / "pbj_employee_detail_sources.csv", pbj_employee)

    provider_archives = select_provider_archives(archive["data"], 2019, 2025)
    archive_rows = []
    for item in provider_archives:
        url = item["url"]
        fname = f"nursing_homes_{item['date']}.zip"
        dest = PROVIDER_ARCHIVES / fname
        meta = download_file(url, dest, overwrite=False)
        archive_rows.append(
            {
                "date": item["date"],
                "type": item["type"],
                "theme": item["theme"],
                "url": url,
                "local_path": str(dest.relative_to(ROOT)),
                "size_reported": item.get("size", ""),
                "bytes": meta["bytes"],
                "sha256": meta["sha256"],
            }
        )
        print(f"provider archive {item['date']}: {meta['bytes']} bytes")
    write_csv(TEMP / "provider_archive_selection.csv", archive_rows)

    current_rows = []
    for name, dataset_id in CURRENT_DATASETS.items():
        meta = request_json(f"{PDC_API}/metastore/schemas/dataset/items/{dataset_id}")
        out = RAW / f"provider_data_metadata_{safe_name(name)}_{access_date}.json"
        out.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        current_rows.append(
            {
                "source_name": name,
                "dataset_id": dataset_id,
                "landing_page": meta.get("landingPage", ""),
                "modified": meta.get("modified", ""),
                "released": meta.get("released", ""),
                "download_url": (meta.get("distribution") or [{}])[0].get("downloadURL", ""),
            }
        )
    write_csv(TEMP / "provider_current_sources.csv", current_rows)

    policy_rows = []
    for src in POLICY_SOURCES:
        suffix = ".pdf" if src["url"].lower().endswith(".pdf") else ".html"
        dest = POLICY / f"{safe_name(src['name'])}{suffix}"
        meta = download_file(src["url"], dest, overwrite=False)
        policy_rows.append(
            {
                "source_name": src["name"],
                "official_source": src["url"],
                "download_access_date": access_date,
                "file_period": "",
                "row_count": "",
                "column_count": "",
                "checksum": meta["sha256"],
                "status": f"downloaded to {dest.relative_to(ROOT)}",
            }
        )
    write_csv(TEMP / "policy_source_records.csv", policy_rows)

    inventory = []
    inventory.append(
        {
            "source_name": "CMS data.json catalog",
            "official_source": CMS_DATA_JSON,
            "download_access_date": access_date,
            "file_period": "catalog snapshot",
            "row_count": len(catalog.get("dataset", [])),
            "column_count": "",
            "checksum": sha256_file(catalog_path),
            "status": f"saved {catalog_path.relative_to(ROOT)}",
        }
    )
    inventory.append(
        {
            "source_name": "Provider Data Catalog nursing homes archive manifest",
            "official_source": PDC_ARCHIVE_NH,
            "download_access_date": access_date,
            "file_period": "2019-2026 archive manifest",
            "row_count": len(archive.get("data", [])),
            "column_count": "",
            "checksum": sha256_file(archive_path),
            "status": f"saved {archive_path.relative_to(ROOT)}",
        }
    )
    for row in pbj_daily:
        inventory.append(
            {
                "source_name": row["source_name"],
                "official_source": row["download_url"],
                "download_access_date": access_date,
                "file_period": row["temporal"],
                "row_count": "",
                "column_count": "",
                "checksum": "",
                "status": "official URL recorded; streamed during panel construction",
            }
        )
    for row in archive_rows:
        inventory.append(
            {
                "source_name": "Provider Data Catalog nursing homes archive ZIP",
                "official_source": row["url"],
                "download_access_date": access_date,
                "file_period": row["date"],
                "row_count": "",
                "column_count": "",
                "checksum": row["sha256"],
                "status": f"downloaded {row['local_path']}",
            }
        )
    inventory.extend(policy_rows)
    write_csv(TEMP / "source_inventory.csv", inventory)

    with (TEMP / "audit_log.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 1 Source Acquisition\n\n"
            f"- Access date: {access_date}.\n"
            f"- Recorded {len(pbj_daily)} PBJ daily nurse staffing quarterly CSV URLs for 2019-2025.\n"
            f"- Recorded {len(pbj_employee)} PBJ employee-detail quarterly CSV URLs. Full employee-detail processing is deferred unless feasible because the files are much larger than the daily aggregate files.\n"
            f"- Downloaded or verified {len(archive_rows)} Provider Data Catalog nursing-home archive ZIP snapshots.\n"
            "- Downloaded official CMS policy and HHS OIG source snapshots for the policy timeline.\n"
        )

    with (TEMP / "iteration_notes.md").open("a", encoding="utf-8") as f:
        f.write(
            "\n## Phase 1: Source and Policy Audit\n\n"
            "CMS QSO-22-08-NH and CMS's July 27, 2022 fact sheet confirm the two policy shocks: January 2022 public posting of weekend staffing and turnover measures and July 27, 2022 incorporation into Five-Star staffing-domain methodology. PBJ daily nurse staffing is available quarterly through 2025 Q4 in the CMS data catalog. Provider Data Catalog nursing-home archive snapshots are available back to 2019 and were selected quarterly to support rating and facility-characteristic outcomes.\n\n"
            "Self-question: The policy exposure is correctly defined as the 2022 transparency/rating sequence. The 2024 minimum staffing rule remains later context, not the main exposure.\n"
        )

    print("Source acquisition complete.")


if __name__ == "__main__":
    main()
