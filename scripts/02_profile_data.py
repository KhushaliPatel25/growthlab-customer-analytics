
from pathlib import Path
import duckdb

PROJECT_DIR = Path(__file__).resolve().parents[1]

DB_PATH = (
    PROJECT_DIR / "data" / "processed"
    / "growthlab.duckdb"
)

DOCS_DIR = PROJECT_DIR / "docs"
DOCS_DIR.mkdir(exist_ok=True)

print("=" * 55)
print("GROWTHLAB | DATA QUALITY PROFILE")
print("=" * 55)

con = duckdb.connect(str(DB_PATH), read_only=True)

# --------------------------------------
# 1. Profile missing and invalid values
# --------------------------------------

quality_query = """
SELECT
    source_file,
    COUNT(*) AS total_events,

    SUM(CASE WHEN event_time IS NULL
        THEN 1 ELSE 0 END) AS missing_time,

    SUM(CASE WHEN user_id IS NULL
        THEN 1 ELSE 0 END) AS missing_user,

    SUM(CASE WHEN product_id IS NULL
        THEN 1 ELSE 0 END) AS missing_product,

    SUM(CASE WHEN price IS NULL OR price < 0
        THEN 1 ELSE 0 END) AS invalid_price,

    SUM(CASE WHEN user_session IS NULL
        THEN 1 ELSE 0 END) AS missing_session,

    SUM(CASE WHEN brand IS NULL
        THEN 1 ELSE 0 END) AS missing_brand,

    SUM(CASE WHEN category_code IS NULL
        THEN 1 ELSE 0 END) AS missing_category,

    SUM(CASE
        WHEN event_type IS NULL
          OR event_type NOT IN (
            'view', 'cart',
            'remove_from_cart', 'purchase'
          )
        THEN 1 ELSE 0
    END) AS invalid_event_type,

    MIN(event_time) AS first_event,
    MAX(event_time) AS last_event

FROM events
GROUP BY source_file
ORDER BY source_file
"""

quality_df = con.execute(quality_query).df()

# --------------------------------------
# 2. Display quality report
# --------------------------------------

for _, row in quality_df.iterrows():

    print(f"\nSource: {row['source_file']}")
    print("-" * 45)

    fields = [
        ("Total events", "total_events"),
        ("Missing timestamps", "missing_time"),
        ("Missing users", "missing_user"),
        ("Missing products", "missing_product"),
        ("Invalid prices", "invalid_price"),
        ("Missing sessions", "missing_session"),
        ("Missing brands", "missing_brand"),
        ("Missing categories", "missing_category"),
        ("Invalid event types", "invalid_event_type")
    ]

    for label, key in fields:
        print(f"{label}: {int(row[key]):,}")

    print(f"First event: {row['first_event']}")
    print(f"Last event: {row['last_event']}")

# --------------------------------------
# 3. Analyze event type distribution
# --------------------------------------

event_query = """
SELECT
    source_file,
    event_type,
    COUNT(*) AS event_count
FROM events
GROUP BY source_file, event_type
ORDER BY source_file, event_count DESC
"""

event_df = con.execute(event_query).df()

print("\nEVENT TYPE DISTRIBUTION")
print(event_df.to_string(index=False))

# --------------------------------------
# 4. Export aggregate quality reports
# --------------------------------------

quality_df.to_csv(
    DOCS_DIR / "data_quality_summary.csv",
    index=False
)

event_df.to_csv(
    DOCS_DIR / "raw_event_distribution.csv",
    index=False
)

print("\nQuality reports saved in docs folder.")
print("DATA PROFILING COMPLETE")

con.close()
