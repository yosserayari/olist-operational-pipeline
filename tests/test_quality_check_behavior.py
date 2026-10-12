import pytest

from src.validation import data_quality_checks as checks


class FakeCursor:
    def __init__(self, results):
        self.results = iter(results)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query):
        pass

    def fetchone(self):
        return (next(self.results),)


class FakeConnection:
    def __init__(self, results):
        self.fake_cursor = FakeCursor(results)

    def cursor(self):
        return self.fake_cursor


def test_critical_failure_stops_quality_checks(monkeypatch):
    monkeypatch.setattr(
        checks,
        "CRITICAL_CHECKS",
        [("Simulated duplicate IDs", "SELECT 1")],
    )
    monkeypatch.setattr(checks, "WARNINGS", [])

    with pytest.raises(RuntimeError, match="Simulated duplicate IDs"):
        checks.run_data_quality_checks(FakeConnection([1]))


def test_warning_does_not_fail_quality_checks(monkeypatch, capsys):
    monkeypatch.setattr(
        checks,
        "CRITICAL_CHECKS",
        [("Core check", "SELECT 1")],
    )
    monkeypatch.setattr(
        checks,
        "WARNINGS",
        [("Known anomaly", "SELECT 1")],
    )

    checks.run_data_quality_checks(FakeConnection([0, 5]))

    output = capsys.readouterr().out

    assert "PASS  Core check" in output
    assert "INFO  Known anomaly: 5" in output
    assert "Core data-quality checks passed." in output