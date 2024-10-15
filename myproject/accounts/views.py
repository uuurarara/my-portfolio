# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import Friendship, FriendRequest, Profile,CustomUser
from .forms import ProfileForm
from django.contrib.auth.views import LoginView
from .forms import UserSearchForm
from django.contrib import messages
from .forms import UserUpdateForm
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Notification


User = get_user_model()

# ログイン用のビュー
class CustomLoginView(LoginView):
    template_name = 'login.html'

# サインアップ用のビュー
class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

# ベーステンプレート表示用ビュー
@login_required
def home(request):
    # 受け取った友達リクエスト
    friend_requests_received = request.user.received_requests.filter(is_accepted=False)
    # デバッグ用
    print(f"受け取ったリクエスト数: {friend_requests_received.count()}")

    # ユーザーの通知
    notifications = request.user.notifications.filter(is_read=False)
    # デバッグ用
    print(f"未読通知数: {notifications.count()}")

    context = {
        'friend_requests_received': friend_requests_received,
        'notifications': notifications,
    }
    
    return render(request, 'accounts/home.html', context)



def base_generic(request):
    return render(request, "accounts/base_generic.html")


#ユーザー編集機能
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'プロフィール情報が更新されました！')
            return redirect('profile', user_id=request.user.id)
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})


#友達検索機能用のビュー

@login_required
def search_users(request):
    query = request.GET.get('q')
    users = CustomUser.objects.filter(Q(email__icontains=query)) if query else None
    
    # デバッグ: クエリとユーザーリストを確認
    print(f"検索クエリ: {query}")
    if users:
        print(f"検索結果: {[user.email for user in users]}")
    else:
        print("ユーザーが見つかりませんでした。")
    
    # 各ユーザーに対してリクエスト済みかどうかを判定
    results = []
    if users:
        for user in users:
            # すでにリクエストを送っているかチェック
            request_sent = FriendRequest.objects.filter(from_user=request.user, to_user=user).exists()
            results.append((user, request_sent))  # (ユーザー, リクエスト済みかどうか) のタプルを追加

    return render(request, 'search.html', {'results': results,'query': query})

def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'profile.html', {'user': user})

# 友達リクエストを送信するビュー
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        # すでにリクエストが存在する場合
        return redirect('home')

    # 友達リクエストを作成
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)

    # 通知を作成
    Notification.objects.create(
        user=to_user,
        message=f"{request.user.username} から友達リクエストが届いています。"
    )

    return redirect('home')

# 友達リクエストを承認するビュー
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    if friend_request:
        Friendship.objects.create(user_from=friend_request.from_user, user_to=friend_request.to_user)
        friend_request.is_accepted = True
        friend_request.save()
    return redirect('profile', user_id=friend_request.from_user.pk)

# 友達リクエストの通知表示ビュー
@login_required
def notifications(request):
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'notifications.html', {'notifications': notifications})


# 友達リクエストを拒否するビュー
@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    if friend_request:
        friend_request.delete()
    return redirect('profile', user_id=friend_request.from_user.pk)

# ユーザーの最寄駅情報を更新するビュー
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

# ユーザーと友達の最寄駅を共有し、両者の中間地点を表示するビュー
@login_required
def share_nearest_station(request, friend_id):
    friend = get_object_or_404(Profile, user__id=friend_id)
    user_profile = get_object_or_404(Profile, user=request.user)
    # Noneチェックを追加
    user_lat = user_profile.nearest_station_lat if user_profile.nearest_station_lat is not None else 0.0
    friend_lat = friend.nearest_station_lat if friend.nearest_station_lat is not None else 0.0

    user_lng = user_profile.nearest_station_lng if user_profile.nearest_station_lng is not None else 0.0
    friend_lng = friend.nearest_station_lng if friend.nearest_station_lng is not None else 0.0

    # 中間地点を計算
    mid_lat = (user_lat + friend_lat) / 2
    mid_lng = (user_lng + friend_lng) / 2
    return render(request, 'yourapp/shared_station.html', {
        'user_station': user_profile.nearest_station_name,
        'friend_station': friend.nearest_station_name,
        'mid_lat': mid_lat,
        'mid_lng': mid_lng,
    })



