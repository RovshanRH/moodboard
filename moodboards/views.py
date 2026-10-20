from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import query_one

from boards.models import Moodboard


def home_page(request: HttpRequest) -> HttpResponse:
    summary = query_one("SELECT COUNT(*) AS moodboard_count FROM moodboards")
    moodboard_count = (
        summary["moodboard_count"]
        if summary is not None
        else Moodboard.objects.count()
    )
    return render(
        request,
        "moodboards/home.html",
        {"moodboard_count": moodboard_count},
    )


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "404.html", status=404)
