from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction

from inicio_sesion.models import Nucleos

def nucleos_registrados(request):
    nucleos = list(Nucleos.objects.values(
        "id_nucleo",
        "municipio",
        "direccion"
    ))

    return JsonResponse({
        "estado": "exito",
        "nucleos": nucleos
    })

def datos_nucleo(request):
    if request.method == "POST":
        id_nucleo = request.POST.get("nucleo")

        nucleo = Nucleos.objects.filter(id_nucleo=id_nucleo).first()

        if not nucleo:
            return JsonResponse({
                "estado": "error",
                "mensaje": "Núcleo no encontrado"
            })

        return JsonResponse({
            "estado": "ok",
            "nucleo": {
                "id": nucleo.id_nucleo,
                "municipio": nucleo.municipio,
                "direccion": nucleo.direccion
            }
        })

def guardar_actualizacion_nucleo(request):
    if request.method == "POST":
        id_nucleo = request.POST.get("nucleoseleccionado")
        municipio = request.POST.get("municipio")
        direccion = request.POST.get("direccionnucleo")

        if not id_nucleo or not municipio or not direccion:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Se encuentra vacío al menos un campo."
            })

        try:
            with transaction.atomic():

                nucleo = Nucleos.objects.get(id_nucleo=id_nucleo)                
                nucleo.municipio = municipio
                nucleo.direccion = direccion
                nucleo.save()

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

def modulo_nucleo(request):
    if request.method == "POST":
        municipio = request.POST.get("municipio")
        direccion = request.POST.get("direccion")
        
        if municipio and direccion:

            Nucleos.objects.create(municipio=municipio, direccion=direccion)

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Núcleo se registro exitosamente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })
    
    return render(request, "Director_General/nucleos.html")
