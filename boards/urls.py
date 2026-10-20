from django.urls import path

from .views import (
    moodboard_detail_page,
    moodboard_export,
    moodboard_list,
    moodboard_create_page,
    moodboard_pages,
)


app_name = "boards"

urlpatterns = [
    path("moodboards/", moodboard_pages, name="list"),
    path("moodboards/create/", moodboard_create_page, name="create"),
    path("moodboards/<int:moodboard_id>/", moodboard_detail_page, name="detail"),
    path("api/moodboards/", moodboard_list, name="api-list"),
    path(
        "api/moodboards/<int:moodboard_id>/export/",
        moodboard_export,
        name="api-export",
    ),
]
