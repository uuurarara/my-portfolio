# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('accounts/', include('accounts.urls')),
    #path('accounts/', include('django.contrib.auth.urls')),
    #path('',TemplateView.as_view(template_name='home.html'),name='home'),
    path('', include('accounts.urls')),
    
    
    
]
