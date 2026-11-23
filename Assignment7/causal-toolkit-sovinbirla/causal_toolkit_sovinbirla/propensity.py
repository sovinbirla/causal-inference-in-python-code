"""Average treatment effect estimation using IPW and doubly robust methods."""

import numpy as np
import pandas as pd
import patsy
from sklearn.linear_model import LinearRegression, LogisticRegression


def ipw(df: pd.DataFrame, ps_formula: str, T: str, Y: str) -> float:
    """Estimate the ATE using inverse propensity weighting."""
    X = patsy.dmatrix(ps_formula, df, NA_action="raise")
    treatment = df[T].to_numpy()
    outcome = df[Y].to_numpy()

    model = LogisticRegression(penalty=None, max_iter=1000)
    model.fit(X, treatment)
    ps = model.predict_proba(X)[:, 1]
    ps = np.clip(ps, 1e-10, 1 - 1e-10)

    ate = np.mean((treatment - ps) * outcome / (ps * (1 - ps)))
    return float(ate)


def doubly_robust(df: pd.DataFrame, formula: str, T: str, Y: str) -> float:
    """Estimate the ATE using augmented inverse propensity weighting."""
    X = patsy.dmatrix(formula, df, NA_action="raise")
    treatment = df[T].to_numpy()
    outcome = df[Y].to_numpy()

    ps_model = LogisticRegression(penalty=None, max_iter=1000)
    ps_model.fit(X, treatment)
    ps = ps_model.predict_proba(X)[:, 1]
    ps = np.clip(ps, 1e-10, 1 - 1e-10)

    control_model = LinearRegression().fit(
        X[treatment == 0], outcome[treatment == 0]
    )
    treated_model = LinearRegression().fit(
        X[treatment == 1], outcome[treatment == 1]
    )
    mu0 = control_model.predict(X)
    mu1 = treated_model.predict(X)

    treated_mean = np.mean(treatment * (outcome - mu1) / ps + mu1)
    control_mean = np.mean((1 - treatment) * (outcome - mu0) / (1 - ps) + mu0)
    return float(treated_mean - control_mean)
