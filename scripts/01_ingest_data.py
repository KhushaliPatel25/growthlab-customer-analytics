
from pathlib import Path
import duckdb

# --------------------------------------
# 1. Project paths
# --------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = PROCESSED_DIR / "growthlab.duckdb"

FILES = [
    "2019-Dec.csv.gz",
    "2020-Jan.csv.gz"
]

# --------------------------------------
# 2. Connect to DuckDB
# --------------------------------------

print("=" * 55)
print("GROWTHLAB | DATA INGESTION")
print("=" * 55)

print(f"\nDatabase: {DB_PATH}")

con = duckdb.connect(str(DB_PATH))

# Limit parallel threads for laptop use
con.execute("SET threads = 2")

# --------------------------------------
# 3. Create structured events table
# --------------------------------------

# Re-running resets the imported events.
con.execute("DROP VIEW IF EXISTS events_clean")
con.execute("DROP TABLE IF EXISTS events")

con.execute("""
CREATE TABLE events (
    event_time TIMESTAMP,
    event_type VARCHAR,
    product_id BIGINT,
    category_id BIGINT,
    category_code VARCHAR,
    brand VARCHAR,
    price DOUBLE,
    user_id BIGINT,
    user_session VARCHAR,
    source_file VARCHAR
)
""")

print("\nEvents table created.")

# --------------------------------------
# 4. Import both monthly datasets
# --------------------------------------

for filename in FILES:

    file_path = RAW_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    # Windows-safe SQL file path
    csv_path = file_path.as_posix().replace("'", "''")

    print(f"\nImporting {filename}...", flush=True)

    con.execute(f"""
    INSERT INTO events
    SELECT
        TRY_CAST(
            REPLACE(
                NULLIF(TRIM(event_time), ''),
                ' UTC',
                ''
            ) AS TIMESTAMP
        ),

        NULLIF(LOWER(TRIM(event_type)), ''),

        TRY_CAST(
            NULLIF(TRIM(product_id), '')
            AS BIGINT
        ),

        TRY_CAST(
            NULLIF(TRIM(category_id), '')
            AS BIGINT
        ),

        NULLIF(TRIM(category_code), ''),

        NULLIF(TRIM(brand), ''),

        TRY_CAST(
            NULLIF(TRIM(price), '')
            AS DOUBLE
        ),

        TRY_CAST(
            NULLIF(TRIM(user_id), '')
            AS BIGINT
        ),

        NULLIF(TRIM(user_session), ''),

        '{filename}'

    FROM read_csv(
        '{csv_path}',
        header = true,
        all_varchar = true
    )
    """)

    count = con.execute(
        """
        SELECT COUNT(*)
        FROM events
        WHERE source_file = ?
        """,
        [filename]
    ).fetchone()[0]

    print(
        f"Successfully imported: {count:,} events",
        flush=True
    )

# --------------------------------------
# 5. Verify combined database
# --------------------------------------

total = con.execute(
    "SELECT COUNT(*) FROM events"
).fetchone()[0]

print("\n" + "=" * 55)
print("DATABASE INGESTION COMPLETE")
print("=" * 55)

print(f"Total imported events: {total:,}")
print("Database table: events")
print("Status: SUCCESS")

con.close()
