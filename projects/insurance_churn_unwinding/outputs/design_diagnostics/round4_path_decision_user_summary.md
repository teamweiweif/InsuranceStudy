# Round-4 Path Decision User Summary

Last updated: `2026-04-26`

## What Is The Current State?

The SIPP + CMS Medicaid unwinding project is still alive as the current main paper candidate.

The strongest version is not a causal ML paper. It is a public-data health policy paper about administrative renewal burden, harmful Medicaid churn, persistent uninsurance, subgroup vulnerability, and bounded risk ranking.

Round 4 is now complete:

- Step 1 timing stress passed with caveat.
- Step 2 subgroup stability passed.
- Step 3 risk ranking was mixed but usable.
- Step 4 chooses a narrowed Path A paper.

## Is The Project Still Worth Continuing?

Yes.

The project is worth continuing as a narrowed paper-first line because it has:

- a useful SIPP person-month outcome layer
- a policy-relevant harmful outcome: `persistent_uninsured_h2`
- a CMS state-month administrative burden linkage
- one leading burden candidate: `backlog_automation_rank_index / same`
- stable vulnerability signals for some subgroup families
- risk-ranking models that beat a naive state baseline

The project should not be abandoned or switched to a new topic now.

## What Can We Honestly Claim?

We can honestly claim:

- SIPP can measure persistent uninsurance after Medicaid exit.
- `persistent_uninsured_h2` is more policy-relevant than a one-month exit screen alone.
- CMS renewal-burden measures can be linked to SIPP transition outcomes for diagnostic analysis.
- `backlog_automation_rank_index / same` is the leading administrative-burden candidate after timing stress.
- Some subgroup dimensions have repeatable harmful-risk ordering, especially:
  - `foreign_born_group`
  - `household_child_group`
  - `snap_group`
- Simple risk-ranking models do better than a naive state baseline.
- The project supports a bounded risk-screening or prioritization prototype with caveats.

## What Can We Not Claim?

We cannot claim:

- administrative burden caused persistent uninsurance
- subgroup differences are causal heterogeneity
- the model can assign outreach treatment
- the model is deployment-ready
- predicted probabilities are well calibrated
- this is causal ML
- this is DML
- this is causal forest
- this is DID or event-study evidence
- this is welfare-based targeting

## What Should Happen Next?

The next agent or user should create a constrained paper outline and results-to-table map for the narrowed Path A paper.

That outline should lock:

- the paper question
- the allowed claims
- the main tables and figures
- the outcome definitions
- the exposure definitions
- the subgroup vulnerability section
- the bounded risk-ranking section
- the limitations section

Do not start causal estimation. Do not open new datasets. Do not switch topics.
