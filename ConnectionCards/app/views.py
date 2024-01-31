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
from PIL import Image
import io
from collections import defaultdict 
import threading



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
    location = int(data["location"]) if data["location"] else None
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

class UploadImageForm(forms.Form):
    file = forms.ImageField() # TODO Check file size

@login_required
@require_POST
def upload_picture(request):
    def get_new_dimensions(width, height):
        if width >= height and width > 1024:
            height = round(height * (1024/width))
            width = 1024
            return True, width, height
        elif height >= width and height > 1024:
            width = round(width * (1024/height))
            height = 1024
            return True, width, height
        else:
            return False, 0, 0

    if request.method == "POST":
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            profile = request.user.profile
            img = Image.open(request.FILES['file'])
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            need_resize, new_width, new_height = get_new_dimensions(*img.size)
            if need_resize:
               img = img.resize((new_width,new_height), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            buf.seek(0)
            profile.picture.save('converted_pic.jpg', buf)
            print(profile.picture.url)
            profile.save()
        else:
            print("Invalid image uploaded")
    return HttpResponseRedirect(reverse("profile"))

_waiting_for_messages = defaultdict(list) 
def notify_message(sender, receiver):
    conv_key = tuple(sorted([sender,receiver]))
    for observer_event in _waiting_for_messages[conv_key]:
        observer_event.set()

def wait_for_message(user1, user2, timeout):
    conv_key = tuple(sorted([user1,user2]))
    event = threading.Event()
    _waiting_for_messages[conv_key].append(event)
    event.wait(timeout) # Wait for the notify_message to be called
    _waiting_for_messages[conv_key].remove(event)
    if not _waiting_for_messages[conv_key]:
        del _waiting_for_messages[conv_key]

@login_required
def send_chat(request):
    data = json.loads(request.body) # {"recipient, message"}
    to_user = int(data["recipient"])
    util.send_message(request.user, to_user, data["message"])
    notify_message(request.user.id, to_user)
    return JsonResponse({"message": "Success"})


@login_required
def get_conversation(request, user_id, later_than_mess_id=None):

    assert util.users_matched(request.user, user_id)
    messages = util.get_conversation_json(request.user, user_id, (later_than_mess_id or 0))
    if not messages and later_than_mess_id is not None:
        #print("No messages availale, waiting 10 seconds for new ones")
        wait_for_message(request.user.id, user_id, timeout=10)
        messages = util.get_conversation_json(request.user, user_id, (later_than_mess_id or 0))
    return JsonResponse({"messages": messages, "conversation_partner": user_id})

@login_required
def get_candidates(request):
    daily_swipes, n_swipes_left = util.get_daily_swipes(request.user)
    if len(daily_swipes) > 4:
        return JsonResponse(status=400)
    return JsonResponse({"swipees": [util.serialize_swipe(hp) for hp in daily_swipes],
                         "seconds_to_next": util_matching.seconds_until_new_swipes(),
                         "n_swipes_left": n_swipes_left})

@login_required
def get_conversations(request):
    conversations = util.get_conversations_json(request.user)
    return JsonResponse({"conversations": conversations})


def start_background_matching(request):
    util_matching.trigger_start_matchmaking()
    return JsonResponse({"message": "Matchmaking will run in background"})

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
    matches = cities.get_matches(request.GET.get('q', ''), 10)
    response = {"possible_cities":[ {"display_name": m[0], "city_id": m[1].geonameid} for m in matches]}
    return JsonResponse(response)
