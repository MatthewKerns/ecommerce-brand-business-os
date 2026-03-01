"""
Database connection management for AI Content Agents.
Handles SQLite (development) and PostgreSQL (production) connections.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATABASE_DIR = Path(__file__).parent

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_DIR / 'content_agents.db'}"
)

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL query debugging
    )
else:
    # PostgreSQL or other database configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db():
    """
    Get database session.

    Yields:
        Session: SQLAlchemy database session

    Example:
        >>> with get_db() as db:
        ...     content = db.query(ContentHistory).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.

    This creates all tables defined in the models module.
    Safe to call multiple times - will not drop existing tables.
    """
    # Import models to ensure they're registered with Base
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db_session():
    """
    Get a new database session.

    Returns:
        Session: SQLAlchemy database session

    Note:
        Caller is responsible for closing the session.
        Consider using get_db() context manager instead.
    """
    return SessionLocal()
