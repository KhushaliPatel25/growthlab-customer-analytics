
# GrowthLab — Customer Analytics Methodology

## Project Overview

GrowthLab analyzes historical e-commerce
customer behavior using Python, DuckDB,
SQL, and Tableau.

## Observation Period

December 1, 2019 to January 31, 2020.

Source:
REES46 eCommerce Events History
in Cosmetics Shop.

## 1. Business KPIs

Active Users:
Distinct user IDs with valid events.

Purchasing Users:
Distinct users with purchase events.

Purchase Item Events:
Individual product purchase records.

Recorded Purchase Value:
Sum of price for purchase events.

Prices use the source dataset's units.
Currency is not independently verified.

## 2. Session Conversion Funnel

Session identity:
Combination of user_id and user_session.

Stages:
1. Session contains a product view.
2. Session contains both view and cart.
3. Session contains view, cart and purchase.

Stage membership does not require
chronological event ordering.

Sessions without identifiers are
excluded from the funnel.

Sessions spanning months are assigned
to the month of their first recorded event.

## 3. Retention Analysis

Cohort:
Month of the customer's first observed
purchase within the analysis period.

Retention:
Percentage of cohort buyers who
purchase in a later observed month.

Only December-to-January retention
can be measured with this dataset.

The first observed purchase is not
necessarily the first-ever purchase.

## 4. RFM Segmentation

Snapshot Date:
February 1, 2020.

Recency:
Days since the last recorded purchase.

Frequency:
Distinct identified purchase sessions.

Monetary:
Sum of recorded purchase-event prices.

Frequency excludes purchase records
without an identifiable session.

Recency and frequency use fixed
thresholds. Monetary scores use
five approximately equal-sized groups.

Customer segments are derived
analytical labels.

## 5. Purchase Trends

Daily recorded purchase value is
calculated by summing product prices
for purchase events on each date.

This is a transaction-event proxy,
not verified accounting revenue.

## 6. Category Performance

Product categories are ranked by
recorded purchase value.

Missing category codes are grouped
under Unclassified. In the two-month analysis,
Unclassified represents approximately 96.1%
of recorded purchase value. Rankings for
labeled categories exclude this group.

## 7. Privacy and Publishing

Original customer-level records and
the DuckDB database remain local.

Only reviewed aggregate CSV exports
are intended for Tableau publishing.

No user IDs or session identifiers
are included in public analytics exports.

## 8. Limitations

- Only two months of events are studied.
- Historical data may be incomplete.
- Purchases may contain multiple items.
- Sessions are not guaranteed to be orders.
- Price currency is not independently verified.
- Funnel stage presence is not causal attribution.
- The A/B test is separately simulated, not a real-world intervention.
