from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction

from inicio_sesion.models import PNFNucleo, UsuarioAsignacion, Materia, MateriaAsignada

def pnfs_pertenece_nucleo(request):
    if request.method == "POST":
        nucleo = request.POST.get("nucleo")

        pnfs = PNFNucleo.objects.filter(
            id_nucleo=nucleo
        ).values(
            "id_pnf__id_pnf",
            "id_pnf__pnf",
            "id_pnf__periodo_academico"
        )

        lista = []

        for pnf in pnfs:
            lista.append({
                "id_pnf": pnf["id_pnf__id_pnf"],
                "pnf": pnf["id_pnf__pnf"],
                "periodo_academico": pnf["id_pnf__periodo_academico"],
            })

        return JsonResponse({"pnfs": lista})
    
def docentes_registrados(request):
    if request.method == "POST":
        nucleo = request.POST.get("nucleo")
        pnf = request.POST.get("pnf")

        if not nucleo or not pnf:
            return JsonResponse({
                "estado": "error",
                "usuarios": []
            })

        docentes = (
            UsuarioAsignacion.objects
            .select_related("id_usuario")
            .filter(
                id_perfil__perfil="Docente",
                id_nucleo_id=nucleo,
                id_pnf_id=pnf
            )
        )

        usuarios = [
            {
                "id_asignacion": docente.id_asignacion,
                "id_usuario": docente.id_usuario.id_usuario,
                "nombres": docente.id_usuario.nombres,
                "apellidos": docente.id_usuario.apellidos,
            }
            for docente in docentes
        ]

        return JsonResponse({
            "estado": "exito",
            "usuarios": usuarios
        })

    return JsonResponse({
        "estado": "error",
        "usuarios": []
    })

def materias_registradas(request):
    if request.method == "POST":
        pnf = request.POST.get("pnf")

        if not pnf:
            return JsonResponse({
                "estado": "error",
                "materias": []
            })

        materias = (
            Materia.objects
            .filter(id_pnf_id=pnf)
            .values(
                "id_materia",
                "nombre",
                "codigo",
                "tipo_materia",
                "recuperacion",
                "id_trayecto__trayecto"
            )
            .order_by(
                "id_trayecto__trayecto",
                "nombre"
            )
        )

        return JsonResponse({
            "estado": "exito",
            "materias": list(materias)
        })

    return JsonResponse({
        "estado": "error",
        "materias": []
    })

def modulo_asignar_materia_docente(request):
    if request.method == "POST":
        id_asignacion = request.POST.get("docentes")
        materias = request.POST.getlist("materias")

        if not id_asignacion or not materias:
            return JsonResponse({
                "estado": "error",
                "descripcion": "Debe seleccionar un docente y al menos una materia.",
                "icon": "warning"
            })

        asignacion = UsuarioAsignacion.objects.get(id_asignacion=id_asignacion)

        with transaction.atomic():
            for id_materia in materias:
                MateriaAsignada.objects.get_or_create(id_asignacion=asignacion, id_materia_id=id_materia)

        return JsonResponse({
            "estado": "success",
            "descripcion": "Las materias fueron asignadas correctamente al docente.",
            "icon": "success"
        })

    return render(request, "asignar_materia.html")