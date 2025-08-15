"""
This script creates and populates the library.db file.
"""

import csv
import os
import sys

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import library_engine, LibrarySessionLocal, create_all_tables
from src.models.wood import Wood
from src.models.story import Story
from src.models.loads import Load
from src.models.wall import Wall

def populate_wood_materials():
    """Reads the joist_and_plank.csv file and populates the wood_materials table."""
    db = LibrarySessionLocal()
    with open('src/data/joist_and_plank.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            wood = Wood(
                species=row['Species'],
                grade=row['Grade'],
                fb=float(row['fb']),
                fv=float(row['fv']),
                fc=float(row['fc']),
                fcp=float(row['fcp']),
                ft=float(row['ft']),
                E=float(row['E']),
                E05=float(row['E05']),
                material_type=row['Type']
            )
            db.add(wood)
    db.commit()
    db.close()

def create_dummy_data():
    """Creates dummy stories, loads, and walls for testing."""
    db = LibrarySessionLocal()

    # Create dummy stories
    story1 = Story(name="Story 1", height=3000, floor_thickness=150)
    story2 = Story(name="Story 2", height=3000, floor_thickness=150)
    db.add_all([story1, story2])
    db.commit()

    # Create dummy loads
    load1 = Load(name="Dead Load", case="Dead", value=10, load_type="Area")
    load2 = Load(name="Live Load", case="Live", value=20, load_type="Area")
    db.add_all([load1, load2])
    db.commit()

    # Create a dummy wall
    wall1 = Wall(
        name="Test Wall",
        length=5000,
        sw=0.5,
        tribs=[[1, 1], [1, 1]],
        loads_left=[[1, 2], [1, 2]],
        loads_right=[[1, 2], [1, 2]],
        lu=[[3000, 600], [3000, 600]],
        stories=[story1, story2]
    )
    db.add(wall1)
    db.commit()

    db.close()

if __name__ == "__main__":
    print("Creating library database...")
    create_all_tables(library_engine)
    print("Populating wood materials...")
    populate_wood_materials()
    print("Creating dummy data...")
    create_dummy_data()
    print("Library database created successfully.")
