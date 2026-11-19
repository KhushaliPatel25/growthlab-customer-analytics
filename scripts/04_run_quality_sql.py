
from pathlib import Path
import duckdb

PROJECT_DIR = Path(__file__).resolve().parents[1]

DB_PATH = (
    PROJECT_DIR / "data" / "processed"
    / "growthlab.duckdb"
)

SQL_PATH = (
    PROJECT_DIR / "sql"
    / "01_quality_checks.sql"
)

print("=" * 55)
print("GROWTHLAB | SQL VALIDATION")
print("=" * 55)

con = duckdb.connect(str(DB_PATH), read_only=True)

# Read saved SQL file
sql_text = SQL_PATH.read_text(encoding="utf-8")

# Split the three SELECT statements
queries = [
    q.strip()
    for q in sql_text.split(";")
    if q.strip()
]

for i, query in enumerate(queries, start=1):

    print(f"\nSQL QUERY {i}")
    print("-" * 45)

    result = con.execute(query).df()

    print(result.to_string(index=False))

print("\nALL SQL QUALITY CHECKS COMPLETED")

con.close()
