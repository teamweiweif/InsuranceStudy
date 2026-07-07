# Identification Audit

## Treatment

The causal treatment is entry into the CCBHC Medicaid Demonstration, not ordinary
SAMHSA CCBHC expansion grants. The 2024 selected states are coded separately
from planning-grant states, original demonstration states, CARES-added states,
and the 2026 future cohort.

State-specific start dates are incomplete. Missing 2024-cohort start dates:
AL, NM. Main estimates use 2024 selection as the
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
