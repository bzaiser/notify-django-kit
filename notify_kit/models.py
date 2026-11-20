from django.conf import settings
from django.db import models


class Notification(models.Model):
    LEVEL_CHOICES = [
        ("info", "Info"),
        ("success", "Erfolg"),
        ("warning", "Warnung"),
        ("danger", "Fehler"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notify_kit_notifications",
    )
    title = models.CharField(max_length=140)
    message = models.TextField(blank=True, default="")
    level = models.CharField(max_length=16, choices=LEVEL_CHOICES, default="info")
    topic = models.CharField(max_length=80, blank=True, default="", db_index=True)
    link = models.CharField(max_length=255, blank=True, default="")
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.level}] {self.title}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notify_kit_preference",
    )
    disabled_topics_json = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences({self.user})"
