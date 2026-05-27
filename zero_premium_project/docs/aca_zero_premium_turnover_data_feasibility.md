# ACA Zero-Premium Turnover Data Feasibility

## Executive Summary

Overall feasibility: **Conditional Go**.

The public files support a county-year feasibility workflow for the Drake et al.-style topic. County-level OEP PUFs for 2022-2024 expose the reenrollment and plan-switching outcome columns needed for aggregate county-year outcomes. QHP Landscape files for PY2022-PY2026 expose county-plan silver premiums, and the Exchange PUF Plan ID Crosswalk exposes prior-to-current plan mapping. The main limitation is not access to public data, but exactness: individual-level retention and household-specific subsidy calculations are not public, and PY2021 QHP Landscape direct files were not available from Data.HealthCare.gov by the tested URL pattern.

## Data Sources Found

| source_group | file_type | years | files_identified | downloads_successful | downloads_failed | source_page_url | direct_download_url_example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| exchange_puf | Plan Attributes Data Dictionary PDF | 2021, 2022, 2023, 2024, 2025, 2026 | 6 | 6 | 0 | https://www.cms.gov/marketplace/resources/data/public-use-files | https://www.cms.gov/files/document/planattributes-datadictionary-py21.pdf |
| exchange_puf | Plan Attributes PUF | 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 8 | 8 | 0 | https://www.cms.gov/marketplace/resources/data/public-use-files | https://download.cms.gov/marketplace-puf/2019/plan-attributes-puf.zip |
| exchange_puf | Plan ID Crosswalk Data Dictionary PDF | 2021, 2022, 2023, 2024, 2025, 2026 | 6 | 5 | 1 | https://www.cms.gov/marketplace/resources/data/public-use-files | https://www.cms.gov/files/document/plan-id-crosswalk-datadictionary-py22.pdf |
| exchange_puf | Plan ID Crosswalk PUF | 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 8 | 8 | 0 | https://www.cms.gov/marketplace/resources/data/public-use-files | https://download.cms.gov/marketplace-puf/2019/plan-id-crosswalk-puf.zip |
| exchange_puf | Rate Data Dictionary PDF | 2021, 2022, 2023, 2024, 2025, 2026 | 6 | 6 | 0 | https://www.cms.gov/marketplace/resources/data/public-use-files | https://www.cms.gov/files/document/rate-datadictionary-py21.pdf |
| exchange_puf | Rate PUF | 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 8 | 8 | 0 | https://www.cms.gov/marketplace/resources/data/public-use-files | https://download.cms.gov/marketplace-puf/2019/rate-puf.zip |
| exchange_puf | Service Area Data Dictionary PDF | 2021, 2022, 2023, 2024, 2025, 2026 | 6 | 6 | 0 | https://www.cms.gov/marketplace/resources/data/public-use-files | https://www.cms.gov/files/document/servicearea-datadictionary-py21.pdf |
| exchange_puf | Service Area PUF | 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 8 | 8 | 0 | https://www.cms.gov/marketplace/resources/data/public-use-files | https://download.cms.gov/marketplace-puf/2019/service-area-puf.zip |
| health_plan_finder | Health Plan Finder Interface Control Document PDF | metadata | 1 | 1 | 0 | https://www.cms.gov/marketplace/resources/data/healthcaregov-plan-finder-data | https://www.cms.gov/cciio/resources/data-resources/downloads/hios-rbis-icd-03-01-00.pdf |
| health_plan_finder | Health Plan Finder Metadata Report XLSX | metadata | 1 | 1 | 0 | https://www.cms.gov/marketplace/resources/data/healthcaregov-plan-finder-data | https://www.cms.gov/cciio/resources/data-resources/downloads/metadata-report-for-puf.xlsx |
| health_plan_finder | Health Plan Finder Q4 HIOS Data | 2019, 2020 | 2 | 2 | 0 | https://www.cms.gov/marketplace/resources/data/healthcaregov-plan-finder-data | https://www.cms.gov/files/document/2019q4-hios.xlsx |
| health_plan_finder | Health Plan Finder Q4 HIOS/RBIS Data | 2021 | 1 | 1 | 0 | https://www.cms.gov/marketplace/resources/data/healthcaregov-plan-finder-data | https://downloads.cms.gov/files/2021q4-hios-rbis.zip |
| health_plan_finder | Health Plan Finder Q4 RBIS Data | 2019, 2020 | 2 | 2 | 0 | https://www.cms.gov/marketplace/resources/data/healthcaregov-plan-finder-data | https://www.cms.gov/files/zip/2019q4.zip |
| oep_puf | County-Level OEP PUF | 2019 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-and-reports/marketplace-products/2019-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/research-statistics-data-and-systems/statistics-trends-and-reports/marketplace-products/downloads/2019oepcountylevelpublicusefile.zip |
| oep_puf | County-Level OEP PUF | 2020 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-and-reports/marketplace-products/2020-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2020-oep-county-level-public-use-file.zip |
| oep_puf | County-Level OEP PUF | 2021 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2021-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2021-oep-county-level-public-use-file.zip |
| oep_puf | County-Level OEP PUF | 2022 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2022-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2022-oep-county-level-public-use-file.zip |
| oep_puf | County-Level OEP PUF | 2023 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2023-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2023-oep-county-level-public-use-file.zip |
| oep_puf | County-Level OEP PUF | 2024 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2024-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2024-oep-county-level-public-use-file.zip |
| oep_puf | County-Level OEP PUF | 2025 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2025-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2025-oep-county-level-public-use-file.zip |
| oep_puf | County-Level OEP PUF | 2026 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2026-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2026-oep-county-level-public-use-file.zip |
| oep_puf | Public Use Files Definitions PDF | 2020 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-and-reports/marketplace-products/2020-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2020-public-use-files-definitions.pdf |
| oep_puf | Public Use Files Definitions PDF | 2021 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2021-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2021-public-use-files-definitions.pdf |
| oep_puf | Public Use Files Definitions PDF | 2022 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2022-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2022-public-use-files-definitions.pdf |
| oep_puf | Public Use Files Definitions PDF | 2023 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2023-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2023-public-use-files-definitions.pdf |
| oep_puf | Public Use Files Definitions PDF | 2024 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2024-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2024-public-use-files-definitions.pdf |
| oep_puf | Public Use Files Definitions PDF | 2025 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2025-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2025-public-use-files-definitions.pdf |
| oep_puf | Public Use Files Definitions PDF | 2026 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2026-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2026-public-use-files-definitions.pdf |
| oep_puf | Public Use Files FAQs PDF | 2020 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-and-reports/marketplace-products/2020-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2020-public-use-files-faqs.pdf |
| oep_puf | Public Use Files FAQs PDF | 2021 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2021-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2021-public-use-files-faqs.pdf |
| oep_puf | Public Use Files FAQs PDF | 2022 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2022-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2022-public-use-files-faqs.pdf |
| oep_puf | Public Use Files FAQs PDF | 2023 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2023-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2023-public-use-files-faqs.pdf |
| oep_puf | Public Use Files FAQs PDF | 2024 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2024-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2024-public-use-files-faqs.pdf |
| oep_puf | Public Use Files FAQs PDF | 2025 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2025-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2025-public-use-files-faqs.pdf |
| oep_puf | Public Use Files FAQs PDF | 2026 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2026-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/document/2026-public-use-files-faqs.pdf |
| oep_puf | State, Metal Level, and Enrollment Status OEP PUF | 2020 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-and-reports/marketplace-products/2020-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2020-oep-state-metal-level-and-enrollment-status-public-use-file.zip |
| oep_puf | State, Metal Level, and Enrollment Status OEP PUF | 2021 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2021-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2021-oep-state-metal-level-and-enrollment-status-public-use-file.zip |
| oep_puf | State, Metal Level, and Enrollment Status OEP PUF | 2022 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2022-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2022-oep-state-metal-level-and-enrollment-status-public-use-file.zip |
| oep_puf | State, Metal Level, and Enrollment Status OEP PUF | 2023 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2023-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2023-oep-state-metal-level-and-enrollment-status-public-use-file.zip |
| oep_puf | State, Metal Level, and Enrollment Status OEP PUF | 2024 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2024-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2024-oep-state-metal-level-and-enrollment-status-public-use-file.zip |
| oep_puf | State, Metal Level, and Enrollment Status OEP PUF | 2025 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2025-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2025-oep-state-metal-level-and-enrollment-status-public-use-file.zip |
| oep_puf | State, Metal Level, and Enrollment Status OEP PUF | 2026 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2026-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2026-oep-state-metal-level-enrollment-status-public-use-file.zip |
| oep_puf | State-Level OEP PUF | 2019 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-and-reports/marketplace-products/2019-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/research-statistics-data-and-systems/statistics-trends-and-reports/marketplace-products/downloads/2019oepstatelevelpublicusefile.zip |
| oep_puf | State-Level OEP PUF | 2020 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-and-reports/marketplace-products/2020-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2020-oep-state-level-public-use-file.zip |
| oep_puf | State-Level OEP PUF | 2021 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2021-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2021-oep-state-level-public-use-file.zip |
| oep_puf | State-Level OEP PUF | 2022 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2022-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2022-oep-state-level-public-use-file.zip |
| oep_puf | State-Level OEP PUF | 2023 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2023-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2023-oep-state-level-public-use-file.zip |
| oep_puf | State-Level OEP PUF | 2024 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2024-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2024-oep-state-level-public-use-file.zip |
| oep_puf | State-Level OEP PUF | 2025 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2025-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2025-oep-state-level-public-use-file.zip |
| oep_puf | State-Level OEP PUF | 2026 | 1 | 1 | 0 | https://www.cms.gov/data-research/statistics-trends-reports/marketplace-products/2026-marketplace-open-enrollment-period-public-use-files | https://www.cms.gov/files/zip/2026-oep-state-level-public-use-file.zip |
| qhp_landscape | QHP Landscape Individual Medical Instructions PDF | 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 8 | 5 | 3 | https://data.healthcare.gov/qhp-landscape-files | https://data.healthcare.gov/datafile/py2022/med-ind-lndscp-in.pdf |
| qhp_landscape | QHP Landscape Individual Medical ZIP | 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 8 | 5 | 3 | https://data.healthcare.gov/qhp-landscape-files | https://data.healthcare.gov/datafile/py2022/individual_market_medical.zip |

Full manifest: `data/metadata/data_manifest.csv`.

## File Inventory

| source_group | year | file_type | container_member | rows | columns | local_path |
| --- | --- | --- | --- | --- | --- | --- |
| exchange_puf | 2019 | Plan Attributes PUF | Plan_Attributes_PUF.csv | 15690 | 152 | data\raw\exchange_puf\2019\plan-attributes-puf.zip |
| exchange_puf | 2019 | Plan ID Crosswalk PUF | Plan_ID_Crosswalk_PUF.CSV | 93619 | 21 | data\raw\exchange_puf\2019\plan-id-crosswalk-puf.zip |
| exchange_puf | 2019 | Rate PUF | Rate_PUF.csv | 1968926 | 21 | data\raw\exchange_puf\2019\rate-puf.zip |
| exchange_puf | 2019 | Service Area PUF | Service_Area_PUF.csv | 10657 | 14 | data\raw\exchange_puf\2019\service-area-puf.zip |
| exchange_puf | 2020 | Plan Attributes PUF | Plan_Attributes_PUF.csv | 18574 | 152 | data\raw\exchange_puf\2020\plan-attributes-puf.zip |
| exchange_puf | 2020 | Plan ID Crosswalk PUF | Plan_ID_Crosswalk_PUF.CSV | 95936 | 21 | data\raw\exchange_puf\2020\plan-id-crosswalk-puf.zip |
| exchange_puf | 2020 | Rate PUF | Rate_PUF.csv | 1886351 | 21 | data\raw\exchange_puf\2020\rate-puf.zip |
| exchange_puf | 2020 | Service Area PUF | Service_Area_PUF.csv | 11308 | 14 | data\raw\exchange_puf\2020\service-area-puf.zip |
| exchange_puf | 2021 | Plan Attributes PUF | Plan_Attributes_PUF.csv | 20236 | 150 | data\raw\exchange_puf\2021\plan-attributes-puf.zip |
| exchange_puf | 2021 | Plan ID Crosswalk PUF | Plan_ID_Crosswalk_PUF.csv | 109776 | 21 | data\raw\exchange_puf\2021\plan-id-crosswalk-puf.zip |
| exchange_puf | 2021 | Rate PUF | Rate_PUF.csv | 2136450 | 20 | data\raw\exchange_puf\2021\rate-puf.zip |
| exchange_puf | 2021 | Service Area PUF | Service_Area_PUF.csv | 11321 | 14 | data\raw\exchange_puf\2021\service-area-puf.zip |
| exchange_puf | 2022 | Plan Attributes PUF | Plan_Attributes_PUF.csv | 27817 | 150 | data\raw\exchange_puf\2022\plan-attributes-puf.zip |
| exchange_puf | 2022 | Plan ID Crosswalk PUF | Plan_ID_Crosswalk_PUF.CSV | 125116 | 21 | data\raw\exchange_puf\2022\plan-id-crosswalk-puf.zip |
| exchange_puf | 2022 | Rate PUF | Rate_PUF.csv | 2498402 | 20 | data\raw\exchange_puf\2022\rate-puf.zip |
| exchange_puf | 2022 | Service Area PUF | Service_Area_PUF.csv | 12634 | 14 | data\raw\exchange_puf\2022\service-area-puf.zip |
| exchange_puf | 2023 | Plan Attributes PUF | Plan_Attributes_PUF.csv | 32528 | 151 | data\raw\exchange_puf\2023\plan-attributes-puf.zip |
| exchange_puf | 2023 | Plan ID Crosswalk PUF | Plan ID Crosswalk.CSV | 164831 | 21 | data\raw\exchange_puf\2023\plan-id-crosswalk-puf.zip |
| exchange_puf | 2023 | Rate PUF | Rate_PUF.csv | 2752441 | 20 | data\raw\exchange_puf\2023\rate-puf.zip |
| exchange_puf | 2023 | Service Area PUF | Service_Area_PUF.csv | 12942 | 14 | data\raw\exchange_puf\2023\service-area-puf.zip |
| exchange_puf | 2024 | Plan Attributes PUF | plan-attributes-puf.csv | 27374 | 151 | data\raw\exchange_puf\2024\plan-attributes-puf.zip |
| exchange_puf | 2024 | Plan ID Crosswalk PUF | Plan_ID_Crosswalk_PUF.csv | 189827 | 24 | data\raw\exchange_puf\2024\plan-id-crosswalk-puf.zip |
| exchange_puf | 2024 | Rate PUF | rate-puf.csv | 2608212 | 20 | data\raw\exchange_puf\2024\rate-puf.zip |
| exchange_puf | 2024 | Service Area PUF | service-area-puf.csv | 12753 | 14 | data\raw\exchange_puf\2024\service-area-puf.zip |
| exchange_puf | 2025 | Plan Attributes PUF | Plan_Attributes_PUF.csv | 24527 | 151 | data\raw\exchange_puf\2025\plan-attributes-puf.zip |
| exchange_puf | 2025 | Plan ID Crosswalk PUF | plan-id-crosswalk-puf.csv | 184909 | 24 | data\raw\exchange_puf\2025\plan-id-crosswalk-puf.zip |
| exchange_puf | 2025 | Rate PUF | Rate_PUF.csv | 2418441 | 20 | data\raw\exchange_puf\2025\rate-puf.zip |
| exchange_puf | 2025 | Service Area PUF | Service_Area_PUF.csv | 11761 | 14 | data\raw\exchange_puf\2025\service-area-puf.zip |
| exchange_puf | 2026 | Plan Attributes PUF | Plan_Attributes_PUF.csv | 22059 | 151 | data\raw\exchange_puf\2026\plan-attributes-puf.zip |
| exchange_puf | 2026 | Plan ID Crosswalk PUF | plan-id-crosswalk-puf.csv | 158746 | 24 | data\raw\exchange_puf\2026\plan-id-crosswalk-puf.zip |
| exchange_puf | 2026 | Rate PUF | Rate_PUF.csv | 2235761 | 20 | data\raw\exchange_puf\2026\rate-puf.zip |
| exchange_puf | 2026 | Service Area PUF | Service_Area_PUF.csv | 8820 | 14 | data\raw\exchange_puf\2026\service-area-puf.zip |
| health_plan_finder | 2019 | Health Plan Finder Q4 HIOS Data |  | 7823 | 19 | data\raw\health_plan_finder\2019\2019q4-hios.xlsx |
| health_plan_finder | 2019 | Health Plan Finder Q4 HIOS Data |  | 44719 | 12 | data\raw\health_plan_finder\2019\2019q4-hios.xlsx |
| health_plan_finder | 2019 | Health Plan Finder Q4 RBIS Data | 2019Q4-HIOS.xlsx | 7823 | 19 | data\raw\health_plan_finder\2019\2019q4.zip |
| health_plan_finder | 2019 | Health Plan Finder Q4 RBIS Data | 2019Q4-HIOS.xlsx | 44719 | 12 | data\raw\health_plan_finder\2019\2019q4.zip |
| health_plan_finder | 2020 | Health Plan Finder Q4 HIOS Data |  | 7909 | 19 | data\raw\health_plan_finder\2020\2020q4-hios.xlsx |
| health_plan_finder | 2020 | Health Plan Finder Q4 HIOS Data |  | 45258 | 12 | data\raw\health_plan_finder\2020\2020q4-hios.xlsx |
| health_plan_finder | 2020 | Health Plan Finder Q4 RBIS Data | RBIS.INSURANCE_PLAN_BASE_RATE_FILE3_20210211225931.zip |  |  | data\raw\health_plan_finder\2020\2020q4-rbis.zip |
| health_plan_finder | 2020 | Health Plan Finder Q4 RBIS Data | RBIS.INSURANCE_PLAN_BASE_RATE_FILE1_20210211225931.zip |  |  | data\raw\health_plan_finder\2020\2020q4-rbis.zip |

Full file inventory: `data/metadata/file_inventory.csv`. Full column inventory: `data/metadata/column_inventory.csv`.

Selected detected key columns:

| source_group | year | file_type | column_name | candidate_roles |
| --- | --- | --- | --- | --- |
| oep_puf | 2019 | State-Level OEP PUF | Individuals Determined Eligible to Enroll, with Financial Assistance | aptc |
| oep_puf | 2019 | State-Level OEP PUF | Total Number of Consumers Who Have Selected an Exchange Plan | total_plan_selections |
| oep_puf | 2019 | State-Level OEP PUF | New Consumers | total_plan_selections\|new_consumers |
| oep_puf | 2019 | State-Level OEP PUF | Total Re-enrollees | total_reenrollment |
| oep_puf | 2019 | State-Level OEP PUF | Active Re-enrollees | total_reenrollment\|active_reenrollment |
| oep_puf | 2019 | State-Level OEP PUF | Automatic Re-enrollees | total_reenrollment\|automatic_reenrollment |
| oep_puf | 2019 | State-Level OEP PUF | Active Re-enrollees who Switched Plans | total_reenrollment\|active_reenrollment\|active_reenrollment_switch |
| oep_puf | 2019 | State-Level OEP PUF | Active Re-enrollees who Remained in the Same Plan or a Crosswalked Plan | total_reenrollment\|active_reenrollment\|active_reenrollment_stay |
| oep_puf | 2019 | State-Level OEP PUF | Average Premium   | premium |
| oep_puf | 2019 | State-Level OEP PUF | Average Premium after APTC   | premium\|aptc |
| oep_puf | 2019 | State-Level OEP PUF | Consumers with APTC and/or CSRs | total_plan_selections\|aptc |
| oep_puf | 2019 | State-Level OEP PUF | Consumers with CSRs | total_plan_selections |
| oep_puf | 2019 | State-Level OEP PUF | Consumers with 73% Actuarial Value | total_plan_selections |
| oep_puf | 2019 | State-Level OEP PUF | Consumers with 87% Actuarial Value | total_plan_selections |
| oep_puf | 2019 | State-Level OEP PUF | Consumers with 94% Actuarial Value | total_plan_selections |
| oep_puf | 2019 | State-Level OEP PUF | Consumers with APTC | total_plan_selections\|aptc |
| oep_puf | 2019 | State-Level OEP PUF | Average APTC among consumers receiving APTC   | total_plan_selections\|aptc |
| oep_puf | 2019 | State-Level OEP PUF | Average Premium after APTC among consumers receiving APTC   | total_plan_selections\|premium\|aptc |
| oep_puf | 2019 | State-Level OEP PUF | Not Requesting Financial Assistance | aptc |
| oep_puf | 2019 | State-Level OEP PUF | ≥100% to ≤150% of FPL  | fpl |
| oep_puf | 2019 | State-Level OEP PUF | >150% to ≤200% of FPL  | fpl |
| oep_puf | 2019 | State-Level OEP PUF | >200% to ≤250% of FPL  | fpl |
| oep_puf | 2019 | State-Level OEP PUF | >250% to ≤300% of FPL  | fpl |
| oep_puf | 2019 | State-Level OEP PUF | >300%- ≤400% of FPL  | fpl |
| oep_puf | 2019 | State-Level OEP PUF | Other FPL | fpl |
| oep_puf | 2019 | State-Level OEP PUF | Metal Level | metal_level |
| oep_puf | 2019 | State-Level OEP PUF | Average APTC among Consumers receiving APTC   | total_plan_selections\|aptc |
| oep_puf | 2019 | State-Level OEP PUF | Average Premium after APTC among Consumers receiving APTC   | total_plan_selections\|premium\|aptc |
| oep_puf | 2019 | State-Level OEP PUF | Re-enrollees | total_reenrollment |
| oep_puf | 2019 | County-Level OEP PUF | Health Insurance Exchanges 2019 Open Enrollment Period: County-Level Public Use File | county |
| oep_puf | 2019 | County-Level OEP PUF | County-Level Public Use File: Contents | county |
| oep_puf | 2019 | County-Level OEP PUF | County FIPS Code | county_fips\|county |
| oep_puf | 2019 | County-Level OEP PUF | State | state |
| oep_puf | 2019 | County-Level OEP PUF | County Name | county |
| oep_puf | 2019 | County-Level OEP PUF | Total Number of Consumers Who Have Selected an Exchange Plan | total_plan_selections |
| oep_puf | 2019 | County-Level OEP PUF | New Consumers | total_plan_selections\|new_consumers |
| oep_puf | 2019 | County-Level OEP PUF | Total Re-enrollees | total_reenrollment |
| oep_puf | 2019 | County-Level OEP PUF | Active Re-enrollees | total_reenrollment\|active_reenrollment |
| oep_puf | 2019 | County-Level OEP PUF | Automatic Re-enrollees | total_reenrollment\|automatic_reenrollment |
| oep_puf | 2019 | County-Level OEP PUF | Active Re-enrollees who Switched Plans | total_reenrollment\|active_reenrollment\|active_reenrollment_switch |
| oep_puf | 2019 | County-Level OEP PUF | Active Re-enrollees who Remained in the Same Plan or a Crosswalked Plan | total_reenrollment\|active_reenrollment\|active_reenrollment_stay |
| oep_puf | 2019 | County-Level OEP PUF | Average Premium   | premium |
| oep_puf | 2019 | County-Level OEP PUF | Average Premium after APTC   | premium\|aptc |
| oep_puf | 2019 | County-Level OEP PUF | Consumers with APTC and/or CSRs | total_plan_selections\|aptc |
| oep_puf | 2019 | County-Level OEP PUF | Consumers with CSRs | total_plan_selections |
| oep_puf | 2019 | County-Level OEP PUF | Consumers with 73% Actuarial Value | total_plan_selections |
| oep_puf | 2019 | County-Level OEP PUF | Consumers with 87% Actuarial Value | total_plan_selections |
| oep_puf | 2019 | County-Level OEP PUF | Consumers with 94% Actuarial Value | total_plan_selections |
| oep_puf | 2019 | County-Level OEP PUF | Consumers with APTC | total_plan_selections\|aptc |
| oep_puf | 2019 | County-Level OEP PUF | Average APTC among consumers receiving APTC   | total_plan_selections\|aptc |
| oep_puf | 2019 | County-Level OEP PUF | Average Premium after APTC among consumers receiving APTC   | total_plan_selections\|premium\|aptc |
| oep_puf | 2019 | County-Level OEP PUF | Not Requesting Financial Assistance | aptc |
| oep_puf | 2019 | County-Level OEP PUF | ≥100% to ≤150% of FPL  | fpl |
| oep_puf | 2019 | County-Level OEP PUF | >150% to ≤200% of FPL  | fpl |
| oep_puf | 2019 | County-Level OEP PUF | >200% to ≤250% of FPL  | fpl |
| oep_puf | 2019 | County-Level OEP PUF | >250% to ≤300% of FPL  | fpl |
| oep_puf | 2019 | County-Level OEP PUF | >300%- ≤400% of FPL  | fpl |
| oep_puf | 2019 | County-Level OEP PUF | Other FPL | fpl |
| oep_puf | 2020 | State-Level OEP PUF | State_Abrvtn | state |
| oep_puf | 2020 | State-Level OEP PUF | Cnsmr | total_plan_selections |

## OEP Outcome Feasibility

| year | outcome | exact_column_name | geographic_level | number_usable_county_year_observations | missingness_rate | suppressed_small_cells_exist | matches_drake_categories |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | total reenrollment | Tot_Renrl | county | 2410 | 0.015924867292772562 | True | Yes |
| 2022 | automatic reenrollment | Auto_Renrl | county | 2388 | 0.02490812576561862 | True | Yes |
| 2022 | active reenrollment | Actv_Renrl | county | 2388 | 0.02490812576561862 | True | Yes |
| 2022 | active reenrollment staying with prior/default plan | Actv_Renrl_Nsw | county | 2358 | 0.03715802368313598 | True | Yes |
| 2022 | active reenrollment switching plans | Actv_Renrl_Sw | county | 2358 | 0.03715802368313598 | True | Yes |
| 2022 | total plan selections | Cnsmr | county | 2445 | 0.0016333197223356473 | True | Yes |
| 2022 | new consumers | New_Cnsmr | county | 2410 | 0.015924867292772562 | True | Yes |
| 2022 | returning consumers | Tot_Renrl | county | 2410 | 0.015924867292772562 | True | Yes |
| 2023 | total reenrollment | Tot_Renrl | county | 2413 | 0.014699877501020826 | True | Yes |
| 2023 | automatic reenrollment | Auto_Renrl | county | 2401 | 0.019599836668027767 | True | Yes |
| 2023 | active reenrollment | Actv_Renrl | county | 2401 | 0.019599836668027767 | True | Yes |
| 2023 | active reenrollment staying with prior/default plan | Actv_Renrl_Nsw | county | 2387 | 0.02531645569620253 | True | Yes |
| 2023 | active reenrollment switching plans | Actv_Renrl_Sw | county | 2387 | 0.02531645569620253 | True | Yes |
| 2023 | total plan selections | Cnsmr | county | 2447 | 0.0008166598611678236 | True | Yes |
| 2023 | new consumers | New_Cnsmr | county | 2413 | 0.014699877501020826 | True | Yes |
| 2023 | returning consumers | Tot_Renrl | county | 2413 | 0.014699877501020826 | True | Yes |
| 2024 | total reenrollment | Tot_Renrl | county | 2296 | 0.008635578583765112 | True | Yes |
| 2024 | automatic reenrollment | Auto_Renrl | county | 2290 | 0.011226252158894647 | True | Yes |
| 2024 | active reenrollment | Actv_Renrl | county | 2290 | 0.011226252158894647 | True | Yes |
| 2024 | active reenrollment staying with prior/default plan | Actv_Renrl_Nsw | county | 2277 | 0.01683937823834197 | True | Yes |
| 2024 | active reenrollment switching plans | Actv_Renrl_Sw | county | 2277 | 0.01683937823834197 | True | Yes |
| 2024 | total plan selections | Cnsmr | county | 2314 | 0.0008635578583765112 | True | Yes |
| 2024 | new consumers | New_Cnsmr | county | 2296 | 0.008635578583765112 | True | Yes |
| 2024 | returning consumers | Tot_Renrl | county | 2296 | 0.008635578583765112 | True | Yes |

County-level outcome construction is possible for the tested years when the exact columns above are present. Suppression and missingness should be handled as data quality flags rather than silently imputed.

## Treatment Construction Feasibility

Prototype output: `data/intermediate/prototype_turnover_2023_2024.csv`.

Join diagnostics:

| metric | numerator | denominator | rate | sample_states | notes |
| --- | --- | --- | --- | --- | --- |
| previous-year top-two silver county-plan rows | 1120 | 1120 | 1.0 | AL\|FL\|NC\|TX\|WI |  |
| previous-year plan to crosswalk | 1120 | 1120 | 1.0 | AL\|FL\|NC\|TX\|WI | Join on county FIPS plus previous-year plan ID. |
| crosswalk to current-year QHP Landscape | 1091 | 1120 | 0.9741071428571428 | AL\|FL\|NC\|TX\|WI | Join on county FIPS plus current-year plan ID. |
| previous-year plan to Rate PUF | 1120 | 1120 | 1.0 | AL\|FL\|NC\|TX\|WI | Join on state, plan ID, rating area, and age 40. |
| current-year plan to Rate PUF | 1091 | 1120 | 0.9741071428571428 | AL\|FL\|NC\|TX\|WI | Join on state, plan ID, rating area, and age 40. |
| current-year plan to service-area county | 1120 | 1120 | 1.0 | AL\|FL\|NC\|TX\|WI | Join Plan Attributes to Service Area PUF by issuer/service area, then to current plan county. |

The prototype tests the necessary keys: county FIPS, plan ID, issuer ID, metal level, rating area, age-40 premium, Plan ID Crosswalk mappings, Rate PUF age-40 rates, and Service Area county mapping. Across-issuer versus within-issuer turnover is distinguishable when issuer IDs are populated in the crosswalk/current-year landscape joins.

## Sample Alignment With Drake Et Al.

| check | value | notes |
| --- | --- | --- |
| OEP county rows 2022 | 2449 | State column: State_Abrvtn; FIPS column: County_FIPS_Cd |
| OEP county rows 2023 | 2449 | State column: State_Abrvtn; FIPS column: County_FIPS_Cd |
| OEP county rows 2024 | 2316 | State column: State_Abrvtn; FIPS column: County_FIPS_Cd |
| counties present in all downloaded 2022-2024 OEP county files | 2315 | Raw overlap before excluding Alaska, Hawaii, Nebraska, or non-HealthCare.gov states. |
| Alaska county FIPS present in OEP county files | True | Drake-style sample would exclude or specially handle this state as described. |
| Hawaii county FIPS present in OEP county files | True | Drake-style sample would exclude or specially handle this state as described. |
| Nebraska county FIPS present in OEP county files | True | Drake-style sample would exclude or specially handle this state as described. |
| mean missing/suppressed rate across tested OEP outcomes 2022 | 0.021692527562270317 | Outcome-specific details are in outputs/oep_outcome_feasibility.csv. |
| mean missing/suppressed rate across tested OEP outcomes 2023 | 0.016843609636586362 | Outcome-specific details are in outputs/oep_outcome_feasibility.csv. |
| mean missing/suppressed rate across tested OEP outcomes 2024 | 0.010362694300518135 | Outcome-specific details are in outputs/oep_outcome_feasibility.csv. |
| OEP reenrollment stratification | county-year aggregate | County-level OEP PUFs do not expose individual-level retention outcomes or income-stratified reenrollment outcomes. |

The raw public files make approximate county-year sample reconstruction possible. They do not make individual-level sample reconstruction possible.

## Problems And Unresolved Issues

- 7 manifest rows did not download. Most are expected missing QHP Landscape direct URLs for PY2019-PY2021 or older dictionary patterns; see the manifest.
- Returning consumers are represented by the same county-level `Tot_Renrl` column as total reenrollment in the tested OEP files.
- The public OEP files are aggregate PUFs, so they do not support individual-level HTE or demographic/income-stratified reenrollment outcomes at county level.
- The treatment prototype uses a low-income age-40 proxy; exact household-specific post-subsidy premiums require explicit subsidy parameterization and household composition.
- Nebraska county-market handling and Alaska/Hawaii exclusions were not force-applied in this Step 1 audit.

## Minimal Tests Completed

- HTTP/download checks with status, file size, and SHA-256 checksum in `data/metadata/data_manifest.csv`.
- ZIP member listing and tabular read tests in `data/metadata/file_inventory.csv`.
- Header checks and candidate variable role detection in `data/metadata/column_inventory.csv`.
- Missingness and suppression-like value counts in `outputs/missingness_summary.csv`.
- OEP outcome constructability checks in `outputs/oep_outcome_feasibility.csv`.
- 2023-to-2024 prototype join-key checks in `outputs/prototype_join_diagnostics.csv`.
- Row-count checks for CSV files read in chunks.

## Recommended Next Step

Proceed to a **full Drake-style replication dataset** before any causal modeling. The next build should formalize the HealthCare.gov state sample, apply Alaska/Hawaii exclusions, decide how to handle Nebraska, and compute the full national county-year zero-to-positive turnover measure. A richer continuous retention-shock measure is plausible after the binary turnover reconstruction is validated. County-level HTE or policy-learning designs should wait until the replication dataset is stable. Individual-level HTE is not supported by these public aggregate PUFs.

## Appendix

- Data manifest: `data/metadata/data_manifest.csv`
- File inventory: `data/metadata/file_inventory.csv`
- Column inventory: `data/metadata/column_inventory.csv`
- Missingness summary: `outputs/missingness_summary.csv`
- OEP outcome feasibility: `outputs/oep_outcome_feasibility.csv`
- Prototype join diagnostics: `outputs/prototype_join_diagnostics.csv`
- Prototype county output: `data/intermediate/prototype_turnover_2023_2024.csv`
- Code files: `scripts/01_download_marketplace_data.py`, `scripts/02_inspect_marketplace_files.py`
- Reproducibility notes: `docs/reproducibility_notes.md`
