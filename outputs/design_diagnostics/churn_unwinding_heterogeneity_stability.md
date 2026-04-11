# Churn / Unwinding Heterogeneity Stability Screen

Last updated: `2026-04-10`

## Purpose

This note runs a conservative first heterogeneity-stability screen using only subgroup dimensions already retained in the current corrected prototype files.

Current subgroup design:

- state baseline-risk tertiles built from pooled corrected `reference years 2021-2022`
- no broad demographic feature layer yet, because the current prototype files intentionally keep a narrow churn-focused variable set

## High-Minus-Low Summary

| source_label | reference_year | weighted_exit_rate | weighted_exit_to_uninsured_rate |
| --- | --- | --- | --- |
| 2021_pre | 2021 | 0.0047 | 0.0017 |
| 2022_pre | 2022 | 0.0053 | 0.0014 |
| 2023_unwinding | 2023 | -0.0012 | -0.0018 |

## Full Summary

| source_label | reference_year | baseline_exit_tertile | states | eligible_weight_sum | weighted_exit_rate | weighted_exit_to_uninsured_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2021_pre | 2021 | high | 17 | 114376361.626 | 0.0047 | 0.0017 |
| 2021_pre | 2021 | low | 17 | 32161873.2082 | 0.0 | 0.0 |
| 2021_pre | 2021 | mid | 17 | 126159150.4415 | 0.0012 | 0.0006 |
| 2022_pre | 2022 | high | 17 | 111297601.2096 | 0.0053 | 0.0014 |
| 2022_pre | 2022 | low | 17 | 35753579.6869 | 0.0 | 0.0 |
| 2022_pre | 2022 | mid | 17 | 135250882.4169 | 0.0024 | 0.0009 |
| 2023_unwinding | 2023 | high | 17 | 115381730.9247 | 0.0051 | 0.0023 |
| 2023_unwinding | 2023 | low | 17 | 33961732.643 | 0.0064 | 0.0041 |
| 2023_unwinding | 2023 | mid | 17 | 127586080.8067 | 0.0101 | 0.0042 |
| 2021_pre | 2021 | high_minus_low | 34 | 146538234.8343 | 0.0047 | 0.0017 |
| 2022_pre | 2022 | high_minus_low | 34 | 147051180.8965 | 0.0053 | 0.0014 |
| 2023_unwinding | 2023 | high_minus_low | 34 | 149343463.5677 | -0.0012 | -0.0018 |

## Reading Guide

- If high-baseline-risk states remain higher-risk in both pre-period years and the unwinding year, that supports stability of the risk ranking, not necessarily treatment identification.
- If ordering flips wildly across years, later targeting logic becomes weaker.
- This screen is intentionally conservative because the current prototype files do not yet carry the future high-dimensional targeting feature set.

## Bottom Line

- The current heterogeneity screen is best read as a stability check on state-level baseline risk ordering.
- It is useful for deciding whether later richer subgroup or `causal ML` work is worth building, but it is not itself a targeting result.
