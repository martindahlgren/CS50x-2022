import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .util import cities
import time


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
    pass

@login_required
def get_my_profile(request):
    pass

@login_required
def update_profile(request):
    pass

@login_required
def block_user(request):
    pass

def suggest_cities(request):
    data = json.loads(request.body)
    matches = cities.get_matches(data.city)
    pass # Based on partial city name
