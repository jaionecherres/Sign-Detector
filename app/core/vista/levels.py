from app.security.instance.menu_module import MenuModule
from app.security.mixins.mixins import PermissionMixin
from django.views.generic import TemplateView

class LevelsTemplateView(PermissionMixin,TemplateView):
    template_name = 'components/course.html'
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title1"]= "IC - Cursos"
        context["title2"]= "Cursos Disponibles"
        MenuModule(self.request).fill(context)
        print(context)
        return context