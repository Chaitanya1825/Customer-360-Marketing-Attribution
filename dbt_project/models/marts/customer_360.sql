-- =====================================================================
-- customer_360.sql
-- ---------------------------------------------------------------------
-- Description:
-- Core Customer 360 mart combining customer profile, order metrics,
-- web session engagement, RFM analysis, and lifecycle segmentation.
--
-- One customer-level record per CRM customer.
-- =====================================================================

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

sessions AS (
    SELECT * FROM {{ ref('int_customer_sessions') }}
),

-- Reference date: latest order date in the entire dataset (for recency calculation)
reference_date AS (
    SELECT MAX(order_date) AS max_order_date FROM orders
),

-- 1. Order metrics aggregated by customer (avoids fan-out / double-counting)
orders_aggregated AS (
    SELECT
        customer_id,
        COUNT(order_id) AS total_orders,
        ROUND(SUM(order_amount), 2) AS total_revenue,
        ROUND(AVG(order_amount), 2) AS average_order_value,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date
    FROM
        orders
    GROUP BY
        customer_id
),

-- 2. Web session metrics aggregated by customer
sessions_aggregated AS (
    SELECT
        customer_id,
        COUNT(ga_session_id) AS total_sessions,
        MIN(DATE(session_start_time)) AS first_session_date,
        MAX(DATE(session_start_time)) AS last_session_date
    FROM
        sessions
    GROUP BY
        customer_id
),

-- 3. Combine customer profile with aggregated orders, sessions, and RFM scores
customer_joined AS (
    SELECT
        -- Customer Details
        c.customer_id,
        c.customer_name AS name,
        c.email,
        c.city,
        c.signup_date,

        -- Order Metrics
        COALESCE(o.total_orders, 0) AS total_orders,
        COALESCE(o.total_revenue, 0.0) AS total_revenue,
        COALESCE(o.average_order_value, 0.0) AS average_order_value,
        o.first_order_date,
        o.last_order_date,

        -- Customer Web Activity (Sessions)
        COALESCE(s.total_sessions, 0) AS total_sessions,
        s.first_session_date,
        s.last_session_date,

        -- RFM Metrics
        -- Recency: Days between customer's last order and dataset reference date
        DATE_DIFF(r.max_order_date, o.last_order_date, DAY) AS recency_days,
        COALESCE(o.total_orders, 0) AS frequency,
        COALESCE(o.total_revenue, 0.0) AS monetary_value

    FROM
        customers c
    CROSS JOIN
        reference_date r
    LEFT JOIN
        orders_aggregated o ON c.customer_id = o.customer_id
    LEFT JOIN
        sessions_aggregated s ON c.customer_id = s.customer_id
)

-- 4. Customer Segmentation Assignment based on RFM
SELECT
    customer_id,
    name,
    email,
    city,
    signup_date,
    total_orders,
    total_revenue,
    average_order_value,
    first_order_date,
    last_order_date,
    total_sessions,
    first_session_date,
    last_session_date,
    recency_days,
    frequency,
    monetary_value,

    CASE
        -- Champions: Frequent buyers, high spend, recent activity
        WHEN frequency >= 3 AND monetary_value >= 600 AND recency_days <= 7 
            THEN 'Champions'
        
        -- Loyal Customers: Multiple purchases and solid lifetime value
        WHEN frequency >= 2 AND monetary_value >= 400 
            THEN 'Loyal Customers'
        
        -- Potential Loyalists: Recent buyers with moderate spend
        WHEN recency_days <= 7 AND monetary_value >= 150 
            THEN 'Potential Loyalists'
        
        -- New Customers: First-time purchase very recently
        WHEN frequency = 1 AND recency_days <= 5 
            THEN 'New Customers'
        
        -- At Risk: Haven't purchased recently (recency >= 12 days)
        WHEN recency_days >= 12 AND monetary_value > 0 
            THEN 'At Risk'
        
        -- Others: Inactive/prospect customers or lower engagement
        ELSE 'Others'
    END AS customer_segment

FROM
    customer_joined

