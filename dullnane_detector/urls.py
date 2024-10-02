from django.conf import settings
from django.conf.urls.static import static
from app.core import views as core
from django.contrib import admin
from django.urls import path, include
from app.core.vista.home import HomeTemplateView
from app.core.vista.modulos import ModuloTemplateView

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),  
    path('admin/', admin.site.urls),
    path('core/', include('app.core.urls', namespace='core')),
    path('modulos/',ModuloTemplateView.as_view(), name='modulos'),
    path('security/', include('app.security.urls', namespace='security')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
