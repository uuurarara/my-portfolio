
# accounts/models.py
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import get_user_model
from django.conf import settings




class CustomUser(AbstractUser):
    name = models.CharField(max_length=100,verbose_name='名前')
    address = models.CharField(max_length=255, verbose_name='住所')
    nearest_station = models.CharField(max_length=100, verbose_name='最寄駅')
    email = models.EmailField(unique=True, max_length=255) 
    

    def __str__(self):
        return self.email

# プロフィールモデル
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    friends = models.ManyToManyField("self", blank=True, related_name="friends_list", symmetrical=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    nearest_station = models.CharField(max_length=255, blank=True, null=True)
    nearest_station_name = models.CharField(max_length=255, blank=True, null=True)  # 駅名
    nearest_station_lat = models.FloatField(blank=True, null=True)  # 緯度
    nearest_station_lng = models.FloatField(blank=True, null=True)  # 経度

    def __str__(self):
        return self.user.username 
    def add_friend(self, friend):
        """友達追加メソッド"""
        self.friends.add(friend)

    def remove_friend(self, friend):
        """友達削除メソッド"""
        self.friends.remove(friend)

    def is_friend(self, friend):
        """友達かどうか確認するメソッド"""
        return friend in self.friends.all()
    
# 友達リクエストモデル
class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='to_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"

# 友達関係モデル
class Friendship(models.Model):
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friends_from', on_delete=models.CASCADE)  
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friends_to', on_delete=models.CASCADE)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_from} <-> {self.user_to}"

#友達リクエストが届いているか確認通知機能
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message