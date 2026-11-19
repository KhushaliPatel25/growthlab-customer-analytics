
# GrowthLab — A/B Testing Methodology

## Experiment Name

Simplified Checkout Experiment

## Experiment Type

Synthetic randomized A/B test.

This experiment was generated for the
purpose of demonstrating statistical
experimentation.

It is separate from the real REES46
e-commerce event dataset.

## Business Question

Would a redesigned checkout experience
improve visitor purchase conversion rates?

## Experiment Groups

Control:
Original checkout experience.

Treatment:
Simplified checkout experience.

## Experiment Design

Total simulated visitors: 40,000

Control: 20,000 visitors

Treatment: 20,000 visitors

Randomization:
Visitors are randomly assigned to one
of the two groups.

Random seed: 20261030

## Simulation Assumptions

Control conversion probability: 8.0%

Treatment conversion probability: 9.6%

These probabilities are predefined
simulation inputs, not observed company
conversion rates.

Visitor outcomes are generated using
independent Bernoulli trials.

## Primary Metric

Visitor-level purchase conversion rate.

Conversion rate equals converted
visitors divided by assigned visitors.

## Hypotheses

Null hypothesis:
Control and Treatment have equal
population conversion probabilities.

Alternative hypothesis:
The probabilities differ.

## Statistical Analysis

Test:
Two-sided two-proportion z-test.

Significance level: 0.05

Confidence level: 95%

The z-test uses a pooled proportion.

The difference confidence interval uses
an unpooled normal approximation.

Group-level intervals use Wilson scores.

## Additional Metrics

- Absolute uplift in percentage points
- Relative conversion uplift
- Z-statistic
- P-value
- Confidence interval

## Business Interpretation

A statistically significant positive
effect in the simulated dataset
demonstrates how a potential improvement
could be assessed.

It does not demonstrate that a real
checkout redesign would improve
business outcomes.

## Limitations

- Entirely simulated experiment data
- No actual customer exposure tracking
- No real implementation cost
- No real experiment duration
- No customer or device segmentation
- No observed revenue impact
- No multiple-testing analysis
- No real-world causal validation

## Reproducibility

1. Run 06_generate_ab_experiment.py
2. Run 07_analyze_ab_experiment.py
3. Review ab_test_results.md
4. Review Tableau CSV exports
5. Review ab_test_conversion.png

## Publication

Visitor-level synthetic records remain
in the locally ignored data folder.

Only clearly labeled synthetic summary
outputs, code, and visualizations will
be included in public documentation.
