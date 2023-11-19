
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("match", views.match_view, name="match"),
    path("chat", views.chat_view, name="chat"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile", views.profile_view, name="profile"),
    path("profileupdate", views.profile_update, name="profileupdate"),
    path("upload_picture", views.upload_picture, name="upload_picture"),

    path("unmatch", views.unmatch_user),
    path("suggest_cities", views.suggest_cities),
    path("get_candidates", views.get_candidates),
    path("send_swipe", views.send_swipe),
    path("test", TemplateView.as_view(template_name="app/testpage.html")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
