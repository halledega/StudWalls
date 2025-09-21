"""
This module contains high-level project management functions, such as creating a new project.
"""

from src.core.database import library_engine, working_engine, create_all_tables, get_library_db, get_working_db
from src.models.wood import Wood
from src.models.story import Story
from src.models.loads import Load
from src.models.wall import Wall
from src.models.wall_story import WallStory
from src.models.stud import Stud
from src.models.section import Section
from src.models.load_combination import LoadCombination, LoadCombinationItem

def new_project():
    """
    Creates a new project by copying all data from the persistent library database
    to the in-memory working database.

    This function orchestrates the setup of a clean project environment. It first
    creates the necessary table schema in the working database and then performs
    a deep copy of all records from the library, ensuring that relationships
    between objects are correctly reconstructed in the new database.
    """
    # Ensure the schema (all tables) exists in the in-memory working database.
    create_all_tables(working_engine)

    # Obtain session objects for both the source (library) and destination (working) databases.
    library_db = next(get_library_db())
    working_db = next(get_working_db())

    # --- Data Copying Process ---
    # The process involves iterating through each type of object in the library DB,
    # creating a new Python object with the same data, and adding it to the working DB.
    # A mapping dictionary (e.g., `wood_map`) is used to keep track of the old library
    # objects and their corresponding new working objects. This is crucial for correctly
    # rebuilding relationships (e.g., linking a Stud to its Material).

    # Copy Wood materials
    wood_map = {}
    for wood in library_db.query(Wood).all():
        new_wood = Wood(
            name=wood.name,
            category=wood.category,
            species=wood.species,
            grade=wood.grade,
            fb=wood.fb,
            fv=wood.fv,
            fc=wood.fc,
            fcp=wood.fcp,
            ft=wood.ft,
            E=wood.E,
            E05=wood.E05,
            material_type=wood.material_type,
        )
        wood_map[wood] = new_wood
        working_db.add(new_wood)

    # Copy Studs and their Sections
    for stud in library_db.query(Stud).all():
        new_section = Section(
            width=stud.section.width,
            depth=stud.section.depth,
            plys=stud.section.plys,
            lu_width=stud.section.lu_width,
            lu_depth=stud.section.lu_depth
        )
        new_stud = Stud(
            name=stud.name,
            section=new_section,
            material=wood_map[stud.material]  # Re-link using the map
        )
        working_db.add(new_stud)

    # Copy Stories
    story_map = {}
    for story in library_db.query(Story).all():
        new_story = Story(name=story.name, height=story.height, floor_thickness=story.floor_thickness)
        story_map[story] = new_story
        working_db.add(new_story)

    # Copy Loads
    load_map = {}
    for load in library_db.query(Load).all():
        new_load = Load(name=load.name, case=load.case, value=load.value, load_type=load.load_type)
        load_map[load] = new_load
        working_db.add(new_load)

    # Copy Walls and their associated WallStories
    for wall in library_db.query(Wall).all():
        new_wall = Wall(
            name=wall.name,
            length=wall.length,
            sw=wall.sw,
            tribs=wall.tribs,
            lu=wall.lu,
        )
        working_db.add(new_wall)

        for wall_story in wall.stories:
            new_wall_story = WallStory(
                wall=new_wall,
                story=story_map[wall_story.story], # Re-link using the map
            )
            # Re-link the many-to-many load relationships using the map
            new_wall_story.loads_left = [load_map[l] for l in wall_story.loads_left]
            new_wall_story.loads_right = [load_map[l] for l in wall_story.loads_right]
            working_db.add(new_wall_story)

    # Copy Load Combinations and their items
    for combo in library_db.query(LoadCombination).all():
        new_combo = LoadCombination(name=combo.name)
        working_db.add(new_combo)
        for item in combo.items:
            new_item = LoadCombinationItem(
                load_combination=new_combo,
                load=load_map[item.load], # Re-link using the map
                factor=item.factor
            )
            working_db.add(new_item)

    # Commit all the new objects to the working database in a single transaction.
    working_db.commit()

    # Close the database sessions to free up resources.
    library_db.close()
    working_db.close()