from app.security.instance.menu_module import MenuModule
from app.security.mixins.mixins import PermissionMixin
from django.views.generic import TemplateView
from app.core.models import Nivel, Progreso, Feedback

class FeedbackTemplateView(TemplateView):
    template_name = 'lecciones/feedbacks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title1"] = "DN - Feedback"

        # Obtener todos los niveles
        niveles = Nivel.objects.all().order_by('orden')
        
        # Obtener el progreso del usuario actual
        usuario = self.request.user
        progreso_usuario = Progreso.objects.filter(usuario=usuario)

        # Crear un diccionario que asocie cada nivel con su estado de completado y feedback
        niveles_con_feedback = []
        for nivel in niveles:
            progreso = progreso_usuario.filter(nivel=nivel).first()
            if progreso and progreso.completado:
                # Si el nivel está completado, buscar el feedback
                feedback = Feedback.objects.filter(usuario=usuario, nivel=nivel).first()
                feedback_disponible = True if feedback else False
            else:
                feedback_disponible = False  # Si el nivel no está completado, no puede haber feedback

            # Añadir el estado del nivel y feedback
            niveles_con_feedback.append({
                'nivel': nivel,
                'feedback_disponible': feedback_disponible,  # Estado del feedback
                'completado': progreso.completado if progreso else False  # Verificar si el nivel está completado
            })

        # Pasar los niveles con su estado de completado y feedback al contexto
        context["niveles_con_feedback"] = niveles_con_feedback
        return context
