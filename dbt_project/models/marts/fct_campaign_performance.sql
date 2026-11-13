-- =====================================================================
-- fct_campaign_performance.sql
-- ---------------------------------------------------------------------
-- Description:
-- Performance mart separating Paid Ad Campaign spend from Web Attribution
-- performance. 
--
-- Methodological Integrity:
-- Synthetic ad spend (Google, Facebook, YouTube) and Google's public GA4
-- web sessions are maintained as separate reporting sections.
-- No artificial mappings or unsubstantiated ROAS/CPA calculations are made
-- between unrelated campaign hierarchies.
-- =====================================================================

WITH ad_spend AS (
    SELECT * FROM {{ ref('stg_ad_spend') }}
),

attribution AS (
    SELECT * FROM {{ ref('fct_order_attribution') }}
),

-- Section 1: Paid Advertising Campaign Performance
paid_campaign_performance AS (
    SELECT
        'paid_campaign' AS reporting_section,
        campaign_id,
        campaign_name,
        marketing_channel,
        CAST(NULL AS STRING) AS traffic_source,
        CAST(NULL AS STRING) AS traffic_medium,

        -- Spend & Volume Metrics
        ROUND(SUM(spend_amount), 2) AS total_spend,
        SUM(clicks_count) AS total_clicks,
        SUM(impressions_count) AS total_impressions,

        -- Unit Cost Efficiency Metrics
        ROUND(SUM(spend_amount) / NULLIF(SUM(clicks_count), 0), 2) AS cost_per_click,
        ROUND((SUM(spend_amount) * 1000.0) / NULLIF(SUM(impressions_count), 0), 2) AS cost_per_1000_impressions,

        -- Attribution Metrics (Not applicable for paid spend hierarchy)
        CAST(NULL AS NUMERIC) AS first_touch_revenue,
        CAST(NULL AS NUMERIC) AS last_touch_revenue,
        CAST(NULL AS NUMERIC) AS linear_attributed_revenue,
        CAST(NULL AS NUMERIC) AS time_decay_attributed_revenue,
        CAST(NULL AS INT64) AS attributed_order_count

    FROM
        ad_spend
    GROUP BY
        campaign_id,
        campaign_name,
        marketing_channel
),

-- Section 2: Web Acquisition Attribution Performance (GA4 Traffic Sources & Mediums)
traffic_attribution_performance AS (
    SELECT
        'attributed_traffic_source' AS reporting_section,
        CAST(NULL AS STRING) AS campaign_id,
        CAST(NULL AS STRING) AS campaign_name,
        CAST(NULL AS STRING) AS marketing_channel,
        traffic_source,
        traffic_medium,

        -- Spend Metrics (Not applicable for organic / web session hierarchy)
        CAST(NULL AS NUMERIC) AS total_spend,
        CAST(NULL AS INT64) AS total_clicks,
        CAST(NULL AS INT64) AS total_impressions,
        CAST(NULL AS NUMERIC) AS cost_per_click,
        CAST(NULL AS NUMERIC) AS cost_per_1000_impressions,

        -- Attributed Revenue across the 4 Attribution Models
        ROUND(SUM(order_amount * first_touch_credit), 2) AS first_touch_revenue,
        ROUND(SUM(order_amount * last_touch_credit), 2) AS last_touch_revenue,
        ROUND(SUM(order_amount * linear_credit), 2) AS linear_attributed_revenue,
        ROUND(SUM(order_amount * time_decay_credit), 2) AS time_decay_attributed_revenue,
        COUNT(DISTINCT order_id) AS attributed_order_count

    FROM
        attribution
    GROUP BY
        traffic_source,
        traffic_medium
),

-- Combine both sections into a structured performance mart
unioned_performance AS (
    SELECT * FROM paid_campaign_performance
    UNION ALL
    SELECT * FROM traffic_attribution_performance
)

SELECT
    reporting_section,
    campaign_id,
    campaign_name,
    marketing_channel,
    traffic_source,
    traffic_medium,
    total_spend,
    total_clicks,
    total_impressions,
    cost_per_click,
    cost_per_1000_impressions,
    first_touch_revenue,
    last_touch_revenue,
    linear_attributed_revenue,
    time_decay_attributed_revenue,
    attributed_order_count
FROM
    unioned_performance
ORDER BY
    reporting_section ASC,
    COALESCE(total_spend, first_touch_revenue) DESC

