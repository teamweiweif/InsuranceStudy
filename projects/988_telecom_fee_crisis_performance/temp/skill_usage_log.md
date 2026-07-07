# Skill Usage Log

Project: Do 988 Telecom Fees Improve Crisis-Line Performance? Evidence from State-Month KPI Panels.

Date started: 2026-07-07

## Discovery

Checked local skill locations:

- `C:\Users\PC\.agents\skills`
- `.agents\skills`
- `C:\Users\PC\.codex\skills`
- `.codex\skills`
- repository-level `skills`
- Codex-provided skill registry in the session context

Installed matches found and read:

| Skill name | Skill path | Summary | Project phase where used | Advice adopted | Advice rejected | Reason for rejection |
|---|---|---|---|---|---|---|
| auto-empirical-research-skills | `C:\Users\PC\.codex\skills\auto-empirical-research-skills\SKILL.md` | Router for the AERS catalog. It says to classify the empirical task by stage and load only focused child skills. | Phase 1 onward | Use a targeted set of empirical, identification, robustness, replication, and writing skills instead of recursively loading the entire catalog. | Broad recursive reading of every vendored skill. | The router explicitly warns against reading the entire repository. |
| Full-empirical-analysis-skill | `C:\Users\PC\.codex\skills\empirical-analysis-python\SKILL.md` | End-to-end Python empirical workflow: cleaning, variable construction, Table 1, diagnostics, DID/SCM/matching, robustness, mechanisms, and publication-ready tables/figures. | Pipeline design, scripts, diagnostics, models, exports | Build explicit sample logs, data contracts, dated empirical strategy, Table 1 before models, event-study figures, robustness/specification curves, and reproducibility stamps. | Exact default table paths such as `tables/`; this project must use `result/` and `report/` per user instructions. | User-specified project layout overrides default skill layout. |
| causal-inference | `C:\Users\PC\.codex\skills\auto-empirical-research-skills\skills\11-James-Traina-compound-science\skills\causal-inference\SKILL.md` | Method guide for IV, DID, RD, synthetic control, matching/AIPW, diagnostics, target estimands, and common anti-patterns. | Identification audit, model choice, robustness | Use modern staggered DID, synthetic/synthetic-DID or matched donor comparisons, pre-trend diagnostics, anticipation checks, and few-cluster inference cautions. | Naive TWFE as the only model. | Fee adoption is staggered and effects may be heterogeneous. |
| aer-workflow | `C:\Users\PC\.codex\skills\aer-workflow\SKILL.md` | Router for AER-style workflow gates from identification through robustness, writing, consistency, and replication. | Overall sequencing | Treat identification as a gate before writing; defer final framing until empirical outputs exist. | AER-only submission assumptions. | This is a research package first; journal targeting remains open. |
| aer-identification | `C:\Users\PC\.codex\skills\aer-identification\SKILL.md` | AER identification checklist covering modern DID, IV, RD, SCM, diagnostics, and red flags. | Identification audit and model scripts | Avoid staggered TWFE as sole estimator; report event-study/pre-trend diagnostics; use synthetic or matched designs for few treated states. | IV/RD branches. | No credible IV or running-variable discontinuity is part of the present design. |
| aer-robustness | `C:\Users\PC\.codex\skills\aer-robustness\SKILL.md` | Robustness, heterogeneity, mechanism, placebo, and specification-curve expectations. | Robustness, mechanism, moderation | Include alternative timing, samples, outcomes, clusters, placebo dates, leave-one-out, and mechanism-predicted heterogeneity. | Exhaustive mined heterogeneity. | User requires theory-driven heterogeneity and warns against decorative causal ML. |
| aer-replication | `C:\Users\PC\.codex\skills\aer-replication\SKILL.md` | AEA-style reproducibility package guidance: README, source provenance, relative paths, one master script, package versions, exhibit register. | Reproducibility and README | Use one-command pipeline, source inventory, relative paths, checksums, package versions, and exhibit/source mapping. | AEA repository folder names such as `code/` and `output/`. | User specified `script/`, `data/`, `result/`, `report/`, and `temp/`. |
| econ-write | `C:\Users\PC\.agents\skills\econ-write\SKILL.md` | Economics paper-writing guidance: reader-first, concrete findings, data/strategy/results structure, identification prose, table notes, limitations, concise abstract. | Phase 10 after empirical outputs exist | Use finding-first report structure, concrete magnitudes, clear identification assumptions, disciplined limitations, and concise abstract-style summary. | Writing final claims before results exist. | The user explicitly says to use economics-writing only after empirical outputs exist. |

## Current Skill-Guided Operating Rules

1. Use official sources first and log all source provenance.
2. Distinguish enactment, effective, collection, revenue, and plausible operational-effect dates.
3. Treat calls as the primary outcome family.
4. Use modern staggered-adoption DID and matched/synthetic comparisons; do not rely on naive TWFE alone.
5. Keep all raw downloads, snapshots, parsing checks, scratch outputs, and audit notes in `temp/`.
6. Keep only analysis-ready datasets in `data/`.
7. Keep scripts reusable, with one command to rerun the main workflow.

