from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "roomly.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection() as connection:
        connection.executescript(schema)


def query_all(
    sql: str,
    parameters: Iterable[Any] = (),
) -> list[sqlite3.Row]:
    with get_connection() as connection:
        return list(connection.execute(sql, tuple(parameters)))


def query_one(
    sql: str,
    parameters: Iterable[Any] = (),
) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute(sql, tuple(parameters)).fetchone()
