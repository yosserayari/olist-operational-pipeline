from pathlib import Path
from io import StringIO
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv


DATA_DIR = Path("data/raw")


TABLES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def load_table(conn, table_name, csv_file):
    csv_path = DATA_DIR / csv_file

    print(f"Loading {csv_file}...")

    df = pd.read_csv(csv_path)

    # PostgreSQL COPY works reliably when missing values
    # are represented as empty fields.
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="")
    buffer.seek(0)

    columns = ", ".join(f'"{column}"' for column in df.columns)

    with conn.cursor() as cur:
        cur.execute(f'DROP TABLE IF EXISTS raw."{table_name}";')

        column_definitions = ", ".join(
            f'"{column}" TEXT'
            for column in df.columns
        )

        cur.execute(
            f'''
            CREATE TABLE raw."{table_name}" (
                {column_definitions}
            );
            '''
        )

        with cur.copy(
            f'''
            COPY raw."{table_name}" ({columns})
            FROM STDIN
            WITH (FORMAT CSV)
            '''
        ) as copy:
            while data := buffer.read(1024 * 1024):
                copy.write(data)

    print(f"  -> {len(df):,} rows loaded")


def load_raw(conn):
    for table_name, csv_file in TABLES.items():
        load_table(conn, table_name, csv_file)

    print("\nRaw ingestion completed.")


def main():
    load_dotenv()

    with get_connection() as conn:
        load_raw(conn)


if __name__ == "__main__":
    main()