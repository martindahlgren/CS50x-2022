from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

from django.db import models
from django.core.validators import MinValueValidator


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

class Listing(models.Model):
    id = models.BigAutoField(primary_key=True)
    #They should be able to specify a title for the listing, a text-based description, and what the starting bid should be. Users should also optionally be able to provide a URL for an image for the listing and/or a category (e.g. Fashion, Toys, Electronics, Home, etc.).
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000, blank=True)
    start_bid = models.DecimalField(max_digits=40, decimal_places=2, validators=[MinValueValidator(0.0),], blank=True)
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    has_ended = models.BooleanField(default=False)
    # Bid has ForeignKey to Listing
    # Comment has ForeignKey to Lising
    watchers = models.ManyToManyField(User, related_name='watched_listings')

class Bid(models.Model):
    id = models.BigAutoField(primary_key=True)
    bidder = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    bid = models.DecimalField(max_digits=40, decimal_places=2, validators=[MinValueValidator(0.0),])
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('listing', 'bid')

class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    content = models.CharField(max_length=1000, blank=False)
