from typing import Any

from django.core.validators import RegexValidator
from django.db import models

from .catalog import MoodboardCatalog
from .client import Client
from .designer import Designer


class Moodboard(models.Model):
    HEX_COLOR = RegexValidator(
        regex=r"^#[0-9A-Fa-f]{6}$",
        message="Цвет должен быть в формате #RRGGBB.",
    )

    designer = models.ForeignKey(
        Designer,
        on_delete=models.CASCADE,
        related_name="moodboards",
    )
    catalog = models.ForeignKey(
        MoodboardCatalog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moodboards",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moodboards",
    )
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    background_color = models.CharField(
        max_length=7,
        default="#F4EFE6",
        validators=[HEX_COLOR],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.designer})"

    def can_use_catalog(self, catalog: MoodboardCatalog) -> bool:
        return catalog.designer == self.designer

    def assign_catalog(self, catalog: MoodboardCatalog | None) -> None:
        if catalog is not None and not self.can_use_catalog(catalog):
            raise ValueError("Каталог принадлежит другому дизайнеру.")
        self.catalog = catalog

    def assign_client(self, client: Client | None) -> None:
        self.client = client

    def change_background(self, color: str) -> None:
        self.background_color = color
        self.full_clean()

    def to_data(self) -> dict[str, str | None]:
        return {
            "title": self.title,
            "description": self.description,
            "background_color": self.background_color,
            "catalog": self.catalog.name if self.catalog else None,
            "client_email": self.client.email if self.client else None,
        }
