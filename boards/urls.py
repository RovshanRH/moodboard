from django.urls import path

from .views import (
    moodboard_create_page,
    moodboard_delete_page,
    moodboard_detail_page,
    moodboard_edit_page,
    moodboard_export,
    moodboard_list,
    moodboard_pages,
)


app_name = "boards"

urlpatterns = [
    path("moodboards/", moodboard_pages, name="list"),
    path("moodboards/create/", moodboard_create_page, name="create"),
    path(
        "moodboards/<int:moodboard_id>/edit/",
        moodboard_edit_page,
        name="edit",
    ),
    path(
        "moodboards/<int:moodboard_id>/delete/",
        moodboard_delete_page,
        name="delete",
    ),
    path("moodboards/<int:moodboard_id>/", moodboard_detail_page, name="detail"),
    path("api/moodboards/", moodboard_list, name="api-list"),
    path(
        "api/moodboards/<int:moodboard_id>/export/",
        moodboard_export,
        name="api-export",
    ),
]
