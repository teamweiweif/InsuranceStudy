# Public Batch Acquisition Run 2026-04-10

## Purpose

This note records the first large automated public-data acquisition run after the initial feasibility pass.

The goal was to:

- execute the highest-value bulk downloads without manual intervention
- prioritize sources attached to the three shortlisted research directions
- skip failures automatically
- leave a clean local paper trail for later agents

Current status note:

- acquisition is now complete enough for the current `SIPP` prototype path
- execution sequencing now lives in [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)
- this file remains a run record, not the execution-control document

## Execution Context

Run date:

- `2026-04-10`

Primary script:

- [run_priority_public_batch_acquisition.ps1](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/acquisition/run_priority_public_batch_acquisition.ps1)

Successful batch run folder:

- [20260410_105055](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/reference/external/feasibility_audit/batch_runs/20260410_105055)

Run artifacts:

- [batch_manifest.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/reference/external/feasibility_audit/batch_runs/20260410_105055/batch_manifest.csv)
- [batch_download_log.csv](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/reference/external/feasibility_audit/batch_runs/20260410_105055/batch_download_log.csv)
- [batch_summary.txt](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/reference/external/feasibility_audit/batch_runs/20260410_105055/batch_summary.txt)

## Outcome Summary

The successful run covered `111` queued artifacts.

Status counts:

- `105` downloaded
- `5` already existed and were kept as-is
- `1` failed

Observed run window from the log:

- start: `2026-04-10T10:50:58Z`
- end: `2026-04-10T10:58:24Z`
- duration: about `7.43` minutes

Current staged storage after the run:

- raw data under [data/raw/feasibility_audit](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit): about `4.2 GB` across `92` files
- reference materials under [reference/external/feasibility_audit](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/reference/external/feasibility_audit): about `0.176 GB` across `104` files

## What Was Acquired

### Priority 1: Churn / Unwinding / Continuity

This was the dominant target of the run.

- `SIPP`: `2018-2024` main public-use CSV zips plus machine-readable schemas
- `HPS`: `2023` weeks `52-63`, `2024` cycles `01-09`, `2024` topical bundles, and `2025` topical bundles
- `NHIS`: `2019-2024` sample-adult CSV zips plus adult codebooks where accessible
- `MEPS`: longitudinal XLSX bundles for `HC-244` and `HC-245`
- `Medicaid`: official snapshot and monthly-report pages were parsed, then `56` linked unwinding/snapshot PDFs were downloaded into a local reports folder

Representative local paths:

- [sipp](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/sipp)
- [hps](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/hps)
- [nhis](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/nhis)
- [meps](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/meps)
- [medicaid_unwinding](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/reference/external/feasibility_audit/medicaid_unwinding)

### Priority 2: Underinsurance

- `CFPB` full complaints bulk archive was downloaded

Representative local path:

- [complaints.csv.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/cfpb/complaints.csv.zip)

### Priority 3: MCBS / MA vs TM

- `MCBS 2022` survey-file zip was downloaded

Representative local path:

- [2022_mcbs_survey_file.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/mcbs/2022/2022_mcbs_survey_file.zip)

## Largest Additions

The largest staged files in this run are:

- [complaints.csv.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/cfpb/complaints.csv.zip): about `1.80 GB`
- [pu2018_csv.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/sipp/2018/pu2018_csv.zip): about `164 MB`
- [pu2021_csv.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/sipp/2021/pu2021_csv.zip): about `157 MB`
- [pu2020_csv.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/sipp/2020/pu2020_csv.zip): about `139 MB`
- [pu2019_csv.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/sipp/2019/pu2019_csv.zip): about `135 MB`

## Existing Files Reused

The batch script intentionally skipped files that were already staged from the earlier feasibility pass.

Existing items reused in this run:

- [pu2024_csv.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/sipp/2024/pu2024_csv.zip)
- [HPS_DECEMBER2024_PUF_CSV.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/hps/2024/HPS_DECEMBER2024_PUF_CSV.zip)
- [HTOPS_HPS_2504_CSV.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/hps/2025/HTOPS_HPS_2504_CSV.zip)
- [adult24csv.zip](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/data/raw/feasibility_audit/nhis/2024/adult24csv.zip)
- [2024_adult_codebook.pdf](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/reference/external/feasibility_audit/nhis/2024_adult_codebook.pdf)

## Failure And Skip Notes

Only one item failed in the successful run:

- `reference/external/feasibility_audit/nhis/2022_adult_codebook.pdf` was requested from `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHIS/2022/adult-codebook.pdf` and did not download, so no local file exists for that item

The script did not stop on this failure. It logged the failure and continued.

Separate from this batch run, the earlier feasibility pass had already identified one host-blocked manual item:

- `ASPE coverage-access-2021-2024.pdf` returned `403` during scripted retrieval attempts

## Process Notes

There was one short aborted attempt before the successful run:

- [20260410_105041](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/reference/external/feasibility_audit/batch_runs/20260410_105041)

Reason:

- PowerShell treated `curl` progress/stderr output as a stopping native-command error

The acquisition script was then patched to make the batch robust:

- set `$PSNativeCommandUseErrorActionPreference = $false`
- switched `curl` calls to silent mode with `-sS`

After that change, the rerun completed cleanly.

## Reading Order For A New Agent

Use these in order:

1. [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md)
2. [../outputs/data_audit/sipp_preflight_2026-04-10.md](../outputs/data_audit/sipp_preflight_2026-04-10.md)
3. [../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md](../outputs/data_audit/sipp_2024_deep_audit_2026-04-10.md)
4. [current_exploration_handoff.md](current_exploration_handoff.md)
5. [public_batch_acquisition_run_2026-04-10.md](public_batch_acquisition_run_2026-04-10.md)
6. [run_priority_public_batch_acquisition.ps1](D:/GlobalHealthPolicy Dropbox/Fan Bowei/US Insurance Project/scripts/acquisition/run_priority_public_batch_acquisition.ps1)

## Immediate Next Step

The most useful next non-download step is now:

- follow [churn_unwinding_execution_handoff.md](churn_unwinding_execution_handoff.md), starting with the `2024 SIPP` coverage-layer prototype path rather than opening a broad cross-source ingestion phase
