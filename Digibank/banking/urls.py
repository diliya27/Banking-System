
from django.urls import path
from banking.views import *
from banking import *
from . import views

urlpatterns = [
    path('',index,name='index'),
    path('create_account/',views.create_account_view,name='create_account'),
    path('login/', views.login_view, name='login'),
    path('user_dashboard',views.user_dashboard_view,name='user_dashboard'),
    path('accounts',views.accounts_page,name='accounts'),
    
    path('deposit/', views.deposit_create_view, name='deposit'),
    path('deposit/razorpay/order/<int:deposit_id>/', views.create_razorpay_order_view, name='create_razorpay_order'),
    path('razorpay/callback/', views.razorpay_callback, name='razorpay_callback'),
    path('account_transfer/',views.account_transfer_view,name='account_transfer'),
    path('view_statement',views.view_statement,name='view_statement'),
    
    
    path("transfer/", account_transfer_view, name="account_transfer"),
    path("transfer/order/<int:transfer_id>/", transfer_razorpay_order_view, name="transfer_razorpay_order"),
    path("razorpay/callback/tranfer/", razorpay_transfer_callback, name="razorpay_transfer_callback"),

    path("transfers/", views.transfer_view, name="transfers"),

    path("billpay",views.billpay,name="billpay"),
    path("kseb_billpay",views.kseb_pay_view,name='kseb_billpay'),
    # path("kseb_razorpay",views.)
    
    path("dish_billpay",views.dish_billpay_view,name='dish_billpay'),
    path("water_billpay",views.water_billpay_view,name='water_billpay'),

    
]

