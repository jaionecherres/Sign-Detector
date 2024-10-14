from django.contrib import admin
from app.security.models import GroupModulePermission, Module, Menu, User, Dashboard
admin.site.register(Module)
admin.site.register(Menu)
admin.site.register(User)
admin.site.register(GroupModulePermission)
admin.site.register(Dashboard)
