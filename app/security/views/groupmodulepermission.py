from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from app.security.models import GroupModulePermission, Module, Group, Permission  # Asegúrate de importar correctamente los modelos
from app.security.forms.groupmodulepermission import GroupModulePermissionForm  # Asegúrate de importar correctamente el formulario GroupModulePermissionForm
from app.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from django.contrib import messages
from django.db.models import Q

class GroupModulePermissionListView(PermissionMixin, ListViewMixin, ListView):
    model = GroupModulePermission
    template_name = 'security/groupmodulepermission/list.html'  # Asegúrate de tener esta ruta correcta según tu estructura de templates
    context_object_name = 'group_module_permissions'
    permission_required = 'view_groupmodulepermission'  # Define aquí el permiso requerido para ver la lista de GroupModulePermission
    
    def get_queryset(self):
        q = self.request.GET.get('q')
        query = Q()
        if q:
            query = Q(group__name__icontains=q) | Q(module__name__icontains=q)
        return GroupModulePermission.objects.filter(query).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('security:groupmodulepermission_create')
        return context


class GroupModulePermissionCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = GroupModulePermission
    template_name = 'security/groupmodulepermission/form.html'
    form_class = GroupModulePermissionForm
    success_url = reverse_lazy('security:groupmodulepermission_list')
    permission_required = 'add_groupmodulepermission'

    def form_valid(self, form):
        group = form.cleaned_data['group']
        # Eliminar todos los permisos actuales del grupo seleccionado
        GroupModulePermission.objects.filter(group=group).delete()
        
        modules_selected = self.request.POST.getlist('modules[]')
        for module_id in modules_selected:
            module = Module.objects.get(id=module_id)
            new_group_module_permission = GroupModulePermission.objects.create(
                group=group,
                module=module,
            )
            permissions_selected = self.request.POST.getlist(f'permissions_{module_id}[]')
            new_group_module_permission.permissions.set(permissions_selected)
        
        messages.success(self.request, "Permisos de grupo para los módulos seleccionados creados exitosamente.")
        return redirect(self.success_url)

    def get_group_permissions(self, group_id):
        all_modules = Module.objects.all()
        group_module_permissions = GroupModulePermission.objects.filter(group_id=group_id).select_related('module')
        assigned_modules = {gmp.module.id: list(gmp.permissions.values('id', 'name')) for gmp in group_module_permissions}
        
        permissions_data = []
        for module in all_modules:
            module_data = {
                'module_id': module.id,
                'module_name': module.name,
                'permissions': list(module.permissions.values('id', 'name')),
                'assigned_permissions': assigned_modules.get(module.id, [])
            }
            permissions_data.append(module_data)
        
        return JsonResponse(permissions_data, safe=False)

class GroupModulePermissionDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = GroupModulePermission
    template_name = 'security/delete.html'  # Asegúrate de tener esta ruta correcta según tu estructura de templates
    success_url = reverse_lazy('security:groupmodulepermission_list')
    permission_required = 'delete_groupmodulepermission'  # Define aquí el permiso requerido para eliminar un GroupModulePermission
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, f"Permiso de grupo para módulo '{self.object.module.name}' eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['description'] = f"¿Está seguro que desea eliminar el permiso de grupo para el módulo '{self.object.module.name}'?"
        return context



def get_module_permissions(request, module_id):
    try:
        module = Module.objects.get(id=module_id)
        permissions = list(module.permissions.values('id', 'name'))
        return JsonResponse(permissions, safe=False)
    except Module.DoesNotExist:
        return JsonResponse({'error': 'Module not found'}, status=404)