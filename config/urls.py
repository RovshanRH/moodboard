from django.contrib import admin
from django.urls import include, path

from moodboards.views import home_page


urlpatterns = [
    path("", home_page, name="home"),
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("boards.urls")),
    path("", include("catalogs.urls")),
    path("", include("moodboards.urls", namespace="moodboards")),
]

handler404 = "moodboards.views.page_not_found"
