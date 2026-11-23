"""Use known effects to verify weighting, confounder adjustment, and imports."""

import numpy as np
import pandas as pd
import pytest

from causal_toolkit_sovinbirla import doubly_robust, ipw


@pytest.mark.parametrize("estimator", [ipw, doubly_robust])
def test_balanced_trial_recovers_exact_effect(estimator):
    data = pd.DataFrame({
        "T": [0, 0, 0, 1, 1, 1],
        "Y": [0, 1, 2, 2, 3, 4],
    })
    assert estimator(data, "1", "T", "Y") == pytest.approx(2)


@pytest.mark.parametrize("estimator", [ipw, doubly_robust])
def test_adjustment_recovers_effect_under_confounding(estimator):
    rng = np.random.default_rng(2026)
    x = rng.normal(size=10000)
    t = rng.binomial(1, 1 / (1 + np.exp(-x)))
    data = pd.DataFrame({"x": x, "treatment": t, "outcome": 2 * t + 3 * x})
    unadjusted = data.groupby("treatment")["outcome"].mean().diff().iloc[-1]
    assert abs(unadjusted - 2) > 1
    assert estimator(data, "1 + x", "treatment", "outcome") == pytest.approx(2, abs=0.2)
