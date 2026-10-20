from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("moodboards", "0003_client_user"),
        ("accounts", "0001_initial"),
        ("catalogs", "0001_initial"),
        ("boards", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="Moodboard"),
                migrations.DeleteModel(name="MoodboardCatalog"),
                migrations.DeleteModel(name="Client"),
                migrations.DeleteModel(name="Designer"),
            ],
            database_operations=[],
        )
    ]
