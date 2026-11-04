# Birthweight and infant survival

## A causal estimation proposal using the Twins benchmark

**Final project proposal | Sovin Birla | Causal Models | November 4, 2026**

### 1. Causal Question and Motivation

**Question.** In same-sex twin pairs where both infants weigh less than 2,000 grams, what is the average difference in first-year mortality between the heavier and lighter twin, and can causal adjustment recover that contrast when only one twin's outcome is observed in a risk-dependent sample?

The primary target is the benchmark average treatment effect, ATE = E[Y(1) - Y(0)], where a pair is the analysis unit, Y(1) is the heavier twin's death indicator, and Y(0) is the lighter twin's. Estimates will be reported as mortality risk differences in percentage points; negative values favor the heavier twin. This is a precisely defined benchmark contrast, with a conditional clinical interpretation requiring much stronger assumptions.

Birthweight and survival motivate a meaningful perinatal question. Twins also offer a way to evaluate causal estimators using real paired outcomes. However, different twins are different people: one twin's outcome is not the literal counterfactual outcome of the other infant. Relative birthweight is not a well-defined medical intervention, and placental conditions or twin-specific illness can affect both weight and mortality. I will distinguish benchmark recovery from a claim that increasing an infant's weight would reduce mortality. [1, 2]

### 2. Dataset Selection and Description

I will use the CEVAE Twins files linked by DoWhy: twin_pairs_X_3years_samesex.csv, twin_pairs_T_3years_samesex.csv, and twin_pairs_Y_3years_samesex.csv. They contain covariates, both birthweights, and both mortality outcomes. The source covers U.S. twin births in 1989-1991; the published low-birthweight benchmark has 11,984 pairs and 46 covariates before analysis-specific exclusions. The final count will be verified after joining and filtering. [1-3]

- **Treatment and outcome:** T = 1 selects the heavier twin's first-year death indicator; T = 0 selects the lighter twin's. Weight orders the twins and defines eligibility; it is not a predictor in the main benchmark model.
- **Baseline information:** candidate covariates include gestational-age category, parental age and education, pregnancy risk factors, smoking, and prenatal care. A documented timing audit will retain only pair-level information available before outcome observation.
- **Pair integrity:** retain one stable pair identifier across all files. Exclude identifiers, death-related information, actual twin outcomes, and variables whose availability depends on which twin is selected from the adjustment set. [2, 3]

Working DAG: X -> T -> Y; X -> Y.

Here T determines which recorded outcome is observed, rather than a biological change in weight. I will generate observation probabilities from baseline pair risk only, retain gestational age in the primary adjustment set, and hide one outcome per pair. Conditional exchangeability holds for this designed observation mechanism, with positivity enforced by construction. A separate stress test will omit gestational age; exchangeability may then fail. Biological birthweight effects would additionally require within-pair comparability and assumptions about interference that these data cannot verify.

<!-- pagebreak -->

### 3. Proposed Methods

**Benchmark construction.** Following the selective-observation idea in the Twins literature, I will generate T from a prespecified logistic function of gestational-age category and a small set of baseline pair covariates. I will choose coefficients before inspecting outcomes and bound observation probabilities between 0.10 and 0.90. Only Y = T*Y(1) + (1 - T)*Y(0) enters fitting. Repeat this process for 30 fixed seeds, using identical assignments and folds for all methods. This is an adaptation of the published benchmark, not a reproduction of its hidden-proxy model. [1]

The full paired outcome file will be held separately for evaluation. Let e(X) = P(T = 1 | X) and mt(X) = E[Y | T = t, X]. I will estimate the same pair-population ATE with three complementary approaches, alongside a raw observed mortality difference. These methods extend the course material on regression, propensity scores, and doubly robust estimation. [4]

**A. Regression standardization.** Fit separate regularized logistic outcome models for the observed heavier and lighter groups. Predict both mortality probabilities for every held-out pair and average their difference. Models will include gestational-age indicators and the prespecified baseline covariates; a shallow tree model will check nonlinear sensitivity. Standardization estimates a risk difference directly. A logistic treatment coefficient or odds ratio will not be substituted for the target ATE.

**B. Inverse probability weighting.** Estimate the observation propensity using logistic regression, then compare normalized outcome means weighted by 1/e_hat(X) in the heavier group and 1/(1 - e_hat(X)) in the lighter group. Weighting balances the risk factors driving selective observation without requiring a correct outcome model. The known generating probabilities will provide an additional diagnostic version, while the main comparison will use estimated propensities as in an ordinary observational analysis.

**C. Augmented inverse probability weighting.** Combine both models using the doubly robust score:

```text
score_i = m1_hat(X_i) - m0_hat(X_i)
  + T_i * [Y_i - m1_hat(X_i)] / e_hat(X_i)
  - (1 - T_i) * [Y_i - m0_hat(X_i)] / (1 - e_hat(X_i)).
ATE_DR = mean(score_i).
```

Under the benchmark identification assumptions, consistency requires either the propensity or the outcome regressions to be correctly specified, with suitable regularity conditions. This protection does not apply to the omitted-gestational-age stress test if the remaining covariates are insufficient for exchangeability.

**Training and fair comparison.** Use three-fold cross-fitting by pair, with preprocessing and tuning confined to training folds. Each pair contributes exactly one observed outcome, and its hidden twin must never appear in another fold or in a fitted feature. Models will be selected using factual log loss and calibration, never benchmark ATE error. All methods will use the same retained pairs, adjustment variables, splits, and seeds.

**Optional heterogeneity.** The two logistic models form a T-learner. If core estimation is stable, compare it with a conservative X-learner, focusing on broad gestational-age groups and out-of-fold predictions. Heterogeneity is exploratory; the average contrast and its dependence on observation bias remain the main project.

<!-- pagebreak -->

### 4. Evaluation Plan

**Data and design audit.** Check that pair identifiers match one-to-one across covariate, weight, and mortality files. Verify the heavier/lighter ordering, eligibility of both twins, death coding, missing-value codes, and the handling of equal weights. Exclude ambiguous weight ties from the ranked-twin analysis and report their number. Fit imputation and categorical encoding inside training folds. Record all exclusions and changes from the published cohort.

**Known benchmark target.** On the final pair cohort, calculate the complete-pair mean of Y(1) - Y(0) only after models and specifications are frozen. Compare each estimator with this finite-cohort contrast using signed error, absolute error, and root mean squared error over the 30 observation draws. Because the same pairs and outcomes recur, these repetitions assess observation-mechanism variability, not 30 independent birth cohorts. No previously published effect estimate will be presented as a result of this project.

**Balance and support.** Plot fitted propensities by observed twin group. Report covariate standardized mean differences before and after weighting, weight percentiles, maximum weight, and effective sample size in both groups. Use a fixed unweighted pooled standard deviation for continuous covariates, and report differences in proportions for binary indicators. An absolute SMD below 0.10 is a screening guide. Enforced probability bounds ensure design positivity, but sparse combinations of risk factors can still create finite-sample instability.

**Uncertainty on two scales.** First, use the 30 observation draws to report variability conditional on the fixed pair cohort. Second, use 300 bootstrap resamples of whole pairs for approximate sampling intervals in a representative draw, refitting preprocessing and all nuisance models. The pair, not the infant row, is the resampling unit. These sampling intervals concern a broader pair population under the model; their containment of the finite-cohort contrast will not be described as formal population coverage.

**Robustness checks.** Prespecify the following before inspecting benchmark error:

- Vary the strength of risk-dependent observation while retaining probability bounds. Compare estimated and known observation-probability weighting to separate propensity error from outcome-model error.
- Compare linear-logit and shallow nonlinear outcome models, then deliberately omit gestational age. Report whether omitted-confounder bias persists for the doubly robust estimator rather than assuming it will disappear.
- Refit after excluding covariates with uncertain timing or missingness. Compare complete-case and fold-imputed analyses while identifying any change in target cohort.
- Add an independent noise covariate and vary split seeds. Large changes will flag model instability. Repeat the main analysis with narrower and wider probability bounds as a sensitivity to overlap.

**Heterogeneity and prediction.** Evaluate hidden-outcome probability predictions with Brier score, log loss, and calibration. Compare predicted average effects with full-pair average contrasts in prespecified broad groups. The realized binary difference between twins is not a noise-free conditional effect, so it will not be labeled an oracle CATE or used to claim standard root-PEHE accuracy. Predictive discrimination alone will not establish accurate treatment-effect estimation.

**Planned outputs.** Deliver a cohort flow table, a common-target ATE comparison, error-versus-selection plots, balance and weight diagnostics, and a short analysis of the gestational-age omission experiment. All reported quantities will distinguish biological interpretation from the designed observation benchmark.

<!-- pagebreak -->

### 5. Expected Challenges and Next Steps

**Interpretation is the central limitation.** Paired outcomes provide an unusually useful evaluation reference, but do not identify the effect of a particular prenatal intervention. Shared family and pregnancy conditions reduce some differences; they do not remove fetal-specific confounding or establish no interference. I will keep conclusions focused on recovery of the ranked-twin mortality contrast under a documented observation design, and explain the additional assumptions needed for a clinical interpretation.

**Variable timing and dependence.** Some public fields describe delivery rather than prenatal conditions. I will audit definitions before selecting predictors, avoid treating birthweight itself as an adjustment variable, and exclude ambiguous fields from the core analysis. A pair identifier will govern joins, sample splits, and uncertainty calculations, preventing the artificial precision that would arise from treating co-twins as unrelated records.

**Rare events and small subgroups.** Mortality is binary, and some risk categories may have few deaths. Regularization, restrained tree depth, and broad prespecified groups will reduce overfitting. I will report event counts and interval widths rather than interpret unstable subgroup rankings. If a training fold has inadequate events, I will simplify the model specification before outcome-based comparisons.

**Feasible implementation.** The selected pair dataset is manageable on a laptop. Python tools will include pandas, NumPy, scikit-learn, statsmodels, and matplotlib. No deep latent-variable model is required to answer the core question. The complete-pair reference, observation generator, fitted-data view, and evaluation code will be kept separate and reproducible.

**Milestones, relative to project start.**

- **Week 1:** Obtain and checksum the three source files; audit pair alignment, field definitions, and cohort eligibility; finalize the target and observation mechanism.
- **Week 2:** Implement regression standardization, weighting, and doubly robust estimation; verify formulas on a simple simulation before using the Twins outcomes.
- **Week 3:** Run the 30 prespecified draws, pair-bootstrap intervals, overlap diagnostics, and gestational-age sensitivity experiment. Add heterogeneity only if core estimation is stable.
- **Week 4:** Produce the final notebook, figures, and report, separating benchmark accuracy from assumptions about biological causation and external validity.

**Expected contribution.** This project will test how well multiple adjustment methods recover a known paired mortality contrast under selective observation, and show how omitted risk factors and weak overlap affect their credibility. The direction and magnitude of the project's estimates remain to be determined.

### References

[1] Louizos, C., et al. (2017). Causal effect inference with deep latent-variable models. *NeurIPS 30*, Section 4.3. [Paper](https://arxiv.org/abs/1705.08821).

[2] PyWhy. DoWhy v0.12: [Twins dataset example](https://www.pywhy.org/dowhy/v0.12/example_notebooks/dowhy_twins_example.html). Treatment, cohort restriction, and paired-file construction. Accessed November 4, 2026.

[3] AMLab-Amsterdam. CEVAE: [public Twins covariate, birthweight, and outcome files](https://github.com/AMLab-Amsterdam/CEVAE/tree/master/datasets/TWINS). Accessed November 4, 2026.

[4] Supplied course notebooks 01-07: potential outcomes, randomization, graphical models, regression adjustment, propensity scores, doubly robust estimation, effect heterogeneity, and meta-learners.
