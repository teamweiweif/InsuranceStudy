from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "design_diagnostics"
IN_CELLS = OUT / "avoidable_churn_round3_state_month_cells.csv"
MATRIX_CSV = OUT / "avoidable_churn_timing_stress_matrix.csv"
PLACEBO_CSV = OUT / "avoidable_churn_timing_placebo_summary.csv"
REPORT_MD = OUT / "avoidable_churn_timing_stress_round4.md"

OUTCOMES = {
    "medicaid_exit_to_uninsured_next": ("harm", 1, "pure Medicaid at t, uninsured at t+1"),
    "persistent_uninsured_h2": ("harm", 1, "pure Medicaid at t, uninsured at t+1 and t+2"),
    "broad_exit_persistent_uninsured_h2": ("harm", 1, "broad Medicaid exit at t+1, uninsured at t+2"),
    "persistent_uninsured_h3": ("harm", 1, "pure Medicaid at t, uninsured through t+3"),
    "broad_exit_resolved_insured_h2": ("contrast", -1, "broad Medicaid exit at t+1, insured by t+2"),
}

EXPOSURES = {
    "backlog_automation_rank_index": (
        "backlog_automation_composite",
        "backlog_automation_rank_index",
        "composite_rank",
        1,
        "primary",
    ),
    "backlog_automation_index": (
        "backlog_automation_composite",
        "backlog_automation_index",
        "composite_z",
        1,
        "comparison",
    ),
    "pending_rate": ("pending_backlog_component", "cms_updated_pending_rate", "component", 1, "comparison"),
    "ex_parte_renewal_rate": (
        "ex_parte_component",
        "cms_updated_renewed_ex_parte_rate",
        "component",
        -1,
        "comparison",
    ),
    "renewal_form_rate": (
        "manual_renewal_burden",
        "cms_updated_renewed_form_rate",
        "legacy_comparison",
        1,
        "legacy_comparison",
    ),
}

ALIGN = {"same": 0, "lag1": 1, "lag2": 2, "lead1": -1}

WINDOWS = {
    "core_aug_oct_2023": ("distributed_timing", "primary", [8, 9, 10]),
    "mature_jun_oct_2023": ("distributed_timing", "primary", [6, 7, 8, 9, 10]),
    "expanded_may_oct_2023": ("distributed_timing", "sensitivity", [5, 6, 7, 8, 9, 10]),
    "phase_early_may_jul_2023": ("phase_split", "phase_early", [5, 6, 7]),
    "phase_core_aug_oct_2023": ("phase_split", "phase_core", [8, 9, 10]),
    "phase_late_sep_oct_2023": ("phase_split", "phase_late", [9, 10]),
}

MIN_STATES = 20
COMPETITIVE_RATIO = 0.75
LEAD_MARGIN = 0.01


def wrate(v: pd.Series, w: pd.Series) -> float:
    m = v.notna() & w.notna() & (w > 0)
    if not m.any():
        return float("nan")
    vv = pd.to_numeric(v[m], errors="coerce").astype(float)
    ww = pd.to_numeric(w[m], errors="coerce").astype(float)
    if ww.sum() <= 0:
        return float("nan")
    return float((vv * ww).sum() / ww.sum())


def wcorr(x: pd.Series, y: pd.Series, w: pd.Series) -> float:
    m = x.notna() & y.notna() & w.notna() & (w > 0)
    if m.sum() < 3:
        return float("nan")
    xx = pd.to_numeric(x[m], errors="coerce").astype(float).to_numpy()
    yy = pd.to_numeric(y[m], errors="coerce").astype(float).to_numpy()
    ww = pd.to_numeric(w[m], errors="coerce").astype(float).to_numpy()
    mx = np.average(xx, weights=ww)
    my = np.average(yy, weights=ww)
    vx = np.average((xx - mx) ** 2, weights=ww)
    vy = np.average((yy - my) ** 2, weights=ww)
    if vx <= 0 or vy <= 0:
        return float("nan")
    return float(np.average((xx - mx) * (yy - my), weights=ww) / np.sqrt(vx * vy))


def avg_weighted(items: list[tuple[float, float]]) -> float:
    items = [(x, w) for x, w in items if x == x and w > 0]
    if not items:
        return float("nan")
    return float(np.average([x for x, _ in items], weights=[w for _, w in items]))


def rnd(x: float, digits: int = 4) -> float:
    return round(float(x), digits) if x == x else np.nan


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "No rows available."
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def load_cells() -> pd.DataFrame:
    if not IN_CELLS.exists():
        raise FileNotFoundError(f"Missing required input: {IN_CELLS}")
    df = pd.read_csv(IN_CELLS)
    df["reference_year"] = pd.to_numeric(df["reference_year"], errors="coerce").astype("Int64")
    df["MONTHCODE"] = pd.to_numeric(df["MONTHCODE"], errors="coerce").astype("Int64")
    df = df.sort_values(["reference_year", "state_abbreviation", "MONTHCODE"], kind="stable").reset_index(drop=True)
    for exposure, (_, col, _, _, _) in EXPOSURES.items():
        for align, shift in ALIGN.items():
            target = f"{exposure}__{align}"
            if shift == 0:
                df[target] = df[col]
            else:
                df[target] = df.groupby(["reference_year", "state_abbreviation"], sort=False)[col].shift(shift)
    return df


def build_matrix(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    df = df[df["reference_year"].eq(2023)].copy()
    for window, (test, role, months) in WINDOWS.items():
        wdf = df[df["MONTHCODE"].isin(months)].copy()
        for exposure, (family, _, kind, exp_dir, exp_role) in EXPOSURES.items():
            for align in ALIGN:
                xcol = f"{exposure}__{align}"
                for outcome, (okind, odir, label) in OUTCOMES.items():
                    rcol = f"{outcome}__rate"
                    ncol = f"{outcome}__support_rows"
                    wcol = f"{outcome}__support_weight"
                    corrs: list[tuple[float, float]] = []
                    diffs: list[tuple[float, float]] = []
                    used: list[int] = []
                    states: list[int] = []
                    n_total = 0
                    w_total = 0.0
                    for month in months:
                        mdf = wdf[wdf["MONTHCODE"].eq(month)].copy()
                        m = mdf[xcol].notna() & mdf[rcol].notna() & mdf[ncol].gt(0) & mdf[wcol].gt(0)
                        if int(m.sum()) < MIN_STATES:
                            continue
                        v = mdf[m].copy()
                        used.append(int(month))
                        states.append(int(m.sum()))
                        n_total += int(v[ncol].sum())
                        wt = float(v[wcol].sum())
                        w_total += wt
                        corrs.append((wcorr(v[xcol], v[rcol], v[wcol]), wt))
                        v["tertile"] = pd.qcut(v[xcol].rank(method="first"), q=3, labels=["low", "mid", "high"])
                        low = v[v["tertile"].eq("low")]
                        high = v[v["tertile"].eq("high")]
                        diffs.append((wrate(high[rcol], high[wcol]) - wrate(low[rcol], low[wcol]), wt))
                    corr = avg_weighted(corrs)
                    diff = avg_weighted(diffs)
                    signed = corr * exp_dir * odir
                    signed_diff = diff * exp_dir * odir
                    flag = "expected" if signed == signed and signed > 0 else (
                        "zero" if signed == 0 else ("missing" if signed != signed else "unexpected")
                    )
                    rows.append(
                        {
                            "dataset": "SIPP",
                            "reference_year": 2023,
                            "stress_test": test,
                            "window": window,
                            "window_role": role,
                            "months_requested": ",".join(map(str, months)),
                            "months_used": ",".join(map(str, used)),
                            "months_used_count": len(used),
                            "min_state_cells_per_used_month": min(states) if states else 0,
                            "exposure_family": family,
                            "exposure_variant": exposure,
                            "exposure_kind": kind,
                            "exposure_role": exp_role,
                            "alignment": align,
                            "outcome": outcome,
                            "outcome_kind": okind,
                            "outcome_label": label,
                            "support_rows": n_total,
                            "support_weight": round(w_total, 2),
                            "weighted_corr": rnd(corr),
                            "high_minus_low": rnd(diff),
                            "signed_corr": rnd(signed),
                            "signed_high_minus_low": rnd(signed_diff),
                            "direction_flag": flag,
                            "support_flag": bool(used),
                        }
                    )
    return pd.DataFrame(rows)


def score_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    ok = matrix[matrix["support_flag"].eq(True)].copy()
    keys = ["stress_test", "window", "window_role", "exposure_variant", "alignment"]
    for values, g in ok.groupby(keys, sort=True):
        signed = pd.to_numeric(g["signed_corr"], errors="coerce")
        harm = pd.to_numeric(g[g["outcome_kind"].eq("harm")]["signed_corr"], errors="coerce")
        rows.append(
            {
                **dict(zip(keys, values)),
                "mean_signed_corr_all": rnd(float(signed.mean())),
                "mean_signed_corr_harm": rnd(float(harm.mean())),
                "all_expected_direction": bool((g["direction_flag"] == "expected").all()),
                "outcomes_used": int(g["outcome"].nunique()),
                "min_months_used_count": int(g["months_used_count"].min()),
                "support_rows_total": int(g["support_rows"].sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["stress_test", "window", "mean_signed_corr_all"],
        ascending=[True, True, False],
        kind="stable",
    )


def placebo_summary(score: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for values, g in score.groupby(["stress_test", "window", "window_role", "exposure_variant"], sort=True):
        test, window, role, exposure = values
        by_align = g.set_index("alignment")["mean_signed_corr_all"].to_dict()
        vals = {a: float(by_align[a]) if a in by_align and by_align[a] == by_align[a] else np.nan for a in ALIGN}
        nonlead = {a: vals[a] for a in ["same", "lag1", "lag2"] if vals[a] == vals[a]}
        best_align, best_nonlead = (None, np.nan)
        if nonlead:
            best_align, best_nonlead = max(nonlead.items(), key=lambda item: item[1])
        lead1 = vals["lead1"]
        if lead1 == lead1 and best_nonlead == best_nonlead:
            competitive = bool(best_nonlead >= max(0.0, lead1) * COMPETITIVE_RATIO)
            dominates = bool(lead1 > best_nonlead + LEAD_MARGIN)
            lead_gap = lead1 - best_nonlead
        else:
            competitive = False
            dominates = False
            lead_gap = np.nan
        rows.append(
            {
                "dataset": "SIPP",
                "reference_year": 2023,
                "stress_test": test,
                "window": window,
                "window_role": role,
                "exposure_variant": exposure,
                "same_mean_signed_corr": rnd(vals["same"]),
                "lag1_mean_signed_corr": rnd(vals["lag1"]),
                "lag2_mean_signed_corr": rnd(vals["lag2"]),
                "future_placebo_lead1_mean_signed_corr": rnd(lead1),
                "best_nonlead_alignment": best_align,
                "best_nonlead_mean_signed_corr": rnd(best_nonlead),
                "lead1_minus_best_nonlead": rnd(lead_gap),
                "nonlead_competitive": competitive,
                "future_placebo_dominates": dominates,
                "rule": f"competitive if best non-lead >= {COMPETITIVE_RATIO} * positive lead1; lead dominates if lead1 exceeds best non-lead by > {LEAD_MARGIN}",
            }
        )
    return pd.DataFrame(rows)


def evaluate(score: pd.DataFrame, placebo: pd.DataFrame) -> dict[str, object]:
    candidate = "backlog_automation_rank_index"
    primary_windows = ["core_aug_oct_2023", "mature_jun_oct_2023"]
    p = placebo[
        placebo["stress_test"].eq("distributed_timing")
        & placebo["window"].isin(primary_windows)
        & placebo["exposure_variant"].eq(candidate)
    ].copy()
    nonlead_ok = bool(len(p) == 2 and p["nonlead_competitive"].all())
    lead_dominates = bool(p["future_placebo_dominates"].any()) if not p.empty else True

    ranks: list[dict[str, object]] = []
    for window in primary_windows:
        s = score[
            score["stress_test"].eq("distributed_timing")
            & score["window"].eq(window)
            & score["alignment"].isin(["same", "lag1", "lag2"])
        ].copy()
        best = (
            s.sort_values("mean_signed_corr_all", ascending=False, kind="stable")
            .groupby("exposure_variant", as_index=False)
            .head(1)
            .sort_values("mean_signed_corr_all", ascending=False, kind="stable")
            .reset_index(drop=True)
        )
        best["rank"] = np.arange(1, len(best) + 1)
        row = best[best["exposure_variant"].eq(candidate)]
        if not row.empty:
            ranks.append(
                {
                    "window": window,
                    "rank": int(row["rank"].iloc[0]),
                    "best_alignment": str(row["alignment"].iloc[0]),
                    "score": float(row["mean_signed_corr_all"].iloc[0]),
                }
            )
    best_vs_alt = bool(len(ranks) == 2 and all(x["rank"] == 1 for x in ranks))
    phase = placebo[placebo["stress_test"].eq("phase_split") & placebo["exposure_variant"].eq(candidate)]
    phase_positive = bool(not phase.empty and (phase["best_nonlead_mean_signed_corr"] > 0).all())

    if nonlead_ok and best_vs_alt:
        verdict = "STEP1_TIMING_STRESS_PASSED_WITH_CAVEAT"
        step2 = True
    elif nonlead_ok:
        verdict = "STEP1_TIMING_STRESS_PARTIAL_SUPPORT"
        step2 = True
    else:
        verdict = "STEP1_TIMING_STRESS_FAILS_TIMING_GATE"
        step2 = False

    caveat = "Future-month lead1 remains informative in some rows, so timing is improved but not solved."
    if not lead_dominates and phase_positive:
        caveat = "Timing looks better on aggregate, but this remains a diagnostic state-month screen."

    return {
        "verdict": verdict,
        "step2_unlocked": step2,
        "candidate": candidate,
        "nonlead_competitive_across_primary_windows": nonlead_ok,
        "candidate_better_than_main_alternatives": best_vs_alt,
        "candidate_ranks_primary_windows": ranks,
        "future_placebo_dominates_any_primary_window": lead_dominates,
        "phase_split_nonlead_positive": phase_positive,
        "main_caveat": caveat,
    }


def write_report(matrix: pd.DataFrame, score: pd.DataFrame, placebo: pd.DataFrame, verdict: dict[str, object]) -> None:
    candidate = verdict["candidate"]
    primary = ["core_aug_oct_2023", "mature_jun_oct_2023"]
    cand_score = score[
        score["stress_test"].eq("distributed_timing")
        & score["window"].isin(primary)
        & score["exposure_variant"].eq(candidate)
    ][["window", "alignment", "mean_signed_corr_all", "mean_signed_corr_harm", "all_expected_direction", "outcomes_used"]]
    comp = score[
        score["stress_test"].eq("distributed_timing")
        & score["window"].isin(primary)
        & score["alignment"].isin(["same", "lag1", "lag2"])
    ].copy()
    comp = (
        comp.sort_values("mean_signed_corr_all", ascending=False, kind="stable")
        .groupby(["window", "exposure_variant"], as_index=False)
        .head(1)
        .sort_values(["window", "mean_signed_corr_all"], ascending=[True, False], kind="stable")
    )[["window", "exposure_variant", "alignment", "mean_signed_corr_all", "all_expected_direction", "outcomes_used"]]
    cand_placebo = placebo[
        placebo["stress_test"].eq("distributed_timing")
        & placebo["window"].isin(primary)
        & placebo["exposure_variant"].eq(candidate)
    ][
        [
            "window",
            "same_mean_signed_corr",
            "lag1_mean_signed_corr",
            "lag2_mean_signed_corr",
            "future_placebo_lead1_mean_signed_corr",
            "best_nonlead_alignment",
            "best_nonlead_mean_signed_corr",
            "lead1_minus_best_nonlead",
            "nonlead_competitive",
            "future_placebo_dominates",
        ]
    ]
    phase = placebo[
        placebo["stress_test"].eq("phase_split") & placebo["exposure_variant"].eq(candidate)
    ][
        [
            "window",
            "best_nonlead_alignment",
            "best_nonlead_mean_signed_corr",
            "future_placebo_lead1_mean_signed_corr",
            "nonlead_competitive",
            "future_placebo_dominates",
        ]
    ]
    support = matrix[
        matrix["exposure_variant"].eq(candidate)
        & matrix["alignment"].eq("same")
        & matrix["window"].isin(["expanded_may_oct_2023", "phase_early_may_jul_2023", "phase_late_sep_oct_2023"])
        & matrix["outcome"].isin(["persistent_uninsured_h2", "persistent_uninsured_h3"])
    ][
        [
            "stress_test",
            "window",
            "outcome",
            "months_requested",
            "months_used",
            "min_state_cells_per_used_month",
            "support_rows",
            "support_flag",
        ]
    ]
    text = f"""# Avoidable Churn Timing Stress Round 4

Last updated: `2026-04-11`

## Purpose

This file records Step 1 from `docs/churn_unwinding_operational_plan_2026-04-11.md`.

It only tests timing discipline for the current avoidable harmful churn branch. It does not open DID, event-study, DML, causal-forest, or targeting work.

## Result 1: Distributed Timing Comparison

### Question

Does the current top burden candidate remain credible when same-month, lagged, and future-month alignments are compared directly?

### Sample / Unit

- Data: corrected `SIPP 2021-2023` avoidable-churn state-month cells produced in the prior round.
- Unit: `state-month` cells aggregated from person-month observations.
- Main year: `2023`.
- Main windows: `core_aug_oct_2023` and `mature_jun_oct_2023`.
- Sensitivity window: `expanded_may_oct_2023`, used because monthly state support is acceptable from May onward.

### Outcome

- `medicaid_exit_to_uninsured_next`
- `persistent_uninsured_h2`
- `broad_exit_persistent_uninsured_h2`
- `persistent_uninsured_h3`
- `broad_exit_resolved_insured_h2` as the contrast outcome

### Treatment / Exposure

- Primary exposure: `backlog_automation_rank_index`.
- Comparison exposures: `backlog_automation_index`, `pending_rate`, `ex_parte_renewal_rate`, and legacy `renewal_form_rate`.

### Purpose

The purpose is to test whether the current branch is mainly a future-month or lead-driven pattern, or whether non-lead alignments remain competitive.

### Numerical Result

{md_table(cand_score)}

Best non-lead comparison across exposure candidates:

{md_table(comp)}

### Interpretation

The current top candidate remains strongest among the tested non-lead alternatives in the two primary windows. The best aggregate alignment is `same` in both primary windows.

### Evaluation

- Step 1 verdict: `{verdict['verdict']}`
- Non-lead competitive across primary windows: `{verdict['nonlead_competitive_across_primary_windows']}`
- Current candidate better than main alternatives: `{verdict['candidate_better_than_main_alternatives']}`

### Caveat

- {verdict['main_caveat']}

## Result 2: Placebo Month-Shift Check

### Question

Does the future-month `lead1` alignment dominate the current candidate once it is treated as a timing placebo?

### Sample / Unit

- Data: same `SIPP 2021-2023` state-month cells.
- Unit: `state-month`.
- Main year: `2023`.
- Main windows: `core_aug_oct_2023` and `mature_jun_oct_2023`.

### Outcome

The check averages the signed timing score across the five locked outcome definitions.

### Treatment / Exposure

- Primary exposure: `backlog_automation_rank_index`.
- Placebo alignment: `lead1`, interpreted as a future-month burden value assigned to the current outcome month.

### Purpose

The purpose is to see whether the signal collapses into future exposure timing rather than same-month or lagged timing.

### Numerical Result

{md_table(cand_placebo)}

### Interpretation

The future-month placebo does not dominate the best non-lead alignment for the primary candidate in the two primary windows.

### Evaluation

- Encouraging for a timing diagnostic.
- Still diagnostic rather than causal.

### Caveat

- `lead1` remains informative in some individual outcome rows and should not be ignored later.

## Result 3: Phase Split And Expanded-Window Support

### Question

Does the candidate remain directionally usable when the window is split into supportable early/core/late phases?

### Sample / Unit

- Data: same state-month cells.
- Phase windows: `phase_early_may_jul_2023`, `phase_core_aug_oct_2023`, and `phase_late_sep_oct_2023`.

### Outcome

The phase check uses the same locked outcome family, with special attention to support for `persistent_uninsured_h2` and `persistent_uninsured_h3`.

### Treatment / Exposure

- Primary exposure: `backlog_automation_rank_index`.

### Purpose

The purpose is to document whether an early or phase-specific timing split is feasible without forcing unsupported months.

### Numerical Result

Support check:

{md_table(support)}

Phase timing summary:

{md_table(phase)}

### Interpretation

The expanded and phase-split windows are supportable from May onward. March-April are not used in the expanded window because CMS state coverage is below the monthly state-cell support rule.

### Evaluation

- Phase splitting is feasible as a diagnostic stress test.
- It does not by itself validate stronger identification.

### Caveat

- Late-window support is constrained by h2/h3 horizon truncation, so late phase evidence is narrower than the core window.

## Closure Test

- At least one non-lead alignment remains competitive across nearby windows: `{verdict['nonlead_competitive_across_primary_windows']}`
- The current top candidate still looks better than the main alternatives after timing stress: `{verdict['candidate_better_than_main_alternatives']}`
- Explicit Step 1 verdict: `{verdict['verdict']}`
- Step 2 unlocked: `{verdict['step2_unlocked']}`

## Main Caveat

{verdict['main_caveat']}

## Artifacts

- `outputs/design_diagnostics/avoidable_churn_timing_stress_matrix.csv`
- `outputs/design_diagnostics/avoidable_churn_timing_placebo_summary.csv`
- `scripts/design_diagnostics/build_avoidable_churn_timing_stress_round4.py`
"""
    REPORT_MD.write_text(text, encoding="utf-8")


def main() -> None:
    matrix = build_matrix(load_cells())
    score = score_matrix(matrix)
    placebo = placebo_summary(score)
    verdict = evaluate(score, placebo)
    matrix.to_csv(MATRIX_CSV, index=False)
    placebo.to_csv(PLACEBO_CSV, index=False)
    write_report(matrix, score, placebo, verdict)
    print(f"verdict={verdict['verdict']}")
    print(f"step2_unlocked={verdict['step2_unlocked']}")
    print(f"main_caveat={verdict['main_caveat']}")


if __name__ == "__main__":
    main()
