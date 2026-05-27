#!/usr/bin/env python
"""Download official ACA Marketplace data files and write a manifest.

This script intentionally keeps source discovery transparent. It scrapes CMS
OEP pages for the required OEP file links, uses the official CMS Exchange PUF
download pattern, and uses Data.HealthCare.gov QHP Landscape direct URLs where
they exist. Missing QHP Landscape direct URLs for PY2019-PY2021 are kept in the
manifest as failed checks, with CMS Health Plan Finder data added as the
official fallback for pre-PY2022 landscape-style data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
MANIFEST_PATH = ROOT / "data" / "metadata" / "data_manifest.csv"

CMS_BASE = "https://www.cms.gov"
OEP_NEW_BASE = (
    "https://www.cms.gov/data-research/statistics-trends-reports/"
    "marketplace-products/{year}-marketplace-open-enrollment-period-public-use-files"
)
OEP_OLD_BASE = (
    "https://www.cms.gov/data-research/statistics-trends-and-reports/"
    "marketplace-products/{year}-marketplace-open-enrollment-period-public-use-files"
)
EXCHANGE_SOURCE_PAGE = "https://www.cms.gov/marketplace/resources/data/public-use-files"
QHP_SOURCE_PAGE = "https://data.healthcare.gov/qhp-landscape-files"
PLAN_FINDER_SOURCE_PAGE = (
    "https://www.cms.gov/marketplace/resources/data/healthcaregov-plan-finder-data"
)


MANIFEST_COLUMNS = [
    "source_group",
    "year",
    "file_type",
    "source_page_url",
    "direct_download_url",
    "local_path",
    "file_format",
    "http_status",
    "download_success",
    "file_size_bytes",
    "checksum_sha256",
    "date_downloaded",
    "notes",
]


@dataclass
class DownloadEntry:
    source_group: str
    year: int | str
    file_type: str
    source_page_url: str
    direct_download_url: str
    notes: str = ""


def ensure_dirs() -> None:
    for path in [
        ROOT / "data" / "raw",
        ROOT / "data" / "intermediate",
        ROOT / "data" / "metadata",
        ROOT / "scripts",
        ROOT / "outputs",
        ROOT / "outputs" / "sample_rows",
        ROOT / "docs",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def file_format_from_url(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower().lstrip(".")
    return suffix or "unknown"


def filename_from_url(url: str) -> str:
    name = Path(unquote(urlparse(url).path)).name
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", name) or "downloaded_file"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_oep_link(text: str, href: str) -> str | None:
    combined = f"{text} {href}".lower()
    if "oep" not in combined and "public-use-files" not in combined:
        return None
    if "zip code" in combined or "snapshot" in combined or "plan design" in combined:
        return None
    if "state, metal level" in combined or "state-metal-level" in combined:
        return "State, Metal Level, and Enrollment Status OEP PUF"
    if "county-level" in combined or "county level" in combined:
        return "County-Level OEP PUF"
    if "state-level" in combined or "state level" in combined:
        if "metal" not in combined:
            return "State-Level OEP PUF"
    if "definitions" in combined and href.lower().endswith(".pdf"):
        return "Public Use Files Definitions PDF"
    if "faq" in combined and href.lower().endswith(".pdf"):
        return "Public Use Files FAQs PDF"
    return None


def discover_oep_entries(years: Iterable[int]) -> list[DownloadEntry]:
    entries: list[DownloadEntry] = []
    session = requests.Session()
    for year in years:
        page_url = (OEP_OLD_BASE if year <= 2020 else OEP_NEW_BASE).format(year=year)
        try:
            response = session.get(page_url, timeout=60)
            page_status = response.status_code
        except requests.RequestException as exc:
            entries.append(
                DownloadEntry(
                    "oep_puf",
                    year,
                    "OEP source page unavailable",
                    page_url,
                    page_url,
                    f"Page request failed: {exc}",
                )
            )
            continue
        if page_status >= 400:
            entries.append(
                DownloadEntry(
                    "oep_puf",
                    year,
                    "OEP source page unavailable",
                    page_url,
                    page_url,
                    f"Page returned HTTP {page_status}",
                )
            )
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        seen: set[tuple[str, str]] = set()
        for link in soup.find_all("a", href=True):
            href = link.get("href", "").strip()
            text = link.get_text(" ", strip=True)
            file_type = classify_oep_link(text, href)
            if not file_type:
                continue
            download_url = urljoin(CMS_BASE, href)
            key = (file_type, download_url)
            if key in seen:
                continue
            seen.add(key)
            entries.append(
                DownloadEntry(
                    "oep_puf",
                    year,
                    file_type,
                    page_url,
                    download_url,
                    "Discovered from official CMS OEP PUF page.",
                )
            )
    return entries


def discover_exchange_entries(years: Iterable[int]) -> list[DownloadEntry]:
    file_types = {
        "rate-puf": "Rate PUF",
        "plan-attributes-puf": "Plan Attributes PUF",
        "service-area-puf": "Service Area PUF",
        "plan-id-crosswalk-puf": "Plan ID Crosswalk PUF",
    }
    entries: list[DownloadEntry] = []
    for year in years:
        for slug, label in file_types.items():
            entries.append(
                DownloadEntry(
                    "exchange_puf",
                    year,
                    label,
                    EXCHANGE_SOURCE_PAGE,
                    f"https://download.cms.gov/marketplace-puf/{year}/{slug}.zip",
                    "Official CMS Exchange PUF direct URL pattern.",
                )
            )

    dictionaries = {
        "rate-datadictionary": "Rate Data Dictionary PDF",
        "planattributes-datadictionary": "Plan Attributes Data Dictionary PDF",
        "servicearea-datadictionary": "Service Area Data Dictionary PDF",
        "plan-id-crosswalk-datadictionary": "Plan ID Crosswalk Data Dictionary PDF",
    }
    for year in range(2021, 2027):
        yy = str(year)[-2:]
        for slug, label in dictionaries.items():
            entries.append(
                DownloadEntry(
                    "exchange_puf",
                    year,
                    label,
                    EXCHANGE_SOURCE_PAGE,
                    f"https://www.cms.gov/files/document/{slug}-py{yy}.pdf",
                    "Official CMS Exchange PUF data dictionary URL pattern. Some older dictionaries may be unavailable.",
                )
            )
    return entries


def discover_qhp_entries() -> list[DownloadEntry]:
    entries: list[DownloadEntry] = []
    for year in range(2019, 2027):
        entries.append(
            DownloadEntry(
                "qhp_landscape",
                year,
                "QHP Landscape Individual Medical ZIP",
                QHP_SOURCE_PAGE,
                f"https://data.healthcare.gov/datafile/py{year}/individual_market_medical.zip",
                "Official Data.HealthCare.gov QHP Landscape direct URL pattern; expected to fail before PY2022.",
            )
        )
        entries.append(
            DownloadEntry(
                "qhp_landscape",
                year,
                "QHP Landscape Individual Medical Instructions PDF",
                QHP_SOURCE_PAGE,
                f"https://data.healthcare.gov/datafile/py{year}/med-ind-lndscp-in.pdf",
                "Official Data.HealthCare.gov QHP Landscape instructions; expected to fail before PY2022.",
            )
        )

    fallback = [
        (
            2019,
            "Health Plan Finder Q4 HIOS Data",
            "https://www.cms.gov/files/document/2019q4-hios.xlsx",
        ),
        (2019, "Health Plan Finder Q4 RBIS Data", "https://www.cms.gov/files/zip/2019q4.zip"),
        (
            2020,
            "Health Plan Finder Q4 HIOS Data",
            "https://www.cms.gov/files/document/2020q4-hios.xlsx",
        ),
        (
            2020,
            "Health Plan Finder Q4 RBIS Data",
            "https://www.cms.gov/files/zip/2020q4-rbis.zip",
        ),
        (
            2021,
            "Health Plan Finder Q4 HIOS/RBIS Data",
            "https://downloads.cms.gov/files/2021q4-hios-rbis.zip",
        ),
        (
            "metadata",
            "Health Plan Finder Interface Control Document PDF",
            "https://www.cms.gov/cciio/resources/data-resources/downloads/hios-rbis-icd-03-01-00.pdf",
        ),
        (
            "metadata",
            "Health Plan Finder Metadata Report XLSX",
            "https://www.cms.gov/cciio/resources/data-resources/downloads/metadata-report-for-puf.xlsx",
        ),
    ]
    for year, file_type, url in fallback:
        entries.append(
            DownloadEntry(
                "health_plan_finder",
                year,
                file_type,
                PLAN_FINDER_SOURCE_PAGE,
                url,
                "Official CMS Health Plan Finder fallback for years without Data.HealthCare.gov QHP Landscape ZIPs.",
            )
        )
    return entries


def local_path_for(entry: DownloadEntry) -> Path:
    source = re.sub(r"[^A-Za-z0-9._-]+", "_", str(entry.source_group))
    year = re.sub(r"[^A-Za-z0-9._-]+", "_", str(entry.year))
    directory = RAW_DIR / source / year
    directory.mkdir(parents=True, exist_ok=True)
    return directory / filename_from_url(entry.direct_download_url)


def download_one(entry: DownloadEntry, force: bool = False) -> dict[str, str | int | bool]:
    local_path = local_path_for(entry)
    file_format = file_format_from_url(entry.direct_download_url)
    date_downloaded = datetime.now(timezone.utc).isoformat(timespec="seconds")
    status: int | str = ""
    success = False
    notes = entry.notes
    final_url = ""

    if local_path.exists() and local_path.stat().st_size > 0 and not force:
        try:
            response = requests.head(entry.direct_download_url, timeout=30, allow_redirects=True)
            status = response.status_code
            final_url = response.url
        except requests.RequestException as exc:
            status = ""
            notes = f"{notes} Existing file retained; HEAD failed: {exc}"
        success = True
    else:
        try:
            with requests.get(
                entry.direct_download_url,
                stream=True,
                timeout=(15, 120),
                allow_redirects=True,
            ) as response:
                status = response.status_code
                final_url = response.url
                if response.status_code >= 400:
                    success = False
                    notes = f"{notes} Download failed with HTTP {response.status_code}."
                    if local_path.exists() and local_path.stat().st_size == 0:
                        local_path.unlink()
                else:
                    with local_path.open("wb") as handle:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                handle.write(chunk)
                    success = local_path.exists() and local_path.stat().st_size > 0
        except requests.RequestException as exc:
            success = False
            notes = f"{notes} Download exception: {exc}"

    file_size = local_path.stat().st_size if success and local_path.exists() else ""
    checksum = sha256_file(local_path) if success and local_path.exists() else ""
    if final_url and final_url != entry.direct_download_url:
        notes = f"{notes} Final URL: {final_url}"

    row = asdict(entry)
    row.update(
        {
            "local_path": str(local_path.relative_to(ROOT)) if success else "",
            "file_format": file_format,
            "http_status": status,
            "download_success": success,
            "file_size_bytes": file_size,
            "checksum_sha256": checksum,
            "date_downloaded": date_downloaded,
            "notes": notes,
        }
    )
    return row


def write_manifest(rows: list[dict[str, str | int | bool]]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in MANIFEST_COLUMNS})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Re-download files that already exist.")
    parser.add_argument(
        "--groups",
        nargs="*",
        default=["oep_puf", "exchange_puf", "qhp_landscape", "health_plan_finder"],
        help="Source groups to download.",
    )
    args = parser.parse_args()

    ensure_dirs()
    entries: list[DownloadEntry] = []
    groups = set(args.groups)
    if "oep_puf" in groups:
        entries.extend(discover_oep_entries(range(2019, 2027)))
    if "exchange_puf" in groups:
        entries.extend(discover_exchange_entries(range(2019, 2027)))
    if "qhp_landscape" in groups or "health_plan_finder" in groups:
        qhp_entries = discover_qhp_entries()
        entries.extend([e for e in qhp_entries if e.source_group in groups])

    rows = []
    for i, entry in enumerate(entries, start=1):
        print(f"[{i}/{len(entries)}] {entry.source_group} {entry.year} {entry.file_type}")
        rows.append(download_one(entry, force=args.force))
    write_manifest(rows)
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)} with {len(rows)} rows.")


if __name__ == "__main__":
    main()
