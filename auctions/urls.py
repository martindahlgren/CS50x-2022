from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing_view, name="create_listing"),
    path("listing/<int:listing_key>", views.listing, name="listing"),
    path("watch-toggle/<int:listing_key>", views.watch_toggle, name="watch_toggle"),
]