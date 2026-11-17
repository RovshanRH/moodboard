from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from boards.models import Moodboard


def home_page(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "moodboards/home.html",
        {"moodboard_count": Moodboard.objects.count()},
    )


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "404.html", status=404)
