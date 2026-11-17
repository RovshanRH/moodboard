from io import BytesIO
import json
from typing import Any, cast

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Value
from django.db.models.functions import Coalesce
from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageDraw

from accounts.models import Client, Designer
from catalogs.models import MoodboardCatalog

from .forms import MoodboardForm, MoodboardSearchForm
from .models import Moodboard


def moodboard_pages(request: HttpRequest) -> HttpResponse:
    boards = Moodboard.objects.with_related()
    page_obj = Paginator(boards, 6).get_page(request.GET.get("page"))
    return render(
        request,
        "moodboards/moodboards.html",
        {"moodboards": page_obj, "page_obj": page_obj},
    )


def moodboard_create_page(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("moodboards:login")

    designer = Designer.objects.filter(user=cast(User, request.user)).first()
    if designer is None:
        return redirect("moodboards:login")

    form = MoodboardForm(designer=designer)
    if request.method == "POST":
        form = MoodboardForm(request.POST, request.FILES, designer=designer)
        if form.is_valid():
            moodboard = form.save(commit=False)
            moodboard.designer = designer
            moodboard.save()
            return redirect("moodboards:detail", moodboard_id=moodboard.pk)

    return render(
        request,
        "moodboards/moodboard_form.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


def moodboard_edit_page(request: HttpRequest, moodboard_id: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("moodboards:login")

    designer = Designer.objects.filter(user=cast(User, request.user)).first()
    if designer is None:
        return redirect("moodboards:login")

    moodboard = get_object_or_404(Moodboard, pk=moodboard_id, designer=designer)
    form = MoodboardForm(instance=moodboard, designer=designer)
    if request.method == "POST":
        form = MoodboardForm(
            request.POST,
            request.FILES,
            instance=moodboard,
            designer=designer,
        )
        if form.is_valid():
            moodboard = form.save()
            return redirect("moodboards:detail", moodboard_id=moodboard.pk)

    return render(
        request,
        "moodboards/moodboard_form.html",
        {
            "form": form,
            "is_edit": True,
            "moodboard": moodboard,
        },
    )


def moodboard_delete_page(request: HttpRequest, moodboard_id: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("moodboards:login")

    designer = Designer.objects.filter(user=cast(User, request.user)).first()
    if designer is None:
        return redirect("moodboards:login")

    moodboard = get_object_or_404(Moodboard, pk=moodboard_id, designer=designer)
    if request.method == "POST":
        moodboard.delete()
        return redirect("moodboards:list")

    return redirect("moodboards:detail", moodboard_id=moodboard.pk)


def moodboard_detail_page(
    request: HttpRequest,
    moodboard_id: int,
) -> HttpResponse:
    board = get_object_or_404(
        Moodboard.objects.with_related(),
        pk=moodboard_id,
    )
    return render(request, "moodboards/moodboard_detail.html", {"moodboard": board})


def moodboard_search(request: HttpRequest) -> HttpResponse:
    form = MoodboardSearchForm(request.GET)
    query = ""
    if form.is_valid():
        query = (form.cleaned_data.get("q") or "").strip()
    boards = (
        Moodboard.objects.with_related()
        .search(query)
        .order_by("title")
    )
    page_obj = Paginator(boards, 6).get_page(request.GET.get("page"))
    return render(
        request,
        "moodboards/search.html",
        {
            "moodboards": page_obj,
            "page_obj": page_obj,
            "query": query,
            "form": form,
        },
    )


def moodboard_statistics(request: HttpRequest) -> HttpResponse:
    summary = Moodboard.objects.aggregate(
        moodboard_count=Count("id"),
        designer_count=Count("designer_id", distinct=True),
        client_count=Count("client_id", distinct=True),
    )
    by_catalog = (
        Moodboard.objects.values("catalog_id", "catalog__name")
        .annotate(
            catalog_name=Coalesce("catalog__name", Value("Без каталога")),
            moodboard_count=Count("id"),
        )
        .order_by("-moodboard_count")
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
        boards = Moodboard.objects.for_designer(designer).with_related()
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
