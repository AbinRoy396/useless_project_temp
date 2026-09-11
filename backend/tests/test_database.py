from sqlalchemy.engine import make_url

from app.database import normalize_database_url


def test_bare_postgresql_urls_use_psycopg3_dialect():
    for original in (
        "postgresql://user:password@db.example:5432/campus_voice",
        "postgres://user:password@db.example:5432/campus_voice",
    ):
        normalized = normalize_database_url(original)
        assert make_url(normalized).drivername == "postgresql+psycopg"


def test_existing_driver_and_sqlite_urls_are_unchanged():
    assert normalize_database_url("postgresql+psycopg://user:password@db.example/campus_voice") == "postgresql+psycopg://user:password@db.example/campus_voice"
    assert normalize_database_url("sqlite:///campus_voice.db") == "sqlite:///campus_voice.db"
