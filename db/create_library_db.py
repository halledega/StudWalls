"""
This script creates and populates the library.db file.
"""

import csv
import os
import sys
import json

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import library_engine, LibrarySessionLocal, create_all_tables
from src.models.wood import Wood
from src.models.story import Story
from src.models.loads import Load
from src.models.wall import Wall
from src.models.wall_story import WallStory
from src.models.section import Section
from src.models.stud import Stud

def populate_wood_materials():
    """Reads the joist_and_plank.csv file and populates the wood_materials table."""
    db = LibrarySessionLocal()
    with open('src/data/joist_and_plank.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            wood = Wood(
                name=str(row['name']),
                category=str(row['category']),
                species=str(row['Species']),
                grade=str(row['Grade']),
                fb=float(row['fb']),
                fv=float(row['fv']),
                fc=float(row['fc']),
                fcp=float(row['fcp']),
                ft=float(row['ft']),
                E=float(row['E']),
                E05=float(row['E05']),
                material_type=str(row['material_type'])
            )
            db.add(wood)
    db.commit()
    db.close()

def populate_from_csv():
    """Reads data from CSV files and populates the database."""
    db = LibrarySessionLocal()

    # Stories
    with open('csv/stories.csv', 'r') as f:
        reader = csv.DictReader(f)
        stories = {row['id']: Story(**row) for row in reader}
        db.add_all(stories.values())

    # Loads
    with open('csv/loads.csv', 'r') as f:
        reader = csv.DictReader(f)
        loads = {row['id']: Load(**row) for row in reader}
        db.add_all(loads.values())

    # Walls
    with open('csv/walls.csv', 'r') as f:
        reader = csv.DictReader(f)
        walls_data = list(reader)
    
    walls = {}
    for row in walls_data:
        row.pop('tribs', None)
        row.pop('loads_left', None)
        row.pop('loads_right', None)
        row.pop('lu', None)
        wall = Wall(**row)
        walls[row['id']] = wall
        db.add(wall)

    db.commit()

    # WallStory Associations
    wall1 = walls['1']
    wall2 = walls['2']

    # Wall1 stories
    wall1_stories = [stories[str(i)] for i in range(1, 4)]
    for story in wall1_stories:
        ws = WallStory(wall=wall1, story=story)
        ws.loads_left = [loads['4'], loads['5'], loads['7']]
        ws.loads_right = [loads['4'], loads['5'], loads['7']]
        db.add(ws)

    # Wall2 stories
    wall2_stories = [stories[str(i)] for i in range(1, 7)]
    for story in wall2_stories:
        ws = WallStory(wall=wall2, story=story)
        if story.name == "Roof":
            ws.loads_left = [loads['1'], loads['2'], loads['3']]
            ws.loads_right = [loads['1'], loads['2'], loads['3']]
        else:
            ws.loads_left = [loads['4'], loads['5'], loads['7']]
            ws.loads_right = [loads['4'], loads['5'], loads['7']]
        db.add(ws)
        
    db.commit()

    # Set tribs and lu
    for wall in walls.values():
        wall.tribs = [[1000, 1500]] * len(wall.stories)
        wall.lu = [[3000, 152]] * len(wall.stories)

    db.commit()
    db.close()

def populate_sections_and_studs():
    """Populates the sections and studs tables with some default values."""
    db = LibrarySessionLocal()

    materials = {m.name: m for m in db.query(Wood).all()}
    if not materials:
        print("No wood materials found in the database. Cannot create studs.")
        return

    stud_data = [
        {"name": "2x4 SPF No.1/No.2", "width": 38.1, "depth": 88.9, "plys": 1, "material_name": "SPF No1/No2"},
        {"name": "2x6 SPF No.1/No.2", "width": 38.1, "depth": 139.7, "plys": 1, "material_name": "SPF No1/No2"},
        {"name": "2x8 SPF No.1/No.2", "width": 38.1, "depth": 184.15, "plys": 1, "material_name": "SPF No1/No2"},
        {"name": "2-2x4 SPF No.1/No.2", "width": 38.1, "depth": 88.9, "plys": 2, "material_name": "SPF No1/No2"},
        {"name": "2-2x6 SPF No.1/No.2", "width": 38.1, "depth": 139.7, "plys": 2, "material_name": "SPF No1/No2"},
        {"name": "2-2x8 SPF No.1/No.2", "width": 38.1, "depth": 184.15, "plys": 2, "material_name": "SPF No1/No2"},
    ]

    for data in stud_data:
        section = Section(width=data["width"], depth=data["depth"], plys=data["plys"])
        stud = Stud(
            name=data["name"],
            section=section,
            material=materials[data["material_name"]]
        )
        db.add(stud)
    
    db.commit()
    db.close()

if __name__ == "__main__":
    print("Creating library database...")
    # Remove the existing database file if it exists
    if os.path.exists("db/library.db"):
        os.remove("db/library.db")
    create_all_tables(library_engine)
    print("Populating wood materials...")
    populate_wood_materials()
    print("Populating from CSV...")
    populate_from_csv()
    print("Populating sections and studs...")
    populate_sections_and_studs()
    print("Library database created successfully.")
