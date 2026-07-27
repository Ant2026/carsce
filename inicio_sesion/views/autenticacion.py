from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse

from inicio_sesion.models import Nacimiento, InformacionSecundaria, CredencialesUsuario

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

        credenciales = CredencialesUsuario.objects.select_related(
            'id_asignacion__id_usuario',
            'id_asignacion__id_perfil'
        ).filter(
            nombre_usuario=nombre_usuario
        ).first()
        if not credenciales:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "El usuario no se encuentra registrado."
            })

        if not check_password(contrasenia, credenciales.clave):
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "Contraseña incorrecta."
            })

        usuario = credenciales.id_asignacion.id_usuario
        perfil = credenciales.id_asignacion.id_perfil

        request.session['cedula_usuario'] = usuario.cedula_identidad
        request.session['usuario_nombre'] = f"{usuario.nombres} {usuario.apellidos}"
        request.session['perfil'] = perfil.perfil

        registro_basico = Nacimiento.objects.filter(id_usuario=usuario).exists()

        registro_estudiante = InformacionSecundaria.objects.filter(id_usuario=usuario).exists()

        request.session['registro_completado'] = (registro_basico or registro_estudiante)

        if not registro_basico:
            if perfil.perfil == "Estudiante":
                url = reverse("completar_registro_estudiante")
            else:
                url = reverse("completar_registro_personal")

        elif perfil.perfil == "Estudiante" and not registro_estudiante:
            url = reverse("completar_registro_pe")
        else:
            url = reverse("panel_usuario")

        print(url)

        return JsonResponse({
            "estado": "exito",
            "url": url
        })

    return render(request, 'Sesion/inicio_sesion.html')

def cerrar_sesion(request):
    request.session.flush() 
    return redirect("inicio_sesion")