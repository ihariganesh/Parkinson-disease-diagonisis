import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

SQLITE_FALLBACK_URL = "sqlite:///./parkinson_dev.db"

def _create_engine_with_fallback():
    """Try PostgreSQL first; fall back to SQLite if it fails."""
    db_url = settings.DATABASE_URL

    # Always use SQLite directly if configured
    if db_url.startswith("sqlite"):
        logger.info("Using SQLite database")
        return create_engine(db_url, connect_args={"check_same_thread": False})

    # Try PostgreSQL
    try:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": 5},
        )
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL connection successful")
        return engine
    except Exception as e:
        logger.warning(
            "PostgreSQL connection failed (%s). Falling back to SQLite.", str(e)[:120]
        )
        return create_engine(
            SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False},
        )


engine = _create_engine_with_fallback()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()