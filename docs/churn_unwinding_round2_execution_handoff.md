# Churn / Unwinding Round-2 Execution Handoff

Last updated: `2026-04-11`

## Purpose

This is the handoff note for the unattended round that implemented the planned `design diagnostics first` extension on the `SIPP + CMS unwinding` stack.

Read this together with:

1. [churn_unwinding_administrative_burden_memo.md](churn_unwinding_administrative_burden_memo.md)
2. [churn_unwinding_round2_diagnostics_memo.md](churn_unwinding_round2_diagnostics_memo.md)
3. [churn_unwinding_paper_strategy_memo.md](churn_unwinding_paper_strategy_memo.md)
4. [churn_unwinding_progress_record.md](churn_unwinding_progress_record.md)
5. [../outputs/design_diagnostics/churn_unwinding_second_round_diagnostics.md](../outputs/design_diagnostics/churn_unwinding_second_round_diagnostics.md)
6. [../outputs/design_diagnostics/risk_prediction_pilot.md](../outputs/design_diagnostics/risk_prediction_pilot.md)

## What Was Actually Run

### Reproducibility and base audit

Reran the existing first-round diagnostics:

- `scripts/design_diagnostics/build_churn_unwinding_first_diagnostics.py`
- `scripts/design_diagnostics/build_churn_unwinding_follow_on_diagnostics.py`

Outcome:

- key first-round summary files matched the existing outputs byte-for-byte

### New feature-stack build

Ran:

- `scripts/design_diagnostics/build_sipp_unwinding_feature_stack.py`

Outputs:

- [sipp_unwinding_feature_stack_2021_2023.parquet](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/sipp_unwinding_feature_stack_2021_2023.parquet)
- [sipp_subgroup_candidate_audit.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/sipp_subgroup_candidate_audit.csv)
- [sipp_subgroup_candidate_audit.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/sipp_subgroup_candidate_audit.md)

### New second-round diagnostics

Ran:

- `scripts/design_diagnostics/build_churn_unwinding_second_round_diagnostics.py`

Outputs:

- [second_round_timing_matrix_long.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/second_round_timing_matrix_long.csv)
- [second_round_highlow_matrix_long.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/second_round_highlow_matrix_long.csv)
- [second_round_falsification_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/second_round_falsification_summary.csv)
- [second_round_subgroup_stability_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/second_round_subgroup_stability_summary.csv)
- [second_round_gate_summary.json](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/second_round_gate_summary.json)
- [churn_unwinding_second_round_diagnostics.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/churn_unwinding_second_round_diagnostics.md)

### Risk pilot

Installed:

- `scikit-learn`

Ran:

- `scripts/design_diagnostics/run_churn_unwinding_risk_pilot.py`

Outputs:

- [risk_prediction_pilot_metrics.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/risk_prediction_pilot_metrics.csv)
- [risk_prediction_pilot_calibration_by_decile.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/risk_prediction_pilot_calibration_by_decile.csv)
- [risk_prediction_pilot_group_calibration.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/risk_prediction_pilot_group_calibration.csv)
- [risk_prediction_pilot.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/risk_prediction_pilot.md)

### Lightweight external checks

Ran:

- `scripts/design_diagnostics/build_hps_nhis_cross_checks.py`

Outputs:

- [hps_unwinding_crosscheck_summary.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/hps_unwinding_crosscheck_summary.csv)
- [hps_unwinding_crosscheck.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/hps_unwinding_crosscheck.md)
- [nhis_public_validation_feasibility.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/nhis_public_validation_feasibility.csv)
- [nhis_public_validation_feasibility.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/design_diagnostics/nhis_public_validation_feasibility.md)

## Key Decisions Made In This Round

### Mechanism language reset

Locked framing:

- use `administrative renewal burden` as the umbrella mechanism

Do not default to:

- `procedural friction is already proven to be the single dominant channel`

### Timing decision

Gate-selected exposure:

- `manual_renewal_burden / renewal_form_rate / lag1`

Why:

- it satisfied the implemented non-lead cross-window timing rule

What was **not** chosen:

- `pending_rate / lead1`
  - stronger raw core signal, but too timing-fragile
- `ex_parte_renewal_rate`
  - substantively interesting, but its preferred alignment changed across windows

### Subgroup decision

Retained subgroup families:

- `age_band`
- `female_group`
- `foreign_born_group`
- `household_child_group`
- `noncitizen_group`
- `pov_band`
- `snap_group`

Dropped from round-2 use:

- `employed_group`
- `disability_group`

Reason:

- missingness among eligible rows remained above the round rule

## Branches That Were Explicitly Rejected

Rejected for this round:

- escalating directly to `DID`
- escalating directly to `event study`
- escalating directly to `DML`
- making `policy targeting` claims beyond risk ranking
- reopening the full `2018-2020` correction problem
- reopening the `MEPS` line as the main execution branch
- forcing `NHIS` into a state-period validation role it cannot support in public files

## Final Verdict

From the implemented gate summary:

- `timing_gate = true`
- `falsification_gate = true`
- `stability_gate = true`
- verdict = `GO_RISK_ONLY`

This verdict should be interpreted as:

- the stack is strong enough for bounded prediction-style work
- the stack is still below the bar for causal escalation

## What A Future Agent May Do Next

Allowed:

- refine the risk model
- stress-test the selected feature families
- test calibration and ranking stability in alternative windows
- improve measurement around the selected burden proxy
- add stronger descriptive validation layers

Not allowed without new evidence:

- causal `DID` or `DDD`
- `event study`
- `DML`
- `causal forest`
- causal or welfare-based policy targeting language

## Known Caveats

- The timing winner is selected by the implemented gate rule, not by raw signal strength alone.
- The HPS external check only partially echoes the SIPP result: coverage moves the expected way, uninsured does not.
- NHIS remains useful only for national or region-level descriptive appendix work unless restricted geography becomes available.
- Some scripts emit pandas future warnings. They do not currently break outputs.

## Environment Notes

- This round installed `scikit-learn` into the current Python environment.
- No destructive git or filesystem operations were used.
- The new work is concentrated in `scripts/design_diagnostics/`, `outputs/design_diagnostics/`, and `docs/`.
