from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Library Database ---
LIBRARY_DATABASE_URL = "sqlite:///db/library.db"
library_engine = create_engine(LIBRARY_DATABASE_URL, connect_args={"check_same_thread": False})
LibrarySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=library_engine)

# --- Working Database (in-memory) ---
WORKING_DATABASE_URL = "sqlite:///:memory:"
working_engine = create_engine(WORKING_DATABASE_URL, connect_args={"check_same_thread": False})
WorkingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=working_engine)

Base = declarative_base()

def get_library_db():
    db = LibrarySessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_working_db():
    db = WorkingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_all_tables(engine):
    Base.metadata.create_all(bind=engine)
