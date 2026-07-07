# Final Report

## Executive Summary

Go/no-go judgment: **NO-GO for a credible causal paper today.** The 2024 CCBHC
Medicaid Demonstration expansion is a promising policy shock, but public data
available in this build do not yet support a defensible causal estimate of local
capacity effects. The main public facility source, N-SUMHSS, is available for
2021-2024 and suppresses county geography. Several selected states did not begin
verified implementation until 2025, so the only observed post year is at best an
announcement/partial-implementation year.

## Policy Background

CCBHCs are certified clinics intended to provide comprehensive mental-health and
substance-use services, including crisis services, outpatient care, care
coordination, peer/family support, primary-care screening, and services
regardless of ability to pay. The treatment studied here is Medicaid
Demonstration entry and PPS/certification infrastructure, not ordinary CCBHC
expansion grants.

## Data Sources and Coverage

The source inventory is `temp/source_inventory.csv`. The reproducible build
archives official federal policy pages, targeted state evidence, N-SUMHSS
2021-2024 PUFs and codebooks, and Census ACS 2019-2024 county covariates.
TEDS-A, CDC WONDER, AHRF, and HPSA are documented as access records but not used
in the main causal models.

N-SUMHSS contains facility-level service indicators and state, but no county,
FIPS, address, or coordinates. This makes county-year DID infeasible from the
PUF.

## Treatment Construction

The 2024 selected states are Alabama, Illinois, Indiana, Iowa, Kansas, Maine,
New Hampshire, New Mexico, Rhode Island, and Vermont. The 2026 selected states
are Alaska, Colorado, Hawaii, Louisiana, Maryland, Mississippi, Montana, North
Dakota, Washington, and West Virginia. Start dates are coded only when state
evidence was found; otherwise they remain missing rather than imputed.

## Outcomes

Primary state-year outcomes are facility density and counts per 100,000
population for crisis intervention, MOUD, integrated primary care, care
coordination/case management, sliding-fee or low-payment access, and a combined
targeted service index. A state-year-service panel classifies services as
directly targeted, related, or weakly targeted for DDD checks.

## Identification Strategy

The build estimates state-year DID/event-study models with state and year fixed
effects, matched-donor sensitivity, synthetic-control attempts, placebo year and
placebo outcome checks, leave-one-treated-state-out sensitivity, and a DDD
targeted-service design.

## Main Results

For the all-non-original control strategy, the DID estimate for targeted service
density is 0.765 (SE 0.544, p=0.167, N=164).
For crisis-service density it is 0.130 (SE 0.132, p=0.329, N=164).
These numbers are diagnostic only. The post period is a single year and does not
line up cleanly with actual demonstration starts.

The DDD estimate is reported in `result/table_ddd_service_category.csv`. It is
useful as a mechanism check: targeted services should move more than weakly
targeted services if the policy channel is real. It is not enough to rescue the
design.

## Robustness and Falsification

The pipeline attempts planning-grant controls, not-yet-treated controls, nearest
matched donors, propensity overlap diagnostics, placebo treatment year 2023,
placebo outcome using sign-language services, and leave-one-treated-state-out
estimates. These checks are informative for future design selection but cannot
solve the short post-period and unobserved county exposure problems.

## Synthetic-Control Findings

Synthetic controls are attempted for targeted service density using 2021-2023
pre-period outcomes and 2024 gaps. The design is fragile because three pre-years
are too few for strong pre-fit assessment and one post year cannot distinguish
implementation from noise or reporting shifts. Summary results are in
`result/synthetic_control_state_summary.csv`.

## Heterogeneity

The build tests whether early changes differ in high-poverty, low-MOUD, or
low-crisis-capacity states. These are exploratory state-level moderation checks,
not policy targeting rules.

## Limitations

- No 2025 N-SUMHSS PUF is available in this build.
- N-SUMHSS PUF suppresses county geography.
- CCBHC site status, certification dates, and PPS payment dates are not observed
  at the facility level.
- Demonstration selection is endogenous to state readiness.
- TEDS-A and mortality outcomes have no credible post-treatment window for this
  early evaluation.

## Judgment

Preserve the workspace as an audit-ready monitoring package, but do not write the
causal paper yet. The project becomes viable after 2025 and preferably 2026
N-SUMHSS PUFs are available, state start dates are fully verified, and a
historical CCBHC site panel can be built or obtained.

## Next Steps

1. Verify exact state demonstration start/payment dates for all 2024 states.
2. Obtain historical CCBHC site lists with county and certification/payment dates.
3. Add N-SUMHSS 2025 when released.
4. Re-run county and facility designs if geography/status become available.
5. Use TEDS-A and mortality only after a longer post period exists.
