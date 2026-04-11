# Churn / Unwinding Execution Handoff

Last updated: `2026-04-11`

## Purpose

This is the canonical execution record for the `coverage churn / Medicaid unwinding / continuity of coverage` line.

Use this file as the first entrypoint for future work by:

- the user
- Codex
- any other agent

This file is the interpretation, sequencing, and progress-control layer.

Audit evidence remains in:

- [../outputs/data_audit](../outputs/data_audit)

This file is intentionally not a vague roadmap.

It records:

- the current bottom line
- the locked sequencing decisions
- the next allowed execution steps
- the exact artifact expected from each step
- the update rules that every future agent must follow

## Mandatory Reading Order

Read in this order:

1. [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)
2. [churn_unwinding_round2_execution_handoff.md](churn_unwinding_round2_execution_handoff.md)
3. [churn_unwinding_round2_diagnostics_memo.md](churn_unwinding_round2_diagnostics_memo.md)
4. [churn_unwinding_administrative_burden_memo.md](churn_unwinding_administrative_burden_memo.md)
5. [churn_unwinding_avoidable_churn_memo.md](churn_unwinding_avoidable_churn_memo.md)
6. [churn_unwinding_outcome_reassessment_memo.md](churn_unwinding_outcome_reassessment_memo.md)
7. [churn_unwinding_avoidable_churn_results_briefing.md](churn_unwinding_avoidable_churn_results_briefing.md)
8. [churn_unwinding_next_tests_memo.md](churn_unwinding_next_tests_memo.md)
9. [churn_unwinding_round3_robustness_memo.md](churn_unwinding_round3_robustness_memo.md)
10. [empirical_result_reporting_convention.md](empirical_result_reporting_convention.md)
11. [churn_unwinding_paper_strategy_memo.md](churn_unwinding_paper_strategy_memo.md)
12. [churn_unwinding_progress_record.md](churn_unwinding_progress_record.md)
13. [../outputs/data_audit/sipp_preflight_2026-04-10.md](../outputs/data_audit/sipp_preflight_2026-04-10.md)
14. [../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md](../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md)
15. [churn_targeting_reset_2026-04-10.md](churn_targeting_reset_2026-04-10.md)

Secondary background, if needed:

- [current_exploration_handoff.md](current_exploration_handoff.md)
- [public_batch_acquisition_run_2026-04-10.md](public_batch_acquisition_run_2026-04-10.md)
- [public_data_feasibility_audit.md](public_data_feasibility_audit.md)

## Current Bottom Line

- `SIPP` is the strongest current public-use base for the churn / unwinding line.
- `2024 SIPP` is the clean template release.
- `2024 SIPP` mostly maps to `reference year 2023`, not literal calendar year `2024`.
- A frozen `Step 1` `2024` coverage-layer prototype now exists in [../outputs/prototype](../outputs/prototype).
- The first `TEHC_ST x MONTHCODE` merge to CMS `Updated Medicaid and CHIP Renewal Outcomes` is now complete and rated `usable with caveats`.
- `2018-2023` monthly health insurance variables are not estimation-ready without correction.
- A bounded `2023` correction pilot now exists in [../outputs/prototype/sipp_2023_correction_pilot_audit.md](../outputs/prototype/sipp_2023_correction_pilot_audit.md) and supports the narrow corrected-stack path.
- A formal Step 4 decision now exists in [churn_unwinding_stack_decision.md](churn_unwinding_stack_decision.md): proceed with a narrow phased corrected-stack path, but do not treat the stack as estimation-ready.
- The first recommended backward extension is now complete in [../outputs/prototype/sipp_2022_correction_pilot_audit.md](../outputs/prototype/sipp_2022_correction_pilot_audit.md).
- A constrained diagnostics memo now exists in [churn_unwinding_design_diagnostics_memo.md](churn_unwinding_design_diagnostics_memo.md).
- The first diagnostics outputs now exist in [../outputs/design_diagnostics](../outputs/design_diagnostics).
- For transition outcomes, the empirically clean core unwinding window is now `August-November 2023`, not a December-inclusive window.
- Support is adequate in the core unwinding window, but exposure timing remains unstable across same-month, lagged, and lead alignments.
- In the first descriptive mechanism screen, `pending_pressure` currently looks more informative than `renewal_intensity`, while `procedural_friction` has not yet shown the hoped-for stronger `exit_to_uninsured` signature.
- The first follow-on diagnostics now exist for pre-period falsification and subgroup stability.
- The first falsification screen is not obviously fatal, but the first state-level heterogeneity stability screen does **not** carry a clean baseline-risk ordering into the unwinding year.
- A second-round feature stack now exists with retained person/household subgroup families for `2021-2023`.
- A second-round diagnostics sweep now exists for expanded timing, falsification, and subgroup stability.
- Under the implemented gate rule, the current round-2 verdict is `GO_RISK_ONLY`, not causal escalation.
- A bounded risk-prediction pilot now exists and materially outperforms the naive state-baseline ranking.
- A lightweight `HPS` external cross-check now exists, while `NHIS` has been formally audited as public `national_or_region_descriptive_only` for this design.
- A new `avoidable churn` branch now exists, based on short-horizon `t+2` outcomes.
- Literal `exit -> return to pure Medicaid` is too sparse, but `persistent_uninsured_h2` is usable.
- The strongest current burden candidate is now `backlog_automation_index / same`, not the old `renewal_form_rate / lag1` branch.
- The avoidable-churn branch currently has a `PROMISING_H2_UPGRADE` verdict, with HPS external directions now lining up in the expected way.
- A deep-search reassessment memo now exists for the new avoidable-churn outcomes and burden candidate.
- Future empirical reporting is now governed by a structured result-reporting convention that explicitly requires outcome, exposure, purpose, numbers, interpretation, evaluation, and caveat.
- A plain-language results briefing now exists for the avoidable-churn branch.
- A prioritized next-test memo now exists, including the decision that the next useful dynamic work is timing-robustness rather than classical time-series modeling.
- A round-3 robustness memo now exists, documenting that the harmful-outcome side held up and that the strongest current candidate has improved to `backlog_automation_rank_index / same`.
- `TEHC_ST` is the best current state-month linkage variable.
- `EMDMTH` and `RPUBTYPE2` must not be treated as interchangeable.
- `WPFINWGT` is usable, and the official December-weight rule matters for reference-year estimation.
- The medium-term contribution target still includes possible `causal ML + policy targeting`, if the data structure ultimately supports it.
- The first executable `ML` role remains `risk prediction`; `causal targeting` is an intended later contribution, not the current validated phase.
- The research moat should come from turning unwinding into a `targeting / decision problem`, not from claiming to be the first unwinding paper.

## Locked Decisions

- Use a staged approach.
- Do not start with a corrected `2018-2024` stack.
- First prototype is `2024 release only`.
- First target object is a `2024` person-month coverage / transition prototype plus one audited `TEHC_ST x MONTHCODE` merge to CMS unwinding data.
- Adopt the sequencing rule:
  - `template-first`
  - `linkage-second`
  - `correction-third`
  - `estimation-fourth`
- The default first CMS metric family for the merge audit is:
  - `Medicaid and CHIP Updated Renewal Outcomes`
- Do not collapse the project into descriptive churn only.
- The intended higher-value contribution remains:
  - `person-level churn dynamics`
  - `state-month unwinding environment`
  - possible later `causal ML / heterogeneity / targeting`
- Early validation steps are still required because `causal ML` is only useful if the treatment, timing, and outcome layers are credible.
- If that merge proves not credible, record failure cleanly and stop escalation before opening new phases.

Working defaults to validate in Step 1:

- `state` candidate: `TEHC_ST`
- exclude non-state `TEHC_ST` codes such as `60` and `61`
- `time` candidate: `MONTHCODE = 1..12`, interpreted as reference months in `2023`
- `pure Medicaid` candidate: `EMDMTH = 1`
- `uninsured` candidate: `RHLTHMTH = 2`
- `public coverage` candidate: `RPUBMTH = 1`
- treat `RPUBTYPE2` as broader than pure Medicaid
- keep `EOTMTH` and other ambiguous coverage separate
- define next-month transition outcomes only on `MONTHCODE = 1..11`

## Execution Ladder

### Step 1

Freeze the `2024` monthly coverage layer and transition definitions.

The goal is to produce one audited `2024` release person-month file that defines:

- insured
- uninsured
- broad public coverage
- pure Medicaid
- any retained ambiguous / other coverage flags
- one-step transition outcomes

### Step 2

Run the first audited `TEHC_ST x MONTHCODE` merge to one chosen CMS unwinding metric family.

The default metric family is:

- `Medicaid and CHIP Updated Renewal Outcomes`

This step is a merge audit, not a causal estimation step.

### Step 3

Write the `2018-2023` correction specification.

This is the point where the project decides exactly how the official Census user notes will be translated into repair rules, avoid rules, and burden estimates.

### Step 4

Make the go / no-go decision on a corrected multi-year stack.

This decision must be based on:

- the Step 2 merge verdict
- the Step 3 correction burden and feasibility assessment

If the answer is `go`, the next downstream phase should evaluate whether the corrected stack is strong enough for:

- `heterogeneity estimation`
- possible `causal ML`
- eventual `policy targeting`

## Post-Step-3 Clarification Record

This section records clarification questions that came up after the first correction pilot.

It is here to prevent future agents from misreading the project state.

### Clarification 1: what "correction" means in this project

`Step 3` correction does **not** mean a full-file repair of all variables.

Current correction scope is intentionally narrow:

- the monthly insurance measurement layer
- the churn-label layer derived from it
- the variables needed to construct:
  - `pure_medicaid_t`
  - `uninsured_t`
  - `medicaid_exit_next`
  - `medicaid_exit_to_uninsured_next`

This does **not** yet include:

- all high-dimensional covariates
- all downstream outcomes
- a full harm-outcome layer
- a full targeting-feature matrix

### Clarification 2: why the correction matters

The official Census user notes do **not** provide a final corrected churn outcome for this project.

They identify measurement problems in the monthly insurance layer.

The project cares because those problems contaminate the project's own churn outcomes.

The `2023` correction pilot showed that this is a real issue, not a theoretical one:

- corrected strict Medicaid month counts changed materially
- corrected one-step exit counts rose materially
- therefore raw `2018-2023` monthly insurance fields should not be treated as harmless for churn construction

Current reading:

- the correction **does** affect outcome construction
- the core public / Medicaid / uninsured correction path looks workable
- the private layer still requires conservative handling because `RPRIMTH` was not safely rebuildable from the currently used local fields

### Clarification 3: how to interpret `2018-2024`

`2018-2024` should not be described as one seamless seven-year individual panel.

Safer interpretation:

- annual public-use releases are `person-month` files with panel structure
- later releases are overlapping-panels files
- a corrected multi-year stack would be a stacked annual-release `person-month` time series
- it would **not** by itself prove a single continuous seven-year person panel

This distinction matters for later `causal ML / targeting` claims.

### Clarification 4: why pre-unwinding years still matter

`Unwinding` is concentrated in recent years.

That does **not** make earlier corrected years irrelevant.

For an unwinding-focused design, earlier corrected years are useful as:

- pre-period support
- baseline churn-risk support
- baseline heterogeneity support
- validation support for outcome construction

They should **not** be described as treated unwinding years.

The estimand should remain anchored on unwinding-era variation if the project stays on the current main line.

### Clarification 5: what a corrected multi-year stack would add for `causal ML`

A corrected multi-year stack would help later `DiD / event-study / DML / causal ML` work by:

- reducing label noise in churn outcomes
- expanding the pre-period
- increasing heterogeneity support
- improving training / validation support for later risk ranking or targeting work

But it does **not** complete identification by itself.

Even after a corrected stack exists, the project would still need:

- credible unwinding-era treatment timing or exposure interpretation
- stable state-month linkage logic
- a defensible bridge from heterogeneity to targeting

### Clarification 6: what Step 1 and Step 2 already contributed

`Step 1` and `Step 2` remain directly useful even under the project's higher-value `causal ML / targeting` ambition.

They already validated two necessary building blocks:

- a prototype person-month churn outcome layer
- a real external `state-month` unwinding context layer

Those are prerequisites for any later heterogeneity or targeting design.

## Step Tracker

| Step | Status | Owner | Input dependencies | Output artifact | Closure test | Next unlocked step |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Freeze `2024` coverage layer | `Completed` | `Codex` | [../outputs/data_audit/sipp_preflight_2026-04-10.md](../outputs/data_audit/sipp_preflight_2026-04-10.md), [../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md](../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md) | [../outputs/prototype/sipp_2024_coverage_layer_spec.md](../outputs/prototype/sipp_2024_coverage_layer_spec.md); [../outputs/prototype/sipp_2024_person_month_flags.parquet](../outputs/prototype/sipp_2024_person_month_flags.parquet); [../outputs/prototype/sipp_2024_coverage_layer_summary.json](../outputs/prototype/sipp_2024_coverage_layer_summary.json) | Passed on `2026-04-10`: variable definitions frozen, exclusions stated, transition outcomes defined, and artifact paths recorded. | Step 2 |
| 2. Merge `TEHC_ST x MONTHCODE` to CMS | `Completed` | `Codex` | Step 1 outputs; staged Medicaid unwinding reference materials | [../outputs/prototype/sipp_2024_state_month_merge_audit.md](../outputs/prototype/sipp_2024_state_month_merge_audit.md); [../outputs/prototype/sipp_2024_cms_updated_renewal_outcomes_merged.parquet](../outputs/prototype/sipp_2024_cms_updated_renewal_outcomes_merged.parquet); [../outputs/prototype/cms_updated_renewal_outcomes_state_month_2023.parquet](../outputs/prototype/cms_updated_renewal_outcomes_state_month_2023.parquet); [../outputs/prototype/sipp_2024_cms_updated_renewal_merge_summary.json](../outputs/prototype/sipp_2024_cms_updated_renewal_merge_summary.json) | Passed on `2026-04-10`: exact CMS metric family named, month alignment documented, matched / unmatched states documented, and merge rated `usable with caveats`. | Step 3 |
| 3. Write `2018-2023` correction spec | `Completed` | `Codex` | Step 1 outputs; Step 2 merge verdict; official Census user notes | [../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md](../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md); [../outputs/data_audit/sipp_2018_2023_correction_map.csv](../outputs/data_audit/sipp_2018_2023_correction_map.csv) | Passed on `2026-04-10`: correction rules are listed by year group, repaired vs avoided variables are identified, implementation burden is estimated, and stack feasibility is stated. | Step 4 |
| 4. Make stack go / no-go decision | `Completed` | `Codex` | Step 2 merge audit; Step 3 correction spec; 2023 correction pilot | [churn_unwinding_stack_decision.md](churn_unwinding_stack_decision.md) | Passed on `2026-04-10`: a formal scoped `GO` is recorded, immediate `NO-GO` items are named, and the next execution path is explicitly set to `2022` extension plus later design diagnostics. | Execution beyond this handoff |

## Completion Log

### `2026-04-10` - Audit groundwork completed before prototype execution

- Actor: `Codex`
- Files produced:
  - [../outputs/data_audit/sipp_preflight_2026-04-10.md](../outputs/data_audit/sipp_preflight_2026-04-10.md)
  - [../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md](../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md)
  - [../outputs/data_audit/sipp_warning_registry.csv](../outputs/data_audit/sipp_warning_registry.csv)
  - [../outputs/data_audit/sipp_core_variable_stability.csv](../outputs/data_audit/sipp_core_variable_stability.csv)
  - [../outputs/data_audit/sipp_variable_triage.csv](../outputs/data_audit/sipp_variable_triage.csv)
- What was learned:
  - `SIPP` remains the strongest public-use base.
  - `2024 SIPP` is a structurally coherent template release.
  - `2024 SIPP` mostly corresponds to `reference year 2023`.
  - `2018-2023` monthly health insurance variables are not safe for naive stacking.
  - `TEHC_ST` is structurally plausible for state-month linkage.
- What changed in the allowed next actions:
  - The project is allowed to start Step 1.
  - The project is not yet allowed to start Step 2, Step 3, or Step 4.

### `2026-04-10` - Canonical execution handoff created

- Actor: `Codex`
- Files produced:
  - [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)
- What was learned:
  - The project needed one execution-control file to prevent future agents from splitting the narrative across unrelated notes.
- What changed in the allowed next actions:
  - Future agents must update this canonical handoff after any meaningful step or blocker.
  - Older notes are now background or evidence records, not execution control files.

### `2026-04-10` - Step 1 prototype coverage layer completed

- Actor: `Codex`
- Files produced:
  - [../outputs/prototype/sipp_2024_coverage_layer_spec.md](../outputs/prototype/sipp_2024_coverage_layer_spec.md)
  - [../outputs/prototype/sipp_2024_person_month_flags.parquet](../outputs/prototype/sipp_2024_person_month_flags.parquet)
  - [../outputs/prototype/sipp_2024_coverage_layer_summary.json](../outputs/prototype/sipp_2024_coverage_layer_summary.json)
  - [../scripts/prototype/build_sipp_2024_coverage_layer.py](../scripts/prototype/build_sipp_2024_coverage_layer.py)
- What was learned:
  - The `2024` template release can be frozen into a valid-state person-month prototype without duplicate keys.
  - The retained file keeps all `MONTHCODE = 1..12` and observed `SPANEL = 2021, 2022, 2023, 2024`.
  - `TEHC_ST = 60` and `TEHC_ST = 61` are the non-state codes excluded from the Step 1 prototype.
  - The first frozen one-step outcomes are now `medicaid_exit_next` and `medicaid_exit_to_uninsured_next`, defined only inside the eligible consecutive-month Medicaid universe.
  - `RPUBTYPE2` remains broader than strict Medicaid and is retained separately from `EMDMTH`.
- What changed in the allowed next actions:
  - The project is now allowed to start Step 2.
  - The project is still not allowed to start Step 3 or Step 4 before the Step 2 merge verdict is recorded.

### `2026-04-10` - Step 2 state-month merge audit completed

- Actor: `Codex`
- Files produced:
  - [../outputs/prototype/sipp_2024_state_month_merge_audit.md](../outputs/prototype/sipp_2024_state_month_merge_audit.md)
  - [../outputs/prototype/sipp_2024_cms_updated_renewal_outcomes_merged.parquet](../outputs/prototype/sipp_2024_cms_updated_renewal_outcomes_merged.parquet)
  - [../outputs/prototype/cms_updated_renewal_outcomes_state_month_2023.parquet](../outputs/prototype/cms_updated_renewal_outcomes_state_month_2023.parquet)
  - [../outputs/prototype/sipp_2024_cms_updated_renewal_merge_summary.json](../outputs/prototype/sipp_2024_cms_updated_renewal_merge_summary.json)
  - [../scripts/prototype/build_sipp_2024_cms_updated_renewal_merge.py](../scripts/prototype/build_sipp_2024_cms_updated_renewal_merge.py)
- What was learned:
  - The first `TEHC_ST x MONTHCODE` merge to the official CMS `Updated Medicaid and CHIP Renewal Outcomes` metric family works mechanically.
  - The merge is strongest from `August-December 2023`, where CMS state coverage is complete for `50 states + DC`.
  - `January-February 2023` remain unmatched in this Step 2 setup because the selected metric family is not staged for those reporting periods.
  - `March-July 2023` have partial state coverage in the chosen CMS metric family, so early-month merge weakness is a CMS source-coverage issue rather than a SIPP key failure.
  - The CMS reporting month must be interpreted as a `renewal due / updated disposition` month, not a clean person-level disenrollment month.
- What changed in the allowed next actions:
  - The project is now allowed to start Step 3.
  - The Step 2 merge verdict is `usable with caveats`, so later work may continue, but no causal claims should be opened from the merge alone.

### `2026-04-10` - Step 3 correction specification completed

- Actor: `Codex`
- Files produced:
  - [../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md](../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md)
  - [../outputs/data_audit/sipp_2018_2023_correction_map.csv](../outputs/data_audit/sipp_2018_2023_correction_map.csv)
- What was learned:
  - The project does **not** need an all-variable correction pass at this stage.
  - The narrow correction target should stay on the monthly insurance / churn layer that defines `pure Medicaid`, `uninsured`, and one-step exit outcomes.
  - `2018-2023` should be handled in year groups rather than as one homogeneous block: `2018-2020`, `2021`, and `2022-2023`.
  - A corrected multi-year churn stack looks realistic enough to justify implementation, but not yet strong enough to treat as estimation-ready or `causal ML`-ready.
  - The recommended first implementation pilot year is `2023`, because it is closest to the clean `2024` template and still has annual recodes available for bounded checks.
- What changed in the allowed next actions:
  - The project is now allowed to start Step 4.
  - The project is also allowed to begin a narrow correction implementation pilot, provided that Step 4 records the stack decision clearly.

### `2026-04-10` - 2023 correction pilot completed

- Actor: `Codex`
- Files produced:
  - [../outputs/prototype/sipp_2023_corrected_person_month_flags.parquet](../outputs/prototype/sipp_2023_corrected_person_month_flags.parquet)
  - [../outputs/prototype/sipp_2023_correction_pilot_summary.json](../outputs/prototype/sipp_2023_correction_pilot_summary.json)
  - [../outputs/prototype/sipp_2023_correction_pilot_audit.md](../outputs/prototype/sipp_2023_correction_pilot_audit.md)
  - [../scripts/prototype/build_sipp_2023_corrected_coverage_layer.py](../scripts/prototype/build_sipp_2023_corrected_coverage_layer.py)
- What was learned:
  - The `2023` release can support a bounded correction pilot on the monthly insurance / churn layer without breaking the person-month structure.
  - Official spell-overrun corrections materially change strict Medicaid month, broad public month, and one-step exit outcomes even though the directly affected rows are a small minority of the file.
  - The public / Medicaid correction path looks operationally credible.
  - A new implementation caution surfaced: direct formula-based rebuilding of `RPRIMTH` from the currently used local fields does not safely reproduce the raw private-coverage recode, so the private layer should remain conservative for now.
- What changed in the allowed next actions:
  - The project now has a concrete pilot basis for `Step 4`.
  - If the stack decision is positive, the next extension target should be `2022`.

### `2026-04-10` - Post-Step-3 clarification record added

- Actor: `Codex`
- Files updated:
  - [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)
  - [../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md](../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md)
- What was learned:
  - `Step 3` correction should be read as a narrow repair of the monthly insurance / churn layer, not a full-file clean.
  - A corrected multi-year stack would help the unwinding line mainly through pre-period, baseline-risk, and heterogeneity support.
  - The stack would strengthen later `DiD / DML / causal ML` possibilities, but it would not by itself finish identification.
- What changed in the allowed next actions:
  - Future agents should preserve the unwinding-focused estimand when discussing multi-year extensions.
  - Future agents should not describe the corrected stack as a seamless seven-year panel or as automatically `causal ML`-ready.

### `2026-04-10` - Step 4 stack decision completed

- Actor: `Codex`
- Files produced:
  - [churn_unwinding_stack_decision.md](churn_unwinding_stack_decision.md)
- What was learned:
  - The corrected-stack path should continue, but only as a narrow phased implementation path.
  - The first backward extension target should be `2022`, not an immediate full backfill through `2018-2020`.
  - The corrected stack is strategically useful for unwinding-focused `DiD / DML / causal ML` possibilities, but it is still not estimation-ready or targeting-ready.
- What changed in the allowed next actions:
  - Future execution may proceed to `2022` correction implementation.
  - After `2022`, the next planning artifact should be a constrained design-diagnostics memo rather than immediate full estimation.

### `2026-04-10` - 2022 correction extension completed

- Actor: `Codex`
- Files produced:
  - [../outputs/prototype/sipp_2022_corrected_person_month_flags.parquet](../outputs/prototype/sipp_2022_corrected_person_month_flags.parquet)
  - [../outputs/prototype/sipp_2022_correction_pilot_summary.json](../outputs/prototype/sipp_2022_correction_pilot_summary.json)
  - [../outputs/prototype/sipp_2022_correction_pilot_audit.md](../outputs/prototype/sipp_2022_correction_pilot_audit.md)
  - [../scripts/prototype/build_sipp_2022_corrected_coverage_layer.py](../scripts/prototype/build_sipp_2022_corrected_coverage_layer.py)
- What was learned:
  - The corrected-stack path remains stable after extending one year backward from the `2023` pilot to the `2022` release.
  - The special `2018-2022` Medicaid end-month repair is real but small in row count and manageable in implementation.
  - Annual recodes in `2022` are useful as bounded validation checks, but they do not replace corrected monthly churn logic.
  - The private-coverage caution remains unresolved, so the monthly public / Medicaid side should remain the project's reliable core.
- What changed in the allowed next actions:
  - The project is now ready to shift from stack-feasibility testing to a constrained design-diagnostics memo.
  - Any further backfill to `2021` or `2018-2020` should be justified by that diagnostics memo rather than treated as automatic.

### `2026-04-10` - Constrained design-diagnostics memo created

- Actor: `Codex`
- Files produced:
  - [churn_unwinding_design_diagnostics_memo.md](churn_unwinding_design_diagnostics_memo.md)
- What was learned:
  - The first design phase should stay unwinding-anchored and use the corrected `2022` and `2023` releases mainly as pre-period support.
  - `August-December 2023` is the safest current core diagnostics window in the selected CMS metric family.
  - The first mechanism family to test should be `procedural friction`, followed by `renewal intensity`, then `pending pressure`.
  - The project should earn later `DiD / DML / causal ML` work through support, timing, mechanism, and falsification diagnostics rather than skipping directly to estimation.
- What changed in the allowed next actions:
  - The next active empirical work should produce the first diagnostics outputs under `outputs/design_diagnostics/`.
  - Additional year backfill should remain secondary until the diagnostics results justify it.

### `2026-04-10` - First design-diagnostics batch completed

- Actor: `Codex`
- Files produced:
  - [../outputs/design_diagnostics/churn_unwinding_support_audit.md](../outputs/design_diagnostics/churn_unwinding_support_audit.md)
  - [../outputs/design_diagnostics/churn_unwinding_timing_sensitivity.md](../outputs/design_diagnostics/churn_unwinding_timing_sensitivity.md)
  - [../outputs/design_diagnostics/churn_unwinding_mechanism_screen.md](../outputs/design_diagnostics/churn_unwinding_mechanism_screen.md)
  - [../outputs/design_diagnostics/churn_unwinding_first_diagnostics_summary.json](../outputs/design_diagnostics/churn_unwinding_first_diagnostics_summary.json)
  - [../outputs/design_diagnostics/yearly_churn_support_summary.csv](../outputs/design_diagnostics/yearly_churn_support_summary.csv)
  - [../outputs/design_diagnostics/unwinding_state_month_transition_cells.csv](../outputs/design_diagnostics/unwinding_state_month_transition_cells.csv)
  - [../outputs/design_diagnostics/unwinding_window_support_summary.csv](../outputs/design_diagnostics/unwinding_window_support_summary.csv)
  - [../outputs/design_diagnostics/unwinding_timing_sensitivity_summary.csv](../outputs/design_diagnostics/unwinding_timing_sensitivity_summary.csv)
  - [../outputs/design_diagnostics/unwinding_mechanism_screen_summary.csv](../outputs/design_diagnostics/unwinding_mechanism_screen_summary.csv)
  - [../scripts/design_diagnostics/build_churn_unwinding_first_diagnostics.py](../scripts/design_diagnostics/build_churn_unwinding_first_diagnostics.py)
- What was learned:
  - The corrected `2022` and `2023` releases plus the merged `2024` file provide enough support to run a first unwinding-linked diagnostics pass.
  - For transition outcomes, the empirically clean core window is `August-November 2023`; `December 2023` has no next-month transition outcome in the current setup.
  - The core unwinding window has full exposure support across `50 states + DC`, but timing remains unstable across same-month, lagged, and lead alignments.
  - In this first descriptive mechanism screen, `pending_pressure` currently looks more informative than `renewal_intensity`, while `procedural_friction` has not yet dominated `exit_to_uninsured`.
  - The project should stay in diagnostics mode rather than escalate directly to `DiD / DML / causal ML`.
- What changed in the allowed next actions:
  - The next active work should be constrained falsification and subgroup-stability diagnostics, or a refined exposure-timing audit.
  - Additional year backfill remains secondary until the diagnostics become more coherent.

### `2026-04-10` - Follow-on diagnostics completed

- Actor: `Codex`
- Files produced:
  - [../outputs/design_diagnostics/churn_unwinding_preperiod_falsification.md](../outputs/design_diagnostics/churn_unwinding_preperiod_falsification.md)
  - [../outputs/design_diagnostics/churn_unwinding_heterogeneity_stability.md](../outputs/design_diagnostics/churn_unwinding_heterogeneity_stability.md)
  - [../outputs/design_diagnostics/preperiod_falsification_summary.csv](../outputs/design_diagnostics/preperiod_falsification_summary.csv)
  - [../outputs/design_diagnostics/heterogeneity_stability_summary.csv](../outputs/design_diagnostics/heterogeneity_stability_summary.csv)
  - [../outputs/design_diagnostics/later_exposure_state_tertiles.csv](../outputs/design_diagnostics/later_exposure_state_tertiles.csv)
  - [../outputs/design_diagnostics/baseline_state_risk_tertiles.csv](../outputs/design_diagnostics/baseline_state_risk_tertiles.csv)
  - [../outputs/design_diagnostics/churn_unwinding_follow_on_diagnostics_summary.json](../outputs/design_diagnostics/churn_unwinding_follow_on_diagnostics_summary.json)
  - [../scripts/design_diagnostics/build_churn_unwinding_follow_on_diagnostics.py](../scripts/design_diagnostics/build_churn_unwinding_follow_on_diagnostics.py)
- What was learned:
  - The first pre-period falsification screen is not obviously fatal: later `2023` exposure tertiles do not simply map onto very large, uniform baseline churn gaps in `2021-2022`.
  - The first heterogeneity-stability screen is more cautionary: state baseline-risk ordering from pooled `2021-2022` does not carry cleanly into the `2023` unwinding year.
  - This means the project still has room to test identification, but it should not yet interpret crude state-level risk ordering as a stable targeting rule.
  - The next empirical gains are more likely to come from refined subgroup definitions or richer future feature layers than from another automatic year backfill.
- What changed in the allowed next actions:
  - The next active work should refine falsification, timing, and subgroup logic before any stronger `DiD / DML / causal ML` escalation.
  - Future targeting discussion should stay explicitly provisional until richer subgroup structure is available.

## Open Questions / Active Risks

1. The biggest current risk is now conceptual rather than mechanical: the CMS reporting month is a `renewal due / updated disposition` month and may not line up tightly enough with observed person-month coverage loss to support stronger causal interpretation.
2. The next design risk is timing interpretation: the first diagnostics batch showed modest and unstable same / lag / lead relationships across exposure families.
3. A linked source-coverage risk remains for early `2023`: the selected CMS metric family has partial state coverage in `March-July 2023`, even though the core `August-November 2023` transition window is complete.
4. A mechanism-ranking risk remains unresolved: `pending_pressure` currently looks more informative than `renewal_intensity`, while the intended flagship `procedural_friction` mechanism has not yet clearly dominated `exit_to_uninsured`.
5. A subgroup-stability risk is now explicit: crude state baseline-risk ordering from pooled `2021-2022` does not carry cleanly into the `2023` unwinding year, so later targeting logic still needs richer subgroup structure.
6. Even with a phased corrected stack, a remaining design risk is whether the unwinding-era design becomes strong enough for the project's intended `causal ML / targeting` contribution rather than only descriptive or predictive work.
7. A secondary implementation risk is that `FINYR2`, `FINYR3`, and replicate-weight files are not currently staged locally, so any design that truly requires them will need an explicit acquisition step later.
8. The `2023` pilot showed that the public / Medicaid correction path is workable, but it also surfaced a caution that remains unresolved: direct formula-based rebuilding of `RPRIMTH` from the currently used local source fields diverges materially from the raw recode and should remain conservative until separately resolved.

## Update Protocol

- Any agent must update this file after finishing a meaningful step.
- No agent should mark a step `Completed` without naming the output artifact.
- No agent should open a new phase until the prior phase's closure test is recorded.
- If a step fails, record failure cleanly and stop escalation.
- Do not drift into a new phase just to preserve momentum.

Phase-gate rules:

- Do not start Step 2 until Step 1 has:
  - frozen variable definitions
  - stated exclusions
  - defined transition outcomes
  - named the prototype artifact path
- Do not start Step 3 until Step 2 has:
  - named the exact CMS metric family used
  - documented month alignment
  - documented matched / unmatched states
  - stated whether the merge is `usable`, `usable with caveats`, or `not credible`
- Do not start Step 4 until Step 3 has:
  - listed correction rules by year group
  - identified which variables are repaired vs avoided
  - estimated implementation burden
  - stated whether a corrected stack is realistic now

Interpretation rules:

- [../outputs/data_audit](../outputs/data_audit) remains the evidence layer.
- This file remains the execution-control layer.
- [churn_targeting_reset_2026-04-10.md](churn_targeting_reset_2026-04-10.md) remains strategic framing, not step control.
- [current_exploration_handoff.md](current_exploration_handoff.md) remains broader background, not the canonical next-step guide.
