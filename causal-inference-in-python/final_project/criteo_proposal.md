# Does advertising create conversions?

## A causal uplift analysis of Criteo's public benchmark

**Final project proposal | Sovin Birla | Causal Models | November 4, 2026**

### 1. Causal Question and Motivation

**Question.** What is the effect of assignment to advertising eligibility, rather than advertising holdout, on a user's probability of conversion during the study window, and can treatment-effect models identify groups with greater incremental response?

The primary target is an intention-to-treat-style average effect, ATE = E[Y(1) - Y(0)], for the corrected public benchmark distribution. T denotes advertising-group assignment; Y is the binary conversion indicator. I will report risk differences in percentage points and incremental conversions per 1,000 eligible users. A secondary target is the conditional average treatment effect, which may guide budget-limited targeting under the benchmark assumptions.

Advertising attribution can reward ads shown to users who would have purchased anyway. A randomized holdout creates a more credible comparison for incrementality and makes it possible to distinguish response prediction from effect estimation. Importantly, eligibility is different from actual ad exposure. The project will estimate assignment effects, without conditioning on exposure or claiming that an exposure-conversion association is causal. [1]

### 2. Dataset Selection and Description

I will use CRITEO-UPLIFTv2, the corrected release associated with the Criteo Hugging Face dataset. Its documented size is 13,979,592 user records, with roughly 85% assigned to treatment and an overall conversion rate of about 0.29%. The publisher corrected an earlier advertiser-related leak; the original roughly 25-million-row release will not be substituted. File revision, checksum, schema, and observed counts will be verified. [1-3]

- **Treatment:** treatment is assignment to the advertising group (1) or holdout (0). Some assigned users receive no exposure; the primary analysis retains them in their assigned group.
- **Outcomes:** conversion is primary; visit is a secondary outcome. Exposure and visit are excluded from adjustment for conversion because they can occur after assignment.
- **Features:** f0-f11 are twelve anonymized baseline fields. Numerical storage does not make every field continuous; the documentation distinguishes continuous and encoded categorical variables. I will verify cardinalities and fit preprocessing only on training data. [1, 2]

Working DAG: T -> E -> Y; X -> E; X -> Y.

The graph summarizes eligibility T, exposure E, baseline X, and conversion Y; shared causes of exposure and conversion may be unmeasured. Randomized eligibility, rather than exposure adjustment, motivates identification. The public release also uses privacy-related nonuniform label sampling. I will treat assignment exchangeability after release as a working assumption, assess balance, and restrict interpretation to the benchmark. Unknown selection probabilities prevent recovery of the original campaign's conversion effect; adjustment cannot automatically undo outcome-dependent sampling. [1, 3]

<!-- pagebreak -->

### 3. Proposed Methods

I will compare a design-based assignment contrast with outcome-adjusted and doubly robust estimates, then evaluate two conditional-effect models on a separate test set. All estimates will use the same public-release target and exclude post-assignment variables. The course notebooks on randomized experiments, propensity scores, effect heterogeneity, and meta-learners provide the methodological foundation. [4]

**A. Difference in mean conversion rates.** Estimate the conversion rate in each assigned group and take their difference. Under exchangeable assignment in the analyzed release, this identifies the assignment ATE without an outcome model. Use the actual group sizes when calculating standard errors; a balanced-trial formula would be inappropriate. Repeat the estimate for visit as a clearly labeled secondary analysis. This is the main transparent reference, not a known true individual effect.

**B. Outcome regression and standardization.** Fit separate regularized outcome models for treated and holdout users, predicting conversion probabilities from baseline X. Begin with logistic regression and compare a shallow histogram-based boosting model. Average m1_hat(X) - m0_hat(X) over held-out users. Standardization targets a risk difference, while an odds ratio from logistic regression answers a different question. Calibration and flexibility matter because conversions are rare.

**C. Augmented inverse probability weighting.** Combine held-out outcome predictions with a propensity model using:

```text
score_i = m1_hat(X_i) - m0_hat(X_i)
  + T_i * [Y_i - m1_hat(X_i)] / e_hat(X_i)
  - (1 - T_i) * [Y_i - m0_hat(X_i)] / (1 - e_hat(X_i)).
ATE_DR = mean(score_i).
```

Use the training-sample treatment fraction as the constant-propensity reference, and a baseline-feature logistic propensity as a sensitivity analysis. The documented 85% ratio is approximate, not an exact known probability for every record. Under identification and regularity assumptions, the augmented estimator is consistent if the outcome regressions or propensity model are correct. Neither version fixes unknown release-selection bias.

**D. Heterogeneous effects: T- and X-learners.** The separate outcome models form a T-learner. An X-learner will impute treatment-effect targets from those models, learn effect functions in each group, and combine them using the propensity score. Unequal group sizes motivate this comparison. Keep the base-model family and tuning budget comparable, constrain complexity, and evaluate incremental benefit rather than conversion prediction alone. [4, 5]

**Training and scale.** Assign records to 60% training, 20% validation, and 20% test partitions using a seeded hash of a stable release row identifier, independent of outcomes. Start with a uniform one-million-record training subset and expand if resources permit. Use validation for hyperparameters and freeze all rankings before testing. Produce out-of-fold training predictions for imputed X-learner targets; the test set remains untouched by fitting or threshold selection.

**Fair comparison.** Score every method on the same held-out release distribution. Record sample sizes, runtime, and event counts. Keep the original treated-control and event proportions: outcome-based downsampling or uncorrected class balancing would change probability calibration and can distort uplift. [1]

<!-- pagebreak -->

### 4. Evaluation Plan

**Release and assignment diagnostics.** Validate the corrected release's row count, all binary fields, missingness, feature cardinalities, and group event rates. Check whether any control rows have exposure and whether conversion occurs without a recorded visit; investigate violations against the published field definitions. Compare baseline covariates across assigned groups using standardized differences and distribution plots. Also measure how well baseline features predict assignment on held-out data. These checks can reveal problems, but cannot prove that anonymization and selection preserved exchangeability.

**Average effects and precision.** Report unadjusted, standardized, and augmented ATE estimates with 95% intervals on the common test population. For the mean difference, use independent Bernoulli-sample variance by arm. For augmented estimates, use the held-out score variance and report sensitivity to the propensity specification. Use a paired test-record bootstrap for method differences, retaining fixed fitted models. These intervals describe test-population uncertainty conditional on training; five prespecified training seeds will separately show model-fitting variability.

**Uplift without observed counterfactuals.** Sort test users by frozen predicted benefit and evaluate targeting fractions q = 0.10, 0.20, 0.50, and 1.00. Let S(q) select the top q fraction. The following inverse-probability score estimates incremental conversions per user in the entire test population under that targeting rule, relative to assigning nobody:

```text
gain(q) = mean_i { S_i(q) *
  [T_i*Y_i/e_hat(X_i) - (1-T_i)*Y_i/(1-e_hat(X_i))] }.
```

Under exchangeability and overlap this targets E[S(q)*(Y(1) - Y(0))]. Compare it with a random-targeting rule of the same size, using q times the overall effect. Report the gain curve and its area above that random baseline, with the normalization stated explicitly. Summaries will not interchange incompatible Qini or AUUC definitions. No PEHE will be reported because individual counterfactual conversion outcomes are unavailable.

**Calibration and policy value.** Compare predicted and observed incremental response in five broad groups formed from frozen uplift scores, reporting treated and control event counts. Suppress strong interpretation of groups with too few control conversions. Report policy gain at the prespecified targeting fractions with paired bootstrap intervals and, as a sensitivity check, augmented-score policy evaluation. The business value of a policy additionally requires conversion values and advertising costs, which are absent here.

**Robustness checks.**

- Repeat the main comparison on visit, preserving conversion as the primary outcome. Different results across outcomes will be interpreted substantively rather than used to select the most favorable claim.
- Compare linear and nonlinear outcome models, constant and feature-based propensity models, and five fixed training seeds. Check probability calibration without changing evaluation-set class proportions.
- Compare T- and X-learners with a conversion-prediction ranking and random targeting. If response ranking performs similarly, report that evidence instead of assuming causal ranking must dominate.
- Assess sensitivity to extreme fitted propensities and document any restriction of the target population. Keep release-selection limitations separate from overlap problems; weight clipping cannot reconstruct missing sampling probabilities.

**Planned outputs.** Deliver an assignment and event-rate table, an ATE interval plot, feature-balance diagnostics, gain curves, group calibration plots, and a runtime/precision summary. Significant average effects alone will not establish useful individual targeting.

<!-- pagebreak -->

### 5. Expected Challenges and Next Steps

**Very low event rates.** Conversion is uncommon and the holdout group is relatively small. Fine-grained rankings can therefore have high evaluation variance despite millions of records. I will use broad targeting fractions, event-count reporting, regularization, and intervals. A visit analysis provides a higher-frequency secondary endpoint, but will not replace an inconclusive conversion result.

**Eligibility, exposure, and selection.** Comparing exposed and unexposed users would reintroduce selection because actual exposure depends on user behavior and the advertising system. Exposure and visit will remain outside the conversion adjustment set. The publisher's nonuniform label sampling also limits transport to original campaign users. Without the selection probabilities, original-population incrementality is not identified by the released conversion rates; the report will explicitly qualify any causal interpretation of release-level contrasts.

**Anonymization and pooled trials.** Anonymous features support prediction but do not support named demographic explanations. Advertiser provenance is not released, and the corrected version rebalances allocation across source trials. I will verify versioning and balance, avoid inferring feature meanings, and explain that these diagnostics do not eliminate all uncertainty about pooling or sampling. User or campaign clustering cannot be reconstructed reliably if the relevant identifiers are absent. [1-3]

**Computation and data handling.** Stream the compressed file and cache only needed baseline fields, assignment, and outcomes. Use compact dtypes, a fixed training cap, shallow models, and batch test prediction. A one-million-record pilot will establish memory and runtime before expanding training. The full held-out partition can be evaluated in batches, retaining only the arrays needed for scores and rankings. Standard Python tools are sufficient; no GPU is required.

**Milestones, relative to project start.**

- **Week 1:** Pin the corrected release and checksum; audit fields and assignment balance; establish outcome-independent partitions and event counts; finalize the assignment-effect target.
- **Week 2:** Implement mean differences, standardized regressions, and augmented estimation. Validate formulas on a simulated randomized example and benchmark memory and runtime.
- **Week 3:** Fit T- and X-learners, select models on validation data, freeze rankings, and calculate test-set ATEs, policy gains, intervals, and robustness checks.
- **Week 4:** Complete a reproducible notebook, figures, and report distinguishing benchmark uplift, original-campaign effects, prediction, and feasible business decisions.

**Expected contribution.** The project will test whether causal ranking improves incremental conversion targeting beyond an average assignment rule or response prediction, and quantify how rare events, treatment imbalance, and release design constrain that conclusion. No positive advertising effect or profitable policy is assumed in advance.

### References

[1] Diemert, E., Betlei, A., Renaudin, C., Amini, M.-R., Gregoir, T., and Rahier, T. (2021). A large scale benchmark for individual treatment effect prediction and uplift modeling. [arXiv:2111.10106](https://arxiv.org/abs/2111.10106), Sections 3 and 5.

[2] Criteo. [Hugging Face dataset card and schema](https://huggingface.co/datasets/criteo/criteo-uplift). Accessed November 4, 2026.

[3] Criteo AI Lab. [Uplift dataset documentation and corrected-release erratum](https://ailab.criteo.com/criteo-uplift-prediction-dataset/). Accessed November 4, 2026.

[4] Supplied course notebooks 01-07, especially randomization, propensity scores, effect heterogeneity, and meta-learners.

[5] Kunzel, S. R., Sekhon, J. S., Bickel, P. J., and Yu, B. (2019). Metalearners for estimating heterogeneous treatment effects using machine learning. *PNAS*, 116(10), 4156-4165. [doi:10.1073/pnas.1804597116](https://doi.org/10.1073/pnas.1804597116).
