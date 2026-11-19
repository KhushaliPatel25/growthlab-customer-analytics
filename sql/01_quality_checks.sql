
-- =======================================
-- GROWTHLAB: DATA QUALITY VALIDATION
-- =======================================

-- Query 1: Overall cleaned data summary

SELECT
    COUNT(*) AS cleaned_events,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(DISTINCT user_session) AS sessions_with_id,
    MIN(event_time) AS first_event_utc,
    MAX(event_time) AS last_event_utc

FROM events_clean;


-- Query 2: Monthly event distribution

SELECT
    event_month,
    event_type,
    COUNT(*) AS total_events

FROM events_clean

GROUP BY
    event_month,
    event_type

ORDER BY
    event_month,
    event_type;


-- Query 3: Daily activity validation

SELECT
    event_date,
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS unique_users

FROM events_clean

GROUP BY event_date

ORDER BY event_date

LIMIT 10;
