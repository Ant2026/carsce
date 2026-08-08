from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone

from inicio_sesion.models import SeccionAcademica, Bitacora

# secciones_registradas
def sec_reg(request):
    secciones = list(
        SeccionAcademica.objects.values(
            "id_seccion",
            "nombre",
            "turno"
        )
    )

    return JsonResponse({
        "estado": "exito",
        "secciones": secciones
    })

# validar el nombre de la sección
def val_sec(request):
    if request.method == "POST":
        seccion = request.POST.get("seccion")
        id_seccion = request.POST.get("id_seccion")

        consulta = SeccionAcademica.objects.filter(nombre=seccion)

        if id_seccion:
            consulta = consulta.exclude(id_seccion=id_seccion)

        existe = consulta.exists()
        
        return JsonResponse({ "existe": existe })

# datos_seccion
def datos_sec(request):
    if request.method == "POST":
        id_seccion = request.POST.get("seccion")

        try:
            seccion = SeccionAcademica.objects.filter(id_seccion=id_seccion).first()
        except SeccionAcademica.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "mensaje": "La sección académica no se encuentra registrada."
            })

        return JsonResponse({
            "estado": "exito",
            "seccion": {
                "id_seccion": seccion.id_seccion,
                "seccion": seccion.nombre,
                "turno": seccion.turno
            }
        })

# guardar_actualizacion_seccion
def guardar_act_sec(request):
    if request.method == "POST":
        id_seccion = request.POST.get("seccion")
        turno = request.POST.get("actualizar_turno")
        nuevo_seccion = request.POST.get("actualizar_seccion")

        controles = [
            (turno, "Turno Académico", "Por favor, debe seleccionar el turno."),
            (nuevo_seccion, "Nombre Sección", "Por favor, debe ingresar el nombre de la sección.")
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })
        
            with transaction.atomic():
                try:
                    seccion = SeccionAcademica.objects.get(id_seccion=id_seccion)
                except SeccionAcademica.DoesNotExist:
                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "error",
                        "title": "Error",
                        "descripcion": "No se encuentra registrada la sección."
                    })
                
                seccion.turno = turno
                seccion.nombre = nuevo_seccion
                seccion.save()

                Bitacora.objects.create(
                    nombre_usuario=request.session.get("usuario_nombre"),
                    fecha_hora=timezone.now(),
                    accion=f"Se actualizo la sección {nuevo_seccion}."
                )
                
                return JsonResponse({
                    "estado": "exito",
                    "icon": "success",
                    "title": "Exito",
                    "descripcion": "La sección se registro exitosamente."
                })

            return JsonResponse({
                "estado": "fallo",
                "icon": "Error",
                "title": "Error",
                "descripcion": "Ocurrio un error al momento de actualizar la sección."
            })

    return render(request, "Director_General/session_academica/visualizar_seccion.html")

# modulo_seccion
def reg_sec(request):
    if request.method == "POST":
        turno = request.POST.get("registro_turno")
        seccion = request.POST.get("registro_seccion")
        
        controles = [
            (seccion, "Nombre de la Sección", "Por favor, debe ingresar el nombre de la sección."),
            (turno, "Turno Académico", "Por favor, debe seleccionar el turno.")
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })
    
        SeccionAcademica.objects.create(
            turno=turno, 
            nombre=seccion
        )

        Bitacora.objects.create(
            nombre_usuario=request.session.get("usuario_nombre"),
            fecha_hora=timezone.now(),
            accion=f"Se actualizo la sección {seccion}."
        )

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Exito",
            "descripcion": "La sección se registro exitosamente."
        })
    
    return render(request, "Director_General/session_academica/registrar_seccion.html")

