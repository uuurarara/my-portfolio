# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm,ProfileForm,UserSearchForm,UserUpdateForm,ProfileUpdateForm
from .models import Friendship, FriendRequest, Profile,CustomUser,Notification,UserProfile
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import get_user_model,update_session_auth_hash
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction    
from django.views.decorators.http import require_POST
from .utils import calculate_midpoint
from django.http import HttpResponseBadRequest



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

    # 未読の通知
    notifications = request.user.notifications.filter(is_read=False)
    
    context = {
        'friend_requests_received': friend_requests_received,
        'notifications': notifications,
    }
    
    return render(request, 'home.html', context)



def base_generic(request):
    return render(request, "accounts/base_generic.html")


#ユーザー編集機能
@login_required
def profile_edit(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
        
    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)
    pw_form = PasswordChangeForm(user=request.user)
        
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'プロフィールが更新されました')
                return redirect('profile', user_id=request.user.id)

        elif 'change_password' in request.POST:
            pw_form = PasswordChangeForm(user=request.user, data=request.POST)
            if pw_form.is_valid():
                pw_form.save()
                update_session_auth_hash(request, pw_form.user)
                context = {
                    'message': 'パスワードが変更されました',
                }
                return render(request, 'accounts/pw.html', context)
            else:
                messages.error(request, 'パスワードの変更に失敗しました')

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'pw_form': pw_form,
    }

    return render(request, "accounts/profile_edit.html", context)

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
        return redirect('home')

    # 友達リクエストを作成
    FriendRequest.objects.create(from_user=request.user, to_user=to_user,is_accepted=False)

    # 通知を作成
    Notification.objects.create(
        user=to_user,
        message=f"{request.user.username} から友達リクエストが届いています。"
    )

    return redirect('home')

# 友達リクエストを承認するビュー
@login_required
@require_POST
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    
    # 友達リクエストの送信者と受信者のProfileが存在することを確認
    from_profile = friend_request.from_user.profile
    to_profile = friend_request.to_user.profile
    
    with transaction.atomic():
        # フレンド関係を追加
        to_profile.friends.add(from_profile)
        from_profile.friends.add(to_profile)
        
        # FriendRequest を更新
        friend_request.is_accepted = True
        friend_request.save()

        # 通知を作成
        Notification.objects.create(
            user=friend_request.from_user,
            message=f"{request.user.username} があなたの友達リクエストを承認しました。"
        )
    
    messages.success(request, "友達リクエストを承認しました。")
    return redirect('home')


    
# 友達リクエストの通知表示ビュー
@login_required
def notifications(request):
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'notifications.html', {'notifications': notifications})


# 友達リクエストを拒否するビュー
def reject_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)
    if friend_request.to_user == request.user:
        friend_request.delete()
        return redirect('profile', user_id=request.user.id)
    else:
        return redirect('home')

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
    return render(request, 'accounts/update_nearest_station.html', {'form': form})

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
    return render(request, 'accounts/shared_station.html', {
        'user_station': user_profile.nearest_station_name,
        'friend_station': friend.nearest_station_name,
        'mid_lat': mid_lat,
        'mid_lng': mid_lng,
    })

#中間地点をマップに表示するビューで計算結果をテンプレートに渡す。
def show_midpoint(request, friend_id):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    friend_profile = get_object_or_404(UserProfile, user_id=friend_id)

# 緯度・経度が設定されているか確認
    if None in (user_profile.station_latitude, user_profile.station_longitude,
                friend_profile.station_latitude, friend_profile.station_longitude):
        return HttpResponseBadRequest("One or both users do not have valid latitude and longitude.")
    
    
    midpoint_lat, midpoint_lng = calculate_midpoint(
        user_profile.station_latitude,
        user_profile.station_longitude,
        friend_profile.station_latitude,
        friend_profile.station_longitude
    )

    return render(request, 'midpoint.html', {
        'midpoint_lat': midpoint_lat,
        'midpoint_lng': midpoint_lng
    })


