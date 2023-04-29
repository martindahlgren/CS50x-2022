from django.core.management.base import BaseCommand
from auctions.models import Category

default_categories = ["Electronics & Computers",
"Home & Kitchen",
"Clothing & Accessories",
"Sports & Outdoors",
"Beauty & Personal Care",
"Health & Wellness",
"Baby & Kids",
"Toys & Games",
"Books & Magazines",
"Arts & Crafts",
"Music & Instruments & Gear",
"Movies & TV Shows",
"Pet Supplies",
"Food & Beverages",
"Garden & Outdoor Living",
"Office & Business Supplies",
"Automotive & Motorcycle",
"Tools & Home Improvement",
"Furniture & Decor",
"Travel & Luggage",
"Cell Phones & Accessories",
"Watches & Jewelry",
"Collectibles & Memorabilia",
"Antiques & Vintage",
"Party Supplies & Decorations"]

class Command(BaseCommand):
    #args = '<foo bar ...>'
    #help = 'our help string comes here'

    def _create_categories(self):
        for category in default_categories:
            category_model = Category(name=category)
            category_model.save()

    def handle(self, *args, **options):
        self._create_categories()