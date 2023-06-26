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

def show_posts(request, page, this_route, page_title, show_new, filter={}):
    latest = request.GET.get("latest")
    if latest is not None:
        posts_query = models.Post.objects.filter(id__lte = int(latest)).filter(**filter).order_by('-id')
    else:
        posts_query = models.Post.objects.filter(**filter).order_by('-id')
        if posts_query.first():
            latest = posts_query.first().id
    p = Paginator(posts_query, 10)
    page_obj = p.page(page)

    return render(request, "network/index.html", {'page_obj': page_obj, "show_new": show_new, "latest": latest, "this_route": this_route, "page_title": page_title})

def index(request, page=1):
    return show_posts(request, page, "index", "All Posts", True)

@login_required
def following(request, page=1):
    following_users = request.user.following.all().values('following')

    filter = {"user__in": following_users}
    return show_posts(request, page, "following", "Following", True, filter)

def user(request, viewed_user, page=1):
    viewed_user_id = models.User.objects.get(username=viewed_user).id
    filter = {"user": viewed_user_id}
    return show_posts(request, page, f"user/{viewed_user}", viewed_user, False, filter)

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

@login_required
@require_POST
def like(request):
    data = json.loads(request.body)
    user = request.user
    post_id = data["post_id"]
    post = models.Post.objects.get(id=post_id)
    likes = post.likes
    try:
        existing_like = likes.get(user=user)
        existing_like.delete()
    except models.Like.DoesNotExist:
        new_like = models.Like(user=user, post=post)
        new_like.save()

    like_count = post.n_likes()

    return JsonResponse({"post_id": post_id, "like_count": like_count}, status=201)


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
