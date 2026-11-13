WITH source AS (
    SELECT * FROM {{ source('raw_data', 'ga4_sessions') }}
)

SELECT
    CAST(user_pseudo_id AS STRING) AS user_pseudo_id,
    CAST(ga_session_id AS INT64) AS ga_session_id,
    CAST(session_start_time AS TIMESTAMP) AS session_start_time,
    CAST(event_count AS INT64) AS event_count,
    TRIM(traffic_source) AS traffic_source,
    TRIM(traffic_medium) AS traffic_medium,
    TRIM(campaign_name) AS campaign_name,
    CAST(purchase_revenue AS NUMERIC) AS purchase_revenue
FROM
    source
WHERE
    ga_session_id IS NOT NULL
    AND user_pseudo_id IS NOT NULL

