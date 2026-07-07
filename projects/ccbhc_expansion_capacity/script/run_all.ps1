$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location $root
try {
    $scripts = @(
        "script/00_setup.py",
        "script/01_acquire_sources.py",
        "script/02_policy_and_treatment_panel.py",
        "script/03_build_facility_county_panels.py",
        "script/04_construct_outcomes.py",
        "script/05_descriptive_diagnostics.py",
        "script/06_main_models.py",
        "script/07_synthetic_and_selection_checks.py",
        "script/08_mechanism_heterogeneity.py",
        "script/09_write_report.py"
    )

    foreach ($script in $scripts) {
        Write-Host "Running $script"
        & python $script
        if ($LASTEXITCODE -ne 0) {
            throw "$script failed with exit code $LASTEXITCODE"
        }
    }
}
finally {
    Pop-Location
}
