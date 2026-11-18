from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def inbox_view(request):
    items = Notification.objects.filter(user=request.user)[:100]
    return render(request, "notify_kit/inbox.html", {"notifications": items})


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
