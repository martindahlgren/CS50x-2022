import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .util import cities
from . import util, util_matching
from .models import HalfPairing
from . import models
from django.views.decorators.http import require_http_methods, require_POST, require_safe


def index(request):
    return render(None, "app/index.html")

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
