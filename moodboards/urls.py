from django.urls import path

from .views import (
    catalog_pages,
    client_pages,
    moodboard_detail_page,
    moodboard_pages,
    moodboard_search,
    moodboard_statistics,
)

app_name = "moodboards"

urlpatterns = [
    path("moodboards/", moodboard_pages, name="list"),
    path(
        "moodboards/<int:moodboard_id>/",
        moodboard_detail_page,
        name="detail",
    ),
    path("catalogs/", catalog_pages, name="catalogs"),
    path("clients/", client_pages, name="clients"),
    path("search/", moodboard_search, name="search"),
    path("statistics/", moodboard_statistics, name="statistics"),
]
