"""
This module defines the SQLAlchemy configuration and session management for the application.

It sets up two separate database engines:
1.  **Library Database**: A persistent, on-disk SQLite database (`library.db`)
    that stores default, non-project-specific data like wood materials.
2.  **Working Database**: An in-memory SQLite database that holds the data for the
    currently active project. It is created by copying from the library database.

This separation ensures that the base library of materials is preserved and that
each new project starts with a clean slate.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Library Database Configuration ---
# The URL for the persistent, on-disk library database file.
LIBRARY_DATABASE_URL = "sqlite:///db/library.db"

# The SQLAlchemy engine is the starting point for any SQLAlchemy application.
# It's the low-level object that manages connections to the database.
# `connect_args` is used to pass arguments to the underlying DB-API driver.
# `check_same_thread=False` is a specific requirement for SQLite to allow it
# to be used in multi-threaded applications (like a GUI application).
library_engine = create_engine(LIBRARY_DATABASE_URL, connect_args={"check_same_thread": False})

# A sessionmaker object is a factory for creating new Session objects.
# A Session is the primary interface for all database operations.
LibrarySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=library_engine)


# --- Working Database (In-Memory) Configuration ---
# The URL for the in-memory database. `:memory:` is a special SQLite identifier.
WORKING_DATABASE_URL = "sqlite:///:memory:"

# A separate engine is created for the in-memory working database.
working_engine = create_engine(WORKING_DATABASE_URL, connect_args={"check_same_thread": False})

# A separate session factory for the working database.
WorkingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=working_engine)


# `declarative_base` returns a base class that all of our SQLAlchemy models will inherit from.
# This base class contains the metadata that SQLAlchemy uses to map our Python objects
# to the database tables.
Base = declarative_base()

def get_library_db():
    """
    A generator function that yields a new SQLAlchemy Session for the library database.

    This pattern is used as a dependency injection system. The `yield` provides the
    session to the caller, and the `finally` block ensures that the session is
    always closed, even if errors occur.
    """
    db = LibrarySessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_working_db():
    """
    A generator function that yields a new SQLAlchemy Session for the working database.

    This follows the same dependency injection pattern as `get_library_db`.
    """
    db = WorkingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_all_tables(engine):
    """
    Creates all database tables defined by the models that inherit from `Base`.

    Args:
        engine: The SQLAlchemy engine to which the tables should be bound.
    """
    # `Base.metadata.create_all` iterates through all the subclasses of `Base`
    # and issues `CREATE TABLE` statements to the database for each one.
    Base.metadata.create_all(bind=engine)