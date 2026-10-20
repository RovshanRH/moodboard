import re
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from accounts.models import Client, Designer
from catalogs.models import MoodboardCatalog

HEX_COLOR_RE = r"^#[0-9A-Fa-f]{6}$"


def validate_palette(value: list[str]) -> None:
    if not isinstance(value, list):
        raise ValidationError("Палитра должна быть списком цветов.")
    for color in value:
        if not isinstance(color, str) or not re.fullmatch(
            HEX_COLOR_RE[1:-1], color
        ):
            raise ValidationError("Каждый цвет должен быть в формате #RRGGBB.")


class Moodboard(models.Model):
    HEX_COLOR = RegexValidator(
        regex=HEX_COLOR_RE,
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
    palette = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_palette],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "moodboards_moodboard"
        ordering = ["-updated_at"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

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


__all__ = ["Moodboard", "validate_palette"]
