from django.urls import path
from . import views



urlpatterns = [
path('', views.fis_loginuser, name='fis_home'),
    path('dashboard/', views.fis_dashboard, name='fis_dashboard'),
    # path('add/', views.addfees, name='addfees'),
    path('payments/', views.payments, name='fis_payments'),
    path('logout/', views.fis_logoutuser, name='fis_logoutuser'),
    # path('agreement/', views.agreement, name='agreement'),
    # #'''''''''''''''''''''
    # path('get_payment_methods/', views.get_payment_methods, name='get_payment_methods'),
    # path('execute_payment/', views.execute_payment, name='execute_payment'),
    # path('get_invoice_data/<int:invoice_id>/', views.get_invoice_data, name='get_invoice_data'),
]