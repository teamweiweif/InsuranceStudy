# Avoidable Churn Subgroup Stability Round 2

Last updated: `2026-04-26`

## Purpose

This file records Step 2 from `docs/churn_unwinding_operational_plan_2026-04-11.md`.

It re-tests subgroup ordering stability using the upgraded avoidable harmful churn outcomes. It remains a risk-ranking and subgroup-stability diagnostic, not DID, DML, causal forest, event-study, or causal targeting work.

## Result 1: Primary Harmful Outcome Ordering

### Question

Do retained person/household subgroup families show repeatable high-risk ordering from the pre-period into the unwinding year when the outcome is upgraded to persistent uninsured churn?

### Sample / Unit

- Data: corrected `SIPP 2021-2023` avoidable-churn outcome layer.
- Unit: person-month observations summarized into subgroup-period weighted rates.
- Pre-period: pooled `2021-2022`.
- Unwinding-year comparison: `2023`.
- Primary window: `core_aug_oct_2023`.

### Outcome

- `persistent_uninsured_h2`: pure Medicaid at `t`, uninsured at both `t+1` and `t+2`.
- `broad_exit_persistent_uninsured_h2`: broad Medicaid exit at `t+1`, uninsured at `t+2`.

### Treatment / Exposure

No causal treatment is estimated in this step. The diagnostic exposure is subgroup membership, used only to assess whether high-risk ordering is repeatable across periods.

### Purpose

The purpose is to test whether the avoidable-churn outcome upgrade creates a more stable subgroup basis for later bounded risk ranking.

### Numerical Result

- stable families on `persistent_uninsured_h2`: `foreign_born_group, household_child_group, snap_group`
- stable families on `broad_exit_persistent_uninsured_h2`: `foreign_born_group, household_child_group, snap_group`
- stable on both harmful outcomes: `foreign_born_group, household_child_group, snap_group`

| feature_family | outcome | groups_compared | pre_top_group | unwinding_top_group | pre_unwinding_spearman | top_group_match | stable_flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| foreign_born_group | persistent_uninsured_h2 | 2 | us_born | us_born | 1.0 | True | True |
| foreign_born_group | broad_exit_persistent_uninsured_h2 | 2 | us_born | us_born | 1.0 | True | True |
| household_child_group | persistent_uninsured_h2 | 2 | household_has_child | household_has_child | 1.0 | True | True |
| household_child_group | broad_exit_persistent_uninsured_h2 | 2 | household_has_child | household_has_child | 1.0 | True | True |
| snap_group | persistent_uninsured_h2 | 2 | snap_no | snap_no | 1.0 | True | True |
| snap_group | broad_exit_persistent_uninsured_h2 | 2 | snap_no | snap_no | 1.0 | True | True |
| age_band | persistent_uninsured_h2 | 5 | age_26_44 | age_18_25 | 0.4 | False | False |
| age_band | broad_exit_persistent_uninsured_h2 | 5 | age_26_44 | age_18_25 | 0.4 | False | False |
| pov_band | persistent_uninsured_h2 | 4 | pov_2_4 | pov_2_4 | 0.4 | True | False |
| pov_band | broad_exit_persistent_uninsured_h2 | 4 | pov_2_4 | pov_2_4 | 0.4 | True | False |
| female_group | persistent_uninsured_h2 | 2 | female | male | -1.0 | False | False |
| female_group | broad_exit_persistent_uninsured_h2 | 2 | female | male | -1.0 | False | False |
| noncitizen_group | persistent_uninsured_h2 | 2 | citizen | noncitizen | -1.0 | False | False |
| noncitizen_group | broad_exit_persistent_uninsured_h2 | 2 | citizen | noncitizen | -1.0 | False | False |

### Interpretation

The upgraded harmful outcome layer produces several repeatable subgroup orderings. Families stable on both harmful outcomes are the most defensible candidates for later risk ranking; families stable on only one harmful outcome should be treated as weaker supporting evidence.

### Evaluation

- repeatable high-risk families on at least one harmful outcome: `3`
- repeatable high-risk families on both harmful outcomes: `3`

### Caveat

The event rates remain low, and subgroup ordering is descriptive. This step does not estimate causal heterogeneity or prove that administrative burden caused the subgroup differences.

## Result 2: Improvement Relative To The Earlier Subgroup Round

### Question

Does the upgraded avoidable-churn outcome layer improve stability relative to the earlier narrower `medicaid_exit_to_uninsured_next` subgroup screen?

### Sample / Unit

- New comparison: `core_aug_oct_2023`, pooled pre-period `2021-2022` against `2023`.
- Earlier comparison: existing second-round subgroup-stability summary for `medicaid_exit_to_uninsured_next`.

### Outcome

- New primary outcome: `persistent_uninsured_h2`.
- Earlier benchmark outcome: `medicaid_exit_to_uninsured_next`.

### Treatment / Exposure

No treatment is estimated. This is a comparison of subgroup ordering stability across outcome definitions.

### Purpose

The purpose is to decide whether the avoidable-churn outcome upgrade strengthens the case for bounded risk-ranking work.

### Numerical Result

- old stable family count on `medicaid_exit_to_uninsured_next`: `2` (`household_child_group, snap_group`)
- new stable family count on `persistent_uninsured_h2`: `3`
- old mean Spearman: `-0.0286`
- new `persistent_uninsured_h2` mean Spearman: `0.2571`
- improves stable count: `True`
- improves mean Spearman: `True`

| feature_family | new_persistent_spearman | new_persistent_top_match | new_persistent_stable | new_persistent_pre_top | new_persistent_2023_top | new_broad_harm_spearman | new_broad_harm_top_match | new_broad_harm_stable | new_broad_harm_pre_top | new_broad_harm_2023_top | old_exit_to_uninsured_spearman | old_exit_to_uninsured_top_match | old_exit_to_uninsured_stable | old_exit_to_uninsured_pre_top | old_exit_to_uninsured_2023_top |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| age_band | 0.4 | False | False | age_26_44 | age_18_25 | 0.4 | False | False | age_26_44 | age_18_25 | 0.6 | False | False | age_26_44 | age_18_25 |
| female_group | -1.0 | False | False | female | male | -1.0 | False | False | female | male | -1.0 | False | False | female | male |
| foreign_born_group | 1.0 | True | True | us_born | us_born | 1.0 | True | True | us_born | us_born | -1.0 | False | False | foreign_born | us_born |
| household_child_group | 1.0 | True | True | household_has_child | household_has_child | 1.0 | True | True | household_has_child | household_has_child | 1.0 | True | True | household_has_child | household_has_child |
| noncitizen_group | -1.0 | False | False | citizen | noncitizen | -1.0 | False | False | citizen | noncitizen | -1.0 | False | False | citizen | noncitizen |
| pov_band | 0.4 | True | False | pov_2_4 | pov_2_4 | 0.4 | True | False | pov_2_4 | pov_2_4 | 0.2 | True | False | pov_2_4 | pov_2_4 |
| snap_group | 1.0 | True | True | snap_no | snap_no | 1.0 | True | True | snap_no | snap_no | 1.0 | True | True | snap_no | snap_no |

### Interpretation

The new outcome layer is more useful if it increases the number of stable families or improves the average pre-to-2023 rank correlation relative to the earlier narrow outcome.

### Evaluation

- outcome-layer stability improvement relative to earlier round: `True`

### Caveat

This is not a perfectly matched comparison because the old round used the earlier outcome layer and its own diagnostic window. The comparison is best read as a directional check, not a formal statistical test.

## Result 3: Resolution Contrast Check

### Question

Does the contrast outcome `broad_exit_resolved_insured_h2` show stable ordering that should change the interpretation of harmful subgroup risk?

### Sample / Unit

- Same `SIPP 2021-2023` subgroup-period setup.
- Primary window: `core_aug_oct_2023`.

### Outcome

`broad_exit_resolved_insured_h2`: broad Medicaid exit at `t+1`, insured again by `t+2`.

### Treatment / Exposure

No causal treatment is estimated. The contrast is used to avoid mistaking all exits for harmful churn.

### Purpose

The purpose is to check whether groups with harmful persistent uninsured churn are simply groups with more exits of all types, including resolved insured exits.

### Numerical Result

| feature_family | groups_compared | pre_top_group | unwinding_top_group | pre_unwinding_spearman | top_group_match | stable_flag |
| --- | --- | --- | --- | --- | --- | --- |
| foreign_born_group | 2 | us_born | us_born | 1.0 | True | True |
| household_child_group | 2 | household_no_child | household_no_child | 1.0 | True | True |
| noncitizen_group | 2 | citizen | citizen | 1.0 | True | True |
| snap_group | 2 | snap_no | snap_no | 1.0 | True | True |
| pov_band | 4 | pov_4_plus | pov_4_plus | 0.8 | True | True |
| age_band | 5 | age_26_44 | age_18_25 | 0.5 | False | False |
| female_group | 2 | male | female | -1.0 | False | False |

### Interpretation

The contrast outcome helps separate harmful persistence from resolved coverage transitions. It should be used as context for risk-ranking claims, not as a main harm endpoint.

### Evaluation

The contrast check is useful as a guardrail but does not by itself unlock stronger causal or targeting language.

### Caveat

The contrast outcome is still built from short-horizon SIPP monthly reports, so it shares the same monthly reporting and support limitations as the harmful outcomes.

## Closure Test

- at least one or two subgroup families now show repeatable high-risk ordering: `True`
- the new outcome layer improves stability relative to the earlier round: `True`
- evidence supports a stronger but bounded risk-ranking interpretation: `True`
- explicit Step 2 verdict: `SUBGROUP_STABILITY_ROUND2_SUPPORTS_RISK_RANKING`
- Step 3 unlocked: `True`

## Main Caveat

This remains subgroup-stability and risk-ranking evidence. It does not establish that state-month administrative burden caused the subgroup ordering, and it does not unlock DID, DML, causal forest, event-study, or causal targeting work.

## Artifacts

- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2_summary.csv`
- `outputs/design_diagnostics/avoidable_churn_subgroup_ordering_tables.csv`
- `scripts/design_diagnostics/build_avoidable_churn_subgroup_stability_round2.py`
