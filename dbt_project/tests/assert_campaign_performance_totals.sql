-- =====================================================================
-- assert_campaign_performance_totals.sql
-- ---------------------------------------------------------------------
-- Singular test: Verifies that total spend and total attributed revenue
-- in fct_campaign_performance match the upstream stg_ad_spend and
-- fct_order_attribution totals without any fan-out or metric loss.
-- Returns rows ONLY if there is a discrepancy (0 rows = PASS).
-- =====================================================================

WITH spend_check AS (
    SELECT
        ROUND(SUM(total_spend), 2) AS mart_spend,
        ROUND((SELECT SUM(spend_amount) FROM {{ ref('stg_ad_spend') }}), 2) AS source_spend
    FROM
        {{ ref('fct_campaign_performance') }}
    WHERE
        reporting_section = 'paid_campaign'
),

revenue_check AS (
    SELECT
        ROUND(SUM(first_touch_revenue), 2) AS mart_rev,
        ROUND((SELECT SUM(order_amount * first_touch_credit) FROM {{ ref('fct_order_attribution') }}), 2) AS source_rev
    FROM
        {{ ref('fct_campaign_performance') }}
    WHERE
        reporting_section = 'attributed_traffic_source'
)

SELECT
    'spend_mismatch' AS check_name,
    mart_spend AS mart_value,
    source_spend AS expected_value
FROM
    spend_check
WHERE
    mart_spend != source_spend

UNION ALL

SELECT
    'revenue_mismatch' AS check_name,
    mart_rev AS mart_value,
    source_rev AS expected_value
FROM
    revenue_check
WHERE
    mart_rev != source_rev

