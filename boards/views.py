from io import BytesIO
import json
from typing import Any, cast

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageDraw

from db.database import query_all, query_one

from accounts.models import Client, Designer
from catalogs.models import MoodboardCatalog

from .models import Moodboard


def moodboard_pages(request: HttpRequest) -> HttpResponse:
    boards = query_all(
        """
        SELECT m.id, m.title, m.description, m.background_color,
               d.display_name AS designer_name
        FROM moodboards AS m
        JOIN designers AS d ON d.id = m.designer_id
        ORDER BY m.updated_at DESC
        """
    )
    if not boards:
        boards = Moodboard.objects.select_related("designer").all()
    return render(request, "moodboards/moodboards.html", {"moodboards": boards})


def moodboard_create_page(request: HttpRequest) -> HttpResponse:
    designer = None
    if request.user.is_authenticated:
        designer = Designer.objects.filter(user=cast(User, request.user)).first()
    if designer is None:
        return redirect("moodboards:login")

    catalogs = MoodboardCatalog.objects.filter(designer=designer)
    clients = Client.objects.all().order_by("name")
    error = ""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        background_color = request.POST.get("background_color", "#F4EFE6").strip()
        palette_text = request.POST.get("palette", "")
        catalog_id = request.POST.get("catalog_id", "")
        client_id = request.POST.get("client_id", "")

        palette = [
            color.strip()
            for color in palette_text.split(",")
            if color.strip()
        ]
        catalog = (
            catalogs.filter(pk=catalog_id).first()
            if catalog_id
            else None
        )
        client = clients.filter(pk=client_id).first() if client_id else None
        if not title:
            error = "Название мудборда обязательно."
        elif catalog_id and catalog is None:
            error = "Выбранный каталог не найден."
        elif client_id and client is None:
            error = "Выбранный заказчик не найден."
        else:
            moodboard = Moodboard(
                designer=designer,
                catalog=catalog,
                client=client,
                title=title,
                description=description,
                background_color=background_color,
                palette=palette,
            )
            try:
                moodboard.full_clean()
                moodboard.save()
            except ValidationError as validation_error:
                error = "; ".join(
                    message
                    for messages in validation_error.message_dict.values()
                    for message in messages
                )
            else:
                return redirect("moodboards:detail", moodboard_id=moodboard.pk)

    return render(
        request,
        "moodboards/moodboard_form.html",
        {
            "catalogs": catalogs,
            "clients": clients,
            "error": error,
        },
    )


def moodboard_detail_page(
    request: HttpRequest,
    moodboard_id: int,
) -> HttpResponse:
    board = query_one(
        """
        SELECT m.*, d.display_name AS designer_name,
               c.name AS catalog_name, cl.name AS client_name
        FROM moodboards AS m
        JOIN designers AS d ON d.id = m.designer_id
        LEFT JOIN catalogs AS c ON c.id = m.catalog_id
        LEFT JOIN clients AS cl ON cl.id = m.client_id
        WHERE m.id = ?
        """,
        (moodboard_id,),
    )
    if board is None:
        board = get_object_or_404(
            Moodboard.objects.select_related("designer", "catalog", "client"),
            pk=moodboard_id,
        )
    return render(request, "moodboards/moodboard_detail.html", {"moodboard": board})


def moodboard_search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    boards = query_all(
        """
        SELECT m.id, m.title, m.description, m.background_color,
               d.display_name AS designer_name
        FROM moodboards AS m
        JOIN designers AS d ON d.id = m.designer_id
        WHERE m.title LIKE ?
        ORDER BY m.title
        """,
        (f"%{query}%",),
    )
    return render(
        request,
        "moodboards/search.html",
        {"moodboards": boards, "query": query},
    )


def moodboard_statistics(request: HttpRequest) -> HttpResponse:
    summary = query_one(
        """
        SELECT COUNT(*) AS moodboard_count,
               COUNT(DISTINCT designer_id) AS designer_count,
               COUNT(DISTINCT client_id) AS client_count
        FROM moodboards
        """
    )
    by_catalog = query_all(
        """
        SELECT COALESCE(c.name, 'Без каталога') AS catalog_name,
               COUNT(m.id) AS moodboard_count
        FROM moodboards AS m
        LEFT JOIN catalogs AS c ON c.id = m.catalog_id
        GROUP BY c.id, c.name
        HAVING COUNT(m.id) >= ?
        ORDER BY moodboard_count DESC
        """,
        (0,),
    )
    return render(
        request,
        "moodboards/statistics.html",
        {"summary": summary, "by_catalog": by_catalog},
    )


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


def _moodboard_data(moodboard: Moodboard) -> dict[str, Any]:
    return {
        "id": moodboard.pk,
        "title": moodboard.title,
        "description": moodboard.description,
        "background_color": moodboard.background_color,
        "palette": list(moodboard.palette or []),
        "designer": {
            "id": moodboard.designer.pk,
            "name": moodboard.designer.display_name,
        },
        "catalog": (
            {"id": moodboard.catalog.pk, "name": moodboard.catalog.name}
            if moodboard.catalog
            else None
        ),
        "client": (
            {"id": moodboard.client.pk, "name": moodboard.client.name}
            if moodboard.client
            else None
        ),
        "created_at": moodboard.created_at.isoformat(),
        "updated_at": moodboard.updated_at.isoformat(),
    }


@csrf_exempt
def moodboard_list(request: HttpRequest) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Требуется авторизация."}, status=401)

    designer = Designer.objects.filter(user=cast(User, request.user)).first()
    if designer is None:
        return JsonResponse(
            {"error": "Только дизайнер может управлять мудбордами."},
            status=403,
        )
    if request.method == "GET":
        boards = Moodboard.objects.filter(designer=designer).select_related(
            "designer", "catalog", "client"
        )
        return JsonResponse({"items": [_moodboard_data(board) for board in boards]})

    if request.method != "POST":
        return JsonResponse({"error": "Метод не поддерживается."}, status=405)

    data = _json_body(request)
    if data is None:
        return JsonResponse({"error": "Некорректный JSON."}, status=400)
    title = _text_value(data, "title")
    if not title:
        return JsonResponse(
            {"error": "Название мудборда обязательно."},
            status=400,
        )

    catalog = None
    catalog_id = data.get("catalog_id")
    if catalog_id is not None:
        if isinstance(catalog_id, bool) or not isinstance(catalog_id, int):
            return JsonResponse({"error": "catalog_id должен быть числом."}, status=400)
        catalog = MoodboardCatalog.objects.filter(
            id=catalog_id, designer=designer
        ).first()
        if catalog is None:
            return JsonResponse({"error": "Каталог не найден."}, status=404)

    client = None
    client_id = data.get("client_id")
    if client_id is not None:
        if isinstance(client_id, bool) or not isinstance(client_id, int):
            return JsonResponse({"error": "client_id должен быть числом."}, status=400)
        client = Client.objects.filter(id=client_id).first()
        if client is None:
            return JsonResponse({"error": "Заказчик не найден."}, status=404)

    description = _text_value(data, "description")
    background_color = data.get("background_color", "#F4EFE6")
    palette = data.get("palette", [])
    if not isinstance(palette, list):
        return JsonResponse(
            {"error": "palette должна быть списком цветов."}, status=400
        )
    if not isinstance(background_color, str):
        return JsonResponse(
            {"error": "background_color должен быть строкой формата #RRGGBB."},
            status=400,
        )
    moodboard = Moodboard(
        designer=designer,
        catalog=catalog,
        client=client,
        title=title,
        description=description or "",
        background_color=background_color,
        palette=palette,
    )
    try:
        moodboard.full_clean()
    except ValidationError as error:
        return JsonResponse({"error": error.message_dict}, status=400)
    moodboard.save()
    return JsonResponse(_moodboard_data(moodboard), status=201)


def moodboard_export(
    request: HttpRequest,
    moodboard_id: int,
) -> FileResponse | JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Требуется авторизация."}, status=401)
    designer = Designer.objects.filter(user=cast(User, request.user)).first()
    if designer is None:
        return JsonResponse(
            {"error": "Только дизайнер может экспортировать мудборды."},
            status=403,
        )
    moodboard = Moodboard.objects.filter(
        id=moodboard_id, designer=designer
    ).first()
    if moodboard is None:
        return JsonResponse({"error": "Мудборд не найден."}, status=404)

    image = Image.new("RGB", (1600, 1000), moodboard.background_color)
    draw = ImageDraw.Draw(image)
    draw.text((100, 100), moodboard.title, fill="#1E1E1E")
    if moodboard.description:
        draw.text((100, 180), moodboard.description, fill="#3D3D3D")
    if moodboard.palette:
        x = 100
        for color in moodboard.palette[:5]:
            draw.rectangle((x, 260, x + 120, 330), fill=color)
            x += 150
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return FileResponse(
        output,
        as_attachment=True,
        filename=f"moodboard-{moodboard.pk}.png",
    )
