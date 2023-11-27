import datetime
from . import util
from . import models
from django.db.models import Max
import random
import time
import threading

MATCHMAKING_SECONDS_BEFORE_NEW_DAY = 5*60 # 5 minutes
MAX_NR_MATCHES = 4

switching_time = datetime.timedelta(hours=18, minutes=15) # This time (utc) into a day the matchmaking process is run!
active_day = (datetime.datetime.now(tz=datetime.timezone.utc) - switching_time).date() # "Day" of which current matchmaking is valid
latest_day = None # Matches are available for this day, might be higher than active_day for a short while
print(f"Matching for {active_day} is valid now")

lock = threading.Lock()
matchmaking_thread = None

def seconds_until_new_swipes():
    current_utc_time = datetime.datetime.now(tz=datetime.timezone.utc)
    next_matches_day = active_day + datetime.timedelta(days=1)
    time_of_next_matches = datetime.datetime(next_matches_day.year, next_matches_day.month, next_matches_day.day, tzinfo=datetime.timezone.utc) + switching_time 
    print(time_of_next_matches)
    print(current_utc_time)
    seconds_until_matchmaking = (time_of_next_matches - current_utc_time).total_seconds()
    return seconds_until_matchmaking

def match_factor(person):
    some_time_back = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=90)
    nr_recent_matches = models.HalfPairing.objects.filter(this_user=person.user, matching_date__gt=some_time_back).count()
    return nr_recent_matches

def interested_in_gender(p1, p2):
    if p1.into_men and p2.user.gender == models.Gender.MAN:
        return True
    if p1.into_women and p2.user.gender == models.Gender.WOMAN:
        return True
    if p1.into_nb and p2.user.gender == models.Gender.OTHER:
        return True
    return False

def people_compatible(p1, p2):
    if p1 == p2:
        # Same user
        return False
    if not interested_in_gender(p1, p2) or not interested_in_gender(p2, p1):
        return False
    if models.HalfPairing.objects.filter(this_user=p1.user, swipee=p2.user).exists():
        # Already matched
        return False

    return True

def matches_left(user, day):
    matches_so_far = models.HalfPairing.objects.filter(this_user=user, matching_date=day).count()
    assert matches_so_far <= MAX_NR_MATCHES
    return MAX_NR_MATCHES - matches_so_far

def match_people(people, day):
    people_by_nr_matches_last_year = sorted(people, key=match_factor)
    for person in people_by_nr_matches_last_year:
        print(person.user.first_name)
        # Get nr of matches already of this day
        potential_partners = [p for p in people if people_compatible(person, p) and matches_left(p.user, day)]
        to_match_with = random.sample(potential_partners, min(matches_left(person.user, day), len(potential_partners)))
        for match in to_match_with:
            print(f"{person.user.first_name} matchd with {match.user.first_name}")
            models.add_pair(person.user, match.user, day)

def step_matching_day():
    global latest_day, active_day
    active_day = latest_day
    print(f"Matching for {active_day} is valid now")

def create_tomorrows_matches():
    should_be_current_active_day = (datetime.datetime.now(tz=datetime.timezone.utc) - switching_time).date()
    day_tomorrow = (should_be_current_active_day + datetime.timedelta(days=1))
    global latest_day, active_day
    if latest_day is None:
        _latest_day_in_db = models.HalfPairing.objects.aggregate(Max('matching_date'))['matching_date__max']
        latest_day = max(active_day, _latest_day_in_db) # Day of last time matchmaking run

    if day_tomorrow == latest_day:
        return # If for some reason the matchmaking was invoked twice

    used_cities = models.UserProfile.objects.order_by().values_list('location', flat=True).distinct()

    # Go through each city. Attempt to match profiles together. Sort the profiles with the ones with few recent suggestions at the top.
    # For each profile find all profiles that match their criteria, and we haven't matched with before. Filter out those who are not compatible. Select 4 at random!
    # Then continue going through the rest of the profiles until as many as possible has 4 matches - not all will be able to get that many but it is fine

    for city in used_cities:
        people = models.UserProfile.objects.filter(location=city)
        match_people(people, day_tomorrow)

    latest_day = day_tomorrow

def background_matching_function():
        while True:
                # Wait until a few minutes before new day to run matchmaking algorith
                time_until_new_available = seconds_until_new_swipes()
                print(f"Time until tomorrow's matches: {time_until_new_available/3600} hours")
                print(f"Will start matchmaking in: {(time_until_new_available-MATCHMAKING_SECONDS_BEFORE_NEW_DAY)/3600} hours")
                if time_until_new_available > MATCHMAKING_SECONDS_BEFORE_NEW_DAY:
                    time.sleep((time_until_new_available - MATCHMAKING_SECONDS_BEFORE_NEW_DAY)) # Sleep until time to matchmake

                _time_before = time.time()
                create_tomorrows_matches()
                print(f"Matchmaking process took {time.time() - _time_before} seconds")

                time_until_new_available = seconds_until_new_swipes()
                if(time_until_new_available > 0):
                    time.sleep(time_until_new_available) # Sleep until time to serve new matches

                step_matching_day()

def trigger_start_matchmaking():
    with lock:
        global matchmaking_thread
        if matchmaking_thread is None:
           matchmaking_thread = threading.Thread(target=background_matching_function, daemon=True)
           matchmaking_thread.start()