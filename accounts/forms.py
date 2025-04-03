# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.contrib.auth import get_user_model
from .utils import get_lat_lng

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'address', 'nearest_station', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        from .utils import get_lat_lng
        if user.nearest_station:
            lat, lng = get_lat_lng(user.nearest_station)
            if lat is not None and lng is not None:
                user.station_latitude = lat
                user.station_longitude = lng
            else:
                print("駅の緯度経度が取得できませんでした")
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'email', 'address', 'nearest_station')

# 最寄駅の情報を編集するフォーム
class NearestStationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nearest_station_name', 'nearest_station_lat', 'nearest_station_lng']

# 友達検索機能
class UserSearchForm(forms.Form):
    username = forms.CharField(label='ユーザー名', max_length=100)

# ユーザー編集機能
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].label = 'ユーザー名'

# アドレスや最寄駅を編集するフォーム
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['address', 'nearest_station']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].label = '住所'
        self.fields['nearest_station'].label = '最寄駅'
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        from .utils import get_lat_lng  # 念のためここでインポート
        if instance.nearest_station:
            lat, lng = get_lat_lng(instance.nearest_station)
            instance.station_latitude = lat
            instance.station_longitude = lng
        if commit:
            instance.save()
        return instance


    