# Do 988 Telecom Fees Improve Crisis-Line Performance?

## Summary

This audit builds a reproducible state-month panel from official 988 Lifeline KPI PDFs and FCC 988 fee accountability reports. The analysis covers 58 source months from 2021-07-01 through 2026-05-01 and uses a primary state/DC sample of 2936 rows.

The evidence is mixed. The preferred not-yet-treated cohort comparison suggests improvements after fee funding: answer rates rise by 6.77 pp with a bootstrap interval of [1.69 pp, 13.27 pp], flowout falls by -3.75 pp, and abandonment falls by -2.90 pp. Average speed to answer improves by -4.79 seconds, but its interval includes zero.

The simpler TWFE diagnostic is much weaker: the operational-start answer-rate coefficient is 0.68 pp with clustered SE 2.03 pp and p=0.737. A placebo timing exercise for that TWFE coefficient has empirical p=0.808.

## Data

The outcome panel is parsed from official 988 Lifeline state-based monthly reports. Outcomes include in-state routed contacts, answered contacts, answer rate, abandoned contacts, flowout to national backup, speed to answer, and talk time. Treatment timing comes from FCC annual 988 fee reports and official state policy sources. Population denominators come from Census Vintage 2025 state resident population estimates.

## Empirical Strategy

The preferred design compares treated cohorts with not-yet-treated or never-treated states around each operational treatment start. Operational start is coded three months after fee collection begins. The fixed-effect checks include state and month fixed effects with state-clustered standard errors.

## Main Results

| Outcome | Not-yet-treated ATT | Bootstrap 95% interval |
| --- | --- | --- |
| In-state answer rate | 6.77 pp | [1.69 pp, 13.27 pp] |
| Flowout to national backup | -3.75 pp | [-7.19 pp, -0.49 pp] |
| Abandoned rate | -2.90 pp | [-7.08 pp, -0.06 pp] |
| Average speed to answer | -4.79 sec | [-12.57, 0.62] sec |

## Robustness Snapshot

| model | estimate | std_error_cluster | p_value |
| --- | --- | --- | --- |
| drop_early_adopters_va_wa | 0.36 pp | 2.14 pp | 0.869 |
| through_2024_only | -0.64 pp | 2.71 pp | 0.815 |
| include_post2025_monitor_rows | 0.47 pp | 2.07 pp | 0.822 |

## Interpretation

The cohort design points toward operationally meaningful improvements after fee adoption, especially higher in-state answer rates and lower flowout. However, the diagnostic TWFE estimates are small and statistically weak, and placebo timing does not reject chance timing patterns for that specification. The safest claim is that fee-funded states improved relative to not-yet-treated comparisons in the preferred event-time design, not that telecom fees are conclusively causal on their own.

## Limitations

- Fee adoption is policy-selected, not randomized.
- Public monthly staffing/capacity data are incomplete, limiting mechanism tests.
- The 988 source index did not include February 2025 in the snapshot used here.
- Post-2024 policy changes are not fully covered by FCC annual fee revenue reports.
- Manual validation sample rows remain marked for human audit in `temp/pdf_extraction_checks/validation_sample.csv`.
