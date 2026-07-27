from django.shortcuts import render
from django.http import JsonResponse

from inicio_sesion.models import Autoridades

def autoridades_registradas(request):
    autoridades = Autoridades.objects.all().values(
        "id_autoridad",
        "nombres",
        "apellidos",
        "cedula_identidad",
        "cargo",
        "resolucion"
    )

    return JsonResponse(list(autoridades), safe=False)

def datos_autoridad(request):
    if request.method == "POST":
        id_autoridad = request.POST.get("id")

        autoridad = Autoridades.objects.filter(id_autoridad=id_autoridad).first()

        if not autoridad:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "La autoridad no existe."
            })

        return JsonResponse({
            "id_autoridad": autoridad.id_autoridad,
            "nombres": autoridad.nombres,
            "apellidos": autoridad.apellidos,
            "cedula": autoridad.cedula_identidad,
            "genero": autoridad.genero,
            "cargo": autoridad.cargo,
            "resolucion": autoridad.resolucion
        })

def actualizar_datos_autoridad(request):
    if request.method == "POST":
        id_autoridad = request.POST.get("usuarioseleccionado")
        nombres = request.POST.get("nombres_actualizarautoridades")
        apellidos = request.POST.get("apellidos_actualizarautoridades")
        nacionalidad = request.POST.get("nacionalidad_actualizarautoridades")
        cedula = request.POST.get("cedula_actualizarautoridades")
        genero = request.POST.get("genero_actualizarautoridades")
        cargo = request.POST.get("cargo_actualizarautoridades")
        resolucion = request.POST.get("resolucion_actualizarautoridades")

        if nombres and apellidos and nacionalidad and cedula and genero and cargo and resolucion:
            
            cedula_identidad = nacionalidad + "-" + cedula

            autoridad = Autoridades.objects.filter(id_autoridad=id_autoridad).first()

            if not autoridad:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "La autoridad no existe."
                })
            
            autoridad.nombres = nombres
            autoridad.apellidos = apellidos
            autoridad.cedula_identidad = cedula_identidad
            autoridad.genero = genero
            autoridad.cargo = cargo
            autoridad.resolucion = resolucion
            autoridad.save()

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Se actualizo exitosamente los datos de la autoridad."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })

def modulo_autoridades(request):    
    if request.method == "POST":
        nombres = request.POST.get("nombres_registrarautoridades")
        apellidos = request.POST.get("apellidos_registrarautoridades")
        nacionalidad = request.POST.get("nacionalidad_actualizarautoridades")
        cedula = request.POST.get("cedula_registrarautoridades")
        genero = request.POST.get("genero_registrarautoridades")
        cargo = request.POST.get("cargo_registrarautoridades")
        resolucion = request.POST.get("resolucion_registrarautoridadess")

        if nombres and apellidos and nacionalidad and cedula and genero and cargo and resolucion:

            cedula_autoridad = nacionalidad + "-" + cedula

            if Autoridades.objects.filter(cedula_identidad__iexact=cedula_autoridad).exists():
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "Ya se encuentra registrado dicho usuario."
                })
            
            if Autoridades.objects.filter(resolucion__iexact=resolucion).exists():
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "Ya se encuentra registrado una resolución."
                })
            
            Autoridades.objects.create(nombres=nombres, apellidos=apellidos, cedula_identidad=cedula_autoridad, genero=genero, cargo=cargo, resolucion=resolucion)

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Las materias fueron asignadas correctamente al docente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })

    return render(request, "autoridades.html")