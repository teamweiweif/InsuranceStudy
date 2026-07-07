# Data Dictionary

Created by `script/03_construct_exposures_outcomes.py`.

## Identifiers

- `facility_id`: six-character CMS Certification Number / Federal Provider Number.
- `state`: provider state from PBJ daily staffing files.
- `month`, `quarter`: facility-time periods constructed from PBJ `WorkDate`.

## Staffing Outcomes

- `weekend_total_nurse_hprd`: weekend total nurse hours per resident day, calculated as weekend RN + LPN + nurse aide hours divided by weekend resident-days.
- `weekend_rn_hprd`: weekend RN hours per resident day, calculated from RN, RN admin, and RN director-of-nursing hours divided by weekend resident-days.
- `weekday_total_nurse_hprd`: weekday total nurse hours per resident day.
- `weekday_rn_hprd`: weekday RN hours per resident day.
- `weekend_minus_weekday_total_hprd`: weekend total nurse HPRD minus weekday total nurse HPRD.
- `weekday_minus_weekend_total_hprd`: weekday total nurse HPRD minus weekend total nurse HPRD. Larger values mean a larger weekday-weekend gap.
- `total_nurse_hprd`: total nurse hours per resident day across all days.
- `rn_share_total_hours`: RN hours divided by total nurse hours.
- `contract_share_total_hours`: contract nurse hours divided by total nurse hours, using PBJ employee/contract hour splits.

## Baseline Exposures

All main exposure variables use only pre-treatment PBJ data from January 2019 through December 2021.

- `baseline_weekend_total_hprd`: facility mean weekend total nurse HPRD in 2019-2021.
- `baseline_weekend_rn_hprd`: facility mean weekend RN HPRD in 2019-2021.
- `baseline_gap_total`: facility mean weekday-minus-weekend total nurse HPRD in 2019-2021.
- `low_baseline_weekend_total_hprd`: indicator for bottom quartile of baseline weekend total nurse HPRD.
- `low_baseline_weekend_rn_hprd`: indicator for bottom quartile of baseline weekend RN HPRD.
- `high_baseline_weekday_weekend_gap`: indicator for top quartile of baseline weekday-minus-weekend total nurse staffing gap.
- `exposure_composite`: average of standardized low weekend total staffing, low weekend RN staffing, and high weekday-weekend gap. Higher values mean greater pre-policy exposure to the weekend-staffing reporting shock.
- `high_exposure_composite`: top quartile of `exposure_composite`; the preferred binary exposure.
- `high_exposure2021_composite`: robustness exposure using 2021 only.
- `high_exposure_no2020_composite`: robustness exposure using 2019 and 2021, excluding 2020.

## Policy Timing

- `post_jan2022`: one from January 2022 onward.
- `jan_to_jun2022`: one from January through June 2022.
- `post_jul2022`: one from July 2022 onward.
- `rel_month_jan2022`: event time in months, where January 2022 equals 0.
- `rel_month_jul2022`: event time in months, where July 2022 equals 0.

## Provider Data Catalog Variables

Provider snapshot variables include ownership type, certified beds, average residents, star ratings, reported CMS staffing and turnover fields, penalties, and survey/deficiency measures extracted from archived nursing-home Provider Data Catalog ZIPs.
