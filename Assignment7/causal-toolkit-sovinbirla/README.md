# causal-toolkit-sovinbirla

[![Tests](https://github.com/sovinbirla/causal-toolkit-sovinbirla/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/sovinbirla/causal-toolkit-sovinbirla/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/causal-toolkit-sovinbirla.svg)](https://pypi.org/project/causal-toolkit-sovinbirla/)

A Python package by Sovin Birla for estimating average treatment effects (ATE)
and conditional average treatment effects (CATE). It packages the Week 2–4
course implementations and the Week 5 pytest suite from
[causal-inference-in-python-code](https://github.com/sovinbirla/causal-inference-in-python-code).

## Installation

Requires Python 3.10 or newer. Install from PyPI:

```bash
pip install causal-toolkit-sovinbirla
```

Verify the installation:

```bash
python -c "from causal_toolkit_sovinbirla import calculate_ate_ci; print('Published!')"
```

PyPI project: https://pypi.org/project/causal-toolkit-sovinbirla/

## Development installation

Using [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/sovinbirla/causal-toolkit-sovinbirla.git
cd causal-toolkit-sovinbirla
uv venv
uv pip install -e .
uv run pytest
```

`uv run` installs the development dependency group, including pytest. To install
the development tools explicitly, use `uv pip install -e '.[dev]'`.

To install directly from GitHub without cloning:

```bash
uv pip install git+https://github.com/sovinbirla/causal-toolkit-sovinbirla.git
```

The distribution name is `causal-toolkit-sovinbirla`; the Python import name is
`causal_toolkit_sovinbirla`.

Scikit-learn is capped below 1.10 because these course implementations use its
unpenalized logistic regression API, which is deprecated in versions 1.8 and 1.9.

## Quick start: randomized trials and propensity scores

```python
import numpy as np
import pandas as pd
from causal_toolkit_sovinbirla import (
    calculate_ate_ci,
    calculate_ate_pvalue,
    ipw,
    doubly_robust,
)

rng = np.random.default_rng(42)
n = 2000
x = rng.normal(size=n)
treatment = rng.binomial(1, 0.5, size=n)
data = pd.DataFrame({
    "x": x,
    "T": treatment,
    "Y": 2 * treatment + x + rng.normal(size=n),
})

ate, lower, upper = calculate_ate_ci(data)
ate, statistic, pvalue = calculate_ate_pvalue(data)
weighted_ate = ipw(data, "1 + x", T="T", Y="Y")
adjusted_ate = doubly_robust(data, "1 + x", T="T", Y="Y")
```

## Meta-learners

```python
from causal_toolkit_sovinbirla import (
    s_learner_discrete,
    t_learner_discrete,
    x_learner_discrete,
    double_ml_cate,
)

train = data.iloc[:1500].copy()
test = data.iloc[1500:].copy()
predictions = s_learner_discrete(train, test, ["x"], "T", "Y")
print(predictions[["x", "cate"]].head())

# The T- and X-learners accept the same arguments.
t_predictions = t_learner_discrete(train, test, ["x"], "T", "Y")
x_predictions = x_learner_discrete(train, test, ["x"], "T", "Y")

# Double ML also supports continuous treatments.
continuous = data.assign(dose=x + rng.normal(size=n))
continuous["outcome"] = (
    1.5 * continuous["dose"] + continuous["x"] + rng.normal(size=n)
)
dml_predictions = double_ml_cate(
    continuous.iloc[:1500], continuous.iloc[1500:], ["x"], "dose", "outcome"
)
```

## API

All eight functions are available from `causal_toolkit_sovinbirla` or their
respective submodules.

| Module | Function | Returns |
| --- | --- | --- |
| `rct` | `calculate_ate_ci(data, alpha=0.05)` | `(ate, ci_lower, ci_upper)` using a normal approximation |
| `rct` | `calculate_ate_pvalue(data)` | `(ate, statistic, pvalue)` for a two-sided normal test |
| `propensity` | `ipw(df, ps_formula, T, Y)` | ATE as a float using inverse propensity weighting |
| `propensity` | `doubly_robust(df, formula, T, Y)` | ATE as a float using augmented inverse propensity weighting |
| `meta_learners` | `s_learner_discrete(train, test, X, T, y)` | Copy of `test` with a `cate` column from one outcome model |
| `meta_learners` | `t_learner_discrete(train, test, X, T, y)` | Copy of `test` with a `cate` column from separate outcome models |
| `meta_learners` | `x_learner_discrete(train, test, X, T, y)` | Copy of `test` with a `cate` column from propensity-weighted imputed effect models |
| `meta_learners` | `double_ml_cate(train, test, X, T, y)` | Copy of `test` with a `cate` column from five-fold cross-fitted residuals |

RCT functions require `T` (0/1 treatment) and `Y` (numeric outcome) columns,
with at least two nonmissing observations in each arm. `alpha` is a significance
level between 0 and 1. Propensity functions accept a Patsy right-hand-side
formula, such as `"1 + age + income"`; `T` and `Y` name the treatment and outcome
columns. Use binary 0/1 treatment with both arms represented and complete data.

For meta-learners, `X` is a list of numeric feature column names, and `T` and `y`
name the treatment and outcome columns. The discrete learners need both treatment
arms in training data. The S-learner also expects `T` in `test`. Double ML needs
at least five training rows and residual treatment variation; its `cate` is the
estimated outcome change per unit of treatment. The estimators assume randomized
treatment or appropriate adjustment for measured confounding, overlap, and no
interference. The package does not validate these causal assumptions.

## Tests and distribution builds

```bash
uv run pytest tests/ -v --cov=causal_toolkit_sovinbirla --cov-report=term-missing
uv build
uv run twine check dist/*
```

`uv build` produces a wheel and source distribution in `dist/` using the
standard Python build configuration in `pyproject.toml`.

## Continuous integration and publishing

[Tests](https://github.com/sovinbirla/causal-toolkit-sovinbirla/actions/workflows/tests.yml)
runs pytest with coverage on Python 3.11 for pushes to `main` and `develop`,
and pull requests targeting `main`. It also builds both distributions, validates
their metadata, and installs the wheel in a clean environment to check every
public function import.

The [publishing workflow](https://github.com/sovinbirla/causal-toolkit-sovinbirla/actions/workflows/publish.yml)
runs when a GitHub release is published. To configure the first release:

1. Create a [PyPI account](https://pypi.org/account/register/) and generate an API
   token in account settings. A first upload needs an account-scoped token.
2. Open the repository's **Settings → Secrets and variables → Actions** and add
   the token as a repository secret named `PYPI_API_TOKEN`. The workflow also
   accepts `MYKEY`, the name configured for this repository's initial release.
3. Confirm the Tests workflow passes for the commit you will release.
4. Create and publish a GitHub release tagged `v0.1.1` from `main`.

The workflow checks that the tag, `pyproject.toml`, and package version agree,
runs the tests, builds and checks the distributions, uploads to PyPI, then
installs the published version in a clean environment and checks all public
imports. For subsequent releases, update both version strings and use a matching
tag. PyPI requires a new version for each upload.

For a manual upload, set `TWINE_USERNAME=__token__` and supply your token securely
through `TWINE_PASSWORD` or Twine's password prompt, then run:

```bash
python -m pytest tests/ -v
python -m build
python -m twine check --strict dist/*
python -m twine upload dist/*
```

Start with an empty `dist/` directory so older versions are not uploaded again.
Never commit API tokens or paste them into source files.

## Source and license

The package preserves the course algorithms and adapts imports for installation.
Example data generation was removed from `rct.py` so importing the package does
not reseed NumPy or create example datasets. The original course files remain in
the source repository. MIT licensed; see [LICENSE](LICENSE), including the
upstream copyright notice for Matheus Facure's code accompanying *Causal
Inference in Python*.
