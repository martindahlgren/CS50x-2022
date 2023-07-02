
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:page>", views.index, name="index"),
    path("index", views.index, name="index"),
    path("index/<int:page>", views.index, name="index"),
    path("following", views.following, name="following"),
    path("following/<int:page>", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("like", views.like, name="like"),
    path("user/<str:viewed_user>", views.user, name="user"),
    path("user/<str:viewed_user>/<int:page>", views.user, name="user"),
    path("follow/user/<str:viewed_user>", views.follow_toggle, name="follow_toggle"),

]
