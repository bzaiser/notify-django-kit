import os
import sys

import django
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import Client, TestCase

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS_DIR = os.path.join(os.path.dirname(BASE_DIR), "django-design-studio")
for p in (BASE_DIR, DS_DIR):
    if p not in sys.path and os.path.isdir(p):
        sys.path.insert(0, p)

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-notify-kit",
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "design_studio",
            "notify_kit",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        ROOT_URLCONF="tests.test_notify_kit",
        TEMPLATES=[{
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "design_studio.context_processors.theme_context",
                    "notify_kit.context_processors.notify_context",
                ],
            },
        }],
        STATIC_URL="/static/",
    )
    django.setup()

from django.contrib.auth import get_user_model
from django.urls import include, path
from notify_kit.services import notify

urlpatterns = [
    path("design-studio/", include("design_studio.urls")),
    path("notifications/", include("notify_kit.urls")),
]


class NotifyKitTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="bob", password="pw", email="bob@example.com")
        self.client = Client()
        self.client.force_login(self.user)

    def test_in_app_notification_email_and_mark_read(self):
        n = notify(self.user, "Backup fertig", "Alle Daten gesichert.", level="success", email=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Backup fertig", mail.outbox[0].subject)

        inbox = self.client.get("/notifications/")
        self.assertEqual(inbox.status_code, 200)
        self.assertIn("Backup fertig", inbox.content.decode("utf-8"))

        unread = self.client.get("/notifications/unread.json").json()
        self.assertEqual(unread["unread_count"], 1)

        self.client.post(f"/notifications/read/{n.pk}/")
        self.assertEqual(self.client.get("/notifications/unread.json").json()["unread_count"], 0)


if __name__ == "__main__":
    from django.test.runner import DiscoverRunner
    call_command("migrate", verbosity=0)
    runner = DiscoverRunner(verbosity=2)
    sys.exit(bool(runner.run_tests(["tests.test_notify_kit"])))
