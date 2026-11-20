from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("notify_kit", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="topic",
            field=models.CharField(blank=True, db_index=True, default="", max_length=80),
        ),
        migrations.CreateModel(
            name="NotificationPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("disabled_topics_json", models.JSONField(blank=True, default=list)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notify_kit_preference",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
