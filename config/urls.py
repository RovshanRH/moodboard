from django.contrib import admin
from django.urls import include, path

from moodboards.views import home_page


urlpatterns = [
    path("", home_page, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("moodboards.api_urls")),
    path("", include("moodboards.urls", namespace="moodboards")),
]

handler404 = "moodboards.views.page_not_found"
