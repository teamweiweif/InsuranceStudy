# Identification Audit

## Target Parameter

The preferred estimand is the average post-operational-start change in state 988 KPI performance for states that adopted telecom fee funding, compared with not-yet-treated or never-treated state/DC controls.

## Treatment

The primary treatment is FCC-confirmed state 988 telecom fee collection. The preferred operational start is three months after fee collection starts. Actual collection and operational timing are both retained in `data/fee_schedule_state_month.csv`.

## Estimators

- Not-yet-treated cohort/event-time ATT: preferred descriptive causal design for staggered adoption.
- TWFE with state and month fixed effects: diagnostic check, not the headline design.
- Dose-response models: fee cents and FCC-observed annual revenue intensity for 2021-2024.
- Robustness: launch-transition exclusion, early-adopter exclusion, leave-one-treated-state-out, placebo timing.

## Core Diagnostic Facts

- Not-yet-treated answer-rate ATT: 6.77 pp; bootstrap 95% interval [1.69 pp, 13.27 pp].
- TWFE operational-start answer-rate coefficient: 0.68 pp; clustered SE 2.03 pp; p=0.737.
- Placebo timing p-value for the TWFE answer-rate coefficient: 0.808.

## Main Threats

- Fee adoption is not random; high-need or better-organized states may adopt earlier.
- Public monthly staffing/capacity measures are incomplete, so the funding-to-capacity mechanism is proxied by fee revenue and baseline load.
- Nationwide 988 launch and later routing/georouting changes are absorbed by month fixed effects but may have heterogeneous state impacts.
- Treatment timing after 2024 is less well observed because the latest FCC annual fee report covers calendar year 2024.
- February 2025 was absent from the 988 source index snapshot used here.

## Bottom Line

The cohort ATT estimates are policy-relevant and point toward better in-state performance after fee funding, but the TWFE and placebo diagnostics do not support a strong standalone causal headline.
