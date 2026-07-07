# Churn / Unwinding Paper Outline And Results Map

Last updated: `2026-04-27`

## Purpose

This file translates the locked Path A decision into a practical paper outline and results-to-table map.

It follows `docs/churn_unwinding_post_round4_path_decision.md` and does not open new data, new topic search, DID, DML, event-study, causal forest, causal ML, causal targeting, welfare targeting, or deployment work.

## Preferred Title

Preferred title:

`Administrative Renewal Burden and Persistent Uninsurance Risk During Medicaid Unwinding: A Public-Data Risk and Vulnerability Study`

Alternative titles:

- `Persistent Uninsurance After Medicaid Exit During Unwinding: Public-Data Evidence On Administrative Burden And Vulnerability`
- `Measuring Harmful Medicaid Churn During Unwinding: A SIPP-CMS Public-Data Risk Study`
- `Administrative Renewal Burden, Harmful Churn, And Risk Ranking During Medicaid Unwinding`

Use the preferred title unless a target journal requires shorter wording.

## Exact Narrowed Research Question

Can public-use SIPP person-month coverage transitions linked to CMS state-month Medicaid unwinding renewal-burden measures identify policy-relevant patterns of persistent uninsurance risk and subgroup vulnerability after Medicaid exit?

This question is intentionally diagnostic. It asks whether public data can identify risk patterns and vulnerability structure. It does not ask whether administrative burden caused coverage loss.

## Allowed Contribution

The paper may claim five contributions:

1. It builds a public-use SIPP person-month framework for studying Medicaid exit and short-horizon persistent uninsurance.
2. It sharpens the harm outcome from a one-month exit screen to `persistent_uninsured_h2`, defined as pure Medicaid at `t` and uninsured at both `t+1` and `t+2`.
3. It links SIPP person-month transition outcomes to CMS state-month Medicaid unwinding renewal-burden measures for diagnostic analysis.
4. It shows that `backlog_automation_rank_index / same` is the leading administrative-burden candidate after timing stress, with future-month placebo timing not dominating the best non-lead alignment.
5. It shows that selected subgroup vulnerability dimensions and simple risk-ranking models add useful risk information beyond crude state baseline ranking, while remaining bounded and non-causal.

## Claims Not Allowed

The paper must not claim:

- administrative renewal burden caused persistent uninsurance
- state-month burden measures identify treatment effects
- subgroup ordering is causal heterogeneity
- DID evidence
- event-study evidence
- DML evidence
- causal forest evidence
- causal ML evidence
- welfare-based targeting
- deployable outreach targeting
- well-calibrated predicted probabilities
- an optimal policy rule
- a proven procedural-friction mechanism

## Abstract-Level Story

Medicaid unwinding created a practical need to distinguish routine coverage transitions from harmful loss of coverage. This paper uses public-use SIPP person-month coverage data linked to CMS state-month unwinding renewal-burden measures to build a diagnostic framework for studying persistent uninsurance after Medicaid exit. The analysis focuses on `persistent_uninsured_h2`, a short-horizon harmful-churn outcome that captures remaining uninsured for two months after Medicaid coverage.

The diagnostic evidence points to `backlog_automation_rank_index / same` as the most stable administrative-burden candidate after timing stress. The future-month `lead1` placebo does not dominate the best non-lead alignment in the primary windows. The upgraded harmful outcome layer also improves subgroup stability: `foreign_born_group`, `household_child_group`, and `snap_group` show repeatable harmful-risk ordering from 2021-2022 into 2023. Finally, simple risk-ranking models outperform a naive state baseline, although AUC is modest and calibration is weak.

The contribution is a replicable public-data framework for administrative-burden and vulnerability diagnostics during Medicaid unwinding. The paper supports bounded risk-screening and prioritization language with caveats. It does not estimate causal effects, causal heterogeneity, or deployable targeting rules.

## Section-By-Section Plan

### 1. Introduction

Purpose:

- Motivate Medicaid unwinding as a setting where public data can help study harmful coverage loss.
- State the narrowed research question.
- Present the paper as a public-data risk and vulnerability study.

Key claims allowed:

- Persistent uninsurance after Medicaid exit is a policy-relevant harm.
- Public-use SIPP and CMS data can be linked into a useful diagnostic framework.
- The contribution is measurement, diagnostic linkage, vulnerability ordering, and bounded risk ranking.

Evidence to cite:

- `docs/churn_unwinding_post_round4_path_decision.md`
- `outputs/design_diagnostics/round4_path_decision_user_summary.md`
- `outputs/design_diagnostics/sipp_avoidable_churn_outcome_audit.md`
- `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`
- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2.md`
- `outputs/design_diagnostics/avoidable_churn_risk_round2.md`

What not to say:

- Do not say the paper estimates the effect of administrative burden.
- Do not describe the model as causal ML or targeting.
- Do not imply the risk model is deployable.

### 2. Policy Background: Medicaid Unwinding And Administrative Renewal Burden

Purpose:

- Explain unwinding, renewal processes, administrative burden, pending renewals, ex parte renewal, manual renewal burden, and backlog pressure.
- Define why persistent uninsurance after exit is a harmful coverage continuity outcome.

Key claims allowed:

- Renewal burden is a plausible administrative environment that can be measured with CMS state-month data.
- The paper studies diagnostic associations and risk patterns during unwinding.
- The policy motivation is operational: identifying where public data show greater harmful-churn risk.

Evidence to cite:

- `docs/churn_unwinding_avoidable_churn_memo.md`
- `docs/churn_unwinding_outcome_reassessment_memo.md`
- `docs/churn_unwinding_round3_robustness_memo.md`
- `outputs/design_diagnostics/avoidable_churn_round3_robustness.md`
- `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`

What not to say:

- Do not narrow the mechanism to proven `procedural friction`.
- Do not say renewal burden caused the observed transitions.
- Do not describe the CMS reporting month as a clean person-level disenrollment month.

### 3. Data

Purpose:

- Describe the SIPP person-month construction, corrected coverage layer, CMS state-month linkage, and analysis windows.
- Define the observation units used in different parts of the paper.

Key claims allowed:

- SIPP supports person-month coverage transitions.
- CMS unwinding renewal measures can be linked by state-month for diagnostic analysis.
- The strongest support is in the 2023 core windows used in the diagnostics.

Evidence to cite:

- `outputs/design_diagnostics/sipp_avoidable_churn_outcome_audit.md`
- `outputs/design_diagnostics/sipp_avoidable_churn_outcome_summary.json`
- `outputs/design_diagnostics/sipp_unwinding_feature_stack_summary.json`
- `outputs/design_diagnostics/avoidable_churn_round3_state_month_cells.csv`
- `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`

What not to say:

- Do not describe the stack as a seamless seven-year panel.
- Do not imply all 2023 months have equal CMS support.
- Do not hide horizon truncation for h2/h3 outcomes.

### 4. Measures

Purpose:

- Define the main outcome, contrast outcomes, administrative-burden exposure, subgroup families, and risk-ranking predictors.

Key claims allowed:

- The main harmful outcome is `persistent_uninsured_h2`.
- Supporting harmful outcomes include `broad_exit_persistent_uninsured_h2` and `persistent_uninsured_h3`.
- The main contrast outcome is `broad_exit_resolved_insured_h2`.
- The leading burden candidate is `backlog_automation_rank_index / same`.
- Retained subgroup families are `age_band`, `female_group`, `foreign_born_group`, `household_child_group`, `noncitizen_group`, `pov_band`, and `snap_group`.

Evidence to cite:

- `outputs/design_diagnostics/sipp_avoidable_churn_outcome_audit.md`
- `outputs/design_diagnostics/avoidable_churn_round3_robustness.md`
- `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`
- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2.md`
- `outputs/design_diagnostics/avoidable_churn_risk_round2.md`

What not to say:

- Do not call `persistent_uninsured_h2` an official CMS published outcome.
- Do not treat subgroup families as causal moderators.
- Do not treat predicted probabilities as calibrated risk levels.

### 5. Empirical Design / Diagnostic Strategy

Purpose:

- Explain that the paper uses staged diagnostics rather than causal identification.
- Organize the empirical strategy around timing stress, outcome robustness, subgroup stability, and bounded risk ranking.

Key claims allowed:

- Timing stress tests ask whether the leading burden candidate survives same, lagged, and future-month comparisons.
- Subgroup stability tests ask whether pre-period ordering repeats in the unwinding year.
- Risk-ranking tests ask whether retained subgroup features beat a naive state baseline when trained on 2021-2022 and tested on 2023.

Evidence to cite:

- `docs/empirical_result_reporting_convention.md`
- `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`
- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2.md`
- `outputs/design_diagnostics/avoidable_churn_risk_round2.md`

What not to say:

- Do not call the design DID, DML, event-study, or causal ML.
- Do not use treatment-effect language.
- Do not call the risk model a targeting rule.

### 6. Results

Purpose:

- Present the main empirical diagnostics in a tight sequence: data support, outcome layer, burden timing, subgroup vulnerability.

Key claims allowed:

- `persistent_uninsured_h2` is usable and more policy-relevant than a one-month exit-only screen.
- `backlog_automation_rank_index / same` remains the leading burden candidate after timing stress.
- The future-month placebo does not dominate the best non-lead alignment.
- `foreign_born_group`, `household_child_group`, and `snap_group` show stable harmful-risk ordering.

Evidence to cite:

- Table 1 through Table 4 below.
- `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`
- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2.md`

What not to say:

- Do not say the burden index caused the outcome.
- Do not say stable subgroup ordering proves vulnerability mechanisms.
- Do not overstate weak or unstable subgroup families.

### 7. Risk-Ranking Prototype

Purpose:

- Present the bounded risk-ranking exercise as a proof of diagnostic usefulness, not as a deployed model.

Key claims allowed:

- Simple models beat a naive state baseline.
- Compact boosting captures `0.1966` of weighted `persistent_uninsured_h2` events in the top decile.
- Weighted logistic has AUC `0.5570`, PR AUC `0.0049`, and top-decile capture `0.1057`.
- Step 3 is useful but mixed.

Evidence to cite:

- `outputs/design_diagnostics/avoidable_churn_risk_round2.md`
- `outputs/design_diagnostics/avoidable_churn_risk_round2_metrics.csv`
- `outputs/design_diagnostics/avoidable_churn_risk_round2_calibration.csv`
- `outputs/design_diagnostics/avoidable_churn_risk_round2_group_calibration.csv`

What not to say:

- Do not say the model is deployment-ready.
- Do not claim calibrated individual risk probabilities.
- Do not say the model assigns outreach treatment.
- Do not present boosting as an opaque final policy tool.

### 8. Discussion

Purpose:

- Interpret the paper as a public-data operational diagnostic.
- Explain what the results imply for public-data monitoring, not causal intervention design.

Key claims allowed:

- Public data can identify harmful churn risk patterns worth monitoring.
- Persistent uninsurance after Medicaid exit is a useful outcome for future public-data work.
- Vulnerability structure appears more informative than crude state-risk ordering.
- Risk ranking can support further diagnostic triage with caveats.

Evidence to cite:

- `docs/churn_unwinding_post_round4_path_decision.md`
- `outputs/design_diagnostics/round4_path_decision_user_summary.md`
- Main result tables.

What not to say:

- Do not claim the paper evaluates policy effects.
- Do not recommend targeting individuals based on the model.
- Do not imply states should allocate outreach solely from these scores.

### 9. Limitations

Purpose:

- State the evidence boundary plainly.
- Preempt overclaiming.

Key claims allowed:

- The design is diagnostic and descriptive/risk-ranking, not causal.
- CMS reporting month may not line up cleanly with person-month coverage loss.
- Event rates are low.
- Calibration is weak.
- The risk model is rank-only.
- Some subgroup families are unstable.
- `lead1` remains informative in some rows even though it does not dominate aggregate primary-window timing.

Evidence to cite:

- `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`
- `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2.md`
- `outputs/design_diagnostics/avoidable_churn_risk_round2.md`
- `docs/churn_unwinding_post_round4_path_decision.md`

What not to say:

- Do not bury the causal limitation.
- Do not present limitations as minor technical issues.
- Do not imply one more model would solve identification.

### 10. Conclusion

Purpose:

- Close with the strongest honest claim.

Key claims allowed:

- The paper provides a replicable public-data framework for studying persistent uninsurance risk during Medicaid unwinding.
- The framework supports diagnostic risk and vulnerability analysis.
- It motivates future work on stronger designs, but this paper does not estimate causal effects.

Evidence to cite:

- Final verdict from `docs/churn_unwinding_post_round4_path_decision.md`.
- Main tables and figures.

What not to say:

- Do not end by promising causal ML in this paper.
- Do not claim policy targeting readiness.

## Table Inventory

| Table | Proposed title | Source file(s) | Exact result or metric to use | Placement | Why it belongs | Caveat to report |
| --- | --- | --- | --- | --- | --- | --- |
| Table 1 | Data construction and sample / support summary | `outputs/design_diagnostics/sipp_avoidable_churn_outcome_audit.md`; `outputs/design_diagnostics/sipp_avoidable_churn_outcome_audit.csv`; `outputs/design_diagnostics/sipp_avoidable_churn_outcome_summary.json`; `outputs/design_diagnostics/sipp_unwinding_feature_stack_summary.json` | total rows/persons; reference years; h2/h3 support; retained outcomes; core Aug-Oct event counts and weighted rates for `persistent_uninsured_h2`, `broad_exit_persistent_uninsured_h2`, and `broad_exit_resolved_insured_h2` | Main text | Establishes the public-data measurement base and outcome support | `persistent_uninsured_h2` is constructed by the project, not an official CMS outcome; event rates are low |
| Table 2 | Main burden candidate and timing-stress results | `outputs/design_diagnostics/avoidable_churn_timing_stress_round4.md`; `outputs/design_diagnostics/avoidable_churn_timing_stress_matrix.csv`; `outputs/design_diagnostics/avoidable_churn_timing_placebo_summary.csv` | Step 1 verdict `STEP1_TIMING_STRESS_PASSED_WITH_CAVEAT`; `backlog_automation_rank_index / same`; scores `0.1722` and `0.1509`; lead placebo deltas `-0.0462` and `-0.0410` | Main text | Shows the leading administrative-burden candidate survives timing stress as a diagnostic signal | Still diagnostic; same-month alignment does not prove temporal causality |
| Table 3 | Harmful churn outcome family and robustness | `outputs/design_diagnostics/avoidable_churn_round3_robustness.md`; `outputs/design_diagnostics/avoidable_churn_round3_robustness_summary.json`; `outputs/design_diagnostics/avoidable_churn_outcome_robustness_audit.csv`; `outputs/design_diagnostics/avoidable_churn_outcome_robustness_timing.csv`; `outputs/design_diagnostics/avoidable_churn_outcome_robustness_falsification.csv` | outcome family: `persistent_uninsured_h2`, `broad_exit_persistent_uninsured_h2`, `persistent_uninsured_h3`, contrast `broad_exit_resolved_insured_h2`; Round-3 continuation verdict; outcome robustness directions | Main text, with detailed rows in appendix | Shows the paper is not hanging on a one-month exit screen alone | Nearby robustness exists, but all outcomes come from short-horizon SIPP monthly reporting |
| Table 4 | Subgroup stability and vulnerability ordering | `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2.md`; `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2_summary.csv`; `outputs/design_diagnostics/avoidable_churn_subgroup_ordering_tables.csv` | Step 2 verdict; stable families `foreign_born_group`, `household_child_group`, `snap_group`; old stable count `2`; new stable count `3`; old mean Spearman `-0.0286`; new mean Spearman `0.2571` | Main text | Anchors the vulnerability section and shows improved stability under the upgraded outcome | Descriptive ordering only; not causal heterogeneity |
| Table 5 | Risk-ranking model performance | `outputs/design_diagnostics/avoidable_churn_risk_round2.md`; `outputs/design_diagnostics/avoidable_churn_risk_round2_metrics.csv` | Step 3 verdict; weighted logistic AUC `0.5570`, PR AUC `0.0049`, top-decile capture `0.1057`; compact boosting AUC `0.5389`, PR AUC `0.0046`, top-decile capture `0.1966`; old-pilot deltas `-0.0850` and `0.0145` | Main text | Shows the bounded risk-ranking prototype beats naive state baseline but remains modest | Ranking diagnostic only; AUC modest; calibration weak |
| Table 6 or Appendix Table A1 | Allowed versus forbidden claims and robustness caveats | `docs/churn_unwinding_post_round4_path_decision.md`; `outputs/design_diagnostics/round4_path_decision_user_summary.md`; `docs/empirical_result_reporting_convention.md` | allowed claims; forbidden causal/targeting claims; main caveats by result family | Appendix, or boxed limitations table in main text | Keeps the paper honest and prevents drift into causal or deployment language | This is a framing table, not an empirical result |

## Figure Inventory

| Figure | Proposed title | Source file(s) | Exact result or metric to use | Placement | Why it belongs | Caveat to report |
| --- | --- | --- | --- | --- | --- | --- |
| Figure 1 | Public-data design: SIPP person-month transitions linked to CMS state-month renewal burden | `docs/churn_unwinding_post_round4_path_decision.md`; `outputs/design_diagnostics/sipp_avoidable_churn_outcome_audit.md`; `outputs/design_diagnostics/avoidable_churn_round3_state_month_cells.csv` | diagram elements: SIPP person-month coverage at `t`, `t+1`, `t+2`; state-month CMS renewal-burden measures; diagnostic state-month link | Main text | Explains the paper design before the results | Make it a design diagram, not an identification diagram |
| Figure 2 | Outcome timeline for `persistent_uninsured_h2` | `outputs/design_diagnostics/sipp_avoidable_churn_outcome_audit.md`; `docs/churn_unwinding_outcome_reassessment_memo.md` | timeline: pure Medicaid at `t`, uninsured at `t+1`, uninsured at `t+2`; contrast with one-month exit and resolved insured exit | Main text | Makes the harm outcome transparent | Do not call this an official CMS metric |
| Figure 3 | Timing-stress comparison for `backlog_automation_rank_index` | `outputs/design_diagnostics/avoidable_churn_timing_stress_matrix.csv`; `outputs/design_diagnostics/avoidable_churn_timing_placebo_summary.csv` | same, lag1, lag2, lead1 scores in core and mature windows; lead placebo deltas | Main text | Shows why the leading burden candidate is retained | Timing stress supports diagnostic credibility, not causal timing |
| Figure 4 | Subgroup stability visualization | `outputs/design_diagnostics/avoidable_churn_subgroup_ordering_tables.csv`; `outputs/design_diagnostics/avoidable_churn_subgroup_stability_round2_summary.csv` | pre-period versus 2023 ordering/rank correlation for retained families; highlight `foreign_born_group`, `household_child_group`, `snap_group` | Main text | Communicates vulnerability ordering better than a dense table | Stable ordering is descriptive and low-event |
| Figure 5 | Risk-ranking top-decile capture and calibration diagnostic | `outputs/design_diagnostics/avoidable_churn_risk_round2_metrics.csv`; `outputs/design_diagnostics/avoidable_churn_risk_round2_calibration.csv`; `outputs/design_diagnostics/avoidable_churn_risk_round2_group_calibration.csv` | top-decile capture by model; top versus bottom decile observed rates; calibration by decile | Main text with full calibration in appendix | Shows the risk prototype is useful but bounded | Calibration is weak; rank-only interpretation |

## Appendix / Robustness Inventory

Keep these outputs mostly in appendix or robustness:

- `outputs/design_diagnostics/avoidable_churn_timing_placebo_summary.csv`
- `outputs/design_diagnostics/avoidable_churn_timing_stress_matrix.csv` full expanded rows
- `outputs/design_diagnostics/avoidable_churn_outcome_robustness_audit.csv`
- `outputs/design_diagnostics/avoidable_churn_outcome_robustness_timing.csv`
- `outputs/design_diagnostics/avoidable_churn_outcome_robustness_falsification.csv`
- `outputs/design_diagnostics/avoidable_churn_subgroup_ordering_tables.csv` full subgroup rows
- `outputs/design_diagnostics/avoidable_churn_risk_round2_calibration.csv`
- `outputs/design_diagnostics/avoidable_churn_risk_round2_group_calibration.csv`
- `outputs/design_diagnostics/risk_prediction_pilot_metrics.csv` as old-pilot benchmark context
- `outputs/design_diagnostics/avoidable_churn_burden_falsification_summary.csv`
- `outputs/design_diagnostics/avoidable_churn_exposure_decomposition_timing.csv`
- `outputs/design_diagnostics/avoidable_churn_exposure_decomposition_ranking.csv`

Appendix framing:

- Use these outputs to show that the chosen line is not arbitrary.
- Do not use them to imply the design has become causal.

## Results Strong Enough For Main Text

These results are strong enough for main text:

- `persistent_uninsured_h2` is the primary harmful-churn outcome.
- `backlog_automation_rank_index / same` remains the leading burden candidate after timing stress.
- Primary timing scores are `0.1722` in `core_aug_oct_2023` and `0.1509` in `mature_jun_oct_2023`.
- Future-month `lead1` placebo does not dominate: core delta `-0.0462`, mature delta `-0.0410`.
- Step 2 subgroup verdict is `SUBGROUP_STABILITY_ROUND2_SUPPORTS_RISK_RANKING`.
- Stable subgroup families are `foreign_born_group`, `household_child_group`, and `snap_group`.
- The subgroup screen improves from old stable count `2` to new stable count `3`, and mean Spearman from `-0.0286` to `0.2571`.
- Risk models beat naive state baseline.
- Compact boosting captures `0.1966` of weighted `persistent_uninsured_h2` events in the top decile.

## Results That Are Supporting Or Caveat Evidence

These results should support the paper but not carry the main claim:

- Step 3 verdict is `RISK_RANKING_ROUND2_MIXED_WITH_CAVEAT`.
- Weighted logistic on the primary outcome has only modest AUC `0.5570`.
- PR AUC is low at `0.0049` for weighted logistic and `0.0046` for compact boosting.
- Calibration is weak and not monotone enough for probability claims.
- Old-pilot benchmark comparison is mixed: AUC delta `-0.0850`, top-decile capture delta `0.0145`.
- `lead1` is still informative in some individual rows even though it does not dominate aggregate primary-window timing.
- Some subgroup families remain unstable, especially `female_group` and `noncitizen_group` in the primary harmful-outcome screen.
- The contrast outcome `broad_exit_resolved_insured_h2` is useful as a guardrail, not as a harm endpoint.

## Small Checks Still Needed Before Drafting

Do only these small checks before drafting. They are table-preparation checks, not new research directions:

1. Build a table-ready extraction file that pulls the main rows for Tables 1-5 from existing CSV/JSON/Markdown outputs.
2. Verify that Table 1 row counts, person counts, support rows, and event rates agree across the outcome audit and feature-stack summary.
3. Create figure-ready CSVs for Figures 3-5 from existing outputs.
4. Decide whether Table 5 should list `weighted_logistic` first for interpretability and `compact_boosting` second for top-decile capture, or sort by top-decile capture.
5. Check that all table notes repeat the non-causal and rank-only caveats.

Do not run new causal models. Do not add new datasets. Do not start a new literature search.

## Next Codex / User Step

The next concrete step is:

`Create table-ready and figure-ready artifacts for the Path A paper from existing outputs.`

Recommended artifact names:

- `scripts/design_diagnostics/build_path_a_paper_tables.py`
- `outputs/design_diagnostics/path_a_table1_sample_support.csv`
- `outputs/design_diagnostics/path_a_table2_timing_stress.csv`
- `outputs/design_diagnostics/path_a_table3_outcome_family.csv`
- `outputs/design_diagnostics/path_a_table4_subgroup_stability.csv`
- `outputs/design_diagnostics/path_a_table5_risk_ranking.csv`
- `outputs/design_diagnostics/path_a_figure3_timing_stress.csv`
- `outputs/design_diagnostics/path_a_figure4_subgroup_stability.csv`
- `outputs/design_diagnostics/path_a_figure5_risk_calibration.csv`

After those artifacts exist, draft a paper skeleton with section headings and table/figure placeholders. Do not write final prose before the table-ready artifacts are locked.
