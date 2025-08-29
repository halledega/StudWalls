import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.database import LibrarySessionLocal
from src.models.wood import Wood

def test_wood_material():
    db = LibrarySessionLocal()
    material = db.query(Wood).first()
    if material:
        print("Material attributes:", material.__dict__)
    else:
        print("No Wood material found in the database.")
    db.close()

if __name__ == "__main__":
    test_wood_material()
