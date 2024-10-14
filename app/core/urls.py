# core/urls.py
from django.urls import path
from . import views

app_name = 'core' 

urlpatterns = [
    path('video_feed/<str:tipo_modelo>/', views.video_feed, name='video_feed'),
    path('detectar_senal/', views.detectar_senal, name='detectar_senal'),
    path('alfabeto/', views.alfabeto, name='alfabeto'),
    path('numeros/', views.numeros, name='numeros'),
]
