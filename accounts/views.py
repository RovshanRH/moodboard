import json
from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import Client, Designer


def register_page(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        display_name = request.POST.get("display_name", "").strip()
        role = request.POST.get("role", "designer")
        email = request.POST.get("email", "").strip()
        if not username or not password or not display_name:
            error = "Заполните имя пользователя, пароль и отображаемое имя."
        elif role not in {"designer", "client"}:
            error = "Выберите корректную роль."
        elif role == "client" and not email:
            error = "Для заказчика нужен email."
        elif User.objects.filter(username=username).exists():
            error = "Пользователь с таким именем уже существует."
        elif role == "client" and Client.objects.filter(email=email).exists():
            error = "Этот email уже зарегистрирован."
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
            )
            if role == "designer":
                Designer.objects.create(user=user, display_name=display_name)
            else:
                Client.objects.create(user=user, name=display_name, email=email)
            login(request, user)
            return redirect("home")
    return render(request, "moodboards/register.html", {"error": error})


def login_page(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", "").strip(),
            password=request.POST.get("password", ""),
        )
        if user is not None:
            login(request, user)
            return redirect("home")
        error = "Неверное имя пользователя или пароль."
    return render(request, "moodboards/login.html", {"error": error})


def logout_page(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        logout(request)
    return redirect("home")


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
def auth_view(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        data = _json_body(request)
        if data is None:
            return JsonResponse({"error": "Некорректный JSON."}, status=400)

        username = _text_value(data, "username")
        password = data.get("password", "")
        display_name = _text_value(data, "display_name", username or "")
        role = _text_value(data, "role", "designer")
        email = _text_value(data, "email")
        company = _text_value(data, "company", "")
        if (
            not username
            or not isinstance(password, str)
            or not password
            or not display_name
            or role not in {"designer", "client"}
        ):
            return JsonResponse(
                {
                    "error": (
                        "Нужны username, password, display_name и role "
                        "(designer или client)."
                    )
                },
                status=400,
            )
        if role == "client" and not email:
            return JsonResponse(
                {"error": "Для регистрации заказчика нужен email."},
                status=400,
            )
        if role == "client" and Client.objects.filter(email=email).exists():
            return JsonResponse(
                {"error": "Этот email уже зарегистрирован."}, status=400
            )
        if User.objects.filter(username=username).exists():
            user = authenticate(request, username=username, password=password)
            if user is None:
                return JsonResponse(
                    {"error": "Неверные данные входа."},
                    status=401,
                )
            login(request, user)
            designer = Designer.objects.filter(user=user).first()
            client = Client.objects.filter(user=user).first()
            profile = designer or client
            if profile is None:
                return JsonResponse(
                    {"error": "У пользователя нет профиля."}, status=409
                )
            return JsonResponse(
                {
                    "id": profile.pk,
                    "username": user.get_username(),
                    "display_name": (
                        designer.display_name if designer else client.name
                    ),
                    "role": "designer" if designer else "client",
                }
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email or "",
        )
        if role == "designer":
            profile = Designer.objects.create(user=user, display_name=display_name)
        else:
            profile = Client.objects.create(
                user=user,
                name=display_name,
                email=email or "",
                company=company or "",
            )
        login(request, user)
        return JsonResponse(
            {
                "id": profile.pk,
                "username": user.username,
                "display_name": display_name,
                "role": role,
            },
            status=201,
        )

    if request.method == "DELETE":
        logout(request)
        return JsonResponse({"detail": "Вы вышли из системы."})

    return JsonResponse({"error": "Метод не поддерживается."}, status=405)
