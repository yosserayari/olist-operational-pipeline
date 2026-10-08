CREATE SCHEMA IF NOT EXISTS mart;

-- ==========================================
-- MART: FACT ORDERS
-- Grain: one row per order
-- ==========================================

DROP TABLE IF EXISTS mart.fact_orders;

CREATE TABLE mart.fact_orders AS
SELECT
    order_id,
    customer_id,
    order_status,

    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,

    CASE
        WHEN order_approved_at IS NOT NULL
        THEN ROUND(
            EXTRACT(EPOCH FROM (
                order_approved_at - order_purchase_timestamp
            )) / 3600,
            2
        )
    END AS approval_delay_hours,

    CASE
        WHEN order_approved_at IS NOT NULL
         AND order_delivered_carrier_date IS NOT NULL
        THEN ROUND(
            EXTRACT(EPOCH FROM (
                order_delivered_carrier_date - order_approved_at
            )) / 3600,
            2
        )
    END AS shipping_delay_hours,

    CASE
        WHEN order_delivered_customer_date IS NOT NULL
        THEN ROUND(
            EXTRACT(EPOCH FROM (
                order_delivered_customer_date - order_purchase_timestamp
            )) / 3600,
            2
        )
    END AS total_delivery_hours,

    CASE
        WHEN order_status = 'delivered'
         AND order_delivered_customer_date IS NULL
        THEN TRUE
        ELSE FALSE
    END AS missing_delivery_flag,

    CASE
        WHEN
            (order_approved_at IS NOT NULL
             AND order_approved_at < order_purchase_timestamp)
            OR
            (order_delivered_carrier_date IS NOT NULL
             AND order_delivered_carrier_date < order_purchase_timestamp)
            OR
            (order_delivered_customer_date IS NOT NULL
             AND order_delivered_customer_date < order_purchase_timestamp)
            OR
            (order_delivered_customer_date IS NOT NULL
             AND order_delivered_carrier_date IS NOT NULL
             AND order_delivered_customer_date < order_delivered_carrier_date)
        THEN TRUE
        ELSE FALSE
    END AS timestamp_sequence_error,

    CASE
        WHEN order_status = 'delivered'
         AND order_delivered_customer_date IS NOT NULL
         AND order_estimated_delivery_date IS NOT NULL
         AND order_delivered_customer_date > order_estimated_delivery_date
        THEN TRUE
        ELSE FALSE
    END AS late_delivery_flag

FROM staging.orders;

ALTER TABLE mart.fact_orders
ADD PRIMARY KEY (order_id);
-- ==========================================
-- MART: FACT ORDER ITEMS
-- Grain: one row per item in an order
-- ==========================================

DROP TABLE IF EXISTS mart.fact_order_items;

CREATE TABLE mart.fact_order_items AS
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value,

    price + freight_value AS item_total_value

FROM staging.order_items;

ALTER TABLE mart.fact_order_items
ADD PRIMARY KEY (order_id, order_item_id);

-- ==========================================
-- MART: DIM PRODUCTS
-- Grain: one row per product
-- ==========================================

DROP TABLE IF EXISTS mart.dim_products;

CREATE TABLE mart.dim_products AS
SELECT
    p.product_id,
    p.product_category_name,
    ct.product_category_name_english,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,

    CASE
        WHEN p.product_weight_g <= 0
        THEN TRUE
        ELSE FALSE
    END AS invalid_weight_flag

FROM staging.products p
LEFT JOIN staging.category_translation ct
    ON p.product_category_name = ct.product_category_name;

ALTER TABLE mart.dim_products
ADD PRIMARY KEY (product_id);

-- ==========================================
-- MART: DIM CUSTOMERS
-- Grain: one row per customer_id
-- ==========================================

DROP TABLE IF EXISTS mart.dim_customers;

CREATE TABLE mart.dim_customers AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM staging.customers;

ALTER TABLE mart.dim_customers
ADD PRIMARY KEY (customer_id);


-- ==========================================
-- MART: DIM SELLERS
-- Grain: one row per seller
-- ==========================================

DROP TABLE IF EXISTS mart.dim_sellers;

CREATE TABLE mart.dim_sellers AS
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM staging.sellers;

ALTER TABLE mart.dim_sellers
ADD PRIMARY KEY (seller_id);

-- ==========================================
-- MART: FACT PAYMENTS
-- Grain: one row per payment record
-- ==========================================

DROP TABLE IF EXISTS mart.fact_payments;

CREATE TABLE mart.fact_payments AS
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM staging.order_payments;

ALTER TABLE mart.fact_payments
ADD PRIMARY KEY (order_id, payment_sequential);

-- ==========================================
-- MART: FACT REVIEWS
-- Grain: one row per review record
-- ==========================================

DROP TABLE IF EXISTS mart.fact_reviews;

CREATE TABLE mart.fact_reviews AS
SELECT
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp,

    CASE
        WHEN review_score <= 2 THEN TRUE
        ELSE FALSE
    END AS negative_review_flag,

    CASE
        WHEN review_score >= 4 THEN TRUE
        ELSE FALSE
    END AS positive_review_flag,

    CASE
        WHEN review_comment_message IS NOT NULL
         AND review_comment_message <> ''
        THEN TRUE
        ELSE FALSE
    END AS has_comment

FROM staging.order_reviews;

CREATE INDEX idx_fact_reviews_order_id
    ON mart.fact_reviews(order_id);