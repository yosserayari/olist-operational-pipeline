CRITICAL_CHECKS = [
    (
        "Orders have unique, non-empty IDs",
        """
        SELECT COUNT(*)
        FROM (
            SELECT order_id
            FROM staging.orders
            GROUP BY order_id
            HAVING order_id IS NULL
                OR BTRIM(order_id) = ''
                OR COUNT(*) > 1
        ) q
        """,
    ),
     (
        "Order items have unique order/item keys",
        """
        SELECT COUNT(*)
        FROM (
            SELECT order_id, order_item_id
            FROM staging.order_items
            GROUP BY order_id, order_item_id
            HAVING order_id IS NULL
                OR order_item_id IS NULL
                OR COUNT(*) > 1
        ) q
        """,
    ),
    (
        "Customer, product and seller IDs are unique",
        """
        SELECT
            (SELECT COUNT(*) FROM (
                SELECT customer_id
                FROM staging.customers
                GROUP BY customer_id
                HAVING customer_id IS NULL OR COUNT(*) > 1
            ) q)
            +
            (SELECT COUNT(*) FROM (
                SELECT product_id
                FROM staging.products
                GROUP BY product_id
                HAVING product_id IS NULL OR COUNT(*) > 1
            ) q)
            +
            (SELECT COUNT(*) FROM (
                SELECT seller_id
                FROM staging.sellers
                GROUP BY seller_id
                HAVING seller_id IS NULL OR COUNT(*) > 1
            ) q)
        """,
    ),
    (
        "Orders reference known customers",
        """
        SELECT COUNT(*)
        FROM staging.orders o
        WHERE NOT EXISTS (
            SELECT 1
            FROM staging.customers c
            WHERE c.customer_id = o.customer_id
        )
        """,
    ),
    (
        "Order items reference known orders, products and sellers",
        """
        SELECT COUNT(*)
        FROM staging.order_items i
        WHERE NOT EXISTS (
            SELECT 1 FROM staging.orders o
            WHERE o.order_id = i.order_id
        )
        OR NOT EXISTS (
            SELECT 1 FROM staging.products p
            WHERE p.product_id = i.product_id
        )
        OR NOT EXISTS (
            SELECT 1 FROM staging.sellers s
            WHERE s.seller_id = i.seller_id
        )
        """,
    ),
    (
        "Payments and reviews reference known orders",
        """
        SELECT
            (SELECT COUNT(*)
             FROM staging.order_payments p
             WHERE NOT EXISTS (
                 SELECT 1 FROM staging.orders o
                 WHERE o.order_id = p.order_id
             ))
            +
            (SELECT COUNT(*)
             FROM staging.order_reviews r
             WHERE NOT EXISTS (
                 SELECT 1 FROM staging.orders o
                 WHERE o.order_id = r.order_id
             ))
        """,
    ),
    (
        "Prices, freight and payments are non-negative",
        """
        SELECT
            (SELECT COUNT(*) FROM staging.order_items
             WHERE price IS NULL OR price < 0
                OR freight_value IS NULL OR freight_value < 0)
            +
            (SELECT COUNT(*) FROM staging.order_payments
             WHERE payment_value IS NULL OR payment_value < 0)
        """,
    ),
    (
        "Review scores are between 1 and 5",
        """
        SELECT COUNT(*)
        FROM staging.order_reviews
        WHERE review_score IS NULL
           OR review_score NOT BETWEEN 1 AND 5
        """,
    ),
]


WARNINGS = [
    (
        "Delivered orders missing delivery timestamps",
        """
        SELECT COUNT(*)
        FROM staging.orders
        WHERE order_status = 'delivered'
          AND order_delivered_customer_date IS NULL
        """,
    ),
    (
        "Orders with timestamp-sequence violations",
        """
        SELECT COUNT(*)
        FROM staging.orders
        WHERE (order_approved_at IS NOT NULL
               AND order_approved_at < order_purchase_timestamp)
           OR (order_delivered_carrier_date IS NOT NULL
               AND order_delivered_carrier_date < order_purchase_timestamp)
           OR (order_delivered_customer_date IS NOT NULL
               AND order_delivered_customer_date < order_purchase_timestamp)
           OR (order_delivered_customer_date IS NOT NULL
               AND order_delivered_carrier_date IS NOT NULL
               AND order_delivered_customer_date < order_delivered_carrier_date)
        """,
    ),
    (
        "Products with non-positive weights",
        """
        SELECT COUNT(*)
        FROM staging.products
        WHERE product_weight_g <= 0
        """,
    ),
    (
        "Payments with non-positive installment counts",
        """
        SELECT COUNT(*)
        FROM staging.order_payments
        WHERE payment_installments <= 0
        """,
    ),
    (
        "Orders without item records",
        """
        SELECT COUNT(*)
        FROM staging.orders o
        WHERE NOT EXISTS (
            SELECT 1 FROM staging.order_items i
            WHERE i.order_id = o.order_id
        )
        """,
    ),
]


def run_data_quality_checks(conn):
    failures = []

    print("\nCore data-quality checks:")

    with conn.cursor() as cur:
        for name, query in CRITICAL_CHECKS:
            cur.execute(query)
            count = cur.fetchone()[0]

            if count == 0:
                print(f"  PASS  {name}")
            else:
                print(f"  FAIL  {name}: {count} problem(s)")
                failures.append(name)

        print("\nData-quality observations:")

        for name, query in WARNINGS:
            cur.execute(query)
            count = cur.fetchone()[0]
            print(f"  INFO  {name}: {count:,}")

    if failures:
        raise RuntimeError(
            "Core data-quality checks failed: "
            + ", ".join(failures)
        )

    print("\nCore data-quality checks passed.")