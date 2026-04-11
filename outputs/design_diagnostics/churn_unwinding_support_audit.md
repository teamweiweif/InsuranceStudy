# Churn / Unwinding Support Audit

Last updated: `2026-04-10`

## Purpose

This note records the first support and overlap audit for the unwinding-era diagnostics phase.

It combines:

- corrected pre-period support from the `2022` and `2023` releases
- the unwinding-era merged `2024` release
- state-month support checks for the first candidate exposure families

This is a diagnostics artifact, not an estimating result.

## Year-Level Support Summary

| reference_year | source | rows | persons | eligible_medicaid_transition_rows | weighted_eligible_transition_sum | weighted_medicaid_exit_rate | weighted_exit_to_uninsured_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 2022 release corrected pilot | 486618 | 41040 | 89010 | 745757305.63 | 0.0033 | 0.0014 |
| 2022 | 2023 release corrected pilot | 475772 | 40245 | 87733 | 775530922.51 | 0.0044 | 0.0016 |
| 2023 | 2024 release merged prototype | 436237 | 36901 | 81207 | 772917077.33 | 0.0078 | 0.0035 |

Interpretation:

- `2022` and `2023` corrected releases now provide usable pre-period support years for baseline churn diagnostics.
- `2024` remains the unwinding-era main layer because it is the release already merged to CMS state-month data.
- The three-year stack is not being treated as one final estimating panel. It is being used as a diagnostics stack with distinct roles by reference year.

## State-Month Window Support

| window | exposure_family | state_month_cells_total | state_month_cells_nonmissing | unique_states_nonmissing | eligible_rows_sum | eligible_weight_sum | exposure_min | exposure_median | exposure_p90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| core_aug_nov_2023 | procedural_friction | 204 | 204 | 51 | 29060 | 276929544.37 | 0.0 | 0.7224 | 0.8653 |
| core_aug_nov_2023 | renewal_intensity | 204 | 204 | 51 | 29060 | 276929544.37 | 5318.0 | 101784.0 | 296845.2 |
| core_aug_nov_2023 | pending_pressure | 204 | 204 | 51 | 29060 | 276929544.37 | 0.0 | 0.0252 | 0.1991 |
| extended_mar_nov_2023 | procedural_friction | 459 | 362 | 51 | 66083 | 629334390.31 | 0.0 | 0.7245 | 0.8778 |
| extended_mar_nov_2023 | renewal_intensity | 459 | 362 | 51 | 66083 | 629334390.31 | 4060.0 | 91655.0 | 289168.3 |
| extended_mar_nov_2023 | pending_pressure | 459 | 362 | 51 | 66083 | 629334390.31 | 0.0 | 0.0233 | 0.1748 |

Interpretation:

- Transition-based diagnostics require `eligible_medicaid_transition`, so the cleanest "core" window is `August-November 2023`, not `August-December 2023`.
- `December 2023` still matters for exposure coverage and reference-year interpretation, but not for next-month transition outcomes inside this file.
- The core window is therefore the first reliable transition-based diagnostics window.

## Bottom Line

- The diagnostics stack now has enough support to begin unwinding-era mechanism testing.
- The project no longer needs another automatic backfill step before opening the first diagnostics.
- The next design question is not whether support exists, but which exposure family and timing alignment behave most credibly.
