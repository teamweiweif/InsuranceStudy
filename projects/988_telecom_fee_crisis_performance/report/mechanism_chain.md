# Mechanism Chain

The observable mechanism is fee funding intensity. Public state-month staffing/capacity data were not available from a consistent official source, so capacity is not directly estimated.

| state | actual_collection_start | operational_start | observed_fee_revenue_total_2021_2024 | max_observed_fee_revenue_per_capita | delta_answer_rate | delta_flowout_rate | delta_asa_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CA | 2023-01-01 | 2023-04-01 | 88552000.000 | 1.130 | -0.001 | 0.028 | -9.152 |
| CO | 2022-01-01 | 2022-04-01 | 55152440.270 | 4.027 | 0.217 | -0.066 | -25.687 |
| DE | 2024-01-01 | 2024-04-01 | 9212568.860 | 8.773 | 0.109 | -0.089 | 6.415 |
| MD | 2024-10-01 | 2025-01-01 | 4812066.000 | 0.771 | 0.049 | -0.005 | -8.845 |
| MN | 2024-01-01 | 2024-04-01 | 3387491.000 | 0.584 | 0.122 | -0.054 | -13.124 |
| NV | 2023-06-01 | 2023-09-01 | 22849219.150 | 4.567 | 0.056 | 0.002 | -8.390 |
| OR | 2024-01-01 | 2024-04-01 | 24800000.000 | 5.814 | 0.045 | -0.013 | -5.567 |
| VA | 2021-07-01 | 2021-10-01 | 38017025.740 | 1.388 | 0.147 | -0.013 | -32.705 |
| VT | 2025-07-01 | 2025-10-01 | 0.000 | 0.000 | -0.001 | 0.005 | 4.584 |
| WA | 2021-10-01 | 2022-01-01 | 109545584.840 | 5.890 | 0.136 | -0.048 | -7.670 |

## Revenue-Intensity Model Rows

| outcome | term | estimate | std_error_cluster | p_value |
| --- | --- | --- | --- | --- |
| in_state_answer_rate | operational_treatment_active | -0.0261 | 0.0399 | 0.5159 |
| in_state_answer_rate | active_x_revenue_per_capita | 0.0054 | 0.0072 | 0.4573 |
| flowout_to_national_backup_rate | operational_treatment_active | 0.0451 | 0.0236 | 0.0614 |
| flowout_to_national_backup_rate | active_x_revenue_per_capita | -0.0064 | 0.0052 | 0.2268 |
| average_speed_to_answer_seconds | operational_treatment_active | -10.0422 | 3.8064 | 0.0111 |
| average_speed_to_answer_seconds | active_x_revenue_per_capita | 0.8536 | 0.5544 | 0.1299 |