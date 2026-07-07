$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

python script/00_setup.py
python script/01_acquire_sources.py
python script/02_parse_988_kpi_pdfs.py
python script/03_build_treatment_timing.py
python script/04_build_covariates_mechanisms.py
python script/05_build_analysis_panel.py
python script/06_descriptive_diagnostics.py
python script/07_main_models.py
python script/08_robustness_and_sensitivity.py
python script/09_mechanism_moderation_heterogeneity.py
python script/10_write_report.py

Write-Host "Pipeline complete. See report/final_report.md and report/go_no_go_assessment.md."
