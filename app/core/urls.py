from django.urls import path
from . import views

app_name = 'core'  # Asegúrate de tener esto para que funcione el namespace 'core'

urlpatterns = [
    path('video_feed/', views.video_feed, name='video_feed'),  # Ruta para video_feed
    path('alfabeto/', views.home, name='alfabeto'),  # Ruta para la vista de inicio
]
