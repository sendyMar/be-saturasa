from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    google_picture_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
