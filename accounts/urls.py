# accounts/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import send_friend_request, accept_friend_request, reject_friend_request





urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('update_nearest_station/', views.update_nearest_station, name='update_nearest_station'),
    path('share_nearest_station/<int:friend_id>/', views.share_nearest_station, name='share_nearest_station'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'), # ログアウト後のリダイレクト先を指定
    path('search_users/', views.search_users, name='search_users'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),  
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('base-jeneric/', views.base_generic, name='base_jeneric'), 
    path('', views.home, name='home'),  # ホーム画面のURLを設定

    
]
    

