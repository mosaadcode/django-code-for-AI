from django.urls import path
from . import views



urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.addfees, name='addfees'),
    path('recorded/', views.recorded, name='recorded'),
    path('agreement/', views.agreement, name='agreement'),
    # path('success/', views.payment_success, name='payment_success'),
    path('fail/', views.fail_page, name='fail_page'),
    # path('pending/', views.pending_page, name='pending_page'),
    # path('payment-response/', views.handle_payment_response, name='handle_payment_response'),
    path('payment-response/', views.handle_payment_response, name='payment_response'),
    

    path('pay-online/', views.Pay_online, name='pay_online'),
]
