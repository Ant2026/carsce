from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse

from inicio_sesion.models import Nacimiento, Cuenta, Usuario

def autenticacion(request):
    if request.method == "POST":
        nombre_usuario = request.POST.get("usuario")
        contrasenia = request.POST.get("contrasenia")

        if not nombre_usuario:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacio",
                "icon": "warning",
                "descripcion": "Por favor, ingresa su nombre de usuario."
            })
        
        if not contrasenia:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacio",
                "icon": "warning",
                "descripcion": "Por favor, ingresa su contraseña."
            })
        try:
            credenciales = Cuenta.objects.get(usuario=nombre_usuario)
        except Cuenta.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "El usuario no se encuentra registrado."
            })
            
        coincide = check_password(credenciales.clave,contrasenia)
        if not coincide:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "La contraseña no coincide con la que esta registrada."
            })

        usuario = Usuario.objects.get(id_usuario=credenciales.id_usuario_id)


        request.session['cedula_usuario'] = usuario.cedula_identidad
        request.session['usuario_nombre'] = f"{usuario.nombres} {usuario.apellidos}"


        registro_basico = Nacimiento.objects.filter(id_usuario=usuario).exists()

        # registro_estudiante = InformacionSecundaria.objects.filter(id_usuario=usuario).exists()

        # request.session['registro_completado'] = (registro_basico or registro_estudiante)

    return render(request, 'Sesion/inicio_sesion.html')

def cerrar_sesion(request):
    request.session.flush() 
    return redirect("inicio_sesion")