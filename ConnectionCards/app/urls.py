
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("unmatch", views.unmatch_user),
    path("suggest_cities", views.suggest_cities),
    path("test", TemplateView.as_view(template_name="app/testpage.html")),

]
