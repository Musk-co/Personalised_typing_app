"""
Database initialization and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Create engine with sqlite or postgresql based on config
engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False,
    }
    if "sqlite" in settings.database_url
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency injection for database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
