from __future__ import annotations

import importlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMP = ROOT / "temp"
REQUIRED_DIRS = [
    ROOT / "data",
    ROOT / "script",
    ROOT / "result",
    ROOT / "report",
    TEMP,
    TEMP / "raw_downloads",
    TEMP / "raw_downloads" / "policy_docs",
    TEMP / "raw_downloads" / "provider_archives",
    TEMP / "intermediate",
]

REQUIRED_PACKAGES = [
    "pandas",
    "numpy",
    "scipy",
    "matplotlib",
    "requests",
    "pyarrow",
    "duckdb",
    "sklearn",
    "openpyxl",
    "docx",
]


def package_version(name: str) -> str:
    try:
        module = importlib.import_module(name)
    except Exception as exc:
        return f"MISSING ({exc.__class__.__name__}: {exc})"
    return str(getattr(module, "__version__", "installed_version_unknown"))


def main() -> None:
    for path in REQUIRED_DIRS:
        path.mkdir(parents=True, exist_ok=True)

    env = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(ROOT),
        "python": sys.version,
        "platform": platform.platform(),
        "packages": {pkg: package_version(pkg) for pkg in REQUIRED_PACKAGES},
    }
    (TEMP / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")

    missing = [pkg for pkg, ver in env["packages"].items() if ver.startswith("MISSING")]
    print(json.dumps(env, indent=2))
    if missing:
        raise SystemExit(
            "Missing required Python packages: "
            + ", ".join(missing)
            + ". Install packages listed in requirements.txt."
        )


if __name__ == "__main__":
    main()
