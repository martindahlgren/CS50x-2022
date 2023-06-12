import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.core.paginator import Paginator

from . import models

def index(request, page=1):
    latest = request.GET.get("latest")
    if latest is not None:
        posts_query = models.Post.objects.filter(id__lte = int(latest)).order_by('-id')
    else:
        posts_query = models.Post.objects.all().order_by('-id')
        latest = posts_query.first().id
    p = Paginator(posts_query, 10)
    page_obj = p.page(page)

    return render(request, "network/index.html", {'page_obj': page_obj, "show_new": True, "latest": latest})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required
@require_POST
def post(request):
    data = json.loads(request.body)
    user = request.user
    post_pody = data["post"]
    if post_pody == "":
        return JsonResponse({"error": "Empty Post"}, status=400)
    new_post = models.Post(user=user, body=post_pody)
    new_post.save()

    return JsonResponse({"TODO": "TODO"}, status=201)



def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = models.User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
