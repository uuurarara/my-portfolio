# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from .models import Profile
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'address', 'nearest_station', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'address', 'nearest_station')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nearest_station_name', 'nearest_station_lat', 'nearest_station_lng']
 
 #友達検索機能
class UserSearchForm(forms.Form):
    username = forms.CharField(label='ユーザー名', max_length=100)     
    
    
#ユーザー編集機能    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
def __init__(self, *args, **kwargs):
    super(UserUpdateForm, self).__init__(*args, **kwargs)
    if 'username' in self.fields:
        self.fields['username'].label = 'ユーザー名'
        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'nearest_station']

    # 初期化時にフィールドのラベルなどを設定可能
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].label = '住所'
        self.fields['nearest_station'].label = '最寄駅'
    
    
    