from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    body = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def timestamp_utc(self):
        return self.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

    def n_likes(self):
        return self.likes.count()

class Like(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    class Meta:
        unique_together = ('user', 'post')
