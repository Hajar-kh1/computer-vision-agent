"""Database engine, session factory, and Base (spec §16).

TODO (Student 2 — Backend Engineer):
- SQLAlchemy engine from settings.DATABASE_URL (psycopg driver).
- SessionLocal (scoped session) + get_db() dependency for FastAPI.
- Base = declarative_base() for the ORM models.
- For tests: support overriding with an in-memory SQLite engine
  (tests/ should not require a running PostgreSQL).
"""

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
#
# engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Base = declarative_base()
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
