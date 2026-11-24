from django.urls import path

from . import views

app_name = "notify_kit"

urlpatterns = [
    path("", views.inbox_view, name="inbox"),
    path("preferences/", views.preferences_view, name="preferences"),
    path("read/<int:pk>/", views.mark_read_view, name="mark_read"),
    path("read-all/", views.mark_all_read_view, name="mark_all_read"),
    path("delete/<int:pk>/", views.delete_notification_view, name="delete"),
    path("delete-read/", views.delete_read_notifications_view, name="delete_read"),
    path("unread.json", views.unread_json_view, name="unread_json"),
]
