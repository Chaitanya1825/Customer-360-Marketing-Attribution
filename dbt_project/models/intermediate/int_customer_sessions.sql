WITH sessions AS (
    SELECT * FROM {{ ref('stg_ga4_sessions') }}
),

identity_mapping AS (
    SELECT * FROM {{ ref('stg_identity_mapping') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

-- Join GA4 sessions with CRM customers using identity resolution
-- Note: SAFE_CAST handles scientific notation string formatting differences from CSV export
customer_sessions AS (
    SELECT
        c.customer_id,
        s.user_pseudo_id,
        s.ga_session_id,
        s.session_start_time,
        s.traffic_source,
        s.traffic_medium,
        s.campaign_name,
        s.event_count,
        s.purchase_revenue,
        m.mapping_type,
        
        -- Chronological touchpoint sequence per customer (1 = First Touch)
        ROW_NUMBER() OVER (
            PARTITION BY c.customer_id 
            ORDER BY s.session_start_time ASC
        ) AS session_sequence_number

    FROM
        sessions s
    INNER JOIN
        identity_mapping m ON SAFE_CAST(s.user_pseudo_id AS FLOAT64) = SAFE_CAST(m.user_pseudo_id AS FLOAT64)
    INNER JOIN
        customers c ON m.customer_id = c.customer_id
)

SELECT
    customer_id,
    user_pseudo_id,
    ga_session_id,
    session_start_time,
    traffic_source,
    traffic_medium,
    campaign_name,
    event_count,
    purchase_revenue,
    mapping_type,
    session_sequence_number
FROM
    customer_sessions
ORDER BY
    customer_id,
    session_sequence_number ASC
