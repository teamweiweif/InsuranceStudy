# US Health Insurance Project

This repository tracks the code, documentation, and lightweight result summaries for a public-data health insurance research project.

The original reusable baseline is a pooled `MEPS FYC 2002-2017` Medicare-at-65 workflow. The current active research frontier has shifted to:

- `SIPP + CMS Medicaid unwinding`
- coverage churn and continuity of coverage
- avoidable harmful churn during the unwinding period
- bounded risk ranking before any causal-ML escalation

Large raw data, intermediate person-month files, parquet outputs, external reference snapshots, and archived scratch material are intentionally kept out of git.

## Current Status

The canonical handoff is:

- `docs/churn_unwinding_execution_handoff.md`

The latest progress ledger is:

- `docs/churn_unwinding_progress_record.md`

As of the latest documented round, the strongest current branch is the `avoidable churn` diagnostic line:

- preferred harmful outcome: `persistent_uninsured_h2`
- preferred exposure candidate: `backlog_automation_rank_index / same`
- latest verdict: `ROUND3_SUPPORTS_CONTINUATION`

This does **not** mean the project is ready for `DID`, `DML`, `causal forest`, or causal policy targeting. The current validated phase is still diagnostic / risk-first.

## Suggested Reading Order

1. `docs/churn_unwinding_execution_handoff.md`
2. `docs/churn_unwinding_progress_record.md`
3. `docs/churn_unwinding_round3_robustness_memo.md`
4. `docs/churn_unwinding_next_tests_memo.md`
5. `docs/current_exploration_handoff.md`

For the older Medicare-at-65 baseline, see:

- `docs/project_briefing_for_reasoning.md`
- `scripts/pipeline/prepare_pooled_2002_2017.R`
- `scripts/pipeline/run_rdd_pooled_2002_2017.R`
- `outputs/rdd_pooled_2002_2017/`

## Reproducibility Layout

- `docs/`: handoffs, strategy memos, progress records, and design decisions.
- `scripts/`: acquisition scripts, SIPP/CMS prototypes, diagnostics, and legacy MEPS pipeline entrypoints.
- `src/`: reusable R feature engineering, QC, and project path helpers.
- `outputs/`: lightweight markdown, JSON, CSV, and figure summaries only.

Excluded local-only directories:

- `data/`
- `archive/`
- `reference/external/`

## Next Empirical Frontier

The next recommended empirical work is:

1. timing stress tests
2. subgroup stability round 2
3. bounded risk-ranking round 2

Classical time-series models and immediate causal ML are not the current bottleneck.
