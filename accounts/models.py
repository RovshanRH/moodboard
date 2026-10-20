from typing import Any

from django.contrib.auth.models import User
from django.db import models


class Designer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="designer",
    )
    display_name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)

    class Meta:
        db_table = "moodboards_designer"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.display_name

    def owns_catalog(self, catalog: Any) -> bool:
        return catalog.designer == self

    def owns_moodboard(self, moodboard: Any) -> bool:
        return moodboard.designer == self


class Client(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="client",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=160)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=160, blank=True)

    class Meta:
        db_table = "moodboards_client"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def contact_label(self) -> str:
        return f"{self.name} <{self.email}>"


__all__ = ["Client", "Designer"]
