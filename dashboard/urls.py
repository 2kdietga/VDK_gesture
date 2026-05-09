from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("entertainment/", views.entertainment, name="entertainment"),
    path("config/save/", views.save_config, name="save_config"),
    path("command/send/", views.send_command, name="send_command"),
    path("api/state/", views.state_api, name="state_api"),
]
