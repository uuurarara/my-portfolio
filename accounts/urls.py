# accounts/urls.py

from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import show_midpoint
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friends/', views.friends_list, name='friends_list'),
    path('search_users/', views.search_users, name='search_users'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),  
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('base-generic/', views.base_generic, name='base_generic'), 
    path('midpoint/<int:friend_id>/', show_midpoint, name='show_midpoint'),

    # ✅ パスワードリセット関連（テンプレートをカスタム指定）
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html',
             email_template_name='password_reset_email.html',
             subject_template_name='password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_done')
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
]
