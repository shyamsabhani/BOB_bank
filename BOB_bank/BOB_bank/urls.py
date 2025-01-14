"""
URL configuration for BOB_bank project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('admin/', admin.site.urls),
    path('user_login', views.user_login, name='user_login'),
    path('profile/', views.profile, name='profile'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('withdrawl/', views.withdrawal, name='withdrawal'),
    path('balance_check/', views.balance_check, name='balance'),
    path('send/', views.send, name='send'),
    path('deposite', views.deposite, name='deposite'),
    path('display_records/', views.display_records, name='transaction'),
    path('feedback/', views.feedback, name='feedback'),
]