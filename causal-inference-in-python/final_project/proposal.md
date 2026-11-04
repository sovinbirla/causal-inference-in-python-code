# Early developmental intervention

## A causal analysis of the IHDP benchmark

**Final project proposal | Sovin Birla | Causal Models | November 4, 2026**

### 1. Causal Question and Motivation

**Question.** Among infants who received the developmental intervention in the public Infant Health and Development Program (IHDP) benchmark, what is its average causal effect on the simulated developmental outcome, and does the estimated benefit differ across baseline characteristics?

I will distinguish an intervention's effect from differences that already existed between treated and untreated infants. Let Y(1) be an infant's potential outcome under treatment and Y(0) the outcome without treatment. The primary target is the average treatment effect on the treated, ATT = E[Y(1) - Y(0) | T = 1]. This asks how recipients benefited compared with their own untreated counterfactual, which is normally unobserved. A higher observed outcome in the treated group alone does not answer that question.

The project will first estimate the average effect for recipients, then examine conditional average treatment effects within their covariate support. This separates program evaluation from the question of who might benefit more. Because IHDP benchmark outcomes are simulated, the analysis can check whether methods recover known effects. Its contribution will be methodological; estimated changes will be reported in benchmark outcome units and will not be interpreted as clinical IQ gains or evidence for a specific treatment-allocation policy.

### 2. Dataset Selection and Description

I will use the ten public IHDP CSV replications in the CEVAE repository, ihdp_npci_1.csv through ihdp_npci_10.csv. Each contains 747 infants, including 139 treated and 608 controls, and 25 baseline covariates: six continuous and 19 binary. These describe child and maternal characteristics and study site. I will verify the mapping before assigning substantive names to x1-x25.

- **Treatment and observed outcome:** T is the intervention indicator and y_factual is the simulated continuous outcome. Only these fields and baseline X will enter estimation.
- **Evaluation fields:** y_cfactual, mu0, and mu1 will remain separate from fitting and tuning. The known conditional-mean effect is mu1 - mu0.
- **Design:** although the source trial was randomized, the benchmark removes treated children with non-white mothers. I will therefore analyze it as an observational benchmark rather than assume its raw group difference is unbiased.

Working DAG: X -> T -> Y; X -> Y.

**Identification before estimation.** The working graph represents baseline common causes of treatment and outcome. I assume consistency, no interference, and conditional independence of potential outcomes and treatment given X within the supported population. I will adjust for baseline common causes and avoid post-treatment mediators and colliders. ATT requires comparable untreated observations wherever recipients occur. A full-population ATE would additionally require treated outcomes in a subgroup removed by construction, motivating the narrower recipient target. Regression extrapolation cannot by itself establish that missing support is credible.

<!-- pagebreak -->

### 3. Proposed Methods

I will compare three complementary ways of estimating the same ATT. The raw treated-control mean difference will be a descriptive baseline. The main comparison will keep the target, covariates, and analysis sample fixed, rather than attribute differences caused by changing populations to the choice of estimator.

**A. Regression adjustment.** Fit an ordinary least-squares model for untreated outcomes, m0(X) = E[Y | T = 0, X], using controls. Predict the untreated counterfactual for recipients, then calculate:

```text
ATT_RA = mean over treated infants of [Y - m0_hat(X)].
```

The initial specification will include all baseline covariates and squared continuous terms. This uses regression as potential-outcome imputation. I will also use the Frisch-Waugh-Lovell decomposition to explain how regression separates treatment variation associated with X from residual variation. Under heterogeneous effects, a single adjusted treatment coefficient can weight groups differently from ATT; it will not replace recipient-standardized predictions. Linear functional-form assumptions and extrapolation will be checked explicitly.

**B. Propensity-score weighting.** Fit a regularized logistic model for e(X) = P(T = 1 | X). Give recipients weight 1 and controls odds weights e_hat(X)/(1 - e_hat(X)). ATT is the treated outcome mean minus the normalized weighted control outcome mean. This adapts propensity weighting to the recipient target, constructing a control comparison with the recipients' baseline distribution. I will assess covariate balance and weight concentration, rather than choose the model for treatment-classification accuracy alone.

**C. Doubly robust estimation.** Combine the untreated-outcome and propensity models using the ATT score below, where n1 is the number of recipients:

```text
ATT_DR = (1 / n1) * sum_i {
  T_i * [Y_i - m0_hat(X_i)]
  - (1 - T_i) * e_hat(X_i)/(1 - e_hat(X_i))
    * [Y_i - m0_hat(X_i)]
}.
```

This applies the outcome-plus-assignment correction to ATT rather than substituting a population ATE formula. Under identification and regularity assumptions, consistency requires either the propensity or the untreated-outcome model to be correct. It does not follow that missing confounders or absent support are harmless.

**Effect heterogeneity.** Begin with a linear outcome model containing treatment-covariate interactions. Next compare a T-learner, which fits separate treated and control outcome models, with an X-learner. The latter imputes effects in each arm, fits effect models to those targets, and combines them using propensity weights. The 139-versus-608 imbalance motivates testing whether the X-learner reduces artifacts caused by differently regularized outcome models. Use conservative boosted trees and a limited tuning budget; improved performance is a question to test.

**Out-of-fold estimation.** Use identical three-fold, treatment-stratified splits, with fixed seed 2026. Fit preprocessing and models outside each evaluation fold. For the X-learner, generate imputed training targets within the outer training data, keeping the evaluation fold out of both stages. This carries the book's out-of-fold prediction principle into the analysis and reduces overfitting leakage. Oracle fields will never determine model selection.

<!-- pagebreak -->

### 4. Evaluation Plan

**Check the design first.** Verify treatment coding, missingness, duplicate records, binary encodings, and replication alignment. Plot baseline covariates and propensity distributions by treatment. Compare recipients with unweighted and weighted controls using standardized mean differences, with the original treated-group standard deviation as a fixed denominator. Report zero-variance cases and raw differences separately. An absolute SMD below 0.10 is a diagnostic guide, not proof of conditional independence.

Report weight percentiles, the maximum control weight, and effective sample size, ESS = (sum w)^2 / sum(w^2). Very large weights or poor matches in covariate space will signal that a nominally large control group provides little relevant information. A smooth fitted propensity is not evidence that structurally missing observations exist.

**Assess average-effect accuracy.** After freezing specifications, calculate each replication's benchmark ATT as the mean of mu1 - mu0 over the same recipients used for estimation. Report each method's estimate, signed error, and absolute error; summarize mean absolute error and root mean squared error across the ten replications. Use paired method comparisons. Reused covariates and treatment assignments mean these replications are different outcome realizations for a shared cohort, not independent clinical samples.

**Quantify uncertainty and precision.** Construct approximate 95% percentile intervals using 200 within-arm bootstrap resamples, refitting preprocessing and the estimation pipeline. Keep copies of a resampled infant in the same fold. Check interval stability with 500 resamples for the first replication. Report interval widths and sensitivity to five fixed split seeds. Emphasize effect magnitude and uncertainty rather than a binary significance decision. A narrow interval cannot compensate for confounding, misspecification, or inadequate support. Oracle containment across shared-cohort replications will be described as a diagnostic, not formal population coverage.

**Evaluate effect estimates rather than outcome predictions.** For the interaction regression, T-learner, and X-learner, compare out-of-fold conditional-effect predictions with mu1 - mu0 on treated infants only. Report root mean squared conditional-effect error for this recipient distribution, and compare the average predictions with the benchmark ATT. Factual outcome prediction error will diagnose model fit but will not be treated as the main causal accuracy measure.

To evaluate effect ordering, rank recipients by out-of-fold predicted benefit and form three groups. Compare average predicted and benchmark effects within each group. Plot cumulative benchmark benefit along that ordering against random ordering, following the distinction between outcome prediction and treatment responsiveness. Raw treated-control differences inside score groups will not serve as validation because the benchmark is observational. These recipient-cohort curves will not be presented as a validated policy for untreated infants.

**Prespecified robustness checks.**

- Compare linear and restrained nonlinear outcome models and a richer logistic propensity specification. Freeze the alternatives before checking oracle error and report all results.
- Compare original ATT weights with 95th- and 99th-percentile caps. Explain the bias-variance trade-off; capping does not automatically preserve exact ATT identification.
- Omit baseline covariate blocks and add independent noise variables as sensitivity exercises. Their results can expose dependence on adjustment choices but cannot rule out hidden confounding.
- If a support restriction excludes recipients, label the restricted ATT and recompute its benchmark target. Do not compare it silently with the original full-recipient estimand.

<!-- pagebreak -->

### 5. Expected Challenges and Next Steps

**Identification remains assumption-dependent.** The benchmark's connection to a randomized trial does not make the selected sample a new randomized experiment. The graph and conditional-independence assumption organize the analysis, but observed balance cannot establish that every relevant common cause was measured. I will distinguish failures of identification from failures to estimate an identified quantity precisely.

**Small treated sample and model flexibility.** With 139 recipients, complex models may learn noise or create artificial effect heterogeneity. The T-learner is particularly vulnerable when the two outcome models regularize differently. I will constrain tree depth and leaf size, use training-only tuning, and compare all heterogeneity estimates with the interaction-regression baseline. The X-learner may help with imbalance, but its imputed effects still depend on estimated counterfactuals.

**Extrapolation and bias-variance trade-offs.** Regression can produce plausible-looking counterfactual predictions even where control support is weak; weighting can reveal the same problem through a few dominant weights. I will examine both diagnostics and resist selecting a method simply because it produces a favorable or precise estimate. If supported comparisons cannot answer the original question credibly, the report will state that limitation and identify any narrower population being analyzed.

**Benchmark meaning and data handling.** Synthetic outcomes make evaluation possible without creating new clinical evidence. I will retain benchmark outcome units, verify anonymous covariate labels and any 1/2 binary coding, and keep evaluation fields isolated from estimation. The ten replications will be analyzed separately rather than stacked as additional independent infants. No estimated effect or successful robustness result is claimed in this proposal.

**Feasible implementation.** Use pandas and NumPy for the data audit, statsmodels for regression and its residual interpretation, scikit-learn for logistic and tree models, and matplotlib for diagnostics. The methods use a small tabular dataset and require no specialized deep-learning system. The final notebook will record source checksums, model specifications, preprocessing, folds, and seeds.

**Milestones, relative to project start.**

- **Week 1:** Audit the ten files; define treatment, outcome, and recipient target; draw the causal graph; finalize baseline adjustments and overlap checks.
- **Week 2:** Implement regression adjustment, ATT weighting, and doubly robust estimation. Verify formulas on a simple known-effect simulation before applying them to IHDP.
- **Week 3:** Estimate effects across replications; fit the interaction model and T- and X-learners; run bootstrap intervals, ranking evaluation, and the prespecified sensitivity checks.
- **Week 4:** Produce the reproducible notebook, comparison tables, balance and interval plots, and heterogeneity figures; write conclusions that separate effect recovery, precision, and identification assumptions.

**Expected contribution.** The project will connect a clearly defined counterfactual question to multiple estimators and transparent validation. It will assess whether their agreement reflects accurate recovery of recipient effects, how overlap and model assumptions explain disagreement, and whether heterogeneity modeling adds useful information beyond an average effect.
