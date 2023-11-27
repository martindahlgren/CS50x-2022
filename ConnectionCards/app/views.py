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
from django.db import transaction
from django import forms


def index(request):
        """index view"""
        return HttpResponseRedirect(reverse("match"))        

def match_view(request):
    """match view"""
    if request.user.is_authenticated:
        return render(request, "app/match.html")
    else:
        return HttpResponseRedirect(reverse("login"))        

@login_required
def profile_view(request):
    """Edit profile view"""
    user = request.user
    if not request.user.profile:
        # Create missing profile
        profile = models.UserProfile.objects.create()
        profile.save()
        user.profile = profile
        user.save()

    name = request.user.first_name
    return render(request, "app/profile_view.html",
                  {
                      "name": name,
                      "gender": request.user.get_gender_display(),
                      "profile": request.user.profile,
                      "location_str": cities.from_id(request.user.profile.location).displayname() if request.user.profile.location else ""
                  })

@login_required
@require_POST
def profile_update(request):
    data = json.loads(request.body)
    profile = request.user.profile
    profile.into_men = data["into_men"]
    profile.into_women = data["into_women"]
    profile.into_nb = data["into_nb"]
    profile.bio = data["bio"]
    location = int(data["location"]) or None
    if not location or location not in cities.id_to_city:
        return JsonResponse(status=400)
    profile.location = location

    profile.save()
    return JsonResponse({"message": "Profile updated."}, status=200)


def chat_view(request):
    """chat view"""
    if request.user.is_authenticated:
        return render(request, "app/chat.html")
    else:
        return HttpResponseRedirect(reverse("login"))        


def login_view(request):
    """login view"""
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
    """logout view"""
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """register view"""
    if request.method == "POST":
        email = request.POST["email"]
        first_name = request.POST["firstname"]
        gender = request.POST["gender"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "app/register.html", {
                "message": "Passwords must match."
            })
        
        if not gender in models.Gender.values:
            return render(request, "app/register.html", {
                "message": "Please select gender."
            })

        # Attempt to create new user
        with transaction.atomic():
            if models.User.objects.filter(username=email).exists():
                return render(request, "app/register.html", {
                    "message": "Email address already used."
                })
            else:
                user = models.User.objects.create_user(username=email, email=email, password=password, first_name=first_name, gender=gender)
                user.full_clean()
                user.save()

        # User created, let's log in
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "app/register.html")

class UploadFileForm(forms.Form):
    file = forms.ImageField()

@login_required
@require_POST
def upload_picture(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = request.user.profile
            profile.picture = request.FILES['file']
            print(profile.picture.url)
            profile.save()
    return HttpResponseRedirect(reverse("index"))

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
    daily_swipes, n_swipes_left = util.get_daily_swipes(request.user)
    if len(daily_swipes) > 4:
        return JsonResponse(status=400)
    return JsonResponse({"swipees": [util.serialize_swipe(hp) for hp in daily_swipes],
                         "seconds_to_next": util_matching.seconds_until_new_swipes(),
                         "n_swipes_left": n_swipes_left})

def start_background_matching(request):
    util_matching.trigger_start_matchmaking()
    return JsonResponse({})

@login_required
@require_POST
def send_swipe(request):
    data = json.loads(request.body)
    swipee_id = data["id"]
    swipe = HalfPairing.objects.get(this_user=request.user, swipee=swipee_id)
    swipes_left = util.get_n_swipes_left(request.user)
    assert swipes_left != 0 # Limiting swiping is the point
    assert swipe.user_likes_swipee == models.SwipeState.TO_SWIPE # Don't allow selecting the same user
    assert swipe.matching_date == util_matching.active_day # Only allowed to swipe on the matches of today
    swipe.user_likes_swipee = models.SwipeState.YES
    swipe.save()
    match_already = (swipe.other_half.user_likes_swipee == models.SwipeState.YES)
    swipes_left = util.get_n_swipes_left(request.user)
    return JsonResponse({"match_already": match_already, "n_swipes_left": swipes_left})

@login_required
@require_POST
def unmatch_user(request):
    data = json.loads(request.body)
    swipee_id = data["umatch_user_id"]
    swipe = HalfPairing.objects.get(this_user=request.user, swipee=swipee_id)
    swipe.user_likes_swipee = models.SwipeState.NO
    swipe.save()
    return JsonResponse({})

def suggest_cities(request):
    # request format {"vänersbo"} => {possible_cities: [{display_name: 'Vänersborg, Vänersborgs Kommun, SE', city_id:2665171}]}
    data = json.loads(request.body)
    matches = cities.get_matches(data["filter"], 10)
    response = {"possible_cities":[ {"display_name": m[0], "city_id": m[1].geonameid} for m in matches]}
    return JsonResponse(response)
