
from django.urls import path
from banking.views import *
from banking import *
from . import views
urlpatterns = [
    path('',index,name='index'),
    path('create_account/',views.create_account_view,name='create_account'),
    path('login/', views.login_view, name='login'),
    path('user_dashboard/',views.user_dashboard_view,name='user_dashboard'),
    
]
