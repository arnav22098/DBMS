from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DB_PATH = ROOT_DIR / "my_database.db"
SCHEMA_PATH = ROOT_DIR / "schema.sql"


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enabled."""
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def apply_schema(
    connection: sqlite3.Connection,
    schema_path: Path | str = SCHEMA_PATH,
) -> None:
    """Create the project schema from the checked-in SQL file."""
    path = Path(schema_path)
    connection.executescript(path.read_text(encoding="utf-8"))
    connection.commit()
