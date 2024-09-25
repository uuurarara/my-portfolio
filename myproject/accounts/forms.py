# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'address', 'nearest_station', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'address', 'nearest_station')
        
        
        
        
  # yourapp/forms.py

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nearest_station_name', 'nearest_station_lat', 'nearest_station_lng']
      