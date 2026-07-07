from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import fitz
import numpy as np
import pandas as pd

from project_utils import DATA, PDF_CHECKS, RAW, STATE_CODES, append_audit, rel, save_csv, save_parquet


PDF_DIR = RAW / "988_state_monthly_reports"


@dataclass
class ParsedRow:
    year_month: str
    state: str
    source_pdf: str
    page: int
    raw_row_text: str
    routed_in_state: float | None
    received_in_state: float | None
    answered_in_state: float | None
    in_state_answer_rate_reported: float | None
    abandoned_in_state_count: float | None
    flowout_to_national_backup_count: float | None
    average_speed_to_answer_seconds: float | None
    average_talk_time_seconds: float | None
    parse_status: str
    parse_note: str


def clean_token(token: str) -> str:
    return token.strip().replace("\u201c", "").replace("\u201d", "").replace('"', "")


def is_state_token(token: str) -> bool:
    token = clean_token(token).upper()
    return token in STATE_CODES


def parse_number(token: str) -> float | None:
    token = clean_token(token)
    if token in {"", "N/A", "[No", "Response]", "--", "-"}:
        return None
    token = token.replace(",", "").replace("$", "")
    if re.fullmatch(r"-?\d+(\.\d+)?", token):
        return float(token)
    return None


def parse_percent(token: str) -> float | None:
    token = clean_token(token)
    m = re.fullmatch(r"(\d+(\.\d+)?)%", token)
    if m:
        return float(m.group(1)) / 100.0
    return None


def parse_colon_time(token: str) -> float | None:
    token = clean_token(token)
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", token)
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2))


def parse_time_tokens(tokens: list[str]) -> tuple[float | None, float | None]:
    values: list[float] = []
    i = 0
    while i < len(tokens):
        tok = clean_token(tokens[i])
        colon = parse_colon_time(tok)
        if colon is not None:
            values.append(colon)
            i += 1
            continue
        num = parse_number(tok)
        unit = clean_token(tokens[i + 1]).lower() if i + 1 < len(tokens) else ""
        if num is not None and unit.startswith("sec"):
            values.append(float(num))
            i += 2
            continue
        if num is not None and unit.startswith("min"):
            values.append(float(num) * 60.0)
            i += 2
            continue
        i += 1
    speed = values[0] if len(values) >= 1 else None
    talk = values[1] if len(values) >= 2 else None
    return speed, talk


def group_words_into_rows(words: list[tuple], y_tol: float = 2.8) -> list[list[tuple]]:
    rows: list[list[tuple]] = []
    for w in sorted(words, key=lambda x: (x[1], x[0])):
        text = clean_token(w[4])
        if not text:
            continue
        placed = False
        for row in rows[-3:]:
            y = np.mean([x[1] for x in row])
            if abs(w[1] - y) <= y_tol:
                row.append(w)
                placed = True
                break
        if not placed:
            rows.append([w])
    return [sorted(row, key=lambda x: x[0]) for row in rows]


def parse_metric_row(tokens: list[str]) -> dict:
    pct_idx = None
    for i, tok in enumerate(tokens):
        if parse_percent(tok) is not None:
            pct_idx = i
            break
    if pct_idx is None:
        return {"status": "failed", "note": "no percentage token"}

    before_pct = [parse_number(tok) for tok in tokens[:pct_idx]]
    before_pct = [x for x in before_pct if x is not None]
    after = tokens[pct_idx + 1 :]
    after_nums = [parse_number(tok) for tok in after]
    after_nums = [x for x in after_nums if x is not None]

    if len(before_pct) >= 3:
        routed, received, answered = before_pct[0], before_pct[1], before_pct[2]
    elif len(before_pct) >= 2:
        routed, received, answered = before_pct[0], None, before_pct[1]
    else:
        return {"status": "failed", "note": "too few count tokens before percentage"}

    abandoned = after_nums[0] if len(after_nums) >= 1 else None
    flowout = after_nums[1] if len(after_nums) >= 2 else None
    speed, talk = parse_time_tokens(after)

    return {
        "status": "parsed",
        "note": "",
        "routed_in_state": routed,
        "received_in_state": received,
        "answered_in_state": answered,
        "in_state_answer_rate_reported": parse_percent(tokens[pct_idx]),
        "abandoned_in_state_count": abandoned,
        "flowout_to_national_backup_count": flowout,
        "average_speed_to_answer_seconds": speed,
        "average_talk_time_seconds": talk,
    }


def parse_pdf(path: Path) -> list[ParsedRow]:
    m = re.match(r"(\d{4}-\d{2})_", path.name)
    if not m:
        raise ValueError(f"Cannot infer year_month from {path.name}")
    year_month = m.group(1)
    rows: list[ParsedRow] = []
    doc = fitz.open(str(path))
    for page_idx, page in enumerate(doc, start=1):
        words = page.get_text("words")
        for row in group_words_into_rows(words):
            if not row:
                continue
            first = clean_token(row[0][4]).upper()
            if not is_state_token(first):
                continue
            if row[0][0] > 85:
                continue
            tokens = [clean_token(w[4]) for w in row]
            state = first
            payload = tokens[1:]
            parsed = parse_metric_row(payload)
            rows.append(
                ParsedRow(
                    year_month=year_month,
                    state=state,
                    source_pdf=rel(path),
                    page=page_idx,
                    raw_row_text=" ".join(tokens),
                    routed_in_state=parsed.get("routed_in_state"),
                    received_in_state=parsed.get("received_in_state"),
                    answered_in_state=parsed.get("answered_in_state"),
                    in_state_answer_rate_reported=parsed.get("in_state_answer_rate_reported"),
                    abandoned_in_state_count=parsed.get("abandoned_in_state_count"),
                    flowout_to_national_backup_count=parsed.get("flowout_to_national_backup_count"),
                    average_speed_to_answer_seconds=parsed.get("average_speed_to_answer_seconds"),
                    average_talk_time_seconds=parsed.get("average_talk_time_seconds"),
                    parse_status=parsed.get("status", "failed"),
                    parse_note=parsed.get("note", ""),
                )
            )
    return rows


def main() -> None:
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    all_rows: list[ParsedRow] = []
    for path in pdfs:
        all_rows.extend(parse_pdf(path))

    raw = pd.DataFrame([r.__dict__ for r in all_rows])
    if raw.empty:
        raise RuntimeError("No KPI rows parsed from PDFs.")

    raw["month"] = pd.to_datetime(raw["year_month"] + "-01")
    raw["state_month_id"] = raw["state"] + "_" + raw["year_month"]
    raw["in_state_answer_rate_calc"] = raw["answered_in_state"] / raw["routed_in_state"]
    raw["abandoned_in_state_rate"] = raw["abandoned_in_state_count"] / raw["routed_in_state"]
    raw["flowout_to_national_backup_rate"] = raw["flowout_to_national_backup_count"] / raw["routed_in_state"]
    raw["answer_rate_abs_diff"] = (
        raw["in_state_answer_rate_calc"] - raw["in_state_answer_rate_reported"]
    ).abs()

    parsed = raw[raw["parse_status"].eq("parsed")].copy()
    dedup = parsed.sort_values(["state", "month", "page"]).drop_duplicates(["state", "month"], keep="first")
    issue = (
        raw.groupby("year_month")
        .agg(
            rows=("state", "count"),
            parsed=("parse_status", lambda s: int((s == "parsed").sum())),
            states=("state", "nunique"),
            max_answer_rate_diff=("answer_rate_abs_diff", "max"),
        )
        .reset_index()
    )

    save_csv(raw, PDF_CHECKS / "parsed_988_kpi_raw.csv")
    save_csv(issue, PDF_CHECKS / "coverage_by_month.csv")
    sample = dedup.sample(min(30, len(dedup)), random_state=988)[
        [
            "year_month",
            "state",
            "source_pdf",
            "page",
            "raw_row_text",
            "routed_in_state",
            "answered_in_state",
            "in_state_answer_rate_reported",
            "abandoned_in_state_count",
            "flowout_to_national_backup_count",
            "average_speed_to_answer_seconds",
            "average_talk_time_seconds",
        ]
    ].copy()
    sample["manual_validation_status"] = "pending_human_check"
    save_csv(sample, PDF_CHECKS / "validation_sample.csv")

    outcomes = dedup[
        [
            "state",
            "month",
            "year_month",
            "routed_in_state",
            "answered_in_state",
            "in_state_answer_rate_reported",
            "in_state_answer_rate_calc",
            "abandoned_in_state_count",
            "abandoned_in_state_rate",
            "flowout_to_national_backup_count",
            "flowout_to_national_backup_rate",
            "average_speed_to_answer_seconds",
            "average_talk_time_seconds",
            "source_pdf",
            "page",
            "raw_row_text",
        ]
    ].rename(columns={"in_state_answer_rate_calc": "in_state_answer_rate"})

    save_parquet(outcomes, DATA / "outcomes_988_state_month.parquet")
    save_csv(outcomes, DATA / "outcomes_988_state_month.csv")
    append_audit(
        f"Parsed 988 KPI PDFs: {len(outcomes)} state-month rows from {len(pdfs)} PDFs. "
        f"Validation sample written to {rel(PDF_CHECKS / 'validation_sample.csv')}."
    )


if __name__ == "__main__":
    main()

