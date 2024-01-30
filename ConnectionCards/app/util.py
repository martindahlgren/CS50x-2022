
from dataclasses import dataclass
import os
from functools import lru_cache
import bisect
from . import util_matching
from .models import HalfPairing, SwipeState, ChatMessage, User
from django.http import HttpResponseServerError

MAX_SWIPES_PER_DAY = 2

class _Cities():

    "Helps finding cities. Data source: geonames.org cities5000.txt"

    @dataclass
    class City():
        geonameid: int
        name: str
        asciiname: str
        alternatenames: [str]
        latitude: float
        longitude: float
        country: str # ISO-3166 2-letter country code, 2 characters
        admin1: str # geonames admin1_code string
        admin2: str # geonames admin2_code string
        population: int

        def displayname(self):
            displayname = self.name
            if self.admin1:
                displayname += f", {self.admin1}"
            if self.admin2:
                displayname += f", {self.admin2}"
            displayname += f", {self.country}"
            return displayname

    def __init__(self):
        self.id_to_city = {}
        self.all_names = {} # All names and ids [(lowercasename, Name, id)]

        admin1_areas = {}
        FILEPATH_ADMIN1=os.path.dirname(__file__) + '/admin1codesASCII.txt'
        with open(FILEPATH_ADMIN1, 'r', encoding='utf-8') as admin1_file:
            for line in admin1_file.readlines():
                (concatenated_code, name, name_ascii, geonameid) = line.split("\t")
                (country, admin1) = concatenated_code.split(".")
                admin1_areas.setdefault(country, {})[admin1] = name

        admin2_areas = {}
        FILEPATH_ADMIN2=os.path.dirname(__file__) + '/admin2codes.txt'
        with open(FILEPATH_ADMIN2, 'r', encoding='utf-8') as admin2_file:
            for line in admin2_file.readlines():
                (concatenated_code, name, asciiname, geonameId) = line.split("\t")
                (country, admin1, admin2) = concatenated_code.split(".")
                admin2_areas.setdefault(country, {}).setdefault(admin1, {})[admin2] = name

        FILEPATH=os.path.dirname(__file__) + '/cities5000.txt'

        all_names_list = []
        cities = []
        with open(FILEPATH, 'r', encoding='utf-8') as citiesfile:
            for line in citiesfile.readlines():
                (geonameid, name, asciiname, alternatenames, latitude,
                longitude, feature_class, feature_code, country_code,
                cc2, admin1_code, admin2_code, admin3_code, admin4_code,
                population, elevation, dem, timezone, modification_date) = line.split("\t")
                geonameid = int(geonameid)
                population = int(population)
                if feature_code in ("PPLX", "PPLW", "STLMT", "PPLQ", "PPLH") :
                    continue # Ignore section of populated place and some other "cities"

                try:
                    admin1_str = admin1_areas[country_code][admin1_code]
                except KeyError:
                    admin1_str = None
                try:
                    admin2_str = admin2_areas[country_code][admin1_code][admin2_code]
                except KeyError:
                    admin2_str = None
                alternatenames=alternatenames.split(",") if alternatenames else []
                city = self.City(geonameid=geonameid,
                                 name=name,
                                 asciiname=asciiname,
                                 latitude=latitude,
                                 longitude=longitude,
                                 country=country_code,
                                 alternatenames=alternatenames,
                                 admin2=admin2_str,
                                 admin1=admin1_str,
                                 population=population)
                cities.append(city)

        # Remove things with the same name. Sorry people who live there :)
        cities.sort(key=lambda x: (-x.population))
        displaynames = set()
        for city in cities:
            displayname = city.displayname()

            if displayname not in displaynames:
                self.id_to_city[city.geonameid] = city

                # Store all names in the big list of names
                if city.name:
                    all_names_list.append((city.name.lower(), city.name, city.geonameid))
                if city.asciiname:
                        all_names_list.append((city.asciiname.lower(), city.asciiname, city.geonameid))
                for alternatename in city.alternatenames:
                    all_names_list.append((alternatename.lower(), alternatename, city.geonameid))

        # Sort firts by name then population
        all_names_list.sort(key=lambda x: (x[0], -self.id_to_city[x[2]].population))
        self.all_names = all_names_list

    def get_matches(self, partial, max_hits):
        if partial == "":
            return []
        # Find cities with names starting with partial. Might return more than max_hits
        partial_low = partial.lower()
        matches = {} # id to list of matching strings

        idx = bisect.bisect_left(self.all_names, partial_low, key=lambda x: x[0])

        while True:
            (lowercasename, name, id) = self.all_names[idx]
            if len(matches) >= max_hits and lowercasename != partial:
                break # Allow more matches if all are identical
            if lowercasename.lower().startswith(partial_low):
                if not matches.get(id) or (name == self.from_id(id).name):
                    matches[id] = name
                idx += 1
            else:
                break
            if idx >= len(self.all_names):
                break

        # Replace id by City Object, convert to list
        matches_list = []
        for id, found_name in matches.items():
            city = self.from_id(id)
            if found_name == city.name:
                displayname = city.name
            else:
                displayname = f"{found_name} ({city.name})"
            if city.admin2:
                displayname += f", {city.admin2}"
            if city.admin1:
                displayname += f", {city.admin1}"
            displayname += f", {city.country}"
            matches_list.append((displayname, city))

        # sort by population size
        matches_list.sort(reverse=True, key=lambda city: city[1].population)
        return matches_list

    def from_id(self, id):
        return self.id_to_city[id]

cities = _Cities()

def get_n_swipes_left(user, day=None):
    if day is None:
        day = util_matching.active_day
    swipes = HalfPairing.objects.filter(this_user=user, matching_date=day, user_likes_swipee=SwipeState.TO_SWIPE)
    swipes = list(swipes)
    n_already_swiped = len(list(HalfPairing.objects.filter(this_user=user, matching_date=day).exclude(user_likes_swipee=SwipeState.TO_SWIPE)))
    n_swipes_left = MAX_SWIPES_PER_DAY - n_already_swiped
    if n_already_swiped > MAX_SWIPES_PER_DAY:
        n_swipes_left = 0
        print(f"{user} swipes has swiped more than allowed! Server integrity error.")
    if n_swipes_left > len(swipes):
        n_swipes_left = len(swipes)
    return n_swipes_left

def get_daily_swipes(user, day=None):
    "Get swipes of the day, only the one where the user didn't swipe yet"
    if day is None:
        day = util_matching.active_day
    swipes = HalfPairing.objects.filter(this_user=user, matching_date=day, user_likes_swipee=SwipeState.TO_SWIPE)
    swipes = list(swipes)
    n_swipes_left = get_n_swipes_left(user)

    return swipes, n_swipes_left

def serialize_swipe(halfpairing):
    swipee = halfpairing.swipee
    profile = swipee.profile
    if not profile:
        print("There are users without a profile shown to others!")
    gender = str(swipee.gender)
    picture = profile.picture.url
    bio = profile.bio
    name = swipee.first_name

    return {
        "id": swipee.id,
        "name": name,
        "gender": gender,
        "picture": picture,
        "bio": bio,
    }
    
def get_conversations_json(user):
    swipes_yes = HalfPairing.objects.filter(this_user=user, user_likes_swipee=SwipeState.YES)
    matches = []
    for swipe in swipes_yes:
        if swipe.other_half.user_likes_swipee == SwipeState.YES:
            matches.append(swipe)

    # Order matches - first unread and then by matching date
    matches = sorted(matches, key=lambda p: ( p.has_unread, p.matching_date ), reverse=True)


    return [{"user_id": s.swipee.id, "name": s.swipee.first_name, "picture": s.swipee.profile.picture.url, "unread": s.has_unread} for s in matches]

def mark_conv_read(this_user, they_user):
    pair = HalfPairing.objects.get(this_user=this_user, swipee=they_user)
    pair.has_unread = False
    pair.save()

def users_matched(u1, u2):
    pair1 = HalfPairing.objects.get(this_user=u1, swipee=u2)
    pair2 = HalfPairing.objects.get(this_user=u2, swipee=u1)
    u1_likes2 = pair1.user_likes_swipee == SwipeState.YES
    u2_likes1 = pair2.user_likes_swipee == SwipeState.YES
    return u2_likes1 and u1_likes2

def get_conversation_json(u1, u2):
    messages = []
    sent = ChatMessage.objects.filter(sender=u1, receiver=u2)
    for message in sent:
        messages.append({"message": message.message, "sent_by_me": True, "id":message.id})
    received = ChatMessage.objects.filter(sender=u2, receiver=u1)
    for message in received:
        messages.append({"message": message.message, "sent_by_me": False, "id":message.id})
    messages.sort(key=lambda m: m["id"])

    # Mark conversation as read
    mark_conv_read(u1, u2)

    return messages

def send_message(from_user, to_user, message):
    receiver_obj = User.objects.get(id=to_user)
    if not users_matched(from_user, to_user):
        return HttpResponseServerError("Invalid receiver")
    pair_recipient_half = HalfPairing.objects.get(this_user=to_user, swipee=from_user)
    pair_recipient_half.has_unread = True
    pair_recipient_half.save()
    ChatMessage.objects.create(sender=request.user, receiver=receiver_obj, message=message)
    return