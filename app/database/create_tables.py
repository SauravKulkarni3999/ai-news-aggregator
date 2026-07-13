# this script creates tables in the database

import os
import sys
from pathlib import Path

# setting the root of the project
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# now using the able path getting the imports from app folder
from app.database.models import Base
from app.database.connection import engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tables created successfully!")