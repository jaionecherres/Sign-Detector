from django.urls import path
from . import views
from .views import LeccionDetailView

app_name = 'core' 

urlpatterns = [
    path('leccion/<int:pk>/', LeccionDetailView.as_view(), name='leccion_detalle'),
    path('video_feed/<str:tipo_modelo>/', views.video_feed, name='video_feed'),
    path('detectar_senal/', views.detectar_senal, name='detectar_senal'),  
    path('alfabeto/', views.alfabeto, name='alfabeto'),
    path('numeros/', views.numeros, name='numeros'),
    path('colores/', views.colores, name='colores'),
    path('feedback/<int:nivel_id>/', views.feedback_nivel, name='feedback_nivel'),
    path('evaluacion_final/', views.evaluacion_final, name='evaluacion_final')
]
