import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from dotenv import load_dotenv
pytestmark = pytest.mark.integration


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def get_db_config():
    return {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }


def test_failed_transaction_rolls_back_database_changes():
    config = get_db_config()
    table = f"public.rollback_probe_{uuid4().hex}"

    try:
        with pytest.raises(RuntimeError, match="simulated failure"):
            with psycopg.connect(**config) as conn:
                conn.execute(
                    f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)"
                )
                conn.execute(f"INSERT INTO {table} VALUES (1)")

                # Simulate a failure partway through the transaction.
                raise RuntimeError("simulated failure")

        with psycopg.connect(**config) as conn:
            exists = conn.execute(
                "SELECT to_regclass(%s)",
                (table,),
            ).fetchone()[0]

        assert exists is None

    finally:
        # Clean up if the test ever leaves the probe table behind.
        with psycopg.connect(**config) as conn:
            conn.execute(f"DROP TABLE IF EXISTS {table}")