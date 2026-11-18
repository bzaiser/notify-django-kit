# notify-django-kit

Wiederverwendbares Benachrichtigungs-, HTML-Mail- & Webhook-Paket (ntfy / Gotify / JSON) für Django + `django-design-studio`.

## Installation
```bash
pip install --no-user --upgrade --no-cache-dir git+https://github.com/bzaiser/notify-django-kit.git@main
```

```python
INSTALLED_APPS = [..., "design_studio", "notify_kit"]
TEMPLATES[0]["OPTIONS"]["context_processors"] += ["notify_kit.context_processors.notify_context"]
# urls.py
path("notifications/", include("notify_kit.urls")),
```
