.PHONY: all setup acquire build exposures diagnostics models robustness report

all: setup acquire build exposures diagnostics models robustness report

setup:
	python script/00_setup.py

acquire:
	python script/01_acquire_sources.py

build:
	python script/02_build_analysis_data.py

exposures:
	python script/03_construct_exposures_outcomes.py

diagnostics:
	python script/04_descriptive_diagnostics.py

models:
	python script/05_main_models.py

robustness:
	python script/06_robustness.py

report:
	python script/07_write_report.py
