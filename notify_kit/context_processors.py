from .models import Notification


def notify_context(request):
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return {"notify_unread_count": 0, "notify_recent": []}
    qs = Notification.objects.filter(user=user)
    return {
        "notify_unread_count": qs.filter(is_read=False).count(),
        "notify_recent": list(qs[:5]),
    }
