
-- GROWTHLAB | OVERALL BUSINESS KPIs
-- Source: cleaned e-commerce events

SELECT
    COUNT(*) AS total_events,

    COUNT(DISTINCT user_id) AS active_users,

    COUNT(*) FILTER (
        WHERE event_type = 'view'
    ) AS view_events,

    COUNT(*) FILTER (
        WHERE event_type = 'cart'
    ) AS cart_events,

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
    ) AS recorded_purchase_value,

    COUNT(*) FILTER (
        WHERE user_session IS NULL
    ) AS events_without_session

FROM events_clean;
