
-- GROWTHLAB | DAILY PURCHASE TRENDS

SELECT
    event_date,

    COUNT(*) AS total_events,

    COUNT(DISTINCT user_id)
        AS active_users,

    COUNT(*) FILTER (
        WHERE event_type = 'purchase'
    ) AS purchase_item_events,

    COUNT(DISTINCT user_id) FILTER (
        WHERE event_type = 'purchase'
    ) AS purchasing_users,

    ROUND(
        COALESCE(
            SUM(price) FILTER (
                WHERE event_type = 'purchase'
            ), 0
        ), 2
    ) AS recorded_purchase_value

FROM events_clean

GROUP BY event_date

ORDER BY event_date;
