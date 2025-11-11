from django.urls import path
from . import views



urlpatterns = [

    path('contact/', views.contact, name='contact'),
    path('application/', views.application, name='application'),
    path('nile-application/', views.nile_application, name='nile-application'),

]