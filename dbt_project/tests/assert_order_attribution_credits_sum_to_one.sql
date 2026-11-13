-- =====================================================================
-- assert_order_attribution_credits_sum_to_one.sql
-- ---------------------------------------------------------------------
-- Singular test: Verifies that every single order's attribution credits
-- sum to 1.0 (100%) under all four models:
--   1. First-Touch
--   2. Last-Touch
--   3. Linear
--   4. Time-Decay
-- Returns rows ONLY if there is an error/violation (0 rows = PASS).
-- =====================================================================

WITH order_credit_sums AS (
    SELECT
        order_id,
        ROUND(SUM(first_touch_credit), 2) AS sum_ft,
        ROUND(SUM(last_touch_credit), 2) AS sum_lt,
        ROUND(SUM(linear_credit), 2) AS sum_lin,
        ROUND(SUM(time_decay_credit), 2) AS sum_td
    FROM
        {{ ref('fct_order_attribution') }}
    GROUP BY
        order_id
)

SELECT
    order_id,
    sum_ft,
    sum_lt,
    sum_lin,
    sum_td
FROM
    order_credit_sums
WHERE
    sum_ft != 1.0
    OR sum_lt != 1.0
    OR sum_lin != 1.0
    OR sum_td != 1.0

