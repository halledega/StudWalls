"""
This module contains project management functions.
"""

from src.core.database import library_engine, working_engine, create_all_tables, get_library_db, get_working_db
from src.models.wood import Wood
from src.models.story import Story
from src.models.loads import Load
from src.models.wall import Wall
from src.models.wall_story import WallStory

def new_project():
    """Creates a new project by copying data from the library to the working database."""
    # Create all tables in the in-memory working database
    create_all_tables(working_engine)

    # Get sessions for both databases
    library_db = next(get_library_db())
    working_db = next(get_working_db())

    # Copy all data from the library to the working database
    wood_map = {}
    for wood in library_db.query(Wood).all():
        new_wood = Wood(
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

    story_map = {}
    for story in library_db.query(Story).all():
        new_story = Story(name=story.name, height=story.height, floor_thickness=story.floor_thickness)
        story_map[story] = new_story
        working_db.add(new_story)

    load_map = {}
    for load in library_db.query(Load).all():
        new_load = Load(name=load.name, case=load.case, value=load.value, load_type=load.load_type)
        load_map[load] = new_load
        working_db.add(new_load)

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
                story=story_map[wall_story.story],
            )
            new_wall_story.loads_left = [load_map[l] for l in wall_story.loads_left]
            new_wall_story.loads_right = [load_map[l] for l in wall_story.loads_right]
            working_db.add(new_wall_story)

    working_db.commit()

    library_db.close()
    working_db.close()
