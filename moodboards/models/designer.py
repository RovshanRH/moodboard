from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import User
from django.db import models

if TYPE_CHECKING:
    from .catalog import MoodboardCatalog
    from .moodboard import Moodboard


class Designer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="designer",
    )
    display_name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.display_name

    def owns_catalog(self, catalog: "MoodboardCatalog") -> bool:
        return catalog.designer == self

    def owns_moodboard(self, moodboard: "Moodboard") -> bool:
        return moodboard.designer == self
