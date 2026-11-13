-- =====================================================================
-- fct_order_attribution.sql
-- ---------------------------------------------------------------------
-- Description:
-- Multi-touch marketing attribution model at the order-touchpoint level.
-- Evaluates four attribution credit models:
--   1. First-Touch Attribution (Top of Funnel - 100% credit to first touch)
--   2. Last-Touch Attribution (Bottom of Funnel - 100% credit to last touch)
--   3. Linear Attribution (Equal split across all preceding touchpoints)
--   4. Time-Decay Attribution (7-day half-life exponential decay)
--
-- Note: Uses simulated customer identity mapping and synthetic CRM orders
-- for demonstration and learning purposes.
-- =====================================================================

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

sessions AS (
    SELECT * FROM {{ ref('int_customer_sessions') }}
),

-- Step 1: Match orders with customer sessions that occurred on or before the order date
order_touchpoint_candidates AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        o.order_amount,
        s.ga_session_id,
        s.session_start_time,
        s.traffic_source,
        s.traffic_medium,
        s.campaign_name,
        -- Number of days prior to order (minimum 0 days)
        DATE_DIFF(o.order_date, DATE(s.session_start_time), DAY) AS days_prior
    FROM
        orders o
    LEFT JOIN
        sessions s ON o.customer_id = s.customer_id 
                  AND DATE(s.session_start_time) <= o.order_date
),

-- Step 2A: Attribution calculation for orders with matched web sessions
matched_orders AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        order_amount,
        traffic_source,
        traffic_medium,
        campaign_name,
        session_start_time,
        
        -- Chronological touchpoint sequence for this specific order
        ROW_NUMBER() OVER (
            PARTITION BY order_id 
            ORDER BY session_start_time ASC, ga_session_id ASC
        ) AS touchpoint_rank,

        COUNT(1) OVER (
            PARTITION BY order_id
        ) AS total_touchpoints,

        -- Time-decay raw exponential weight using 7-day half-life: 2 ^ (-days_prior / 7)
        POWER(2.0, -1.0 * (days_prior / 7.0)) AS raw_decay_weight

    FROM
        order_touchpoint_candidates
    WHERE
        ga_session_id IS NOT NULL
),

matched_with_decay_sum AS (
    SELECT
        *,
        -- Sum of decay weights per order for normalization
        SUM(raw_decay_weight) OVER (PARTITION BY order_id) AS sum_order_decay_weights
    FROM
        matched_orders
),

matched_attributed AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        order_amount,
        traffic_source,
        traffic_medium,
        campaign_name,
        touchpoint_rank,
        total_touchpoints,

        -- 1. First-Touch Attribution: 100% to rank 1, 0 otherwise
        IF(touchpoint_rank = 1, 1.0, 0.0) AS first_touch_credit,

        -- 2. Last-Touch Attribution: 100% to final rank, 0 otherwise
        IF(touchpoint_rank = total_touchpoints, 1.0, 0.0) AS last_touch_credit,

        -- 3. Linear Attribution: Equal credit across all touchpoints
        ROUND(1.0 / total_touchpoints, 6) AS linear_credit,

        -- 4. Time-Decay Attribution: Normalized weight summing to 1.0 per order
        ROUND(raw_decay_weight / sum_order_decay_weights, 6) AS time_decay_credit

    FROM
        matched_with_decay_sum
),

-- Step 2B: Unmatched orders (no prior sessions recorded for customer)
-- Labeled as 'Direct' / 'Unattributed' with 100% credit
unmatched_attributed AS (
    SELECT DISTINCT
        order_id,
        customer_id,
        order_date,
        order_amount,
        'Direct' AS traffic_source,
        '(none)' AS traffic_medium,
        'Unattributed' AS campaign_name,
        1 AS touchpoint_rank,
        1 AS total_touchpoints,
        1.0 AS first_touch_credit,
        1.0 AS last_touch_credit,
        1.0 AS linear_credit,
        1.0 AS time_decay_credit
    FROM
        order_touchpoint_candidates
    WHERE
        ga_session_id IS NULL
),

-- Step 3: Combine attributed matched orders with direct/unattributed orders
combined_attribution AS (
    SELECT * FROM matched_attributed
    UNION ALL
    SELECT * FROM unmatched_attributed
)

SELECT
    order_id,
    customer_id,
    order_date,
    order_amount,
    traffic_source,
    traffic_medium,
    campaign_name,
    touchpoint_rank,
    total_touchpoints,
    first_touch_credit,
    last_touch_credit,
    linear_credit,
    time_decay_credit
FROM
    combined_attribution
ORDER BY
    order_id ASC,
    touchpoint_rank ASC

