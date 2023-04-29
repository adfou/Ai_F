from django.urls import path, re_path

from . import views

from .models import Account
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    re_path(r'^api/serp/$', views.serp_api),
    re_path(r'^api/registration/$', views.registration_view),
    re_path(r'^api/login/$', obtain_auth_token),
    re_path(r'^api/report/creat/$', views.create_report),
    re_path(r'^api/report/get/$', views.return_report),
    re_path(r'^api/report/compare/$', views.compare_report),
    re_path(r'^api/report/compare/news/$', views.compare_news),
    
    
    ]