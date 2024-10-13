# core/urls.py
from django.urls import path
from . import views

app_name = 'core' 

urlpatterns = [
    path('video_feed/<str:tipo_modelo>/', views.video_feed, name='video_feed'),
    path('alfabeto/', views.alfabeto, name='alfabeto'),
    path('numeros/', views.numeros, name='numeros'),
]
