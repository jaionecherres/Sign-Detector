from django.urls import path
from app.core.vista import invitado, niveles

app_name='core' # define un espacio de nombre para la aplicación
urlpatterns = [ 
    #Niveles
    # path('level_list/', niveles.LevelListView.as_view() ,name='level_list'),
    # path('level_create/', niveles.LevelCreateView.as_view(),name='level_create'),
    # path('level_update/<int:pk>/', niveles.LevelUpdateView.as_view(),name='level_update'),
    # path('level_delete/<int:pk>/', niveles.LevelDeleteView.as_view(),name='level_delete'),   
    
    
    
    # path('niveles/', niveles.NivelesTemplateView.as_view(), name='niveles'),
    # path('evaluacion/', evaluacion.EvaluacionTemplateView.as_view(), name='evaluacion'),
    # path('editarperfil/', editarpefil.EditProfileTemplateView.as_view(), name= 'editarperfil'),
    # path('perfil/', profile.ProfileTemplateView.as_view(), name= 'perfil'),
    #path('cambiarcontraseña/', cambiarcontraseña.CambiarContraseñaTemplateView.as_view(), name= 'cambiarcontraseña'),
    path('invitado/', invitado.InvitadoTemplateView.as_view(), name= 'invitado'),
    # path('Dashboard/', Dashboard.DashboardTemplateView.as_view(), name= 'Dashboard'),
    #path('login/', login.LoginTemplateView.as_view(), name='login'), 
    #path('register/', register.RegisterTemplateView.as_view(), name='register'),  
    # path('home2/', home2.Home2TemplateView.as_view(), name='home2'),  
    # path('feedback/', feedback.FeedbackTemplateView.as_view(), name='feedback'),
 ]
    