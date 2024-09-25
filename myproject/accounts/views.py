from django.shortcuts import render
def signup(request):
    return render(request, 'signup.html')

# Create your views here.


# accounts/views.py
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'base_jeneric.html' 'home.html' 'signup.html'
    
def bese_jeneric(request):
    return render(request,"accounts/base_jeneric.html" "accounts/home.html" "accounts/signup.html")


# yourapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Friendship, FriendRequest

@login_required
def send_friend_request(request, user_id):
    user_to = get_object_or_404(User, id=user_id)
    if user_to != request.user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=user_to)
    return redirect('profile', user_id=user_id)

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    if friend_request:
        Friendship.objects.create(user_from=friend_request.from_user, user_to=friend_request.to_user)
        friend_request.is_accepted = True
        friend_request.save()
    return redirect('profile', user_id=friend_request.from_user)

@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    if friend_request:
        friend_request.delete()
    return redirect('profile', user_id=friend_request.from_user)





# yourapp/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile, Friendship
from .forms import ProfileForm

@login_required
def update_nearest_station(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=request.user.id)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'yourapp/update_nearest_station.html', {'form': form})

@login_required
def share_nearest_station(request, friend_id):
    friend = get_object_or_404(Profile, user__id=friend_id)
    user_profile = get_object_or_404(Profile, user=request.user)

    # 両者の緯度経度を使って中間地点を計算
    mid_lat = (user_profile.nearest_station_lat + friend.nearest_station_lat) / 2
    mid_lng = (user_profile.nearest_station_lng + friend.nearest_station_lng) / 2

    return render(request, 'yourapp/shared_station.html', {
        'user_station': user_profile.nearest_station_name,
        'friend_station': friend.nearest_station_name,
        'mid_lat': mid_lat,
        'mid_lng': mid_lng,
    })

