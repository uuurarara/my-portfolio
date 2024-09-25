
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    name = models.CharField(max_length=100,verbose_name='名前')
    address = models.CharField(max_length=255, verbose_name='住所')
    nearest_station = models.CharField(max_length=100, verbose_name='最寄駅')

    def __str__(self):
        return self.username


# yourapp/models.py

from django.conf import settings
from django.db import models

class Friendship(models.Model):
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships_from', on_delete=models.CASCADE)
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships_to', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_from', 'user_to')

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_requests_received', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)




class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nearest_station_name = models.CharField(max_length=100)
    nearest_station_lat = models.FloatField()  # 緯度
    nearest_station_lng = models.FloatField()  # 経度

    def __str__(self):
        return f"{self.user.username}'s profile"
