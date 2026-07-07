# Iteration Notes

## Phase 0: Skill discovery (2026-07-07)
- The registry scan found installed AERS, causal inference, DID, synthetic control, panel, reproducibility, data-audit, and econ-write skills.
- Adopted a Python-only, script-first workflow with raw downloads in temp and clean analysis-ready data in data.
- County CCBHC exposure will not be imputed; if public files lack county geography, the county design will be explicitly rejected.

## Phase 1: Policy/source audit (2026-07-07)
- Archived official federal policy pages, N-SUMHSS PUFs/codebooks for 2021-2024, and ACS county covariates.
- Recorded TEDS-A, CDC WONDER, AHRF, and HPSA as access records rather than forcing non-post or non-historical sources into the main design.
- N-SUMHSS PUF has no county geography; county-level capacity outcomes require a different source or restricted data.

## Phase 3: Treatment construction (2026-07-07)
- Constructed state-year treatment panel with 2024 and 2026 cohorts, planning grants, original demonstration exclusions, and verified/missing start-date flags.
- Did not collapse selection, certification, operation, and PPS payment dates.
- Rejected county CCBHC exposure for now because county/site timing is not available in N-SUMHSS PUF and current locators are not historical.

## Phase 2: Data audit (2026-07-07)
- Read N-SUMHSS 2021-2024 PUFs into a facility-year panel using state-level geography only.
- Created state-level capacity outcomes and ACS county/state covariates.
- Created county capacity files with explicit missing-outcome flags; no county behavioral-health outcomes are fabricated.

## Phase 4: Outcome construction (2026-07-07)
- Built state-year and state-year-service outcomes from observed N-SUMHSS services.
- Classified directly targeted, related, and weakly targeted service lines for DDD.
- Kept downstream TEDS-A and mortality out of the main outcome stack because no credible post-treatment window is public yet.

## Phase 5: Control construction/descriptives (2026-07-07)
- Produced raw trends, balance diagnostics, missingness, data coverage, service distributions, and cohort tile map.
- Planning-grant and not-yet-treated controls are available at the state level; county matched controls are not estimable without county outcomes.
- Baseline balance is diagnostic only because selection into demonstration is non-random and pre-period is short.

## Phase 6: Main models (2026-07-07)
- Estimated state-year DID/event-study models for multiple N-SUMHSS capacity outcomes.
- Estimated DDD service-category model comparing directly targeted services to related/weakly targeted services.
- Ran placebo year, placebo outcome, leave-one-treated-state-out, and low-baseline-capacity heterogeneity diagnostics.
- All causal estimates are early and fragile because the observed post period is only 2024 and many demonstrations start in 2025.

## Phase 7: Synthetic and selection checks (2026-07-07)
- Built nearest-neighbor matched donor states from 2021-2023 baseline outcomes and ACS covariates.
- Attempted state-level synthetic controls for targeted service density with 2021-2023 pre-fit and 2024 gaps.
- Logged propensity overlap scores as a selection-bias diagnostic.
- Synthetic-control evidence is weak by design because there are only three pre-years and one partial post-year.

## Phase 8: Mechanism and heterogeneity (2026-07-07)
- Tested state-level heterogeneity for high poverty, low baseline MOUD, and low baseline crisis capacity.
- Framed DDD and heterogeneity as mechanism consistency checks, not causal mediation.
- Rejected county DID, facility conversion, TEDS-A early post, mortality main outcome, and causal ML for documented data/design reasons.

## Phase 9: Final judgment (2026-07-07)
- Applied econ-writing guidance after empirical outputs existed: result first, concrete limitations, no overclaiming.
- Final judgment is no-go for a causal paper today, preserve workspace for future post-period updates.
