from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseBadRequest
from django.db.models import Max
import decimal

from .models import User, Listing, Bid, Comment, Category


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

class PlaceBidForm(forms.Form):
    def __init__(self, starting_value, highest_bid=None, *args, **kwargs):
        super(PlaceBidForm, self).__init__(*args, **kwargs)
        decimal_places = 2
        
        if not highest_bid:
            min_value=starting_value
        else:
            min_value=(highest_bid+decimal.Decimal("0.1")**decimal_places)

        self.fields['bid_val'] = forms.DecimalField(min_value=min_value, decimal_places=decimal_places, label=False)

def _get_highest_bid(listing_id):
    return Bid.objects.filter(listing_id=listing_id).aggregate(Max('bid'))['bid__max']


def index(request):
    listings = Listing.objects.filter(has_ended=False)
    listings_with_bid = [(l, _get_highest_bid(l.id) or l.start_bid) or l.start_bid for l in listings]
    return render(request, "auctions/index.html",
                  {
                      "listings": listings_with_bid,
                      "title": "Active Listings",
                  })

@login_required
def watchlist(request):
    listings = Listing.objects.filter(watchers=request.user)
    listings_with_bid = [(l, _get_highest_bid(l.id) or l.start_bid) or l.start_bid for l in listings]
    return render(request, "auctions/index.html",
                  {
                      "listings": listings_with_bid,
                      "title": "My Watchlist",
                  })

def category(request, category_name):
    category = Category.objects.get(name = category_name)
    listings = category.listing_set.all()
    listings_with_bid = [(l, _get_highest_bid(l.id) or l.start_bid) or l.start_bid for l in listings]
    return render(request, "auctions/index.html",
                  {
                      "listings": listings_with_bid,
                      "title": category_name,
                  })

def categories(request):
    categories = Category.objects.all().order_by('name')

    return render(request, "auctions/categories.html",
                  {
                      "categories": categories,
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
        listing.owner = request.user
        listing.save()
        form = NewListingForm()
    return render(request, "auctions/create-listing.html", {
        "form": form
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@transaction.atomic
@login_required
def post_bid(request, listing_key):
    if request.method == "POST":
        try:
            listing = Listing.objects.get(id=listing_key)
        except ObjectDoesNotExist:
            raise Http404(f"Listing with id {listing_key} does not exist")

        highest_bid = _get_highest_bid(listing.id)
        form = PlaceBidForm(data=request.POST, starting_value=listing.start_bid, highest_bid=highest_bid)
        new_bid = None
        if form.data.get("bid_val"):
            new_bid = decimal.Decimal(form.data.get("bid_val"))
        if form.is_valid():
            new_bid = Bid(bid=form.cleaned_data["bid_val"], bidder=request.user, listing=listing)
            new_bid.save()
            return redirect("listing", listing_key=listing_key)
        elif(new_bid and ((highest_bid and new_bid <= highest_bid) or new_bid < listing.start_bid )):
            # Redirect but show warning
            return redirect(f"{reverse('listing', kwargs={'listing_key':listing_key})}?bid-error=True")
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


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

def close_bid(request, listing_key):
    try:
        listing = Listing.objects.get(id=listing_key)
    except ObjectDoesNotExist:
        raise Http404(f"Listing with id {listing_key} does not exist")
    if listing.owner == request.user:
        listing.has_ended = True
        listing.save()
    return redirect("listing", listing_key=listing_key)

@login_required
def add_comment(request, listing_key):
    try:
        listing = Listing.objects.get(id=listing_key)
    except ObjectDoesNotExist:
        raise Http404(f"Listing with id {listing_key} does not exist")
    comment = Comment(listing=listing, owner=request.user, content=request.POST["comment"])
    comment.save()
    listing.comments.add(comment)
    return redirect("listing", listing_key=listing_key)


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

    highest_bid = _get_highest_bid(listing.id)
    if highest_bid:
        highest_bid_obj = Bid.objects.get(bid=highest_bid, listing_id=listing.id)
        user_is_highest = highest_bid_obj.bidder == request.user
        price = highest_bid
    else:
        user_is_highest = False
        price = listing.start_bid
    nr_bids = Bid.objects.filter(listing_id=listing.id).count()
    if request.user.is_authenticated:
        is_watched = listing.watchers.filter(pk=request.user.id).exists()
    else:
        is_watched = False
    return render(request, "auctions/single_listing.html",
                  {
                      "listing": listing,
                      "price": price,
                      "category": listing.category,
                      "watched": is_watched,
                      "user_is_highest": user_is_highest,
                      "nr_bids": nr_bids,
                      "bid_form": PlaceBidForm(starting_value=listing.start_bid, highest_bid=highest_bid),
                      "show_bid_error": "bid-error" in request.GET,
                      "has_ended": listing.has_ended,
                      "comments": listing.comments.all()
                  })
