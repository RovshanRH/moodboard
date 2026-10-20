from django.urls import path

from .views import catalog_list, catalog_pages, client_pages


app_name = "catalogs"

urlpatterns = [
    path("catalogs/", catalog_pages, name="list"),
    path("clients/", client_pages, name="clients"),
    path("api/catalogs/", catalog_list, name="api-list"),
]
