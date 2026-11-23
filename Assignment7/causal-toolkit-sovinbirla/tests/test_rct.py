"""Check trial estimates against analytic mean and variance calculations."""

import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

from causal_toolkit_sovinbirla import calculate_ate_ci, calculate_ate_pvalue


@pytest.fixture
def trial():
    return pd.DataFrame({"T": [0, 0, 0, 1, 1, 1], "Y": [0, 1, 2, 2, 3, 4]})


def test_ate_ci_matches_analytic_result(trial):
    ate, lower, upper = calculate_ate_ci(trial)
    margin = norm.ppf(0.975) * np.sqrt(2 / 3)
    assert (ate, lower, upper) == pytest.approx((2, 2 - margin, 2 + margin))


def test_significance_level_changes_interval_width(trial):
    _, low95, high95 = calculate_ate_ci(trial)
    _, low99, high99 = calculate_ate_ci(trial, alpha=0.01)
    assert low99 < low95 < high95 < high99


def test_pvalue_matches_two_sided_normal_test(trial):
    ate, statistic, pvalue = calculate_ate_pvalue(trial)
    expected_statistic = 2 / np.sqrt(2 / 3)
    assert ate == pytest.approx(2)
    assert statistic == pytest.approx(expected_statistic)
    assert pvalue == pytest.approx(2 * norm.sf(expected_statistic))


def test_identical_arms_have_zero_effect(trial):
    trial.loc[trial["T"].eq(1), "Y"] -= 2
    ate, statistic, pvalue = calculate_ate_pvalue(trial)
    assert (ate, statistic, pvalue) == pytest.approx((0, 0, 1))
