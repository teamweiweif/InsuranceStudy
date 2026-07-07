from __future__ import annotations

import importlib.util
import platform
import sys

from project_utils import ROOT, append_audit, ensure_dirs, json_dump


def main() -> None:
    ensure_dirs()
    required = [
        "pandas",
        "numpy",
        "requests",
        "bs4",
        "fitz",
        "pyarrow",
        "matplotlib",
        "seaborn",
        "scipy",
        "sklearn",
        "duckdb",
        "openpyxl",
    ]
    optional = ["statsmodels", "linearmodels", "pdfplumber", "camelot", "polars"]
    packages = {}
    for name in required + optional:
        try:
            packages[name] = bool(importlib.util.find_spec(name))
        except Exception:
            packages[name] = False

    stamp = {
        "python": sys.version,
        "platform": platform.platform(),
        "root": str(ROOT),
        "packages": packages,
        "note": (
            "Core pipeline uses pandas, PyMuPDF, numpy/scipy, matplotlib, and pyarrow. "
            "Missing econometric packages are handled with transparent fallback estimators."
        ),
    }
    json_dump(stamp, ROOT / "result" / "environment.json")
    append_audit("Setup completed; environment stamp written to result/environment.json.")


if __name__ == "__main__":
    main()

