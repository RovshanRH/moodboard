from io import BytesIO
import json
from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
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


def _moodboard_data(moodboard: Moodboard) -> dict:
    return {
        "id": moodboard.id,
        "title": moodboard.title,
        "description": moodboard.description,
        "background_color": moodboard.background_color,
        "designer": {
            "id": moodboard.designer_id,
            "name": moodboard.designer.display_name,
        },
        "catalog": (
            {"id": moodboard.catalog_id, "name": moodboard.catalog.name}
            if moodboard.catalog
            else None
        ),
        "client": (
            {"id": moodboard.client_id, "name": moodboard.client.name}
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

        username = data.get("username", "").strip()
        password = data.get("password", "")
        display_name = data.get("display_name", username).strip()
        if not username or not password or not display_name:
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
            designer = user.designer
            return JsonResponse(
                {
                    "id": designer.id,
                    "username": user.username,
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
                "id": designer.id,
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

    designer = request.user.designer
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

    title = data.get("title", "").strip()
    if not title:
        return JsonResponse(
            {"error": "Название мудборда обязательно."},
            status=400,
        )

    catalog = None
    catalog_id = data.get("catalog_id")
    if catalog_id is not None:
        catalog = MoodboardCatalog.objects.filter(
            id=catalog_id,
            designer=designer,
        ).first()
        if catalog is None:
            return JsonResponse({"error": "Каталог не найден."}, status=404)

    client = None
    client_id = data.get("client_id")
    if client_id is not None:
        client = Client.objects.filter(id=client_id).first()
        if client is None:
            return JsonResponse({"error": "Заказчик не найден."}, status=404)

    moodboard = Moodboard.objects.create(
        designer=designer,
        catalog=catalog,
        client=client,
        title=title,
        description=data.get("description", "").strip(),
        background_color=data.get("background_color", "#F4EFE6"),
    )
    return JsonResponse(_moodboard_data(moodboard), status=201)


def moodboard_export(
    request: HttpRequest,
    moodboard_id: int,
) -> FileResponse | JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Требуется авторизация."}, status=401)
    moodboard = Moodboard.objects.filter(
        id=moodboard_id,
        designer=request.user.designer,
    ).first()
    if moodboard is None:
        return JsonResponse({"error": "Мудборд не найден."}, status=404)

    image = Image.new("RGB", (1600, 1000), moodboard.background_color)
    draw = ImageDraw.Draw(image)
    draw.text((100, 100), moodboard.title, fill="#1E1E1E")
    if moodboard.description:
        draw.text((100, 180), moodboard.description, fill="#3D3D3D")
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    filename = f"moodboard-{moodboard.id}.png"
    return FileResponse(output, as_attachment=True, filename=filename)
