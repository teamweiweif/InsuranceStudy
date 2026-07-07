# Churn / Unwinding Post-Round-4 Path Decision

Last updated: `2026-04-26`

## Purpose

This memo closes Step 4 from `docs/churn_unwinding_operational_plan_2026-04-11.md`.

It converts the Round-4 diagnostics into one paper-path decision. It does not open new data, new topics, broad literature search, DID, DML, causal forest, event-study, causal targeting, or deployment work.

## Final Verdict

`PATH_A_NARROW_RISK_BURDEN_VULNERABILITY_PAPER_WITH_CAVEATS`

The current SIPP + CMS Medicaid unwinding line should continue as:

- `Path A: paper-first risk / burden / vulnerability line`

but only in a narrowed form.

It should not move to:

- `Path B: continue design strengthening toward quasi-causal escalation`
- `Path C: keep as supporting branch only and do not make it the main paper`

## Decision In Plain Language

The project is still viable as a public-data, data-driven health policy paper about administrative renewal burden, avoidable harmful churn, persistent uninsurance after Medicaid exit, subgroup vulnerability, and bounded risk ranking.

It is not viable right now as a causal effect paper, causal ML paper, DML paper, causal forest paper, welfare targeting paper, or deployable outreach targeting model.

The right path is therefore not to abandon the line and not to escalate it. The right path is to write the paper around the contribution that the evidence can actually support.

## Why The Paper Path Is Still Viable

The paper path remains viable because the project now has a coherent empirical core:

- `SIPP` person-month data can construct coverage-transition outcomes around Medicaid exit.
- The upgraded harmful outcome `persistent_uninsured_h2` focuses the paper on persistent uninsurance rather than any short coverage movement.
- CMS unwinding state-month administrative renewal measures can be linked to SIPP transition outcomes for diagnostic analysis.
- The leading administrative-burden candidate, `backlog_automation_rank_index / same`, survived Round-4 timing stress.
- Several person/household subgroup dimensions show repeatable harmful-risk ordering.
- Simple risk-ranking models outperform a naive state baseline.

This is enough for a paper-first public-data policy contribution if the paper is framed as measurement, diagnostic linkage, vulnerability, and bounded prioritization.

## Why Step 2 Strengthens The Vulnerability Part

Step 2 matters because it moved the subgroup evidence from weak descriptive heterogeneity toward repeatable harmful-risk ordering on the upgraded outcome layer.

The stable harmful-risk subgroup families in the primary window were:

- `foreign_born_group`
- `household_child_group`
- `snap_group`

They were stable on both:

- `persistent_uninsured_h2`
- `broad_exit_persistent_uninsured_h2`

The upgraded `persistent_uninsured_h2` screen improved over the older `medicaid_exit_to_uninsured_next` subgroup screen:

- old stable family count: `2`
- new stable family count: `3`
- old mean Spearman: `-0.0286`
- new mean Spearman: `0.2571`

This does not prove causal heterogeneity. It does support the narrower claim that some vulnerability dimensions are more stable than crude state ordering for harmful churn risk.

## Why Step 3 Is Mixed But Not Fatal

Step 3 is mixed because the new risk-ranking round gives two different messages.

Positive message:

- the new models beat the naive state baseline
- the AUC-leading model on `persistent_uninsured_h2` was `weighted_logistic`
- `weighted_logistic` AUC was `0.5570`
- `weighted_logistic` top-decile capture was `0.1057`
- the top-decile-capture-leading model was `compact_boosting`
- `compact_boosting` captured `0.1966` of weighted `persistent_uninsured_h2` events in the top decile

Cautionary message:

- AUC is modest
- event rates are low
- calibration is weak
- decile ordering is not perfectly monotone
- benchmark AUC was lower than the old risk pilot
- benchmark top-decile capture was only modestly better than the old risk pilot

The result is not fatal because the paper does not need a deployment-grade model. The paper only needs to show that a transparent person/household risk layer adds useful prioritization information beyond naive state baseline. Step 3 supports that narrower statement.

## Why Step 3 Requires Narrowing The Claims

Step 3 prevents the project from using strong model or targeting language.

The correct reading is:

- the risk layer is useful for ranking diagnostics
- the risk layer is not a calibrated probability engine
- the risk layer is not an outreach assignment rule
- the risk layer is not evidence of treatment effects

Therefore the paper can discuss a bounded risk-screening or prioritization prototype, but it must not claim a deployable targeting model.

## Why Causal Escalation Remains Forbidden

Round 4 did not create a quasi-experimental design.

The timing stress tests are encouraging but still diagnostic. The subgroup stability tests show repeatable ordering but not causal heterogeneity. The risk models rank risk better than a naive baseline but do not identify treatment effects.

Therefore the following remain forbidden:

- DID
- DML
- event-study
- causal forest
- causal ML
- causal targeting
- welfare-based targeting
- deployment-ready outreach assignment

Using any of those labels would make the result sound stronger than the evidence.

## Allowed Paper Positioning

The allowed paper positioning is:

`A public-data, data-driven health policy paper on administrative renewal burden, avoidable harmful churn, persistent uninsurance after Medicaid exit, subgroup vulnerability, and bounded risk-ranking during Medicaid unwinding.`

Shorter possible positioning:

`Administrative renewal burden and persistent uninsurance risk during Medicaid unwinding: a public-data risk and vulnerability study.`

The paper should be written as a constrained empirical contribution, not as a causal ML contribution.

## Allowed Claims

The paper may claim:

- SIPP person-month data can construct useful Medicaid exit and persistent-uninsurance outcomes.
- `persistent_uninsured_h2` is a more policy-relevant harmful-churn outcome than a one-month exit screen alone.
- CMS state-month renewal-burden measures can be linked to SIPP transition outcomes for diagnostic analysis.
- `backlog_automation_rank_index / same` remains the leading administrative-burden candidate after Round-4 timing stress.
- Future-month `lead1` placebo timing did not dominate the best non-lead alignment in the primary timing windows.
- Some subgroup dimensions show more stable harmful-risk ordering, especially `foreign_born_group`, `household_child_group`, and `snap_group`.
- The upgraded outcome layer improves subgroup stability relative to the older one-month exit-to-uninsured screen.
- Simple risk-ranking models outperform a naive state baseline.
- The current line supports a bounded risk-screening / prioritization prototype with caveats.
- The paper contributes a replicable public-data framework for studying unwinding-era harmful churn risk.

## Forbidden Claims

The paper must not claim:

- administrative burden caused persistent uninsurance
- state-month burden measures identify causal treatment effects
- subgroup differences are causal heterogeneity
- the model can assign outreach treatment
- the model is deployment-ready
- predicted probabilities are well calibrated
- this is causal ML evidence
- this is DML evidence
- this is causal forest evidence
- this is DID evidence
- this is event-study evidence
- this is welfare-based targeting
- the model has solved policy targeting
- `procedural friction` has been proven as the main mechanism

## Chosen Path Versus Alternatives

### Path A

`Path A: paper-first risk / burden / vulnerability line`

Decision: choose this path, narrowed.

Reason: the evidence supports a coherent data-driven policy paper if the claims are limited to diagnostic linkage, persistent-uninsurance measurement, subgroup vulnerability, and bounded risk ranking.

### Path B

`Path B: continue design strengthening toward quasi-causal escalation`

Decision: do not choose this path now.

Reason: Round 4 did not produce identification evidence strong enough to justify quasi-causal escalation. Moving there now would weaken the project by overclaiming.

### Path C

`Path C: keep as supporting branch only and do not make it the main paper`

Decision: do not choose this path.

Reason: Step 1, Step 2, and Step 3 together are strong enough for a narrowed main-paper candidate. The branch is no longer only background support.

## Next Practical Step

The next step should be:

`Create a constrained paper outline and results-to-table map for Path A.`

That next artifact should include:

- one-paragraph paper question
- final allowed contribution list
- table and figure inventory from existing diagnostics
- main outcome definitions
- main exposure definitions
- subgroup vulnerability section plan
- bounded risk-ranking section plan
- limitations section with the forbidden causal and targeting claims stated explicitly

Do not start new causal estimation. Do not start a new dataset search. Do not write final paper prose before the outline and results-to-table map are locked.

## Closure

Step 4 is complete.

Final Step 4 verdict:

`PATH_A_NARROW_RISK_BURDEN_VULNERABILITY_PAPER_WITH_CAVEATS`

The current SIPP + CMS Medicaid unwinding line should now move into a narrowed paper-outline phase, not causal escalation and not topic switching.
