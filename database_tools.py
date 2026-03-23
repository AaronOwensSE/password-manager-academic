# DATABASE TOOLS #

import os
import sqlite3

# LITERAL SUBSTITUTIONS

DB_RELATIVE_PATH = "db/database.db"

# FUNCTIONS

# Returns absolute path to relative_path, creating the path if it does not exist.
def absolute_path(relative_path):
    script_path = os.path.dirname(__file__)
    absolute_path = os.path.join(script_path, relative_path)

    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

    return absolute_path

# Connects to database at relative_path.
def connect_to_db(relative_path):
    return sqlite3.connect(absolute_path(relative_path))
