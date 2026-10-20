from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "data" / "moodboards.json"


def _items(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"Раздел {key} должен быть списком объектов.")
    return value


def import_json(
    json_path: str | Path = JSON_PATH,
) -> int:
    path = Path(json_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Корень JSON-файла должен быть объектом.")

    initialize_database()
    imported = 0
    with get_connection() as connection:
        connection.execute("DELETE FROM palette_colors")
        connection.execute("DELETE FROM moodboards")
        connection.execute("DELETE FROM catalogs")
        connection.execute("DELETE FROM clients")
        connection.execute("DELETE FROM designers")

        designers = {1: ("Импортированный дизайнер", "")}
        for designer_id, (name, bio) in designers.items():
            connection.execute(
                "INSERT INTO designers (id, display_name, bio) VALUES (?, ?, ?)",
                (designer_id, name, bio),
            )

        clients = _items(payload, "clients")
        client_ids: dict[str, int] = {}
        for index, item in enumerate(clients, start=1):
            email = item.get("email")
            if not isinstance(email, str) or not item.get("name"):
                raise ValueError("Клиент должен содержать name и email.")
            connection.execute(
                "INSERT INTO clients (id, name, email, company) VALUES (?, ?, ?, ?)",
                (index, item["name"], email, item.get("company", "")),
            )
            client_ids[email] = index

        catalog_ids: dict[str, int] = {}
        for index, item in enumerate(_items(payload, "catalogs"), start=1):
            name = item.get("name")
            if not isinstance(name, str) or not name:
                raise ValueError("Каталог должен содержать name.")
            connection.execute(
                "INSERT INTO catalogs (id, designer_id, name, description) "
                "VALUES (?, ?, ?, ?)",
                (index, 1, name, item.get("description", "")),
            )
            catalog_ids[name] = index

        for index, item in enumerate(_items(payload, "moodboards"), start=1):
            title = item.get("title")
            if not isinstance(title, str) or not title:
                raise ValueError("Мудборд должен содержать title.")
            connection.execute(
                """
                INSERT INTO moodboards (
                    id, designer_id, catalog_id, client_id, title, description,
                    background_color
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    index,
                    1,
                    catalog_ids.get(item.get("catalog")),
                    client_ids.get(item.get("client_email")),
                    title,
                    item.get("description", ""),
                    item.get("background_color", "#F4EFE6"),
                ),
            )
            for position, color in enumerate(item.get("palette", [])):
                connection.execute(
                    "INSERT INTO palette_colors (moodboard_id, color, position) "
                    "VALUES (?, ?, ?)",
                    (index, color, position),
                )
            imported += 1
    return imported


if __name__ == "__main__":
    print(f"Импортировано мудбордов: {import_json()}")
