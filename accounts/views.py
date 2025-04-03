# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserSearchForm, UserUpdateForm, UserProfileUpdateForm, NearestStationForm
from .models import Friendship, FriendRequest, CustomUser, Notification
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
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
    u_form = UserUpdateForm(instance=request.user)
    p_form = UserProfileUpdateForm(instance=request.user)
    pw_form = PasswordChangeForm(user=request.user)
        
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = UserProfileUpdateForm(request.POST, instance=request.user)
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
                messages.success(request, 'パスワードが変更されました')
                return redirect('profile_edit')
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

    with transaction.atomic():
        # `CustomUser` の `friends` フィールドに友達関係を追加
        request.user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(request.user)

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


@login_required
def friends_list(request):
    friends = request.user.friends_list.all()  # `CustomUser` の `friends` フィールドを取得
    return render(request, 'accounts/friends_list.html', {'friends': friends})




    
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

# ユーザーと友達の最寄駅を共有し、両者の中間地点を表示するビュー
@login_required
def show_midpoint(request, friend_id):
    user = request.user
    friend = get_object_or_404(CustomUser, id=friend_id)

    if None in (user.station_latitude, user.station_longitude, friend.station_latitude, friend.station_longitude):
        return HttpResponseBadRequest("One or both users do not have valid latitude and longitude.")

    midpoint_lat, midpoint_lng = calculate_midpoint(
        user.station_latitude,
        user.station_longitude,
        friend.station_latitude,
        friend.station_longitude
    )

    return render(request, 'midpoint.html', {
        'midpoint_lat': midpoint_lat,
        'midpoint_lng': midpoint_lng,
        'user_lat': user.station_latitude,
        'user_lng': user.station_longitude,
        'friend_lat': friend.station_latitude,
        'friend_lng': friend.station_longitude,
        'user_station_name': user.nearest_station,
        'friend_station_name': friend.nearest_station,
    })



@login_required
def update_nearest_station(request):
    if request.method == 'POST':
        form = NearestStationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "最寄駅の情報が更新されました。")
            return redirect('profile', user_id=request.user.id)
    else:
        form = NearestStationForm(instance=request.user)

    return render(request, 'accounts/update_nearest_station.html', {'form': form})
