
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

   
    # path('transaction/<int:user_id>/', perform_transaction, name='perform_transaction'),

    # path("deposittable/", views.deposittable_view, name="deposittable"),
    # path("confirm_deposit/", views.confirm_deposit, name="confirm_deposit"),
    # path("transaction_history/", views.transaction_history, name="transaction_history"),
    path("transfers/", views.transfer_view, name="transfers"),

    
]

