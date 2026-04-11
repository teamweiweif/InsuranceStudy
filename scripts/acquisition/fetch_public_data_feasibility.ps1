param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Get-ProjectRoot {
    param([string]$Start = (Get-Location).Path)

    $current = [System.IO.Path]::GetFullPath($Start)
    while ($true) {
        if (Test-Path (Join-Path $current "src\utils\project_paths.R")) {
            return $current
        }

        $parent = Split-Path $current -Parent
        if ($parent -eq $current) {
            throw "Could not locate project root from $Start"
        }
        $current = $parent
    }
}

function New-PreviewForZip {
    param(
        [string]$ZipPath,
        [string]$PreviewPath
    )

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        $rows = $archive.Entries |
            Select-Object -First 60 `
                @{Name = "full_name"; Expression = { $_.FullName }}, `
                @{Name = "bytes"; Expression = { $_.Length }}
        $rows | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $PreviewPath
    } finally {
        $archive.Dispose()
    }
}

function Download-Artifact {
    param(
        [pscustomobject]$Item,
        [string]$ProjectRoot,
        [bool]$Overwrite
    )

    $dest = Join-Path $ProjectRoot $Item.relative_path
    $destDir = Split-Path $dest -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    }

    $result = [ordered]@{
        topic          = $Item.topic
        source         = $Item.source
        artifact_type  = $Item.artifact_type
        relative_path  = $Item.relative_path
        url            = $Item.url
        status         = ""
        bytes          = $null
        sha256         = ""
        zip_preview    = ""
        note           = $Item.note
        downloaded_at  = ""
    }

    if ((Test-Path $dest) -and (-not $Overwrite)) {
        $result.status = "exists"
    } else {
        try {
            Invoke-WebRequest -Uri $Item.url -OutFile $dest -UseBasicParsing
            $result.status = "downloaded"
        } catch {
            $result.status = "failed"
            $result.note = ($Item.note + " | ERROR: " + $_.Exception.Message).Trim(" |")
            return [pscustomobject]$result
        }
    }

    if (Test-Path $dest) {
        $file = Get-Item $dest
        $result.bytes = $file.Length
        $result.downloaded_at = [DateTime]::UtcNow.ToString("s") + "Z"

        try {
            $result.sha256 = (Get-FileHash -Algorithm SHA256 -Path $dest).Hash
        } catch {
            $result.sha256 = ""
        }

        if ([System.IO.Path]::GetExtension($dest).ToLowerInvariant() -eq ".zip") {
            $preview = "$dest.contents.csv"
            try {
                New-PreviewForZip -ZipPath $dest -PreviewPath $preview
                $result.zip_preview = [System.IO.Path]::GetRelativePath($ProjectRoot, $preview)
            } catch {
                $result.zip_preview = ""
                $result.note = ($result.note + " | ZIP preview failed").Trim(" |")
            }
        }
    }

    return [pscustomobject]$result
}

$projectRoot = Get-ProjectRoot
Set-Location $projectRoot

$items = @(
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "SIPP"
        artifact_type = "user_guide"
        relative_path = "reference/external/feasibility_audit/sipp/2024_sipp_users_guide.pdf"
        url = "https://www2.census.gov/programs-surveys/sipp/tech-documentation/methodology/2024_SIPP_Users_Guide.pdf"
        note = "Core methodology guide for the 2024 SIPP release."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "SIPP"
        artifact_type = "data_dictionary"
        relative_path = "reference/external/feasibility_audit/sipp/2024_sipp_data_dictionary.pdf"
        url = "https://www2.census.gov/programs-surveys/sipp/tech-documentation/data-dictionaries/2024/2024_SIPP_Data_Dictionary.pdf"
        note = "Variable dictionary for the 2024 public-use file."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "SIPP"
        artifact_type = "release_notes"
        relative_path = "reference/external/feasibility_audit/sipp/2024_sipp_release_notes.pdf"
        url = "https://www2.census.gov/programs-surveys/sipp/tech-documentation/2024/2024_SIPP_Release_Notes.pdf"
        note = "Release notes for the 2024 public-use file."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "SIPP"
        artifact_type = "schema"
        relative_path = "reference/external/feasibility_audit/sipp/2024_pu2024_schema.json"
        url = "https://www2.census.gov/programs-surveys/sipp/data/datasets/2024/pu2024_schema.json"
        note = "Machine-readable schema for the main 2024 SIPP PUF."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "SIPP"
        artifact_type = "user_note"
        relative_path = "reference/external/feasibility_audit/sipp/2022_monthly_hi_variables_error.html"
        url = "https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2022-usernotes/2022-monthly-hi-variables-error.html"
        note = "Important note about 2022 monthly health insurance variables."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "SIPP"
        artifact_type = "topic_brochure"
        relative_path = "reference/external/feasibility_audit/sipp/2025_sipp_health_coverage_disability_brochure.pdf"
        url = "https://www.census.gov/content/dam/Census/programs-surveys/sipp/about/2025_SIPP_Health_Coverage_Disability_Brochure.pdf"
        note = "High-level official brochure on SIPP health coverage content."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "SIPP"
        artifact_type = "data_zip"
        relative_path = "data/raw/feasibility_audit/sipp/2024/pu2024_csv.zip"
        url = "https://www2.census.gov/programs-surveys/sipp/data/datasets/2024/pu2024_csv.zip"
        note = "Main 2024 SIPP public-use CSV bundle."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "SIPP"
        artifact_type = "weights_zip"
        relative_path = "data/raw/feasibility_audit/sipp/2024/lgtwgt2024yr4_csv.zip"
        url = "https://www2.census.gov/programs-surveys/sipp/data/datasets/2024/lgtwgt2024yr4_csv.zip"
        note = "Longitudinal weights file for year 4."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "HPS"
        artifact_type = "landing_page"
        relative_path = "reference/external/feasibility_audit/hps/hps_datasets_2025.html"
        url = "https://www.census.gov/programs-surveys/household-pulse-survey/data/datasets.2025.html"
        note = "2025 Household Pulse datasets landing page."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "HPS"
        artifact_type = "technical_doc"
        relative_path = "reference/external/feasibility_audit/hps/htops_2502_source_and_accuracy.pdf"
        url = "https://www2.census.gov/programs-surveys/demo/technical-documentation/hhp/HTOPS_2502_Source_and_Accuracy.pdf"
        note = "Source and accuracy document for the February 2025 topical HPS release."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "HPS"
        artifact_type = "data_zip"
        relative_path = "data/raw/feasibility_audit/hps/2025/HTOPS_HPS_2504_CSV.zip"
        url = "https://www2.census.gov/programs-surveys/demo/datasets/hhp/2025/topical/HTOPS_HPS_2504_CSV.zip"
        note = "April 2025 topical HPS CSV public-use file."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "HPS"
        artifact_type = "data_zip"
        relative_path = "data/raw/feasibility_audit/hps/2024/HPS_DECEMBER2024_PUF_CSV.zip"
        url = "https://www2.census.gov/programs-surveys/demo/datasets/hhp/2024/topical/HPS_DECEMBER2024_PUF_CSV.zip"
        note = "December 2024 topical HPS CSV public-use file."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "NHIS"
        artifact_type = "survey_description"
        relative_path = "reference/external/feasibility_audit/nhis/2024_survey_description.pdf"
        url = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHIS/2024/srvydesc-508.pdf"
        note = "NHIS 2024 survey description and design."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "NHIS"
        artifact_type = "codebook"
        relative_path = "reference/external/feasibility_audit/nhis/2024_adult_codebook.pdf"
        url = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHIS/2024/adult-codebook.pdf"
        note = "NHIS 2024 sample adult codebook."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "NHIS"
        artifact_type = "summary"
        relative_path = "reference/external/feasibility_audit/nhis/2024_adult_summary.pdf"
        url = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHIS/2024/adult-summary.pdf"
        note = "NHIS 2024 sample adult summary."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "NHIS"
        artifact_type = "questionnaire"
        relative_path = "reference/external/feasibility_audit/nhis/2024_english_questionnaire.pdf"
        url = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Survey_Questionnaires/NHIS/2024/EnglishQuest.pdf"
        note = "NHIS 2024 English questionnaire."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "NHIS"
        artifact_type = "data_zip"
        relative_path = "data/raw/feasibility_audit/nhis/2024/adult24csv.zip"
        url = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHIS/2024/adult24csv.zip"
        note = "NHIS 2024 sample adult CSV zip."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "MEPS"
        artifact_type = "doc"
        relative_path = "reference/external/feasibility_audit/meps/h244_doc.pdf"
        url = "https://meps.ahrq.gov/data_stats/download_data/pufs/h244/h244doc.pdf"
        note = "MEPS HC-244 two-year longitudinal documentation."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "MEPS"
        artifact_type = "codebook"
        relative_path = "reference/external/feasibility_audit/meps/h244_codebook.pdf"
        url = "https://meps.ahrq.gov/data_stats/download_data/pufs/h244/h244cb.pdf"
        note = "MEPS HC-244 codebook."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "MEPS"
        artifact_type = "doc"
        relative_path = "reference/external/feasibility_audit/meps/h245_doc.pdf"
        url = "https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245doc.pdf"
        note = "MEPS HC-245 four-year longitudinal documentation."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "MEPS"
        artifact_type = "codebook"
        relative_path = "reference/external/feasibility_audit/meps/h245_codebook.pdf"
        url = "https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245cb.pdf"
        note = "MEPS HC-245 codebook."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "MEPS"
        artifact_type = "data_zip"
        relative_path = "data/raw/feasibility_audit/meps/h244dta.zip"
        url = "https://meps.ahrq.gov/data_files/pufs/h244/h244dta.zip"
        note = "MEPS HC-244 Stata bundle."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "MEPS"
        artifact_type = "data_zip"
        relative_path = "data/raw/feasibility_audit/meps/h245dta.zip"
        url = "https://meps.ahrq.gov/data_files/pufs/h245/h245dta.zip"
        note = "MEPS HC-245 Stata bundle."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "Medicaid"
        artifact_type = "policy_report"
        relative_path = "reference/external/feasibility_audit/medicaid_unwinding/january2025_snapshot.pdf"
        url = "https://www.medicaid.gov/resources-for-states/downloads/eligib-oper-and-enrol-snap-january2025.pdf"
        note = "Official January 2025 eligibility operations snapshot."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "Medicaid"
        artifact_type = "policy_report"
        relative_path = "reference/external/feasibility_audit/medicaid_unwinding/december2024_snapshot.pdf"
        url = "https://www.medicaid.gov/resources-for-states/downloads/eligib-oper-and-enrol-snap-december2024.pdf"
        note = "Official December 2024 eligibility operations snapshot."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "Medicaid"
        artifact_type = "specification"
        relative_path = "reference/external/feasibility_audit/medicaid_unwinding/eligibility_processing_data_report_specifications.pdf"
        url = "https://www.medicaid.gov/media/136536"
        note = "Eligibility processing report specifications referenced by Medicaid.gov."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "Medicaid"
        artifact_type = "landing_page"
        relative_path = "reference/external/feasibility_audit/medicaid_unwinding/eligibility_operations_snapshot.html"
        url = "https://www.medicaid.gov/medicaid-and-chip-eligibility-operations-and-enrollment-snapshot"
        note = "Snapshot landing page with current monthly PDFs and links to underlying data."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "Medicaid"
        artifact_type = "underlying_data_page"
        relative_path = "reference/external/feasibility_audit/medicaid_unwinding/data_medicaid_snapshot_page.html"
        url = "https://data.medicaid.gov/medicaid-chip-eligibility-enrollment-snapshot-data"
        note = "Underlying data landing page on Data.Medicaid.gov."
    },
    [pscustomobject]@{
        topic = "priority1_churn_unwinding"
        source = "ASPE"
        artifact_type = "policy_report"
        relative_path = "reference/external/feasibility_audit/aspe/coverage_access_2021_2024.pdf"
        url = "https://aspe.hhs.gov/sites/default/files/documents/9a943f1b8f8d3872fc3d82b02d0df466/coverage-access-2021-2024.pdf"
        note = "ASPE report on coverage and access trends through 2024."
    },
    [pscustomobject]@{
        topic = "priority2_underinsurance"
        source = "CMS"
        artifact_type = "framework"
        relative_path = "reference/external/feasibility_audit/cms/cms_framework_health_equity.pdf"
        url = "https://www.cms.gov/files/document/cms-framework-health-equity.pdf"
        note = "CMS Health Equity Framework used for official policy gap framing."
    },
    [pscustomobject]@{
        topic = "priority2_underinsurance"
        source = "CFPB"
        artifact_type = "policy_report"
        relative_path = "reference/external/feasibility_audit/cfpb/medical_debt_burden_2022.pdf"
        url = "https://www.consumerfinance.gov/documents/10436/cfpb_medical-debt-burden-in-the-united-states_report_2022-03.pdf"
        note = "CFPB flagship report on the medical debt burden in the United States."
    },
    [pscustomobject]@{
        topic = "priority2_underinsurance"
        source = "CFPB"
        artifact_type = "policy_report_page"
        relative_path = "reference/external/feasibility_audit/cfpb/older_americans_medical_billing_full_report.html"
        url = "https://www.consumerfinance.gov/data-research/research-reports/issue-spotlight-medical-billing-and-collections-among-older-americans/full-report/"
        note = "Issue spotlight page on medical billing and collections among older Americans."
    },
    [pscustomobject]@{
        topic = "priority2_underinsurance"
        source = "CFPB"
        artifact_type = "api_doc"
        relative_path = "reference/external/feasibility_audit/cfpb/consumer_complaints_api.html"
        url = "https://cfpb.github.io/api/ccdb/api.html"
        note = "CFPB consumer complaints API documentation; full CSV download is intentionally not fetched in this run because it is very large."
    },
    [pscustomobject]@{
        topic = "priority3_mcbs_ma_tm"
        source = "MCBS"
        artifact_type = "landing_page"
        relative_path = "reference/external/feasibility_audit/mcbs/mcbs_public_use_file_page.html"
        url = "https://www.cms.gov/priorities/health-equity/minority-health/research-data/current-beneficiary-survey-public-use-file"
        note = "CMS MCBS public-use file landing page."
    },
    [pscustomobject]@{
        topic = "priority3_mcbs_ma_tm"
        source = "MCBS"
        artifact_type = "faq"
        relative_path = "reference/external/feasibility_audit/mcbs/2021_mcbs_data_user_faqs.pdf"
        url = "https://data.cms.gov/sites/default/files/2023-10/2021MCBSDataUserFAQs.pdf"
        note = "MCBS data user FAQs for the public-use file."
    },
    [pscustomobject]@{
        topic = "priority3_mcbs_ma_tm"
        source = "MCBS"
        artifact_type = "glossary"
        relative_path = "reference/external/feasibility_audit/mcbs/mcbs_glossary.pdf"
        url = "https://www.cms.gov/files/document/mcbs-glossary.pdf"
        note = "MCBS glossary with variable and survey terminology."
    },
    [pscustomobject]@{
        topic = "priority3_mcbs_ma_tm"
        source = "MCBS"
        artifact_type = "data_zip"
        relative_path = "data/raw/feasibility_audit/mcbs/2024/2024_mcbs_survey_file_early_release.zip"
        url = "https://www.cms.gov/files/zip/2024-mcbs-survey-file-early-release.zip"
        note = "MCBS 2024 early release survey file."
    },
    [pscustomobject]@{
        topic = "priority3_mcbs_ma_tm"
        source = "MedPAC"
        artifact_type = "policy_report"
        relative_path = "reference/external/feasibility_audit/medpac/march_2026_ch12_medicare_payment_policy.pdf"
        url = "https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_Ch12_MedPAC_Report_To_Congress_SEC.pdf"
        note = "MedPAC chapter used for MA/TM policy-gap framing."
    }
)

$logDir = Join-Path $projectRoot "reference\external\feasibility_audit"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$manifestPath = Join-Path $logDir "download_manifest.csv"
$logPath = Join-Path $logDir "download_log.csv"

$items | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $manifestPath

$results = foreach ($item in $items) {
    Download-Artifact -Item $item -ProjectRoot $projectRoot -Overwrite:$Force.IsPresent
}

$results | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $logPath

$summary = $results | Group-Object status | Sort-Object Name | ForEach-Object {
    "{0}: {1}" -f $_.Name, $_.Count
}

Write-Host "Project root: $projectRoot"
Write-Host "Manifest: $manifestPath"
Write-Host "Log: $logPath"
Write-Host "Status summary:"
$summary | ForEach-Object { Write-Host "  $_" }
