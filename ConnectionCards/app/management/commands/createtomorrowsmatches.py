from django.conf import settings
from django.core.management.base import BaseCommand
import app.util_matching as util_matching

class Command(BaseCommand):
    def handle(self, *args, **options):
        # For testing create tomorrows matches
        util_matching.create_tomorrows_matches()
