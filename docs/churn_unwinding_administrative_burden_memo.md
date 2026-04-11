# Medicaid Unwinding Administrative Burden Memo

Last updated: `2026-04-10`

## Purpose

This memo resets the mechanism language for the `SIPP + CMS unwinding` line.

The key change is:

- do **not** anchor the paper too narrowly on `procedural friction`
- use `administrative renewal burden` as the umbrella mechanism
- treat current CMS exposure families as competing or complementary sub-mechanisms inside that umbrella

This is a better fit for both:

- the public-policy literature
- the current first- and second-round diagnostics

## Why The Framing Had To Change

The original instinct was:

- `procedural friction` is the main mechanism
- administrative paperwork and renewal failure should show up most clearly as `Medicaid exit -> uninsured`

That story is still plausible, but the current data do **not** naturally force that conclusion.

What the current diagnostics show instead:

- `procedural termination burden` is not the clean leading signal
- `pending/backlog burden` can look strong, but mostly through `lead1`, which is not safe enough for escalation
- `manual renewal burden` is the only gate-eligible family that currently keeps the same preferred non-lead alignment across both windows
- `ex parte renewal relief` looks substantively plausible and directionally coherent, but it does not satisfy the current timing-gate rule because its preferred alignment changes across windows

So the right theory language is:

- the Medicaid unwinding process creates **administrative renewal burden**
- that burden can arise through paperwork, renewal workload, system backlog, and low automation
- the empirical task is to identify which observable burden proxy best tracks avoidable coverage loss

## Mechanism Map

| mechanism family | plain-language meaning | current CMS field | expected sign on `medicaid_exit_next` | expected sign on `medicaid_exit_to_uninsured_next` | interpretation |
| --- | --- | --- | --- | --- | --- |
| `procedural_termination_burden` count | more people are being terminated for procedural reasons | `cms_updated_procedural_termination_n` | positive | positive | suggests more exits associated with administrative failure rather than smooth renewal |
| `procedural_termination_burden` share | a larger share of all terminations are procedural | `cms_updated_procedural_share_of_terminated` | positive | positive | cleaner procedural signal than raw count, but depends on the termination mix |
| `renewal_workload_burden` count | more cases come due for renewal in the month | `cms_updated_renewal_due_n` | positive | positive | workload can raise churn if staffing and systems cannot absorb the volume |
| `pending_backlog_burden` count | more renewals remain unresolved | `cms_updated_pending_n` | positive | positive | captures backlog and processing strain |
| `pending_backlog_burden` rate | a larger pending share of the renewal workload | `cms_updated_pending_rate` | positive | positive | more comparable than raw count across states |
| `ex_parte_renewal_relief` | more renewals are completed automatically without beneficiary action | `cms_updated_renewed_ex_parte_rate` | negative | negative | protective mechanism that should reduce avoidable exits |
| `manual_renewal_burden` | more renewals require forms or active beneficiary response | `cms_updated_renewed_form_rate` | positive | positive | direct proxy for renewal burden faced by households |
| `formal_ineligibility_channel` | more cases end because the state classifies them as ineligible | `cms_updated_ineligible_rate` | positive | ambiguous | more compatible with true eligibility loss than with pure paperwork failure |

Current omitted variant:

- `renewal_due_rate` was **not** added because the staged CMS files in this workspace do not expose a clean shared denominator that would make that rate stable enough across the stack.

## How To Read The Outcomes

The two current outcomes are narrow transition outcomes from the SIPP corrected stack:

- `medicaid_exit_next`
  - this month the person is on pure Medicaid
  - next month they are no longer on Medicaid
  - this is a broad exit measure

- `medicaid_exit_to_uninsured_next`
  - this month the person is on pure Medicaid
  - next month they move to no coverage
  - this is the sharper bad outcome

Interpretation rule:

- if an exposure only predicts broad exit, it may reflect transitions to other coverage
- if it also predicts `exit_to_uninsured`, it is more consistent with harmful or avoidable churn

## Literature And Official Support

### 1. General theory: administrative burden is a real health-policy mechanism

- Herd and Moynihan argue that administrative burden in health policy is not just paperwork noise; it changes access and disproportionately harms vulnerable groups.
- Source: https://journals.sagepub.com/doi/10.37808/jhhsa.43.1.2

### 2. Medicaid unwinding heavily features procedural loss

- MACPAC reports that from `April 2023` to `June 2024`, roughly `68.7%` of reported disenrollments were procedural terminations.
- Source: https://www.macpac.gov/wp-content/uploads/2024/11/State-Reported-Medicaid-Unwinding-Data-Brief.pdf

- GAO reports roughly `70%` procedural disenrollment and highlights state outreach strategies aimed at people at risk of failing renewal.
- Source: https://www.gao.gov/products/gao-25-107413

### 3. Administrative burden is not randomly distributed

- LEP beneficiaries are more exposed to renewal barriers and procedural loss.
- Sources:
  - https://pubmed.ncbi.nlm.nih.gov/33755840/
  - https://www.kff.org/medicaid/unwinding-of-the-phe-maintaining-medicaid-for-people-with-limited-english-proficiency/
  - https://www.macpac.gov/wp-content/uploads/2024/07/Enrollment-and-Access-Barriers-for-People-with-Limited-English-Proficiency.pdf

- Racial and socioeconomic gaps in renewal failure are also documented in recent medical-policy literature.
- Sources:
  - https://jamanetwork.com/journals/jamainternmedicine/fullarticle/2819478
  - https://jamanetwork.com/journals/jama-health-forum/fullarticle/2831563

### 4. Outreach and navigation can reduce loss caused by burden

- Experimental evidence shows that navigation and assistance can improve successful renewal and reduce administrative coverage loss.
- Source: https://www.nber.org/papers/w34191

## Current Empirical Read

This memo should be read together with:

- [churn_unwinding_round2_diagnostics_memo.md](churn_unwinding_round2_diagnostics_memo.md)
- [../outputs/design_diagnostics/churn_unwinding_second_round_diagnostics.md](../outputs/design_diagnostics/churn_unwinding_second_round_diagnostics.md)

The main empirical takeaways are:

- `procedural_termination_burden` is not currently the clean winner
- `pending_backlog_burden` can look strong, but it is timing-fragile because its best performance comes through `lead1`
- `manual_renewal_burden` currently provides the cleanest gate-eligible timing pattern under the implemented rule set
- `ex_parte_renewal_relief` remains theoretically important and empirically plausible, even though it did not become the formal timing winner

## Testable Hypotheses For The Current Stack

- `H1`: higher `administrative renewal burden` should raise next-month Medicaid exit among people currently on pure Medicaid
- `H2`: the more harmful burden proxies should also raise `exit_to_uninsured`, not just broad exit
- `H3`: protective automation proxies such as `ex parte renewal relief` should move in the opposite direction
- `H4`: burden effects should be more visible in subgroups that already face tighter administrative or financial margins

## What This Memo Allows And What It Does Not

This memo supports:

- writing the mechanism section around `administrative renewal burden`
- treating current exposure families as measurable sub-channels
- justifying continued risk-oriented or design-diagnostic work

This memo does **not** support:

- claiming that `procedural friction` alone has already been identified as the dominant mechanism
- claiming that the current exposure family is already a clean causal treatment
- jumping directly to `DML` or `causal targeting`

The right next use of this framework is:

- keep the theory broad enough to fit the evidence
- keep the empirical claims narrower than the theory
- let future escalation depend on whether the selected burden proxy remains stable in stronger designs
