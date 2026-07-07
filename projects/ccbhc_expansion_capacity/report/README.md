# CCBHC Expansion Capacity Workspace

This workspace evaluates whether the 2024 BSCA-authorized CCBHC Medicaid
Demonstration expansion increased behavioral-health capacity.

Run from the project root:

```bash
bash script/run_all.sh
```

On Windows without Bash or Make:

```powershell
powershell -ExecutionPolicy Bypass -File script/run_all.ps1
```

Main clean data are in `data/`, generated results are in `result/`, source
snapshots and raw downloads are in `temp/`, and human-readable outputs are in
`report/`.

Observed N-SUMHSS years in this build: [2021, 2022, 2023, 2024]. The key limitation is
that 2025 N-SUMHSS public-use data are not available in this build, and 2024 is
only a partial/early implementation year for several selected states.
