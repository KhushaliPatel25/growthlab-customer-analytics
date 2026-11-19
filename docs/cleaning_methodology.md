
# GrowthLab — Data Cleaning Methodology

## Source Data

REES46 eCommerce Events History in Cosmetics Shop.

Analysis period:
December 2019 to January 2020.

## Ingestion

The original gzip-compressed CSV files are read
using DuckDB.

Raw text values are converted into appropriate
SQL data types using TRY_CAST.

Timestamps are interpreted as UTC.

## Data Quality

The pipeline checks for:

- Missing event timestamps
- Missing customer identifiers
- Missing product identifiers
- Missing or negative prices
- Missing session identifiers
- Missing brands and categories
- Invalid event types

## Cleaning Rules

The events_clean SQL view excludes events with:

- Missing timestamps
- Timestamps outside the analysis period
- Missing customer IDs
- Missing or nonpositive product IDs
- Missing or negative prices
- Unsupported event types

Missing optional brand, category, or session
values are retained.

## Duplicate Handling

Identical event records are not automatically
removed because the source lacks a unique
event identifier.

## Analytical Considerations

Each source record represents a product event.

Multiple purchase events may belong to the
same shopping session.

Missing session identifiers are excluded from
session-level metrics when required.

## Reproducibility

Run scripts in order:

1. 00_verify_data.py
2. 01_ingest_data.py
3. 02_profile_data.py
4. 03_clean_data.py
5. 04_run_quality_sql.py

## Privacy

Raw data and local databases remain excluded
from the public GitHub repository.

Only reviewed aggregate reports are intended
for publication.
