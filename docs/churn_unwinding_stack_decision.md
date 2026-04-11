# Churn / Unwinding Stack Decision

Last updated: `2026-04-10`

## Purpose

This note is the formal `Step 4` decision memo for the churn / unwinding line.

Its job is to decide whether the project should proceed with a corrected multi-year `SIPP` stack after:

- the `2024` template-year freeze
- the first audited CMS `state x month` merge
- the `2018-2023` correction specification
- the first bounded `2023` correction pilot

This is a path decision.

It is **not**:

- a final estimating memo
- a final identification memo
- a final `causal ML` memo

## Governing Evidence

This decision is based on:

- [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)
- [../outputs/data_audit/sipp_preflight_2026-04-10.md](../outputs/data_audit/sipp_preflight_2026-04-10.md)
- [../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md](../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md)
- [../outputs/prototype/sipp_2024_coverage_layer_spec.md](../outputs/prototype/sipp_2024_coverage_layer_spec.md)
- [../outputs/prototype/sipp_2024_state_month_merge_audit.md](../outputs/prototype/sipp_2024_state_month_merge_audit.md)
- [../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md](../outputs/data_audit/sipp_2018_2023_hi_correction_spec.md)
- [../outputs/prototype/sipp_2023_correction_pilot_audit.md](../outputs/prototype/sipp_2023_correction_pilot_audit.md)
- [churn_targeting_reset_2026-04-10.md](churn_targeting_reset_2026-04-10.md)

## Decision

Formal decision:

- `GO` for a **narrow, phased corrected-stack implementation path**
- `NO-GO` for immediate full corrected-stack estimation
- `NO-GO` for immediate `causal ML / targeting` execution

Practical reading:

- the project should continue building the corrected multi-year monthly insurance / churn layer
- the next implementation extension should be `2022`
- the project should not yet backfill all the way through `2018-2020`
- the project should not yet behave as if the corrected stack has already validated identification

Status update after this decision:

- the first recommended backward extension to `2022` has now been completed in [../outputs/prototype/sipp_2022_correction_pilot_audit.md](../outputs/prototype/sipp_2022_correction_pilot_audit.md)
- this strengthens the phased `GO`
- the constrained design-diagnostics memo now exists in [churn_unwinding_design_diagnostics_memo.md](churn_unwinding_design_diagnostics_memo.md)
- the first diagnostics outputs under `outputs/design_diagnostics/` now exist
- the next active work should now be falsification, subgroup-stability, and refined timing diagnostics rather than another automatic backfill step

## What This Decision Means

The project now has enough evidence to stop asking:

- "Should we abandon the corrected-stack path?"

The answer to that is now:

- `No`

But the project should still keep asking:

- "How far should the corrected stack be extended before estimation begins?"
- "Is the unwinding-era exposure interpretation strong enough for more than descriptive or predictive work?"
- "Is the eventual contribution closer to robust `risk prediction`, to `DiD / DML heterogeneity`, or to true targeting?"

## Why The Decision Is `GO`

### 1. The outcome layer is no longer hypothetical

`Step 1` froze a valid person-month churn object in the `2024` template release.

That matters because later stack work no longer has to invent the target layer from scratch.

The core monthly objects are already defined:

- `pure_medicaid_t`
- `uninsured_t`
- `medicaid_exit_next`
- `medicaid_exit_to_uninsured_next`

### 2. The external unwinding layer is real enough to justify continuation

`Step 2` showed that `TEHC_ST x MONTHCODE` can be merged to a real CMS unwinding metric family.

That merge is only `usable with caveats`, but it is good enough to justify keeping the unwinding-focused design alive.

This is important because a corrected stack only has strategic value if it can eventually serve an unwinding-linked design rather than general churn description alone.

### 3. The correction path is real, not just planned

`Step 3` plus the `2023` pilot showed that the correction logic changes the churn layer in meaningful ways and does not break the person-month structure.

That means the project is no longer relying on a speculative claim that early years can probably be repaired.

The repair path exists in practice.

### 4. A phased stack adds real value even for an unwinding-focused paper

Earlier corrected years are still useful as:

- pre-period support
- baseline churn-risk support
- baseline heterogeneity support
- validation support for the corrected churn layer

That is enough to justify continuation even though unwinding itself is concentrated in recent years.

## Why The Decision Is Not A Broader `GO`

### 1. The CMS exposure layer is still conceptually imperfect

The selected CMS month is a `renewal due / updated disposition` month.

It is not a clean person-level disenrollment month.

So the project is not yet entitled to treat the merged stack as a fully validated treatment-timing design.

### 2. The corrected stack is not yet broad enough for final estimation

Only one bounded pilot year has been corrected so far.

That is enough to justify the path.

It is not enough to authorize:

- full-stack estimation
- publication-ready identification claims
- final `causal ML / targeting` claims

### 3. Private coverage handling remains conservative

The `2023` pilot surfaced a real implementation caution:

- direct rebuilding of `RPRIMTH` from the currently used local fields diverged materially from the raw recode

So the public / Medicaid side looks workable, but the private side should remain conservative until separately resolved.

### 4. The project still needs design diagnostics, not just more rows

A longer corrected stack would help later `DiD / event-study / DML / causal ML` work.

But it would not finish identification by itself.

The project still needs later testing of:

- alternative exposure timing
- early-month source coverage weakness
- mechanism plausibility
- heterogeneity stability

## Go / No-Go Matrix

| Path decision | Verdict | Reason |
| --- | --- | --- |
| Continue the corrected-stack path at all | `GO` | The correction logic is now operationally credible and strategically useful. |
| Immediately build a full corrected `2018-2023` or `2018-2024` stack | `NO-GO` | Too much untested implementation remains. The project should phase backward instead. |
| Immediately start estimation on the corrected stack | `NO-GO` | The stack is not yet validated enough for serious estimation. |
| Immediately launch `causal ML / targeting` on the current stack | `NO-GO` | Outcome correction, treatment timing, and targeting interpretation are not mature enough yet. |
| Extend correction work one step backward to `2022` | `GO` | This is the highest-value next implementation extension after the `2023` pilot. |
| Keep the research question anchored on unwinding while using earlier years as support | `GO` | This preserves the intended estimand while using earlier years for pre-period and heterogeneity support. |
| Reframe the project now as general multi-year churn only | `NO-GO` | That would dilute the current contribution logic too early. |

## Recommended Next Active Path

The next active path should have two linked components.

### Path A: extend the corrected stack one year backward

This path is now completed once.

Completed implementation target:

- `2022`

Why `2022` next:

- it is adjacent to the successful `2023` pilot
- annual recodes are still available for bounded checks
- it increases pre-unwinding support without immediately taking on the more complicated earlier groups

Produced outputs:

- `outputs/prototype/sipp_2022_corrected_person_month_flags.parquet`
- `outputs/prototype/sipp_2022_correction_pilot_audit.md`
- `outputs/prototype/sipp_2022_correction_pilot_summary.json`

### Path B: start a constrained design-diagnostics memo after `2022`

Once `2022` is corrected, the next design memo should not be a final paper outline yet.

That memo now exists and answers:

- what the cleanest unwinding-era exposure definition is
- which months are safe enough for the first serious design window
- whether the project should start from `risk prediction`, `DiD / DML heterogeneity`, or a narrower mechanism test
- which mechanism families deserve first-pass testing

This keeps the project from single-betting too early on one story.

The first diagnostics artifacts under `outputs/design_diagnostics/` now exist.

The next active outputs should be the next constrained diagnostics layer:

- falsification-style checks
- subgroup-stability checks
- refined timing / exposure interpretation outputs

Status update after those follow-on diagnostics:

- the first pre-period falsification screen is not obviously fatal
- the first state-level subgroup-stability screen is more cautionary and does not yet support a stable targeting interpretation
- this keeps the project on a `GO` path for diagnostics, but not yet on a `GO` path for strong identification or `causal ML`

## What Should Still Wait

The following should remain blocked for now:

- full backfill through `2018-2020`
- final downstream-harm outcome construction
- broad covariate harmonization
- final identification claims
- final `causal ML / targeting` execution
- article framing based on preferred results

Those depend on a stronger corrected stack and cleaner design diagnostics.

## Bottom Line

The corrected-stack path is now worth continuing.

But the correct continuation is:

- narrow
- phased
- unwinding-anchored
- diagnostic-heavy

The next move is not "estimate everything."

It is:

- extend the correction implementation to `2022`
- then write the first constrained design-diagnostics memo before broader estimation
