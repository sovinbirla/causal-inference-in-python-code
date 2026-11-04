# Does job training raise earnings?

## A causal analysis of the Lalonde / NSW data

**Final project proposal | Sovin Birla | Causal Models | November 4, 2026**

### 1. Causal Question and Motivation

**Question.** What is the effect of assignment to the National Supported Work (NSW) job-training program on 1978 earnings for the workers assigned to training, and how closely can observational adjustment recover an experimental reference estimate?

The primary observational estimand is the average treatment effect on the treated, ATT = E[Y(1) - Y(0) | T = 1], where Y(1) and Y(0) are 1978 earnings under assignment to training and control. I will target NSW trainees rather than the entire external comparison population and report effects in the source data's U.S.-dollar units. This is an effect of program assignment, not an identified effect of training hours or completion.

Job training is intended to improve labor-market opportunities, but trainees and nonparticipants often differ in prior earnings and demographics. The Lalonde setting is valuable because it offers both an experimental comparison and nonexperimental comparison groups. The project will ask whether methods based on measured covariates produce a credible counterfactual for trainees, rather than merely predict earnings well. Experimental estimates will be a noisy reference, not known individual treatment effects. [1, 2]

### 2. Dataset Selection and Description

I will use the Dehejia-Wahba male NSW subset with 1974 earnings, distributed on Rajeev Dehejia's data page. The experimental files contain 185 assigned trainees and 260 randomized controls. For the observational analysis, combine those same 185 trainees with the 15,992-person Current Population Survey (CPS) comparison file. Keep experimental controls separate for validation. This explicitly distinguishes the 445-person experimental sample from other datasets also called Lalonde. [1, 3]

- **Treatment and outcome:** treat is the assignment indicator; re78 is 1978 earnings. Retain earnings zeros and the original monetary units for the primary mean-effect analysis.
- **Adjustment set:** age, education, Black and Hispanic indicators, marital status, no-degree indicator, and earnings in 1974 and 1975 (re74, re75). Zero-earnings indicators u74 and u75 can be derived from the baseline earnings fields.
- **Provenance:** use nswre74_treated.txt, nswre74_control.txt, and cps_controls.txt. Add a source indicator and stable row identifier, verify the ten-field schema, and document all recoding. [1]

Working DAG: X -> T -> Y; X -> Y.

In the observational comparison, X must block differences between trainees and CPS controls that affect untreated earnings. Identification requires consistency, no interference, conditional exchangeability of Y(0), and control support for trainee covariates. Motivation and labor-market circumstances may remain unmeasured. Trial randomization supports the experimental contrast but does not randomize NSW membership relative to CPS membership. Source comparability is therefore an additional assumption for observational recovery.

<!-- pagebreak -->

### 3. Proposed Methods

**Experimental reference.** First estimate the difference in mean re78 between the 185 NSW trainees and 260 randomized controls, with a heteroskedasticity-robust interval. This estimates the assignment effect in the experimental subset under its design assumptions. In expectation, randomization makes treated and control workers comparable, but the realized difference is not the exact finite-sample ATT of the 185 trainees. I will also show a baseline-adjusted trial estimate as a precision check.

The primary observational analysis then compares the 185 trainees only with CPS controls, without using trial-control outcomes for model selection. Let e(X) be the propensity to belong to the treated NSW group in this composite sample and m0(X) the expected untreated earnings. Three methods will estimate a common trainee-targeted ATT. Their foundations come from the course's regression and propensity-score notebooks. [4]

**A. Regression adjustment.** Fit a control-outcome regression on CPS controls and predict untreated earnings for NSW trainees. Average Y - m0_hat(X) among trainees. The initial model will use all baseline covariates, squared age and earnings terms, and zero-earnings indicators. A restrained gradient-boosting model will assess nonlinear sensitivity. I will retain re78 in levels for the primary estimand: a log-earnings model changes the question and complicates retransformation to mean dollar effects.

**B. ATT propensity weighting.** Estimate e(X) with a regularized logistic model. Give trainees weight 1 and CPS controls odds weights e_hat(X)/(1 - e_hat(X)). The estimator is the trainee outcome mean minus the normalized weighted control outcome mean. These odds concern membership in the chosen composite sample, not a population probability of receiving NSW training. Their purpose is to align CPS covariates with those of the trainees.

**C. Doubly robust ATT estimation.** Combine the propensity and untreated-outcome models using:

```text
ATT_DR = (1 / n1) * sum_i {
  T_i * [Y_i - m0_hat(X_i)]
  - (1 - T_i) * e_hat(X_i)/(1 - e_hat(X_i))
    * [Y_i - m0_hat(X_i)]
}.
```

Here n1 is the number of trainees. Under identification and regularity assumptions, this estimator remains consistent if either nuisance model is correctly specified. It cannot compensate for hidden motivation differences, lack of control support, or a failure to transport untreated outcomes from CPS workers to NSW trainees.

**Implementation and comparison.** Use identical three-fold, treatment-stratified cross-fitting splits with seed 2026. Fit transformations and nuisance models within training folds, and score the held-out folds. Prespecify specifications using baseline balance and factual prediction diagnostics. Freeze them before comparing observational results with trial earnings outcomes. Compare point estimates, uncertainty, weight concentration, and experimental discrepancies together; proximity to one reference estimate will not be the model-selection rule.

**Secondary extension.** If core results are stable, perform propensity matching with a prespecified caliper as a design sensitivity check. Report retained trainees, reused controls, and balance. Dropping trainees changes the target; matching estimates will not be silently compared with a full-cohort ATT. Heterogeneous-effect modeling is optional given the small treated sample.

<!-- pagebreak -->

### 4. Evaluation Plan

**Audit the data version.** Verify treatment counts, source labels, earnings units, baseline field definitions, zero-earnings indicators, and missingness. Identical covariate profiles do not necessarily identify duplicate people; do not delete them without provenance. Confirm that experimental controls never enter the observational fitting sample and that the same NSW trainee records are reused consistently across analyses.

**Overlap and balance.** Plot baseline earnings and propensity distributions separately by group. Report unweighted and ATT-weighted standardized mean differences for all covariates, fixing the denominator to the original trainee standard deviation. Flag zero-variance cases and report raw differences in proportions or means. Use absolute SMD below 0.10 as a diagnostic guide. Also report maximum weight, weight percentiles, control effective sample size, and the fraction of trainee profiles with poor control support. A large CPS sample alone does not guarantee relevant controls.

**Experimental comparison with uncertainty.** For each observational method, report its ATT estimate, interval, and signed dollar difference from the experimental reference. Because both estimates reuse the same trainees, their errors are correlated. A joint bootstrap will resample trainees once and use that same resample in both estimators, while separately resampling trial controls and CPS controls. Refit the full nuisance pipeline in 500 resamples. Report an interval for the observational-minus-experimental discrepancy, not just two disconnected confidence intervals.

This comparison assesses recovery of an experimentally informed target under comparable population assumptions. A small discrepancy is encouraging but does not prove observational identification; a large one may reflect bias, sampling variability, or differences between realized ATT and the trial estimand. No individual counterfactual outcomes are available, so I will not report PEHE, exact ATT error, or nominal coverage against an invented ground truth.

**Prespecified robustness checks.**

- Compare the main baseline specification with richer age, education, and earnings terms and a nonlinear outcome model. Add independent noise covariates and vary split seeds to assess instability.
- Contrast unmodified ATT odds weights with 95th- and 99th-percentile weight caps. Capping can trade bias for variance and does not automatically preserve exact ATT identification. Any support restriction that removes trainees will be labeled as a new target.
- Examine how omitting re74 and re75 changes estimates and balance. Separately evaluate weighted baseline earnings as a design diagnostic, not as an unquestionable placebo outcome: program timing and anticipatory behavior must be checked.
- Report the influence of the largest earnings observations with leave-one-out or capped-outcome sensitivity summaries. The primary outcome remains uncapped earnings; winsorization changes the estimand.

**Sensitivity to unmeasured differences.** Supplement covariate checks with a transparent bias scenario. Suppose, after measured adjustment, untreated earnings for NSW trainees would exceed the CPS-based prediction by delta dollars. Then the adjusted ATT shifts downward by delta. Plot this shift over a prespecified symmetric range calibrated to baseline earnings differences, and report the delta needed to change the conclusion. This is an assumption-based sensitivity analysis, not an estimate of hidden bias.

**Planned outputs.** A sample-composition table, baseline earnings plots, an overlap plot, a balance plot, and an ATT comparison with experimental-discrepancy intervals will make the identification and precision trade-offs visible.

<!-- pagebreak -->

### 5. Expected Challenges and Next Steps

**Substantial selection differences.** NSW trainees may be much less similar to the CPS population than trial controls are. I will prioritize balance and support diagnostics before fitting increasingly flexible models. If comparable controls are unavailable for important trainee groups, I will explicitly report that the full trainee ATT relies on extrapolation, and present a clearly named restricted analysis only as a secondary result.

**Small treated sample and skewed earnings.** The 185 trainees limit model complexity, even with thousands of controls. Earnings have zeros and a long right tail. Regularization, simple specifications, whole-pipeline uncertainty calculations, and influence diagnostics will help distinguish unstable estimates from substantive disagreement. I will not discard high earners simply to obtain a favorable program effect.

**Multiple Lalonde versions.** The 445-person NSW subset, the larger original trial sample, the CPS and PSID comparison files, and the 614-row MatchIt example are different analytical datasets. I will pin the three named files and retain their provenance rather than combine versions with the same label. The MatchIt example is not the experimental control sample used here. [1, 5]

**Interpretation and external validity.** The question concerns program assignment for a historical male NSW subset. Estimates will not be generalized to today's labor market or to the effect of training completion without additional assumptions. The experimental reference itself has uncertainty. Agreement across regression, weighting, and doubly robust estimation will be assessed jointly with substantive assumptions rather than used as automatic validation.

**Implementation and milestones.** The roughly 16,000-person observational sample is feasible in Python using pandas, NumPy, scikit-learn, statsmodels, and matplotlib.

- **Week 1:** Download and checksum the NSW and CPS files; audit coding and timing; finalize the trainee ATT, adjustment graph, and specifications.
- **Week 2:** Implement regression, weighting, and doubly robust ATT estimation; verify formulas on a known-effect simulation and produce baseline design diagnostics.
- **Week 3:** Freeze the observational analysis, calculate the experimental reference, run the joint bootstrap and sensitivity checks, and document support restrictions.
- **Week 4:** Complete the reproducible notebook, figures, and report; explain discrepancies with the experiment and the limits of the evidence.

**Expected contribution.** This project will evaluate how much observed covariate adjustment can recover a trial-informed earnings effect in a difficult selection setting. A credible finding can be either successful recovery under adequate support or a clear demonstration of why the observational comparison remains unreliable.

### References

[1] Dehejia, R. H. [NSW, CPS, and PSID data documentation and files](https://users.nber.org/~rdehejia/data/.nswdata3.html). Dehejia-Wahba sample and field definitions. Accessed November 4, 2026.

[2] LaLonde, R. J. (1986). Evaluating the econometric evaluations of training programs with experimental data. *American Economic Review*, 76(4), 604-620. Dehejia, R. H., and Wahba, S. (1999). Causal effects in nonexperimental studies: Reevaluating the evaluation of training programs. *JASA*, 94(448), 1053-1062. Bibliographic details on the [authors' data page](https://users.nber.org/~rdehejia/data/.nswdata3.html).

[3] PyWhy. DoWhy v0.12: [Lalonde / IHDP refutation example](https://www.pywhy.org/dowhy/v0.12/example_notebooks/dowhy_refutation_testing.html). Accessed November 4, 2026.

[4] Supplied course notebooks 01-07, especially regression, propensity scores, doubly robust estimation, and graphical identification.

[5] MatchIt. [Lalonde dataset documentation](https://kosukeimai.github.io/MatchIt/reference/lalonde.html). Distinct 614-observation example. Accessed November 4, 2026.
