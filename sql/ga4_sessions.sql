-- =====================================================================
-- ga4_sessions.sql
-- ---------------------------------------------------------------------
-- Description:
-- Extracts session-level data from Google's public GA4 sample e-commerce
-- dataset in BigQuery for January 2021.
--
-- Dataset: bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*
-- =====================================================================

WITH extracted_events AS (
  -- Step 1: Extract individual event details and unnest ga_session_id
  SELECT
    user_pseudo_id,
    
    -- Extract ga_session_id from the nested event_params array
    (
      SELECT value.int_value 
      FROM UNNEST(event_params) 
      WHERE key = 'ga_session_id'
    ) AS ga_session_id,
    
    -- Convert event_timestamp (microseconds) to a human-readable TIMESTAMP
    TIMESTAMP_MICROS(event_timestamp) AS event_time,
    
    -- Traffic acquisition source fields
    traffic_source.source AS traffic_source,
    traffic_source.medium AS traffic_medium,
    traffic_source.name   AS campaign_name,
    
    -- Extract purchase revenue using the standard GA4 schema: ecommerce.purchase_revenue_in_usd
    COALESCE(ecommerce.purchase_revenue_in_usd, 0.0) AS event_purchase_revenue

  FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE
    -- Use only January 2021 data
    _TABLE_SUFFIX BETWEEN '20210101' AND '20210131'
)

-- Step 2: Group events into distinct sessions using user_pseudo_id and ga_session_id
SELECT
  user_pseudo_id,
  ga_session_id,
  
  -- Timestamp of the first event in the session
  MIN(event_time) AS session_start_time,
  
  -- Total events in this session
  COUNT(1) AS event_count,
  
  -- Traffic acquisition details associated with the session
  ANY_VALUE(traffic_source) AS traffic_source,
  ANY_VALUE(traffic_medium) AS traffic_medium,
  ANY_VALUE(campaign_name)  AS campaign_name,
  
  -- Total purchase revenue for the session
  ROUND(SUM(event_purchase_revenue), 2) AS purchase_revenue

FROM
  extracted_events
WHERE
  -- Keep only events that have a valid session ID
  ga_session_id IS NOT NULL

GROUP BY
  user_pseudo_id,
  ga_session_id

ORDER BY
  session_start_time DESC;
