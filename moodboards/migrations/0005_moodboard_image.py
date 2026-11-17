from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("moodboards", "0004_remove_legacy_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="moodboard",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="moodboards/"),
        ),
    ]
