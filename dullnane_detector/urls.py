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
    path('alfabeto/', views.home, name='alfabeto'),
    path('', HomeTemplateView.as_view(), name='home'),  
    path('admin/', admin.site.urls),
    #path('core/', include(('app.core.urls', 'core'), namespace='core')),
    path('core/', include('app.core.urls', namespace='core')),
    path('modulos/',ModuloTemplateView.as_view(), name='modulos'),
    path('levels/',LevelsTemplateView.as_view(), name='levels'),
    path('security/', include('app.security.urls', namespace='security')),
    #path('signs/', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
