# Churn / Unwinding Outcome Reassessment Memo

Last updated: `2026-04-11`

## Purpose

This memo answers four questions that became critical after the first `avoidable churn` upgrade:

1. Does the new outcome setup have real theoretical, official, or literature support?
2. What do the new outcomes actually represent in plain language?
3. Does switching to these outcomes change the research question?
4. How should future agents describe results so the empirical logic stays clear?

This memo is a reassessment note, not a final identification memo.

## Short Answer

- Yes, the new setup has real support, but not in the sense that `persistent_uninsured_h2` is a standard CMS published metric.
- The support is indirect but meaningful:
  - official unwinding documents make clear that `procedural terminations`, `pending renewals`, and `ex parte renewals` are central operational concepts
  - official and peer-reviewed sources treat `coverage gaps`, `churn`, and `continuity of coverage` as substantively important outcomes
  - official unwinding reporting is itself cohort-based and can include outcomes completed up to several months after the original due month, which makes a slightly more persistent short-horizon outcome more defensible than a pure one-step signal
- So the new outcome does **not** fully change the project into a different paper.
- But it **does** narrow and sharpen the question:
  - away from `immediate next-month loss only`
  - toward `short-run persistent harmful loss and avoidable instability`

## Structured Reassessment

### 1. Outcome

Current key outcomes now mean:

- `medicaid_exit_to_uninsured_next`
  - At month `t`, the person is in pure Medicaid.
  - At month `t+1`, the person is uninsured.
  - This is the original narrow one-step harmful transition outcome.

- `persistent_uninsured_h2`
  - At month `t`, the person is in pure Medicaid.
  - At month `t+1`, the person is uninsured.
  - At month `t+2`, the person is still uninsured.
  - This is the new stricter harmful short-horizon outcome.

- `broad_exit_resolved_insured_h2`
  - At month `t`, the person is in pure Medicaid.
  - At month `t+1`, the person is no longer in pure Medicaid.
  - By month `t+2`, the person is insured again.
  - This is a contrast outcome: instability happened, but it did not persist into short-run uninsurance.

### 2. Exposure

The current leading exposure candidate is:

- `backlog_automation_index / same`

In plain language, this is a state-month burden index that is higher when:

- `pending renewals` are high
- `ex parte / automatic renewals` are weak

So higher exposure means:

- the renewal system is more backlogged
- fewer renewals are being resolved automatically
- more beneficiaries are exposed to a heavier administrative renewal environment

### 3. Purpose

The purpose of the new outcome design is **not** to make the result look prettier.

It is to fix a real mismatch in the earlier screen:

- the old outcome was too narrow and noisy
- literal `exit -> return to Medicaid` was too sparse to support a serious branch
- the CMS unwinding reporting system is cohort-based and operational, not a clean person-level disenrollment clock

So the new outcome layer tries to better capture:

- harmful short-run loss that persists beyond a one-month blip
- versus instability that resolves back into insured status shortly after the exit

### 4. Numerical Result

In the current `core Aug-Oct 2023` corrected stack:

- `persistent_uninsured_h2`
  - `64` event rows in `2023`
  - weighted event rate `0.002933`

- `broad_exit_resolved_insured_h2`
  - `75` event rows in `2023`
  - weighted event rate `0.005024`

- literal `broad_exit_back_to_medicaid_h2`
  - only `1` event row in `2023`
  - weighted event rate `0.00007`
  - too sparse for mainline use

For the burden round, the strongest current candidate became:

- `Exposure`: `backlog_automation_index / same`
- `Outcome family`: one-step uninsured exit + persistent uninsured h2 + resolved insured h2
- `Core score`: `0.1242`
- `Mature score`: `0.1105`
- `Falsification`: passed for all three tracked outcomes in the implemented rule

### 5. Interpretation

The new outcome setup means:

- the project is now less focused on `any immediate drop`
- and more focused on `administratively burdened environments that are associated with short-run persistent uninsured loss`

That is a more defensible harmful outcome if the real concern is:

- avoidable loss of coverage
- not every transition away from Medicaid
- not every temporary administrative data mismatch

### 6. Evaluation

This change is encouraging, but only under a disciplined interpretation.

What it supports:

- a more coherent empirical core than the old `renewal_form_rate / lag1` branch
- a better alignment between theory, measurement, and external HPS direction checks
- a clearer distinction between:
  - harmful unresolved loss
  - instability that resolves back to insured status

What it does **not** support:

- that `persistent_uninsured_h2` is a standard official CMS endpoint
- that we have already identified a clean causal treatment effect
- that the project is ready to jump to `DML / causal ML`

## Why The New Outcome Has Real Support

### A. Official support for the mechanism side

Official unwinding materials make clear that the administrative side of renewals matters.

CMS defines:

- `ex parte renewal`
  - renewal based on information already available to the agency, without asking the beneficiary for more information
- `procedural termination`
  - termination when the beneficiary does not provide needed renewal information
- `pending renewals`
  - renewals not yet fully resolved by the end of the reporting period

This matters because the current exposure candidate is built exactly around those operational concepts, not an invented theory object.

### B. Official support for timing not being purely one-month

Both CMS and GAO make clear that unwinding renewal outcomes are tracked by monthly cohorts whose final outcome can extend beyond the due month.

That matters for outcome choice.

If the state-month operational burden is reported around a renewal-due month, a one-month person-level uninsured transition may be too narrow or too mechanically misaligned.

A stricter short-horizon persistent loss measure is therefore more defensible than treating `t+1 uninsured` as the only meaningful endpoint.

### C. Literature and policy support for continuity / gaps as the real substantive object

Peer-reviewed and policy sources consistently say:

- Medicaid `churn` and `gaps in coverage` matter
- continuity of coverage affects care access and health system use
- ex parte reviews and lower paperwork burden are policy levers intended to reduce churn

So the substantive object here is not just “did someone flip status next month?”

It is:

- whether the renewal environment contributes to harmful coverage instability
- and whether that instability persists enough to look like a real coverage gap

### D. Policy support for distinguishing persistent loss from quickly resolved loss

KFF documents that states must offer a `90-day reconsideration` period after procedural disenrollment.

That means the unwinding system itself already distinguishes between:

- someone procedurally terminated who may regain coverage quickly
- someone whose loss remains unresolved

That is exactly why `persistent_uninsured_h2` and `broad_exit_resolved_insured_h2` are useful as a pair.

They separate:

- unresolved short-run harm
- from short-run instability that is later corrected

## Does This Change The Research Question?

### Short answer

- `Yes, but only in a narrowing sense.`

### What did not change

The project is still about:

- Medicaid unwinding
- administrative renewal burden
- coverage instability
- who is more vulnerable

So the core policy domain is unchanged.

### What did change

The question is no longer best written as:

- `Does administrative friction increase immediate next-month uninsured exit?`

It is now better written as:

- `Does administrative renewal burden increase short-run persistent uninsured loss and avoidable Medicaid instability during unwinding?`

That is a real refinement.

It shifts the empirical target from:

- any immediate harmful transition

to:

- the more policy-relevant subset of transitions that remain unresolved over a short horizon

### Bottom-line judgment

This is **not** a full pivot to a different paper.

It is a `measurement upgrade` and a `question sharpening`.

But to stay honest, the paper framing should acknowledge that the project is now closer to:

- `avoidable harmful churn`

than to:

- `all churn`

## Recommended Framing Going Forward

### Preferred primary outcome

- `persistent_uninsured_h2`

Why:

- more harmful than a one-month blip
- less sparse than literal return-to-Medicaid
- better aligned with operational renewal timing uncertainty

### Recommended supporting outcomes

- `medicaid_exit_to_uninsured_next`
  - keep as the narrow one-step benchmark

- `broad_exit_resolved_insured_h2`
  - keep as a contrast outcome

This prevents the project from overcommitting to a single handcrafted endpoint.

### Preferred mechanism wording

Do **not** oversell narrow `procedural friction` alone.

Prefer:

- `administrative renewal burden`

with current leading empirical subchannel:

- `backlog + weak automatic renewal`

## Reporting Rule For Future Updates

From this point forward, future empirical updates should always report:

1. `Question`
2. `Sample / Unit`
3. `Outcome`
4. `Treatment / Exposure`
5. `Purpose`
6. `Numerical Result`
7. `Interpretation`
8. `Evaluation`
9. `Caveat`

This requirement is now formally recorded in:

- [empirical_result_reporting_convention.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/empirical_result_reporting_convention.md)

## Bottom Line

The new outcome setup is not arbitrary.

It is supported by:

- official unwinding concepts
- official evidence that timing and resolution can extend beyond a single month
- literature that treats continuity and coverage gaps as meaningful outcomes
- policy logic distinguishing unresolved loss from quickly corrected loss

But the support is still `conceptually defensible`, not `officially standardized`.

So the correct interpretation is:

- this is a better research design choice
- not a claim that CMS itself uses `persistent_uninsured_h2`

## Sources

- CMS, `Medicaid and CHIP Unwinding: Data Sources and Metrics Definitions Overview`:
  - https://www.medicaid.gov/resources-for-states/downloads/data-sources-and-definitions.pdf
- CMS, `Ex Parte Renewal Strategies`:
  - https://www.medicaid.gov/resources-for-states/downloads/ex-parte-renewal-102022.pdf
- CMS, `Available State Strategies to Minimize Terminations for Procedural Reasons During the COVID-19 Unwinding Period`:
  - https://www.medicaid.gov/resources-for-states/downloads/considerations-for-procedural-termination-strategies.pdf
- GAO, `Disenrollments After COVID-19 Varied Across States and Populations`:
  - https://www.gao.gov/assets/gao-25-107413.pdf
- MACPAC, `State Reported Medicaid Unwinding Data Brief`:
  - https://www.macpac.gov/wp-content/uploads/2024/11/State-Reported-Medicaid-Unwinding-Data-Brief.pdf
- MACPAC, `Updated Analyses of Churn and Coverage Transitions`:
  - https://www.macpac.gov/publication/updated-analyses-of-churn-and-coverage-transitions/
- KFF, `Medicaid and CHIP Eligibility, Enrollment, and Renewal Policies`:
  - https://www.kff.org/medicaid/medicaid-and-chip-eligibility-enrollment-and-renewal-policies-as-states-resume-routine-operations-following-the-unwinding-of-the-pandemic-era-continuous-enrollment-provision/
- KFF, `An Examination of Medicaid Renewal Outcomes and Enrollment Changes at the End of the Unwinding`:
  - https://www.kff.org/medicaid/an-examination-of-medicaid-renewal-outcomes-and-enrollment-changes-at-the-end-of-the-unwinding/
- JAMA Health Forum, `Duration and Continuity of Medicaid Enrollment Before the COVID-19 Pandemic`:
  - https://jamanetwork.com/journals/jama-health-forum/fullarticle/2799532
- Herd and Moynihan, `Administrative Burdens in Health Policy`:
  - https://journals.sagepub.com/doi/10.37808/jhhsa.43.1.2
- NBER, `Reducing Administrative Barriers Increases Take-up of Subsidized Health Insurance Coverage`:
  - https://www.nber.org/papers/w30885
