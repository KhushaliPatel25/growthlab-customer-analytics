
-- GROWTHLAB | CUSTOMER CONVERSION FUNNEL
-- Session-based, stage-presence funnel.
-- Does not require strict chronological order.

WITH session_flags AS (

    SELECT
        user_id,
        user_session,

        CAST(
            DATE_TRUNC('month', MIN(event_time))
            AS DATE
        ) AS session_month,

        MAX(CASE
            WHEN event_type = 'view'
            THEN 1 ELSE 0
        END) AS has_view,

        MAX(CASE
            WHEN event_type = 'cart'
            THEN 1 ELSE 0
        END) AS has_cart,

        MAX(CASE
            WHEN event_type = 'purchase'
            THEN 1 ELSE 0
        END) AS has_purchase

    FROM events_clean

    WHERE user_session IS NOT NULL

    GROUP BY user_id, user_session
),

monthly_counts AS (

    SELECT
        session_month,

        COUNT(*) AS total_sessions,

        SUM(has_view) AS viewed_sessions,

        SUM(CASE
            WHEN has_view = 1
             AND has_cart = 1
            THEN 1 ELSE 0
        END) AS viewed_cart_sessions,

        SUM(CASE
            WHEN has_view = 1
             AND has_cart = 1
             AND has_purchase = 1
            THEN 1 ELSE 0
        END) AS completed_funnel_sessions

    FROM session_flags

    GROUP BY session_month
),

funnel_stages AS (

    SELECT
        session_month,
        total_sessions,
        1 AS stage_number,
        'Viewed Product' AS stage,
        viewed_sessions AS sessions

    FROM monthly_counts

    UNION ALL

    SELECT
        session_month,
        total_sessions,
        2,
        'Viewed + Cart',
        viewed_cart_sessions

    FROM monthly_counts

    UNION ALL

    SELECT
        session_month,
        total_sessions,
        3,
        'Viewed + Cart + Purchased',
        completed_funnel_sessions

    FROM monthly_counts
)

SELECT
    session_month,
    stage_number,
    stage,
    sessions,
    total_sessions,

    ROUND(
        100.0 * sessions /
        NULLIF(
            FIRST_VALUE(sessions) OVER (
                PARTITION BY session_month
                ORDER BY stage_number
            ), 0
        ), 2
    ) AS pct_of_view_sessions,

    ROUND(
        100.0 * sessions /
        NULLIF(
            LAG(sessions) OVER (
                PARTITION BY session_month
                ORDER BY stage_number
            ), 0
        ), 2
    ) AS pct_from_previous_stage

FROM funnel_stages

ORDER BY session_month, stage_number;
