# Final project proposals

This folder contains four alternative proposals, each four pages. The IHDP proposal has no reference list or numbered citations, as requested; the alternatives retain their references.

| Dataset | Proposal PDF | Editable source |
| --- | --- | --- |
| IHDP | `final_project_proposal.pdf` | `proposal.md` |
| Twins | `twins_proposal.pdf` | `twins_proposal.md` |
| Lalonde / NSW + CPS | `lalonde_proposal.pdf` | `lalonde_proposal.md` |
| Criteo Uplift v2 | `criteo_proposal.pdf` | `criteo_proposal.md` |

Each alternative follows the same five assignment sections and is a proposal rather than a completed empirical analysis. No data downloads, effect estimates, or fitted models are included. The course notebooks are methodological references.

- **Twins:** a pair-level selective-observation benchmark, with regression standardization, weighting, and doubly robust estimation. Recovery of a paired mortality contrast is distinguished from identifying a biological birthweight intervention effect.
- **Lalonde:** trainee ATT estimation using NSW trainees and CPS controls, evaluated against a separate experimental NSW comparison with uncertainty and shared-trainee dependence accounted for.
- **Criteo:** assignment effects and T-/X-learner uplift evaluation using the corrected public release, with explicit limits from privacy sampling and a distinction between eligibility and actual exposure.

## IHDP proposal

The original deliverable is `final_project_proposal.pdf`, a four-page proposal for a causal analysis of the public IHDP semi-synthetic benchmark. It follows all five assignment sections. Its latest rewrite uses chapters 1-7 of Matheus Facure's *Causal Inference in Python*, supplied as a local PDF, while preserving the requested removal of formal references.

The primary target is the average treatment effect on the treated (ATT). The core average-effect methods are regression adjustment, ATT inverse probability weighting, and doubly robust ATT estimation. A treatment-interaction regression and T- and X-learners address secondary effect-heterogeneity questions. The target avoids relying on treatment-effect extrapolation into a subgroup removed from the benchmark's treated arm; control support for treated infants must still be verified.

This is a proposal, not a completed empirical analysis. It contains no claimed treatment-effect estimates or analysis results.

### How the rewrite uses chapters 1-7

| Chapter | Application in the IHDP proposal |
| --- | --- |
| 1. Introduction to Causal Inference | Potential outcomes, ATT versus ATE, association versus causation, consistency, and no interference. |
| 2. Randomized Experiments and Stats Review | Separate identification from estimation; qualify the selected benchmark's randomized origin; report confidence intervals, precision, and sampling uncertainty. |
| 3. Graphical Causal Models | Working DAG, conditional independence, baseline adjustment, avoiding mediators and colliders, and positivity for the chosen target. |
| 4. The Unreasonable Effectiveness of Linear Regression | Untreated-outcome imputation for ATT, Frisch-Waugh-Lovell interpretation, extrapolation, and distinguishing a regression coefficient from the recipient average under heterogeneity. |
| 5. Propensity Score | Logistic propensities, recipient-targeted odds weights, weight instability, design versus outcome modeling, and an ATT adaptation of doubly robust estimation. |
| 6. Effect Heterogeneity | Treatment interactions, distinguishing response prediction from effect prediction, held-out effect groups, and cumulative-benefit ordering. |
| 7. Metalearners | T- and X-learners, unequal-group regularization, two-stage imputation, and out-of-fold estimation. |

The chapter methods are adapted to IHDP's binary treatment and recipient target. The proposed weighting and doubly robust formulas target ATT rather than copying population ATE formulas. The book's raw group-effect validation examples use randomized evaluation data; the proposal instead uses the benchmark conditional means on held-out recipients, avoiding unadjusted validation in observational score groups. Later-chapter panel and instrumental-variable methods are outside this proposal's scope.

## Files

- `final_project_proposal.pdf`: submission-ready proposal.
- `proposal.md`: editable proposal text, with explicit page breaks.
- `build_proposal.py`: reproducible PDF generator; reads `proposal.md`.
- `requirements.txt`: PDF-generation and verification dependencies.

## Rebuild

From this directory, using an environment with the listed requirements installed:

```bash
python3 build_proposal.py
```

Rebuild an alternative with its own source and dataset label:

```bash
python3 build_proposal.py --source twins_proposal.md --output twins_proposal.pdf --dataset Twins --date 'November 4, 2026'
python3 build_proposal.py --source lalonde_proposal.md --output lalonde_proposal.pdf --dataset Lalonde --date 'November 4, 2026'
python3 build_proposal.py --source criteo_proposal.md --output criteo_proposal.pdf --dataset Criteo --date 'November 4, 2026'
```

The generator uses Georgia and Arial when available on macOS, otherwise standard PDF fonts. It verifies that the output contains four pages. For visual review, render with Poppler:

```bash
pdftoppm -r 120 -png final_project_proposal.pdf /tmp/final-project-proposal
```

Alternatively, PyMuPDF can render the PDF if Poppler is unavailable. No dataset download or model fitting is performed by the PDF generator. Future analysis should record the data revision, checksums, environment, and fixed splits, and keep oracle columns separate from fitting and tuning.
