from django.shortcuts import render
from django.http import JsonResponse

from inicio_sesion.models import  Nucleos, AulaAcademica

from collections import defaultdict

def aulas_registrados(request):
    if request.method == "POST":
        id_nucleo = request.POST.get("id_nucleo")

        aulas = AulaAcademica.objects.filter(
            id_nucleo=id_nucleo
        ).values(
            "id_aula",
            "nombre_aula",
            "nombre_edificio",
            "piso_edificio"
        )

        return JsonResponse({
            "success": True,
            "aulas": list(aulas)
        })

def aulas_almacenadas(request):
    aulas_queryset = AulaAcademica.objects.all().select_related("id_nucleo").values(
        "id_aula",
        "nombre_aula",
        "nombre_edificio",
        "piso_edificio",
        "id_nucleo__municipio"
    )

    aulas_agrupadas = defaultdict(list)
    for aula in aulas_queryset:
        municipio = aula["id_nucleo__municipio"] or "Sin Municipio"
        aulas_agrupadas[municipio].append({
            "id_aula": aula["id_aula"],
            "nombre_aula": aula["nombre_aula"],
            "nombre_edificio": aula["nombre_edificio"],
            "piso_edificio": aula["piso_edificio"],
            "id_nucleo": municipio 
        })

    return JsonResponse(dict(aulas_agrupadas), safe=True)

def datos_aula(request):
    if request.method == "POST":
        id_aula = request.POST.get("id_aula")

        aula = AulaAcademica.objects.select_related("id_nucleo").get(id_aula=id_aula)

        return JsonResponse({
            "estado": "ok",
            "id_aula": aula.id_aula,
            "nombre_aula": aula.nombre_aula,
            "nombre_edificio": aula.nombre_edificio,
            "piso_edificio": aula.piso_edificio,
            "id_nucleo": aula.id_nucleo.id_nucleo,
            "municipio": aula.id_nucleo.municipio
        })
    
def actualizar_aula_academica(request):
    if request.method == "POST":
        aula_seleccionado = request.POST.get("aulaseleccionar")
        nombre_aula = request.POST.get("actualizar_aula")
        edificio = request.POST.get("actualizar_edificio")
        piso = request.POST.get("actualizar_piso")
        id_nucleo = request.POST.get("actualizar_nucleo")

        if nombre_aula and edificio and piso and id_nucleo:

            nucleo = Nucleos.objects.get(id_nucleo=id_nucleo)
            aula = AulaAcademica.objects.get(id_aula=aula_seleccionado)

            aula.nombre_aula = nombre_aula
            aula.nombre_edificio = edificio
            aula.piso_edificio = piso
            aula.id_nucleo = nucleo

            aula.save()

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "El aula se actualizó exitosamente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })
    
def modulo_aula_academica(request):
    if request.method == "POST":
        aula = request.POST.get("registrar_aula")
        edificio = request.POST.get("registrar_edificio")
        piso = request.POST.get("registrar_piso")
        id_nucleo = request.POST.get("registrar_nucleo")

        if aula and edificio and piso and id_nucleo:
            existe = AulaAcademica.objects.filter(nombre_aula__iexact=aula).exists()
            if existe:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "Ya existe una aula registrada con el mismo nombre."
                })
            
            nucleo = Nucleos.objects.get(id_nucleo=id_nucleo)

            AulaAcademica.objects.create(nombre_aula=aula, nombre_edificio=edificio, piso_edificio=piso, id_nucleo=nucleo)
            
            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Se registro exitosamente el aula académica."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })

    return render(request, "Director_General/aulas_academicas.html")