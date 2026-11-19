
-- GROWTHLAB | PRODUCT CATEGORY PERFORMANCE
-- Show the top 15 categories with at least
-- 30 recorded purchase-item events.

SELECT
    COALESCE(
        category_code,
        'Unclassified'
    ) AS category,

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

GROUP BY 1

HAVING COUNT(*) FILTER (
    WHERE event_type = 'purchase'
) >= 30

ORDER BY recorded_purchase_value DESC

LIMIT 15;
