# Skill Usage Log

Access date: 2026-07-07

The full local registry scan found 1170 SKILL.md files. Matching empirical, causal,
reproducibility, data-audit, and economics-writing paths are listed in
`temp/skill_registry_matching.txt`; the complete path list is in
`temp/skill_registry_all.txt`.

| Skill found/read | Path | Stage used | Advice adopted | Advice rejected and reason |
|---|---|---|---|---|
| auto-empirical-research-skills | C:/Users/PC/.codex/skills/auto-empirical-research-skills/SKILL.md | Router before research | Use focused child skills instead of reading every vendored skill | None |
| Full-empirical-analysis-skill Python | C:/Users/PC/.codex/skills/empirical-analysis-python/SKILL.md | Pipeline design | Explicit cleaning, diagnostics, DID/event-study, robustness, tables and figures | Heavy optional packages rejected because local Python lacks statsmodels/linearmodels and the pipeline can run with NumPy/SciPy |
| aer-workflow | C:/Users/PC/.codex/skills/aer-workflow/SKILL.md | Sequencing | Identification before writing; replication from day one | AER submission-specific gates are out of scope for this early audit |
| aer-identification | C:/Users/PC/.codex/skills/aer-identification/SKILL.md | Identification | Avoid naive staggered TWFE, show pre-trends, use synthetic checks, state identifying assumption | Full Callaway-Sant'Anna not used because all observed treated units share the 2024 selection cohort and public post-period is one year |
| aer-robustness | C:/Users/PC/.codex/skills/aer-robustness/SKILL.md | Robustness | Alternative controls, placebo year/outcome, leave-one-treated-state-out, mechanism/heterogeneity | Broad fishing heterogeneity rejected |
| aer-replication | C:/Users/PC/.codex/skills/aer-replication/SKILL.md | Reproducibility | One-command pipeline, source provenance, environment and output map | AEA deposit PDF not created because this is not a submitted manuscript package |
| aer-tables-figures | C:/Users/PC/.codex/skills/aer-tables-figures/SKILL.md | Results | One claim per exhibit, notes, vector and PNG output | Journal-specific LaTeX styling minimized for Markdown report |
| causal-inference-mixtape | C:/Users/PC/.codex/skills/causal-inference-mixtape/SKILL.md | DID, event study, synthetic | Parallel-trend plots, placebo treatment dates, synthetic placebo logic | R/Stata templates rejected to keep this workspace Python-only |
| data-audit | C:/Users/PC/.codex/skills/auto-empirical-research-skills/skills/29-quarcs-lab-project20XXy/dot-claude/skills/data-audit/SKILL.md | Data audit | Verify referenced files, count rows/columns, document missing sources | Notebook-specific scan not used because this pipeline is script-only |
| reproducible-pipelines | C:/Users/PC/.codex/skills/auto-empirical-research-skills/skills/11-James-Traina-compound-science/skills/reproducible-pipelines/SKILL.md | Workspace | Raw in temp, clean in data, generated results in result/report, single run script | DVC/Snakemake rejected as unnecessary for this compact pipeline |
| did-analysis | C:/Users/PC/.codex/skills/auto-empirical-research-skills/skills/67-econfin-workflow-toolkit/did-analysis/SKILL.md | Main models | State and year fixed effects, clustered SE, event-study pre-trends | County DID rejected because county is not in the N-SUMHSS PUF |
| synthetic-control | C:/Users/PC/.codex/skills/auto-empirical-research-skills/skills/67-econfin-workflow-toolkit/synthetic-control/SKILL.md | Selection checks | Donor-pool construction, pre-fit diagnostics, placebo/weight reporting | Strong SCM claims rejected due only three pre-years and one partial post-year |
| panel-data | C:/Users/PC/.codex/skills/auto-empirical-research-skills/skills/67-econfin-workflow-toolkit/panel-data/SKILL.md | FE implementation | Entity and year FE, cluster at treatment level | Random-effects/Hausman branch not relevant |
| web-research | C:/Users/PC/.codex/skills/auto-empirical-research-skills/skills/67-econfin-workflow-toolkit/web-research/SKILL.md | Source audit | Official-source-first search and cited snapshots | Delegated subagents not used; all source interpretation done by main agent |
| econ-write | C:/Users/PC/.codex/skills/econ-write/SKILL.md and C:/Users/PC/.agents/skills/econ-write/SKILL.md | Final report | Results-first, concrete limitations, no overclaiming, policy-readable summary | Full manuscript introduction not drafted because current evidence is a go/no-go audit |
