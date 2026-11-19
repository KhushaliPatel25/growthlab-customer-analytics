
from pathlib import Path
import duckdb

PROJECT_DIR = Path(__file__).resolve().parents[1]

DB_PATH = (
    PROJECT_DIR / "data" / "processed"
    / "growthlab.duckdb"
)

DOCS_DIR = PROJECT_DIR / "docs"

print("=" * 55)
print("GROWTHLAB | DATA CLEANING")
print("=" * 55)

con = duckdb.connect(str(DB_PATH))

# --------------------------------------
# 1. Create a reusable cleaned view
# --------------------------------------

con.execute("""
CREATE OR REPLACE VIEW events_clean AS

SELECT
    event_time,

    CAST(event_time AS DATE)
        AS event_date,

    CAST(
        DATE_TRUNC('month', event_time)
        AS DATE
    ) AS event_month,

    event_type,
    product_id,
    category_id,
    category_code,
    brand,
    price,
    user_id,
    user_session,
    source_file

FROM events

WHERE
    event_time IS NOT NULL
    AND event_time >= TIMESTAMP '2019-12-01'
    AND event_time < TIMESTAMP '2020-02-01'

    AND user_id IS NOT NULL

    AND product_id IS NOT NULL
    AND product_id > 0

    AND price IS NOT NULL
    AND price >= 0

    AND event_type IN (
        'view',
        'cart',
        'remove_from_cart',
        'purchase'
    )
""")

print("\nCleaned view created: events_clean")

# --------------------------------------
# 2. Compare original vs cleaned rows
# --------------------------------------

raw_count = con.execute(
    "SELECT COUNT(*) FROM events"
).fetchone()[0]

clean_count = con.execute(
    "SELECT COUNT(*) FROM events_clean"
).fetchone()[0]

excluded_count = raw_count - clean_count

retention_pct = (
    clean_count / raw_count * 100
    if raw_count else 0
)

print("\nDATA CLEANING SUMMARY")
print("-" * 45)

print(f"Original events: {raw_count:,}")
print(f"Cleaned events: {clean_count:,}")
print(f"Excluded events: {excluded_count:,}")
print(f"Events retained: {retention_pct:.2f}%")

# --------------------------------------
# 3. Monthly cleaned event counts
# --------------------------------------

monthly_query = """
SELECT
    event_month,
    event_type,
    COUNT(*) AS event_count

FROM events_clean

GROUP BY event_month, event_type
ORDER BY event_month, event_type
"""

monthly_df = con.execute(monthly_query).df()

print("\nCLEANED MONTHLY EVENT SUMMARY")
print(monthly_df.to_string(index=False))

# --------------------------------------
# 4. Export aggregate results
# --------------------------------------

monthly_df.to_csv(
    DOCS_DIR / "clean_events_by_month.csv",
    index=False
)

print("\nCleaned summary exported.")
print("DATA CLEANING COMPLETE")

con.close()
