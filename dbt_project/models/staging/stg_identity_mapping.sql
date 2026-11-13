WITH source AS (
    SELECT * FROM {{ source('raw_data', 'identity_mapping') }}
)

SELECT
    CAST(user_pseudo_id AS STRING) AS user_pseudo_id,
    CAST(customer_id AS STRING) AS customer_id,
    TRIM(mapping_type) AS mapping_type
FROM
    source

