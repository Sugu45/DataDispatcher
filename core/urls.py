from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

urlpatterns = [
    path('account_crud', views.account_crud, name='account_crud'),
    path('destination_crud', views.destination_crud, name='account_crud'),
    path('get_destinations/<account_id>', views.get_destinations, name='get_destinations'),
    path('server/incoming_data', views.incoming_data, name='incoming_data')]
