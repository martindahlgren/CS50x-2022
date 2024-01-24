from django.contrib.auth.models import AbstractUser
from django.db import models, transaction

from django.utils.translation import gettext_lazy as _

class SwipeState(models.TextChoices):
    TO_SWIPE = "T"
    YES = "Y"
    NO = "N"
class Gender(models.TextChoices):
    MAN = "M", _("Man")
    WOMAN = "W", _("Woman")
    OTHER = "O", _("Other")

class UserProfile(models.Model):
    into_men = models.BooleanField(default=False)
    into_women = models.BooleanField(default=False)
    into_nb = models.BooleanField(default=False)
    picture = models.ImageField(default="images/placeholder.png", upload_to="images/user_upload")
    bio = models.CharField(max_length=300, default="")
    # Location is a GeoNames id
    location = models.IntegerField(default=0)

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
    )
    profile = models.OneToOneField(UserProfile, null=True, blank=True,
                                    on_delete=models.CASCADE)

class HalfPairing(models.Model):
    this_user = models.ForeignKey(User, related_name='pairings', on_delete=models.CASCADE)
    swipee = models.ForeignKey(User, on_delete=models.CASCADE)
    matching_date = models.DateField()
    user_likes_swipee = models.CharField(
        max_length=1,
        choices=SwipeState.choices,
        default=SwipeState.TO_SWIPE,
    )
    has_unread = models.BooleanField(default=True) # Has unread conversations or never opened 
    other_half = models.OneToOneField('self', on_delete=models.CASCADE, null=True)
    class Meta:
        unique_together = [["this_user", "swipee"]]


def add_pair(user_a, user_b, date):
    """ Convenience function to add a pair of HalfPairing """
    with transaction.atomic():
        pair_a = HalfPairing(this_user=user_a, swipee=user_b, matching_date=date)
        pair_b = HalfPairing(this_user=user_b, swipee=user_a, matching_date=date, other_half=pair_a)
        pair_a.save()
        pair_b.save()
        pair_a.other_half = pair_b
        pair_a.save()
    return (pair_a, pair_b)

class ChatMessage(models.Model):
    pass
