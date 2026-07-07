from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TEMP = ROOT / "temp"
RESULT = ROOT / "result"
REPORT = ROOT / "report"
RAW = TEMP / "raw_downloads"
SNAP = TEMP / "source_snapshots"
WORK = TEMP / "work"
ACCESS_DATE = "2026-07-07"
SEED = 20260707

STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08",
    "CT": "09", "DE": "10", "DC": "11", "FL": "12", "GA": "13", "HI": "15",
    "ID": "16", "IL": "17", "IN": "18", "IA": "19", "KS": "20", "KY": "21",
    "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27",
    "MS": "28", "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
    "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46",
    "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53",
    "WV": "54", "WI": "55", "WY": "56",
}

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

ORIGINAL_DEMO_STATES = {"MN", "MO", "NV", "NJ", "NY", "OK", "OR", "PA"}
CARES_ADDED_DEMO_STATES = {"KY", "MI"}
COHORT_2024 = {"AL", "IL", "IN", "IA", "KS", "ME", "NH", "NM", "RI", "VT"}
COHORT_2026 = {"AK", "CO", "HI", "LA", "MD", "MS", "MT", "ND", "WA", "WV"}
PLANNING_2023 = {
    "AL", "DE", "GA", "IA", "KS", "ME", "MS", "MT", "NC", "NH", "NM", "OH",
    "RI", "VT", "WV",
}
PLANNING_2025 = {
    "AK", "CO", "CT", "DE", "DC", "HI", "LA", "MD", "MT", "NC", "ND", "SD",
    "UT", "WA", "WV",
}

# State-specific starts are entered only when public state evidence was found
# during the source audit. Missing values are not imputed.
DEMO_START_EVIDENCE = {
    "IL": ("2024-10-01", "state evidence: HFS kickoff/certification materials indicate sites operationally compliant Oct. 1, 2024", "medium"),
    "IN": ("2025-01-01", "state evidence: Indiana bulletin describes CCBHC claims for dates of service on or after Jan. 1, 2025", "medium"),
    "IA": ("2025-07-01", "state evidence: Iowa HHS materials state the demonstration began July 1, 2025", "high"),
    "KS": ("2024-07-01", "state legislative/budget sources indicate statewide CCBHC certification by July 1, 2024; payment start not independently verified", "low"),
    "ME": ("2025-03-01", "state evidence: MaineCare comment summary gives planned implementation March 1, 2025", "medium"),
    "NH": ("2024-07-01", "state evidence implies a four-year demonstration through June 2028 after June 2024 selection; exact payment date not independently verified", "low"),
    "RI": ("2024-10-01", "state evidence: Rhode Island CCBHC page and operations manual state launch/DY1 on Oct. 1, 2024", "high"),
    "VT": ("2025-07-01", "state evidence: Vermont certification/budget materials state demonstration begins July 1, 2025", "high"),
}


def ensure_dirs() -> None:
    for path in [DATA, TEMP, RESULT, REPORT, RAW, SNAP, WORK]:
        path.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def append_note(phase: str, bullets: Iterable[str]) -> None:
    lines = [f"\n## {phase} ({ACCESS_DATE})\n"]
    lines.extend(f"- {b}\n" for b in bullets)
    with (TEMP / "iteration_notes.md").open("a", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)


def yes_indicator(series: pd.Series) -> pd.Series:
    vals = series.astype("string").str.strip().str.upper()
    out = pd.Series(np.nan, index=series.index, dtype="float64")
    out[vals.isin(["1", "1.0", "YES", "Y", "TRUE"])] = 1.0
    out[vals.isin(["0", "0.0", "NO", "N", "FALSE", "2", "3", "4", "5", "6"])] = 0.0
    return out


def rate_per_100k(count: pd.Series, pop: pd.Series) -> pd.Series:
    return np.where(pop.astype(float) > 0, count.astype(float) / pop.astype(float) * 100000.0, np.nan)


def save_csv(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def _fixed_effect_matrix(df: pd.DataFrame, fe_cols: list[str]) -> np.ndarray:
    mats = [np.ones((len(df), 1))]
    for col in fe_cols:
        d = pd.get_dummies(df[col].astype("string"), prefix=col, dummy_na=True, dtype=float)
        mats.append(d.to_numpy())
    return np.column_stack(mats)


def residualize(df: pd.DataFrame, cols: list[str], fe_cols: list[str]) -> pd.DataFrame:
    z = _fixed_effect_matrix(df, fe_cols)
    out = {}
    for col in cols:
        y = df[col].astype(float).to_numpy()
        mask = np.isfinite(y) & np.all(np.isfinite(z), axis=1)
        beta = np.linalg.lstsq(z[mask], y[mask], rcond=None)[0]
        resid = np.full(len(df), np.nan)
        resid[mask] = y[mask] - z[mask] @ beta
        out[col] = resid
    return pd.DataFrame(out, index=df.index)


def fit_fe_ols(
    df: pd.DataFrame,
    y_col: str,
    x_cols: list[str],
    fe_cols: list[str],
    cluster_col: str | None = None,
) -> tuple[pd.DataFrame, dict]:
    needed_cols = list(dict.fromkeys([y_col] + x_cols + fe_cols + ([cluster_col] if cluster_col else [])))
    work = df[needed_cols].copy()
    for col in [y_col] + x_cols:
        work[col] = pd.to_numeric(work[col], errors="coerce")
    work = work.dropna(subset=[y_col] + x_cols)
    if len(work) <= len(x_cols) + 2:
        rows = [
            {"term": x, "coef": np.nan, "se": np.nan, "t": np.nan, "p": np.nan, "n": len(work)}
            for x in x_cols
        ]
        return pd.DataFrame(rows), {"n": len(work), "status": "too_few_observations"}

    rz = residualize(work, [y_col] + x_cols, fe_cols)
    y = rz[y_col].to_numpy()
    x = rz[x_cols].to_numpy()
    valid = np.isfinite(y) & np.all(np.isfinite(x), axis=1)
    y = y[valid]
    x = x[valid]
    work_valid = work.loc[valid].copy()
    k = x.shape[1]
    n = len(y)
    try:
        xtx_inv = np.linalg.pinv(x.T @ x)
        beta = xtx_inv @ x.T @ y
        resid = y - x @ beta
        if cluster_col:
            meat = np.zeros((k, k))
            groups = work_valid[cluster_col].astype("string").to_numpy()
            unique_groups = pd.unique(groups)
            for g in unique_groups:
                idx = groups == g
                xg = x[idx]
                eg = resid[idx][:, None]
                meat += xg.T @ (eg @ eg.T) @ xg
            g_count = len(unique_groups)
            correction = (g_count / max(g_count - 1, 1)) * ((n - 1) / max(n - k, 1))
            vcov = correction * xtx_inv @ meat @ xtx_inv
            df_resid = max(g_count - 1, 1)
        else:
            meat = x.T @ np.diag(resid ** 2) @ x
            correction = n / max(n - k, 1)
            vcov = correction * xtx_inv @ meat @ xtx_inv
            df_resid = max(n - k, 1)
        se = np.sqrt(np.maximum(np.diag(vcov), 0))
        tstat = beta / se
        pval = 2 * (1 - stats.t.cdf(np.abs(tstat), df=df_resid))
        rows = []
        for i, term in enumerate(x_cols):
            rows.append({
                "term": term,
                "coef": beta[i],
                "se": se[i],
                "t": tstat[i],
                "p": pval[i],
                "n": n,
                "df": df_resid,
            })
        meta = {
            "n": n,
            "k": k,
            "fe": fe_cols,
            "cluster": cluster_col,
            "status": "ok",
            "r2_resid": 1 - float(np.sum(resid ** 2) / np.sum((y - y.mean()) ** 2)) if np.sum((y - y.mean()) ** 2) > 0 else np.nan,
        }
        return pd.DataFrame(rows), meta
    except Exception as exc:
        rows = [
            {"term": x, "coef": np.nan, "se": np.nan, "t": np.nan, "p": np.nan, "n": n}
            for x in x_cols
        ]
        return pd.DataFrame(rows), {"n": n, "status": f"failed: {exc}"}


def joint_wald(table: pd.DataFrame, terms: list[str]) -> dict:
    sub = table[table["term"].isin(terms)].dropna(subset=["coef", "se"])
    if sub.empty:
        return {"wald": np.nan, "p": np.nan, "df": 0}
    wald = float(np.sum((sub["coef"] / sub["se"]) ** 2))
    df = len(sub)
    return {"wald": wald, "p": float(1 - stats.chi2.cdf(wald, df)), "df": df}


def smd(a: pd.Series, b: pd.Series) -> float:
    a = pd.to_numeric(a, errors="coerce").dropna()
    b = pd.to_numeric(b, errors="coerce").dropna()
    if len(a) == 0 or len(b) == 0:
        return np.nan
    pooled = math.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return float((a.mean() - b.mean()) / pooled) if pooled > 0 else np.nan


def json_dump(obj: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def source_row(
    source_name: str,
    agency_or_owner: str,
    source_type: str,
    url: str,
    years_covered: str = "",
    geography: str = "",
    unit: str = "",
    row_count: str | int | None = "",
    column_count: str | int | None = "",
    checksum_if_possible: str = "",
    license_or_access_note: str = "",
    status: str = "",
    caveats: str = "",
) -> dict:
    return {
        "source_name": source_name,
        "agency_or_owner": agency_or_owner,
        "source_type": source_type,
        "URL_or_access_path": url,
        "access_date": ACCESS_DATE,
        "years_covered": years_covered,
        "geography": geography,
        "unit": unit,
        "row_count": row_count,
        "column_count": column_count,
        "checksum_if_possible": checksum_if_possible,
        "license_or_access_note": license_or_access_note,
        "status": status,
        "caveats": caveats,
    }
