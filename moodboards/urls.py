from django.urls import path

from .views import auth_view, moodboard_export, moodboard_list


urlpatterns = [
    path("auth/", auth_view, name="auth"),
    path("moodboards/", moodboard_list, name="moodboard-list"),
    path(
        "moodboards/<int:moodboard_id>/export/",
        moodboard_export,
        name="moodboard-export",
    ),
]
