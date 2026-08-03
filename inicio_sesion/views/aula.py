from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone

from inicio_sesion.models import AulaAcademica, DirectorGeneral, Bitacora

# aulas_registrados
def aulas_reg(request):

    director = DirectorGeneral.objects.get(usuario__cedula_identidad=request.session.get("cedula_usuario"))

    aulas = AulaAcademica.objects.filter(
        id_nucleo=director.nucleo
    ).values(
        "id_aula",
        "nombre_aula",
        "nombre_edificio",
        "piso_edificio"
    )

    return JsonResponse({
        "aulas": list(aulas)
    })

# datos_aula
def datos_a(request):
    if request.method == "POST":
        id_aula = request.POST.get("id_aula")

        director = DirectorGeneral.objects.get(usuario__cedula_identidad=request.session.get("cedula_usuario"))

        aula = AulaAcademica.objects.select_related("id_nucleo").get(
            id_aula=id_aula,
            id_nucleo=director.nucleo
        )

        return JsonResponse({
            "id_aula": aula.id_aula,
            "nombre_aula": aula.nombre_aula,
            "nombre_edificio": aula.nombre_edificio,
            "piso_edificio": aula.piso_edificio,
            "id_nucleo": aula.id_nucleo.id_nucleo,
            "municipio": aula.id_nucleo.municipio
        })

def val_aula(request):
    if request.method == "POST":
        aula = request.POST.get("aula")

        existe = AulaAcademica.objects.filter(nombre_aula__iexact=aula).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

# actualizar_aula_academica
def act_aula_acad(request):
    if request.method == "POST":
        aula_seleccionado = request.POST.get("aulaseleccionar")
        nombre_aula = request.POST.get("actualizar_aula")
        edificio = request.POST.get("actualizar_edificio")
        piso = request.POST.get("actualizar_piso")

        controles = [
            (nombre_aula, "Nombre/Número del Aula", "Por favor, debe ingresar el nombre del aula."),
            (edificio, "Nombre del Edificio", "Por favor, debe ingresar el nombre del edificio."),
            (piso, "Piso de la Ubicación del Aula", "Por favor, debe ingresar el piso donde se encuentra el aula.")
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })
    
        aula = AulaAcademica.objects.get(id_aula=aula_seleccionado)

        aula.nombre_aula = nombre_aula
        aula.nombre_edificio = edificio
        aula.piso_edificio = piso
        aula.save()

        Bitacora.objects.create(
            nombre_usuario=request.session.get("usuario_nombre"),
            fecha_hora=timezone.now(),
            accion=f"Se actualizo la aula {nombre_aula} que se encuentra en el edificio{edificio} del piso {piso}."
        )

        return JsonResponse({
            "estado": "exito",
            "title": "Exito",
            "icon": "success",
            "descripcion": "El aula se actualizó exitosamente."
        })
    return render(request, "Director_General/aula/visualizar_aulas.html")

# modulo_aula_academica
def reg_aula(request):
    if request.method == "POST":
        nombre_aula = request.POST.get("registrar_aula")
        edificio = request.POST.get("registrar_edificio")
        piso = request.POST.get("registrar_piso")

        controles = [
            (nombre_aula, "Nombre/Número del Aula", "Por favor, debe ingresar el nombre del aula."),
            (edificio, "Nombre del Edificio", "Por favor, debe ingresar el nombre del edificio."),
            (piso, "Piso de la Ubicación del Aula", "Por favor, debe ingresar el piso donde se encuentra el aula.")
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })

        director = DirectorGeneral.objects.get(usuario__cedula_identidad=request.session.get("cedula_usuario"))

        AulaAcademica.objects.create(
            nombre_aula=nombre_aula,
            nombre_edificio=edificio,
            piso_edificio=piso,
            id_nucleo=director.nucleo
        )

        Bitacora.objects.create(
            nombre_usuario=request.session.get("usuario_nombre"),
            fecha_hora=timezone.now(),
            accion=f"Se registro la aula {nombre_aula} que se encuentra en el edificio{edificio} del piso {piso}."
        )

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Exito",
            "descripcion": "Se registró exitosamente el aula académica."
        })

    return render(request, "Director_General/aula/registrar_aula.html")


