# Churn / Unwinding Design Diagnostics Memo

Last updated: `2026-04-10`

## Purpose

This memo defines the first constrained design-diagnostics phase for the churn / unwinding project.

It comes after:

- the `2024` template-year freeze
- the first CMS `state x month` merge audit
- the `2018-2023` correction specification
- the `2023` and `2022` correction pilots

This memo is not a final model plan.

It is a diagnostics plan whose job is to answer:

- what the most defensible unwinding-era exposure definition is
- what the safest first design window is
- which mechanism families are worth testing first
- whether the project should first look more like:
  - `risk prediction`
  - `DiD / event-study / DML heterogeneity`
  - or a narrower mechanism-validation exercise

## Governing Evidence

This memo is based on:

- [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)
- [churn_unwinding_stack_decision.md](churn_unwinding_stack_decision.md)
- [churn_targeting_reset_2026-04-10.md](churn_targeting_reset_2026-04-10.md)
- [../outputs/data_audit/sipp_preflight_2026-04-10.md](../outputs/data_audit/sipp_preflight_2026-04-10.md)
- [../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md](../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md)
- [../outputs/prototype/sipp_2024_coverage_layer_spec.md](../outputs/prototype/sipp_2024_coverage_layer_spec.md)
- [../outputs/prototype/sipp_2024_state_month_merge_audit.md](../outputs/prototype/sipp_2024_state_month_merge_audit.md)
- [../outputs/prototype/sipp_2023_correction_pilot_audit.md](../outputs/prototype/sipp_2023_correction_pilot_audit.md)
- [../outputs/prototype/sipp_2022_correction_pilot_audit.md](../outputs/prototype/sipp_2022_correction_pilot_audit.md)

## Current Bottom-Line Reading

The project is now beyond the stage of asking whether the churn / unwinding path is real.

That path is real enough to continue.

What remains unresolved is not the existence of a path, but the shape of the first defensible design.

The strongest current reading is:

- the project should stay anchored on `unwinding`, not widen into general churn too early
- the project should use corrected earlier years mainly as support, not as treated unwinding years
- the next phase should test design credibility before opening full estimation or `causal ML`

## Status Update: First Diagnostics Batch

The first constrained diagnostics batch has now been completed.

Produced outputs:

- [../outputs/design_diagnostics/churn_unwinding_support_audit.md](../outputs/design_diagnostics/churn_unwinding_support_audit.md)
- [../outputs/design_diagnostics/churn_unwinding_timing_sensitivity.md](../outputs/design_diagnostics/churn_unwinding_timing_sensitivity.md)
- [../outputs/design_diagnostics/churn_unwinding_mechanism_screen.md](../outputs/design_diagnostics/churn_unwinding_mechanism_screen.md)
- [../outputs/design_diagnostics/churn_unwinding_first_diagnostics_summary.json](../outputs/design_diagnostics/churn_unwinding_first_diagnostics_summary.json)

Current reading after that batch:

- support is adequate for a first unwinding-linked diagnostics pass
- for transition outcomes, the empirically clean core window is `August-November 2023`
- timing is still unstable across same-month, lagged, and lead alignments
- `pending_pressure` currently looks more informative than `renewal_intensity` in the first descriptive mechanism screen
- the intended flagship mechanism, `procedural_friction`, has not yet shown the hoped-for stronger `exit_to_uninsured` signature
- the first pre-period falsification screen is not obviously fatal
- the first state-level heterogeneity stability screen does **not** carry clean baseline-risk ordering into the unwinding year

Implication:

- the project should continue in constrained diagnostics mode
- it should not jump directly to `DiD / DML / causal ML`
- the next diagnostics should focus on richer falsification, better subgroup structure, and refined timing / exposure interpretation

## The Minimal Diagnostic Stack

The first design-diagnostics phase should treat the following as the minimum working stack:

| Release file | Main reference-year role | Status in workspace | Diagnostic role |
| --- | --- | --- | --- |
| `2022 SIPP release` | mainly `reference year 2021` | corrected pilot completed | pre-period support |
| `2023 SIPP release` | mainly `reference year 2022` | corrected pilot completed | pre-period support |
| `2024 SIPP release` | mainly `reference year 2023` | clean template + CMS merge completed | unwinding-era outcome and exposure layer |

This means the first diagnostics phase does **not** require immediate backfill to `2021` or `2018-2020`.

Those earlier years should remain optional until the constrained diagnostics say they are worth the burden.

## Target Research Question For This Phase

For diagnostics, the research question should stay narrowly framed:

- can person-month Medicaid-related churn outcomes in `SIPP` be credibly linked to state-month unwinding pressure in a way that supports later heterogeneity and targeting work?

This is narrower than the eventual paper.

It is also narrower than generic "who churns?" work.

The key point is to validate the unwinding-linked design first.

## Core Outcome Layer For Diagnostics

The first diagnostics phase should keep the outcome layer narrow and stable.

Primary outcomes:

- `pure_medicaid_t`
- `medicaid_exit_next`
- `medicaid_exit_to_uninsured_next`

Secondary diagnostic outcome:

- `uninsured_t`

Do **not** widen the first diagnostics pass to:

- downstream care-utilization outcomes
- spending outcomes
- uninsured-care outcomes
- broad harm batteries

Those can wait until the unwinding-linked churn layer is better understood.

## Candidate Exposure Families

The first diagnostics phase should not act as if there is already one validated treatment.

It should compare a small menu of exposure candidates.

### Exposure Family A: renewal intensity

Candidate variables:

- `cms_updated_renewal_due_n`
- corresponding rate versions where usable

Interpretation:

- administrative workload / renewal pressure

Why it matters:

- this is the broadest state-month pressure concept
- it does not require claiming that disenrollment timing is exact

Risk:

- it may be too diffuse to map tightly to observed individual coverage loss

### Exposure Family B: procedural friction

Candidate variables:

- `cms_updated_procedural_termination_n`
- `cms_updated_procedural_share_of_terminated`

Interpretation:

- administrative or procedural loss channel

Why it matters:

- this is the most substantively aligned mechanism for an unwinding-linked churn paper
- it is the clearest bridge from descriptive churn to a targeting / decision problem

Risk:

- the numerator and denominator are still defined at the state-month reporting level, not the individual event-time level

### Exposure Family C: administrative backlog / pending pressure

Candidate variables:

- `cms_updated_pending_n`
- pending-rate versions where usable

Interpretation:

- backlog, unresolved renewals, or delayed disposition pressure

Why it matters:

- this may capture capacity strain rather than only formal terminations
- it could be useful if procedural-termination measures are too sparse or too unstable

Risk:

- it is one step further from clean individual disenrollment timing

## Exposure Family Priority Order

The first diagnostics pass should prioritize the exposure families in this order:

1. `procedural friction`
2. `renewal intensity`
3. `administrative backlog / pending pressure`

Original reason:

- `procedural friction` is the closest mechanism match to the project's intended contribution
- `renewal intensity` is the strongest fallback if procedural measures are too noisy
- `pending pressure` should be treated as a supplementary mechanism, not the flagship treatment candidate

First-batch empirical update:

- keep this priority order for now as a theory-first ordering
- but note that the first descriptive screen did **not** confirm it empirically
- `pending_pressure` currently looks more informative than `renewal_intensity`
- `procedural_friction` remains substantively important, but it now needs stronger timing and falsification checks before being treated as the obvious lead mechanism

## Safe Design Windows

The first diagnostics phase should use explicit window tiers rather than one undifferentiated `2023` period.

### Tier 1: core window

Use:

- `August-November 2023` for transition outcomes
- `August-December 2023` only if a later diagnostic explicitly uses contemporaneous level outcomes without a next-month transition requirement

Why:

- this is the first period where the selected CMS metric family has complete `50 states + DC` coverage
- `December 2023` has no next-month outcome inside the current transition construction
- it is the cleanest state-month support window currently documented

Interpretation:

- this should be the default first diagnostics window

### Tier 2: extended exploratory window

Use:

- `March-December 2023`

Why:

- it captures more of the unwinding year
- but it inherits early source-coverage weakness from the CMS series

Interpretation:

- acceptable for sensitivity and support checks
- not the cleanest first headline window

### Tier 3: pre-period support window

Use:

- `reference year 2021` from the corrected `2022` release
- `reference year 2022` from the corrected `2023` release

Interpretation:

- untreated support years
- useful for baseline risk, label stability, and falsification-style diagnostics
- not unwinding-treated years

## First Mechanism Tests To Run

The project should not single-bet on one story before diagnostics.

But it should constrain the first mechanism menu.

### Mechanism 1: administrative Medicaid loss

Question:

- do higher procedural-friction state-months line up more strongly with `medicaid_exit_next` and especially `medicaid_exit_to_uninsured_next`?

Why first:

- this is the cleanest mechanism for an unwinding story

What would count as encouraging:

- stronger alignment for `exit_to_uninsured` than for broad Medicaid exit

### Mechanism 2: renewal workload pressure

Question:

- do higher renewal-due state-months line up with higher observed churn risk even when procedural metrics are not emphasized?

Why second:

- this tests whether the project has a usable broader pressure story if procedural metrics are unstable

What would count as encouraging:

- monotone or near-monotone risk gradients across workload intensity bins

### Mechanism 3: backlog or unresolved processing pressure

Question:

- do high-pending state-months show signs of churn instability consistent with administrative bottlenecks?

Why third:

- this is a useful supporting mechanism, but not the first claim to lead with

What would count as encouraging:

- evidence that backlog pressure is not just noise and relates to the churn layer in a coherent direction

## First Diagnostics To Run

The first diagnostics phase should produce decision-quality checks before any broader estimation.

### Diagnostic 1: support and overlap audit

Goal:

- verify how much usable state-month support exists in the core window for each exposure family

Questions:

- how many state-month cells remain after non-missing exposure requirements?
- how much within-window spread exists across states?
- are exposure distributions dominated by only a few extreme states or months?

### Diagnostic 2: timing sensitivity audit

Goal:

- test how sensitive the relationship is to month alignment choices

Minimum comparisons:

- same-month exposure
- one-month lag
- one-month lead

Why:

- the CMS reporting month is a `renewal due / updated disposition` month, not a clean individual disenrollment month

### Diagnostic 3: mechanism specificity audit

Goal:

- check whether the most policy-relevant exposure family behaves more like the intended mechanism than the weaker alternatives

Example reading:

- if procedural friction tracks `exit_to_uninsured` better than generic workload does, that is stronger evidence for the intended administrative-loss story

### Diagnostic 4: pre-period falsification audit

Goal:

- test whether the proposed exposure ranking is simply proxying for pre-existing state churn differences

Working approach:

- classify states by later `2023` exposure intensity
- compare corrected `2021` and `2022` baseline churn patterns across those groups

Why:

- if pre-period differences are already large and unstable, later unwinding interpretation weakens

### Diagnostic 5: heterogeneity stability screen

Goal:

- check whether the same broad subgroup patterns appear across the corrected pre-period years and the unwinding-era year

Allowed first-pass subgroup dimensions:

- income / poverty status if already available in the corrected files
- broad age groups
- household composition or child-presence measures if straightforward
- state baseline public-coverage intensity if constructible cleanly

This should remain a simple stability screen, not full `causal ML`.

## What Should Not Happen In This Phase

The following should remain out of scope:

- final paper writing
- final mechanism selection based on preferred results only
- broad downstream outcome testing
- final `DiD` or `DML` estimation
- final `causal forest` or `policy tree` work
- broad cross-dataset validator integration

The point of this memo is to decide what is worth estimating later, not to skip the diagnostic stage.

## First Downstream Path Decision Rules

After the constrained diagnostics run, the next path should be chosen by rule rather than by instinct.

### Path 1: move first to `risk prediction`

Choose this if:

- the churn-label layer is stable
- exposure timing remains noisy
- mechanism evidence is suggestive but not yet strong enough for a clean policy-exposure interpretation

### Path 2: move first to `DiD / event-study / DML heterogeneity`

Choose this if:

- the core window behaves coherently
- timing sensitivity is manageable
- pre-period falsification does not look fatal
- at least one exposure family shows a defensible mechanism pattern

### Path 3: remain in design-repair mode

Choose this if:

- exposure timing is too unstable
- mechanism differences are incoherent
- pre-period patterns already look too divergent
- or corrected-stack quality starts to weaken outside the late-year group

## Recommended Next Empirical Artifacts

The first implementation round after this memo aimed to produce:

- `outputs/design_diagnostics/churn_unwinding_support_audit.md`
- `outputs/design_diagnostics/churn_unwinding_timing_sensitivity.md`
- `outputs/design_diagnostics/churn_unwinding_mechanism_screen.md`

These outputs now exist.

Optional sidecars that were also produced:

- a state-month support table
- exposure-distribution CSVs
- subgroup stability summary tables

The next implementation round should focus on:

- `pre-period falsification`
- `heterogeneity stability`
- refined exposure-timing or exposure-family comparisons

First follow-on batch status:

- [../outputs/design_diagnostics/churn_unwinding_preperiod_falsification.md](../outputs/design_diagnostics/churn_unwinding_preperiod_falsification.md) now exists
- [../outputs/design_diagnostics/churn_unwinding_heterogeneity_stability.md](../outputs/design_diagnostics/churn_unwinding_heterogeneity_stability.md) now exists
- the pre-period falsification result is not obviously fatal
- the first stability screen is more cautionary, because pooled pre-period baseline-risk ordering does not carry cleanly into the unwinding year

## Bottom Line

The project should now stop asking whether the corrected-stack path is real.

It is real enough.

The next question is narrower:

- which unwinding-era exposure family, window, and mechanism are strong enough to justify later `DiD / DML / causal ML` work?

The best first diagnostics posture is:

- use `2022` and `2023` corrected releases as pre-period support
- use the `2024 release` as the unwinding-era outcome + exposure layer
- prioritize `August-November 2023` for transition-based diagnostics
- test `procedural friction` first
- treat `risk prediction`, `DiD / DML heterogeneity`, and `targeting` as downstream branches to be earned, not assumed

Current post-batch reading:

- support is good enough to continue
- timing is not yet clean enough to escalate
- mechanism ordering remains open
- the project should earn its next escalation through stronger falsification, richer subgroup logic, and better timing interpretation
