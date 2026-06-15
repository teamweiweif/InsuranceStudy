# Remaining Gaps After Manual Dataset Migration

Generated: 2026-06-16

This file tracks gaps after moving `additional_dataset/` into `curated_dataset_library/`.

## Downloadable / saveable gaps

None currently known for the curated flagship set. The previously listed d023 and d024 ONS Metadata Catalogue assets were downloaded into `01_core_metadata/` on 2026-06-16.

## Current caveats

- d006 ASHE linked to Census 2021 - Northern Ireland: the public NISRA data dictionary is explicitly marked as a draft version pending final release; it is usable for variable-level scoping, but should be refreshed when NISRA publishes the final dictionary.
- d018 LEO England: public variable-level scoping is available via ONS LEO variable request forms. The ADR UK page says the full LEO user guide is available to accredited researchers inside the ONS Secure Research Service / LEO Research Community, so the public curated copy is not a full internal SRS user guide.

## Not publicly retrievable / needs enquiry or dead official link

- d021 MoJ-DfE linked dataset: current metadata must be requested from `DataLinkingTeam@justice.gov.uk` or `data.sharing@education.gov.uk`.
- d025 KEHC Phase 1: Health Data Gateway dataset-level metadata exists, but current structural metadata export is header-only with zero rows. KEHC protocol and supplementary appendix have been saved as supporting evidence, but no public variable-level data dictionary/user guide was found.
- d027 Adult Health, Social Care and Census - Scotland: no exact match in RDS metadata catalogue; existing local RDS/social-care crawl is related-source noise, not exact dataset metadata.
- d028 Housing, Health & Environment - Scotland: no exact match in RDS metadata catalogue; existing local RDS files are not exact dataset metadata.
