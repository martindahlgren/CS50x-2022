import json
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .util import cities
from . import util, util_matching
from .models import HalfPairing
from . import models
from django.views.decorators.http import require_http_methods, require_POST, require_safe

def index(request):
        return HttpResponseRedirect(reverse("match"))        

def match_view(request):
    if request.user.is_authenticated:
        return render(request, "app/index.html")
    else:
        return HttpResponseRedirect(reverse("login"))        


def messages_view(request):
    if request.user.is_authenticated:
        return render(request, "app/index.html")
    else:
        return HttpResponseRedirect(reverse("login"))        


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "app/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "app/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = models.User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "app/register.html", {
                "message": "Email address already used."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "app/register.html")




@login_required
def upload_picture(request):
    pass

@login_required
def get_matches(request):
    pass

@login_required
def get_chat(request):
    pass

@login_required
def send_chat(request):
    pass

@login_required
def get_more_messages(request):
    pass

@login_required
def get_candidates(request):
    daily_swipes = util.get_daily_swipes(request.user)
    if len(daily_swipes) > 4:
        return JsonResponse(status=400)

    return JsonResponse({"swipees": [util.serialize_swipe(hp) for hp in daily_swipes],
                         "hours_to_next": util_matching.hours_until_next_day()})

@login_required
def send_swipes(request):
    pass

@login_required
def get_my_profile(request):
    pass

@login_required
def update_profile(request):
    pass

@login_required
@require_POST
def unmatch_user(request):
    data = json.loads(request.body)
    swipee_id = data["umatch_user_id"]
    swipe = HalfPairing.objects.get(this_user=request.user, swipee=swipee_id)
    swipe.user_likes_swipee = models.SwipeState.NO
    swipe.save()
    return JsonResponse({})

@require_safe
def suggest_cities(request):
    # request format {"vänersbo"} => {possible_cities: [{display_name: 'Vänersborg, Vänersborgs Kommun, SE', city_id:2665171}]}
    data = json.loads(request.body)
    matches = cities.get_matches(data.city, 10)
    response = {"possible_cities":[ {"display_name": m[0], "city_id": m[1].geonameid} for m in matches]}
    return JsonResponse(response)
