from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from app.security.forms.auth import CustomUserCreationForm, CustomUserUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# ----------------- Perfil -----------------
def profile(request):
    data = {"title1": "DN - Perfil",
            "title2": "Perfil de Usuario"}
    return render(request, 'core/editperfil/profile.html', data)

#  Actualizar perfil 
@login_required
def update_profile(request):
    data = {"title1": "DN - Actualizar Perfil", "title2": "Actualizar Perfil"}
    
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('security:auth_profile')
        else:
            messages.error(request, 'Error en los datos del formulario.')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    
    return render(request, 'core/editperfil/update_profile.html', {'form': form, **data})

@login_required
def signout(request):
    logout(request)
    return redirect("home")

# ----------------- Registro -----------------
# ----------------- Registro -----------------
from django.contrib.auth.models import Group

def signup(request):
    data = {"title1": "DN - Registro", "title2": "Registro de Usuarios"}
    
    if request.method == "GET":
        # Renderiza el formulario vacío en caso de GET
        return render(request, "security/auth/signup.html", {"form": CustomUserCreationForm(), **data})
    else:
        # Procesa el formulario enviado por POST
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Si el formulario es válido, guarda el usuario
            user = form.save()

            # Asigna el grupo "user" automáticamente al nuevo usuario
            user_group = Group.objects.get(name='User')
            user.groups.add(user_group)

            username = form.cleaned_data.get('username')
            messages.success(request, f"Bienvenido {username}, tu cuenta ha sido creada exitosamente. Inicia sesión para continuar.")
            return redirect("security:auth_login")  # Redirige a la página de inicio de sesión
        else:
            # Si hay errores en el formulario, muestra el formulario con los errores
            messages.error(request, "Error al registrar el usuario. Por favor, revisa los datos ingresados.")
            return render(request, "security/auth/signup.html", {"form": form, **data})

# ----------------- Iniciar Sesión -----------------
def signin(request):
    data = {"title1": "DN - Login", "title2": "Inicio de Sesión"}
    
    if request.method == "GET":
        success_messages = messages.get_messages(request)
        return render(request, "security/auth/signin.html", {"form": AuthenticationForm(), "success_messages": success_messages, **data})
    
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Verifica si el usuario pertenece al grupo de administradores
                if user.groups.filter(name='Administradores').exists():
                    return redirect("modulos")  # Redirige a los módulos de seguridad
                else:
                    return redirect("levels")  # Redirige a los módulos de lecciones

            else:
                messages.error(request, "El usuario o la contraseña son incorrectos")
        
        return render(request, "security/auth/signin.html", {"form": form, "error": "Datos inválidos", **data})

@login_required
def modulos_seguridad(request):
    # Lógica para mostrar los módulos de seguridad
    return render(request, "security/modulos.html")

@login_required
def modulos_lecciones(request):
    # Lógica para mostrar los módulos de lecciones para usuarios
    return render(request, "core/course.html")

def actulizarcontra(request):
    # Cambiar contraseña del usuario
    data = {"title1": "CS-ACTUALIZAR", "title2": "Actualizar Contraseña"}
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        data["form"] = form
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Actualiza la sesión con la nueva contraseña
            return redirect('home')  # Redirige a la página de perfil o cualquier otra página
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.', extra_tags='alert-error')
    else:
        form = PasswordChangeForm(request.user)
        data["form"] = form
    return render(request, 'security/auth/contra_actualizar.html', data)
    
    
