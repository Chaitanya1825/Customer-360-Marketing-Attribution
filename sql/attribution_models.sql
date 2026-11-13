-- =====================================================================
-- attribution_models.sql
-- ---------------------------------------------------------------------
-- Description:
-- Demonstrates First-Touch and Last-Touch marketing attribution by
-- joining GA4 web sessions to CRM orders through identity resolution.
-- =====================================================================

WITH customer_sessions AS (
  -- Step 1: Link GA4 sessions to CRM customer IDs via identity_mapping
  SELECT
    m.customer_id,
    s.user_pseudo_id,
    s.ga_session_id,
    s.session_start_time,
    s.traffic_source,
    s.traffic_medium,
    s.campaign_name,
    
    -- Rank sessions chronologically per customer
    ROW_NUMBER() OVER (
      PARTITION BY m.customer_id 
      ORDER BY s.session_start_time ASC
    ) AS touchpoint_rank_asc,  -- 1 = First Touch
    
    ROW_NUMBER() OVER (
      PARTITION BY m.customer_id 
      ORDER BY s.session_start_time DESC
    ) AS touchpoint_rank_desc  -- 1 = Last Touch

  FROM
    identity_mapping m
  INNER JOIN
    ga4_sessions s ON m.user_pseudo_id = s.user_pseudo_id
),

customer_revenue AS (
  -- Step 2: Calculate total revenue per customer from orders
  SELECT
    customer_id,
    ROUND(SUM(order_amount), 2) AS total_revenue,
    COUNT(order_id) AS total_orders
  FROM
    orders
  GROUP BY
    customer_id
),

first_touch AS (
  -- Step 3: Extract First-Touch Channel for each customer
  SELECT
    cs.customer_id,
    cs.traffic_source AS first_touch_source,
    cs.traffic_medium AS first_touch_medium,
    cs.session_start_time AS first_touch_time,
    COALESCE(cr.total_revenue, 0.0) AS attributed_revenue
  FROM
    customer_sessions cs
  LEFT JOIN
    customer_revenue cr ON cs.customer_id = cr.customer_id
  WHERE
    cs.touchpoint_rank_asc = 1
),

last_touch AS (
  -- Step 4: Extract Last-Touch Channel for each customer
  SELECT
    cs.customer_id,
    cs.traffic_source AS last_touch_source,
    cs.traffic_medium AS last_touch_medium,
    cs.session_start_time AS last_touch_time,
    COALESCE(cr.total_revenue, 0.0) AS attributed_revenue
  FROM
    customer_sessions cs
  LEFT JOIN
    customer_revenue cr ON cs.customer_id = cr.customer_id
  WHERE
    cs.touchpoint_rank_desc = 1
)

-- Step 5: Summary comparison of First-Touch vs Last-Touch attributed revenue by channel
SELECT
  COALESCE(ft.first_touch_source, lt.last_touch_source) AS marketing_channel,
  
  -- First-Touch Metrics
  COUNT(DISTINCT ft.customer_id) AS first_touch_customers,
  ROUND(SUM(ft.attributed_revenue), 2) AS first_touch_revenue,
  
  -- Last-Touch Metrics
  COUNT(DISTINCT lt.customer_id) AS last_touch_customers,
  ROUND(SUM(lt.attributed_revenue), 2) AS last_touch_revenue

FROM
  first_touch ft
FULL OUTER JOIN
  last_touch lt ON ft.first_touch_source = lt.last_touch_source 
               AND ft.customer_id = lt.customer_id

GROUP BY
  marketing_channel

ORDER BY
  first_touch_revenue DESC;

