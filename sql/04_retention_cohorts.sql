
-- GROWTHLAB | PURCHASER RETENTION COHORTS
-- First observed purchase within Dec 2019-Jan 2020.
-- Only two months of observation are available.

WITH monthly_buyers AS (

    SELECT DISTINCT
        user_id,
        event_month

    FROM events_clean

    WHERE event_type = 'purchase'
),

first_purchase_cohort AS (

    SELECT
        user_id,

        MIN(event_month) AS cohort_month

    FROM monthly_buyers

    GROUP BY user_id
),

cohort_sizes AS (

    SELECT
        cohort_month,
        COUNT(*) AS cohort_buyers

    FROM first_purchase_cohort

    GROUP BY cohort_month
),

retained_buyers AS (

    SELECT
        c.cohort_month,

        DATE_DIFF(
            'month',
            c.cohort_month,
            m.event_month
        ) AS months_since_first_purchase,

        COUNT(DISTINCT m.user_id)
            AS retained_buyers

    FROM first_purchase_cohort c

    JOIN monthly_buyers m
        ON c.user_id = m.user_id

    GROUP BY
        c.cohort_month,
        months_since_first_purchase
)

SELECT
    r.cohort_month,

    r.months_since_first_purchase,

    s.cohort_buyers,

    r.retained_buyers,

    ROUND(
        100.0 * r.retained_buyers /
        NULLIF(s.cohort_buyers, 0),
        2
    ) AS retention_pct

FROM retained_buyers r

JOIN cohort_sizes s
    ON r.cohort_month = s.cohort_month

ORDER BY
    r.cohort_month,
    r.months_since_first_purchase;
