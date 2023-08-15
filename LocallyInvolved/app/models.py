from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Gender(models.TextChoices):
    MAN = "M", _("Man")
    WOMAN = "W", _("Woman")
    OTHER = "O", _("Other")

class UserProfile(models.Model):
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
    )
    into_men = models.BooleanField()
    into_women = models.BooleanField()
    into_other = models.BooleanField()

    picture = models.FileField()
    bio = models.CharField(max_length=1500)
    # Location is a GeoNames id
    location = models.IntegerField()

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    profile = models.OneToOneField(UserProfile, null=True,
                                    on_delete=models.CASCADE)

class Pairing(models.Model):
    part_a = models.ForeignKey(User, related_name='parts_a', on_delete=models.CASCADE)
    part_b = models.ForeignKey(User, related_name='parts_b', on_delete=models.CASCADE)
    is_blocked = models.BooleanField()


class ChatMessage(models.Model):
    pass