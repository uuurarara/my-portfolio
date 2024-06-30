from django.contrib import admin

# Register your models here.


# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'name', 'email', 'address', 'nearest_station', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
