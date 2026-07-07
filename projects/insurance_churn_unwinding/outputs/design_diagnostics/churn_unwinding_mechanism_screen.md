# Churn / Unwinding Mechanism Screen

Last updated: `2026-04-10`

## Purpose

This note records the first mechanism screen for the unwinding-era diagnostics phase.

It compares the first three candidate exposure families in the `core_aug_nov_2023` transition window:

- `procedural friction`
- `renewal intensity`
- `pending pressure`

For each exposure family, state-month cells are split into low / mid / high terciles.

The reported outcome rates are weighted by the state-month eligible Medicaid-transition support.

## Mechanism Screen Summary

| exposure_family | tertile | cells | eligible_weight_sum | weighted_exit_rate | weighted_exit_to_uninsured_rate |
| --- | --- | --- | --- | --- | --- |
| procedural_friction | high | 68 | 55550326.73 | 0.008 | 0.0029 |
| procedural_friction | low | 68 | 78057735.07 | 0.0049 | 0.003 |
| procedural_friction | mid | 68 | 143321482.57 | 0.0089 | 0.0038 |
| procedural_friction | high_minus_low | 136 | 133608061.8 | 0.0031 | -0.0001 |
| renewal_intensity | high | 68 | 195216432.57 | 0.0074 | 0.0033 |
| renewal_intensity | low | 68 | 18490760.53 | 0.0078 | 0.003 |
| renewal_intensity | mid | 68 | 63222351.28 | 0.0082 | 0.0038 |
| renewal_intensity | high_minus_low | 136 | 213707193.1 | -0.0004 | 0.0003 |
| pending_pressure | high | 68 | 104075968.39 | 0.0082 | 0.0045 |
| pending_pressure | low | 68 | 74940922.98 | 0.0065 | 0.0032 |
| pending_pressure | mid | 68 | 97912653.01 | 0.0078 | 0.0024 |
| pending_pressure | high_minus_low | 136 | 179016891.37 | 0.0017 | 0.0013 |

## Reading Guide

- A stronger `high_minus_low` contrast for `exit_to_uninsured` than for broad `medicaid_exit_next` is more consistent with an administrative-loss mechanism.
- A strong pattern for `procedural friction` is the most directly useful signal for the project's intended unwinding contribution.
- A signal that appears only for broader `renewal intensity` but not procedural friction would point to a weaker, more diffuse pressure story.

## Bottom Line

- This screen should be used to decide which mechanism family deserves the next serious empirical pass.
- It should not yet be treated as a final paper result.
