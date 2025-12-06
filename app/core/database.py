"""
Database configuration and session management
SQLModel setup for SQLite database
"""
from sqlmodel import SQLModel, create_engine, Session
from .config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=True  # Log SQL queries (disable in production)
)


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency for getting database sessions
    Yields a session and ensures it's closed after use
    """
    with Session(engine) as session:
        yield session
