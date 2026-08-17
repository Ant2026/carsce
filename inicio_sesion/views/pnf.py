from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone

from inicio_sesion.models import Nucleos, Pnf, PNFNucleo, Bitacora, DirectorGeneral, ControlEstudio

# pnfs_registrada
def pnfs_reg(request):
    cedula_usuario = request.session.get("cedula_usuario")

    nucleo = None

    # Buscar como Director General
    director = DirectorGeneral.objects.select_related(
        "nucleo"
    ).filter(
        usuario__cedula_identidad=cedula_usuario
    ).first()

    if director:
        nucleo = director.nucleo

    # Si no es Director, buscar como Control de Estudio
    if not nucleo:
        control = ControlEstudio.objects.select_related(
            "nucleo"
        ).filter(
            usuario__cedula_identidad=cedula_usuario
        ).first()

        if control:
            nucleo = control.nucleo

    if not nucleo:
        return JsonResponse({
            "estado": "error",
            "mensaje": "El usuario no tiene un núcleo asignado."
        }, status=404)

    datos = []

    nucleos = Nucleos.objects.filter(
        id_nucleo=nucleo.id_nucleo
    ).prefetch_related(
        "pnfnucleo_set__id_pnf"
    )

    for nucleo in nucleos:
        datos.append({
            "id_nucleo": nucleo.id_nucleo,
            "municipio": nucleo.municipio,
            "pnfs": [
                {
                    "id_pnf": relacion.id_pnf.id_pnf,
                    "pnf": relacion.id_pnf.pnf,
                    "codigo": relacion.id_pnf.codigo,
                    "periodo_academico": relacion.id_pnf.periodo_academico,
                }
                for relacion in nucleo.pnfnucleo_set.all()
            ]
        })

    return JsonResponse({
        "estado": "exito",
        "nucleos": datos
    })

# datos_pnf
def datos_pnf(request):
    if request.method == "POST":
        codigo_pnf = request.POST.get("codigo")

        director = DirectorGeneral.objects.select_related(
            "nucleo"
        ).get(
            usuario__cedula_identidad=request.session.get("cedula_usuario")
        )

        try:
            pnf = Pnf.objects.get(codigo=codigo_pnf)
        except Pnf.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Verifique que si se encuentra registrado."
            })

        # Validar asignación del PNF al núcleo del director
        existe_asignacion = PNFNucleo.objects.filter(
            id_pnf_id=pnf.id_pnf,
            id_nucleo_id=director.nucleo_id
        ).exists()

        if not existe_asignacion:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "PNF no permitido",
                "descripcion": "El PNF seleccionado no pertenece al núcleo asignado al Director General."
            })

        return JsonResponse({
            "estado": "exito",
            "title": "PNF encontrado",
            "descripcion": "El PNF se encuentra Registrado",
            "pnf": {
                "id": pnf.id_pnf,
                "nombre": pnf.pnf,
                "periodo_academico": pnf.periodo_academico
            }
        })

# guardar_actuailizacion_pnf
def act_pnf(request):
    if request.method == "POST":
        id_pnf = request.POST.get("pnfseleccionado")
        nombre_pnf = request.POST.get("nombrepnf")
        periodoacademico_pnf = request.POST.get("periodoacademico")

        controles = [
            (nombre_pnf, "Nombre del PNF", "Debe ingresar el nombre del PNF."),
            (periodoacademico_pnf, "Periodo Académico", "Debe seleccionar el periodo académico.")
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })

        try:
            with transaction.atomic():

                pnf = Pnf.objects.get(id_pnf=id_pnf)

                pnf.pnf = nombre_pnf
                pnf.periodo_academico = periodoacademico_pnf
                pnf.save()

                Bitacora.objects.create(
                    nombre_usuario=request.session.get("usuario_nombre"),
                    accion=f"Actualización del PNF: {nombre_pnf} y periodo académico: {periodoacademico_pnf}.",
                    fecha_hora=timezone.now()
                )

                return JsonResponse({
                    "estado": "exito",
                    "icon": "success",
                    "title": "Éxito",
                    "descripcion": "Los datos del PNF se actualizaron exitosamente."
                })

        except Pnf.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "PNF no encontrado",
                "descripcion": "El PNF seleccionado no existe."
            })

    return render(request, "Director_General/pnf/actualizar_pnf.html")

def nombre_pnf(request):
    if request.method == "POST":
        pnf = request.POST.get("nombrepnf")

        existe = Pnf.objects.filter(pnf__iexact=pnf).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def codigo_pnf(request):
    if request.method == "POST":
        codigo_pnf = request.POST.get("codigopnf")

        existe = Pnf.objects.filter(codigo__iexact=codigo_pnf).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def reg_pnf(request):
    if request.method == "POST":
        nombre_pnf = request.POST.get("nombrepnf")
        codigo_pnf = request.POST.get("codigopnf")
        periodoacademico_pnf = request.POST.get("periodoacademico")

        controles = [
            (nombre_pnf, "Nombre del PNF", "Debe ingresar el nombre del PNF."),
            (codigo_pnf, "Código del PNF", "Debe ingresar el código del PNF."),
            (periodoacademico_pnf, "Periodo Académico", "Debe seleccionar el periodo académico.")
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })
      
        director = DirectorGeneral.objects.select_related(
            "nucleo"
        ).get(
            usuario__cedula_identidad=request.session.get("cedula_usuario")
        )

        nucleo_director = director.nucleo

        with transaction.atomic():
   
            pnf = Pnf.objects.create(pnf=nombre_pnf, codigo=codigo_pnf, periodo_academico=periodoacademico_pnf)

            # Relacionarlo automáticamente con el núcleo del Director
            PNFNucleo.objects.create(id_pnf=pnf, id_nucleo=nucleo_director)

            Bitacora.objects.create(
                nombre_usuario=request.session.get("usuario_nombre"),
                accion=f"Registro del PNF: {nombre_pnf} con código: {codigo_pnf} y periodo académico: {periodoacademico_pnf}.",
                fecha_hora=timezone.now()
            )

            return JsonResponse({
                "estado": "exito",
                "icon": "success",
                "title": "Exito",
                "descripcion": "Los datos del PNF han sido registrados correctamente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Error",
            "descripcion": "Hubo un error al registrar los datos del PNF."
        })
    
    return render(request, "Director_General/pnf/registrar_pnfs.html")

def ver_pnf(request):
    return render(request, "Director_General/pnf/visualizar_pnf.html")