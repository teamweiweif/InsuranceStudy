# Curated ADR UK Dataset Library

This is the simplified working library for the ADR UK PhD dataset documentation audit.

The old `adruk_phd_dataset_workspace/material/` folder is retained as crawler evidence and machine-processing history. Use this curated library for human review.

## Folder rules

Each dataset has the same structure:

- `01_core_metadata`: user guides, data dictionaries, variable lists, structural metadata, data specifications.
- `02_supporting_documents`: Data Explained, methodology, FAQ, webinar slides, synthetic-data material.
- `03_official_pages`: saved official pages, if added later.
- `99_duplicates_or_uncertain`: duplicates, out-of-scope nearby files, or material not counted as core metadata.

Shared documents are stored in `_shared/` and copied into relevant dataset folders when helpful for direct by-dataset reading.

## Index files

- `_index/dataset_index.csv`: one row per target dataset with curated file counts.
- `_index/file_manifest.csv`: one row per migrated source file, including source path, curated path, document type, hash, and migration action.
- `_index/remaining_gaps.md`: gaps that remain after this migration.
