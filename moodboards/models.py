from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Designer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="designer",
    )
    display_name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.display_name


class Client(models.Model):
    name = models.CharField(max_length=160)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=160, blank=True)

    def __str__(self) -> str:
        return self.name


class MoodboardCatalog(models.Model):
    designer = models.ForeignKey(
        Designer,
        on_delete=models.CASCADE,
        related_name="catalogs",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["designer", "name"],
                name="unique_catalog_per_designer",
            )
        ]

    def __str__(self) -> str:
        return self.name


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

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.designer})"

    def can_use_catalog(self, catalog: MoodboardCatalog) -> bool:
        return catalog.designer_id == self.designer_id
