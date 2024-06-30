from django.db import models

# Create your models here.


# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    nearest_station = models.CharField(max_length=100)

    def __str__(self):
        return self.username
