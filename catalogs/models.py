from typing import Any

from django.db import models

from accounts.models import Designer


class MoodboardCatalog(models.Model):
    designer = models.ForeignKey(
        Designer,
        on_delete=models.CASCADE,
        related_name="catalogs",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "moodboards_moodboardcatalog"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["designer", "name"],
                name="unique_catalog_per_designer",
            )
        ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def belongs_to(self, designer: Designer) -> bool:
        return self.designer == designer


__all__ = ["MoodboardCatalog"]
