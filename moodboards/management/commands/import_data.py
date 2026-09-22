import argparse
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from moodboards.models import Designer
from moodboards.storage import DEFAULT_DATA_PATH, import_data


class Command(BaseCommand):
    help = "Загружает данные дизайнера из JSON."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("username")
        parser.add_argument("--file", default=str(DEFAULT_DATA_PATH))

    def handle(self, *args: Any, **options: Any) -> None:
        designer = Designer.objects.filter(user__username=options["username"]).first()
        if designer is None:
            raise CommandError("Дизайнер не найден.")
        try:
            imported = import_data(designer, options["file"])
        except ValueError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(self.style.SUCCESS(f"Загружено мудбордов: {imported}"))
