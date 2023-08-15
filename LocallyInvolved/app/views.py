import json
from django.shortcuts import render
from .util import cities
import time


def index(request):
    return render(None, "app/index.html")

def upload_picture(request):
    pass

def get_matches(request):
    pass

def get_chat(request):
    pass

def send_chat(request):
    pass

def get_more_messages(request):
    pass

def get_candidates(request):
    pass

def get_my_profile(request):
    pass

def update_profile(request):
    pass

def block_user(request):
    pass

def suggest_cities(request):
    data = json.loads(request.body)
    matches = cities.get_matches(data.city)
    pass # Based on partial city name

start = time.time()
print("\n\n")
print(tuple(zip(*cities.get_matches("sto", 5)))[0])
print("\n\n")
print(time.time() - start)
