-- =====================================================================
-- marketing_performance.sql
-- ---------------------------------------------------------------------
-- Description:
-- 1. Summarizes ad spend performance by channel (Google, Facebook, YouTube).
-- 2. Calculates digital marketing KPIs: CTR, CPC, and total investment.
-- =====================================================================

-- Part 1: Channel-Level Ad Performance
SELECT
  channel,
  
  -- Volume metrics
  COUNT(DISTINCT campaign_id) AS active_campaigns,
  SUM(impressions) AS total_impressions,
  SUM(clicks) AS total_clicks,
  
  -- Financial metrics
  ROUND(SUM(spend), 2) AS total_spend,
  
  -- Key Efficiency Metrics:
  -- Click-Through Rate (CTR%): Clicks / Impressions * 100
  ROUND((SUM(clicks) * 100.0) / NULLIF(SUM(impressions), 0), 2) AS ctr_percentage,
  
  -- Cost Per Click (CPC$): Spend / Clicks
  ROUND(SUM(spend) / NULLIF(SUM(clicks), 0), 2) AS cost_per_click_usd

FROM
  ad_spend

GROUP BY
  channel

ORDER BY
  total_spend DESC;

