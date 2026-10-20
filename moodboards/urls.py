from django.urls import path

from accounts.views import login_page, register_page
from boards.views import (
    moodboard_detail_page,
    moodboard_pages,
    moodboard_search,
    moodboard_statistics,
)
from catalogs.views import catalog_pages, client_pages

app_name = "moodboards"

urlpatterns = [
    path("register/", register_page, name="register"),
    path("login/", login_page, name="login"),
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
