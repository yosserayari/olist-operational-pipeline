import pytest

import scripts.run_pipeline as pipeline


class FakeConnection:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_pipeline_stops_before_marts_on_quality_failure(monkeypatch):
    executed_sql = []

    # Skip checking local CSV files and database settings.
    monkeypatch.setattr(pipeline, "RAW_FILES", [])
    monkeypatch.setattr(pipeline, "get_db_config", lambda: {})

    # Prevent connections to the real database.
    monkeypatch.setattr(
        pipeline.psycopg,
        "connect",
        lambda **kwargs: FakeConnection(),
    )

    # Record SQL files without executing them.
    monkeypatch.setattr(
        pipeline,
        "execute_sql_file",
        lambda conn, path: executed_sql.append(path),
    )

    monkeypatch.setattr(pipeline, "load_raw", lambda conn: None)
    # Simulate a critical quality-check failure.
    def fail_quality_checks(conn):
        raise RuntimeError("Simulated critical failure")

    monkeypatch.setattr(
        pipeline,
        "run_data_quality_checks",
        fail_quality_checks,
    )

    with pytest.raises(RuntimeError, match="Simulated critical failure"):
        pipeline.main()

    assert executed_sql == [
        "sql/raw_schema.sql",
        "sql/staging/build_staging.sql",
    ]