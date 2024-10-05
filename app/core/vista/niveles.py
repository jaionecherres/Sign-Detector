# from django.urls import reverse_lazy
# from django.contrib import messages
# from django.db.models import Q
# from django.views.generic import CreateView, ListView, UpdateView, DeleteView
# from app.core.forms.niveles import LevelForm
# from app.core.models import Level  # Asegúrate de que el modelo Level esté correctamente importado
# from app.security.mixins.mixins import (
#     CreateViewMixin,
#     DeleteViewMixin,
#     ListViewMixin,
#     PermissionMixin,
#     UpdateViewMixin,
# )

# class LevelListView(PermissionMixin, ListViewMixin, ListView):
#     template_name = 'core/levels/list.html'
#     model = Level
#     context_object_name = 'levels'
#     permission_required = 'view_level'
#     query = Q()

#     def get_queryset(self):
#         q1 = self.request.GET.get('q')
#         if q1:
#             self.query.add(Q(name__icontains=q1), Q.OR)
#         return self.model.objects.filter(self.query).order_by('id')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['create_url'] = reverse_lazy('core:level_create')
#         return context

# class LevelCreateView(PermissionMixin, CreateViewMixin, CreateView):
#     model = Level
#     template_name = 'core/levels/form.html'
#     form_class = LevelForm
#     success_url = reverse_lazy('core:level_list')
#     permission_required = 'add_level'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['grabar'] = 'Grabar Nivel'
#         context['back_url'] = self.success_url
#         return context
    
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         level = self.object
#         messages.success(self.request, f"Éxito al crear el nivel {level.name}.")
#         return response
    
# class LevelUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
#     model = Level
#     template_name = 'core/levels/form.html'
#     form_class = LevelForm
#     success_url = reverse_lazy('core:level_list')
#     permission_required = 'change_level'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['grabar'] = 'Actualizar Nivel'
#         context['back_url'] = self.success_url
#         return context
    
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         level = self.object
#         messages.success(self.request, f"Éxito al actualizar el nivel {level.name}.")
#         return response
    
# class LevelDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
#     model = Level
#     template_name = 'core/delete.html'
#     success_url = reverse_lazy('core:level_list')
#     permission_required = 'delete_level'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['grabar'] = 'Eliminar Nivel'
#         context['description'] = f"¿Desea eliminar el nivel: {self.object.name}?"
#         context['back_url'] = self.success_url
#         return context
    
#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         success_message = f"Éxito al eliminar lógicamente el nivel {self.object.name}."
#         messages.success(self.request, success_message)
#         self.object.deleted = True  # Cambia a True si estás manejando eliminación lógica
#         self.object.save()
        
#         return super().delete(request, *args, **kwargs)
