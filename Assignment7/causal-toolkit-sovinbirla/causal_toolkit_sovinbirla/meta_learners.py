"""Estimate conditional average treatment effects with four meta-learners."""

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict


def s_learner_discrete(
    train: pd.DataFrame, test: pd.DataFrame, X: list[str], T: str, y: str
) -> pd.DataFrame:
    """Compare treated and control predictions from a single outcome model."""
    features = list(X) + [T]
    model = LGBMRegressor(verbosity=-1)
    model.fit(train[features], train[y])

    treated = test[features].copy()
    control = test[features].copy()
    treated[T] = 1
    control[T] = 0

    return test.assign(cate=model.predict(treated) - model.predict(control))


def t_learner_discrete(
    train: pd.DataFrame, test: pd.DataFrame, X: list[str], T: str, y: str
) -> pd.DataFrame:
    """Compare predictions from separate control and treated outcome models."""
    control = train.loc[train[T] == 0]
    treated = train.loc[train[T] == 1]

    mu0 = LGBMRegressor(verbosity=-1).fit(control[X], control[y])
    mu1 = LGBMRegressor(verbosity=-1).fit(treated[X], treated[y])

    return test.assign(cate=mu1.predict(test[X]) - mu0.predict(test[X]))


def x_learner_discrete(
    train: pd.DataFrame, test: pd.DataFrame, X: list[str], T: str, y: str
) -> pd.DataFrame:
    """Combine imputed effect models using the estimated propensity score."""
    control = train.loc[train[T] == 0]
    treated = train.loc[train[T] == 1]

    # First stage: learn the two potential outcome functions.
    mu0 = LGBMRegressor(verbosity=-1).fit(control[X], control[y])
    mu1 = LGBMRegressor(verbosity=-1).fit(treated[X], treated[y])

    # Second stage: impute individual effects and learn each group's CATE.
    effect0 = mu1.predict(control[X]) - control[y].to_numpy()
    effect1 = treated[y].to_numpy() - mu0.predict(treated[X])
    tau0 = LGBMRegressor(verbosity=-1).fit(control[X], effect0)
    tau1 = LGBMRegressor(verbosity=-1).fit(treated[X], effect1)

    propensity = LogisticRegression(penalty=None, max_iter=1000)
    propensity.fit(train[X], train[T])
    e = propensity.predict_proba(test[X])[:, 1]
    cate = e * tau0.predict(test[X]) + (1 - e) * tau1.predict(test[X])

    return test.assign(cate=cate)


def double_ml_cate(
    train: pd.DataFrame, test: pd.DataFrame, X: list[str], T: str, y: str
) -> pd.DataFrame:
    """Learn continuous treatment effects from cross-fitted residuals."""
    # Out-of-fold predictions keep each row out of its nuisance model's fit.
    treatment_hat = cross_val_predict(
        LGBMRegressor(verbosity=-1), train[X], train[T], cv=5
    )
    outcome_hat = cross_val_predict(
        LGBMRegressor(verbosity=-1), train[X], train[y], cv=5
    )
    treatment_res = train[T].to_numpy() - treatment_hat
    outcome_res = train[y].to_numpy() - outcome_hat

    weights = treatment_res**2
    if not np.any(weights > 0):
        raise ValueError("Treatment has no residual variation after cross-fitting.")

    # Zero treatment residuals have zero weight, so their target can be zero.
    transformed_outcome = np.divide(
        outcome_res,
        treatment_res,
        out=np.zeros_like(outcome_res, dtype=float),
        where=treatment_res != 0,
    )
    cate_model = LGBMRegressor(verbosity=-1).fit(
        train[X], transformed_outcome, sample_weight=weights
    )

    return test.assign(cate=cate_model.predict(test[X]))
