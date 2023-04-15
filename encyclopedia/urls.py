from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.wikipage, name="wikipage"),
    path("search", views.search, name="search"),
    path("new", views.new, name="new")
]
