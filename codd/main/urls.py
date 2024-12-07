from django.urls import path
from . import views

urlpatterns = [
    path('incidents/', views.incident_list, name='incident_list'),
    path('map/', views.map, name= 'map'),
]