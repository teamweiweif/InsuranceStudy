# Current Exploration Handoff

Last updated: `2026-04-11`

## Purpose

This document is a compact handoff for a new agent with no prior memory.

It summarizes:

- the current accepted project state
- what has already been tried and what the current preliminary results actually show
- why the project is likely not yet publication-ready in its current form
- which new research directions look most promising
- what public-data feasibility work has already been completed

Read the canonical execution record first:

- [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)

Newest round-2 additions:

- [churn_unwinding_round2_execution_handoff.md](churn_unwinding_round2_execution_handoff.md)
- [churn_unwinding_round2_diagnostics_memo.md](churn_unwinding_round2_diagnostics_memo.md)
- [churn_unwinding_administrative_burden_memo.md](churn_unwinding_administrative_burden_memo.md)
- [churn_unwinding_avoidable_churn_memo.md](churn_unwinding_avoidable_churn_memo.md)
- [churn_unwinding_outcome_reassessment_memo.md](churn_unwinding_outcome_reassessment_memo.md)
- [churn_unwinding_avoidable_churn_results_briefing.md](churn_unwinding_avoidable_churn_results_briefing.md)
- [churn_unwinding_next_tests_memo.md](churn_unwinding_next_tests_memo.md)
- [churn_unwinding_round3_robustness_memo.md](churn_unwinding_round3_robustness_memo.md)
- [churn_unwinding_paper_strategy_memo.md](churn_unwinding_paper_strategy_memo.md)
- [churn_unwinding_progress_record.md](churn_unwinding_progress_record.md)
- [empirical_result_reporting_convention.md](empirical_result_reporting_convention.md)

This file is now secondary background context, not the execution-control document.

## Fast Take

The workspace still contains one serious legacy baseline pipeline:

- pooled `MEPS FYC 2002-2017 Medicare@65`

But the current active research line is now:

- `coverage churn / Medicaid unwinding / continuity of care`

That pipeline is real, reproducible, and not just scratch work. It already produces:

- harmonized pooled data
- pooled RD / fuzzy RD estimates
- robustness tables
- exploratory GRF HTE
- exploratory policy-tree outputs

However, after reviewing the code, outputs, the public-data audit, and the current unwinding design constraints, the most important conclusion is:

- the current `Medicare@65 RDD + causal ML` direction is a reusable analytical asset, not the lead line
- the strongest current line is now `coverage churn / Medicaid unwinding / continuity of care`

## Legacy Baseline Project State

Reusable baseline workflow:

- [README.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/README.md)
- [project_map.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/project_map.md)
- [prepare_pooled_2002_2017.R](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/pipeline/prepare_pooled_2002_2017.R)
- [run_rdd_pooled_2002_2017.R](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/pipeline/run_rdd_pooled_2002_2017.R)

Main active outputs:

- [outputs/rdd_pooled_2002_2017](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/rdd_pooled_2002_2017)
- [outputs/harmonization_report](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/harmonization_report)

Canonical active dataset:

- [pooled_2002_2017.parquet](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/derived/pooled_2002_2017.parquet)
- [pooled_2002_2017.rds](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/derived/pooled_2002_2017.rds)

Archive policy:

- older single-year Medicare@65 runs
- age-26 prototype code
- older pooled code
- earlier acquisition/prototype materials

have been moved under:

- [archive](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/archive)

## What The Current Medicare@65 Pipeline Actually Does

Data engineering:

- harmonizes yearly MEPS FYC files into canonical variable names
- derives age-in-months around age 65 and age 26
- constructs treatment proxies, churn variables, catastrophic OOP, and binary recodes

Key feature code:

- [harmonize_variables.R](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/src/features/harmonize_variables.R)
- [derive_features.R](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/src/features/derive_features.R)

Current active identification / modeling chain:

1. pooled sample restricted to `2002-2017`
2. RD window of `+/-120` months around age 65
3. fuzzy RD using `t_medicare_any = 1[MCREV == 1]`
4. exploratory HTE via `grf::instrumental_forest`
5. exploratory targeting via `policytree`

## What The Current Results Show

Main result files:

- [rd_results.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/rdd_pooled_2002_2017/tables/rd_results.csv)
- [robustness.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/rdd_pooled_2002_2017/tables/robustness.csv)
- [var_importance.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/rdd_pooled_2002_2017/tables/var_importance.csv)
- [run_20260402_030356.txt](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/outputs/rdd_pooled_2002_2017/logs/run_20260402_030356.txt)

Current pooled sample:

- `92,804` observations
- years `2002-2017`
- `163` columns

Strongest findings:

- first stage around age 65 is strong, about `0.53`
- the most stable pooled effect is lower OOP burden
- pooled fuzzy RD for `TOTSLF` is about `-289`
- `log_totslf` is also negative
- `cat_oop05` declines
- `y_afrdca42` has a small negative effect

Why the current pipeline still matters:

- it shows the codebase is already capable of harmonization, pooled estimation, and exploratory causal ML
- it also shows that single-year testing was too unstable, which is why the project moved to pooled analysis

## Why The Current Pipeline Is Not Yet Publication-Ready

The current Medicare@65 setup is useful, but not yet strong enough as a paper core.

Main reasons:

- the topic itself is crowded; classical Medicare-at-65 financial risk / utilization results already exist
- the current mechanism work is still mostly a large outcome battery, not a tight mechanism story
- spending variables still need inflation adjustment
- the active pooled RD helper does not currently use survey weights or cluster-robust design, even though older code did
- annual outcomes and round-specific outcomes currently share the same running-variable / treatment logic too loosely
- the all-outcome HTE loop is effectively not complete; in practice only `TOTSLF` really ran cleanly
- policy-tree output exists, but current sign/value interpretation still needs caution

Short version:

- this is a serious exploratory pipeline
- it is not yet a defendable final paper package

## Research-Direction Reassessment

Detailed memo:

- [research_directions_analysis.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/research_directions_analysis.md)

After combining the internal project review with external gap scanning, the preferred direction ranking became:

1. `coverage churn / Medicaid unwinding / continuity of care`
2. `underinsurance / medical financial hardship despite coverage`
3. `MCBS-based Medicare plan choice / MA vs TM`

### Why Priority 1 Became The Lead Direction

This direction is strongest because it fits all three criteria at once:

- strong current policy gap
- public data are realistically available
- DML / causal ML can be the core contribution rather than decoration

Why it is stronger than staying with Medicare@65:

- it is less saturated
- it naturally uses larger samples than an RD window
- it makes heterogeneity and targeting substantively central
- it gives a clean role for DML, causal forest, and policy learning

## Public Data Feasibility Work Already Completed

Detailed audit:

- [public_data_feasibility_audit.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/public_data_feasibility_audit.md)
- [public_batch_acquisition_run_2026-04-10.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/public_batch_acquisition_run_2026-04-10.md)

Supporting directory:

- [reference/external/feasibility_audit](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/reference/external/feasibility_audit)
- [data/raw/feasibility_audit](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit)

Reusable acquisition script:

- [fetch_public_data_feasibility.ps1](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/acquisition/fetch_public_data_feasibility.ps1)

Audit summary:

- `37` artifacts downloaded successfully
- `1` artifact blocked by host-side `403`

Follow-up batch acquisition:

- a larger automated run was then executed across the shortlisted priority sources
- see [public_batch_acquisition_run_2026-04-10.md](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/docs/public_batch_acquisition_run_2026-04-10.md)
- that run queued `111` artifacts and completed with `105` downloads, `5` reused existing files, and `1` logged failure

Blocked item:

- `ASPE coverage-access-2021-2024.pdf`

### What Is Already Local

#### SIPP

Local status:

- 2024 users guide
- 2024 data dictionary
- 2024 release notes
- 2024 schema
- 2024 main CSV zip
- 2024 longitudinal weights zip
- 2022 health-insurance variable error note

Important finding:

- `pu2024.csv` is locally staged via zip and expands to about `3.43 GB`

This confirms:

- `SIPP` is fully viable for coverage transitions / churn / continuity work

#### HPS / HTOPS

Local status:

- 2025 and 2024 topical public-use CSV zips
- source-and-accuracy document
- datasets landing page

Important finding from zip preview:

- the 2025 topical zip includes:
  - main public-use CSV
  - replicate-weight CSV
  - data dictionary workbook

This confirms:

- `HPS` is easy to use for fast policy-timing screens and auxiliary state-period analysis

#### NHIS

Local status:

- 2024 sample adult CSV zip
- codebook
- summary
- questionnaire
- survey description

This confirms:

- `NHIS` is easy to prototype for access / unmet need / usual-source outcomes

#### MEPS Longitudinal

Local status:

- `HC-244` documentation and codebook
- `HC-245` documentation and codebook
- `HC-244` Stata zip
- `HC-245` Stata zip

This confirms:

- the project is not limited to FYC pooled cross-sections
- public longitudinal MEPS is available and already staged

#### Medicaid Unwinding

Local status:

- monthly snapshot PDFs
- eligibility-processing specifications PDF
- Medicaid snapshot landing page
- Data.Medicaid.gov snapshot page

Important finding:

- the saved underlying page exposes metadata IDs for the snapshot resources

This confirms:

- the official unwinding data ecosystem is available
- but the underlying export/API still needs a dedicated extraction script

#### CFPB

Local status:

- medical debt burden report
- older-Americans issue-spotlight page
- complaints API documentation page

Important finding:

- full complaints bulk file is public but large, about `1.8 GB`

This confirms:

- CFPB is feasible as a contextual or supplemental layer
- but should not be bulk-ingested casually without a specific design

#### MCBS

Local status:

- 2024 early-release survey file zip
- glossary
- user FAQ
- landing page

Important finding from zip preview:

- the package includes tutorials, codebooks, release notes, methodology, questionnaires, and survey files

This confirms:

- the `MCBS / MA vs TM` direction is technically feasible

## Best Current Recommendation

If a new agent had to choose one line to develop now, the best choice is:

- `coverage churn / Medicaid unwinding / continuity of care`

Best initial data stack:

1. `SIPP` as the main longitudinal person-level engine
2. `HPS` for fast state-period policy scans
3. `NHIS` for access validation
4. `MEPS longitudinal` for richer spending and access follow-up
5. `Medicaid.gov / Data.Medicaid.gov` for official unwinding timing and operational context

## What Has Not Been Done Yet

Important unfinished items:

- no cross-dataset variable map has been built yet
- no systematic variable extraction has been run on the newly downloaded data bundles
- no `Data.Medicaid.gov` API/export ingestor has been written yet
- no unified prototype panel has been built across the new priority-1 sources
- no final decision memo has been written that converts the new direction into one exact paper title/design

## Most Useful Immediate Next Steps

This section now serves as broader exploration background only.

For the current active execution path, follow:

- [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)

The older broad exploration sequence was:

1. inspect the downloaded raw files and codebooks
2. build a variable map across `SIPP`, `HPS`, `NHIS`, `MEPS longitudinal`, and `MCBS`
3. script `Data.Medicaid.gov` extraction for the snapshot data
4. run a quick feasibility prototype for `priority1`
5. only after that, decide whether `priority2` or `priority3` should remain active backups

## Suggested Reading Order For A New Agent

Read in this order:

1. [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)
2. [../outputs/data_audit/sipp_preflight_2026-04-10.md](../outputs/data_audit/sipp_preflight_2026-04-10.md)
3. [../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md](../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md)
4. [churn_targeting_reset_2026-04-10.md](churn_targeting_reset_2026-04-10.md)
5. [current_exploration_handoff.md](current_exploration_handoff.md)
6. [public_data_feasibility_audit.md](public_data_feasibility_audit.md)

## One-Sentence Handoff

The workspace has a functioning but likely non-final `MEPS Medicare@65` exploratory pipeline; after internal review and external gap/data scanning, the strongest next paper candidate is now `coverage churn / Medicaid unwinding / continuity of care`, and the key public datasets needed for that pivot have already been located and mostly downloaded into the workspace.
