WITH source AS (
    SELECT * FROM {{ source('raw_data', 'customers') }}
)

SELECT
    CAST(customer_id AS STRING) AS customer_id,
    TRIM(name) AS customer_name,
    LOWER(TRIM(email)) AS email,
    TRIM(city) AS city,
    CAST(signup_date AS DATE) AS signup_date
FROM
    source

