# accounts/admin.py
from django.contrib import admin
from .models import CustomUser,FriendRequest, Friendship, Notification

admin.site.register(CustomUser)
admin.site.register(FriendRequest)
admin.site.register(Friendship)
admin.site.register(Notification)
