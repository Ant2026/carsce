from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction

from inicio_sesion.models import Nucleos, Pnf, PNFNucleo

from collections import defaultdict

def pnfs_registrada(request):

    data = PNFNucleo.objects.select_related("id_pnf", "id_nucleo")

    resultado = defaultdict(lambda: {
        "id_pnf": None,
        "pnf": "",
        "codigo": "",
        "nucleos": []
    })

    for item in data:
        pnf_id = item.id_pnf.id_pnf

        resultado[pnf_id]["id_pnf"] = pnf_id
        resultado[pnf_id]["pnf"] = item.id_pnf.pnf
        resultado[pnf_id]["codigo"] = item.id_pnf.codigo

        resultado[pnf_id]["nucleos"].append({
            "id_nucleo": item.id_nucleo.id_nucleo,
            "municipio": item.id_nucleo.municipio
        })

    return JsonResponse({
        "estado": "exito",
        "pnfs": list(resultado.values())
    })

def datos_pnf(request):
    if request.method == "POST":
        pnf = request.POST.get("pnf")

        pnfs = Pnf.objects.get(id_pnf=pnf)

        nucleos_asignados = []
        relaciones = PNFNucleo.objects.filter(id_pnf=pnfs)
        for relacion in relaciones:
            nucleos_asignados.append({
                "id": relacion.id_nucleo.id_nucleo,
                "municipio": relacion.id_nucleo.municipio
            })

        todos_nucleos = []
        for nucleo in Nucleos.objects.all():
            todos_nucleos.append({
                "id": nucleo.id_nucleo,
                "municipio": nucleo.municipio
            })

        return JsonResponse({
            "pnf": {
                "id": pnfs.id_pnf,
                "nombre": pnfs.pnf,
                "codigo": pnfs.codigo,
                "periodo_academico": pnfs.periodo_academico
            },
            "nucleos": nucleos_asignados,
            "todos_nucleos": todos_nucleos
        })

def guardar_actuailizacion_pnf(request):
    if request.method == "POST":
        id_pnf = request.POST.get("pnfseleccionado")
        nombre_pnf = request.POST.get("nombrepnf", "").strip()
        codigo_pnf = request.POST.get("codigopnf", "").strip()
        periodoacademico_pnf = request.POST.get("periodoacademico", "").strip()
        nucleos = request.POST.getlist("nucleo")

        if not id_pnf or not nombre_pnf or not codigo_pnf or not nucleos or not periodoacademico_pnf:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Se encuentra vacío al menos un campo."
            })

        try:
            with transaction.atomic():

                pnf = Pnf.objects.get(id_pnf=id_pnf)                
                pnf.pnf = nombre_pnf
                pnf.codigo = codigo_pnf
                pnf.periodo_academico = periodoacademico_pnf
                pnf.save()

                PNFNucleo.objects.filter(id_pnf=pnf).delete()

                for id_nucleo in nucleos:
                    nucleo = Nucleos.objects.get(id_nucleo=id_nucleo)
                    PNFNucleo.objects.create(
                        id_pnf=pnf,
                        id_nucleo=nucleo
                    )

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "PNF actualizado correctamente."
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

def modulo_pnf(request):
    if request.method == "POST":
        nombre_pnf = request.POST.get("nombrepnf")
        codigo_pnf = request.POST.get("codigopnf")
        periodoacademico_pnf = request.POST.get("periodoacademico")
        nucleos = request.POST.getlist("nucleos")

        if nombre_pnf and codigo_pnf and nucleos:
            existe = Pnf.objects.filter(codigo__iexact=codigo_pnf).exists()
            if existe:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Debe ingresar otro código."
                })

            existe = Pnf.objects.filter(pnf__iexact=nombre_pnf).exists()
            if existe:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe un Programa Nacional de Formación con ese nombre."
                })

            pnf_registrado = Pnf.objects.create(pnf=nombre_pnf, codigo=codigo_pnf, periodo_academico=periodoacademico_pnf)
            for nucleo_id in nucleos:
                PNFNucleo.objects.create(id_pnf=pnf_registrado, id_nucleo_id=nucleo_id)

            return JsonResponse({
                "icon": "success",
                "descripcion": "PNF se registro exitosamente."
            })

        return JsonResponse({
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })

    return render(request, "Director_General/pnfs.html")