from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction

from inicio_sesion.models import Nucleos, Pnf, SeccionAcademica, AulaAcademica

def secciones_registradas(request):
    secciones = list(
        SeccionAcademica.objects.values(
            "id_seccion",
            "seccion",
            "turno",
            "id_nucleo__municipio",
            "id_pnf__pnf",
            "id_trayecto__trayecto",
            "id_aula__nombre_aula",
            "id_aula__nombre_edificio",
            "id_aula__piso_edificio"
        )
    )

    return JsonResponse({
        "estado": "exito",
        "secciones": secciones
    })

def datos_seccion(request):
    if request.method == "POST":
        id_seccion = request.POST.get("seccion")

        seccion = SeccionAcademica.objects.filter(id_seccion=id_seccion).first()

        if not seccion:
            return JsonResponse({
                "estado": "error",
                "mensaje": "Sección no encontrada"
            })

        return JsonResponse({
            "estado": "ok",
            "seccion": {
                "id_seccion": seccion.id_seccion,
                "seccion": seccion.seccion,
                "turno": seccion.turno,
                "nucleo": {
                    "id": seccion.id_nucleo.id_nucleo,
                    "nombre": seccion.id_nucleo.municipio
                },
                "pnf": {
                    "id": seccion.id_pnf.id_pnf,
                    "nombre": seccion.id_pnf.pnf
                },
                "trayecto": {
                    "id": seccion.id_trayecto.id_trayecto,
                    "nombre": seccion.id_trayecto.trayecto
                },
                "aula": {
                    "id": seccion.id_aula.id_aula,
                    "nombre": seccion.id_aula.nombre_aula
                }
            }
        })
    
def guardar_actualizacion_seccion(request):
    if request.method == "POST":
        id_seccion = request.POST.get("seccion")
        nucleo = request.POST.get("actualizar_nucleo")
        pnf = request.POST.get("actualizar_pnf")
        trayecto = request.POST.get("actualizar_trayecto")
        aula = request.POST.get("actualizar_aula")
        turno = request.POST.get("actualizar_turno")
        nuevo_seccion = request.POST.get("actualizar_seccion")

        if not id_seccion or not nucleo or not pnf or not trayecto or not aula or not turno or not nuevo_seccion:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Se encuentra vacío al menos un campo."
            })

        try:
            with transaction.atomic():
                id_nucleo = Nucleos.objects.get(id_nucleo=nucleo)
                id_pnf = Pnf.objects.get(id_pnf=pnf)
                # id_trayecto = TrayectoAcademico.objects.get(id_trayecto=trayecto)
                id_aula = AulaAcademica.objects.get(id_aula=aula)
                seccion = SeccionAcademica.objects.get(id_seccion=id_seccion)

                seccion.id_nucleo = id_nucleo
                seccion.id_pnf = id_pnf
                # seccion.id_trayecto = id_trayecto
                seccion.id_aula = id_aula
                seccion.turno = turno
                seccion.seccion = nuevo_seccion

                seccion.save()

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Sección actualizado correctamente."
            })

        except Exception as e:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": str(e)
            })

    return JsonResponse({
        "estado": "fallo",
        "icon": "warning",
        "descripcion": "Método no permitido."
    })

def modulo_seccion(request):
    if request.method == "POST":
        nucleo = request.POST.get("registro_nucleo")
        pnf = request.POST.get("registro_pnf")
        trayecto = request.POST.get("registro_trayecto")
        aula = request.POST.get("registro_aula")
        turno = request.POST.get("registro_turno")
        seccion = request.POST.get("registro_seccion")
        
        if nucleo and pnf and trayecto and aula and turno and seccion:
            id_nucleo = Nucleos.objects.get(id_nucleo=nucleo)
            id_pnf = Pnf.objects.get(id_pnf=pnf)
            # id_trayecto = TrayectoAcademico.objects.get(id_trayecto=trayecto)
            id_aula = AulaAcademica.objects.get(id_aula=aula)
        
            # SeccionAcademica.objects.create(id_nucleo=id_nucleo, id_pnf=id_pnf, id_trayecto=id_trayecto, id_aula=id_aula, turno=turno, seccion=seccion)

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Sección se registro exitosamente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })
    
    return render(request, "secciones.html")