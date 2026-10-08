-- ==========================================
-- STAGING: ORDERS
-- ==========================================
CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.orders;

CREATE TABLE staging.orders (
    order_id TEXT,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

INSERT INTO staging.orders
SELECT
    order_id,
    customer_id,
    order_status,
    NULLIF(order_purchase_timestamp, '')::TIMESTAMP,
    NULLIF(order_approved_at, '')::TIMESTAMP,
    NULLIF(order_delivered_carrier_date, '')::TIMESTAMP,
    NULLIF(order_delivered_customer_date, '')::TIMESTAMP,
    NULLIF(order_estimated_delivery_date, '')::TIMESTAMP
FROM raw.orders;


-- ==========================================
-- STAGING: ORDER ITEMS
-- ==========================================

DROP TABLE IF EXISTS staging.order_items;

CREATE TABLE staging.order_items (
    order_id TEXT,
    order_item_id INTEGER,
    product_id TEXT,
    seller_id TEXT,
    shipping_limit_date TIMESTAMP,
    price NUMERIC(12,2),
    freight_value NUMERIC(12,2)
);

INSERT INTO staging.order_items
SELECT
    order_id,
    NULLIF(order_item_id, '')::INTEGER,
    product_id,
    seller_id,
    NULLIF(shipping_limit_date, '')::TIMESTAMP,
    NULLIF(price, '')::NUMERIC(12,2),
    NULLIF(freight_value, '')::NUMERIC(12,2)
FROM raw.order_items;


-- ==========================================
-- STAGING: PRODUCTS
-- ==========================================

DROP TABLE IF EXISTS staging.products;

CREATE TABLE staging.products (
    product_id TEXT,
    product_category_name TEXT,
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g NUMERIC(12,2),
    product_length_cm NUMERIC(12,2),
    product_height_cm NUMERIC(12,2),
    product_width_cm NUMERIC(12,2)
);

INSERT INTO staging.products
SELECT
    product_id,
    NULLIF(product_category_name, ''),
    NULLIF(product_name_lenght, '')::NUMERIC::INTEGER,
    NULLIF(product_description_lenght, '')::NUMERIC::INTEGER,
    NULLIF(product_photos_qty, '')::NUMERIC::INTEGER,
    NULLIF(product_weight_g, '')::NUMERIC(12,2),
    NULLIF(product_length_cm, '')::NUMERIC(12,2),
    NULLIF(product_height_cm, '')::NUMERIC(12,2),
    NULLIF(product_width_cm, '')::NUMERIC(12,2)
FROM raw.products;

-- ==========================================
-- STAGING: CUSTOMERS
-- ==========================================

DROP TABLE IF EXISTS staging.customers;

CREATE TABLE staging.customers (
    customer_id TEXT,
    customer_unique_id TEXT,
    customer_zip_code_prefix TEXT,
    customer_city TEXT,
    customer_state TEXT
);

INSERT INTO staging.customers
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM raw.customers;


-- ==========================================
-- STAGING: ORDER PAYMENTS
-- ==========================================

DROP TABLE IF EXISTS staging.order_payments;

CREATE TABLE staging.order_payments (
    order_id TEXT,
    payment_sequential INTEGER,
    payment_type TEXT,
    payment_installments INTEGER,
    payment_value NUMERIC(12,2)
);

INSERT INTO staging.order_payments
SELECT
    order_id,
    NULLIF(payment_sequential, '')::NUMERIC::INTEGER,
    payment_type,
    NULLIF(payment_installments, '')::NUMERIC::INTEGER,
    NULLIF(payment_value, '')::NUMERIC(12,2)
FROM raw.order_payments;


-- ==========================================
-- STAGING: SELLERS
-- ==========================================

DROP TABLE IF EXISTS staging.sellers;

CREATE TABLE staging.sellers (
    seller_id TEXT,
    seller_zip_code_prefix TEXT,
    seller_city TEXT,
    seller_state TEXT
);

INSERT INTO staging.sellers
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM raw.sellers;


-- ==========================================
-- STAGING: ORDER REVIEWS
-- ==========================================

DROP TABLE IF EXISTS staging.order_reviews;

CREATE TABLE staging.order_reviews (
    review_id TEXT,
    order_id TEXT,
    review_score INTEGER,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

INSERT INTO staging.order_reviews
SELECT
    review_id,
    order_id,
    NULLIF(review_score, '')::NUMERIC::INTEGER,
    NULLIF(review_comment_title, ''),
    NULLIF(review_comment_message, ''),
    NULLIF(review_creation_date, '')::TIMESTAMP,
    NULLIF(review_answer_timestamp, '')::TIMESTAMP
FROM raw.order_reviews;


-- ==========================================
-- STAGING: CATEGORY TRANSLATION
-- ==========================================

DROP TABLE IF EXISTS staging.category_translation;

CREATE TABLE staging.category_translation (
    product_category_name TEXT,
    product_category_name_english TEXT
);

INSERT INTO staging.category_translation
SELECT
    product_category_name,
    product_category_name_english
FROM raw.category_translation;