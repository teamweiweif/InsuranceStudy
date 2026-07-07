# Rejected Designs

## County-year DID

Rejected for this build. N-SUMHSS public-use files include state but not county,
FIPS, address, latitude, or longitude. Current CCBHC locator lists are not enough
to reconstruct historical county treatment timing.

## Facility-level CCBHC conversion design

Rejected for this build. N-SUMHSS PUF does not identify CCBHC demonstration status,
CCBHC grantee status, certification date, or payment status.

## TEDS-A admissions as an early post outcome

Rejected for main models. Public files are available through 2023 in this build,
so there is no post-selection admissions outcome.

## Mortality as a main outcome

Rejected. Overdose and suicide mortality are downstream, slow-moving outcomes;
the post period is too short and current public releases do not support a causal
claim for the 2024 CCBHC expansion.

## Causal ML targeting

Rejected. The main identification evidence is not credible enough yet. Policy
learning would optimize noise from one partial post year and unverified county
exposure.
