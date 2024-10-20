from app.security.instance.menu_module import MenuModule
from app.security.mixins.mixins import PermissionMixin
from django.views.generic import TemplateView
from app.core.models import Nivel, Progreso

class LevelsTemplateView(TemplateView):
    template_name = 'components/course.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title1"] = "IC - Cursos"

        #Obtener todos los niveles
        niveles = Nivel.objects.all().order_by('orden')
        
        #Obtener el progreso del usuario actual
        usuario = self.request.user
        progreso_usuario = Progreso.objects.filter(usuario=usuario)

        #Crear un diccionario que asocie cada nivel con su estado de desbloqueo
        niveles_con_progreso = []
        for nivel in niveles:
            progreso = progreso_usuario.filter(nivel=nivel).first()
            if progreso:
                desbloqueado = progreso.desbloqueado
            else:
                desbloqueado = False #Si no hay progreso para el nivel, está bloqueado
            niveles_con_progreso.append({
                'nivel': nivel,
                'desbloqueado': desbloqueado,
            })
        
        #Pasar los niveles con su estado de desbloqueo al contexto
        context["niveles_con_progreso"] = niveles_con_progreso
        return context
