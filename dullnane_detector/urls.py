from django.conf import settings
from django.conf.urls.static import static
from app.core import views as core
from django.contrib import admin
from django.urls import path, include
from app.core.vista.home import HomeTemplateView
from app.core.vista.modulos import ModuloTemplateView
from app.core.vista.levels import LevelsTemplateView
from app.core import views

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),  
    path('admin/', admin.site.urls),
    
    # path('alfabeto/', views.alfabeto, name='alfabeto'),
    # path('numeros/', views.numeros, name='numeros'),
    path('core/', include('app.core.urls', namespace='core')),
    path('levels/',LevelsTemplateView.as_view(), name='levels'),
    path('modulos/',ModuloTemplateView.as_view(), name='modulos'),
    path('security/', include('app.security.urls', namespace='security')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
