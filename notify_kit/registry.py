from threading import RLock

_LOCK = RLock()
NOTIFICATION_TOPICS: dict[str, dict] = {}


def register_notification_topic(
    key: str,
    label: str,
    description: str = "",
    icon: str = "bi-bell",
    default_enabled: bool = True,
    staff_only: bool = False,
) -> dict:
    """Register a notification topic so users can opt in/out in /notifications/."""
    clean_key = (key or "").strip()
    if not clean_key:
        raise ValueError("Notification topic key must not be empty.")
    entry = {
        "key": clean_key,
        "label": label or clean_key,
        "description": description or "",
        "icon": icon or "bi-bell",
        "default_enabled": bool(default_enabled),
        "staff_only": bool(staff_only),
    }
    with _LOCK:
        NOTIFICATION_TOPICS[clean_key] = entry
    return entry


def get_topic(key: str) -> dict | None:
    if not key:
        return None
    with _LOCK:
        entry = NOTIFICATION_TOPICS.get(key)
        return dict(entry) if entry else None


def get_registered_topics(user=None) -> list[dict]:
    is_staff = bool(getattr(user, "is_staff", False)) if user is not None else True
    with _LOCK:
        topics = [
            dict(entry)
            for entry in NOTIFICATION_TOPICS.values()
            if is_staff or not entry.get("staff_only", False)
        ]
    return topics
