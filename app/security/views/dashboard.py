from django.views.generic import TemplateView
from app.core.models import Nivel, Progreso
from app.security.models import Dashboard

class DashboardTemplateView(TemplateView):
    template_name = 'security/dashboard/dashboard.html'  # Asegúrate de que el nombre sea el correcto

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title1"] = "Dashboard"

        # Obtener totales generales (usuarios registrados, terminados, cursando)
        totales_generales = Dashboard.obtener_totales_generales()
        context["totales_generales"] = totales_generales

        # Obtener el dashboard del usuario actual
        usuario = self.request.user
        dashboard, created = Dashboard.objects.get_or_create(usuario=usuario)
        
        # Pasar datos del dashboard al contexto
        context["dashboard"] = dashboard

        # Crear un diccionario que asocie cada nivel con su estado de desbloqueo y progreso
        progreso_usuario = Progreso.objects.filter(usuario=usuario)
        niveles = Nivel.objects.all().order_by('orden')
        niveles_con_progreso = []
        for nivel in niveles:
            progreso = progreso_usuario.filter(nivel=nivel).first()
            if progreso:
                desbloqueado = progreso.desbloqueado
                completado = progreso.completado
            else:
                desbloqueado = False  # Si no hay progreso para el nivel, está bloqueado
                completado = False  # Si no hay progreso, no está completado

            # Añadir el número total de alumnos por nivel
            alumnos_totales = Progreso.objects.filter(nivel=nivel).count()

            # Añadir el estado del nivel al diccionario
            niveles_con_progreso.append({
                'nivel': nivel,
                'desbloqueado': desbloqueado,
                'completado': completado,
                'alumnos_totales': alumnos_totales  # Cantidad de alumnos por nivel
            })

        # Pasar los niveles con su estado de desbloqueo y completado al contexto
        context["niveles_con_progreso"] = niveles_con_progreso

        return context
