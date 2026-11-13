WITH source AS (
    SELECT * FROM {{ source('raw_data', 'ad_spend') }}
)

SELECT
    CAST(campaign_id AS STRING) AS campaign_id,
    TRIM(campaign_name) AS campaign_name,
    TRIM(channel) AS marketing_channel,
    CAST(date AS DATE) AS spend_date,
    CAST(spend AS NUMERIC) AS spend_amount,
    CAST(clicks AS INT64) AS clicks_count,
    CAST(impressions AS INT64) AS impressions_count
FROM
    source

