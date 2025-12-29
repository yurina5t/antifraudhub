# app/database/database.py
import logging
import os
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from app.database.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_database_engine():
    # Test mode → SQLite in-memory
    if settings.TESTING or os.getenv("TESTING") == "1":
        return create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    defaults = settings.defaults_used()
    if defaults:
        logger.warning(
            "Settings: default values used for: %s",
            ", ".join(defaults)
        )

    return create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


engine = get_database_engine()


def get_session():
    with Session(engine) as session:
        yield session


def init_db(drop_all: bool = False):
    try:
        if drop_all:
            SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"[init_db] DB init error: {e}")
        raise
