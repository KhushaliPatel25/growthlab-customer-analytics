
from pathlib import Path
from collections import Counter
import csv
import gzip

# ----------------------------------
# 1. Set project folder locations
# ----------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"

# ----------------------------------
# 2. Define input datasets
# ----------------------------------

FILES = [
    "2019-Dec.csv.gz",
    "2020-Jan.csv.gz"
]

# ----------------------------------
# 3. Define required columns
# ----------------------------------

REQUIRED_COLUMNS = {
    "event_time",
    "event_type",
    "product_id",
    "category_id",
    "category_code",
    "brand",
    "price",
    "user_id",
    "user_session"
}

SAMPLE_SIZE = 10000

print("=" * 55)
print("GROWTHLAB | INITIAL DATA VERIFICATION")
print("=" * 55)

# ----------------------------------
# 4. Verify each dataset
# ----------------------------------

for filename in FILES:

    file_path = RAW_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing file: {file_path}"
        )

    event_counts = Counter()
    sample_rows = 0

    with gzip.open(
        file_path,
        mode="rt",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns

        if missing:
            raise ValueError(
                f"{filename} is missing: {sorted(missing)}"
            )

        for row in reader:

            event_counts[row["event_type"]] += 1
            sample_rows += 1

            if sample_rows >= SAMPLE_SIZE:
                break

    print(f"\nFile: {filename}")
    print("Status: PASSED")
    print(f"Sample rows checked: {sample_rows:,}")

    print(
        f"File size: "
        f"{file_path.stat().st_size / (1024**2):.1f} MB"
    )

    print("Sample event distribution:")

    for event, count in sorted(event_counts.items()):
        print(f"  {event}: {count:,}")

print("\nBoth files passed initial verification.")
print("Note: Counts above are from samples, not full data.")
