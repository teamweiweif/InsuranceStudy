import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    import pyarrow.parquet as pq
except Exception:  # pragma: no cover
    pq = None


SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".xlsx", ".parquet"}
FULL_PROFILE_MAX_MB = 50
SAMPLE_ROWS = 10000
TOP_VALUE_LIMIT = 10


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        try:
            return path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return path.as_posix()


def discover_files(root: Path):
    candidate_dirs = ["data", "data_clean", "data_intermediate", "data_raw"]
    files = []
    for name in candidate_dirs:
        base = root / name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(path)

    for path in root.glob("*.csv"):
        files.append(path)

    deduped = []
    seen = set()
    for path in sorted(files):
        key = path.resolve()
        if key not in seen:
            deduped.append(path)
            seen.add(key)
    return deduped


def count_csv_rows(path: Path) -> int | None:
    try:
        with path.open("rb") as fh:
            return max(sum(1 for _ in fh) - 1, 0)
    except Exception:
        return None


def load_profile_frame(path: Path, size_mb: float):
    suffix = path.suffix.lower()
    full_profile = size_mb <= FULL_PROFILE_MAX_MB
    profile_basis = "full_file" if full_profile else f"first_{SAMPLE_ROWS}_rows"

    if suffix == ".csv":
        if full_profile:
            frame = pd.read_csv(path, low_memory=False)
            return frame, profile_basis, len(frame)
        row_count = count_csv_rows(path)
        return pd.read_csv(path, nrows=SAMPLE_ROWS, low_memory=False), profile_basis, row_count

    if suffix == ".parquet":
        row_count = None
        parquet_file = None
        if pq is not None:
            try:
                parquet_file = pq.ParquetFile(path)
                row_count = parquet_file.metadata.num_rows
            except Exception:
                row_count = None
        if full_profile:
            return pd.read_parquet(path), profile_basis, row_count
        if parquet_file is not None and parquet_file.num_row_groups:
            return parquet_file.read_row_group(0).to_pandas().head(SAMPLE_ROWS), profile_basis, row_count
        return pd.read_parquet(path).head(SAMPLE_ROWS), profile_basis, row_count

    if suffix == ".xlsx":
        return pd.read_excel(path, nrows=None if full_profile else SAMPLE_ROWS), profile_basis, None

    if suffix == ".jsonl":
        return pd.read_json(path, lines=True, nrows=None if full_profile else SAMPLE_ROWS), profile_basis, None

    if suffix == ".json":
        try:
            return pd.read_json(path), profile_basis, None
        except ValueError:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                data = [data]
            return pd.json_normalize(data), profile_basis, None

    raise ValueError(f"Unsupported extension: {suffix}")


def numeric_summary(series: pd.Series):
    if pd.api.types.is_bool_dtype(series):
        numeric = series.astype("float64")
        return {
            "min": numeric.min(),
            "p25": numeric.quantile(0.25),
            "median": numeric.quantile(0.5),
            "p75": numeric.quantile(0.75),
            "max": numeric.max(),
            "mean": numeric.mean(),
            "std": numeric.std(),
        }
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == 0:
        return {}
    q = numeric.quantile([0.25, 0.5, 0.75])
    return {
        "min": numeric.min(),
        "p25": q.loc[0.25],
        "median": q.loc[0.5],
        "p75": q.loc[0.75],
        "max": numeric.max(),
        "mean": numeric.mean(),
        "std": numeric.std(),
    }


def summarize_dataset(project_name: str, project_root: Path, path: Path):
    size_mb = path.stat().st_size / (1024 * 1024)
    inventory = {
        "project": project_name,
        "dataset_path": rel(path, project_root),
        "format": path.suffix.lower().lstrip("."),
        "size_mb": round(size_mb, 4),
        "row_count": "",
        "column_count": "",
        "profile_basis": "",
        "profile_rows": "",
        "status": "ok",
        "error": "",
    }
    variables = []
    top_values = []

    try:
        frame, profile_basis, row_count = load_profile_frame(path, size_mb)
        inventory["row_count"] = row_count if row_count is not None else len(frame)
        inventory["column_count"] = len(frame.columns)
        inventory["profile_basis"] = profile_basis
        inventory["profile_rows"] = len(frame)

        for column in frame.columns:
            series = frame[column]
            nonmissing = int(series.notna().sum())
            missing = int(series.isna().sum())
            unique = int(series.nunique(dropna=True))
            variable = {
                "project": project_name,
                "dataset_path": rel(path, project_root),
                "variable": str(column),
                "dtype": str(series.dtype),
                "row_count": inventory["row_count"],
                "profile_basis": profile_basis,
                "profile_rows": len(frame),
                "nonmissing_in_profile": nonmissing,
                "missing_in_profile": missing,
                "unique_in_profile": unique,
                "min": "",
                "p25": "",
                "median": "",
                "p75": "",
                "max": "",
                "mean": "",
                "std": "",
                "top_value": "",
                "top_value_count": "",
            }

            for key, value in numeric_summary(series).items():
                variable[key] = value

            counts = series.dropna().astype(str).value_counts().head(TOP_VALUE_LIMIT)
            if not counts.empty:
                variable["top_value"] = counts.index[0]
                variable["top_value_count"] = int(counts.iloc[0])
                for rank, (value, count) in enumerate(counts.items(), start=1):
                    top_values.append(
                        {
                            "project": project_name,
                            "dataset_path": rel(path, project_root),
                            "variable": str(column),
                            "rank": rank,
                            "value": value,
                            "count_in_profile": int(count),
                            "profile_basis": profile_basis,
                            "profile_rows": len(frame),
                        }
                    )
            variables.append(variable)
    except Exception as exc:
        inventory["status"] = "error"
        inventory["error"] = f"{type(exc).__name__}: {exc}"

    return inventory, variables, top_values


def write_metadata(project_name: str, source_root: Path, output_root: Path):
    output_root.mkdir(parents=True, exist_ok=True)
    inventories = []
    variables = []
    top_values = []

    for path in discover_files(source_root):
        inventory, variable_rows, top_rows = summarize_dataset(project_name, source_root, path)
        inventories.append(inventory)
        variables.extend(variable_rows)
        top_values.extend(top_rows)

    pd.DataFrame(inventories).to_csv(output_root / "dataset_inventory.csv", index=False)
    pd.DataFrame(variables).to_csv(output_root / "variable_catalog.csv", index=False)
    pd.DataFrame(top_values).to_csv(output_root / "categorical_top_values.csv", index=False)

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    readme = f"""# Data Metadata

Generated: {generated_at}

Source project root: `{source_root}`

This folder is the GitHub-friendly data audit layer for `{project_name}`. It is
intended to make the datasets inspectable without committing raw downloads,
large intermediate panels, or bulky Parquet/CSV files.

Files:

- `dataset_inventory.csv`: one row per profiled data file, with format, file
  size, row count where available, column count, and whether the profile used the
  full file or the first {SAMPLE_ROWS} rows.
- `variable_catalog.csv`: one row per variable, with dtype, missingness and
  uniqueness in the profiled rows, numeric summaries when applicable, and the
  most common observed value.
- `categorical_top_values.csv`: top observed values for each variable in the
  profiled rows.

For files larger than {FULL_PROFILE_MAX_MB} MB, row counts are still recorded
when feasible, but distribution summaries are based on the first {SAMPLE_ROWS}
rows. For smaller supported files, summaries are full-file profiles.
"""
    (output_root / "README.md").write_text(readme, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()

    write_metadata(args.project_name, Path(args.source_root), Path(args.output_root))


if __name__ == "__main__":
    main()
