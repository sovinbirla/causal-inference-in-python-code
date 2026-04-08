from math import erfc, sqrt
from statistics import NormalDist
from typing import Tuple

import pandas as pd


REQUIRED_COLUMNS = {"I", "T", "Y"}


def _validate_input(data: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    if data.empty:
        raise ValueError("Input data must not be empty.")


def _estimate_ate_and_se(data: pd.DataFrame) -> Tuple[float, float]:
    _validate_input(data)

    treated = data.loc[data["T"] == 1, "Y"]
    control = data.loc[data["T"] == 0, "Y"]

    if treated.empty or control.empty:
        raise ValueError("Both treatment and control groups must contain observations.")

    ate_estimate = treated.mean() - control.mean()

    treated_var = treated.var(ddof=1)
    control_var = control.var(ddof=1)
    standard_error = sqrt((treated_var / len(treated)) + (control_var / len(control)))

    return float(ate_estimate), float(standard_error)


def calculate_ate_ci(data: pd.DataFrame, alpha: float = 0.05) -> Tuple[float, float, float]:
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1.")

    ate_estimate, standard_error = _estimate_ate_and_se(data)
    z_critical = NormalDist().inv_cdf(1 - alpha / 2)
    margin_of_error = z_critical * standard_error

    ci_lower = ate_estimate - margin_of_error
    ci_upper = ate_estimate + margin_of_error

    return float(ate_estimate), float(ci_lower), float(ci_upper)


def calculate_ate_pvalue(data: pd.DataFrame) -> Tuple[float, float, float]:
    ate_estimate, standard_error = _estimate_ate_and_se(data)

    if standard_error == 0:
        if ate_estimate == 0:
            return float(ate_estimate), 0.0, 1.0
        raise ValueError("Standard error is zero, so the test statistic is undefined.")

    t_statistic = ate_estimate / standard_error
    p_value = erfc(abs(t_statistic) / sqrt(2))

    return float(ate_estimate), float(t_statistic), float(p_value)
