from django.contrib import admin
from django.db.models import Count

from accounts.models import Client, Designer
from boards.models import Moodboard
from catalogs.models import MoodboardCatalog


class MoodboardInline(admin.TabularInline):
    model = Moodboard
    extra = 0
    fields = ("title", "background_color", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(Designer)
class DesignerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "bio")
    search_fields = ("display_name", "user__username", "user__email")
    ordering = ("display_name",)
    list_per_page = 20
    inlines = (MoodboardInline,)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "moodboard_count")
    search_fields = ("name", "email", "company")
    ordering = ("name",)
    list_per_page = 20
    inlines = (MoodboardInline,)

    @admin.display(description="Мудбордов")
    def moodboard_count(self, obj: Client) -> int:
        return obj.moodboard_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            moodboard_count=Count("moodboards")
        )


@admin.register(MoodboardCatalog)
class MoodboardCatalogAdmin(admin.ModelAdmin):
    list_display = ("name", "designer", "moodboard_count")
    search_fields = ("name", "description", "designer__display_name")
    list_filter = ("designer",)
    ordering = ("name",)
    list_per_page = 20
    inlines = (MoodboardInline,)

    @admin.display(description="Мудбордов")
    def moodboard_count(self, obj: MoodboardCatalog) -> int:
        return obj.moodboard_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            moodboard_count=Count("moodboards")
        )


@admin.register(Moodboard)
class MoodboardAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "designer",
        "catalog",
        "client",
        "background_color",
        "updated_at",
    )
    search_fields = (
        "title",
        "description",
        "designer__display_name",
        "catalog__name",
        "client__name",
        "client__email",
    )
    list_filter = ("designer", "catalog", "background_color")
    date_hierarchy = "updated_at"
    ordering = ("-updated_at",)
    list_per_page = 20
    readonly_fields = ("created_at", "updated_at")
