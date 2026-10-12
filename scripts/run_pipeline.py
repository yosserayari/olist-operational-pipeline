from pathlib import Path
import os
import sys

import psycopg
from dotenv import load_dotenv


# --------------------------------------------------
# Project setup
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

RAW_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


def get_db_config():
    required = [
        "DB_HOST",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing = [
        name for name in required
        if not os.getenv(name)
    ]

    if missing:
        raise RuntimeError(
            f"Missing settings in .env: {', '.join(missing)}"
        )

    return {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }


def execute_sql_file(conn, relative_path):
    path = ROOT / relative_path

    if not path.is_file():
        raise FileNotFoundError(f"SQL file not found: {path}")

    print(f"Running {relative_path}...")

    sql = path.read_text(encoding="utf-8")

    with conn.cursor() as cur:
        # These scripts contain multiple SQL statements.
        cur.execute(sql, prepare=False)


def main():
    # 1. Verify that all source files are present.
    data_dir = ROOT / "data" / "raw"
    missing_files = [
        filename
        for filename in RAW_FILES
        if not (data_dir / filename).is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing source CSV files:\n"
            + "\n".join(missing_files)
        )

    db_config = get_db_config()

    # 2. Ensure the raw schema exists.
    with psycopg.connect(**db_config) as conn:
        execute_sql_file(conn, "sql/raw_schema.sql")

    # 3. Reload all raw tables from the source CSVs.
    print("\nStep 1/4: Loading raw data...")
    from src.ingestion.load_raw import main as load_raw_main

    load_raw_main()

    # 4. Rebuild staging, marts and reporting.
    print("\nSteps 2-4/4: Building downstream layers...")

    with psycopg.connect(**db_config) as conn:
        execute_sql_file(
            conn,
            "sql/staging/build_staging.sql",
        )

        # The reporting view depends on mart tables.
        # Drop it before rebuilding those tables.
        with conn.cursor() as cur:
            cur.execute(
                "CREATE SCHEMA IF NOT EXISTS reporting;"
            )
            cur.execute(
                "DROP VIEW IF EXISTS reporting.daily_sales;"
            )

        execute_sql_file(
            conn,
            "sql/marts/build_marts.sql",
        )

        execute_sql_file(
            conn,
            "sql/views/build_reporting_views.sql",
        )

        # 5. Verify key row counts.
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM raw.orders),
                    (SELECT COUNT(*) FROM staging.orders),
                    (SELECT COUNT(*) FROM mart.fact_orders),
                    (SELECT COUNT(*) FROM raw.order_items),
                    (SELECT COUNT(*) FROM staging.order_items),
                    (SELECT COUNT(*) FROM mart.fact_order_items),
                    (SELECT COUNT(*) FROM reporting.daily_sales)
            """)

            (
                raw_orders,
                staging_orders,
                mart_orders,
                raw_items,
                staging_items,
                mart_items,
                reporting_days,
            ) = cur.fetchone()

        if not (
            raw_orders == staging_orders == mart_orders
        ):
            raise RuntimeError(
                "Order row counts do not match across layers."
            )

        if not (
            raw_items == staging_items == mart_items
        ):
            raise RuntimeError(
                "Order-item row counts do not match across layers."
            )

        if reporting_days == 0:
            raise RuntimeError(
                "The daily sales view contains no rows."
            )

        print("\nValidation passed.")
        print(f"Orders across raw/staging/mart: {raw_orders:,}")
        print(
            "Order items across raw/staging/mart: "
            f"{raw_items:,}"
        )
        print(f"Daily sales rows: {reporting_days:,}")

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()