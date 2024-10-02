from django.views.generic import TemplateView

class InvitadoTemplateView(TemplateView):  
    template_name = 'core/invitado/invitado.html'
    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = {"title1": "Invitado"}
        
        return context