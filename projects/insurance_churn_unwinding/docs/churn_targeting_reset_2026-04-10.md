# Churn Targeting Reset

Last updated: `2026-04-10`

## Purpose

This note compresses the current project direction after:

- the internal workspace exploration notes
- the first public-data acquisition pass
- the shared external reasoning thread: <https://chatgpt.com/share/69d880cb-4ef8-8333-94ec-faaab0c80f75>

This is a planning memo only.

- It does **not** run a data audit.
- It does **not** start modeling.
- It does **not** replace the older Medicare@65 pipeline files.

Execution sequencing has now moved to:

- [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)

This file remains a strategic framing note, not the execution-control document.

## Current Decision

The project is now centered on:

- `coverage churn / Medicaid unwinding / continuity of care`

The old `MEPS Medicare@65` line should now be treated as:

- a real analytical asset
- a backup / companion line
- not the preferred core paper

## The Most Important Compressed Take

The key shift is not just topic selection.

The key shift is the **research claim**:

- weak claim: "I study Medicaid unwinding"
- still weak: "I study subgroup heterogeneity in Medicaid unwinding"
- stronger claim: "I use public data to turn unwinding into a precision targeting / decision problem"

In other words, the moat should come from:

- identifying who is at highest risk of administratively driven coverage loss
- identifying who is most harmed by that loss
- asking who should be prioritized for outreach or retention support under limited policy resources

That is the most important point absorbed from the shared link.

## What The Shared Link Adds Beyond The Current Docs

The local docs had already moved the project toward `priority1_churn_unwinding`.

The shared link sharpens four things:

1. The contribution should not be sold as "nobody has studied unwinding."
2. The first wave of papers already exists, including:
   - descriptive coverage-loss papers
   - subgroup heterogeneity papers
   - quasi-experimental state-month papers
   - downstream outcome papers
   - outreach / renewal experiment papers
3. The plausible open space is narrower:
   - `causal ML + policy targeting + public data + person-level dynamics`
4. The right immediate move is not broad brainstorming.
   - It is a conservative data audit followed by an exact design memo.

## Guardrails For Innovation Claims

Do **not** frame the project as:

- "the first unwinding paper"
- "the first paper on heterogeneity in unwinding"

Safer framing:

- one of the first public-data studies to treat unwinding as a targeting problem
- a paper that links churn risk, downstream harm, and prioritization logic
- a paper that moves beyond average or descriptive effects toward policy allocation

The innovation should come from the combined structure:

- person-level insurance dynamics
- state-month unwinding environment
- heterogeneity estimation
- policy-targeting logic

## Current Data Position In This Workspace

The current local staging already supports a serious **audit** of the churn direction.

Priority-1 relevant data already staged:

- `SIPP 2018-2024` under [../data/raw/feasibility_audit/sipp](../data/raw/feasibility_audit/sipp)
- `HPS 2023-2025` under [../data/raw/feasibility_audit/hps](../data/raw/feasibility_audit/hps)
- `NHIS 2019-2024` under [../data/raw/feasibility_audit/nhis](../data/raw/feasibility_audit/nhis)
- `MEPS` feasibility files under [../data/raw/feasibility_audit/meps](../data/raw/feasibility_audit/meps)
- Medicaid unwinding pages, snapshots, and reports under [../reference/external/feasibility_audit/medicaid_unwinding](../reference/external/feasibility_audit/medicaid_unwinding)

Useful supporting notes:

- [current_exploration_handoff.md](current_exploration_handoff.md)
- [public_data_feasibility_audit.md](public_data_feasibility_audit.md)
- [public_batch_acquisition_run_2026-04-10.md](public_batch_acquisition_run_2026-04-10.md)

## Working Data Architecture

The current best working structure is:

- **Primary engine**: `SIPP + CMS / Medicaid state-month unwinding layer`
- **Validation layer**:
  - `NHIS` for access / unmet need validation
  - `MEPS` for spending / financial-protection follow-up
  - `HPS / HTOPS` for fast descriptive or timing cross-checks
- **Secondary / non-primary sources**:
  - `CFPB` for distress side evidence
  - `MCBS` only if the project later pivots back toward Medicare / duals

Current judgment:

- `SIPP` is the most likely public-use main engine
- `NHIS` and `MEPS` are more valuable as validators than as the main unwinding identifier
- `HPS` is useful but should not be the flagship estimating engine

## Why SIPP Is The Leading Audit Target

At the planning level, `SIPP` is the strongest current candidate because it is the dataset most likely to support all of the following at once:

- longitudinal structure
- person-level coverage dynamics
- churn / spell construction
- richer covariates for risk stratification
- potential linkage to state-month unwinding context

This does **not** mean SIPP is automatically sufficient.

It means:

- `SIPP` should be audited first
- the exact public-use geography, weights, insurance fields, and time structure should be verified before any modeling claim is made

## Immediate Plan Before Any Modeling

### Phase 1: Conservative Data Audit

Start with `SIPP`, then compare it against `NHIS`, `MEPS`, and `HPS`.

The audit should answer:

- what files are actually present locally
- what the unit of observation is
- whether the data are cross-sectional, repeated cross-sectional, or longitudinal
- what geography is available in public files
- whether person-month coverage and churn measures are constructible
- which outcome families are actually present
- whether a credible state-policy linkage is possible

Two special audit modules matter most:

- **policy-linkability audit**
  - can the public dataset be credibly linked to state-by-month unwinding timing or renewal environment?
- **targeting-feasibility audit**
  - can the data support:
    - risk prediction
    - heterogeneous harm
    - prioritization logic

### Phase 2: Exact Design Memo

Only after the audit, write a one-page exact design memo that fixes:

- treatment definition
- timing variation
- core estimand
- primary outcome family
- validation outcome family
- heterogeneity dimensions
- policy-targeting interpretation
- identification risks

### Phase 3: Minimal Implementation

Only after Phase 1 and Phase 2:

- define ingestion scope
- define derived variables
- define analysis-ready panels
- begin actual empirical work

## Condensed Codex Audit Brief

If Codex is asked to proceed later, the request should be close to this:

```text
Audit the local public-use datasets for a churn / Medicaid unwinding project.

Do not model yet.
Do not assume variables exist until verified locally.
Start with SIPP as the leading candidate main engine.

Your task:
1. Build a manifest of all local files for SIPP, HPS/HTOPS, NHIS, MEPS, MCBS, CFPB, and Medicaid unwinding materials.
2. Verify, from local documentation and file headers, the unit of observation, time structure, public geography, weights, insurance variables, churn feasibility, and downstream outcomes.
3. Score each dataset for:
   - primary unwinding engine
   - access validator
   - spending validator
   - targeting / causal-ML suitability
4. Write a decision memo answering:
   - Is SIPP really the best public-use main engine?
   - What is the best 2- or 3-dataset stack?
   - Does causal ML add real value here, or would it be decorative?

Deliver audit artifacts only. No final modeling.
```

## References

Shared reasoning thread:

- <https://chatgpt.com/share/69d880cb-4ef8-8333-94ec-faaab0c80f75>

Relevant local planning notes:

- [research_directions_analysis.md](research_directions_analysis.md)
- [current_exploration_handoff.md](current_exploration_handoff.md)
- [public_data_feasibility_audit.md](public_data_feasibility_audit.md)
- [public_batch_acquisition_run_2026-04-10.md](public_batch_acquisition_run_2026-04-10.md)

Useful external policy context:

- Medicaid returning-to-regular-operations page: <https://www.medicaid.gov/resources-for-states/coronavirus-disease-2019-covid-19>
- KFF end-of-unwinding renewal analysis: <https://www.kff.org/medicaid/issue-brief/an-examination-of-medicaid-renewal-outcomes-and-enrollment-changes-at-the-end-of-the-unwinding/>

## Status

This memo records the current direction and the next planning move.

It does **not** claim that the exact unwinding design is already locked.
It does **not** claim that SIPP has already passed a full audit.
It does claim that `SIPP-led audit first` is now the most defensible next step.
