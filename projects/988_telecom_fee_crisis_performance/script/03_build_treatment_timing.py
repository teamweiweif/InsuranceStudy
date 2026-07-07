from __future__ import annotations

import pandas as pd

from project_utils import ABBR_TO_STATE_NAME, DATA, append_audit, append_iteration, read_parquet, save_csv, save_parquet


POLICY_RECORDS = [
    {
        "state": "VA",
        "actual_collection_start": "2021-07-01",
        "operational_start": "2021-10-01",
        "first_revenue_year": 2021,
        "primary_policy_group": "fee_collected_2021_2024",
        "date_confidence": "high",
        "source_ids": "fcc_fee_report_2021;fcc_fee_report_2022;fcc_fee_report_2023;fcc_fee_report_2024",
        "policy_note": "Virginia collected a postpaid wireless fee and prepaid wireless charge during 2021-2024.",
    },
    {
        "state": "WA",
        "actual_collection_start": "2021-10-01",
        "operational_start": "2022-01-01",
        "first_revenue_year": 2021,
        "primary_policy_group": "fee_collected_2021_2024",
        "date_confidence": "high",
        "source_ids": "fcc_fee_report_2021;fcc_fee_report_2022;fcc_fee_report_2023;fcc_fee_report_2024;wa_dor_988_tax;wa_rcw_82_86",
        "policy_note": "Washington began imposing and collecting the statewide 988 tax on October 1, 2021.",
    },
    {
        "state": "CO",
        "actual_collection_start": "2022-01-01",
        "operational_start": "2022-04-01",
        "first_revenue_year": 2022,
        "primary_policy_group": "fee_collected_2021_2024",
        "date_confidence": "high",
        "source_ids": "fcc_fee_report_2021;fcc_fee_report_2022;fcc_fee_report_2023;fcc_fee_report_2024;co_session_law_988_surcharge",
        "policy_note": "Colorado collection began January 1, 2022; annual fee amount is set by the 988 enterprise.",
    },
    {
        "state": "CA",
        "actual_collection_start": "2023-01-01",
        "operational_start": "2023-04-01",
        "first_revenue_year": 2023,
        "primary_policy_group": "fee_collected_2021_2024",
        "date_confidence": "high",
        "source_ids": "fcc_fee_report_2022;fcc_fee_report_2023;fcc_fee_report_2024;ca_cdtfa_988_surcharge_rates",
        "policy_note": "California began imposing the 988 surcharge January 1, 2023.",
    },
    {
        "state": "NV",
        "actual_collection_start": "2023-06-01",
        "operational_start": "2023-09-01",
        "first_revenue_year": 2023,
        "primary_policy_group": "fee_collected_2021_2024",
        "date_confidence": "medium_high",
        "source_ids": "fcc_fee_report_2023;fcc_fee_report_2024;nv_988_temp_regulation",
        "policy_note": "Nevada fee was adopted through temporary regulation and FCC reports collection beginning in June 2023.",
    },
    {
        "state": "DE",
        "actual_collection_start": "2024-01-01",
        "operational_start": "2024-04-01",
        "first_revenue_year": 2024,
        "primary_policy_group": "fee_collected_2021_2024",
        "date_confidence": "high",
        "source_ids": "fcc_fee_report_2023;fcc_fee_report_2024;de_hb160",
        "policy_note": "Delaware began collecting a monthly and prepaid 988 fee January 1, 2024.",
    },
    {
        "state": "MN",
        "actual_collection_start": "2024-01-01",
        "operational_start": "2024-04-01",
        "first_revenue_year": 2024,
        "primary_policy_group": "fee_collected_2021_2024",
        "date_confidence": "medium_high",
        "source_ids": "fcc_fee_report_2023;fcc_fee_report_2024;mn_statute_145_561",
        "policy_note": "Minnesota authorized a monthly 988 fee beginning in 2024; FCC notes prepaid collection began September 1, 2024.",
    },
    {
        "state": "OR",
        "actual_collection_start": "2024-01-01",
        "operational_start": "2024-04-01",
        "first_revenue_year": 2024,
        "primary_policy_group": "fee_collected_2021_2024",
        "date_confidence": "high",
        "source_ids": "fcc_fee_report_2023;fcc_fee_report_2024;or_hb2757",
        "policy_note": "Oregon measure applies to subscriber bills and retail transactions on or after January 1, 2024.",
    },
    {
        "state": "MD",
        "actual_collection_start": "2024-10-01",
        "operational_start": "2025-01-01",
        "first_revenue_year": 2024,
        "primary_policy_group": "fee_collected_2021_2024",
        "date_confidence": "medium_high",
        "source_ids": "fcc_fee_report_2024;md_sb974;md_sb974_chapter_pdf",
        "policy_note": "Maryland Chapter 781 was approved May 16, 2024 and took effect October 1, 2024.",
    },
    {
        "state": "VT",
        "actual_collection_start": "2025-07-01",
        "operational_start": "2025-10-01",
        "first_revenue_year": 2025,
        "primary_policy_group": "fee_start_after_2024",
        "date_confidence": "medium_high",
        "source_ids": "fcc_fee_report_2024",
        "policy_note": "FCC fourth report states Vermont Act 145 funding did not take effect until July 1, 2025 and no 2024 funds were collected.",
    },
    {
        "state": "VI",
        "actual_collection_start": "",
        "operational_start": "",
        "first_revenue_year": "",
        "primary_policy_group": "established_not_collected_by_2024",
        "date_confidence": "medium",
        "source_ids": "fcc_fee_report_2024",
        "policy_note": "U.S. Virgin Islands reported authority to collect 988 fees but did not report collection during calendar year 2024.",
    },
    {
        "state": "IL",
        "actual_collection_start": "",
        "operational_start": "",
        "first_revenue_year": "",
        "primary_policy_group": "post_2024_monitor_policy",
        "date_confidence": "low",
        "source_ids": "fcc_fee_report_2024",
        "policy_note": "FCC fourth report notes Illinois enacted 2025 legislation establishing a Statewide 9-8-8 Trust Fund after the 2024 reporting period; not coded as fee collection treatment.",
    },
    {
        "state": "NM",
        "actual_collection_start": "",
        "operational_start": "",
        "first_revenue_year": "",
        "primary_policy_group": "post_2024_monitor_policy",
        "date_confidence": "medium",
        "source_ids": "fcc_fee_report_2024",
        "policy_note": "FCC fourth report notes New Mexico 2025 legislation transferring a percentage of a relay surcharge to a 988 lifeline fund effective July 1, 2025; not coded as core fee treatment.",
    },
]


FEE_SEGMENTS = [
    ("VA", "2021-07-01", "2026-05-01", 12.0, "Postpaid wireless 12 cents; prepaid wireless 8 cents."),
    ("WA", "2021-10-01", "2022-12-01", 24.0, "Statewide 988 tax before January 2023 increase."),
    ("WA", "2023-01-01", "2026-05-01", 40.0, "Statewide 988 tax after January 2023 increase."),
    ("CO", "2022-01-01", "2022-12-01", 18.0, "Colorado 2022 amount reported by FCC."),
    ("CO", "2023-01-01", "2023-12-01", 27.0, "Colorado 2023 amount reported by FCC."),
    ("CO", "2024-01-01", "2024-12-01", 14.0, "Colorado 2024 amount reported by FCC."),
    ("CO", "2025-01-01", "2026-05-01", 7.0, "FCC fourth report footnote states Colorado decreased to 7 cents effective January 1, 2025."),
    ("CA", "2023-01-01", "2025-12-01", 8.0, "California CDTFA 988 surcharge rate for 2023-2025."),
    ("CA", "2026-01-01", "2026-05-01", 5.0, "California CDTFA 988 surcharge rate for 2026."),
    ("NV", "2023-06-01", "2026-05-01", 35.0, "Nevada surcharge set at 35 cents."),
    ("DE", "2024-01-01", "2026-05-01", 60.0, "Delaware monthly and prepaid fee."),
    ("MN", "2024-01-01", "2026-05-01", 12.0, "Minnesota monthly fee; prepaid timing differs but maximum amount is 12 cents."),
    ("OR", "2024-01-01", "2026-05-01", 40.0, "Oregon wireless, prepaid, and VoIP fee; wireline no fee per FCC response."),
    ("MD", "2024-10-01", "2026-05-01", 25.0, "Maryland 25-cent fee after October 2024 effective date."),
    ("VT", "2025-07-01", "2026-05-01", pd.NA, "Vermont Act 145 funding starts July 2025; amount not coded from FCC report."),
]


REVENUE_RECORDS = [
    ("VA", 2021, 3593925.00, "fcc_fee_report_2021", "Includes $3,593,263 in fees or charges and $662 in interest."),
    ("WA", 2021, 4476684.51, "fcc_fee_report_2021", ""),
    ("CO", 2022, 16773446.65, "fcc_fee_report_2022", ""),
    ("VA", 2022, 10919378.18, "fcc_fee_report_2022", ""),
    ("WA", 2022, 30410200.60, "fcc_fee_report_2022", ""),
    ("CA", 2023, 44276000.00, "fcc_fee_report_2023", ""),
    ("CO", 2023, 23806942.70, "fcc_fee_report_2023", ""),
    ("NV", 2023, 7990541.35, "fcc_fee_report_2023", ""),
    ("VA", 2023, 11261800.19, "fcc_fee_report_2023", "FCC table footnote is attached to the amount; numeric value coded without footnote marker."),
    ("WA", 2023, 27962314.00, "fcc_fee_report_2023", ""),
    ("CA", 2024, 44276000.00, "fcc_fee_report_2024", ""),
    ("CO", 2024, 14572050.92, "fcc_fee_report_2024", ""),
    ("DE", 2024, 9212568.86, "fcc_fee_report_2024", ""),
    ("MD", 2024, 4812066.00, "fcc_fee_report_2024", ""),
    ("MN", 2024, 3387491.00, "fcc_fee_report_2024", ""),
    ("NV", 2024, 14858677.80, "fcc_fee_report_2024", ""),
    ("OR", 2024, 24800000.00, "fcc_fee_report_2024", ""),
    ("VA", 2024, 12241922.37, "fcc_fee_report_2024", ""),
    ("WA", 2024, 46696385.73, "fcc_fee_report_2024", ""),
    ("VT", 2024, 0.00, "fcc_fee_report_2024", "FCC reports no Vermont funds collected for 988 during calendar year 2024."),
]


def month_range(start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    return pd.date_range(start=start, end=end, freq="MS")


def build_policy_table(states: list[str]) -> pd.DataFrame:
    records = pd.DataFrame(POLICY_RECORDS)
    records["actual_collection_start"] = pd.to_datetime(records["actual_collection_start"], errors="coerce")
    records["operational_start"] = pd.to_datetime(records["operational_start"], errors="coerce")
    base = pd.DataFrame({"state": sorted(states)})
    out = base.merge(records, on="state", how="left")
    out["state_name"] = out["state"].map(ABBR_TO_STATE_NAME)
    out["primary_policy_group"] = out["primary_policy_group"].fillna("never_or_no_fee_reported")
    out["source_ids"] = out["source_ids"].fillna("fcc_fee_report_2024")
    out["policy_note"] = out["policy_note"].fillna("No FCC-reported state 988 telecom fee collection through the 2024 annual report.")
    out["date_confidence"] = out["date_confidence"].fillna("not_applicable")
    out["first_revenue_year"] = pd.to_numeric(out["first_revenue_year"], errors="coerce").astype("Int64")
    out["ever_core_fee_collection"] = out["actual_collection_start"].notna() & ~out["primary_policy_group"].eq("post_2024_monitor_policy")
    out["fcc_confirmed_collection_by_2024"] = out["primary_policy_group"].eq("fee_collected_2021_2024")
    out["post_2024_monitor_policy"] = out["primary_policy_group"].eq("post_2024_monitor_policy")
    out["established_not_collected_by_2024"] = out["primary_policy_group"].eq("established_not_collected_by_2024")
    return out[
        [
            "state",
            "state_name",
            "primary_policy_group",
            "actual_collection_start",
            "operational_start",
            "first_revenue_year",
            "ever_core_fee_collection",
            "fcc_confirmed_collection_by_2024",
            "post_2024_monitor_policy",
            "established_not_collected_by_2024",
            "date_confidence",
            "source_ids",
            "policy_note",
        ]
    ]


def build_fee_schedule(states: list[str], months: pd.DatetimeIndex, policy: pd.DataFrame) -> pd.DataFrame:
    grid = pd.MultiIndex.from_product([sorted(states), months], names=["state", "month"]).to_frame(index=False)
    grid["fee_cents_max"] = 0.0
    grid["fee_schedule_note"] = ""
    for state, start, end, cents, note in FEE_SEGMENTS:
        mask = grid["state"].eq(state) & grid["month"].between(pd.Timestamp(start), pd.Timestamp(end))
        grid.loc[mask, "fee_cents_max"] = cents
        grid.loc[mask, "fee_schedule_note"] = note
    grid = grid.merge(
        policy[
            [
                "state",
                "primary_policy_group",
                "actual_collection_start",
                "operational_start",
                "ever_core_fee_collection",
                "post_2024_monitor_policy",
                "established_not_collected_by_2024",
            ]
        ],
        on="state",
        how="left",
    )
    grid["fee_collection_active"] = (
        grid["actual_collection_start"].notna() & (grid["month"] >= grid["actual_collection_start"])
    ).astype(int)
    grid["operational_treatment_active"] = (
        grid["operational_start"].notna() & (grid["month"] >= grid["operational_start"])
    ).astype(int)
    grid["months_since_collection_start"] = pd.NA
    grid["months_since_operational_start"] = pd.NA
    for col, start_col in [
        ("months_since_collection_start", "actual_collection_start"),
        ("months_since_operational_start", "operational_start"),
    ]:
        valid = grid[start_col].notna()
        grid.loc[valid, col] = (
            (grid.loc[valid, "month"].dt.year - grid.loc[valid, start_col].dt.year) * 12
            + grid.loc[valid, "month"].dt.month
            - grid.loc[valid, start_col].dt.month
        )
    grid["post2025_policy_monitor_active"] = (
        grid["post_2024_monitor_policy"].fillna(False) & (grid["month"] >= pd.Timestamp("2025-07-01"))
    ).astype(int)
    grid["fee_cents_max"] = pd.to_numeric(grid["fee_cents_max"], errors="coerce")
    return grid


def build_revenue_table() -> pd.DataFrame:
    rows = []
    for state, year, revenue, source_id, note in REVENUE_RECORDS:
        rows.append(
            {
                "state": state,
                "state_name": ABBR_TO_STATE_NAME.get(state, state),
                "year": year,
                "fee_revenue_nominal": revenue,
                "source_id": source_id,
                "revenue_note": note,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    outcomes = read_parquet(DATA / "outcomes_988_state_month.parquet")
    states = sorted(outcomes["state"].dropna().unique())
    months = month_range(outcomes["month"].min(), outcomes["month"].max())

    policy = build_policy_table(states)
    fee_schedule = build_fee_schedule(states, months, policy)
    revenue = build_revenue_table()

    save_parquet(policy, DATA / "treatment_timing_state.parquet")
    save_csv(policy, DATA / "treatment_timing_state.csv")
    save_parquet(fee_schedule, DATA / "fee_schedule_state_month.parquet")
    save_csv(fee_schedule, DATA / "fee_schedule_state_month.csv")
    save_parquet(revenue, DATA / "fcc_annual_fee_revenue_state_year.parquet")
    save_csv(revenue, DATA / "fcc_annual_fee_revenue_state_year.csv")

    treated = int(policy["fcc_confirmed_collection_by_2024"].sum())
    append_audit(
        f"Built treatment timing files with {treated} FCC-confirmed fee-collecting states by 2024; "
        "actual collection and 3-month operational timing are stored separately."
    )
    append_iteration(
        "Treatment timing",
        "Primary treatment uses FCC-confirmed telecom fee collection dates. "
        "A separate operational-start variable lags collection by three months to allow funding to affect staffing and routing. "
        "Illinois/New Mexico 2025 policy mentions are flagged for sensitivity rather than coded as core treatment.",
    )


if __name__ == "__main__":
    main()
