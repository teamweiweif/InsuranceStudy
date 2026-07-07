# Churn / Unwinding Pre-Period Falsification Audit

Last updated: `2026-04-10`

## Purpose

This note tests whether later `2023` unwinding-exposure rankings may simply be proxying for pre-existing baseline state churn differences.

Method:

- classify states by their later `August-November 2023` exposure intensity
- use corrected `reference year 2021` and `reference year 2022` core-window churn outcomes as untreated support years
- compare weighted state-level churn rates across later exposure tertiles

## High-Minus-Low Summary

| reference_year | exposure_family | weighted_exit_rate | weighted_exit_to_uninsured_rate |
| --- | --- | --- | --- |
| 2021 | pending_pressure | -0.0018 | -0.0005 |
| 2021 | procedural_friction | 0.0003 | -0.0009 |
| 2021 | renewal_intensity | -0.0001 | 0.0004 |
| 2022 | pending_pressure | -0.0008 | -0.0006 |
| 2022 | procedural_friction | 0.0009 | -0.0 |
| 2022 | renewal_intensity | 0.0019 | 0.0003 |

## Full Summary

| reference_year | exposure_family | tertile | states | eligible_weight_sum | weighted_exit_rate | weighted_exit_to_uninsured_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | procedural_friction | high | 17 | 61290538.6739 | 0.0025 | 0.0004 |
| 2021 | procedural_friction | low | 17 | 66130579.9867 | 0.0022 | 0.0013 |
| 2021 | procedural_friction | mid | 17 | 145276266.6152 | 0.0027 | 0.0011 |
| 2022 | procedural_friction | high | 17 | 66433562.7382 | 0.0032 | 0.001 |
| 2022 | procedural_friction | low | 17 | 68924106.2415 | 0.0023 | 0.001 |
| 2022 | procedural_friction | mid | 17 | 146944394.3338 | 0.0036 | 0.001 |
| 2021 | procedural_friction | high_minus_low | 34 | 127421118.6606 | 0.0003 | -0.0009 |
| 2022 | procedural_friction | high_minus_low | 34 | 135357668.9796 | 0.0009 | -0.0 |
| 2021 | renewal_intensity | high | 17 | 196069664.1373 | 0.0025 | 0.0012 |
| 2021 | renewal_intensity | low | 17 | 17316935.7958 | 0.0026 | 0.0008 |
| 2021 | renewal_intensity | mid | 17 | 59310785.3427 | 0.0027 | 0.0005 |
| 2022 | renewal_intensity | high | 17 | 201159959.3182 | 0.0034 | 0.0011 |
| 2022 | renewal_intensity | low | 17 | 17957368.9714 | 0.0015 | 0.0009 |
| 2022 | renewal_intensity | mid | 17 | 63184735.0238 | 0.003 | 0.0006 |
| 2021 | renewal_intensity | high_minus_low | 34 | 213386599.933 | -0.0001 | 0.0004 |
| 2022 | renewal_intensity | high_minus_low | 34 | 219117328.2896 | 0.0019 | 0.0003 |
| 2021 | pending_pressure | high | 17 | 106102242.6897 | 0.002 | 0.0008 |
| 2021 | pending_pressure | low | 17 | 76302588.4383 | 0.0038 | 0.0013 |
| 2021 | pending_pressure | mid | 17 | 90292554.1478 | 0.0021 | 0.001 |
| 2022 | pending_pressure | high | 17 | 109122566.657 | 0.003 | 0.0009 |
| 2022 | pending_pressure | low | 17 | 76799820.1782 | 0.0038 | 0.0015 |
| 2022 | pending_pressure | mid | 17 | 96379676.4783 | 0.0029 | 0.0007 |
| 2021 | pending_pressure | high_minus_low | 34 | 182404831.128 | -0.0018 | -0.0005 |
| 2022 | pending_pressure | high_minus_low | 34 | 185922386.8352 | -0.0008 | -0.0006 |

## Reading Guide

- Large and stable `high_minus_low` pre-period gaps would weaken later unwinding interpretation.
- Small or mixed pre-period gaps do not prove identification, but they reduce one obvious falsification concern.
- This is a state-level falsification screen, not a final event-study test.

## Bottom Line

- Across the first falsification screen, the largest absolute pre-period `high_minus_low` difference is `0.0019` for `medicaid_exit_next` and `0.0009` for `exit_to_uninsured`.
- This means the project should still run later design diagnostics, but later exposure rankings do not automatically look like trivial proxies for pre-existing state churn levels.
