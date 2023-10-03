from django.conf import settings
from django.core.management.base import BaseCommand
from app.models import User, HalfPairing, UserProfile
import app.models as models
import app.util_matching as util_matching
import datetime

assert settings.DEBUG
# Create example data for user Adam
already_matched_with = [
    {
        "name":   "Alex",
        "gender": "M",
        "into_men": True,
        "into_women": False,
        "into_nb": False,
        "bio": "I love hiking and exploring new places. Looking for someone to share adventures with.",
        "location": 5128581
    },
    {
        "name":   "Jordan",
        "gender": "O",
        "into_men": True,
        "into_women": True,
        "into_nb": True,
        "bio": "Nature enthusiast, cat lover, and video game addict. Open to meeting people from all walks of life.",
        "location": 5809844
    },
    {
        "name":   "Ethan",
        "gender": "M",
        "into_men": True,
        "into_women": False,
        "into_nb": False,
        "bio": "Tech geek by day, rock climber by weekend. Looking for a partner in both code and adventure.",
        "location": 5391959
    },
    {
        "name":   "Olivia",
        "gender": "Woman",
        "into_men": False,
        "into_women": True,
        "into_nb": False,
        "bio": "Bookworm and coffee lover. Hoping to find someone who enjoys deep conversations and caffeine as much as I do.",
        "location": 4887398
    },
    {
        "name":   "Liam",
        "gender": "M",
        "into_men": True,
        "into_women": False,
        "into_nb": False,
        "bio": "Foodie on a mission to try every restaurant in town. Looking for a fellow food adventurer to join me on the journey.",
        "location": 4164138
    },
    {
        "name":   "Avery",
        "gender": "O",
        "into_men": True,
        "into_women": True,
        "into_nb": True,
        "bio": "Travel addict exploring the world one city at a time. Looking to connect with fellow wanderlusters.",
        "location": 5419384
    },
    {
        "name":   "Noah",
        "gender": "M",
        "into_men": True,
        "into_women": False,
        "into_nb": False,
        "bio": "Musician and music producer. Hoping to find someone who appreciates the beauty of melodies and harmonies.",
        "location": 4644585
    },
]

current_swipes = [
    {
        "name":   "Emily",
        "gender": "Woman",
        "into_men": False,
        "into_women": True,
        "into_nb": False,
        "bio": "Passionate about art and photography. Seeking a creative soul to inspire and be inspired by.",
        "location": 5368361
    },
    {
        "name":   "Sophia",
        "gender": "Woman",
        "into_men": False,
        "into_women": True,
        "into_nb": False,
        "bio": "Fitness enthusiast and personal trainer. Looking for a workout buddy and maybe something more.",
        "location": 5391811
    },
    {
        "name":   "Mia",
        "gender": "Woman",
        "into_men": False,
        "into_women": True,
        "into_nb": False,
        "bio": "Yoga enthusiast and meditation practitioner. Seeking someone who values mindfulness and inner peace.",
        "location": 4671654
    },
]

class Command(BaseCommand):
    def handle(self, *args, **options):
        test_user = User(username="Adam")
        test_user.first_name = "Adam"
        test_user.last_name = "Testersen"
        test_user.save()
        yesterday = datetime.datetime.now(datetime.timezone.utc).date() + datetime.timedelta(days=-1)

        for profile in already_matched_with:
            new_user =  User(username=profile["name"], password="test")
            new_user.first_name = profile["name"]
            new_user.last_name = "Testsson"

            new_profile = UserProfile(
                gender = profile["gender"],
                into_men = profile["into_men"],
                into_women = profile["into_women"],
                into_nb = profile["into_nb"],
                bio = profile["bio"],
                location = profile["location"],
            )
            new_profile.save()
            new_user.profile = new_profile
            new_user.save()
            half_a, half_b = models.add_pair(test_user, new_user, yesterday)
            half_a.user_likes_swipee = "Y"
            half_b.user_likes_swipee = "Y"
            half_a.save()
            half_b.save()
