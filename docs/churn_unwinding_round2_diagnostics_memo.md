# Churn / Unwinding Round-2 Diagnostics Memo

Last updated: `2026-04-10`

## Purpose

This memo records the second-round diagnostic results for the `SIPP corrected stack + CMS updated renewal outcomes` design.

The question for this round was not:

- can we already claim a publishable causal effect

The question was:

- is this stack now coherent enough to justify a limited next step beyond descriptive diagnostics

## Inputs Used

Core inputs:

- [sipp_2022_corrected_person_month_flags.parquet](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/prototype/sipp_2022_corrected_person_month_flags.parquet)
- [sipp_2023_corrected_person_month_flags.parquet](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/prototype/sipp_2023_corrected_person_month_flags.parquet)
- [sipp_2024_cms_updated_renewal_outcomes_merged.parquet](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/prototype/sipp_2024_cms_updated_renewal_outcomes_merged.parquet)

Round-2 derived objects:

- [sipp_unwinding_feature_stack_2021_2023.parquet](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/sipp_unwinding_feature_stack_2021_2023.parquet)
- [sipp_subgroup_candidate_audit.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/sipp_subgroup_candidate_audit.csv)
- [second_round_timing_matrix_long.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/second_round_timing_matrix_long.csv)
- [second_round_falsification_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/second_round_falsification_summary.csv)
- [second_round_subgroup_stability_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/second_round_subgroup_stability_summary.csv)
- [second_round_gate_summary.json](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/second_round_gate_summary.json)
- [risk_prediction_pilot_metrics.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/risk_prediction_pilot_metrics.csv)
- [hps_unwinding_crosscheck_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/hps_unwinding_crosscheck_summary.csv)
- [nhis_public_validation_feasibility.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/nhis_public_validation_feasibility.csv)

## Reproducibility Check

This round began by rerunning the existing first-round scripts:

- `build_churn_unwinding_first_diagnostics.py`
- `build_churn_unwinding_follow_on_diagnostics.py`

The rerun outputs matched the existing first-round artifacts byte-for-byte on the key summary files. That means the round-2 extension was built on a reproducible first-round base rather than on stale or drifting outputs.

## Subgroup Feature Audit

The new feature stack retained the subgroup families that were stable across `2021-2023`, interpretable, and not too missing among eligible transition rows.

Retained for round 2:

- `age_band`
- `female_group`
- `foreign_born_group`
- `household_child_group`
- `noncitizen_group`
- `pov_band`
- `snap_group`

Dropped because missingness among eligible rows stayed above the `20%` rule:

- `disability_group`
- `employed_group`

Support summary from the built stack:

- total rows: `1,398,627`
- unique persons: `69,933`
- eligible transition rows: `257,950`

## Timing Matrix: What Actually Won

The full timing sweep covered:

- `same`
- `lag1`
- `lead1`
- `lag2` when support was adequate

The strongest raw core-window signals were **not** the safest signals:

- `pending_rate / lead1` had the highest mean signed correlation in the core window
- that is exactly why it is not a safe escalation target by itself
- a lead-driven signal can reflect misalignment rather than a defensible treatment clock

Under the implemented timing-gate rule, the chosen candidate became:

- `manual_renewal_burden / renewal_form_rate / lag1`

Why this one won:

- it was the only gate-eligible exposure variant whose best alignment was the same non-lead alignment in both the core and extended windows
- both windows kept positive mean signed correlations for that alignment

Important caveat:

- this does **not** mean `renewal_form_rate` is the strongest raw signal overall
- it means it is the cleanest candidate under the current rule that rejects lead-only timing stories

## Falsification Result

For the chosen candidate `renewal_form_rate / lag1`, the matched pre-period contrasts were smaller than the `2023` unwinding contrast for both outcomes.

`medicaid_exit_next`

- `2021 pre contrast`: `-0.0008`
- `2022 pre contrast`: `-0.0007`
- `2023 unwinding contrast`: `0.0016`

`medicaid_exit_to_uninsured_next`

- `2021 pre contrast`: `0.0004`
- `2022 pre contrast`: `0.0002`
- `2023 unwinding contrast`: `0.0018`

Interpretation:

- later high-exposure states were **not** already showing comparably large and same-direction gaps in the matched pre-period
- this does not prove causality
- it does remove the most trivial version of the “these states were always worse” objection

## Subgroup Stability Result

The old crude comparator was `state_baseline_tertile`.

That comparator stayed weak:

- mean Spearman rank correlation across outcomes: `-0.5`
- top-risk state tertile did **not** stay the top-risk tertile in `2023`

Two subgroup families did better under the implemented stability rule:

- `pov_band`
- `snap_group`

Why they counted as supporting families:

- their mean stability exceeded the weak state-baseline comparator
- they also preserved the top-risk group for the sharper outcome `medicaid_exit_to_uninsured_next`

Important nuance:

- this is a low but meaningful threshold
- it says “risk ordering is not pure noise”
- it does **not** say subgroup targeting is already publication-ready

Partial but not fully stable families:

- `age_band` is promising for broad exit, but it does not hold the top-risk group for `exit_to_uninsured`
- `female_group`, `foreign_born_group`, `household_child_group`, and `noncitizen_group` are not stable enough yet for escalation claims

## Gate Verdict

The implemented gate summary is:

- `timing_gate = true`
- `falsification_gate = true`
- `stability_gate = true`
- final verdict: `GO_RISK_ONLY`

This verdict should be read narrowly:

- the stack is good enough for a limited risk-prediction pilot
- it is **not** good enough to jump to `DID`, `DML`, or `causal targeting`

## Risk Prediction Pilot

Pilot setup:

- train years: `2021-2022`
- test year: `2023`
- months: `August-November`
- features: retained subgroup families only
- baseline comparator: naive `state baseline risk`

Main results:

| outcome | model | auc | pr_auc | top_decile_capture |
| --- | --- | --- | --- | --- |
| `medicaid_exit_next` | `baseline_state` | `0.4245` | `0.0069` | `0.0859` |
| `medicaid_exit_next` | `logistic` | `0.6756` | `0.0127` | `0.1884` |
| `medicaid_exit_next` | `tree` | `0.6438` | `0.0114` | `0.1629` |
| `medicaid_exit_to_uninsured_next` | `baseline_state` | `0.4567` | `0.0032` | `0.0427` |
| `medicaid_exit_to_uninsured_next` | `logistic` | `0.6483` | `0.0058` | `0.1077` |
| `medicaid_exit_to_uninsured_next` | `tree` | `0.5994` | `0.0051` | `0.0917` |

Interpretation:

- the simple subgroup-based logistic model materially outperforms the naive state baseline
- this supports the narrow claim that there is some usable risk ranking in the current stack
- it does **not** convert the stack into a causal-targeting design

## External Cross-Checks

### HPS

The HPS screen was intentionally lightweight and late-2023 only.

Results for the chosen exposure `renewal_form_rate / lag1`:

- `current_medicaid_rate`: negative correlation and negative high-minus-low contrast
- `public_coverage_rate`: negative correlation and negative high-minus-low contrast
- `uninsured_rate`: essentially flat to slightly negative, which is **not** the expected sign

Interpretation:

- HPS provides a weak external echo for lower current coverage in higher-burden states
- HPS does **not** currently reinforce the sharper uninsured-loss story
- that keeps the external validation only partial

### NHIS

Public NHIS adult files retain useful insurance and access variables, but they do not expose public state geography in the audited years.

That means:

- NHIS can still support national or region-level descriptive appendix work
- NHIS cannot currently provide the needed `state-period` merge for this unwinding design

## Bottom Line

What got stronger in this round:

- the subgroup layer is now real rather than hypothetical
- the design no longer depends only on crude state tertiles
- a nontrivial risk-ranking signal exists

What still blocks causal escalation:

- the timing winner is selected under a permissive rule and is not the strongest raw signal overall
- the leading alternative signals remain timing-fragile
- external validation is only partial
- the subgroup stability win is enough for risk work, not enough for strong targeting claims

## Allowed Next Step

Allowed next step:

- refine the `risk / prioritization` line using the current stack

Not yet allowed:

- `DID`
- `event study`
- `DML`
- `causal ML`
- `policy targeting` claims framed as causal or welfare-improving

If a future agent wants to escalate beyond risk work, it should first show either:

- stronger timing discipline for the selected burden proxy, or
- a more convincing external or quasi-experimental validation layer
