import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0001_initial")]
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="MoodboardCatalog",
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
                        ("name", models.CharField(max_length=120)),
                        ("description", models.TextField(blank=True)),
                        (
                            "designer",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="catalogs",
                                to="accounts.designer",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "moodboards_moodboardcatalog",
                        "ordering": ["name"],
                    },
                ),
                migrations.AddConstraint(
                    model_name="moodboardcatalog",
                    constraint=models.UniqueConstraint(
                        fields=("designer", "name"),
                        name="unique_catalog_per_designer",
                    ),
                ),
            ],
            database_operations=[],
        )
    ]
