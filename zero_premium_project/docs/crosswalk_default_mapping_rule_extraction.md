# Crosswalk Default Mapping Rule Extraction

## Confirmed From Drake

- Drake describes defaulting through the CCIIO Plan ID Crosswalk: if available, a plan defaults to itself; if not, a similar plan becomes the default.
- Drake defines treatment using the prior-year lowest and second-lowest silver plans and their current-year default plans.
- Drake defines across-insurer turnover when the default current-year plan is offered by a different insurer.
- Drake does not state how duplicate Crosswalk rows are resolved.
- Drake does not state how ZIP-level Crosswalk rows are collapsed to county-year treatment.
- Drake does not state that any ZIP-level default change is sufficient to treat a county-year.
- Drake does not state special handling for ReasonForCrosswalk = 8.
- Drake does not state whether CrosswalkLevel 4/5 rows are excluded or treated as nonconstructible.

## Confirmed From CMS Documentation

- CMS Plan ID Crosswalk PUF is an Exchange PUF data product available from the CMS Exchange PUF page.
- CMS Plan ID Crosswalk Data Dictionary defines `FIPSCode` as the county FIPS field and `ZipCode` as ZIP-level geography.
- CMS documentation says `ZipCode = 00000` means the issuer did not split the county into ZIP codes and the entire county is covered.
- CrosswalkLevel values identify default mapping level: 0 same Plan ID, 1 Plan ID level, 2 Plan ID plus county coverage level, 3 ZIP-code level, 4 no reenrollment option, and 5 withdrawn/no enrollment option.
- ReasonForCrosswalk values include 0, 1, 2, 3, 6, 7, 8, and 10; Reason 8 means crosswalk to a different issuer determined by CMS, not the existing issuer.

CMS sources used:
- https://www.cms.gov/marketplace/resources/data/public-use-files
- https://www.cms.gov/files/document/plan-id-crosswalk-datadictionary-py26.pdf

## Repo Assumptions

- The current repo rule selects one row per state/county/prior plan after filtering dental plans and prior silver plans.
- The current repo rule prioritizes mapped current plans, current silver metal, same issuer, lowest numeric CrosswalkLevel, then lexical current plan/issuer IDs.
- County-year treatment is true if either prior top-two silver plan has selected zero-to-positive turnover.

## Diagnostic-Only Sensitivities

- Removing same-issuer priority.
- Using raw source order.
- Selecting the lowest CrosswalkLevel.
- Preferring county-wide `00000` rows.
- Treating any ZIP-level candidate as enough to classify county-year turnover.
- Prioritizing ReasonForCrosswalk = 8.
