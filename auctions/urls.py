from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing_view, name="create_listing"),
    path("listing/<int:listing_key>", views.listing, name="listing"),
    path("post-bid/<int:listing_key>", views.post_bid, name="post_bid"),
    path("watch-toggle/<int:listing_key>", views.watch_toggle, name="watch_toggle"),
    path("close-bid/<int:listing_key>", views.close_bid, name="close_bid"),
    path("add-comment/<int:listing_key>", views.add_comment, name="add_comment"),
    path("watchlist", views.watchlist, name="watchlist"),
]
