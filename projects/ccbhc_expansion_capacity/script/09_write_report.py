from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline_utils import DATA, REPORT, RESULT, TEMP, append_note, write_text


def coef_sentence(path: Path, outcome: str, strategy: str = "all_non_original_non_2024_controls") -> str:
    if not path.exists():
        return "No estimate available."
    df = pd.read_csv(path)
    sub = df[(df.get("outcome") == outcome) & (df.get("strategy") == strategy)]
    if sub.empty:
        return "No estimate available."
    r = sub.iloc[0]
    return f"{r['coef']:.3f} (SE {r['se']:.3f}, p={r['p']:.3f}, N={int(r['n'])})"


def main() -> None:
    inv = pd.read_csv(TEMP / "source_inventory.csv")
    state = pd.read_parquet(DATA / "analysis_main_state_year.parquet")
    did = pd.read_csv(RESULT / "table_main_state_did.csv") if (RESULT / "table_main_state_did.csv").exists() else pd.DataFrame()
    es = pd.read_csv(RESULT / "table_event_study_state.csv") if (RESULT / "table_event_study_state.csv").exists() else pd.DataFrame()
    synth = pd.read_csv(RESULT / "synthetic_control_state_summary.csv") if (RESULT / "synthetic_control_state_summary.csv").exists() else pd.DataFrame()

    observed_years = sorted(state.loc[state["facility_count"].notna(), "year"].unique().astype(int).tolist())
    treated_start_missing = state[(state["treated_state_2024"] == 1) & (state["year"] == 2024) & (state["demo_start_date"].fillna("") == "")]
    start_missing_states = ", ".join(sorted(treated_start_missing["state"].unique()))

    readme = f"""# CCBHC Expansion Capacity Workspace

This workspace evaluates whether the 2024 BSCA-authorized CCBHC Medicaid
Demonstration expansion increased behavioral-health capacity.

Run from the project root:

```bash
bash script/run_all.sh
```

On Windows without Bash or Make:

```powershell
powershell -ExecutionPolicy Bypass -File script/run_all.ps1
```

Main clean data are in `data/`, generated results are in `result/`, source
snapshots and raw downloads are in `temp/`, and human-readable outputs are in
`report/`.

Observed N-SUMHSS years in this build: {observed_years}. The key limitation is
that 2025 N-SUMHSS public-use data are not available in this build, and 2024 is
only a partial/early implementation year for several selected states.
"""
    write_text(REPORT / "README.md", readme)

    audit = f"""# Identification Audit

## Treatment

The causal treatment is entry into the CCBHC Medicaid Demonstration, not ordinary
SAMHSA CCBHC expansion grants. The 2024 selected states are coded separately
from planning-grant states, original demonstration states, CARES-added states,
and the 2026 future cohort.

State-specific start dates are incomplete. Missing 2024-cohort start dates:
{start_missing_states or "none"}. Main estimates use 2024 selection as the
earliest policy shock and should not be read as effects of verified PPS payment.

## Main Design

State-year DID/event-study models compare 2024 selected states to alternative
state control pools over 2021-2024, with state and year fixed effects and
state-clustered standard errors.

## Diagnostics

- Raw trends are saved in `result/raw_trend_*.png`.
- Event-study estimates are saved in `result/table_event_study_state.csv`.
- Balance diagnostics are saved in `result/balance_table_control_strategies.csv`
  and `result/balance_table_matched_donors.csv`.
- Placebo year, placebo outcome, leave-one-treated-state-out, DDD, matched DID,
  and synthetic-control diagnostics are saved in `result/`.

## Threats

Selection bias is severe: states chose to plan for, apply to, and were selected
into the demonstration based on readiness and policy infrastructure. The public
post period is too short, county CCBHC exposure is not reconstructed, and many
states began actual implementation in 2025 rather than 2024.

## Gate Decision

The identification gate does not pass for a publishable causal claim. The
workspace is reproducible and useful for monitoring early capacity measures, but
the current public data support a diagnostic/no-go judgment rather than a causal
paper.
"""
    write_text(REPORT / "identification_audit.md", audit)

    final = f"""# Final Report

## Executive Summary

Go/no-go judgment: **NO-GO for a credible causal paper today.** The 2024 CCBHC
Medicaid Demonstration expansion is a promising policy shock, but public data
available in this build do not yet support a defensible causal estimate of local
capacity effects. The main public facility source, N-SUMHSS, is available for
2021-2024 and suppresses county geography. Several selected states did not begin
verified implementation until 2025, so the only observed post year is at best an
announcement/partial-implementation year.

## Policy Background

CCBHCs are certified clinics intended to provide comprehensive mental-health and
substance-use services, including crisis services, outpatient care, care
coordination, peer/family support, primary-care screening, and services
regardless of ability to pay. The treatment studied here is Medicaid
Demonstration entry and PPS/certification infrastructure, not ordinary CCBHC
expansion grants.

## Data Sources and Coverage

The source inventory is `temp/source_inventory.csv`. The reproducible build
archives official federal policy pages, targeted state evidence, N-SUMHSS
2021-2024 PUFs and codebooks, and Census ACS 2019-2024 county covariates.
TEDS-A, CDC WONDER, AHRF, and HPSA are documented as access records but not used
in the main causal models.

N-SUMHSS contains facility-level service indicators and state, but no county,
FIPS, address, or coordinates. This makes county-year DID infeasible from the
PUF.

## Treatment Construction

The 2024 selected states are Alabama, Illinois, Indiana, Iowa, Kansas, Maine,
New Hampshire, New Mexico, Rhode Island, and Vermont. The 2026 selected states
are Alaska, Colorado, Hawaii, Louisiana, Maryland, Mississippi, Montana, North
Dakota, Washington, and West Virginia. Start dates are coded only when state
evidence was found; otherwise they remain missing rather than imputed.

## Outcomes

Primary state-year outcomes are facility density and counts per 100,000
population for crisis intervention, MOUD, integrated primary care, care
coordination/case management, sliding-fee or low-payment access, and a combined
targeted service index. A state-year-service panel classifies services as
directly targeted, related, or weakly targeted for DDD checks.

## Identification Strategy

The build estimates state-year DID/event-study models with state and year fixed
effects, matched-donor sensitivity, synthetic-control attempts, placebo year and
placebo outcome checks, leave-one-treated-state-out sensitivity, and a DDD
targeted-service design.

## Main Results

For the all-non-original control strategy, the DID estimate for targeted service
density is {coef_sentence(RESULT / "table_main_state_did.csv", "targeted_services_per100k")}.
For crisis-service density it is {coef_sentence(RESULT / "table_main_state_did.csv", "crisis_intervention_per100k")}.
These numbers are diagnostic only. The post period is a single year and does not
line up cleanly with actual demonstration starts.

The DDD estimate is reported in `result/table_ddd_service_category.csv`. It is
useful as a mechanism check: targeted services should move more than weakly
targeted services if the policy channel is real. It is not enough to rescue the
design.

## Robustness and Falsification

The pipeline attempts planning-grant controls, not-yet-treated controls, nearest
matched donors, propensity overlap diagnostics, placebo treatment year 2023,
placebo outcome using sign-language services, and leave-one-treated-state-out
estimates. These checks are informative for future design selection but cannot
solve the short post-period and unobserved county exposure problems.

## Synthetic-Control Findings

Synthetic controls are attempted for targeted service density using 2021-2023
pre-period outcomes and 2024 gaps. The design is fragile because three pre-years
are too few for strong pre-fit assessment and one post year cannot distinguish
implementation from noise or reporting shifts. Summary results are in
`result/synthetic_control_state_summary.csv`.

## Heterogeneity

The build tests whether early changes differ in high-poverty, low-MOUD, or
low-crisis-capacity states. These are exploratory state-level moderation checks,
not policy targeting rules.

## Limitations

- No 2025 N-SUMHSS PUF is available in this build.
- N-SUMHSS PUF suppresses county geography.
- CCBHC site status, certification dates, and PPS payment dates are not observed
  at the facility level.
- Demonstration selection is endogenous to state readiness.
- TEDS-A and mortality outcomes have no credible post-treatment window for this
  early evaluation.

## Judgment

Preserve the workspace as an audit-ready monitoring package, but do not write the
causal paper yet. The project becomes viable after 2025 and preferably 2026
N-SUMHSS PUFs are available, state start dates are fully verified, and a
historical CCBHC site panel can be built or obtained.

## Next Steps

1. Verify exact state demonstration start/payment dates for all 2024 states.
2. Obtain historical CCBHC site lists with county and certification/payment dates.
3. Add N-SUMHSS 2025 when released.
4. Re-run county and facility designs if geography/status become available.
5. Use TEDS-A and mortality only after a longer post period exists.
"""
    write_text(REPORT / "final_report.md", final)

    append_note("Phase 9: Final judgment", [
        "Applied econ-writing guidance after empirical outputs existed: result first, concrete limitations, no overclaiming.",
        "Final judgment is no-go for a causal paper today, preserve workspace for future post-period updates.",
    ])


if __name__ == "__main__":
    main()
