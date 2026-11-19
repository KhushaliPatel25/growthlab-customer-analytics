
from pathlib import Path
import numpy as np
import pandas as pd

# -----------------------------------------
# GROWTHLAB | SIMULATED A/B EXPERIMENT
# -----------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "ab_experiment_visitors.csv"

# -----------------------------------------
# 1. Experiment configuration
# -----------------------------------------

RANDOM_SEED = 20261030

VISITORS_PER_GROUP = 20000

CONTROL_PROBABILITY = 0.080
TREATMENT_PROBABILITY = 0.096

TOTAL_VISITORS = VISITORS_PER_GROUP * 2

rng = np.random.default_rng(RANDOM_SEED)

print("=" * 60)
print("GROWTHLAB | A/B TEST SIMULATION")
print("=" * 60)

print("\nExperiment: Simplified Checkout")
print("Data type: SYNTHETIC / SIMULATED")
print(f"Random seed: {RANDOM_SEED}")

# -----------------------------------------
# 2. Assign visitors to experiment groups
# -----------------------------------------

variants = np.array(
    ["Control"] * VISITORS_PER_GROUP
    + ["Treatment"] * VISITORS_PER_GROUP
)

# Randomly shuffle group assignments
rng.shuffle(variants)

# -----------------------------------------
# 3. Assign conversion probabilities
# -----------------------------------------

probabilities = np.where(
    variants == "Control",
    CONTROL_PROBABILITY,
    TREATMENT_PROBABILITY
)

# -----------------------------------------
# 4. Generate binary conversion outcomes
# -----------------------------------------

converted = rng.binomial(
    n=1,
    p=probabilities
)

# -----------------------------------------
# 5. Build visitor-level dataset
# -----------------------------------------

df = pd.DataFrame({
    "visitor_id": np.arange(
        1, TOTAL_VISITORS + 1
    ),
    "variant": variants,
    "converted": converted
})

# -----------------------------------------
# 6. Validate experiment design
# -----------------------------------------

assert len(df) == TOTAL_VISITORS

assert df["visitor_id"].is_unique

assert set(df["variant"].unique()) == {
    "Control", "Treatment"
}

assert set(df["converted"].unique()).issubset({
    0, 1
})

group_counts = df["variant"].value_counts()

assert group_counts["Control"] == VISITORS_PER_GROUP
assert group_counts["Treatment"] == VISITORS_PER_GROUP

# -----------------------------------------
# 7. Save synthetic data locally
# -----------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

# -----------------------------------------
# 8. Print verification results
# -----------------------------------------

print("\nEXPERIMENT CONFIGURATION")
print("-" * 45)

print(f"Total visitors: {TOTAL_VISITORS:,}")
print(f"Control visitors: {group_counts['Control']:,}")
print(f"Treatment visitors: {group_counts['Treatment']:,}")

print(f"\nAssumed control rate: {CONTROL_PROBABILITY:.2%}")
print(f"Assumed treatment rate: {TREATMENT_PROBABILITY:.2%}")

print("\nDATASET PREVIEW")
print(df.head(10).to_string(index=False))

print("\nOUTPUT FILE")
print(OUTPUT_FILE)

print("\nSIMULATION COMPLETE")
print("Randomization checks: PASSED")
print("Data type: SYNTHETIC")
