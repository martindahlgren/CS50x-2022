from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db.models import Max

from .models import User, Listing, Bid


class NewListingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = self.fields['category'].queryset.order_by(
            'name')

    # Override the widget of description
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Listing
        fields = ['title', 'description', 'start_bid', 'image_url', 'category']


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html",
                  {
                      "listings": listings
                  })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
def create_listing_view(request):
    form = NewListingForm(request.POST or None)
    if form.is_valid():
        # Save the listing
        listing = form.save(commit=False)
        start_bid = Bid(bid=listing.start_bid, bidder=request.user, listing=listing)
        listing.owner = request.user
        listing.save()
        start_bid.save()
        form = NewListingForm()
    return render(request, "auctions/create-listing.html", {
        "form": form
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def watch_toggle(request, listing_key):
    try:
        listing = Listing.objects.get(id=listing_key)
    except ObjectDoesNotExist:
        raise Http404(f"Listing with id {listing_key} does not exist")
    is_watched = listing.watchers.filter(pk=request.user.id).exists()
    if is_watched:
        instance = listing.watchers.remove(request.user.id)
    else:
        listing.watchers.add(request.user)
    return redirect("listing", listing_key=listing_key)

def listing(request, listing_key):
    try:
        listing = Listing.objects.get(id=listing_key)
    except ObjectDoesNotExist:
        raise Http404(f"Listing with id {listing_key} does not exist")

    highest_bid = Bid.objects.filter(listing_id=listing.id).aggregate(Max('bid'))['bid__max']
    if request.user.is_authenticated:
        is_watched = listing.watchers.filter(pk=request.user.id).exists()
    else:
        is_watched = False

    return render(request, "auctions/single_listing.html",
                  {
                      "listing": listing,
                      "highest_bid": highest_bid,
                      "watched": is_watched
                  })