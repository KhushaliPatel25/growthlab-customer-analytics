
-- GROWTHLAB | RFM CUSTOMER SEGMENTATION
-- Snapshot date: 2020-02-01
-- Frequency = distinct purchase sessions
-- Uses customers with identifiable purchase sessions

WITH customer_purchases AS (

    SELECT
        user_id,

        DATE_DIFF(
            'day',
            CAST(MAX(event_time) AS DATE),
            DATE '2020-02-01'
        ) AS days_since_last_purchase,

        COUNT(DISTINCT user_session)
            AS purchase_sessions,

        COUNT(*) AS purchased_item_events,

        SUM(price) AS monetary_value

    FROM events_clean

    WHERE event_type = 'purchase'
      AND user_session IS NOT NULL

    GROUP BY user_id
),

rfm_scores AS (

    SELECT
        user_id,
        days_since_last_purchase,
        purchase_sessions,
        purchased_item_events,
        monetary_value,

        CASE
            WHEN days_since_last_purchase <= 7 THEN 5
            WHEN days_since_last_purchase <= 14 THEN 4
            WHEN days_since_last_purchase <= 30 THEN 3
            WHEN days_since_last_purchase <= 45 THEN 2
            ELSE 1
        END AS r_score,

        CASE
            WHEN purchase_sessions >= 5 THEN 5
            WHEN purchase_sessions = 4 THEN 4
            WHEN purchase_sessions = 3 THEN 3
            WHEN purchase_sessions = 2 THEN 2
            ELSE 1
        END AS f_score,

        NTILE(5) OVER (
            ORDER BY monetary_value ASC, user_id
        ) AS m_score

    FROM customer_purchases
),

customer_segments AS (

    SELECT
        *,

        CASE
            WHEN r_score >= 4
             AND f_score >= 4
             AND m_score >= 4
                THEN 'Champions'

            WHEN r_score >= 3
             AND f_score >= 3
                THEN 'Loyal Customers'

            WHEN r_score >= 4
             AND f_score <= 2
                THEN 'Promising Customers'

            WHEN r_score <= 2
             AND f_score >= 3
                THEN 'At Risk'

            WHEN r_score <= 2
             AND f_score <= 2
                THEN 'Hibernating'

            ELSE 'Other Buyers'
        END AS customer_segment

    FROM rfm_scores
)

SELECT
    customer_segment,

    COUNT(*) AS customers,

    ROUND(
        AVG(days_since_last_purchase), 1
    ) AS avg_days_since_purchase,

    ROUND(
        AVG(purchase_sessions), 2
    ) AS avg_purchase_sessions,

    ROUND(
        AVG(monetary_value), 2
    ) AS avg_purchase_value_per_customer,

    ROUND(
        SUM(monetary_value), 2
    ) AS recorded_purchase_value

FROM customer_segments

GROUP BY customer_segment

ORDER BY customers DESC;
