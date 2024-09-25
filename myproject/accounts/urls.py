# accounts/urls.py
from django.urls import path
from .views import SignUpView
from accounts.views import bese_jeneric

from django.contrib import admin
urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path("",bese_jeneric),
    path('admin/', admin.site.urls),
]


# yourapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    
]






# yourapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('update_station/', views.update_nearest_station, name='update_nearest_station'),
    path('share_station/<int:friend_id>/', views.share_nearest_station, name='share_nearest_station'),
]
