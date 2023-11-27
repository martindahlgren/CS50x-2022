from django.test import TestCase
from . import util, util_matching
from . import views
from .models import User, HalfPairing
from . import models
import datetime
import json


class LocationMatchingTestCase(TestCase):
    def setUp(self):
        pass

    def test_can_get_vänersborg(self):
        """ Try retrieving the list of cities starting with vä """
        city_matches = util.cities.get_matches("vän", 10)
        city_matches_display = [(displayname.split(",")[0], city.geonameid) for (displayname, city) in city_matches]
        assert city_matches_display == [("Vänersborg", 2665171), ('Vännäs', 2665093), ('Vändra', 587440), ('Vännäsby', 2665090), ('Vänqli (Vank)',584747)]

    def test_limit_hits(self):
        """ Try retrieving the list of cities starting with vä """
        city_matches = util.cities.get_matches("vä", 10)
        assert len(city_matches) == 10


    def _add_user_a_matches(self):
        # Create swipe-possibilities for today and yesterday
        today = util_matching.active_day
        user_a = User(username="Anna")
        user_a.save()
        user_b = User(username="Bertil")
        user_b.save()
        models.add_pair(user_a, user_b, today)

        yesterday = today + datetime.timedelta(days=-1)
        user_c = User(username="Cristin")
        user_c.save()
        models.add_pair(user_c, user_a, yesterday)

    def test_get_matches(self):
        self._add_user_a_matches()
        # See we can get back what we set above
        user_a = User.objects.get(username="Anna")
        daily_swipes, n_left = util.get_daily_swipes(user_a)
        assert len(daily_swipes) == 1
        assert daily_swipes[0].this_user == user_a
        assert daily_swipes[0].swipee.username == "Bertil"

    def test_umatch_user(self):
        self._add_user_a_matches()
        user_a = User.objects.get(username="Anna")
        self.client.force_login(user_a)
        bertil_id = User.objects.get(username="Bertil").id
        json_string = json.dumps({"umatch_user_id": bertil_id})
        response = self.client.post('/unmatch', json_string, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        swipe = HalfPairing.objects.get(this_user=user_a, swipee=bertil_id)
        self.assertEqual(swipe.user_likes_swipee, models.SwipeState.NO)

        daily_swipes, n_left = util.get_daily_swipes(user_a)
        assert len(daily_swipes) == 0
        # TODO: Verify that the blocked user is not returned using any endpoint!
