# Public Data Feasibility Audit

## Purpose

This audit was created to answer a narrow question:

- Can the three shortlisted research directions be supported with public data that are easy to find, download, and stage inside this workspace?

The three directions are:

1. `priority1_churn_unwinding`: coverage churn / Medicaid unwinding / continuity of care
2. `priority2_underinsurance`: underinsurance / medical financial hardship despite coverage
3. `priority3_mcbs_ma_tm`: Medicare plan choice / MA vs TM

This is a feasibility pass, not a full production ingestion. The goal was to:

- locate official data pages, codebooks, and methodology guides
- download representative raw public files where direct automation was practical
- preserve a reproducible local record of URLs, file locations, and process notes

## What Was Added

Artifacts are split into two areas:

- Raw downloadable data bundles:
  - `data/raw/feasibility_audit/`
- External documentation, codebooks, policy reports, and landing pages:
  - `reference/external/feasibility_audit/`

Reproducible download script:

- `scripts/acquisition/fetch_public_data_feasibility.ps1`

Download manifest and status log:

- `reference/external/feasibility_audit/download_manifest.csv`
- `reference/external/feasibility_audit/download_log.csv`

## Outcome Summary

Current status from `download_log.csv`:

- `37` artifacts downloaded successfully
- `1` artifact blocked by the source host

Blocked item:

- `ASPE` report `coverage-access-2021-2024.pdf`
- URL returned `403 Forbidden` to scripted download attempts
- This is the only remaining item that likely needs manual browser download if you want the local PDF

## Key Source-Level Findings

### SIPP

Downloaded:

- 2024 users guide
- 2024 data dictionary
- 2024 release notes
- 2024 schema JSON
- 2022 user note on monthly health insurance variable issues
- 2025 topical brochure on health coverage/disability
- 2024 main CSV public-use file
- 2024 year-4 longitudinal weights CSV zip

What this proves:

- `SIPP` is directly automatable from official Census URLs.
- The core 2024 CSV zip was downloaded successfully.
- The zip preview shows a single main file:
  - `pu2024.csv` with uncompressed size about `3.43 GB`
- The 2024 file stack is therefore large but fully practical for local work.
- This is the strongest public-data base for the `coverage churn / transitions / continuity` direction.

### HPS / HTOPS

Downloaded:

- 2025 datasets landing page
- 2025 topical source-and-accuracy document
- April 2025 topical CSV zip
- December 2024 topical CSV zip

What this proves:

- `HPS` is easy to automate from direct Census links.
- The April 2025 zip preview shows:
  - one main public-use CSV
  - one replicate-weight CSV
  - one Excel data dictionary
- This makes `HPS` a very good fast-screening platform for `state-month policy timing`, but still better as a screening or external-validation layer than as the only final paper dataset.

### NHIS

Downloaded:

- 2024 survey description
- 2024 sample adult codebook
- 2024 sample adult summary
- 2024 English questionnaire
- 2024 sample adult CSV zip

What this proves:

- `NHIS` is also easy to automate from CDC FTP.
- The sample-adult zip is small and immediately inspectable.
- The zip preview shows `adult24.csv` plus a readme.
- This is a strong validation dataset for `access`, `usual source`, and `cost-related delay` outcomes.

### MEPS Longitudinal

Downloaded:

- `HC-244` documentation and codebook
- `HC-245` documentation and codebook
- `HC-244` Stata zip
- `HC-245` Stata zip

What this proves:

- Public `MEPS longitudinal` files are directly downloadable and easy to stage.
- This matters because it removes the old assumption that the project must stay in FYC-only pooled cross-sections.
- The downloaded bundles are small enough to prototype immediately.
- This is important for both `coverage transitions` and `underinsurance / financial protection` directions.

### Medicaid Unwinding / Snapshot Infrastructure

Downloaded:

- January 2025 snapshot PDF
- December 2024 snapshot PDF
- eligibility processing report specifications
- Medicaid snapshot landing page
- Data.Medicaid.gov snapshot landing page

What this proves:

- Official monthly snapshot PDFs and specifications are directly downloadable.
- The underlying data page was saved successfully.
- The saved HTML shows machine-usable metadata IDs:
  - `processing_metadata_id = 5abea2e0-3f8e-4b49-a50d-d63d5fd9103c`
  - `enrollment_metadata_id = 6165f45b-ca93-5bb5-9d06-db29c692a360`

What is not finished yet:

- I did not yet build a dedicated extractor for the underlying `Data.Medicaid.gov` data export.
- The source is clearly usable, but the next step should be a separate ingestion script that maps those metadata IDs to the final export/API route.

### CFPB

Downloaded:

- medical debt burden report PDF
- older Americans issue spotlight page
- consumer complaints API documentation page

Important note:

- The full complaint bulk file is publicly accessible, but it is large:
  - `complaints.csv.zip` is about `1.8 GB`
- I intentionally did not pull the full complaint archive in this feasibility pass.
- If we decide CFPB complaints belong in the active paper design, we should script filtered API pulls first, not bulk-download blindly.

### MCBS

Downloaded:

- MCBS public-use landing page
- MCBS user FAQs
- MCBS glossary
- 2024 early-release survey-file zip

What this proves:

- `MCBS` is public and directly downloadable.
- The 2024 zip preview shows the package is rich:
  - tutorials
  - codebooks
  - release notes
  - user guide
  - methodology report
  - questionnaire material
- This makes the `MA vs TM / senior plan choice` direction technically feasible with public data.

### MedPAC / CMS Policy Framing

Downloaded:

- CMS Health Equity Framework PDF
- MedPAC March 2026 chapter PDF

What this proves:

- The official policy-gap framing material is easy to preserve locally.
- This is useful for turning a data-feasibility scan into a later paper memo.

## Feasibility Assessment By Research Direction

### 1. Coverage Churn / Medicaid Unwinding

Feasibility: `High`

Why:

- `SIPP` is directly available and large enough for dynamic coverage analysis.
- `HPS` is easy to use for fast timing screens and state-period checks.
- `NHIS` is easy to use for access validation.
- `MEPS longitudinal` is directly available for richer spending and access follow-up.
- `Medicaid.gov` snapshot/specification materials are directly archived locally.

Main remaining technical task:

- script the `Data.Medicaid.gov` underlying export/API layer

### 2. Underinsurance / Medical Financial Hardship

Feasibility: `High`

Why:

- `MEPS longitudinal` is now locally staged
- `SIPP` is locally staged and supports insurance plus financial variables
- `NHIS` can validate access-related hardship outcomes
- `CFPB` policy framing and complaint API docs are locally archived

Main remaining technical task:

- decide whether CFPB complaints are actually part of the outcome design or only contextual policy framing

### 3. MCBS / MA vs TM / Senior Plan Choice

Feasibility: `Moderate to High`

Why:

- `MCBS` public-use data are directly downloadable
- documentation is extensive
- the raw early-release survey zip is now local

Main remaining technical task:

- unpack and inspect variable coverage around plan choice, access, affordability, and utilization before committing this as the core paper

## Process Notes

Two acquisition modes were used:

1. `PowerShell Invoke-WebRequest`
2. `curl.exe` for sources that were slower or more reliable outside the default PowerShell downloader

The first full scripted run timed out because a single long process mixed fast data hosts with slower CMS/Medicaid/CFPB pages. I then completed the remaining artifacts in smaller batches.

That matters for later ingestion design:

- large data bundles are not the problem
- mixed-host batch downloading is the problem
- future production ingestion should be source-grouped

## Recommended Next Step

If the immediate goal is still feasibility plus fast empirical movement, the next concrete step should be:

1. unpack and inspect `SIPP 2024`, `HPS 2025`, `NHIS 2024`, `MEPS HC-244/245`, and `MCBS 2024`
2. build a variable map for:
   - insurance status and transitions
   - continuity / churn measures
   - access barriers
   - OOP / spending / hardship outcomes
3. separately script the `Data.Medicaid.gov` extraction layer

## Re-Run

To re-run the scripted portion:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\acquisition\fetch_public_data_feasibility.ps1 -Force
```

If you only want to inspect what was staged, start with:

- `reference/external/feasibility_audit/download_manifest.csv`
- `reference/external/feasibility_audit/download_log.csv`
