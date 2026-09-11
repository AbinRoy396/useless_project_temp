import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DEFAULT_DB = f"sqlite:///{Path(__file__).resolve().parent.parent / 'campus_voice.db'}"


def normalize_database_url(database_url: str) -> str:
    """Select SQLAlchemy's psycopg 3 dialect for bare PostgreSQL URLs.

    Render supplies a standard ``postgresql://`` URL. Without an explicit
    driver, SQLAlchemy's PostgreSQL default is psycopg2, which this project
    deliberately does not install.
    """
    scheme = database_url.lower()
    if scheme.startswith("postgresql://"):
        return "postgresql+psycopg://" + database_url[len("postgresql://"):]
    if scheme.startswith("postgres://"):
        return "postgresql+psycopg://" + database_url[len("postgres://"):]
    return database_url


DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", DEFAULT_DB))
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
