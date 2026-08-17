from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse

from inicio_sesion.models import Nacimiento, Cuenta, Usuario, Estudiante, Docente, CoordinadorPNF, ControlEstudio, DirectorGeneral

def obtener_roles(usuario):
    roles = []

    for estudiante in Estudiante.objects.filter(usuario=usuario).select_related("nucleo", "pnf"):
        roles.append({
            "rol": "Estudiante",
            "nucleo": estudiante.nucleo.municipio if estudiante.nucleo else None,
            "pnf": estudiante.pnf.pnf if estudiante.pnf else None,
            "registro_completo": estudiante.nucleo is not None and estudiante.pnf is not None,
        })

    for docente in Docente.objects.filter(usuario=usuario).select_related("nucleo", "pnf"):
        roles.append({
            "rol": "Docente",
            "nucleo": docente.nucleo.municipio,
            "pnf": docente.pnf.pnf,
        })

    for coordinador in CoordinadorPNF.objects.filter(usuario=usuario).select_related("nucleo", "pnf"):
        roles.append({
            "rol": "Coordinador PNF",
            "nucleo": coordinador.nucleo.municipio,
            "pnf": coordinador.pnf.pnf,
        })

    for control in ControlEstudio.objects.filter(usuario=usuario).select_related("nucleo"):
        roles.append({
            "rol": "Control de Estudio",
            "nucleo": control.nucleo.municipio,
        })

    if DirectorGeneral.objects.filter(usuario=usuario).exists():
        roles.append({
            "rol": "Director General",
        })

    return roles

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
        
        coincide = check_password(contrasenia, credenciales.clave)
        if not coincide:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "La contraseña no coincide con la que esta registrada."
            })

        usuario = credenciales.id_usuario
        
        # --- AQUÍ ASIGNAMOS id_cuenta DESDE credenciales ---
        request.session['id_cuenta'] = credenciales.id_cuenta
        request.session['cedula_usuario'] = usuario.cedula_identidad
        request.session['usuario_nombre'] = f"{usuario.nombres} {usuario.apellidos}"

        roles = obtener_roles(usuario)
        request.session["roles"] = roles
        request.session["rol"] = [r["rol"] for r in roles]

        registro_basico = Nacimiento.objects.filter(id_usuario=usuario).exists()

        if registro_basico:
            request.session['registro_completado'] = True

            return JsonResponse({
                "estado": "exito",
                "url": reverse("panel_usuario")
            })
        else:
            request.session['registro_completado'] = False

            return JsonResponse({
                "estado": "exito",
                "url": reverse("comp_registro")
            })
    
    return render(request, 'Sesion/inicio_sesion.html')

def cerrar_sesion(request):
    request.session.flush() 
    return redirect("inicio_sesion")