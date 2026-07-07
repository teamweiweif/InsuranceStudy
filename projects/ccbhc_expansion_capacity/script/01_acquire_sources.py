from __future__ import annotations

import csv
import json
import re
import zipfile
from pathlib import Path

import pandas as pd
import requests

from pipeline_utils import (
    ACCESS_DATE,
    RAW,
    SNAP,
    TEMP,
    ensure_dirs,
    save_csv,
    sha256,
    source_row,
    write_text,
    append_note,
)


HEADERS = {"User-Agent": "ccbhc-expansion-capacity-research/1.0"}

POLICY_URLS = {
    "Medicaid.gov CCBHC Demonstration page": "https://www.medicaid.gov/medicaid/financial-management/certified-community-behavioral-health-clinic-ccbhc-demonstration",
    "CMS 2024 cohort press release": "https://www.cms.gov/newsroom/press-releases/biden-harris-administration-expands-access-mental-health-and-substance-use-services-addition-10-new",
    "SAMHSA CCBHC history/background": "https://www.samhsa.gov/communities/certified-community-behavioral-health-clinics/history-background",
    "SAMHSA Section 223 page": "https://www.samhsa.gov/communities/certified-community-behavioral-health-clinics/section-223",
    "SAMHSA CCBHC expansion grants": "https://www.samhsa.gov/communities/certified-community-behavioral-health-clinics/expansion-grants",
    "SAMHSA certification criteria": "https://www.samhsa.gov/communities/certified-community-behavioral-health-clinics/certification-criteria",
    "SAMHSA evaluations and reports": "https://www.samhsa.gov/communities/certified-community-behavioral-health-clinics/evaluations-reports",
    "N-SUMHSS datafiles": "https://www.samhsa.gov/data/data-we-collect/n-sumhss-national-substance-use-and-mental-health-services-survey/datafiles",
    "TEDS datafiles": "https://www.samhsa.gov/data/data-we-collect/teds-treatment-episode-data-set/datafiles",
    "CDC WONDER": "https://wonder.cdc.gov/",
    "HRSA AHRF": "https://data.hrsa.gov/topics/health-workforce/ahrf",
    "HRSA HPSA": "https://data.hrsa.gov/topics/health-workforce/shortage-areas",
    "National Council CCBHC locator": "https://www.thenationalcouncil.org/program/ccbhc-success-center/ccbhc-locator/",
}

STATE_URLS = {
    "Alabama CCBHC press release": "https://mh.alabama.gov/alabama-selected-for-certified-community-behavioral-health-clinic-medicaid-demonstration-program/",
    "Illinois CCBHC initiative": "https://hfs.illinois.gov/medicalproviders/certifiedcommunitybasedhealthcenterinitiative.html",
    "Indiana CCBHC page": "https://www.in.gov/fssa/dmha/certified-community-behavioral-health-clinic/",
    "Iowa CCBHC page": "https://hhs.iowa.gov/health-prevention/behavioral-health-service-system/certified-community-behavioral-health-clinics",
    "Maine CCBHC page": "https://www.maine.gov/dhhs/oms/providers/value-based-purchasing/ccbhc",
    "New Hampshire CCBHC page": "https://www.dhhs.nh.gov/programs-services/health-care/behavioral-health/certified-community-behavioral-health-clinics",
    "Rhode Island CCBHC page": "https://bhddh.ri.gov/CCBHC",
}

NSUMHSS = {
    2021: {
        "csv": "https://www.samhsa.gov/data/system/files/media-puf-file/N-SUMHSS-2021-DS0001-bndl-data-csv_v2.zip",
        "codebook": "https://www.samhsa.gov/data/system/files/media-puf-file/N-SUMHSS-2021-DS0001-info-codebook.pdf",
    },
    2022: {
        "csv": "https://www.samhsa.gov/data/system/files/media-puf-file/N-SUMHSS-2022-DS0001-bndl-data-csv_v1.zip",
        "codebook": "https://www.samhsa.gov/data/system/files/media-puf-file/N-SUMHSS-2022-DS0001-info-codebook.pdf",
    },
    2023: {
        "csv": "https://www.samhsa.gov/data/system/files/media-puf-file/N-SUMHSS-2023-DS0001-bndl-data-csv_v1.zip",
        "codebook": "https://www.samhsa.gov/data/system/files/media-puf-file/N-SUMHSS-2023-DS0001-info-codebook_v1.pdf",
    },
    2024: {
        "csv": "https://www.samhsa.gov/data/system/files/media-puf-file/N-SUMHSS-2024-DS0001-bndl-data-csv_v1.zip",
        "codebook": "https://www.samhsa.gov/data/system/files/media-puf-file/N-SUMHSS-2024-DS0001-info-codebook_v1.pdf",
    },
}


def fetch(url: str, path: Path, binary: bool = True) -> tuple[str, str]:
    if path.exists() and path.stat().st_size > 0:
        return "cached", sha256(path)
    try:
        r = requests.get(url, headers=HEADERS, timeout=120)
        r.raise_for_status()
        if binary:
            path.write_bytes(r.content)
        else:
            path.write_text(r.text, encoding="utf-8", newline="\n")
        return "downloaded", sha256(path)
    except Exception as exc:
        return f"failed: {exc}", ""


def zip_shape(path: Path) -> tuple[int, int]:
    with zipfile.ZipFile(path) as z:
        csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            return 0, 0
        with z.open(csv_names[0]) as f:
            header = f.readline().decode("utf-8", errors="replace").rstrip("\n\r")
            cols = next(csv.reader([header]))
            rows = sum(1 for _ in f)
        return rows, len(cols)


def census_acs() -> pd.DataFrame:
    rows = []
    variables = [
        "NAME",
        "B01003_001E",  # population
        "B17001_001E",  # poverty universe
        "B17001_002E",  # below poverty
        "B23025_003E",  # civilian labor force
        "B23025_005E",  # unemployed
        "B19013_001E",  # median household income
    ]
    for year in range(2019, 2025):
        url = f"https://api.census.gov/data/{year}/acs/acs5"
        params = {"get": ",".join(variables), "for": "county:*"}
        status = "ok"
        try:
            r = requests.get(url, params=params, timeout=120)
            r.raise_for_status()
            data = r.json()
            head = data[0]
            for item in data[1:]:
                row = dict(zip(head, item))
                row["year"] = year
                rows.append(row)
        except Exception as exc:
            status = f"failed: {exc}"
        (TEMP / "audit_log.md").open("a", encoding="utf-8").write(f"\nACS {year}: {status}\n")
    df = pd.DataFrame(rows)
    if df.empty:
        pop_url = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv"
        try:
            pop = pd.read_csv(pop_url, encoding="latin1")
            pop = pop[pop["SUMLEV"].astype(str).str.zfill(3).eq("050")].copy()
            out = []
            for year in range(2021, 2025):
                col = f"POPESTIMATE{year}"
                tmp = pop[["STATE", "COUNTY", "STNAME", "CTYNAME", col]].copy()
                tmp = tmp.rename(columns={col: "population"})
                tmp["year"] = year
                tmp["state_fips"] = tmp["STATE"].astype(str).str.zfill(2)
                tmp["county_fips3"] = tmp["COUNTY"].astype(str).str.zfill(3)
                tmp["county_fips"] = tmp["state_fips"] + tmp["county_fips3"]
                tmp["NAME"] = tmp["CTYNAME"].astype(str) + ", " + tmp["STNAME"].astype(str)
                tmp["poverty_universe"] = pd.NA
                tmp["poverty_count"] = pd.NA
                tmp["civilian_labor_force"] = pd.NA
                tmp["unemployed_count"] = pd.NA
                tmp["median_household_income"] = pd.NA
                tmp["poverty_rate"] = pd.NA
                tmp["unemployment_rate"] = pd.NA
                out.append(tmp[[
                    "NAME", "population", "poverty_universe", "poverty_count",
                    "civilian_labor_force", "unemployed_count", "median_household_income",
                    "state_fips", "county_fips3", "county_fips", "year",
                    "poverty_rate", "unemployment_rate",
                ]])
            fallback = pd.concat(out, ignore_index=True)
            (TEMP / "audit_log.md").open("a", encoding="utf-8").write(
                "\nACS API failed because a Census key was required; used Census county population estimates fallback.\n"
            )
            return fallback
        except Exception as exc:
            (TEMP / "audit_log.md").open("a", encoding="utf-8").write(
                f"\nCensus population-estimates fallback failed: {exc}\n"
            )
            return df
    rename = {
        "B01003_001E": "population",
        "B17001_001E": "poverty_universe",
        "B17001_002E": "poverty_count",
        "B23025_003E": "civilian_labor_force",
        "B23025_005E": "unemployed_count",
        "B19013_001E": "median_household_income",
    }
    df = df.rename(columns=rename)
    df["state_fips"] = df["state"].astype(str).str.zfill(2)
    df["county_fips3"] = df["county"].astype(str).str.zfill(3)
    df["county_fips"] = df["state_fips"] + df["county_fips3"]
    for col in rename.values():
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["poverty_rate"] = df["poverty_count"] / df["poverty_universe"]
    df["unemployment_rate"] = df["unemployed_count"] / df["civilian_labor_force"]
    return df


def main() -> None:
    ensure_dirs()
    inventory = []

    for source_name, url in {**POLICY_URLS, **STATE_URLS}.items():
        safe = re.sub(r"[^A-Za-z0-9]+", "_", source_name).strip("_")
        suffix = ".pdf" if url.lower().endswith(".pdf") else ".html"
        path = SNAP / f"{safe}{suffix}"
        status, digest = fetch(url, path, binary=suffix == ".pdf")
        inventory.append(source_row(
            source_name, "official or high-quality public source", "webpage/pdf snapshot",
            str(path), geography="US/state", unit="policy source", checksum_if_possible=digest,
            license_or_access_note="public web source", status=status,
            caveats="State source list is targeted to auditable start-date evidence; missing 2024 states are documented in treatment notes.",
        ))

    for year, links in NSUMHSS.items():
        for kind, url in links.items():
            filename = url.split("/")[-1]
            path = RAW / filename if kind == "csv" else SNAP / filename
            status, digest = fetch(url, path, binary=True)
            row_count, col_count = ("", "")
            if kind == "csv" and path.exists():
                try:
                    row_count, col_count = zip_shape(path)
                except Exception as exc:
                    status = f"{status}; shape_failed: {exc}"
            inventory.append(source_row(
                f"N-SUMHSS {year} {kind}", "SAMHSA", "public-use file" if kind == "csv" else "codebook",
                str(path), years_covered=str(year), geography="US states; county suppressed in PUF",
                unit="facility", row_count=row_count, column_count=col_count,
                checksum_if_possible=digest, license_or_access_note="SAMHSA public-use file",
                status=status,
                caveats="PUF includes state but no county/FIPS/address; county designs cannot use this file directly.",
            ))

    acs = census_acs()
    acs_path = RAW / "acs_county_covariates_2019_2024.csv"
    if not acs.empty:
        save_csv(acs, acs_path)
        acs_status = "downloaded"
        acs_rows, acs_cols = acs.shape
        acs_hash = sha256(acs_path)
    else:
        acs_status = "failed"
        acs_rows, acs_cols, acs_hash = "", "", ""
    inventory.append(source_row(
        "Census county covariates/population 2019-2024", "US Census Bureau", "API extract with population-estimates fallback",
        str(acs_path), years_covered="2019-2024", geography="US county",
        unit="county-year", row_count=acs_rows, column_count=acs_cols,
        checksum_if_possible=acs_hash, license_or_access_note="public API; cite Census ACS",
        status=acs_status,
        caveats="ACS API required a key in this environment; fallback uses county population estimates for 2021-2024, with poverty/unemployment flagged missing.",
    ))

    inventory.extend([
        source_row(
            "TEDS-A admissions public-use files", "SAMHSA", "access record",
            "https://www.samhsa.gov/data/data-we-collect/teds-treatment-episode-data-set/datafiles",
            years_covered="2019-2023 available; no 2024/2025 public file found", geography="state",
            unit="admission episode", status="documented_not_downloaded",
            caveats="Not used in main models because no post-2024 public admissions file is available and TEDS-A is admission episodes, not people.",
        ),
        source_row(
            "CDC WONDER mortality", "CDC/NCHS", "access record",
            "https://wonder.cdc.gov/", years_covered="through 2023/2024 depending on database",
            geography="county/state", unit="death", status="documented_not_downloaded",
            caveats="Mortality is downstream and too slow for 2024 early capacity evaluation; no 2025 post period.",
        ),
        source_row(
            "HRSA AHRF", "HRSA", "access record",
            "https://data.hrsa.gov/topics/health-workforce/ahrf", years_covered="current and historical",
            geography="county/state", unit="county", status="documented_not_downloaded",
            caveats="Large multi-domain covariate source; ACS was used for first-pass covariates.",
        ),
        source_row(
            "HRSA mental-health HPSA", "HRSA", "access record",
            "https://data.hrsa.gov/topics/health-workforce/shortage-areas", years_covered="daily current snapshot",
            geography="county/designation area", unit="HPSA designation", status="documented_not_downloaded",
            caveats="Current HPSA status is useful for moderation but not a historical annual panel in this first build.",
        ),
    ])

    inv = pd.DataFrame(inventory)
    save_csv(inv, TEMP / "source_inventory.csv")
    append_note("Phase 1: Policy/source audit", [
        "Archived official federal policy pages, N-SUMHSS PUFs/codebooks for 2021-2024, and ACS county covariates.",
        "Recorded TEDS-A, CDC WONDER, AHRF, and HPSA as access records rather than forcing non-post or non-historical sources into the main design.",
        "N-SUMHSS PUF has no county geography; county-level capacity outcomes require a different source or restricted data.",
    ])


if __name__ == "__main__":
    main()
