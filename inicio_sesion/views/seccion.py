from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone

from inicio_sesion.models import Pnf, SeccionAcademica, AulaAcademica, DirectorGeneral, Bitacora

# secciones_registradas
def sec_reg(request):
    secciones = list(
        SeccionAcademica.objects.values(
            "id_seccion",
            "seccion",
            "turno",
            "id_nucleo__municipio",
            "id_pnf__pnf",
            "trayecto",
            "id_aula__nombre_aula",
            "id_aula__nombre_edificio",
            "id_aula__piso_edificio"
        )
    )

    return JsonResponse({
        "estado": "exito",
        "secciones": secciones
    })

def val_sec(request):
    if request.method == "POST":
        seccion = request.POST.get("seccion")
        id_seccion = request.POST.get("id_seccion")

        consulta = SeccionAcademica.objects.filter(seccion=seccion)

        if id_seccion:
            consulta = consulta.exclude(id_seccion=id_seccion)

        existe = consulta.exists()
        
        return JsonResponse({ "existe": existe })

def bus_aula(request):
    if request.method == "POST":
        aula = request.POST.get("aula")

        if not aula:
            return JsonResponse({
                "estado": "fallo",
                "secciones": []
            })
        
        secciones = list(
            SeccionAcademica.objects.filter(id_aula=aula).values(
                "id_seccion",
                "seccion",
                "trayecto",
                "turno",
                "id_pnf__pnf",
            )
        )

        return JsonResponse({
            "estado": "exito",
            "secciones": secciones
        })

def turno_sec(request):
    if request.method == "POST":
        id_seccion = request.POST.get("id_seccion")
        turno = request.POST.get("turno")

        seccion = (
            SeccionAcademica.objects
            .exclude(id_seccion=id_seccion)
            .filter(turno=turno)
            .select_related("id_pnf", "id_aula")
            .first()
        )

        secciones = SeccionAcademica.objects.select_related(
            "id_pnf",
            "id_aula",
        ).values(
            "id_seccion",
            "seccion",
            "turno",
            "trayecto",
            "id_pnf__pnf",
            "id_aula__nombre_aula"
        )

        return JsonResponse({
            "existe": seccion is not None,
            "seccion": {
                "id": seccion.id_seccion,
                "seccion": seccion.seccion,
                "turno": seccion.turno,
                "trayecto": seccion.trayecto,
                "pnf": seccion.id_pnf.nombre,
                "aula": seccion.id_aula.nombre,
                "nucleo": seccion.id_nucleo.nombre
            } if seccion else None,
            "secciones": list(secciones)
        })

def act_turno(request):
    if request.method == "POST":
        try:
            accion = request.POST.get("accion")
            id_actual = request.POST.get("id_actual")
            id_otro = request.POST.get("id_otro")

            with transaction.atomic():
                actual = SeccionAcademica.objects.get(id_seccion=id_actual)

                if accion == "intercambio":
                    otra = SeccionAcademica.objects.get(id_seccion=id_otro)
                    actual.turno, otra.turno = otra.turno, actual.turno

                    actual.save(update_fields=["turno"])
                    otra.save(update_fields=["turno"])

                    descripcion = "Los turnos se intercambiaron correctamente."

                else:
                    actual.turno = request.POST.get("turno")
                    actual.save(update_fields=["turno"])

                    descripcion = "El turno se actualizó correctamente."

                return JsonResponse({
                    "estado": "exito",
                    "icon": "success",
                    "title": "Actualizado",
                    "descripcion": descripcion
                })

            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Ocurrio un error al momento de actualizar el turno"
            })

        except SeccionAcademica.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "No se encontró una de las secciones."
            })
        
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
                "seccion": seccion.seccion,
                "turno": seccion.turno,
                "trayecto": seccion.trayecto,
                "pnf": {
                    "id": seccion.id_pnf.id_pnf,
                    "nombre": seccion.id_pnf.pnf
                },
                "aula": {
                    "id": seccion.id_aula.id_aula,
                    "nombre": seccion.id_aula.nombre_aula
                }
            }
        })

# guardar_actualizacion_seccion
def guardar_act_sec(request):
    if request.method == "POST":
        id_seccion = request.POST.get("seccion")
        pnf = request.POST.get("actualizar_pnf")
        trayecto = request.POST.get("actualizar_trayecto")
        aula = request.POST.get("actualizar_aula")
        turno = request.POST.get("actualizar_turno")
        nuevo_seccion = request.POST.get("actualizar_seccion")

        controles = [
            (pnf, "P.N.F", "Por favor, debe seleccionar el programa nacional de formación que pertenecera."),
            (trayecto, "Trayecto", "Por favor, debe seleccionar el trayecto académico."),
            (aula, "Aula Académico", "Por favor, debe seleccionar el aula académica"),
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
                pnf = Pnf.objects.get(id_pnf=pnf)
                aula = AulaAcademica.objects.get(id_aula=aula)

                try:
                    seccion = SeccionAcademica.objects.get(id_seccion=id_seccion)
                except SeccionAcademica.DoesNotExist:
                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "error",
                        "title": "Error",
                        "descripcion": "No se encuentra registrada la sección."
                    })
                
                seccion.id_pnf = pnf
                seccion.trayecto = trayecto
                seccion.id_aula = aula
                seccion.turno = turno
                seccion.seccion = nuevo_seccion
                seccion.save()

                Bitacora.objects.create(
                    nombre_usuario=request.session.get("usuario_nombre"),
                    fecha_hora=timezone.now(),
                    accion=f"Se actualizo la sección {nuevo_seccion} del aula {aula} del turno {turno} utilizado por el P.N.F en {pnf.pnf}."
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
        pnf = request.POST.get("registro_pnf")
        trayecto = request.POST.get("registro_trayecto")
        aula = request.POST.get("registro_aula")
        turno = request.POST.get("registro_turno")
        seccion = request.POST.get("registro_seccion")
        
        controles = [
            (pnf, "P.N.F", "Por favor, debe seleccionar el programa nacional de formación que pertenecera."),
            (trayecto, "Trayecto", "Por favor, debe seleccionar el trayecto académico."),
            (aula, "Aula Académico", "Por favor, debe seleccionar el aula académica"),
            (turno, "Turno Académico", "Por favor, debe seleccionar el turno."),
            (seccion, "Nombre de la Sección", "Por favor, debe ingresar el nombre de la sección.")
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })

        director = DirectorGeneral.objects.filter(
            usuario__cedula_identidad=request.session.get("cedula_usuario")
        ).select_related(
            "nucleo"
        ).first()

        id_pnf = Pnf.objects.get(id_pnf=pnf)
        trayecto = trayecto
        id_aula = AulaAcademica.objects.get(id_aula=aula)
    
        SeccionAcademica.objects.create(
            id_nucleo=director.nucleo, 
            id_pnf=id_pnf, 
            trayecto=trayecto, 
            id_aula=id_aula, 
            turno=turno, 
            seccion=seccion
        )

        Bitacora.objects.create(
            nombre_usuario=request.session.get("usuario_nombre"),
            fecha_hora=timezone.now(),
            accion=f"Se actualizo la sección {seccion} del aula {aula} del turno {turno} utilizado por el P.N.F en {id_pnf.pnf}."
        )

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Exito",
            "descripcion": "La sección se registro exitosamente."
        })
    
    return render(request, "Director_General/session_academica/registrar_seccion.html")

