from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .models import Notification, NotificationPreference
from .registry import get_registered_topics, get_topic
from .services import is_topic_enabled_for_user


@login_required
def inbox_view(request):
    items = list(Notification.objects.filter(user=request.user)[:100])
    for item in items:
        meta = get_topic(item.topic) if item.topic else None
        item.topic_label = meta["label"] if meta else ""
        item.topic_icon = meta["icon"] if meta else ""

    topics = []
    for t in get_registered_topics(request.user):
        t_copy = dict(t)
        t_copy["enabled"] = is_topic_enabled_for_user(request.user, t["key"])
        topics.append(t_copy)

    active_tab = request.GET.get("tab") or "inbox"
    return render(
        request,
        "notify_kit/inbox.html",
        {
            "notifications": items,
            "topics": topics,
            "active_tab": active_tab,
            "unread_count": sum(1 for i in items if not i.is_read),
        },
    )


@login_required
@require_POST
def preferences_view(request):
    enabled = set(request.POST.getlist("enabled_topics"))
    visible_topics = get_registered_topics(request.user)
    pref, _created = NotificationPreference.objects.get_or_create(user=request.user)
    disabled = set(pref.disabled_topics_json or [])
    for t in visible_topics:
        key = t["key"]
        if key in enabled:
            disabled.discard(key)
        else:
            disabled.add(key)
    pref.disabled_topics_json = sorted(disabled)
    pref.save(update_fields=["disabled_topics_json", "updated_at"])
    messages.success(request, _("Meldungs-Einstellungen gespeichert."))
    return redirect(f"{reverse('notify_kit:inbox')}?tab=settings")


@login_required
@require_POST
def mark_read_view(request, pk):
    item = get_object_or_404(Notification, pk=pk, user=request.user)
    item.is_read = True
    item.save(update_fields=["is_read"])
    if item.link:
        return redirect(item.link)
    return redirect("notify_kit:inbox")


@login_required
@require_POST
def mark_all_read_view(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notify_kit:inbox")


@login_required
def unread_json_view(request):
    qs = Notification.objects.filter(user=request.user, is_read=False)
    return JsonResponse({
        "unread_count": qs.count(),
        "items": list(qs.values("id", "title", "level", "link", "created_at")[:10]),
    })
