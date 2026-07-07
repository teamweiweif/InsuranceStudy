# Churn / Unwinding Risk Prediction Pilot

## Purpose

This pilot was triggered because the second-round diagnostics gates all passed under the current rule set.

The model is intentionally conservative:

- train on `2021-2022` matched core months
- test on `2023` core months
- use retained person/household subgroup features only
- compare against a naive `state baseline risk` score

- gate verdict at launch: `GO_RISK_ONLY`

## Metrics

| outcome | model | auc | pr_auc | brier | top_decile_capture | rows_test | weight_sum_test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| medicaid_exit_next | baseline_state | 0.4245447899648783 | 0.006904030980255999 | 0.00756503644756585 | 0.0859 | 29060 | 276929544.37 |
| medicaid_exit_next | logistic | 0.6755631752769694 | 0.012677548628717766 | 0.007540658154552164 | 0.1884 | 29060 | 276929544.37 |
| medicaid_exit_next | tree | 0.6437867987145756 | 0.011441013823246523 | 0.007547882587537108 | 0.1629 | 29060 | 276929544.37 |
| medicaid_exit_to_uninsured_next | baseline_state | 0.45666331420784034 | 0.0031752688638742627 | 0.003384989200203883 | 0.0427 | 29060 | 276929544.37 |
| medicaid_exit_to_uninsured_next | logistic | 0.6482873170225224 | 0.005805923458241018 | 0.0033805314550065407 | 0.1077 | 29060 | 276929544.37 |
| medicaid_exit_to_uninsured_next | tree | 0.599401824592497 | 0.005139525608339782 | 0.0033811770512698932 | 0.0917 | 29060 | 276929544.37 |

## Calibration By Decile

| outcome | model | decile | rows | weight_sum | mean_pred | observed_rate |
| --- | --- | --- | --- | --- | --- | --- |
| medicaid_exit_next | baseline_state | 1 | 2906 | 26491149.53 | 0.0 | 0.0077 |
| medicaid_exit_next | baseline_state | 2 | 2906 | 27419570.62 | 0.0005 | 0.0098 |
| medicaid_exit_next | baseline_state | 3 | 2906 | 25328047.19 | 0.0014 | 0.02 |
| medicaid_exit_next | baseline_state | 4 | 2906 | 32608774.66 | 0.0019 | 0.0038 |
| medicaid_exit_next | baseline_state | 5 | 2906 | 34518812.22 | 0.0023 | 0.0098 |
| medicaid_exit_next | baseline_state | 6 | 2906 | 27823331.92 | 0.0031 | 0.0035 |
| medicaid_exit_next | baseline_state | 7 | 2906 | 20639167.89 | 0.0035 | 0.0089 |
| medicaid_exit_next | baseline_state | 8 | 2906 | 23748222.71 | 0.0035 | 0.0024 |
| medicaid_exit_next | baseline_state | 9 | 2906 | 31270537.49 | 0.0043 | 0.0056 |
| medicaid_exit_next | baseline_state | 10 | 2906 | 27081930.14 | 0.0082 | 0.0054 |
| medicaid_exit_next | logistic | 1 | 2906 | 26290385.22 | 0.001 | 0.0015 |
| medicaid_exit_next | logistic | 2 | 2906 | 25164035.77 | 0.0012 | 0.0014 |
| medicaid_exit_next | logistic | 3 | 2906 | 27088576.2 | 0.0016 | 0.0022 |
| medicaid_exit_next | logistic | 4 | 2906 | 27226238.24 | 0.0018 | 0.005 |
| medicaid_exit_next | logistic | 5 | 2906 | 25137208.56 | 0.002 | 0.0064 |
| medicaid_exit_next | logistic | 6 | 2906 | 27534394.84 | 0.0026 | 0.0072 |
| medicaid_exit_next | logistic | 7 | 2906 | 32408912.32 | 0.0034 | 0.0108 |
| medicaid_exit_next | logistic | 8 | 2906 | 27122764.38 | 0.0043 | 0.0083 |
| medicaid_exit_next | logistic | 9 | 2906 | 28185194.46 | 0.005 | 0.0175 |
| medicaid_exit_next | logistic | 10 | 2906 | 30771834.39 | 0.0068 | 0.0132 |
| medicaid_exit_next | tree | 1 | 2906 | 28501674.26 | 0.0016 | 0.0022 |
| medicaid_exit_next | tree | 2 | 2906 | 28845591.93 | 0.0017 | 0.001 |
| medicaid_exit_next | tree | 3 | 2906 | 22804290.23 | 0.0018 | 0.0019 |
| medicaid_exit_next | tree | 4 | 2906 | 25200148.23 | 0.002 | 0.009 |

## Major Group Calibration

| outcome | group_family | group_label | rows | weight_sum | observed_rate | baseline_pred | logistic_pred | tree_pred |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| medicaid_exit_next | age_band | age_0_17 | 10596 | 110181935.57 | 0.0074 | 0.0028 | 0.0025 | 0.0024 |
| medicaid_exit_next | age_band | age_18_25 | 3062 | 33732559.13 | 0.0143 | 0.0029 | 0.0044 | 0.0036 |
| medicaid_exit_next | age_band | age_26_44 | 5462 | 56222866.61 | 0.0072 | 0.0029 | 0.0041 | 0.0039 |
| medicaid_exit_next | age_band | age_45_64 | 5596 | 49311721.67 | 0.0054 | 0.003 | 0.0027 | 0.0028 |
| medicaid_exit_next | age_band | age_65_plus | 4344 | 27480461.38 | 0.0048 | 0.0028 | 0.0022 | 0.0022 |
| medicaid_exit_next | pov_band | missing | 94 | 844913.69 | 0.0 | 0.0019 | 0.0036 | 0.0023 |
| medicaid_exit_next | pov_band | pov_1_2 | 7849 | 74145743.26 | 0.0073 | 0.0028 | 0.002 | 0.0023 |
| medicaid_exit_next | pov_band | pov_2_4 | 7748 | 74709121.67 | 0.0127 | 0.0028 | 0.0052 | 0.0041 |
| medicaid_exit_next | pov_band | pov_4_plus | 3629 | 39423522.43 | 0.0105 | 0.003 | 0.0044 | 0.004 |
| medicaid_exit_next | pov_band | pov_lt_1 | 9740 | 87806243.32 | 0.0023 | 0.0028 | 0.0016 | 0.0019 |
| medicaid_exit_next | snap_group | missing | 27 | 0.0 | nan | nan | nan | nan |
| medicaid_exit_next | snap_group | snap_no | 19206 | 185409548.13 | 0.01 | 0.0028 | 0.0038 | 0.0033 |
| medicaid_exit_next | snap_group | snap_yes | 9827 | 91519996.24 | 0.0027 | 0.0028 | 0.0016 | 0.0021 |
| medicaid_exit_to_uninsured_next | age_band | age_0_17 | 10596 | 110181935.57 | 0.0037 | 0.001 | 0.001 | 0.0011 |
| medicaid_exit_to_uninsured_next | age_band | age_18_25 | 3062 | 33732559.13 | 0.0077 | 0.001 | 0.001 | 0.001 |
| medicaid_exit_to_uninsured_next | age_band | age_26_44 | 5462 | 56222866.61 | 0.0029 | 0.001 | 0.0015 | 0.0013 |
| medicaid_exit_to_uninsured_next | age_band | age_45_64 | 5596 | 49311721.67 | 0.002 | 0.001 | 0.0007 | 0.0009 |
| medicaid_exit_to_uninsured_next | age_band | age_65_plus | 4344 | 27480461.38 | 0.0003 | 0.001 | 0.0005 | 0.0003 |
| medicaid_exit_to_uninsured_next | pov_band | missing | 94 | 844913.69 | 0.0 | 0.0008 | 0.0015 | 0.0012 |
| medicaid_exit_to_uninsured_next | pov_band | pov_1_2 | 7849 | 74145743.26 | 0.0019 | 0.001 | 0.0008 | 0.0009 |
| medicaid_exit_to_uninsured_next | pov_band | pov_2_4 | 7748 | 74709121.67 | 0.0072 | 0.001 | 0.0014 | 0.0013 |
| medicaid_exit_to_uninsured_next | pov_band | pov_4_plus | 3629 | 39423522.43 | 0.0039 | 0.0012 | 0.0009 | 0.0008 |
| medicaid_exit_to_uninsured_next | pov_band | pov_lt_1 | 9740 | 87806243.32 | 0.0012 | 0.001 | 0.0009 | 0.0009 |
| medicaid_exit_to_uninsured_next | snap_group | missing | 27 | 0.0 | nan | nan | nan | nan |
