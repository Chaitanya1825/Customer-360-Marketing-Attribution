-- =====================================================================
-- customer_360.sql
-- ---------------------------------------------------------------------
-- Description:
-- Combines customer profile data with transaction history to produce
-- a unified Customer 360 view with RFM metrics and segmentation.
-- =====================================================================

WITH customer_order_summary AS (
  -- Step 1: Aggregate order metrics per customer
  SELECT
    customer_id,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(order_amount), 2) AS total_spend,
    ROUND(AVG(order_amount), 2) AS avg_order_value,
    MIN(order_date) AS first_order_date,
    MAX(order_date) AS last_order_date
  FROM
    orders
  GROUP BY
    customer_id
),

customer_category_ranking AS (
  -- Step 2: Determine each customer's most purchased product category
  SELECT
    customer_id,
    product_category,
    COUNT(order_id) AS category_order_count,
    ROW_NUMBER() OVER(
      PARTITION BY customer_id 
      ORDER BY COUNT(order_id) DESC, product_category ASC
    ) AS rank_num
  FROM
    orders
  GROUP BY
    customer_id,
    product_category
),

top_categories AS (
  -- Step 3: Keep only the #1 top category per customer
  SELECT
    customer_id,
    product_category AS favorite_category
  FROM
    customer_category_ranking
  WHERE
    rank_num = 1
)

-- Step 4: Join customer details with aggregated metrics and top category
SELECT
  c.customer_id,
  c.name,
  c.email,
  c.city,
  c.signup_date,
  
  -- Order & Revenue Metrics (handle customers with 0 orders using COALESCE)
  COALESCE(o.total_orders, 0) AS total_orders,
  COALESCE(o.total_spend, 0.0) AS total_spend,
  COALESCE(o.avg_order_value, 0.0) AS avg_order_value,
  
  -- Recency / Dates
  o.first_order_date,
  o.last_order_date,
  
  -- Product preferences
  COALESCE(t.favorite_category, 'No Purchases') AS favorite_category,
  
  -- Customer Lifecycle Segmentation
  CASE
    WHEN COALESCE(o.total_spend, 0) >= 1000 THEN 'VIP'
    WHEN COALESCE(o.total_spend, 0) >= 500  THEN 'High Value'
    WHEN COALESCE(o.total_orders, 0) >= 1   THEN 'Regular'
    ELSE 'Prospect (No Orders)'
  END AS customer_segment

FROM
  customers c
LEFT JOIN
  customer_order_summary o ON c.customer_id = o.customer_id
LEFT JOIN
  top_categories t ON c.customer_id = t.customer_id

ORDER BY
  total_spend DESC;

