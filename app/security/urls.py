from django.urls import path
from app.security.views import auth
app_name='security' # define un espacio de nombre para la aplicación
urlpatterns = [    
    path('auth/login',auth.signin,name="auth_login"),
    path('auth/signup',auth.signup,name="auth_signup"),
    path('auth/logout',auth.signout,name='auth_logout'),
    path('auth/profile',auth.profile,name='auth_profile'),
    path('auth/update_profile',auth.update_profile,name='auth_update_profile'),
    path('auth/update_contra' , auth.actulizarcontra, name='auth_update_contra'),
]
    