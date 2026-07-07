from __future__ import annotations

import re
import time
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

from project_utils import (
    RAW,
    SNAP,
    append_audit,
    append_source,
    browser_headers,
    ensure_dirs,
    parse_month_label,
    rel,
    save_csv,
    sha256_file,
    today_iso,
)


STATE_REPORTS_URL = "https://988lifeline.org/professionals/our-network/state-based-monthly-reports/"
SAMHSA_METRICS_URL = "https://www.samhsa.gov/mental-health/988/performance-metrics"
SAMHSA_TIMELINE_URL = "https://www.samhsa.gov/mental-health/988/lifeline-timeline"
FCC_REPORTING_URL = "https://www.fcc.gov/988-fee-reports-and-reporting"
FCC_ANNUAL_REPORTS = [
    {
        "source_id": "fcc_fee_report_2021",
        "name": "First Annual 988 Fee Accountability Report",
        "url": "https://docs.fcc.gov/public/attachments/DOC-388659A1.pdf",
        "publication_date": "2022-10-14",
        "coverage_start": "2021-01-01",
        "coverage_end": "2021-12-31",
        "filename": "2021_first_annual_988_fee_accountability_report.pdf",
    },
    {
        "source_id": "fcc_fee_report_2022",
        "name": "Second Annual 988 Fee Accountability Report",
        "url": "https://docs.fcc.gov/public/attachments/DOC-398971A1.pdf",
        "publication_date": "2023-10-17",
        "coverage_start": "2022-01-01",
        "coverage_end": "2022-12-31",
        "filename": "2022_second_annual_988_fee_accountability_report.pdf",
    },
    {
        "source_id": "fcc_fee_report_2023",
        "name": "Third Annual 988 Fee Accountability Report",
        "url": "https://docs.fcc.gov/public/attachments/DOC-406726A1.pdf",
        "publication_date": "2024-10-17",
        "coverage_start": "2023-01-01",
        "coverage_end": "2023-12-31",
        "filename": "2023_third_annual_988_fee_accountability_report.pdf",
    },
    {
        "source_id": "fcc_fee_report_2024",
        "name": "Fourth Annual 988 Fee Accountability Report",
        "url": "https://docs.fcc.gov/public/attachments/DOC-415434A1.pdf",
        "publication_date": "2025-11-19",
        "coverage_start": "2024-01-01",
        "coverage_end": "2024-12-31",
        "filename": "2024_fourth_annual_988_fee_accountability_report.pdf",
    },
]

CENSUS_POP_URL = (
    "https://www2.census.gov/programs-surveys/popest/tables/2020-2025/"
    "state/totals/NST-EST2025-POP.xlsx"
)
NSUMHSS_DATAFILES_URL = (
    "https://www.samhsa.gov/data/data-we-collect/"
    "n-sumhss-national-substance-use-and-mental-health-services-survey/datafiles"
)

STATE_POLICY_SOURCES = [
    ("ca_cdtfa_988_surcharge_rates", "California CDTFA 911 Surcharge, 988 Surcharge, and Local Charge Rates", "https://cdtfa.ca.gov/taxes-and-fees/mts.htm"),
    ("co_session_law_988_surcharge", "Colorado General Assembly Session Law Creating 988 Surcharge", "https://leg.colorado.gov/laws/session-laws/465/download"),
    ("wa_dor_988_tax", "Washington Department of Revenue 988 tax page", "https://dor.wa.gov/taxes-rates/other-taxes/statewide-988-behavioral-health-crisis-response-suicide-prevention-line-tax"),
    ("wa_rcw_82_86", "Washington RCW Chapter 82.86", "https://app.leg.wa.gov/RCW/default.aspx?cite=82.86&full=true"),
    ("de_hb160", "Delaware HB 160 bill detail", "https://legis.delaware.gov/BillDetail/140522"),
    ("md_sb974", "Maryland SB 974 legislation detail", "https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0974?ys=2024RS"),
    ("md_sb974_chapter_pdf", "Maryland SB 974 Chapter 781 PDF", "https://mgaleg.maryland.gov/2024rs/Chapters_noln/CH_781_sb0974t.pdf"),
    ("mn_statute_145_561", "Minnesota Statute 145.561 988 suicide and crisis lifeline", "https://www.revisor.mn.gov/statutes/cite/145.561"),
    ("or_hb2757", "Oregon HB 2757 measure document", "https://olis.oregonlegislature.gov/liz/2023r1/Downloads/MeasureDocument/HB2757/B-Engrossed"),
    ("nv_988_temp_regulation", "Nevada 988 Surcharge Temporary Regulation", "https://www.leg.state.nv.us/Register/2023TempRegister/T004-23A.pdf"),
]


def get(url: str, attempts: int = 4) -> requests.Response:
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, headers=browser_headers(), timeout=60)
            if r.status_code == 429 and attempt < attempts:
                time.sleep(15 * attempt)
                continue
            r.raise_for_status()
            return r
        except Exception as exc:
            last_exc = exc
            if attempt < attempts:
                time.sleep(5 * attempt)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"Download failed for {url}")


def save_response(url: str, path, source_id: str, source_name: str, source_type: str, file_format: str,
                  official_or_secondary: str = "official", publication_date: str = "",
                  coverage_start: str = "", coverage_end: str = "", unit: str = "",
                  geography: str = "", notes: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        status = "cached_existing"
    else:
        r = get(url)
        path.write_bytes(r.content)
        status = "downloaded"
    append_source(
        {
            "source_id": source_id,
            "source_name": source_name,
            "source_type": source_type,
            "official_or_secondary": official_or_secondary,
            "url_or_access_path": url,
            "download_date": today_iso(),
            "publication_date": publication_date,
            "coverage_start": coverage_start,
            "coverage_end": coverage_end,
            "unit": unit,
            "geography": geography,
            "file_format": file_format,
            "raw_file_path": rel(path),
            "checksum": sha256_file(path),
            "status": status,
            "notes": notes,
            "citation_text": source_name,
        }
    )


def scrape_monthly_links() -> pd.DataFrame:
    html = get(STATE_REPORTS_URL).text
    snapshot = SNAP / "988_state_based_monthly_reports.html"
    snapshot.write_text(html, encoding="utf-8")
    append_source(
        {
            "source_id": "988_state_reports_index",
            "source_name": "988 Lifeline State-based Monthly Reports index",
            "source_type": "webpage",
            "official_or_secondary": "official",
            "url_or_access_path": STATE_REPORTS_URL,
            "download_date": today_iso(),
            "coverage_start": "2021-07-01",
            "coverage_end": "2026-05-01",
            "unit": "monthly PDF link",
            "geography": "state and territory",
            "file_format": "html",
            "raw_file_path": rel(snapshot),
            "checksum": sha256_file(snapshot),
            "status": "snapshot_downloaded",
            "notes": "Index lists state-based monthly report PDFs.",
            "citation_text": "988 Lifeline, State-based Monthly Reports.",
        }
    )
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    seen = set()
    for a in soup.find_all("a"):
        label = " ".join(a.get_text(" ", strip=True).split())
        href = a.get("href") or ""
        if not re.search(r"\b(2021|2022|2023|2024|2025|2026)\b", label):
            continue
        if not href.lower().endswith(".pdf"):
            continue
        try:
            month = parse_month_label(label)
        except ValueError:
            continue
        key = (month.strftime("%Y-%m"), href)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"year_month": month.strftime("%Y-%m"), "month": month, "label": label, "url": href})
    df = pd.DataFrame(rows).sort_values("month")
    save_csv(df, SNAP / "988_monthly_pdf_links.csv")
    return df


def download_monthly_pdfs(links: pd.DataFrame) -> None:
    outdir = RAW / "988_state_monthly_reports"
    for row in links.itertuples(index=False):
        path = outdir / f"{row.year_month}_988_in_state_monthly_report.pdf"
        if not path.exists():
            period = pd.Period(row.year_month, freq="M")
            try:
                save_response(
                    row.url,
                    path,
                    source_id=f"988_kpi_pdf_{row.year_month}",
                    source_name=f"988 Lifeline In-State KPI Monthly Report {row.label}",
                    source_type="state-month KPI PDF",
                    file_format="pdf",
                    coverage_start=str(period.start_time.date()),
                    coverage_end=str(period.end_time.date()),
                    unit="state-month",
                    geography="state and territory",
                    notes="Downloaded from official 988 Lifeline state-based monthly reports index.",
                )
                time.sleep(2)
            except Exception as exc:
                append_source(
                    {
                        "source_id": f"988_kpi_pdf_{row.year_month}",
                        "source_name": f"988 Lifeline In-State KPI Monthly Report {row.label}",
                        "source_type": "state-month KPI PDF",
                        "official_or_secondary": "official",
                        "url_or_access_path": row.url,
                        "download_date": today_iso(),
                        "coverage_start": str(period.start_time.date()),
                        "coverage_end": str(period.end_time.date()),
                        "unit": "state-month",
                        "geography": "state and territory",
                        "file_format": "pdf",
                        "status": "download_failed",
                        "notes": str(exc),
                        "citation_text": f"988 Lifeline In-State KPI Monthly Report {row.label}",
                    }
                )


def download_static_sources() -> None:
    html_sources = [
        ("samhsa_988_performance_metrics", "SAMHSA 988 Lifeline Performance Metrics", SAMHSA_METRICS_URL, "performance metrics definitions and national dashboard"),
        ("samhsa_988_timeline", "SAMHSA 988 Lifeline Timeline", SAMHSA_TIMELINE_URL, "policy timeline and routing milestones"),
        ("fcc_988_fee_reporting_page", "FCC 988 Fee Reports and Reporting", FCC_REPORTING_URL, "annual fee reporting portal"),
        ("samhsa_nsumhss_datafiles_page", "SAMHSA N-SUMHSS data files page", NSUMHSS_DATAFILES_URL, "mechanism data discovery; public-use files are large and optional"),
    ]
    for source_id, name, url, notes in html_sources:
        if source_id == "fcc_988_fee_reporting_page":
            append_source(
                {
                    "source_id": source_id,
                    "source_name": name,
                    "source_type": "webpage",
                    "official_or_secondary": "official",
                    "url_or_access_path": url,
                    "download_date": today_iso(),
                    "file_format": "html",
                    "status": "skipped_direct_fcc_pdfs_used",
                    "notes": "Portal snapshot is optional; direct official FCC annual report PDFs are downloaded separately.",
                    "citation_text": name,
                }
            )
            continue
        try:
            save_response(url, SNAP / f"{source_id}.html", source_id, name, "webpage", "html", notes=notes)
        except Exception as exc:
            append_source(
                {
                    "source_id": source_id,
                    "source_name": name,
                    "source_type": "webpage",
                    "official_or_secondary": "official",
                    "url_or_access_path": url,
                    "download_date": today_iso(),
                    "file_format": "html",
                    "status": "download_failed",
                    "notes": str(exc),
                    "citation_text": name,
                }
            )

    fcc_rows = []
    for item in FCC_ANNUAL_REPORTS:
        path = RAW / "fcc_988_fee_reports" / item["filename"]
        try:
            save_response(
                item["url"],
                path,
                item["source_id"],
                item["name"],
                "annual fee accountability report",
                "pdf",
                publication_date=item["publication_date"],
                coverage_start=item["coverage_start"],
                coverage_end=item["coverage_end"],
                unit="jurisdiction-year",
                geography="state, territory, tribal",
                notes="FCC annual 988 fee accountability report.",
            )
        except Exception as exc:
            append_source(
                {
                    "source_id": item["source_id"],
                    "source_name": item["name"],
                    "source_type": "annual fee accountability report",
                    "official_or_secondary": "official",
                    "url_or_access_path": item["url"],
                    "download_date": today_iso(),
                    "publication_date": item["publication_date"],
                    "coverage_start": item["coverage_start"],
                    "coverage_end": item["coverage_end"],
                    "unit": "jurisdiction-year",
                    "geography": "state, territory, tribal",
                    "file_format": "pdf",
                    "status": "download_failed",
                    "notes": str(exc),
                    "citation_text": item["name"],
                }
            )
        fcc_rows.append(item)
    save_csv(pd.DataFrame(fcc_rows), SNAP / "fcc_annual_reports.csv")

    try:
        save_response(
            CENSUS_POP_URL,
            RAW / "census" / "NST-EST2025-POP.xlsx",
            "census_nst_est2025_pop",
            "Census annual state resident population estimates 2020-2025",
            "population estimates",
            "xlsx",
            official_or_secondary="official",
            publication_date="2026-01",
            coverage_start="2020-04-01",
            coverage_end="2025-07-01",
            unit="state-year",
            geography="state, DC, Puerto Rico",
            notes="Used for routed contacts per 100,000 and revenue per capita denominators.",
        )
    except Exception as exc:
        append_source(
            {
                "source_id": "census_nst_est2025_pop",
                "source_name": "Census annual state resident population estimates 2020-2025",
                "source_type": "population estimates",
                "official_or_secondary": "official",
                "url_or_access_path": CENSUS_POP_URL,
                "download_date": today_iso(),
                "publication_date": "2026-01",
                "coverage_start": "2020-04-01",
                "coverage_end": "2025-07-01",
                "unit": "state-year",
                "geography": "state, DC, Puerto Rico",
                "file_format": "xlsx",
                "status": "download_failed",
                "notes": str(exc),
                "citation_text": "Census annual state resident population estimates 2020-2025",
            }
        )

    for source_id, name, url in STATE_POLICY_SOURCES:
        parsed = urlparse(url)
        suffix = ".pdf" if parsed.path.lower().endswith(".pdf") or "MeasureDocument" in url or "session-laws" in url else ".html"
        fmt = "pdf" if suffix == ".pdf" else "html"
        safe = re.sub(r"[^A-Za-z0-9_]+", "_", source_id)
        path = RAW / "state_policy_sources" / f"{safe}{suffix}"
        try:
            save_response(
                url,
                path,
                source_id,
                name,
                "state policy source",
                fmt,
                geography="state",
                notes="Official state/statutory source used to cross-check fee timing.",
            )
        except Exception as exc:
            append_source(
                {
                    "source_id": source_id,
                    "source_name": name,
                    "source_type": "state policy source",
                    "official_or_secondary": "official",
                    "url_or_access_path": url,
                    "download_date": today_iso(),
                    "file_format": fmt,
                    "status": "download_failed",
                    "notes": str(exc),
                    "citation_text": name,
                }
            )


def main() -> None:
    ensure_dirs()
    links = scrape_monthly_links()
    download_monthly_pdfs(links)
    download_static_sources()
    append_audit(f"Acquired official sources: {len(links)} monthly KPI PDFs plus FCC/Census/policy snapshots.")


if __name__ == "__main__":
    main()
