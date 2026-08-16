"""Database engine, session factory, and Base (spec §16).

Design notes:
- SQLAlchemy 2.0 engine built from settings.DATABASE_URL (psycopg driver).
- ``get_db()`` is the FastAPI dependency; tests override it with an
  in-memory SQLite engine so the suite runs without PostgreSQL.
- ``init_db()`` creates tables on startup (also idempotent for tests).
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    # echo=settings.DEBUG,  # uncomment to log all SQL while debugging
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yield a database session, always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables (import models so they register on Base)."""
    from backend.app import models  # noqa: F401  (side effect: register tables)

    Base.metadata.create_all(bind=engine)
