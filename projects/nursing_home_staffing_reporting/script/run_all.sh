#!/usr/bin/env bash
set -euo pipefail

python script/00_setup.py
python script/01_acquire_sources.py
python script/02_build_analysis_data.py
python script/03_construct_exposures_outcomes.py
python script/04_descriptive_diagnostics.py
python script/05_main_models.py
python script/06_robustness.py
python script/07_write_report.py
