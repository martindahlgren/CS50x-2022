
from django.urls import path
from django.views.generic import TemplateView


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("match", views.match_view, name="match"),
    path("chat", views.chat_view, name="chat"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile", views.edit_profile, name="profile"),
    path("unmatch", views.unmatch_user),
    path("suggest_cities", views.suggest_cities),
    path("get_candidates", views.get_candidates),
    path("send_swipe", views.send_swipe),
    path("test", TemplateView.as_view(template_name="app/testpage.html")),
]
