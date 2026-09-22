import json
from pathlib import Path
from typing import Any

from django.db import transaction

from .models import Client, Designer, Moodboard, MoodboardCatalog


DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "moodboards.json"


def find_client(clients: list[Client], email: str) -> Client | None:
    return next((client for client in clients if client.email == email), None)


def find_catalog(
    catalogs: list[MoodboardCatalog],
    name: str,
) -> MoodboardCatalog | None:
    return next((catalog for catalog in catalogs if catalog.name == name), None)


def export_data(
    designer: Designer,
    file_path: str | Path = DEFAULT_DATA_PATH,
) -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    catalogs = MoodboardCatalog.objects.filter(designer=designer)
    moodboards = Moodboard.objects.filter(designer=designer).select_related(
        "catalog", "client"
    )
    clients = Client.objects.filter(moodboards__designer=designer).distinct()
    payload: dict[str, list[dict[str, Any]]] = {
        "clients": [
            {"name": client.name, "email": client.email, "company": client.company}
            for client in clients
        ],
        "catalogs": [
            {"name": catalog.name, "description": catalog.description}
            for catalog in catalogs
        ],
        "moodboards": [board.to_data() for board in moodboards],
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    path.write_text(serialized, encoding="utf-8")
    return path


@transaction.atomic
def import_data(
    designer: Designer,
    file_path: str | Path = DEFAULT_DATA_PATH,
) -> int:
    path = Path(file_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        message = "Файл данных недоступен или содержит некорректный JSON."
        raise ValueError(message) from error
    if not isinstance(payload, dict):
        raise ValueError("Корень JSON-файла должен быть объектом.")

    clients_data = payload.get("clients", [])
    catalogs_data = payload.get("catalogs", [])
    moodboards_data = payload.get("moodboards", [])
    data_sections = (clients_data, catalogs_data, moodboards_data)
    if not all(isinstance(items, list) for items in data_sections):
        raise ValueError("Разделы clients, catalogs и moodboards должны быть списками.")

    clients: list[Client] = []
    for item in clients_data:
        if not isinstance(item, dict) or not item.get("name") or not item.get("email"):
            raise ValueError("Каждый клиент должен содержать name и email.")
        client_record, _ = Client.objects.update_or_create(
            email=item["email"],
            defaults={"name": item["name"], "company": item.get("company", "")},
        )
        clients.append(client_record)

    catalogs: list[MoodboardCatalog] = []
    for item in catalogs_data:
        if not isinstance(item, dict) or not item.get("name"):
            raise ValueError("Каждый каталог должен содержать name.")
        catalog_record, _ = MoodboardCatalog.objects.update_or_create(
            designer=designer,
            name=item["name"],
            defaults={"description": item.get("description", "")},
        )
        catalogs.append(catalog_record)

    imported = 0
    for item in moodboards_data:
        if not isinstance(item, dict) or not item.get("title"):
            raise ValueError("Каждый мудборд должен содержать title.")
        client_email = item.get("client_email")
        catalog_name = item.get("catalog")
        client: Client | None = (
            find_client(clients, client_email) if client_email else None
        )
        catalog: MoodboardCatalog | None = (
            find_catalog(catalogs, catalog_name) if catalog_name else None
        )
        if client_email and client is None:
            raise ValueError(f"Клиент {client_email} не найден в файле.")
        if catalog_name and catalog is None:
            raise ValueError(f"Каталог {catalog_name} не найден в файле.")
        board = Moodboard(
            designer=designer,
            client=client,
            catalog=catalog,
            title=item["title"],
            description=item.get("description", ""),
            background_color=item.get("background_color", "#F4EFE6"),
        )
        board.full_clean()
        board.save()
        imported += 1
    return imported
