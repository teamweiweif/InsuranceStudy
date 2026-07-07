param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$PSNativeCommandUseErrorActionPreference = $false

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

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
}

function Save-TextUrl {
    param(
        [string]$Url,
        [string]$Dest,
        [int]$MaxTimeSec = 300
    )

    Ensure-Dir (Split-Path $Dest -Parent)
    & curl.exe -sS -L --fail --retry 2 --connect-timeout 30 --max-time $MaxTimeSec -o "$Dest" "$Url" 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

function Download-File {
    param(
        [pscustomobject]$Item,
        [string]$ProjectRoot
    )

    $dest = Join-Path $ProjectRoot $Item.relative_path
    Ensure-Dir (Split-Path $dest -Parent)

    $result = [ordered]@{
        topic         = $Item.topic
        priority      = $Item.priority
        source        = $Item.source
        artifact_type = $Item.artifact_type
        relative_path = $Item.relative_path
        url           = $Item.url
        status        = ""
        bytes         = $null
        sha256        = ""
        zip_preview   = ""
        note          = $Item.note
        started_at    = [DateTime]::UtcNow.ToString("s") + "Z"
        finished_at   = ""
    }

    if ((Test-Path $dest) -and (-not $Force.IsPresent)) {
        $result.status = "exists"
    } else {
        $maxTime = if ($Item.PSObject.Properties.Name -contains "max_time_sec") { [int]$Item.max_time_sec } else { 1200 }
        $ok = $false

        try {
            & curl.exe -sS -L --fail --retry 2 --connect-timeout 30 --max-time $maxTime -o "$dest" "$($Item.url)" 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $ok = $true
            }
        } catch {
            $ok = $false
        }

        if ($ok) {
            $result.status = "downloaded"
        } else {
            if (Test-Path $dest) {
                Remove-Item -Force -LiteralPath $dest -ErrorAction SilentlyContinue
            }
            $result.status = "failed"
        }
    }

    if (Test-Path $dest) {
        $file = Get-Item $dest
        $result.bytes = $file.Length
        try {
            $result.sha256 = (Get-FileHash -Algorithm SHA256 -Path $dest).Hash
        } catch {
            $result.sha256 = ""
        }
        if ([System.IO.Path]::GetExtension($dest).ToLowerInvariant() -eq ".zip") {
            $preview = "$dest.contents.csv"
            if (-not (Test-Path $preview)) {
                try {
                    Add-Type -AssemblyName System.IO.Compression.FileSystem
                    $archive = [System.IO.Compression.ZipFile]::OpenRead($dest)
                    try {
                        $archive.Entries |
                            Select-Object -First 80 `
                                @{Name = "full_name"; Expression = { $_.FullName }},
                                @{Name = "bytes"; Expression = { $_.Length }} |
                            Export-Csv -NoTypeInformation -Encoding UTF8 -Path $preview
                    } finally {
                        $archive.Dispose()
                    }
                } catch {
                    $preview = ""
                }
            }
            if (Test-Path $preview) {
                $result.zip_preview = $preview.Replace($ProjectRoot + "\", "")
            }
        }
    }

    $result.finished_at = [DateTime]::UtcNow.ToString("s") + "Z"
    return [pscustomobject]$result
}

function Add-SippItems {
    param([System.Collections.Generic.List[object]]$List)

    for ($year = 2018; $year -le 2024; $year++) {
        $List.Add([pscustomobject]@{
            topic = "priority1_churn_unwinding"
            priority = 1
            source = "SIPP"
            artifact_type = "data_zip"
            relative_path = "data/raw/feasibility_audit/sipp/$year/pu${year}_csv.zip"
            url = "https://www2.census.gov/programs-surveys/sipp/data/datasets/$year/pu${year}_csv.zip"
            note = "Main SIPP CSV bundle for $year."
            max_time_sec = 3600
        })

        $List.Add([pscustomobject]@{
            topic = "priority1_churn_unwinding"
            priority = 1
            source = "SIPP"
            artifact_type = "schema"
            relative_path = "reference/external/feasibility_audit/sipp/${year}_schema.json"
            url = "https://www2.census.gov/programs-surveys/sipp/data/datasets/$year/pu${year}_schema.json"
            note = "Machine-readable schema for SIPP $year."
            max_time_sec = 300
        })
    }
}

function Add-HpsItems {
    param([System.Collections.Generic.List[object]]$List)

    for ($week = 52; $week -le 63; $week++) {
        $wkPadded = "{0:D2}" -f $week
        $List.Add([pscustomobject]@{
            topic = "priority1_churn_unwinding"
            priority = 1
            source = "HPS"
            artifact_type = "data_zip"
            relative_path = "data/raw/feasibility_audit/hps/2023/HPS_Week${week}_PUF_CSV.zip"
            url = "https://www2.census.gov/programs-surveys/demo/datasets/hhp/2023/wk$week/HPS_Week${week}_PUF_CSV.zip"
            note = "Household Pulse 2023 week $week public-use CSV zip."
            max_time_sec = 900
        })
    }

    $cycleInfo = @(
        @{ cycle = "01"; stem = "HPS_Phase4Cycle01_PUF_CSV.zip" },
        @{ cycle = "02"; stem = "HPS_Phase4Cycle02_PUF_CSV.zip" },
        @{ cycle = "03"; stem = "HPS_Phase4Cycle03_PUF_CSV.zip" },
        @{ cycle = "04"; stem = "HPS_Phase4-1Cycle04_PUF_CSV.zip" },
        @{ cycle = "05"; stem = "HPS_Phase4-1Cycle05_PUF_CSV.zip" },
        @{ cycle = "06"; stem = "HPS_Phase4-1Cycle06_PUF_CSV.zip" },
        @{ cycle = "07"; stem = "HPS_Phase4-1Cycle07_PUF_CSV.zip" },
        @{ cycle = "08"; stem = "HPS_Phase4-2Cycle08_PUF_CSV.zip" },
        @{ cycle = "09"; stem = "HPS_Phase4-2Cycle09_PUF_CSV.zip" }
    )

    foreach ($item in $cycleInfo) {
        $List.Add([pscustomobject]@{
            topic = "priority1_churn_unwinding"
            priority = 1
            source = "HPS"
            artifact_type = "data_zip"
            relative_path = "data/raw/feasibility_audit/hps/2024/$($item.stem)"
            url = "https://www2.census.gov/programs-surveys/demo/datasets/hhp/2024/cycle$($item.cycle)/$($item.stem)"
            note = "Household Pulse 2024 cycle $($item.cycle) CSV zip."
            max_time_sec = 900
        })
    }

    $topical2024 = @("HPS_OCTOBER2024_PUF_CSV.zip", "HPS_DECEMBER2024_PUF_CSV.zip")
    foreach ($stem in $topical2024) {
        $List.Add([pscustomobject]@{
            topic = "priority1_churn_unwinding"
            priority = 1
            source = "HPS"
            artifact_type = "data_zip"
            relative_path = "data/raw/feasibility_audit/hps/2024/$stem"
            url = "https://www2.census.gov/programs-surveys/demo/datasets/hhp/2024/topical/$stem"
            note = "Household Pulse topical 2024 CSV zip: $stem."
            max_time_sec = 900
        })
    }

    $topical2025 = @("HTOPS_HPS_2502%20CSV.zip", "HTOPS_HPS_2504_CSV.zip")
    foreach ($stem in $topical2025) {
        $relativeStem = $stem.Replace("%20", " ")
        $List.Add([pscustomobject]@{
            topic = "priority1_churn_unwinding"
            priority = 1
            source = "HPS"
            artifact_type = "data_zip"
            relative_path = "data/raw/feasibility_audit/hps/2025/$relativeStem"
            url = "https://www2.census.gov/programs-surveys/demo/datasets/hhp/2025/topical/$stem"
            note = "Household Pulse topical 2025 CSV zip: $relativeStem."
            max_time_sec = 900
        })
    }
}

function Add-NhisItems {
    param([System.Collections.Generic.List[object]]$List)

    for ($year = 2019; $year -le 2024; $year++) {
        $yy = $year.ToString().Substring(2)
        $List.Add([pscustomobject]@{
            topic = "priority1_churn_unwinding"
            priority = 1
            source = "NHIS"
            artifact_type = "data_zip"
            relative_path = "data/raw/feasibility_audit/nhis/$year/adult${yy}csv.zip"
            url = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHIS/$year/adult${yy}csv.zip"
            note = "NHIS sample adult CSV zip for $year."
            max_time_sec = 1200
        })

        $List.Add([pscustomobject]@{
            topic = "priority1_churn_unwinding"
            priority = 1
            source = "NHIS"
            artifact_type = "codebook"
            relative_path = "reference/external/feasibility_audit/nhis/${year}_adult_codebook.pdf"
            url = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHIS/$year/adult-codebook.pdf"
            note = "NHIS sample adult codebook for $year."
            max_time_sec = 300
        })
    }
}

function Add-MepsItems {
    param([System.Collections.Generic.List[object]]$List)

    foreach ($code in @("h244", "h245")) {
        $List.Add([pscustomobject]@{
            topic = "priority1_churn_unwinding"
            priority = 1
            source = "MEPS"
            artifact_type = "xlsx_zip"
            relative_path = "data/raw/feasibility_audit/meps/${code}xlsx.zip"
            url = "https://meps.ahrq.gov/data_files/pufs/$code/${code}xlsx.zip"
            note = "MEPS $code XLSX bundle."
            max_time_sec = 2400
        })
    }
}

function Add-MedicaidItems {
    param(
        [System.Collections.Generic.List[object]]$List,
        [string]$ProjectRoot
    )

    $pages = @(
        [pscustomobject]@{
            relative_path = "reference/external/feasibility_audit/medicaid_unwinding/eligibility_operations_snapshot_latest.html"
            url = "https://www.medicaid.gov/medicaid-and-chip-eligibility-operations-and-enrollment-snapshot"
        },
        [pscustomobject]@{
            relative_path = "reference/external/feasibility_audit/medicaid_unwinding/monthly_data_reports_historical.html"
            url = "https://www.medicaid.gov/resources-for-states/coronavirus-disease-2019-covid-19/unwinding-and-returning-regular-operations-after-covid-19/data-reporting/monthly-data-reports"
        }
    )

    foreach ($page in $pages) {
        $dest = Join-Path $ProjectRoot $page.relative_path
        if (-not (Test-Path $dest)) {
            $ok = Save-TextUrl -Url $page.url -Dest $dest -MaxTimeSec 300
        } else {
            $ok = $true
        }
        if (-not $ok) { continue }

        $html = Get-Content $dest -Raw -ErrorAction SilentlyContinue
        if (-not $html) { continue }

        $matches = [regex]::Matches($html, '/resources-for-states/downloads/[^"''<> ]+\.pdf')
        $seen = @{}
        foreach ($m in $matches) {
            $href = $m.Value
            if ($seen.ContainsKey($href)) { continue }
            $seen[$href] = $true
            $fileName = Split-Path $href -Leaf
            $List.Add([pscustomobject]@{
                topic = "priority1_churn_unwinding"
                priority = 1
                source = "Medicaid"
                artifact_type = "policy_report"
                relative_path = "reference/external/feasibility_audit/medicaid_unwinding/reports/$fileName"
                url = "https://www.medicaid.gov$href"
                note = "Medicaid unwinding or enrollment snapshot PDF parsed from official page."
                max_time_sec = 600
            })
        }
    }
}

function Add-CfpbItems {
    param([System.Collections.Generic.List[object]]$List)

    $List.Add([pscustomobject]@{
        topic = "priority2_underinsurance"
        priority = 2
        source = "CFPB"
        artifact_type = "bulk_data_zip"
        relative_path = "data/raw/feasibility_audit/cfpb/complaints.csv.zip"
        url = "https://files.consumerfinance.gov/ccdb/complaints.csv.zip"
        note = "Full CFPB consumer complaints bulk CSV archive."
        max_time_sec = 7200
    })
}

function Add-McbsItems {
    param([System.Collections.Generic.List[object]]$List)

    $List.Add([pscustomobject]@{
        topic = "priority3_mcbs_ma_tm"
        priority = 3
        source = "MCBS"
        artifact_type = "data_zip"
        relative_path = "data/raw/feasibility_audit/mcbs/2022/2022_mcbs_survey_file.zip"
        url = "https://www.cms.gov/files/zip/2022-mcbs-survey-file.zip"
        note = "MCBS 2022 survey file."
        max_time_sec = 2400
    })
}

$projectRoot = Get-ProjectRoot
Set-Location $projectRoot

$runStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $projectRoot "reference\external\feasibility_audit\batch_runs\$runStamp"
Ensure-Dir $logDir

$items = New-Object System.Collections.Generic.List[object]

Add-SippItems -List $items
Add-HpsItems -List $items
Add-NhisItems -List $items
Add-MepsItems -List $items
Add-MedicaidItems -List $items -ProjectRoot $projectRoot
Add-CfpbItems -List $items
Add-McbsItems -List $items

$manifestPath = Join-Path $logDir "batch_manifest.csv"
$items | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $manifestPath

$results = foreach ($item in $items) {
    Download-File -Item $item -ProjectRoot $projectRoot
}

$logPath = Join-Path $logDir "batch_download_log.csv"
$results | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $logPath

$summaryPath = Join-Path $logDir "batch_summary.txt"
$statusSummary = $results | Group-Object status | Sort-Object Name | ForEach-Object {
    "{0}: {1}" -f $_.Name, $_.Count
}
$statusSummary | Set-Content -Encoding UTF8 -Path $summaryPath

Write-Host "Batch acquisition complete."
Write-Host "Manifest: $manifestPath"
Write-Host "Log: $logPath"
Write-Host "Summary: $summaryPath"
$statusSummary | ForEach-Object { Write-Host "  $_" }
