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
        assert (str(city_matches)) == "[('Vänersborg, Vänersborgs Kommun, SE', _Cities.City(geonameid=2665171, name='Vänersborg', latitude='58.38075', longitude='12.3234', country='SE', admin2='Vänersborgs Kommun', population=23119)), ('Vännäs, Vännäs Kommun, SE', _Cities.City(geonameid=2665093, name='Vännäs', latitude='63.90676', longitude='19.75712', country='SE', admin2='Vännäs Kommun', population=4373)), ('Vändra, Põhja-Pärnumaa vald, EE', _Cities.City(geonameid=587440, name='Vändra', latitude='58.64806', longitude='25.03611', country='EE', admin2='Põhja-Pärnumaa vald', population=2544)), ('Vännäsby, Vännäs Kommun, SE', _Cities.City(geonameid=2665090, name='Vännäsby', latitude='63.91564', longitude='19.82438', country='SE', admin2='Vännäs Kommun', population=1581)), ('Vänqli (Vank), AZ', _Cities.City(geonameid=584747, name='Vank', latitude='40.05275', longitude='46.54419', country='AZ', admin2=None, population=1335))]"


    def _add_user_a_matches(self):
        # Create swipe-possibilities for today and yesterday
        today = datetime.datetime.now(datetime.timezone.utc).date()
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
        # See we can get back what we setp above
        user_a = User.objects.get(username="Anna")
        daily_swipes = util.get_daily_swipes(user_a)
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

        daily_swipes = util.get_daily_swipes(user_a)
        assert len(daily_swipes) == 0
        # TODO: Verify that the blocked user is not returned using any endpoint!
