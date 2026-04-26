# Paper Outline User Summary

Last updated: `2026-04-27`

## What Would The Paper Be About?

The paper would be about Medicaid unwinding, administrative renewal burden, and the risk that people who exit Medicaid remain uninsured.

The core framing is:

`Administrative renewal burden and persistent uninsurance risk during Medicaid unwinding: a public-data risk and vulnerability study.`

This is a public-data health policy paper. It is not a causal ML paper and not a targeting paper.

## Main Findings So Far

The main findings are:

- SIPP person-month data can support a useful persistent-uninsurance outcome after Medicaid exit.
- The main harmful outcome is `persistent_uninsured_h2`.
- The leading burden candidate is `backlog_automation_rank_index / same`.
- Timing stress passed with caveat: same-month timing stayed strongest in the main windows.
- The future-month placebo did not dominate the best non-lead timing.
- Three subgroup families show more stable harmful-risk ordering:
  - `foreign_born_group`
  - `household_child_group`
  - `snap_group`
- Risk-ranking models beat a naive state baseline.
- Compact boosting captured `19.66%` of weighted `persistent_uninsured_h2` events in the top decile.

## Main Tables And Figures

Main tables should be:

- Table 1: data construction and sample/support summary
- Table 2: burden candidate and timing-stress results
- Table 3: harmful churn outcome family and robustness
- Table 4: subgroup stability and vulnerability ordering
- Table 5: risk-ranking model performance
- Table 6 or appendix table: allowed versus forbidden claims and caveats

Main figures should be:

- Figure 1: design diagram linking SIPP person-month transitions to CMS state-month renewal burden
- Figure 2: timeline for `persistent_uninsured_h2`
- Figure 3: timing-stress comparison for `backlog_automation_rank_index`
- Figure 4: subgroup stability visualization
- Figure 5: top-decile capture and calibration diagnostic

## What Is Still Weak?

The weak points are:

- The design is diagnostic, not causal.
- The CMS reporting month may not line up perfectly with person-level coverage loss.
- Event rates are low.
- Risk-model AUC is modest.
- Calibration is weak.
- The old-pilot comparison is mixed.
- The model is useful for ranking, not for assigning outreach treatment.

## What Should Happen Next?

The next step should be to build table-ready and figure-ready files from the existing outputs.

Recommended next artifact:

`scripts/design_diagnostics/build_path_a_paper_tables.py`

This should create the final CSV panels for the proposed tables and figures. Do not start causal estimation, do not open new datasets, and do not switch topics.
