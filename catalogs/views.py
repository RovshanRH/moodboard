import json
from typing import Any, cast

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from db.database import query_all

from accounts.models import Client, Designer
from boards.models import Moodboard

from .models import MoodboardCatalog


def catalog_pages(request: HttpRequest) -> HttpResponse:
    catalogs = query_all(
        """
        SELECT c.*, d.display_name AS designer_name, COUNT(m.id) AS moodboard_count
        FROM catalogs AS c
        JOIN designers AS d ON d.id = c.designer_id
        LEFT JOIN moodboards AS m ON m.catalog_id = c.id
        GROUP BY c.id, d.display_name
        ORDER BY c.name
        """
    )
    if not catalogs:
        catalogs = MoodboardCatalog.objects.select_related("designer").all()
    return render(request, "moodboards/catalogs.html", {"catalogs": catalogs})


def client_pages(request: HttpRequest) -> HttpResponse:
    clients = query_all(
        """
        SELECT cl.*, COUNT(m.id) AS moodboard_count
        FROM clients AS cl
        LEFT JOIN moodboards AS m ON m.client_id = cl.id
        GROUP BY cl.id
        ORDER BY cl.name
        """
    )
    if not clients:
        clients = Client.objects.all()
    return render(request, "moodboards/clients.html", {"clients": clients})


def _json_body(request: HttpRequest) -> dict[str, Any] | None:
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _text_value(
    data: dict[str, Any],
    key: str,
    default: str = "",
) -> str | None:
    value = data.get(key, default)
    return value.strip() if isinstance(value, str) else None


@csrf_exempt
def catalog_list(request: HttpRequest) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Требуется авторизация."}, status=401)

    designer = Designer.objects.filter(user=cast(User, request.user)).first()
    if designer is None:
        return JsonResponse(
            {"error": "Только дизайнер может управлять каталогами."},
            status=403,
        )
    if request.method == "GET":
        catalogs = MoodboardCatalog.objects.filter(designer=designer)
        return JsonResponse(
            {
                "items": [
                    {
                        "id": catalog.pk,
                        "name": catalog.name,
                        "description": catalog.description,
                        "moodboard_ids": list(
                            catalog.moodboards.values_list("id", flat=True)
                        ),
                    }
                    for catalog in catalogs
                ]
            }
        )

    if request.method != "POST":
        return JsonResponse({"error": "Метод не поддерживается."}, status=405)
    data = _json_body(request)
    if data is None:
        return JsonResponse({"error": "Некорректный JSON."}, status=400)
    name = _text_value(data, "name")
    if not name:
        return JsonResponse({"error": "Название каталога обязательно."}, status=400)

    moodboard_ids = data.get("moodboard_ids", [])
    if not isinstance(moodboard_ids, list) or any(
        isinstance(item, bool) or not isinstance(item, int) for item in moodboard_ids
    ):
        return JsonResponse(
            {"error": "moodboard_ids должен быть списком чисел."}, status=400
        )
    boards = Moodboard.objects.filter(designer=designer, id__in=moodboard_ids)
    if boards.count() != len(set(moodboard_ids)):
        return JsonResponse(
            {"error": "Можно добавлять только свои мудборды."}, status=404
        )

    catalog = MoodboardCatalog(
        designer=designer,
        name=name,
        description=_text_value(data, "description") or "",
    )
    try:
        catalog.full_clean()
        catalog.save()
    except ValidationError as error:
        return JsonResponse({"error": error.message_dict}, status=400)
    boards.update(catalog=catalog)
    return JsonResponse(
        {
            "id": catalog.pk,
            "name": catalog.name,
            "description": catalog.description,
            "moodboard_ids": list(boards.values_list("id", flat=True)),
        },
        status=201,
    )
