from io import BytesIO
import json
from typing import Any, cast

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import FileResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageDraw

from .models import Client, Designer, Moodboard, MoodboardCatalog


def _json_body(request: HttpRequest) -> dict[str, Any] | None:
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _text_value(data: dict[str, Any], key: str, default: str = "") -> str | None:
    value = data.get(key, default)
    return value.strip() if isinstance(value, str) else None


def _moodboard_data(moodboard: Moodboard) -> dict:
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
def auth_view(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        data = _json_body(request)
        if data is None:
            return JsonResponse({"error": "Некорректный JSON."}, status=400)

        username = _text_value(data, "username")
        password = data.get("password", "")
        display_name = _text_value(data, "display_name", username or "")
        if (
            not username
            or not isinstance(password, str)
            or not password
            or not display_name
        ):
            return JsonResponse(
                {"error": "Нужны username, password и display_name."},
                status=400,
            )
        if User.objects.filter(username=username).exists():
            user = authenticate(request, username=username, password=password)
            if user is None:
                return JsonResponse(
                    {"error": "Неверные данные входа."},
                    status=401,
                )
            login(request, user)
            designer = Designer.objects.get(user=user)
            return JsonResponse(
                {
                    "id": designer.pk,
                    "username": user.get_username(),
                    "display_name": designer.display_name,
                }
            )

        user = User.objects.create_user(username=username, password=password)
        designer = Designer.objects.create(
            user=user,
            display_name=display_name,
        )
        login(request, user)
        return JsonResponse(
            {
                "id": designer.pk,
                "username": user.username,
                "display_name": display_name,
            },
            status=201,
        )

    if request.method == "DELETE":
        logout(request)
        return JsonResponse({"detail": "Вы вышли из системы."})

    return JsonResponse({"error": "Метод не поддерживается."}, status=405)


@csrf_exempt
def moodboard_list(request: HttpRequest) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Требуется авторизация."}, status=401)

    user = cast(User, request.user)
    designer = Designer.objects.get(user=user)
    if request.method == "GET":
        boards = Moodboard.objects.filter(designer=designer).select_related(
            "designer", "catalog", "client"
        )
        return JsonResponse(
            {"items": [_moodboard_data(board) for board in boards]}
        )

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
            id=catalog_id,
            designer=designer,
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
    moodboard = Moodboard.objects.filter(
        id=moodboard_id,
        designer=Designer.objects.get(user=cast(User, request.user)),
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
    filename = f"moodboard-{moodboard.pk}.png"
    return FileResponse(output, as_attachment=True, filename=filename)
