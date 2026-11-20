import json
import urllib.request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Notification, NotificationPreference
from .registry import get_topic


def send_themed_email(to_emails, subject, title, message, link="", primary_color="#0d6efd"):
    recipients = [e for e in (to_emails if isinstance(to_emails, (list, tuple)) else [to_emails]) if e]
    if not recipients:
        return 0
    app_name = getattr(settings, "DESIGN_STUDIO_APP_NAME", "App")
    html_body = render_to_string(
        "notify_kit/email/themed_notification.html",
        {
            "app_name": app_name,
            "title": title,
            "message": message,
            "link": link,
            "primary_color": primary_color,
        },
    )
    text_body = strip_tags(html_body)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
        to=recipients,
    )
    msg.attach_alternative(html_body, "text/html")
    return msg.send(fail_silently=False)


def send_webhook(url: str, title: str, message: str = "", level: str = "info", timeout: int = 5) -> bool:
    if not url:
        return False
    payload = json.dumps({"title": title, "message": message, "level": level}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Title": title[:100],
            "Priority": "high" if level == "danger" else "default",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return 200 <= resp.status < 300


def is_topic_enabled_for_user(user, topic_key: str) -> bool:
    if not topic_key or user is None:
        return True
    topic_meta = get_topic(topic_key)
    pref = NotificationPreference.objects.filter(user=user).first()
    if pref is None:
        return bool(topic_meta.get("default_enabled", True)) if topic_meta else True
    return topic_key not in set(pref.disabled_topics_json or [])


def notify(
    user,
    title: str,
    message: str = "",
    level: str = "info",
    link: str = "",
    email: bool = False,
    webhook_url: str = "",
    topic: str = "",
    body: str = "",
):
    clean_topic = (topic or "").strip()[:80]
    if clean_topic and not is_topic_enabled_for_user(user, clean_topic):
        return None
    text = message if message else body
    notif = Notification.objects.create(
        user=user,
        title=title[:140],
        message=text,
        level=level if level in ("info", "success", "warning", "danger") else "info",
        topic=clean_topic,
        link=link[:255],
    )
    if email and getattr(user, "email", ""):
        send_themed_email(user.email, title, title, text, link=link)
    target_hook = webhook_url or getattr(settings, "NOTIFY_KIT_WEBHOOK_URL", "")
    if target_hook:
        try:
            send_webhook(target_hook, title, text, level=level)
        except Exception:
            pass
    return notif


send_notification = notify
