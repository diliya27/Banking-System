
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
    path('download-statement-pdf/', views.download_statement_pdf, name='download_statement_pdf'),
    
    
    path("transfer/", views.account_transfer_view, name="account_transfer"),
    path("transfer/order/<int:transfer_id>/",views. transfer_razorpay_order_view, name="transfer_razorpay_order"),
    path("razorpay/callback/tranfer/", views.razorpay_transfer_callback, name="razorpay_transfer_callback"),

    path("transfers/", views.transfer_view, name="transfers"),
    path('transactions/', views.transaction_history, name='transaction_history'),

    path('billpay/', views.billpay, name='billpay'),

    path('billpay/kseb/', views.kseb_pay_view, name='billpay_kseb'),
    path('billpay/kseb/razorpay/<int:kseb_pay_id>/',views. kseb_razorpay_view, name='billpay_razorpay'),
    path('razorpay/callback/kseb_billpay/', views.razorpay_kseb_callback, name='razorpay_kseb_callback'),
    
    path('water_billpay/', views.water_billpay_view, name='water_billpay'),
    path('water_billpay/razorpay/<int:water_billpay_id>/',views. water_razorpay_view, name='waterbill_razorpay'),
    path('razorpay/callback/water_billpay/',views. razorpay_water_callback, name='razorpay_water_callback'),
    
    
    path("dth/bill-payment/", dth_bill_payment_view, name="dth_bill_payment"),
    path("dth/payment/<int:dth_payment_id>/", dth_razorpay_payment_view, name="dth_razorpay_payment"),
    path("razorpay/callback/dth/", razorpay_dth_callback, name="razorpay_dth_callback"),

    path("loan_management/",views.loan_management_view,name="loan_management"),
    path("loan_details/<int:loan_id>/", loan_details_view, name="loan_details"),

    path("check_cibil_score",views.check_cibil_score,name="check_cibil_score"),

    path("submit_card_request/",views.submit_card_request,name="submit_card_request"),
    path("view_card_request/<int:card_request_id>/", views.view_card_request, name="view_card_request"),
    path("logout/", views.user_logout, name="logout"),


    
]

