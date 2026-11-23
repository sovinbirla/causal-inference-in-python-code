"""ATE estimation and normal-approximation inference for randomized trials."""

from typing import Tuple

import numpy as np
import pandas as pd
from scipy import stats


def calculate_ate_ci(data: pd.DataFrame, alpha: float = 0.05) -> Tuple[float, float, float]:
    """
    Calculate the Average Treatment Effect (ATE) and its confidence interval.

    Parameters:
    data (pd.DataFrame): A DataFrame containing columns 'T' (treatment) and 'Y' (outcome).
    alpha (float): Significance level for the confidence interval.

    Returns:
    Tuple[float, float, float]: ATE, lower bound of the confidence interval, upper bound of the confidence interval.
    """
    treated = data[data['T'] == 1]['Y']
    control = data[data['T'] == 0]['Y']

    ate = treated.mean() - control.mean()

    # Calculate standard error
    se_treated = treated.std() / np.sqrt(len(treated))
    se_control = control.std() / np.sqrt(len(control))
    se_ate = np.sqrt(se_treated**2 + se_control**2)

    # Calculate confidence interval
    z_score = stats.norm.ppf(1 - alpha / 2)
    ci_lower = ate - z_score * se_ate
    ci_upper = ate + z_score * se_ate

    return ate, ci_lower, ci_upper


def calculate_ate_pvalue(data: pd.DataFrame) -> Tuple[float, float, float]:
    """
    Calculate the ATE and a two-sided normal-approximation p-value for H0: ATE = 0.

    Parameters:
    data (pd.DataFrame): A DataFrame containing columns 'T' (treatment) and 'Y' (outcome).

    Returns:
    Tuple[float, float, float]: ATE, t-statistic, p-value.
    """
    treated = data[data['T'] == 1]['Y']
    control = data[data['T'] == 0]['Y']

    ate = treated.mean() - control.mean()

    # Standard error of the difference between independent group means.
    se_ate = np.sqrt(
        treated.var(ddof=1) / treated.count()
        + control.var(ddof=1) / control.count()
    )
    t_stat = ate / se_ate

    # sf(x) = 1 - CDF(x), evaluated accurately even for small p-values.
    p_value = 2 * stats.norm.sf(abs(t_stat))

    return ate, t_stat, p_value
