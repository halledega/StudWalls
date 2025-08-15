"""
This module contains project management functions.
"""

from src.core.database import library_engine, working_engine, create_all_tables, get_library_db, get_working_db
from src.models.wood import Wood
from src.models.story import Story
from src.models.loads import Load
from src.models.wall import Wall

def new_project():
    """Creates a new project by copying data from the library to the working database."""
    # Create all tables in the in-memory working database
    create_all_tables(working_engine)

    # Get sessions for both databases
    library_db = next(get_library_db())
    working_db = next(get_working_db())

    # Copy all data from the library to the working database
    for wood in library_db.query(Wood).all():
        working_db.merge(wood)
    for story in library_db.query(Story).all():
        working_db.merge(story)
    for load in library_db.query(Load).all():
        working_db.merge(load)
    for wall in library_db.query(Wall).all():
        working_db.merge(wall)

    working_db.commit()

    library_db.close()
    working_db.close()
