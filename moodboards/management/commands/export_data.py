import argparse
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from moodboards.models import Designer
from moodboards.storage import DEFAULT_DATA_PATH, export_data


class Command(BaseCommand):
    help = "Экспортирует данные дизайнера в JSON."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("username")
        parser.add_argument("--file", default=str(DEFAULT_DATA_PATH))

    def handle(self, *args: Any, **options: Any) -> None:
        designer = Designer.objects.filter(user__username=options["username"]).first()
        if designer is None:
            raise CommandError("Дизайнер не найден.")
        path = export_data(designer, options["file"])
        self.stdout.write(self.style.SUCCESS(f"Данные сохранены в {path}"))
