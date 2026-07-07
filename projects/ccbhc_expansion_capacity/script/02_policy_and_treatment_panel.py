from __future__ import annotations

import pandas as pd

from pipeline_utils import (
    CARES_ADDED_DEMO_STATES,
    COHORT_2024,
    COHORT_2026,
    DATA,
    DEMO_START_EVIDENCE,
    ORIGINAL_DEMO_STATES,
    PLANNING_2023,
    PLANNING_2025,
    RAW,
    REPORT,
    STATE_FIPS,
    STATE_NAMES,
    TEMP,
    append_note,
    save_parquet,
    write_text,
)


def build_state_policy() -> pd.DataFrame:
    rows = []
    for state, fips in STATE_FIPS.items():
        start = DEMO_START_EVIDENCE.get(state, ("", "", "unverified"))
        start_date, evidence, confidence = start
        for year in range(2019, 2027):
            selected_2024 = int(state in COHORT_2024)
            selected_2026 = int(state in COHORT_2026)
            planning23 = int(state in PLANNING_2023)
            planning25 = int(state in PLANNING_2025)
            start_year = int(start_date[:4]) if start_date else pd.NA
            post_verified = int(bool(selected_2024 and start_date and year >= int(start_date[:4])))
            rows.append({
                "state": state,
                "state_name": STATE_NAMES[state],
                "state_fips": fips,
                "year": year,
                "original_demo_state": int(state in ORIGINAL_DEMO_STATES),
                "cares_added_demo_state": int(state in CARES_ADDED_DEMO_STATES),
                "treated_state_2024": selected_2024,
                "selected_2026_cohort": selected_2026,
                "planning_grant_2023": planning23,
                "planning_grant_2025": planning25,
                "planning_grant_not_selected_2024": int(planning23 and not selected_2024),
                "not_yet_treated_2026": int(selected_2026 and year < 2026),
                "demo_selected_date_2024": "2024-06-04" if selected_2024 else "",
                "demo_selected_date_2026": "2026-05-28" if selected_2026 else "",
                "demo_start_window_start": "2024-07-01" if selected_2024 else ("2026-07-01" if selected_2026 else ""),
                "demo_start_window_end": "2025-07-01" if selected_2024 else ("2027-07-01" if selected_2026 else ""),
                "demo_start_date": start_date if selected_2024 else "",
                "demo_start_year": start_year if selected_2024 and start_date else pd.NA,
                "demo_start_confidence": confidence if selected_2024 else "",
                "demo_start_evidence": evidence if selected_2024 else "",
                "post_selection_2024": int(year >= 2024),
                "treated_post_selection_2024": int(selected_2024 and year >= 2024),
                "post_verified_demo_start": post_verified,
                "event_time_selection_2024": year - 2024 if selected_2024 else pd.NA,
                "eligible_all_non_original_control": int(state not in ORIGINAL_DEMO_STATES and state not in CARES_ADDED_DEMO_STATES and not selected_2024),
                "eligible_planning_control": int(planning23 and not selected_2024),
                "eligible_not_yet_control": int(selected_2026 and year < 2026),
                "source_flags": "federal_policy;state_start_evidence" if state in DEMO_START_EVIDENCE else "federal_policy",
                "missingness_flags": "" if (not selected_2024 or start_date) else "state_specific_start_date_unverified",
                "inclusion_flag_state_did": int(year >= 2021 and year <= 2024 and state not in ORIGINAL_DEMO_STATES and state not in CARES_ADDED_DEMO_STATES),
            })
    return pd.DataFrame(rows)


def build_county_policy(state_policy: pd.DataFrame) -> pd.DataFrame:
    acs_path = RAW / "acs_county_covariates_2019_2024.csv"
    if not acs_path.exists():
        return pd.DataFrame()
    acs = pd.read_csv(acs_path, dtype={"state_fips": str, "county_fips": str})
    cols = ["county_fips", "state_fips", "year", "NAME"]
    counties = acs[cols].drop_duplicates()
    out = counties.merge(state_policy, on=["state_fips", "year"], how="left")
    out["county_ccbhc_presence_public_verified"] = pd.NA
    out["county_ccbhc_sites_per_100k"] = pd.NA
    out["county_treatment_construction_status"] = "not_constructed_n_sumhss_puf_lacks_county_geography"
    return out


def main() -> None:
    state = build_state_policy()
    county = build_county_policy(state)
    save_parquet(state, DATA / "state_policy_panel.parquet")
    save_parquet(state, DATA / "ccbhc_treatment_panel.parquet")
    if not county.empty:
        save_parquet(county, DATA / "county_policy_panel.parquet")

    timeline = """# Policy Timeline

- 2017-04-01 and 2017-07-01: the original Section 223 Medicaid CCBHC demonstration started in eight states. These states are excluded from the preferred control pool.
- 2022-06-25: the Bipartisan Safer Communities Act authorized expansion and extension of the CCBHC demonstration.
- 2023-03: SAMHSA awarded the first BSCA CCBHC planning grants.
- 2024-02-15: CMS released updated CCBHC PPS guidance.
- 2024-06-04: HHS/CMS/SAMHSA selected Alabama, Illinois, Indiana, Iowa, Kansas, Maine, New Hampshire, New Mexico, Rhode Island, and Vermont for the first BSCA expansion cohort.
- 2024-07-01 to 2025-07-01: federal source says the 2024 cohort begins demonstrations within this window; state-specific start dates are only coded where public state evidence was found.
- 2025-01-07: SAMHSA awarded the next planning-grant round to 14 states and DC.
- 2026-05-28: HHS/CMS/SAMHSA selected Alaska, Colorado, Hawaii, Louisiana, Maryland, Mississippi, Montana, North Dakota, Washington, and West Virginia for the 2026 cohort.
- 2026-07-01 to 2027-07-01: federal source says the 2026 cohort begins demonstrations within this window.
"""
    write_text(REPORT / "policy_timeline.md", timeline)

    notes = """# Treatment Construction Notes

The treatment of interest is Medicaid Demonstration entry and the associated
state certification/payment infrastructure, not ordinary SAMHSA CCBHC expansion
grants. The file `data/ccbhc_treatment_panel.parquet` separates:

- selection into the 2024 BSCA cohort;
- federal start-date windows;
- state-specific start dates when public state evidence was found;
- planning-grant status;
- original and CARES-added demonstration states;
- future 2026 cohort states.

State-specific start dates remain unverified for Alabama and New Mexico in this
first build, and low-confidence for Kansas and New Hampshire. Main models
therefore use 2024 selection/post as an early policy shock, while the final
judgment treats actual payment timing as unresolved.

County CCBHC exposure is not constructed. The N-SUMHSS public-use file includes
state but no county, FIPS, address, latitude, or longitude fields. County-level
site timing would require a verified public clinic list with dates or restricted
facility geography.
"""
    write_text(REPORT / "treatment_construction_notes.md", notes)
    append_note("Phase 3: Treatment construction", [
        "Constructed state-year treatment panel with 2024 and 2026 cohorts, planning grants, original demonstration exclusions, and verified/missing start-date flags.",
        "Did not collapse selection, certification, operation, and PPS payment dates.",
        "Rejected county CCBHC exposure for now because county/site timing is not available in N-SUMHSS PUF and current locators are not historical.",
    ])


if __name__ == "__main__":
    main()
