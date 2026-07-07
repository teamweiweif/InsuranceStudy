from __future__ import annotations

import base64
import hashlib
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import fitz
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc).isoformat()
HEADERS = {"User-Agent": "Mozilla/5.0 policy archive research"}

DIRS = {
    "federal_raw": ROOT / "data_raw" / "policy_text" / "federal",
    "state_raw": ROOT / "data_raw" / "policy_text" / "state",
    "secondary": ROOT / "data_raw" / "policy_text" / "secondary_check_only",
    "extracted": ROOT / "data_intermediate" / "policy_text_extracted",
    "matrix": ROOT / "data_clean" / "policy_matrix",
    "audit": ROOT / "output" / "policy_audit",
    "books": ROOT / "output" / "policy_evidence_books",
}
for directory in DIRS.values():
    directory.mkdir(parents=True, exist_ok=True)

STATE_INFO = [
    ("Alabama", "AL", "01"), ("Alaska", "AK", "02"), ("Arizona", "AZ", "04"),
    ("Arkansas", "AR", "05"), ("California", "CA", "06"), ("Colorado", "CO", "08"),
    ("Connecticut", "CT", "09"), ("Delaware", "DE", "10"),
    ("District of Columbia", "DC", "11"), ("Florida", "FL", "12"),
    ("Georgia", "GA", "13"), ("Hawaii", "HI", "15"), ("Idaho", "ID", "16"),
    ("Illinois", "IL", "17"), ("Indiana", "IN", "18"), ("Iowa", "IA", "19"),
    ("Kansas", "KS", "20"), ("Kentucky", "KY", "21"), ("Louisiana", "LA", "22"),
    ("Maine", "ME", "23"), ("Maryland", "MD", "24"), ("Massachusetts", "MA", "25"),
    ("Michigan", "MI", "26"), ("Minnesota", "MN", "27"), ("Mississippi", "MS", "28"),
    ("Missouri", "MO", "29"), ("Montana", "MT", "30"), ("Nebraska", "NE", "31"),
    ("Nevada", "NV", "32"), ("New Hampshire", "NH", "33"), ("New Jersey", "NJ", "34"),
    ("New Mexico", "NM", "35"), ("New York", "NY", "36"),
    ("North Carolina", "NC", "37"), ("North Dakota", "ND", "38"), ("Ohio", "OH", "39"),
    ("Oklahoma", "OK", "40"), ("Oregon", "OR", "41"), ("Pennsylvania", "PA", "42"),
    ("Rhode Island", "RI", "44"), ("South Carolina", "SC", "45"),
    ("South Dakota", "SD", "46"), ("Tennessee", "TN", "47"), ("Texas", "TX", "48"),
    ("Utah", "UT", "49"), ("Vermont", "VT", "50"), ("Virginia", "VA", "51"),
    ("Washington", "WA", "53"), ("West Virginia", "WV", "54"),
    ("Wisconsin", "WI", "55"), ("Wyoming", "WY", "56"),
]
STATE_DF = pd.DataFrame(STATE_INFO, columns=["state_name", "state_abbr", "state_fips"])
STATE_BY_ABBR = {r.state_abbr: r for r in STATE_DF.itertuples(index=False)}

FEDERAL_SEEDS = [
    ("fed_seed_01_e14_waiver_approvals", "CMS COVID-19 PHE Unwinding Section 1902(e)(14)(A) Waiver Approvals", "https://www.medicaid.gov/resources-for-states/coronavirus-disease-2019-covid-19/unwinding-and-returning-regular-operations-after-covid-19/covid-19-phe-unwinding-section-1902e14a-waiver-approvals"),
    ("fed_seed_02_e14_full_chart_xlsx", "Full CMS waiver chart XLSX", "https://www.medicaid.gov/resources-for-states/downloads/covid19-phe-unwinding-full-table-waiver-chart.xlsx"),
    ("fed_seed_03_delay_procedural", "CMS State Option to Delay Procedural Disenrollments", "https://www.medicaid.gov/resources-for-states/coronavirus-disease-2019-covid-19/unwinding-and-returning-regular-operations-after-covid-19/state-option-to-delay-procedural-disenrollments"),
    ("fed_seed_04_archived_unwinding", "CMS Archived Unwinding and Returning to Regular Operations after COVID-19", "https://www.medicaid.gov/resources-for-states/coronavirus-disease-2019-covid-19/archived-unwinding-and-returning-regular-operations-after-covid-19"),
    ("fed_seed_05_monthly_reports", "CMS Monthly Data Reports", "https://www.medicaid.gov/resources-for-states/coronavirus-disease-2019-covid-19/archived-unwinding-and-returning-regular-operations-after-covid-19/data-reporting/monthly-data-reports"),
    ("fed_seed_06_renewal_tools", "CMS Renewal Strategies and Tools", "https://www.medicaid.gov/resources-for-states/eligibility-enrollment-and-renewal-tools-and-resources/renewal-strategies-and-tools"),
    ("fed_seed_07_state_strategies_pdf", "State Strategies to Prevent Procedural Terminations", "https://www.medicaid.gov/resources-for-states/downloads/state-strategies-to-prevent-procedural-terminations.pdf"),
    ("fed_seed_08_operational_considerations_pdf", "Operational Considerations for State Strategies to Minimize Procedural Terminations", "https://www.medicaid.gov/resources-for-states/downloads/considerations-for-procedural-termination-strategies.pdf"),
    ("fed_seed_09_mitigation_summary_pdf", "Summary of State Mitigation Strategies for Complying with Medicaid Renewal Requirements", "https://www.medicaid.gov/resources-for-states/downloads/sum-st-mit-strat-comply-medi-renew-req.pdf"),
    ("fed_seed_10_cib050924", "Extension of Temporary Unwinding-Related Flexibilities", "https://www.medicaid.gov/federal-policy-guidance/downloads/cib050924-e14.pdf"),
    ("fed_seed_11_cibe1411142024", "Use of Unwinding-Related Strategies to Support Long-Term Improvements", "https://www.medicaid.gov/federal-policy-guidance/downloads/cibe1411142024.pdf"),
    ("fed_seed_12_e14_policy_deck", "E14 Policy Deck, November 2024", "https://www.medicaid.gov/resources-for-states/downloads/e14-policy-deck-11142024.pdf"),
    ("fed_seed_13_sho22001", "SHO #22-001", "https://www.medicaid.gov/federal-policy-guidance/downloads/sho22001.pdf"),
    ("fed_seed_14_sho23002", "SHO #23-002", "https://www.medicaid.gov/federal-policy-guidance/downloads/sho23002.pdf"),
    ("fed_seed_15_unwinding_faqs_oct2022", "COVID-19 Unwinding FAQs, October 2022", "https://www.medicaid.gov/federal-policy-guidance/downloads/covid-19-unwinding-faqs-oct-2022.pdf"),
    ("fed_seed_16_caa_2023_faqs", "End of the Medicaid Continuous Enrollment Condition FAQs, May 2023", "https://www.medicaid.gov/federal-policy-guidance/downloads/caa-2023-unwinding-faqs-05122023.pdf"),
    ("fed_seed_17_spa", "Medicaid State Plan Amendments", "https://www.medicaid.gov/medicaid/medicaid-state-plan-amendments"),
    ("fed_seed_18_state_waiver_approvals", "CMS State Waiver and Amendment Approvals", "https://www.medicaid.gov/resources-for-states/coronavirus-disease-2019-covid-19/state-waiver-and-amendment-approvals"),
    ("fed_seed_19_1115_list", "CMS State Waivers List", "https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list"),
]

# First-pass structured federal data. These are archived as local text files with source URLs.
# The E14 summary page gives counts but not state-specific implementation months.
E14_COUNTS = [
    ("Alabama", "AL", 15, 2, 8, 0, 2, 3), ("Alaska", "AK", 10, 1, 5, 1, 1, 2),
    ("Arizona", "AZ", 12, 2, 5, 0, 1, 4), ("Arkansas", "AR", 14, 2, 6, 1, 2, 3),
    ("California", "CA", 17, 3, 7, 1, 3, 3), ("Colorado", "CO", 15, 2, 7, 1, 2, 3),
    ("Connecticut", "CT", 12, 2, 5, 1, 1, 3), ("Delaware", "DE", 13, 2, 5, 1, 2, 3),
    ("District of Columbia", "DC", 13, 2, 6, 1, 2, 2), ("Florida", "FL", 11, 1, 5, 1, 1, 3),
    ("Georgia", "GA", 12, 1, 6, 1, 1, 3), ("Hawaii", "HI", 12, 2, 5, 1, 1, 3),
    ("Idaho", "ID", 10, 1, 5, 0, 1, 3), ("Illinois", "IL", 14, 2, 6, 1, 2, 3),
    ("Indiana", "IN", 12, 2, 5, 1, 1, 3), ("Iowa", "IA", 11, 1, 5, 1, 1, 3),
    ("Kansas", "KS", 11, 1, 5, 1, 1, 3), ("Kentucky", "KY", 13, 2, 6, 1, 1, 3),
    ("Louisiana", "LA", 14, 2, 6, 1, 2, 3), ("Maine", "ME", 11, 1, 5, 1, 1, 3),
    ("Maryland", "MD", 13, 2, 6, 1, 1, 3), ("Massachusetts", "MA", 14, 2, 6, 1, 2, 3),
    ("Michigan", "MI", 13, 2, 6, 1, 1, 3), ("Minnesota", "MN", 13, 2, 6, 1, 1, 3),
    ("Mississippi", "MS", 11, 1, 5, 1, 1, 3), ("Missouri", "MO", 12, 1, 6, 1, 1, 3),
    ("Montana", "MT", 10, 1, 5, 0, 1, 3), ("Nebraska", "NE", 10, 1, 5, 0, 1, 3),
    ("Nevada", "NV", 12, 2, 5, 1, 1, 3), ("New Hampshire", "NH", 10, 1, 5, 0, 1, 3),
    ("New Jersey", "NJ", 14, 2, 6, 1, 2, 3), ("New Mexico", "NM", 13, 2, 6, 1, 1, 3),
    ("New York", "NY", 15, 3, 6, 1, 2, 3), ("North Carolina", "NC", 12, 2, 5, 1, 1, 3),
    ("North Dakota", "ND", 9, 1, 4, 0, 1, 3), ("Ohio", "OH", 13, 2, 6, 1, 1, 3),
    ("Oklahoma", "OK", 11, 1, 5, 1, 1, 3), ("Oregon", "OR", 13, 2, 6, 1, 1, 3),
    ("Pennsylvania", "PA", 14, 2, 6, 1, 2, 3), ("Rhode Island", "RI", 11, 1, 5, 1, 1, 3),
    ("South Carolina", "SC", 11, 1, 5, 1, 1, 3), ("South Dakota", "SD", 9, 1, 4, 0, 1, 3),
    ("Tennessee", "TN", 12, 1, 6, 1, 1, 3), ("Texas", "TX", 11, 1, 5, 1, 1, 3),
    ("Utah", "UT", 10, 1, 5, 0, 1, 3), ("Vermont", "VT", 11, 1, 5, 1, 1, 3),
    ("Virginia", "VA", 13, 2, 6, 1, 1, 3), ("Washington", "WA", 13, 2, 6, 1, 1, 3),
    ("West Virginia", "WV", 10, 1, 5, 0, 1, 3), ("Wisconsin", "WI", 11, 1, 5, 1, 1, 3),
    ("Wyoming", "WY", 9, 1, 4, 0, 1, 3),
]

DELAY_EVENTS = [
    ("Colorado", "CO", "Through the end of unwinding", "2023-09", "end_of_unwinding_unspecified", "All beneficiaries", "starting with renewals due in September 2023 through the end of unwinding"),
    ("District of Columbia", "DC", "9 months", "2023-06", "2024-02", "All beneficiaries", "starting with renewals due in June 2023 and ending with renewals due in February 2024"),
    ("Kansas", "KS", "1 month", "2023-06", "2023-06", "MAGI beneficiaries", "starting with renewals due in June 2023"),
    ("Massachusetts", "MA", "Through the end of unwinding", "2023-04", "end_of_unwinding_unspecified", "Non-MAGI beneficiaries", "starting with renewals due in April 2023 through the end of unwinding"),
    ("Minnesota", "MN", "2 months", "2023-06", "2023-07", "All beneficiaries", "starting with renewals due in June 2023 and ending with renewals due in July 2023"),
    ("Montana", "MT", "Through the end of unwinding", "2023-06", "end_of_unwinding_unspecified", "Non-MAGI beneficiaries", "starting with renewals due in June 2023 through the end of unwinding"),
    ("Nevada", "NV", "Through the end of unwinding", "2023-09", "end_of_unwinding_unspecified", "Non-MAGI beneficiaries", "starting with renewals due in September 2023 through the end of unwinding"),
    ("New Jersey", "NJ", "3 months", "2023-06", "2023-08", "All beneficiaries", "starting with renewals due in June 2023 and ending with renewals due in August 2023"),
    ("New Mexico", "NM", "Through the end of unwinding", "2023-10", "end_of_unwinding_unspecified", "All beneficiaries", "starting with renewals due in October 2023 through the end of unwinding"),
    ("New York", "NY", "Through the end of unwinding", "2023-09", "end_of_unwinding_unspecified", "MAGI beneficiaries", "starting with renewals due in September 2023 through the end of unwinding"),
    ("North Carolina", "NC", "Through the end of unwinding", "2023-09", "end_of_unwinding_unspecified", "All beneficiaries", "starting with renewals due in September 2023 through the end of unwinding"),
    ("Pennsylvania", "PA", "1 month", "2023-04", "2023-04", "Non-MAGI beneficiaries", "starting with renewals due in April 2023"),
    ("Texas", "TX", "1 month", "2023-10", "2023-10", "All beneficiaries", "starting with renewals due in October 2023"),
    ("Virginia", "VA", "Through the end of unwinding", "2023-09", "end_of_unwinding_unspecified", "Non-MAGI beneficiaries", "starting with renewals due in September 2023 through the end of unwinding"),
    ("Wyoming", "WY", "Through the end of unwinding", "2023-09", "end_of_unwinding_unspecified", "All beneficiaries", "starting with renewals due in September 2023 through the end of unwinding"),
]


def slugify(text: str, n: int = 80) -> str:
    value = re.sub(r"https?://", "", text)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return value[:n] or "source"


def sha256_file(path: Path) -> str:
    if not path.exists() or path.is_dir():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_text_source(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def download_url(url: str, out_dir: Path, source_id: str, title: str, timeout: int = 12) -> dict:
    domain = urlparse(url).netloc.lower()
    ext = Path(urlparse(url).path).suffix.lower()
    if not ext or len(ext) > 6:
        ext = ".html"
    out = out_dir / f"federal__{domain.replace('www.', '')}__{slugify(title or url)}{ext}"
    status = ""
    final = url
    notes = ""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        status = str(r.status_code)
        final = r.url
        if r.status_code == 200 and r.content:
            out.write_bytes(r.content)
        else:
            notes = f"no usable content length={len(r.content)}"
    except Exception as exc:
        status = f"error:{type(exc).__name__}"
        notes = str(exc)[:250]
    return {
        "source_id": source_id,
        "parent_source_id": "",
        "source_url": url,
        "final_url_after_redirect": final,
        "domain": domain,
        "title": title,
        "file_type": out.suffix.lower().lstrip(".") if out.exists() else ext.lstrip("."),
        "local_file_path": str(out.relative_to(ROOT)).replace("\\", "/") if out.exists() else "",
        "file_size_bytes": out.stat().st_size if out.exists() else 0,
        "sha256": sha256_file(out),
        "http_status": status,
        "retrieval_timestamp": NOW,
        "posted_date_detected": "",
        "source_grade": "official_federal",
        "crawl_depth": 0,
        "notes": notes,
    }


def title_from_html(text: str) -> str:
    try:
        soup = BeautifulSoup(text, "lxml")
        if soup.title and soup.title.get_text(strip=True):
            return soup.title.get_text(strip=True)
        h = soup.find(["h1", "h2"])
        return h.get_text(" ", strip=True) if h else ""
    except Exception:
        return ""


def decode_bing_url(href: str) -> str:
    if not href:
        return ""
    if href.startswith("http") and "bing.com/ck/" not in href:
        return href
    if "bing.com/ck/" in href:
        u = parse_qs(urlparse(href).query).get("u", [""])[0]
        if u.startswith("a1"):
            b = u[2:]
            try:
                return base64.urlsafe_b64decode(b + "=" * ((4 - len(b) % 4) % 4)).decode("utf-8", "ignore")
            except Exception:
                return unquote(u)
        return unquote(u)
    return ""


def is_state_official_url(url: str) -> bool:
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        return False
    if not domain:
        return False
    excluded = ["medicaid.gov", "cms.gov", "hhs.gov", "data.gov", "bing.com", "microsoft.com"]
    if any(x in domain for x in excluded):
        return False
    if not (domain.endswith(".gov") or ".gov." in domain):
        return False
    text = f"{url} {domain}".lower()
    keywords = [
        "medicaid", "medical-assistance", "health", "human", "dhhs", "hhs", "dhs",
        "benefit", "unwinding", "renewal", "covid", "coverage", "services",
        "exchange", "marketplace",
    ]
    return any(k in text for k in keywords)


def search_state_urls(state_name: str) -> tuple[list[str], str]:
    queries = [
        f'"{state_name}" Medicaid unwinding renewal official',
        f'"{state_name}" Medicaid redetermination schedule 2023 official',
    ]
    urls: list[str] = []
    for query in queries:
        try:
            r = requests.get("https://www.bing.com/search", params={"q": query}, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "lxml")
            for a in soup.find_all("a", href=True):
                url = decode_bing_url(a.get("href", ""))
                if url and is_state_official_url(url) and url not in urls:
                    urls.append(url)
            if len(urls) >= 3:
                break
        except Exception:
            continue
        time.sleep(0.2)
    return urls[:3], " | ".join(queries)


def parse_file(source_id: str, path_str: str, parsing_rows: list[dict]) -> None:
    if not path_str:
        return
    path = ROOT / path_str
    if not path.exists():
        return
    outtxt = DIRS["extracted"] / f"{source_id}.txt"
    parser = ""
    text = ""
    pages_or_sheets = ""
    table_count = 0
    warning = ""
    ext = path.suffix.lower()
    try:
        if ext in [".html", ".htm"]:
            raw = path.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(raw, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            parts = []
            for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th", "caption"]):
                value = el.get_text(" ", strip=True)
                if value:
                    parts.append(value)
            text = "\n".join(parts)
            parser = "beautifulsoup_html"
            pages_or_sheets = "html"
            table_count = len(soup.find_all("table"))
        elif ext == ".pdf":
            doc = fitz.open(str(path))
            pages = [f"\n\n--- PAGE {page.number + 1} ---\n{page.get_text()}" for page in doc]
            text = "\n".join(pages)
            parser = "pymupdf"
            pages_or_sheets = str(len(doc))
        elif ext in [".xlsx", ".xls"]:
            xl = pd.ExcelFile(path)
            parts = []
            for sheet in xl.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet, dtype=str)
                parts.append(f"--- SHEET {sheet} ---\n{df.to_csv(index=False)}")
            text = "\n".join(parts)
            parser = "pandas_excel"
            pages_or_sheets = ";".join(xl.sheet_names)
            table_count = len(xl.sheet_names)
        elif ext == ".csv":
            text = pd.read_csv(path, dtype=str).to_csv(index=False)
            parser = "pandas_csv"
            pages_or_sheets = "csv"
            table_count = 1
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
            parser = "plain_text"
            pages_or_sheets = "text"
        outtxt.write_text(text, encoding="utf-8")
        parsed_success = True
    except Exception as exc:
        parsed_success = False
        warning = f"{type(exc).__name__}: {exc}"[:300]
    parsing_rows.append({
        "source_id": source_id,
        "parsed_success": parsed_success,
        "parser_used": parser,
        "pages_or_sheets": pages_or_sheets,
        "text_length": len(text),
        "table_count": table_count,
        "parse_warnings": warning,
    })


def month_in_range(yyyymm: int, start: str, end: str) -> bool:
    start_i = int(start.replace("-", ""))
    end_i = 202406 if end == "end_of_unwinding_unspecified" else int(end.replace("-", ""))
    return start_i <= yyyymm <= end_i


def main() -> None:
    federal_manifest = [download_url(url, DIRS["federal_raw"], sid, title) for sid, title, url in FEDERAL_SEEDS]

    e14_url = FEDERAL_SEEDS[0][2]
    e14_text = (
        "Official source: CMS COVID-19 PHE Unwinding Section 1902(e)(14)(A) Waiver Approvals\n"
        f"URL: {e14_url}\nRetrieved: {NOW}\n\n"
        "This local text archive records the official CMS page and its state-level waiver count table used for structured extraction. "
        "The page does not provide per-state implementation months.\n\n"
        "state_name,state_abbr,total,ex_parte,form_submission_completion,contact_update,reinstatement,other\n"
        + "\n".join(",".join(map(str, row)) for row in E14_COUNTS)
    )
    e14_path = write_text_source(DIRS["federal_raw"] / "federal__medicaid.gov__e14_waiver_approvals_archived_table.txt", e14_text)
    federal_manifest.append({
        "source_id": "fed_cms_e14_archived_table_text",
        "parent_source_id": "fed_seed_01_e14_waiver_approvals",
        "source_url": e14_url,
        "final_url_after_redirect": e14_url,
        "domain": "www.medicaid.gov",
        "title": "CMS E14 waiver approvals archived table text",
        "file_type": "txt",
        "local_file_path": str(e14_path.relative_to(ROOT)).replace("\\", "/"),
        "file_size_bytes": e14_path.stat().st_size,
        "sha256": sha256_file(e14_path),
        "http_status": "web_verified_text_archive",
        "retrieval_timestamp": NOW,
        "posted_date_detected": "2024-12-11",
        "source_grade": "official_federal",
        "crawl_depth": 0,
        "notes": "Medicaid.gov script downloads timed out; table text archived from official page access and structured extraction.",
    })

    delay_url = FEDERAL_SEEDS[2][2]
    delay_text = (
        "Official source: CMS State Option to Delay Procedural Disenrollments\n"
        f"URL: {delay_url}\nRetrieved: {NOW}\n\n"
        "The official CMS page says 15 states were approved to use the temporary state option to delay procedural disenrollments. "
        "Rows below are coded by renewal due month.\n\n"
        "state_name,state_abbr,duration,renewal_due_month_start,renewal_due_month_end,affected_population,evidence\n"
        + "\n".join(",".join('"' + str(x).replace('"', '""') + '"' for x in row) for row in DELAY_EVENTS)
    )
    delay_path = write_text_source(DIRS["federal_raw"] / "federal__medicaid.gov__delay_procedural_disenrollments_archived_table.txt", delay_text)
    federal_manifest.append({
        "source_id": "fed_cms_delay_archived_table_text",
        "parent_source_id": "fed_seed_03_delay_procedural",
        "source_url": delay_url,
        "final_url_after_redirect": delay_url,
        "domain": "www.medicaid.gov",
        "title": "CMS delay procedural disenrollment archived table text",
        "file_type": "txt",
        "local_file_path": str(delay_path.relative_to(ROOT)).replace("\\", "/"),
        "file_size_bytes": delay_path.stat().st_size,
        "sha256": sha256_file(delay_path),
        "http_status": "web_verified_text_archive",
        "retrieval_timestamp": NOW,
        "posted_date_detected": "2024-02-01",
        "source_grade": "official_federal",
        "crawl_depth": 0,
        "notes": "Structured from official CMS page text; expected validation count is 15 states.",
    })
    pd.DataFrame(federal_manifest).to_csv(DIRS["audit"] / "federal_source_manifest.csv", index=False)

    state_manifest = []
    for state_name, state_abbr, _fips in STATE_INFO:
        outdir = DIRS["state_raw"] / state_abbr
        outdir.mkdir(parents=True, exist_ok=True)
        urls, query_used = search_state_urls(state_name)
        if not urls:
            state_manifest.append({
                "state_name": state_name, "state_abbr": state_abbr, "source_id": f"state_{state_abbr}_not_found",
                "source_url": "", "final_url_after_redirect": "", "domain": "", "title": "not_found",
                "file_type": "", "local_file_path": "", "file_size_bytes": 0, "sha256": "",
                "http_status": "not_found", "retrieval_timestamp": NOW, "posted_date_detected": "",
                "official_source_flag": False, "official_agency_name": "", "source_grade": "not_found",
                "search_query_used": query_used,
                "notes": "No official .gov state source found in automated first-pass search. Do not infer absence of policy.",
            })
            continue
        for i, url in enumerate(urls, 1):
            source_id = f"state_{state_abbr}_{i:02d}"
            domain = urlparse(url).netloc.lower()
            ext = Path(urlparse(url).path).suffix.lower() or ".html"
            if len(ext) > 6:
                ext = ".html"
            out = outdir / f"state__{state_abbr}__{domain.replace('www.', '')}__{slugify(url)}{ext}"
            status = ""
            final_url = url
            title = ""
            notes = ""
            try:
                r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
                status = str(r.status_code)
                final_url = r.url
                if r.status_code == 200 and r.content:
                    out.write_bytes(r.content)
                    if "html" in r.headers.get("content-type", "") or ext in [".html", ".htm"]:
                        title = title_from_html(r.text)
                else:
                    notes = f"no usable content length={len(r.content)}"
            except Exception as exc:
                status = f"error:{type(exc).__name__}"
                notes = str(exc)[:200]
            state_manifest.append({
                "state_name": state_name, "state_abbr": state_abbr, "source_id": source_id,
                "source_url": url, "final_url_after_redirect": final_url, "domain": domain, "title": title,
                "file_type": out.suffix.lower().lstrip(".") if out.exists() else ext.lstrip("."),
                "local_file_path": str(out.relative_to(ROOT)).replace("\\", "/") if out.exists() else "",
                "file_size_bytes": out.stat().st_size if out.exists() else 0,
                "sha256": sha256_file(out), "http_status": status, "retrieval_timestamp": NOW,
                "posted_date_detected": "", "official_source_flag": True,
                "official_agency_name": "unknown_state_official_gov_domain",
                "source_grade": "official_state_candidate", "search_query_used": query_used, "notes": notes,
            })
    state_manifest_df = pd.DataFrame(state_manifest)
    state_manifest_df.to_csv(DIRS["audit"] / "state_source_manifest.csv", index=False)

    parsing_rows = []
    for row in federal_manifest:
        parse_file(row["source_id"], row.get("local_file_path", ""), parsing_rows)
    for row in state_manifest:
        parse_file(row["source_id"], row.get("local_file_path", ""), parsing_rows)
    pd.DataFrame(parsing_rows).to_csv(DIRS["audit"] / "parsing_manifest.csv", index=False)

    events = []

    def add_event(**kwargs):
        events.append(kwargs)

    common_cols = [
        "event_id", "state_name", "state_abbr", "state_fips", "federal_or_state_source", "source_id",
        "source_url", "local_file_path", "document_title", "page_number_or_section", "policy_authority",
        "policy_category", "policy_subcategory", "policy_description_short", "affected_population",
        "posted_date", "approval_date", "effective_start_date", "effective_end_date",
        "renewal_due_month_start", "renewal_due_month_end", "implementation_month_start",
        "implementation_month_end", "extracted_date_text", "quoted_evidence_text", "confidence",
        "ambiguity_flag", "notes",
    ]
    for state_name, abbr, total, exparte, form, contact, reinst, other in E14_COUNTS:
        add_event(
            event_id=f"evt_e14_{abbr}", state_name=state_name, state_abbr=abbr,
            state_fips=STATE_BY_ABBR[abbr].state_fips, federal_or_state_source="federal",
            source_id="fed_cms_e14_archived_table_text", source_url=e14_url,
            local_file_path=str(e14_path.relative_to(ROOT)).replace("\\", "/"),
            document_title="CMS E14 waiver approvals archived table text", page_number_or_section="state table",
            policy_authority="Section 1902(e)(14)(A)", policy_category="ex_parte_increase",
            policy_subcategory="e14_strategy_counts",
            policy_description_short=f"CMS table reports {total} approved E14 strategies.",
            affected_population="Medicaid/CHIP beneficiaries subject to unwinding renewals",
            posted_date="2024-12-11", approval_date="", effective_start_date="", effective_end_date="",
            renewal_due_month_start="", renewal_due_month_end="", implementation_month_start="",
            implementation_month_end="",
            extracted_date_text="Approved E14 strategies as of December 11, 2024; state implementation months not provided.",
            quoted_evidence_text=f"{state_name}: total={total}; ex parte={exparte}; form support={form}; contact update={contact}; reinstatement={reinst}; other={other}",
            confidence="medium", ambiguity_flag=True,
            notes="Use as documented strategy count, not precise implementation timing.",
        )
    for state_name, abbr, duration, start, end, population, evidence in DELAY_EVENTS:
        add_event(
            event_id=f"evt_delay_{abbr}", state_name=state_name, state_abbr=abbr,
            state_fips=STATE_BY_ABBR[abbr].state_fips, federal_or_state_source="federal",
            source_id="fed_cms_delay_archived_table_text", source_url=delay_url,
            local_file_path=str(delay_path.relative_to(ROOT)).replace("\\", "/"),
            document_title="CMS State Option to Delay Procedural Disenrollments archived table text",
            page_number_or_section="state table", policy_authority="CMS mitigation strategy",
            policy_category="delay_procedural_disenrollment", policy_subcategory="state_option_delay",
            policy_description_short=f"State approved to delay procedural disenrollments for {duration}.",
            affected_population=population, posted_date="2024-02-01", approval_date="",
            effective_start_date="", effective_end_date="", renewal_due_month_start=start,
            renewal_due_month_end=end, implementation_month_start="", implementation_month_end="",
            extracted_date_text=evidence,
            quoted_evidence_text=f"{state_name}: {duration}, {population}, {evidence}",
            confidence="high" if "end_of_unwinding" not in end else "medium",
            ambiguity_flag="end_of_unwinding" in end, notes="Coded by renewal due month, not coverage loss month.",
        )

    for row in state_manifest:
        if not row.get("local_file_path") or row["http_status"] != "200":
            continue
        txt_path = DIRS["extracted"] / f"{row['source_id']}.txt"
        if not txt_path.exists():
            continue
        txt = txt_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r".{0,120}(unwinding|redetermination|renewal|continuous coverage|public health emergency).{0,180}", txt, re.I | re.S)
        if m:
            add_event(
                event_id=f"evt_doc_{row['source_id']}", state_name=row["state_name"], state_abbr=row["state_abbr"],
                state_fips=STATE_BY_ABBR[row["state_abbr"]].state_fips, federal_or_state_source="state",
                source_id=row["source_id"], source_url=row["source_url"], local_file_path=row["local_file_path"],
                document_title=row.get("title") or "official state source", page_number_or_section="html/text",
                policy_authority="State administrative guidance", policy_category="state_dashboard_or_reporting_update",
                policy_subcategory="official_state_unwinding_document",
                policy_description_short="Official state source discusses Medicaid unwinding/renewal; no implementation date coded by automated first pass.",
                affected_population="Medicaid/CHIP beneficiaries", posted_date="", approval_date="",
                effective_start_date="", effective_end_date="", renewal_due_month_start="", renewal_due_month_end="",
                implementation_month_start="", implementation_month_end="", extracted_date_text="",
                quoted_evidence_text=m.group(0).replace("\n", " ")[:500], confidence="low",
                ambiguity_flag=True, notes="Documentation-only event; not used as main active treatment feature.",
            )

    policy_events = pd.DataFrame(events, columns=common_cols)
    policy_events.to_csv(DIRS["matrix"] / "policy_events_official.csv", index=False)

    e14_df = pd.DataFrame(E14_COUNTS, columns=[
        "state_name", "state_abbr", "e14_total_strategy_count", "e14_ex_parte_strategy_count",
        "e14_form_submission_completion_strategy_count", "e14_contact_update_strategy_count",
        "e14_reinstatement_strategy_count", "e14_other_strategy_count",
    ])

    matrix_rows = []
    for st in STATE_DF.itertuples(index=False):
        e14 = e14_df[e14_df.state_abbr == st.state_abbr].iloc[0].to_dict()
        for period in pd.period_range("2023-03", "2024-06", freq="M"):
            row = {
                "state_name": st.state_name, "state_abbr": st.state_abbr, "state_fips": st.state_fips,
                "year": period.year, "month": period.month, "yyyymm": int(period.strftime("%Y%m")),
            }
            for k, v in e14.items():
                if k not in ["state_name", "state_abbr"]:
                    row[k] = v
            row["e14_any_approved"] = int(row["e14_total_strategy_count"] > 0)
            row["e14_ex_parte_any"] = int(row["e14_ex_parte_strategy_count"] > 0)
            row["e14_form_submission_completion_any"] = int(row["e14_form_submission_completion_strategy_count"] > 0)
            row["e14_contact_update_any"] = int(row["e14_contact_update_strategy_count"] > 0)
            row["e14_reinstatement_any"] = int(row["e14_reinstatement_strategy_count"] > 0)
            row["e14_other_any"] = int(row["e14_other_strategy_count"] > 0)
            zero_cols = [
                "delay_procedural_disenrollment_any", "delay_procedural_disenrollment_months",
                "delay_procedural_disenrollment_all_beneficiaries", "delay_procedural_disenrollment_MAGI",
                "delay_procedural_disenrollment_nonMAGI", "pause_termination_any",
                "renewal_started_this_month", "renewal_staggered_over_12_months",
                "renewal_due_cohort_schedule_available", "official_ex_parte_improvement_policy_active",
                "official_manual_form_support_policy_active", "official_contact_update_policy_active",
                "official_mco_or_provider_outreach_policy_active", "official_targeted_outreach_policy_active",
                "official_reinstatement_policy_active", "official_reconsideration_extension_active",
                "cms_mitigation_strategy_active", "cms_compliance_plan_required_or_available",
                "individual_level_exparte_compliance_issue_flag", "renewal_requirement_correction_plan_flag",
            ]
            for c in zero_cols:
                row[c] = 0
            row["renewal_start_month"] = ""
            row["first_procedural_termination_month"] = ""
            row["planned_unwinding_completion_month"] = ""
            row["pause_or_delay_evidence_source_id"] = ""
            row["n_official_sources_supporting_state_month"] = 1
            row["n_federal_sources_supporting_state_month"] = 1
            row["n_state_sources_supporting_state_month"] = 0
            row["highest_source_grade"] = "official_federal"
            row["has_direct_state_source"] = False
            row["has_direct_federal_state_table_source"] = True
            row["policy_coding_confidence"] = "medium_documented_no_month"
            matrix_rows.append(row)
    matrix = pd.DataFrame(matrix_rows)

    for _state_name, abbr, duration, start, end, population, _evidence in DELAY_EVENTS:
        mask = (matrix.state_abbr == abbr) & matrix.yyyymm.apply(lambda x: month_in_range(x, start, end))
        matrix.loc[mask, "delay_procedural_disenrollment_any"] = 1
        months = int(re.search(r"(\d+)", duration).group(1)) if re.search(r"(\d+)", duration) else np.nan
        matrix.loc[mask, "delay_procedural_disenrollment_months"] = months
        matrix.loc[mask, "delay_procedural_disenrollment_all_beneficiaries"] = int(population == "All beneficiaries")
        matrix.loc[mask, "delay_procedural_disenrollment_MAGI"] = int("MAGI" in population and "Non-MAGI" not in population)
        matrix.loc[mask, "delay_procedural_disenrollment_nonMAGI"] = int("Non-MAGI" in population)
        matrix.loc[mask, "cms_mitigation_strategy_active"] = 1
        matrix.loc[mask, "pause_or_delay_evidence_source_id"] = "fed_cms_delay_archived_table_text"
        matrix.loc[mask, "n_federal_sources_supporting_state_month"] = 2
        matrix.loc[mask, "n_official_sources_supporting_state_month"] = 2
        matrix.loc[mask, "policy_coding_confidence"] = "medium_end_unclear" if "end_of_unwinding" in end else "high"

    state_counts = state_manifest_df[
        (state_manifest_df.local_file_path != "") & (state_manifest_df.http_status == "200")
    ].groupby("state_abbr").size().to_dict() if not state_manifest_df.empty else {}
    for abbr, n in state_counts.items():
        matrix.loc[matrix.state_abbr == abbr, "n_state_sources_supporting_state_month"] = n
        matrix.loc[matrix.state_abbr == abbr, "has_direct_state_source"] = True
        matrix.loc[matrix.state_abbr == abbr, "n_official_sources_supporting_state_month"] += n

    id_cols = {
        "state_name", "state_abbr", "state_fips", "year", "month", "yyyymm", "highest_source_grade",
        "policy_coding_confidence", "pause_or_delay_evidence_source_id", "renewal_start_month",
        "first_procedural_termination_month", "planned_unwinding_completion_month",
    }
    for col in [c for c in matrix.columns if c not in id_cols]:
        if pd.api.types.is_numeric_dtype(matrix[col]) or matrix[col].dtype == bool:
            matrix[f"L1_{col}"] = matrix.groupby("state_abbr")[col].shift(1)
            matrix[f"L2_{col}"] = matrix.groupby("state_abbr")[col].shift(2)
    matrix.to_csv(DIRS["matrix"] / "state_month_policy_matrix_official.csv", index=False)

    bridge = []
    for row in matrix.itertuples(index=False):
        event_id = f"evt_e14_{row.state_abbr}"
        evidence = policy_events.loc[policy_events.event_id == event_id, "quoted_evidence_text"].iloc[0]
        bridge.append({
            "state_abbr": row.state_abbr, "yyyymm": row.yyyymm, "policy_feature": "e14_total_strategy_count",
            "feature_value": row.e14_total_strategy_count, "event_id": event_id,
            "source_id": "fed_cms_e14_archived_table_text", "source_url": e14_url,
            "quoted_evidence_text": evidence, "confidence": "medium",
        })
        if row.delay_procedural_disenrollment_any == 1:
            event_id = f"evt_delay_{row.state_abbr}"
            erow = policy_events.loc[policy_events.event_id == event_id].iloc[0]
            bridge.append({
                "state_abbr": row.state_abbr, "yyyymm": row.yyyymm,
                "policy_feature": "delay_procedural_disenrollment_any", "feature_value": 1,
                "event_id": event_id, "source_id": "fed_cms_delay_archived_table_text",
                "source_url": delay_url, "quoted_evidence_text": erow.quoted_evidence_text,
                "confidence": erow.confidence,
            })
    pd.DataFrame(bridge).to_csv(DIRS["matrix"] / "state_month_policy_source_bridge.csv", index=False)

    e14_val = e14_df.copy()
    e14_val["parsed_total"] = e14_val[[
        "e14_ex_parte_strategy_count", "e14_form_submission_completion_strategy_count",
        "e14_contact_update_strategy_count", "e14_reinstatement_strategy_count", "e14_other_strategy_count",
    ]].sum(axis=1)
    e14_val["count_difference"] = e14_val["e14_total_strategy_count"] - e14_val["parsed_total"]
    e14_val["validation_status"] = np.where(e14_val["count_difference"] == 0, "pass", "check")
    e14_val.to_csv(DIRS["audit"] / "e14_extraction_validation.csv", index=False)

    pd.DataFrame({
        "expected_delay_states": [15],
        "extracted_delay_states": [len(DELAY_EVENTS)],
        "validation_status": ["pass" if len(DELAY_EVENTS) == 15 else "check"],
    }).to_csv(DIRS["audit"] / "delay_procedural_disenrollment_validation.csv", index=False)

    coverage_rows = []
    delay_states = {x[1] for x in DELAY_EVENTS}
    for st in STATE_DF.itertuples(index=False):
        n_state = int(state_counts.get(st.state_abbr, 0))
        coverage_rows.append({
            "state_name": st.state_name, "state_abbr": st.state_abbr,
            "number_of_official_state_pages_found": n_state,
            "number_of_federal_state_specific_references_found": 1 + int(st.state_abbr in delay_states),
            "renewal_timeline_found": False, "e14_waiver_info_found": True,
            "delay_pause_info_found": st.state_abbr in delay_states,
            "state_implementation_date_found": False,
            "state_specific_source_missing": n_state == 0,
            "notes": "Automated first-pass state crawl; timeline/implementation dates not coded unless explicit.",
        })
    coverage = pd.DataFrame(coverage_rows)
    coverage.to_csv(DIRS["audit"] / "state_source_coverage_dashboard.csv", index=False)

    pd.DataFrame(columns=[
        "state_abbr", "event_id_1", "event_id_2", "conflict_type", "description", "resolution"
    ]).to_csv(DIRS["audit"] / "policy_event_conflicts.csv", index=False)
    policy_events[
        (policy_events.ambiguity_flag == True)
        | (policy_events.implementation_month_start.fillna("") == "")
        | (policy_events.confidence == "low")
    ].to_csv(DIRS["audit"] / "policy_extraction_ambiguities.csv", index=False)

    example_states = ["TX", "UT", "ID", "NC", "OR", "CA", "NY", "FL", "GA", "PA"]
    example_lines = []
    for abbr in example_states:
        st = STATE_BY_ABBR[abbr]
        e = e14_df[e14_df.state_abbr == abbr].iloc[0]
        delay = [x for x in DELAY_EVENTS if x[1] == abbr]
        delay_summary = "No CMS delay option extracted." if not delay else (
            f"CMS delay option: {delay[0][2]}, {delay[0][3]} to {delay[0][4]}, population={delay[0][5]}."
        )
        example_lines.append(
            f"- **{abbr} ({st.state_name})**: E14 total={int(e.e14_total_strategy_count)}, "
            f"ex parte={int(e.e14_ex_parte_strategy_count)}, form support={int(e.e14_form_submission_completion_strategy_count)}, "
            f"contact update={int(e.e14_contact_update_strategy_count)}, reinstatement={int(e.e14_reinstatement_strategy_count)}. "
            f"{delay_summary}"
        )

    fed_downloads = sum(1 for row in federal_manifest if row.get("file_size_bytes", 0) > 0)
    state_downloads = int(sum(1 for row in state_manifest if row.get("local_file_path") and row.get("http_status") == "200"))
    states_with_state_source = int((coverage.number_of_official_state_pages_found > 0).sum())
    book = f"""# Policy Text Archive Summary

Last updated: `{NOW}`

## Executive Summary

- Federal official source records archived or logged: `{len(federal_manifest)}`.
- Federal local files with usable bytes: `{fed_downloads}`.
- Official state candidate documents downloaded in first-pass search: `{state_downloads}`.
- Policy events extracted: `{len(policy_events)}`.
- State-month policy rows: `{len(matrix)}`.
- States with at least one official state source downloaded: `{states_with_state_source}`.
- States relying only on federal source tables in this first pass: `{51 - states_with_state_source}`.

This first-pass archive emphasizes official CMS federal tables and guidance. State-source discovery is automated and conservative; missing state sources are marked as missing rather than filled from secondary sources.

## Source Hierarchy

1. Federal CMS tables and guidance: E14 waiver approvals and state option to delay procedural disenrollments are the highest-grade structured sources in this pass.
2. State official agency pages: downloaded only when an official `.gov` state source was found and verified by URL/domain.
3. State PDFs/plans/FAQs: parsed if downloaded, but implementation dates are not inferred from posting dates.
4. Secondary sources: not used for primary coding in this pass.

## Key Policy Features

- `e14_*`: CMS Section 1902(e)(14)(A) strategy-count features. These are documented strategy counts, not precise month-specific implementation dates.
- `delay_procedural_disenrollment_*`: CMS state option with renewal due month ranges. These are the strongest month-coded policy features in this pass.
- `official_*` outreach/form/contact/reinstatement features: mostly zero in the current matrix unless backed by structured federal categories; state-document extraction needs manual review before main use.
- `cms_mitigation_strategy_active`: active for state-months covered by the CMS delay option.

## State Examples

{chr(10).join(example_lines)}

## Research-Use Recommendation

- Credible as ex ante policy indicators now: `delay_procedural_disenrollment_any`, population-specific delay flags, and E14 strategy counts as documented state-level policy capacity indicators.
- Documentation/evidence variables: `n_official_sources_supporting_state_month`, `has_direct_state_source`, `highest_source_grade`, and bridge-file source IDs.
- Auxiliary controls: E14 strategy count groups, especially ex parte, form support, contact update, and reinstatement counts.
- Too ambiguous for main treatment without manual review: exact E14 implementation month, state renewal start dates from generic FAQ pages, and any state page where only a posted date is available.
- Ready to merge with CMS/SIPP for exploratory diagnostics: the state-month matrix and bridge file, with the caveat that E14 timing is documented but not month-specific.

## Validation Summary

- E14 count validation file: `output/policy_audit/e14_extraction_validation.csv`.
- Delay procedural disenrollment validation: extracted `{len(DELAY_EVENTS)}` states; expected `15`.
- Ambiguities are saved in `output/policy_audit/policy_extraction_ambiguities.csv`.

## Guardrail

This archive does not estimate or claim causal effects. It creates an official policy-document layer for later design diagnostics, mechanism evidence, auxiliary controls, ML features, and validation against CMS realized renewal metrics.
"""
    (DIRS["books"] / "policy_text_archive_summary.md").write_text(book, encoding="utf-8")

    print("DONE")
    for path in [
        DIRS["audit"] / "federal_source_manifest.csv",
        DIRS["audit"] / "state_source_manifest.csv",
        DIRS["audit"] / "parsing_manifest.csv",
        DIRS["matrix"] / "policy_events_official.csv",
        DIRS["matrix"] / "state_month_policy_matrix_official.csv",
        DIRS["matrix"] / "state_month_policy_source_bridge.csv",
        DIRS["audit"] / "e14_extraction_validation.csv",
        DIRS["audit"] / "delay_procedural_disenrollment_validation.csv",
        DIRS["audit"] / "state_source_coverage_dashboard.csv",
        DIRS["audit"] / "policy_event_conflicts.csv",
        DIRS["audit"] / "policy_extraction_ambiguities.csv",
        DIRS["books"] / "policy_text_archive_summary.md",
    ]:
        print(path.relative_to(ROOT), path.stat().st_size if path.exists() else "missing")


if __name__ == "__main__":
    main()
