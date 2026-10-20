from django.urls import path

from accounts.views import auth_view
from boards.views import moodboard_export, moodboard_list
from catalogs.views import catalog_list


urlpatterns = [
    path("auth/", auth_view, name="auth"),
    path("moodboards/", moodboard_list, name="moodboard-list"),
    path("catalogs/", catalog_list, name="catalog-list"),
    path(
        "moodboards/<int:moodboard_id>/export/",
        moodboard_export,
        name="moodboard-export",
    ),
]
