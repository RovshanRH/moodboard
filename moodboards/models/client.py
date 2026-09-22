from typing import Any

from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=160)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=160, blank=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def contact_label(self) -> str:
        return f"{self.name} <{self.email}>"
