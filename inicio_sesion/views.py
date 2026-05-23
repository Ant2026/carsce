from django.shortcuts import render, redirect
from .models import Usuario, UsuarioPerfil, Perfiles
from django.contrib.auth.hashers import check_password

# Create your views here.

def foro(request):
    return render(request, 'foro.html')

def inicio_sesion(request):

    if request.method == "POST":
        nombre_usuario = request.POST.get("usuario")
        contrasenia = request.POST.get("contrasenia")

        if nombre_usuario and contrasenia:

            try:
                usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)


                if check_password(contrasenia, usuario.clave):
                    nombre_completo = usuario.nombres + " " + usuario.apellidos

                    perfiles = Perfiles.objects.filter(
                        usuarioperfil__id_usuario=usuario
                    )

                    lista_perfiles = list(perfiles.values_list('perfil', flat=True))

                    request.session['usuario_nombre'] = nombre_completo
                    request.session['perfiles'] = lista_perfiles

                    return redirect("panel_usuario")
                else:
                    request.session['login_error'] = "Contraseña incorrecta"
                    return redirect("inicio_sesion")

            except Usuario.DoesNotExist:
                request.session['login_error'] = "Usuario no existe"
                return redirect("inicio_sesion")

        else:
            request.session['login_error'] = "Campos vacíos"
            return redirect("inicio_sesion")

    error = request.session.pop('login_error', None)
    return render(request, 'inicio_sesion.html', {'login_error': error})

def cerrar_sesion(request):
    request.session.flush() 
    return redirect("inicio_sesion")

def buscar_usuario(request):
    return render(request, 'buscar_usuario.html')

def panel_recuperar_credenciales(request):
    return render(request, 'panel_recuperar_credenciales.html')

def recuperar_contrasenia(request):
    return render(request, 'recuperar_contrasenia.html')

def recuperar_usuario(request):
    return render(request, 'recuperar_usuario.html')


def panel_registro(request):
    return render(request, 'panel_registro.html')

def confirmar_registro_personal(request):
    return render(request, 'confirmar_registro_personal.html')


def panel_usuario(request):
    return render(request, 'panel_usuario.html')

def inscripcion_estudiante(request):
    return render(request, 'inscripcion_estudiante.html')
