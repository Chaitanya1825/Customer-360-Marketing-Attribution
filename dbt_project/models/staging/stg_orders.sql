WITH source AS (
    SELECT * FROM {{ source('raw_data', 'orders') }}
)

SELECT
    CAST(order_id AS STRING) AS order_id,
    CAST(customer_id AS STRING) AS customer_id,
    CAST(order_date AS DATE) AS order_date,
    CAST(order_amount AS NUMERIC) AS order_amount,
    TRIM(product_category) AS product_category
FROM
    source

