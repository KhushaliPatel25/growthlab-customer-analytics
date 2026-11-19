
from pathlib import Path
import argparse
import duckdb

# ----------------------------------------
# 1. Set project paths
# ----------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

DB_PATH = (
    PROJECT_DIR / "data" / "processed"
    / "growthlab.duckdb"
)

SQL_DIR = PROJECT_DIR / "sql"

EXPORT_DIR = (
    PROJECT_DIR / "tableau" / "exports"
)

# ----------------------------------------
# 2. Register SQL analyses
# ----------------------------------------

REPORTS = {
    "kpi": (
        "02_kpi_overview.sql",
        "kpi_overview.csv"
    ),
    "funnel": (
        "03_conversion_funnel.sql",
        "conversion_funnel.csv"
    ),
    "cohorts": (
        "04_retention_cohorts.sql",
        "retention_cohorts.csv"
    ),
    "rfm": (
        "05_rfm_segments.sql",
        "rfm_segments.csv"
    ),
    "daily": (
        "06_daily_revenue.sql",
        "daily_revenue.csv"
    ),
    "category": (
        "07_category_performance.sql",
        "category_performance.csv"
    )
}

# ----------------------------------------
# 3. Optional command-line selection
# ----------------------------------------

parser = argparse.ArgumentParser(
    description="Run GrowthLab SQL analytics"
)

parser.add_argument(
    "--only",
    choices=list(REPORTS.keys()),
    default=None,
    help="Run only one analysis"
)

args = parser.parse_args()

selected = (
    [args.only]
    if args.only
    else list(REPORTS.keys())
)

# ----------------------------------------
# 4. Check database and folders
# ----------------------------------------

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"GrowthLab database not found: {DB_PATH}"
    )

EXPORT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("GROWTHLAB | CUSTOMER ANALYTICS")
print("=" * 60)

con = duckdb.connect(
    str(DB_PATH),
    read_only=True
)

results = {}

try:
    # Confirm that Phase 2 was completed
    con.execute(
        "SELECT 1 FROM events_clean LIMIT 1"
    )

    # ------------------------------------
    # 5. Execute selected SQL files
    # ------------------------------------

    for name in selected:

        sql_filename, csv_filename = REPORTS[name]

        sql_path = SQL_DIR / sql_filename
        csv_path = EXPORT_DIR / csv_filename

        if not sql_path.exists():
            raise FileNotFoundError(
                f"Missing SQL file: {sql_path}"
            )

        print(f"\nRunning: {name.upper()}", flush=True)
        print("-" * 60)

        query = sql_path.read_text(
            encoding="utf-8"
        )

        df = con.execute(query).df()

        if df.empty:
            raise ValueError(
                f"No data returned for {name}"
            )

        # Never publish customer-level identifiers
        forbidden = {
            "user_id",
            "user_session",
            "product_id"
        }

        if forbidden.intersection(df.columns):
            raise ValueError(
                "Unsafe identifier found in export"
            )

        # Validate funnel stage counts
        if name == "funnel":

            for _, group in df.groupby(
                "session_month"
            ):

                counts = (
                    group.sort_values("stage_number")
                    ["sessions"].tolist()
                )

                if counts != sorted(
                    counts, reverse=True
                ):
                    raise ValueError(
                        "Funnel counts are not decreasing"
                    )

        # Validate retention percentages
        if name == "cohorts":

            invalid = (
                (df["retention_pct"] < 0) |
                (df["retention_pct"] > 100)
            )

            if invalid.any():
                raise ValueError(
                    "Invalid retention percentage"
                )

        # Save only reviewed aggregate outputs
        df.to_csv(
            csv_path,
            index=False
        )

        results[name] = df

        print(df.head(12).to_string(index=False))

        print(f"\nRows exported: {len(df):,}")
        print(f"Saved to: {csv_path.name}")
        print("Status: SUCCESS")

    # ------------------------------------
    # 6. Cross-check purchase totals
    # ------------------------------------

    if "kpi" in results and "daily" in results:

        kpi_value = float(
            results["kpi"].iloc[0][
                "recorded_purchase_value"
            ]
        )

        daily_value = float(
            results["daily"][
                "recorded_purchase_value"
            ].sum()
        )

        # Small differences can arise from
        # rounding values by day.
        if abs(kpi_value - daily_value) > 1.0:
            raise ValueError(
                "Daily purchase totals do not "
                "match the overall KPI total"
            )

        print(
            "\nRevenue consistency check: PASSED"
        )

    print("\n" + "=" * 60)
    print("GROWTHLAB ANALYTICS COMPLETE")
    print("=" * 60)

    print(
        f"Successful analyses: {len(results)}"
    )

    print(
        "Tableau CSV exports are available."
    )

finally:
    con.close()
