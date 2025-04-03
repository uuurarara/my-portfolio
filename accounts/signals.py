# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


User = get_user_model()




#@receiver(post_save, sender=User)
#def create_profile(sender, instance, created, **kwargs):
    #if created:
        #Profile.objects.create(
            #user=instance,
            #station_latitude=0.0,
            #station_longitude=0.0
        #)

#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
    #if created:
        #UserProfile.objects.create(
            #user=instance,
            #station_latitude=0.0,  # デフォルトの緯度
            #station_longitude=0.0  # デフォルトの経度
        #)
