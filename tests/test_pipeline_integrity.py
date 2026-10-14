import os
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv
pytestmark = pytest.mark.integration

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@pytest.fixture(scope="module")
def db():
    config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    if not all(config.values()):
        pytest.fail("Database settings are missing from .env")

    conn = psycopg.connect(**config)
    yield conn
    conn.close()


def value(db, query):
    with db.cursor() as cur:
        cur.execute(query)
        return cur.fetchone()[0]


def test_order_counts_match_across_layers(db):
    counts = [
        value(db, "SELECT COUNT(*) FROM raw.orders"),
        value(db, "SELECT COUNT(*) FROM staging.orders"),
        value(db, "SELECT COUNT(*) FROM mart.fact_orders"),
    ]

    assert counts[0] > 0
    assert counts[0] == counts[1] == counts[2]


def test_order_item_counts_match_across_layers(db):
    counts = [
        value(db, "SELECT COUNT(*) FROM raw.order_items"),
        value(db, "SELECT COUNT(*) FROM staging.order_items"),
        value(db, "SELECT COUNT(*) FROM mart.fact_order_items"),
    ]

    assert counts[0] > 0
    assert counts[0] == counts[1] == counts[2]


def test_order_ids_are_unique_and_present(db):
    problems = value(db, """
        SELECT COUNT(*)
        FROM (
            SELECT order_id
            FROM staging.orders
            GROUP BY order_id
            HAVING order_id IS NULL
                OR BTRIM(order_id) = ''
                OR COUNT(*) > 1
        ) q
    """)

    assert problems == 0


def test_order_item_keys_are_unique(db):
    problems = value(db, """
        SELECT COUNT(*)
        FROM (
            SELECT order_id, order_item_id
            FROM staging.order_items
            GROUP BY order_id, order_item_id
            HAVING order_id IS NULL
                OR order_item_id IS NULL
                OR COUNT(*) > 1
        ) q
    """)

    assert problems == 0


def test_order_items_reference_existing_entities(db):
    problems = value(db, """
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
    """)

    assert problems == 0


def test_item_totals_equal_price_plus_freight(db):
    problems = value(db, """
        SELECT COUNT(*)
        FROM mart.fact_order_items
        WHERE item_total_value IS DISTINCT FROM
              price + freight_value
    """)

    assert problems == 0


def test_daily_sales_accounts_for_all_orders(db):
    total_orders = value(
        db, "SELECT COUNT(*) FROM mart.fact_orders"
    )
    reported_orders = value(
        db, "SELECT COALESCE(SUM(total_orders), 0) "
            "FROM reporting.daily_sales"
    )

    assert reported_orders == total_orders


def test_daily_sales_has_one_row_per_date(db):
    duplicate_dates = value(db, """
        SELECT COUNT(*) - COUNT(DISTINCT sales_date)
        FROM reporting.daily_sales
    """)

    assert duplicate_dates == 0