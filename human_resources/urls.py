from django.urls import path
from . import views
# from . import admin

urlpatterns = [

    path('', views.home, name='home2'),
    path('salary/', views.salary, name='salary'),
    path('perm/', views.perm, name='perm'),
    path('vacation/', views.vacation, name='vacation'),
    path('contact/', views.employee_contact, name='employee_contact'),
    path('delete_permission/<int:permission_id>/', views.delete_permission, name='delete_permission'),
    path('delete_vacation/<int:vacation_id>/', views.delete_vacation, name='delete_vacation'),
    path('rules/', views.rules, name='rules'),
    path('agree-to-rules/', views.agree_to_rules, name='agree_to_rules'),

]