# Avoidable Churn Risk-Ranking Round 2

Last updated: `2026-04-26`

## Purpose

This file records Step 3 from `docs/churn_unwinding_operational_plan_2026-04-11.md`.

It upgrades the earlier bounded risk pilot to the avoidable harmful churn outcome layer. It remains a risk-ranking and prioritization diagnostic, not DID, DML, causal forest, event-study, or causal targeting work.

## Result 1: Primary Risk-Ranking Performance

### Question

Can retained person/household subgroup features rank `2023` persistent-uninsurance risk better than a naive state-baseline score when trained only on `2021-2022`?

### Sample / Unit

- Data: corrected `SIPP 2021-2023` avoidable-churn outcome layer.
- Unit: eligible person-month observations.
- Train: `2021-2022`, months `8-10`.
- Test: `2023`, months `8-10`.
- Weights: `WPFINWGT`.

### Outcome

`persistent_uninsured_h2`: pure Medicaid at `t`, uninsured at both `t+1` and `t+2`.

### Treatment / Exposure

No causal treatment is estimated. Predictors are retained person/household subgroup features; the benchmark exposure is a naive state-baseline risk score from the `2021-2022` training period.

### Purpose

The purpose is to decide whether the current line can support a bounded risk-ranking / prioritization prototype.

### Numerical Result

| outcome | model | auc | pr_auc | top_decile_capture | event_rate | rows_test | delta_auc_vs_naive_state | delta_top_decile_vs_naive_state | delta_auc_vs_old_pilot_logistic | delta_top_decile_vs_old_pilot_logistic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| persistent_uninsured_h2 | naive_state_baseline | 0.417915 | 0.002873 | 0.039633 | 0.002933 | 21774 |  |  |  |  |
| persistent_uninsured_h2 | weighted_logistic | 0.557036 | 0.004931 | 0.105725 | 0.002933 | 21774 | 0.139121 | 0.066091 |  |  |
| persistent_uninsured_h2 | shallow_tree | 0.529255 | 0.003111 | 0.130421 | 0.002933 | 21774 | 0.11134 | 0.090787 |  |  |
| persistent_uninsured_h2 | compact_boosting | 0.538876 | 0.004594 | 0.196646 | 0.002933 | 21774 | 0.120961 | 0.157013 |  |  |

### Interpretation

The AUC-leading primary model is `weighted_logistic` with AUC `0.5570`. The strongest top-decile-capture model is `compact_boosting` with top-decile capture `0.1966`.

### Evaluation

- primary best-model AUC gain over naive state baseline: `0.1391`
- primary best-model top-decile capture gain over naive state baseline: `0.0661`
- primary capture-model top-decile capture gain over naive state baseline: `0.1570`
- primary model beats naive state baseline under the round-2 rule: `True`

### Caveat

The primary outcome remains rare. The model is useful only as a ranking diagnostic and should not be interpreted as a causal targeting rule.

## Result 2: Comparison Against Old Risk Pilot

### Question

Does the round-2 risk screen remain competitive with the older risk pilot on the benchmark outcome?

### Sample / Unit

- New comparison: train `2021-2022`, test `2023`, months `8-10`.
- Old pilot: existing `risk_prediction_pilot_metrics.csv`, built before the avoidable-churn upgrade.

### Outcome

`medicaid_exit_to_uninsured_next`, retained as the benchmark outcome for direct comparison with the older pilot.

### Treatment / Exposure

No treatment is estimated. The comparison is between risk-ranking models and the older bounded risk-prediction pilot.

### Purpose

The purpose is to enforce the stop rule that the new risk round should not be materially weaker than the old pilot.

### Numerical Result

| outcome | model | auc | pr_auc | top_decile_capture | event_rate | rows_test | delta_auc_vs_naive_state | delta_top_decile_vs_naive_state | delta_auc_vs_old_pilot_logistic | delta_top_decile_vs_old_pilot_logistic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| medicaid_exit_to_uninsured_next | naive_state_baseline | 0.440819 | 0.00316 | 0.036463 | 0.003178 | 21827 |  |  |  |  |
| medicaid_exit_to_uninsured_next | weighted_logistic | 0.563267 | 0.005191 | 0.12216 | 0.003178 | 21827 | 0.122448 | 0.085697 | -0.085021 | 0.01446 |
| medicaid_exit_to_uninsured_next | shallow_tree | 0.529985 | 0.00338 | 0.119988 | 0.003178 | 21827 | 0.089167 | 0.083525 | -0.118302 | 0.012288 |
| medicaid_exit_to_uninsured_next | compact_boosting | 0.527146 | 0.003426 | 0.100813 | 0.003178 | 21827 | 0.086327 | 0.06435 | -0.121142 | -0.006887 |

- old risk-pilot logistic on `medicaid_exit_to_uninsured_next`: AUC `0.6483`, PR AUC `0.0058`, top-decile capture `0.1077`

### Interpretation

The benchmark outcome checks whether the new implementation is still competitive on the earlier narrow outcome while the paper core shifts to persistent uninsurance.

### Evaluation

- benchmark logistic AUC delta versus old pilot logistic: `-0.0850`
- benchmark logistic top-decile delta versus old pilot logistic: `0.0145`
- benchmark AUC remains not materially worse than old pilot: `False`
- benchmark top-decile capture remains not materially worse than old pilot: `True`
- benchmark comparison versus old pilot is mixed: `True`

### Caveat

The old pilot used the earlier outcome layer and a slightly different month window. This is a directional stop-rule check, not a formal model-selection test.

## Result 3: Calibration And Subgroup Calibration

### Question

Is calibration good enough to describe the output as a modest prioritization prototype rather than just a discrimination score?

### Sample / Unit

Same Step 3 test sample, summarized by weighted risk deciles and retained subgroup families.

### Outcome

Primary calibration is reported for `persistent_uninsured_h2`; full calibration tables are saved to CSV for both outcomes.

### Treatment / Exposure

No treatment is estimated. Calibration evaluates predicted risk scores against observed weighted outcome rates.

### Purpose

The purpose is to check whether the ranking model can support a bounded prioritization prototype with transparent caveats.

### Numerical Result

Primary prioritization-model (`compact_boosting`) calibration at the bottom and top risk deciles:

| risk_decile | mean_pred | observed_rate | event_count_unweighted | event_weighted |
| --- | --- | --- | --- | --- |
| 1.0 | 0.000521 | 0.000391 | 1.0 | 8099.83 |
| 10.0 | 0.001711 | 0.005766 | 11.0 | 119655.78 |

Primary prioritization-model (`compact_boosting`) calibration for Step 2 stable subgroup families:

| group_family | group_label | observed_rate | mean_pred | calibration_error | event_count_unweighted |
| --- | --- | --- | --- | --- | --- |
| foreign_born_group | foreign_born | 0.002423 | 0.000819 | -0.001603 | 9 |
| foreign_born_group | us_born | 0.003033 | 0.001113 | -0.00192 | 54 |
| household_child_group | household_has_child | 0.003086 | 0.001114 | -0.001972 | 42 |
| household_child_group | household_no_child | 0.002666 | 0.000979 | -0.001687 | 21 |
| snap_group | snap_no | 0.003798 | 0.00109 | -0.002708 | 53 |
| snap_group | snap_yes | 0.001171 | 0.001013 | -0.000158 | 10 |

### Interpretation

The decile table is the main calibration guardrail. Subgroup calibration is retained as a diagnostic because subgroup ordering, not individual causal targeting, is the current validated contribution. The calibration evidence supports rank-only language, not probability-calibrated targeting.

### Evaluation

- calibration good enough for bounded rank-prototype language: `True`

### Caveat

Predicted probabilities are not externally calibrated, and decile ordering is not perfectly monotone. They should be used for rank ordering and prioritization diagnostics only.

## Closure Test

- the new risk round improves ranking usefulness relative to the old risk pilot: `mixed`
- old-pilot comparison detail: AUC not-worse `False`, top-decile not-worse `True`
- the signal remains better than naive state baseline: `True`
- calibration is good enough to support a modest risk prioritization prototype: `True`
- explicit Step 3 verdict: `RISK_RANKING_ROUND2_MIXED_WITH_CAVEAT`
- Step 4 unlocked: `True`

## Main Caveat

This remains a risk-ranking prototype. It does not establish that state-month administrative burden caused persistent uninsurance, and it does not unlock DID, DML, causal forest, event-study, or causal targeting work.

## Artifacts

- `outputs/design_diagnostics/avoidable_churn_risk_round2_metrics.csv`
- `outputs/design_diagnostics/avoidable_churn_risk_round2_calibration.csv`
- `outputs/design_diagnostics/avoidable_churn_risk_round2_group_calibration.csv`
- `scripts/design_diagnostics/run_avoidable_churn_risk_round2.py`
