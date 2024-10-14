from django.urls import path
from app.security.views import auth, module, menu, groupmodulepermission

app_name='security'
urlpatterns = [    
    path('auth/login',auth.signin,name="auth_login"),
    path('auth/signup',auth.signup,name="auth_signup"),
    path('auth/logout',auth.signout,name='auth_logout'),
    path('auth/profile',auth.profile,name='auth_profile'),
    path('auth/update_profile',auth.update_profile,name='auth_update_profile'),
    path('auth/update_contra' , auth.actulizarcontra, name='auth_update_contra'),
    
    path('module_list/', module.ModuleListView.as_view(), name='module_list'),
    path('module_create/', module.ModuleCreateView.as_view(), name='module_create'),
    path('module_update/<int:pk>/', module.ModuleUpdateView.as_view(), name='module_update'),
    path('module_delete/<int:pk>/', module.ModuleDeleteView.as_view(), name='module_delete'),
    
    path('menu_list/', menu.MenuListView.as_view(), name='menu_list'),
    path('menu_create/', menu.MenuCreateView.as_view(), name='menu_create'),
    path('menu_update/<int:pk>/', menu.MenuUpdateView.as_view(), name='menu_update'),
    path('menu_delete/<int:pk>/', menu.MenuDeleteView.as_view(), name='menu_delete'),
    
    path('groupmodulepermission_list/', groupmodulepermission.GroupModulePermissionListView.as_view(), name='groupmodulepermission_list'),
    path('groupmodulepermission_create/', groupmodulepermission.GroupModulePermissionCreateView.as_view(), name='groupmodulepermission_create'),
    path('groupmodulepermission_delete/<int:pk>/', groupmodulepermission.GroupModulePermissionDeleteView.as_view(), name='groupmodulepermission_delete'),
    path('get_module_permissions/<int:module_id>/', groupmodulepermission.get_module_permissions, name='get_module_permissions'),
    path('get_group_permissions/<int:group_id>/', groupmodulepermission.GroupModulePermissionCreateView.get_group_permissions, name='get_group_permissions'),
]
    