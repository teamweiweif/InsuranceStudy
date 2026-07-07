# Data Dictionary

## outcomes_988_state_month.parquet

| column | dtype |
| --- | --- |
| state | object |
| month | datetime64[ns] |
| year_month | object |
| routed_in_state | float64 |
| answered_in_state | float64 |
| in_state_answer_rate_reported | float64 |
| in_state_answer_rate | float64 |
| abandoned_in_state_count | float64 |
| abandoned_in_state_rate | float64 |
| flowout_to_national_backup_count | float64 |
| flowout_to_national_backup_rate | float64 |
| average_speed_to_answer_seconds | float64 |
| average_talk_time_seconds | float64 |
| source_pdf | object |
| page | int64 |
| raw_row_text | object |

## treatment_timing_state.parquet

| column | dtype |
| --- | --- |
| state | object |
| state_name | object |
| primary_policy_group | object |
| actual_collection_start | datetime64[ns] |
| operational_start | datetime64[ns] |
| first_revenue_year | Int64 |
| ever_core_fee_collection | bool |
| fcc_confirmed_collection_by_2024 | bool |
| post_2024_monitor_policy | bool |
| established_not_collected_by_2024 | bool |
| date_confidence | object |
| source_ids | object |
| policy_note | object |

## fee_schedule_state_month.parquet

| column | dtype |
| --- | --- |
| state | object |
| month | datetime64[ns] |
| fee_cents_max | float64 |
| fee_schedule_note | object |
| primary_policy_group | object |
| actual_collection_start | datetime64[ns] |
| operational_start | datetime64[ns] |
| ever_core_fee_collection | bool |
| post_2024_monitor_policy | bool |
| established_not_collected_by_2024 | bool |
| fee_collection_active | int64 |
| operational_treatment_active | int64 |
| months_since_collection_start | float64 |
| months_since_operational_start | float64 |
| post2025_policy_monitor_active | int64 |

## state_population_state_year.parquet

| column | dtype |
| --- | --- |
| state | object |
| state_name | object |
| year | int64 |
| population | float64 |
| population_source_year | int64 |
| population_carried_forward | bool |

## covariates_state_month.parquet

| column | dtype |
| --- | --- |
| state | object |
| month | datetime64[ns] |
| year | int32 |
| state_name | object |
| population | float64 |
| population_lookup_year | int32 |
| population_carried_forward | bool |
| has_population_denominator | bool |
| population_source_note | object |

## mechanism_state_year.parquet

| column | dtype |
| --- | --- |
| state | object |
| year | int32 |
| annual_routed_contacts | float64 |
| annual_answered_contacts | float64 |
| annual_mean_answer_rate | float64 |
| annual_mean_flowout_rate | float64 |
| annual_mean_asa_seconds | float64 |
| observed_months | int64 |
| fee_active_months | int64 |
| operational_active_months | int64 |
| mean_fee_cents_max | float64 |
| max_fee_cents | float64 |
| state_name | object |
| fee_revenue_nominal | float64 |
| source_id | object |
| revenue_note | object |
| population | float64 |
| latest_population | float64 |
| population_for_revenue | float64 |
| fee_revenue_observed | bool |
| fee_revenue_nominal_for_2021_2024 | float64 |
| fee_revenue_per_capita | float64 |
| fee_revenue_per_100k | float64 |
| fee_revenue_per_routed_contact | float64 |
| routed_per_100k_annual | float64 |
| mechanism_observation_note | object |

## analysis_panel_state_month.parquet

| column | dtype |
| --- | --- |
| state | object |
| month | datetime64[ns] |
| year_month | object |
| routed_in_state | float64 |
| answered_in_state | float64 |
| in_state_answer_rate_reported | float64 |
| in_state_answer_rate | float64 |
| abandoned_in_state_count | float64 |
| abandoned_in_state_rate | float64 |
| flowout_to_national_backup_count | float64 |
| flowout_to_national_backup_rate | float64 |
| average_speed_to_answer_seconds | float64 |
| average_talk_time_seconds | float64 |
| source_pdf | object |
| page | int64 |
| raw_row_text | object |
| fee_cents_max | float64 |
| fee_schedule_note | object |
| primary_policy_group | object |
| actual_collection_start | datetime64[ns] |
| operational_start | datetime64[ns] |
| ever_core_fee_collection | bool |
| post_2024_monitor_policy | bool |
| established_not_collected_by_2024 | bool |
| fee_collection_active | int64 |
| operational_treatment_active | int64 |
| months_since_collection_start | float64 |
| months_since_operational_start | float64 |
| post2025_policy_monitor_active | int64 |
| state_name | object |
| primary_policy_group_timing | object |
| first_revenue_year | Int64 |
| fcc_confirmed_collection_by_2024 | bool |
| date_confidence | object |
| source_ids | object |
| policy_note | object |
| year | int32 |
| population | float64 |
| population_lookup_year | int32 |
| population_carried_forward | bool |
| has_population_denominator | bool |
| population_source_note | object |
| fee_revenue_nominal | float64 |
| fee_revenue_nominal_for_2021_2024 | float64 |
| fee_revenue_per_capita | float64 |
| fee_revenue_per_100k | float64 |
| fee_revenue_per_routed_contact | float64 |
| fee_active_months | int64 |
| operational_active_months | int64 |
| mechanism_observation_note | object |
| month_id | object |
| calendar_month | int32 |
| post_988_launch | int64 |
| months_since_988_launch | int32 |
| is_state_dc | bool |
| is_territory_or_pr | bool |
| answer_rate_pp | float64 |
| flowout_rate_pp | float64 |
| abandoned_rate_pp | float64 |
| routed_per_100k | float64 |
| answered_per_100k | float64 |
| log_routed_in_state | float64 |
| log_routed_per_100k | float64 |
| asa_minutes | float64 |
| talk_minutes | float64 |
| treated_ever_by_2024 | bool |
| primary_analysis_sample | bool |
| observed_month_count | int64 |
| balanced_full_window_state | bool |
| baseline_prelaunch_answer_rate | float64 |
| baseline_prelaunch_flowout_rate | float64 |
| baseline_prelaunch_asa_seconds | float64 |
| baseline_prelaunch_routed_per_100k | float64 |
| baseline_prelaunch_months | float64 |
| low_baseline_answer_rate | bool |
| high_baseline_volume | bool |
| baseline_answer_rate_centered | float64 |
| baseline_volume_centered | float64 |
