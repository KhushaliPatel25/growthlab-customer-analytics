
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import norm

# -----------------------------------------
# GROWTHLAB | A/B TEST STATISTICAL ANALYSIS
# -----------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR / "data" / "processed"
    / "ab_experiment_visitors.csv"
)

EXPORT_DIR = PROJECT_DIR / "tableau" / "exports"
CHART_DIR = PROJECT_DIR / "assets" / "charts"
DOCS_DIR = PROJECT_DIR / "docs"

for folder in [EXPORT_DIR, CHART_DIR, DOCS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

ALPHA = 0.05
Z_CRITICAL = norm.ppf(1 - ALPHA / 2)

print("=" * 60)
print("GROWTHLAB | A/B TEST ANALYSIS")
print("=" * 60)
print("Experiment: Simplified Checkout")
print("Data type: SYNTHETIC / SIMULATED")

# -----------------------------------------
# 1. Load experiment data
# -----------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        "Experiment data missing. Run "
        "06_generate_ab_experiment.py first."
    )

df = pd.read_csv(INPUT_FILE)

required_columns = {
    "visitor_id", "variant", "converted"
}

if not required_columns.issubset(df.columns):
    raise ValueError("Missing required columns")

if df["visitor_id"].duplicated().any():
    raise ValueError("Duplicate visitor IDs found")

if df[list(required_columns)].isnull().any().any():
    raise ValueError("Missing experiment values found")

if set(df["variant"].unique()) != {
    "Control", "Treatment"
}:
    raise ValueError("Unexpected experiment variants")

if not df["converted"].isin([0, 1]).all():
    raise ValueError("Conversion values must be 0 or 1")

# -----------------------------------------
# 2. Calculate group-level metrics
# -----------------------------------------

summary = (
    df.groupby("variant", as_index=False)
    .agg(
        visitors=("converted", "size"),
        conversions=("converted", "sum")
    )
)

summary["conversion_rate"] = (
    summary["conversions"] / summary["visitors"]
)

control = summary.loc[
    summary["variant"] == "Control"
].iloc[0]

treatment = summary.loc[
    summary["variant"] == "Treatment"
].iloc[0]

n_c = int(control["visitors"])
n_t = int(treatment["visitors"])

x_c = int(control["conversions"])
x_t = int(treatment["conversions"])

p_c = x_c / n_c
p_t = x_t / n_t

# -----------------------------------------
# 3. Check traffic allocation
# -----------------------------------------

allocation_control = n_c / (n_c + n_t)
allocation_treatment = n_t / (n_c + n_t)

print("\nTRAFFIC ALLOCATION")
print("-" * 45)
print(f"Control: {allocation_control:.2%}")
print(f"Treatment: {allocation_treatment:.2%}")

if n_c != n_t:
    print("Note: Groups have unequal sample sizes.")

# -----------------------------------------
# 4. Absolute and relative uplift
# -----------------------------------------

absolute_difference = p_t - p_c

relative_uplift = (
    absolute_difference / p_c * 100
    if p_c > 0
    else float("nan")
)

# -----------------------------------------
# 5. Two-proportion z-test
# -----------------------------------------

pooled_rate = (x_c + x_t) / (n_c + n_t)

pooled_se = np.sqrt(
    pooled_rate
    * (1 - pooled_rate)
    * (1 / n_c + 1 / n_t)
)

if pooled_se == 0:
    raise ValueError(
        "Insufficient outcome variation "
        "for the z-test."
    )

z_statistic = absolute_difference / pooled_se

p_value = float(
    2 * norm.sf(abs(z_statistic))
)

# -----------------------------------------
# 6. Confidence interval for difference
# -----------------------------------------

# Unpooled normal approximation.
unpooled_se = np.sqrt(
    p_c * (1 - p_c) / n_c
    + p_t * (1 - p_t) / n_t
)

ci_lower = (
    absolute_difference - Z_CRITICAL * unpooled_se
)

ci_upper = (
    absolute_difference + Z_CRITICAL * unpooled_se
)

# -----------------------------------------
# 7. Confidence intervals for each group
# -----------------------------------------

# Wilson score intervals for group proportions.
def wilson_interval(conversions, visitors):
    rate = conversions / visitors
    z2 = Z_CRITICAL ** 2

    denominator = 1 + z2 / visitors

    center = (
        rate + z2 / (2 * visitors)
    ) / denominator

    margin = (
        Z_CRITICAL
        * np.sqrt(
            rate * (1 - rate) / visitors
            + z2 / (4 * visitors ** 2)
        )
        / denominator
    )

    return center - margin, center + margin


group_intervals = [
    wilson_interval(
        int(row["conversions"]),
        int(row["visitors"])
    )
    for _, row in summary.iterrows()
]

summary["ci_lower_pct"] = [
    lower * 100 for lower, _ in group_intervals
]

summary["ci_upper_pct"] = [
    upper * 100 for _, upper in group_intervals
]

summary["conversion_rate_pct"] = (
    summary["conversion_rate"] * 100
)

# -----------------------------------------
# 8. Statistical decision
# -----------------------------------------

significant = p_value < ALPHA

if significant and absolute_difference > 0:
    conclusion = (
        "Treatment has a statistically significant "
        "positive conversion-rate difference "
        "in the simulated sample."
    )
elif significant and absolute_difference < 0:
    conclusion = (
        "Treatment has a statistically significant "
        "negative conversion-rate difference "
        "in the simulated sample."
    )
else:
    conclusion = (
        "The simulated sample does not provide "
        "sufficient evidence of a difference "
        "at alpha = 0.05."
    )

# -----------------------------------------
# 9. Print results
# -----------------------------------------

print("\nCONVERSION RESULTS")
print("-" * 45)

print(f"Control visitors: {n_c:,}")
print(f"Control conversions: {x_c:,}")
print(f"Control conversion rate: {p_c:.2%}")

print(f"\nTreatment visitors: {n_t:,}")
print(f"Treatment conversions: {x_t:,}")
print(f"Treatment conversion rate: {p_t:.2%}")

print("\nSTATISTICAL RESULTS")
print("-" * 45)

print(
    f"Absolute uplift: "
    f"{absolute_difference * 100:.3f} percentage points"
)

print(f"Relative uplift: {relative_uplift:.2f}%")
print(f"Z-statistic: {z_statistic:.4f}")
print(f"P-value: {p_value:.8f}")

print(
    f"95% CI for difference: "
    f"[{ci_lower * 100:.3f}, "
    f"{ci_upper * 100:.3f}] percentage points"
)

print(f"Statistically significant: {significant}")
print(f"\nConclusion: {conclusion}")

# -----------------------------------------
# 10. Export summary for Tableau
# -----------------------------------------

summary_export = summary[
    [
        "variant",
        "visitors",
        "conversions",
        "conversion_rate_pct",
        "ci_lower_pct",
        "ci_upper_pct"
    ]
].copy()

summary_path = (
    EXPORT_DIR / "ab_test_summary.csv"
)

summary_export.to_csv(
    summary_path,
    index=False
)

# -----------------------------------------
# 11. Export statistical comparison
# -----------------------------------------

comparison = pd.DataFrame([{
    "experiment": "Simplified Checkout",
    "data_type": "Synthetic",
    "control_rate_pct": round(p_c * 100, 5),
    "treatment_rate_pct": round(p_t * 100, 5),
    "absolute_uplift_pp": round(
        absolute_difference * 100, 5
    ),
    "relative_uplift_pct": round(
        relative_uplift, 5
    ),
    "z_statistic": round(
        float(z_statistic), 6
    ),
    "p_value": p_value,
    "ci_lower_pp": round(ci_lower * 100, 5),
    "ci_upper_pp": round(ci_upper * 100, 5),
    "significant": significant,
    "alpha": ALPHA
}])

comparison.to_csv(
    EXPORT_DIR / "ab_test_comparison.csv",
    index=False
)

# -----------------------------------------
# 12. Create a conversion rate chart
# -----------------------------------------

fig, ax = plt.subplots(figsize=(9, 5.5))

chart_rates = summary_export[
    "conversion_rate_pct"
].to_numpy()

lower_errors = (
    chart_rates
    - summary_export["ci_lower_pct"].to_numpy()
)

upper_errors = (
    summary_export["ci_upper_pct"].to_numpy()
    - chart_rates
)

bars = ax.bar(
    summary_export["variant"],
    chart_rates,
    width=0.55,
    yerr=[lower_errors, upper_errors],
    capsize=7
)

for bar, rate in zip(bars, chart_rates):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.4,
        f"{rate:.2f}%",
        ha="center",
        fontsize=11,
        fontweight="bold"
    )

ax.set_title(
    "Simulated A/B Test | Checkout Conversion",
    fontsize=14,
    fontweight="bold",
    pad=15
)

ax.set_ylabel("Conversion Rate (%)")
ax.set_xlabel("Experiment Group")

ax.set_ylim(
    0,
    max(
        12,
        float(summary_export["ci_upper_pct"].max()) + 2
    )
)

ax.grid(axis="y", alpha=0.2)
ax.set_axisbelow(True)

fig.text(
    0.5, 0.015,
    "Synthetic data | Error bars: 95% Wilson intervals",
    ha="center",
    fontsize=9
)

fig.tight_layout(rect=[0, 0.04, 1, 1])

chart_path = (
    CHART_DIR / "ab_test_conversion.png"
)

fig.savefig(
    chart_path,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

# -----------------------------------------
# 13. Generate Markdown results document
# -----------------------------------------

report = f"""# GrowthLab — Simulated A/B Test Results

> **Synthetic experiment.**
> These results are not based on real customer
> experiment assignments.

## Experiment
Simplified Checkout

## Primary Metric
Visitor-level purchase conversion rate

## Group Results

| Group | Visitors | Conversions | Rate |
|---|---:|---:|---:|
| Control | {n_c:,} | {x_c:,} | {p_c:.2%} |
| Treatment | {n_t:,} | {x_t:,} | {p_t:.2%} |

## Statistical Test

- Test: Two-sided two-proportion z-test
- Significance threshold: {ALPHA}
- Z-statistic: {z_statistic:.4f}
- P-value: {p_value:.8f}
- Absolute difference: {absolute_difference * 100:.3f} percentage points
- Relative uplift: {relative_uplift:.2f}%
- 95% CI for difference: [{ci_lower * 100:.3f}, {ci_upper * 100:.3f}] percentage points

## Statistical Interpretation

{conclusion}

## Business Recommendation

Use this experiment as a demonstration of
statistical analysis and decision-making.

The data is simulated and does not justify
deploying a real checkout redesign.

A real experiment would require validated
event tracking, an appropriate sample-size
plan, guardrail metrics, and operational review.

## Limitations

- Simulated visitor outcomes
- Assumed conversion probabilities
- No observed customer behavior
- No real implementation costs
- No real experiment duration
- No device or market segmentation
- Large-sample confidence interval approximation
"""

report_path = DOCS_DIR / "ab_test_results.md"

report_path.write_text(
    report,
    encoding="utf-8"
)

# -----------------------------------------
# 14. Final execution summary
# -----------------------------------------

print("\nOUTPUT FILES")
print("-" * 45)

print(summary_path)
print(EXPORT_DIR / "ab_test_comparison.csv")
print(chart_path)
print(report_path)

print("\nA/B TEST ANALYSIS COMPLETE")
print("Statistical validation: PASSED")
print("Tableau exports: READY")
print("Data type: SYNTHETIC")
