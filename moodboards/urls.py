from django.urls import path

from .views import (
    catalog_pages,
    client_pages,
    moodboard_detail_page,
    moodboard_pages,
)


urlpatterns = [
    path("moodboards/", moodboard_pages, name="moodboard-pages"),
    path(
        "moodboards/<int:moodboard_id>/",
        moodboard_detail_page,
        name="moodboard-detail",
    ),
    path("catalogs/", catalog_pages, name="catalog-pages"),
    path("clients/", client_pages, name="client-pages"),
]
