# Skill Usage Log

Created: 2026-07-07

This log records installed skills discovered for the nursing-home staffing reporting project, where they were used, and which advice was adopted or rejected.

## Discovery

Local skill roots inspected:

- `C:\Users\PC\.codex\skills`
- `C:\Users\PC\.agents\skills`

Relevant installed skills found:

| Skill | Path | Match reason | Task stage used | Advice adopted | Advice rejected or deferred |
|---|---|---|---|---|---|
| `auto-empirical-research-skills` | `C:\Users\PC\.codex\skills\auto-empirical-research-skills\SKILL.md` | Router for AERS empirical-research workflows | Skill routing and project scoping | Use focused child skills rather than recursively loading all vendored skills; classify the task as full empirical pipeline plus causal identification and AER-style reproducibility. | Did not create or install new custom skills because the objective explicitly requires using existing installed skills. |
| `empirical-analysis-python` / `Full-empirical-analysis-skill` | `C:\Users\PC\.codex\skills\empirical-analysis-python\SKILL.md` | Full Python empirical pipeline, panel FE, event study, robustness, tables and figures | Data construction, diagnostics, modeling, robustness, output design | Use explicit source/sample logs, data contracts, panel duplicate checks, Table 1/balance diagnostics, raw trends, event-study plots, main panel FE models, placebo/specification checks, and reproducibility stamps. | Deferred ML-causal and epidemiology modes because the project is a national policy panel design, not a CATE targeting or target-trial problem. |
| `aer-workflow` | `C:\Users\PC\.codex\skills\aer-workflow\SKILL.md` | AER-style sequencing and quality gates | Sequencing | Identification must be stable before report writing; robustness and replication gates precede final prose. | Did not run topic-selection or literature-review skills because the objective fixes the research question and asks for empirical workspace construction. |
| `aer-identification` | `C:\Users\PC\.codex\skills\aer-identification\SKILL.md` | Causal identification, DiD/event-study, pre-trends, inference | Identification audit and model design | Treat identification as exposure-weighted DiD/event-study with facility and time fixed effects; do not label lower-exposure facilities untreated; require visual and formal pre-trend checks. | Rejected staggered-adoption estimators as the primary design because the policy timing is national and simultaneous; retained event-time interactions with pre-treatment exposure instead. |
| `aer-robustness` | `C:\Users\PC\.codex\skills\aer-robustness\SKILL.md` | Robustness, heterogeneity, placebo checks | Robustness design | Include alternative exposure definitions, alternative periods, facility-month and facility-quarter panels, placebo dates, weekday contrast outcomes, ownership heterogeneity, and sample/missingness checks. | Rejected decorative robustness that does not address plausible threats, such as causal ML without a targeting question. |
| `aer-replication` | `C:\Users\PC\.codex\skills\aer-replication\SKILL.md` | Reproducible research package and README audit | Reproduction structure and report README | Use a one-command runner, relative paths, package/version documentation, source inventory, source provenance, and output-to-script mapping. | Full AEA/openICPSR packaging is deferred; this workspace is an audit-ready research package, not a final journal deposit. |
| `causal-inference-mixtape` | `C:\Users\PC\.codex\skills\causal-inference-mixtape\SKILL.md` | DiD/event-study implementation patterns | Model implementation | Use explicit lead/lag event-time indicators, fixed effects, clustered standard errors, parallel-trends plots, and placebo timing checks. | Avoided simple two-group untreated DiD templates because there is no never-treated group in a national reform. |
| `econ-write` | `C:\Users\PC\.codex\skills\econ-write\SKILL.md` | Economics paper writing, data/results/limitations framing | Final report only, after empirical outputs exist | Write the report in reader-first order: executive summary, exact data and exposure definitions, identification assumptions, concrete results, limitations, and go/no-go judgment. | Not used to draft claims before estimates exist; prose must follow actual diagnostics and model outputs. |
| `econ-write` | `C:\Users\PC\.agents\skills\econ-write\SKILL.md` | Duplicate economics-writing skill in agent root | Documented as discovered but not separately used | Preferred the `.codex\skills` copy because it was directly available in the Codex skill root and read for this task. | Duplicate not used to avoid conflicting copies of the same guidance. |

## Stage Log

- Phase 1 source and policy audit: use `auto-empirical-research-skills`, `aer-workflow`, `aer-replication`.
- Phase 2 raw data acquisition and schema audit: use `empirical-analysis-python`, `aer-replication`.
- Phase 3 analysis-ready panel construction: use `empirical-analysis-python`.
- Phase 4 outcome construction: use `empirical-analysis-python`, `aer-identification`.
- Phase 5 exposure and comparison construction: use `aer-identification`, `causal-inference-mixtape`.
- Phase 6 main models: use `empirical-analysis-python`, `aer-identification`, `causal-inference-mixtape`.
- Phase 7 robustness and falsification: use `aer-robustness`, `empirical-analysis-python`.
- Phase 8 final interpretation and report: use `econ-write`, `aer-replication`.
