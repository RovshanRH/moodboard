import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import boards.models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("accounts", "0001_initial"),
        ("catalogs", "0001_initial"),
    ]
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Moodboard",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        ("title", models.CharField(max_length=160)),
                        ("description", models.TextField(blank=True)),
                        (
                            "background_color",
                            models.CharField(
                                default="#F4EFE6",
                                max_length=7,
                                validators=[
                                    django.core.validators.RegexValidator(
                                        message="Цвет должен быть в формате #RRGGBB.",
                                        regex="^#[0-9A-Fa-f]{6}$",
                                    )
                                ],
                            ),
                        ),
                        (
                            "palette",
                            models.JSONField(
                                blank=True,
                                default=list,
                                validators=[boards.models.validate_palette],
                            ),
                        ),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        (
                            "client",
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=django.db.models.deletion.SET_NULL,
                                related_name="moodboards",
                                to="accounts.client",
                            ),
                        ),
                        (
                            "designer",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="moodboards",
                                to="accounts.designer",
                            ),
                        ),
                        (
                            "catalog",
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=django.db.models.deletion.SET_NULL,
                                related_name="moodboards",
                                to="catalogs.moodboardcatalog",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "moodboards_moodboard",
                        "ordering": ["-updated_at"],
                    },
                )
            ],
            database_operations=[],
        )
    ]
