from django.core.management.base import BaseCommand
from .sample_posts import sample_posts
from network import models
import datetime
import random
import textwrap


def random_datetime_last_2_days():
    now = datetime.datetime.now()
    five_days_ago = now - datetime.timedelta(days=2)
    random_time = random.uniform(five_days_ago.timestamp(), now.timestamp())
    return datetime.datetime.fromtimestamp(random_time).astimezone(None)


class Command(BaseCommand):
    #args = '<foo bar ...>'
    #help = 'our help string comes here'

    def _create_samples(self):
        users = []
        posts = []
        for (username, user_posts) in sample_posts:
            # Create user
            user = models.User.objects.create_user(username, "example@example.com", "pass")
            user.save()
            users.append(user)

            for post in user_posts:
                posts.append((user, post, random_datetime_last_2_days()))

        posts.sort(key=lambda x: x[2])
        for (user, post, timestamp) in posts:
            new_post = models.Post(user=user, body=post)
            new_post.save()
            # force a timestamp
            models.Post.objects.filter(pk=new_post.pk).update(timestamp=timestamp)

        # Each user follows some users:
        for user in users:
            num_following = random.randint(3, 6)
            for to_follow in random.sample(users, num_following):
                if to_follow == user:
                    continue
                new_follow = models.Follow(follower=user, following=to_follow)
                new_follow.save()

        # Make each post get some likes
        for post in models.Post.objects.all():
            num_likes = random.randint(0, 10)
            for to_like in random.sample(users, num_likes):
                new_like = models.Like(user=to_like, post=post)
                new_like.save()

        extra_post = textwrap.dedent(
        """
            <script>
                function showAlert() {
                    alert("Hello! If you see an alert this page is not very safe.");
                }
            </script>
        """)
        new_post = models.Post(user=users[0], body=extra_post).save()

    def handle(self, *args, **options):
        self._create_samples()