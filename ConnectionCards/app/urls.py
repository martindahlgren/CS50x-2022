
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("unmatch", views.unmatch_user),
    path("suggest_cities", views.suggest_cities)

]
