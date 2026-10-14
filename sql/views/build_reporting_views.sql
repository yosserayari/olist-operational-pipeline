CREATE SCHEMA IF NOT EXISTS reporting;

DROP VIEW IF EXISTS reporting.daily_sales;

CREATE VIEW reporting.daily_sales AS
WITH order_totals AS (
    SELECT
        order_id,
        SUM(price) AS product_value,
        SUM(freight_value) AS freight_value,
        SUM(item_total_value) AS order_value
    FROM mart.fact_order_items
    GROUP BY order_id
)
SELECT
    DATE(o.order_purchase_timestamp) AS sales_date,

    COUNT(*) AS total_orders,

    COUNT(*) FILTER (
        WHERE o.order_status = 'delivered'
    ) AS delivered_orders,

    COUNT(*) FILTER (
        WHERE o.order_status IN (
            'created', 'approved', 'invoiced',
            'processing', 'shipped'
        )
    ) AS in_progress_orders,

    COUNT(*) FILTER (
        WHERE o.order_status = 'canceled'
    ) AS canceled_orders,

    COUNT(*) FILTER (
        WHERE o.order_status = 'unavailable'
    ) AS unavailable_orders,

    COUNT(*) FILTER (
        WHERE ot.order_id IS NULL
    ) AS orders_without_items,

    ROUND(COALESCE(SUM(ot.product_value), 0), 2)
        AS ordered_product_value,

    ROUND(COALESCE(SUM(ot.freight_value), 0), 2)
        AS ordered_freight_value,

    ROUND(COALESCE(SUM(ot.order_value), 0), 2)
        AS ordered_gross_value,

    ROUND(COALESCE(
        SUM(ot.product_value) FILTER (
            WHERE o.order_status = 'delivered'
        ), 0
    ), 2) AS delivered_product_value,

    ROUND(COALESCE(
        SUM(ot.freight_value) FILTER (
            WHERE o.order_status = 'delivered'
        ), 0
    ), 2) AS delivered_freight_value,

    ROUND(COALESCE(
        SUM(ot.order_value) FILTER (
            WHERE o.order_status = 'delivered'
        ), 0
    ), 2) AS delivered_gross_order_value,

    ROUND(
        AVG(ot.order_value) FILTER (
            WHERE o.order_status = 'delivered'
        ),
        2
    ) AS avg_delivered_order_value

FROM mart.fact_orders o
LEFT JOIN order_totals ot
    ON o.order_id = ot.order_id

GROUP BY DATE(o.order_purchase_timestamp);