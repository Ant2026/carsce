from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction

from inicio_sesion.models import Usuario, Nucleos, Contacto, PNFNucleo, Docente, CoordinadorPNF, ControlEstudio

import json

PERFILES = {
    "1": "Coordinador PNF",
    "2": "Control de Estudio",
    "3": "Docente"
}

def datos_perfiles(request):
    perfiles = [
        {
            "id_perfil": 1,
            "perfil": "Coordinador PNF"
        },
        {
            "id_perfil": 2,
            "perfil": "Control de Estudio"
        },
        {
            "id_perfil": 3,
            "perfil": "Docente"
        }
    ]

    nucleos = Nucleos.objects.values(
        "id_nucleo",
        "municipio"
    )

    return JsonResponse({
        "perfiles": perfiles,
        "nucleos": list(nucleos)
    })

def nucleos_disp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        perfil = data.get("perfil")  # "Control de Estudio", "Docente", etc.

        nucleos = Nucleos.objects.all()

        if perfil == "Control de Estudio":
            nucleos_ocupados = ControlEstudio.objects.values_list(
                "nucleo_id",
                flat=True
            )

            nucleos = nucleos.exclude(
                id_nucleo__in=nucleos_ocupados
            )

        return JsonResponse({
            "nucleos": list(
                nucleos.values(
                    "id_nucleo",
                    "municipio"
                )
            )
        })

def pnfs_disp(request):
    if request.method == "POST":
        data = json.loads(request.body)

        nucleo_id = data.get("id_nucleo")
        perfil = data.get("perfil")

        pnfs = PNFNucleo.objects.filter(
            id_nucleo_id=nucleo_id
        ).select_related("id_pnf")

        if perfil == "Coordinador PNF":

            pnfs_ocupados = CoordinadorPNF.objects.filter(
                nucleo_id=nucleo_id
            ).values_list(
                "pnf_id",
                flat=True
            )

            pnfs = pnfs.exclude(
                id_pnf_id__in=pnfs_ocupados
            )

        resultado = [
            {
                "id_pnf": item.id_pnf.id_pnf,
                "pnf": item.id_pnf.pnf
            }
            for item in pnfs
        ]

        return JsonResponse({
            "pnfs": resultado
        })

def pre_reg_personal(request):
    if request.method == "POST":
        nombres = request.POST.get("nombres")
        apellidos = request.POST.get("apellidos")
        nacionalidad = request.POST.get("nacionalidad")
        num_cedula = request.POST.get("cedula_identidad")
        nombre_correo = request.POST.get("correo_electronico")
        dominio = request.POST.get("dominio")
        prefijo = request.POST.get("prefijo")
        num_telefono = request.POST.get("telefono")

        perfiles_asignados = request.POST.getlist("perfil")

        nucleos_control = request.POST.getlist("nucleo_encargado_control_estudios")
        nucleos_coordinador = request.POST.getlist("nucleo_coordinador_pnf")
        nucleos_docente = request.POST.getlist("nucleo_docente")

        pnfs_coordinador = request.POST.getlist("pnf_coordinador_pnf")
        pnfs_docente = request.POST.getlist("pnf_docente")

        campos = [
            (nombres, "Nombres", "Por favor, ingresar los nombres del usuario."),
            (apellidos, "Apellidos", "Por favor, ingresar los apellidos del usuario."),
            (nacionalidad, "Nacionalidad", "Por favor, selecciona la nacionalidad."),
            (num_cedula, "Números de la Cedula Identidad", "Por favor, ingresa los números de la cedula de identidad."),
            (nombre_correo, "Nombres del Correo Electrónico", "Por favor, ingresa el nombre del correo electrónico."),
            (dominio, "Dominio del Correo Electrónico", "Por favor, selecciona el dominio del correo electronico."),
            (prefijo, "Perfijo Telefonico", "Por favor, selecciona el prefijo telefonico."),
            (num_telefono, "Números Telefonicos", "Por favor, ingresa los números telefonico."),
        ]

        for valor, campo, mensaje in campos:
            if not valor:
                return JsonResponse({
                    "estado": "fallo",
                    "title": campo,
                    "descripcion": mensaje,
                    "icon": "warning"
                })
            
        for perfil_id in perfiles_asignados:

            perfil = PERFILES.get(perfil_id)

            if perfil == "Control de Estudio":

                if not nucleos_control:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "Vacío",
                        "descripcion": "Debe seleccionar al menos un núcleo para el perfil Control de Estudio.",
                        "icon": "warning"
                    })


            elif perfil == "Coordinador PNF":

                if not nucleos_coordinador:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "Vacío",
                        "descripcion": "Debe seleccionar al menos un núcleo para el perfil Coordinador PNF.",
                        "icon": "warning"
                    })

                if not pnfs_coordinador:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "Vacío",
                        "descripcion": "Debe seleccionar al menos un PNF para el perfil Coordinador PNF.",
                        "icon": "warning"
                    })

            elif perfil == "Docente":

                if not nucleos_docente:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "Vacío",
                        "descripcion": "Debe seleccionar al menos un núcleo para el perfil Docente.",
                        "icon": "warning"
                    })

                if not pnfs_docente:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "Vacío",
                        "descripcion": "Debe seleccionar al menos un PNF para el perfil Docente.",
                        "icon": "warning"
                    })

        cedula_identidad = f"{nacionalidad}-{num_cedula}"
        correo_principal = f"{nombre_correo}{dominio}"
        telefono_principal = f"{prefijo}{num_telefono}"

        with transaction.atomic():
            usuario = Usuario.objects.create(nombres=nombres, apellidos=apellidos, cedula_identidad=cedula_identidad)

            Contacto.objects.create(correo_electronico=correo_principal, telefono_personal=telefono_principal, id_usuario=usuario)

            # Control de Estudio
            if nucleos_control:
                for nucleo_id in nucleos_control:
                    ControlEstudio.objects.create(
                        usuario=usuario,
                        nucleo_id=nucleo_id
                    )
            # Coordinador PNF
            if nucleos_coordinador:
                for nucleo_id, pnf_id in zip(nucleos_coordinador, pnfs_coordinador):

                    if PNFNucleo.objects.filter(
                        id_nucleo_id=nucleo_id,
                        id_pnf_id=pnf_id
                    ).exists():

                        CoordinadorPNF.objects.create(
                            usuario=usuario,
                            nucleo_id=nucleo_id,
                            pnf_id=pnf_id
                        )

            # Docente
            if nucleos_docente:
                for nucleo_id, pnf_id in zip(nucleos_docente, pnfs_docente):

                    if PNFNucleo.objects.filter(
                        id_nucleo_id=nucleo_id,
                        id_pnf_id=pnf_id
                    ).exists():

                        Docente.objects.create(
                            usuario=usuario,
                            nucleo_id=nucleo_id,
                            pnf_id=pnf_id
                        )

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Exito",
            "descripcion": "Los datos del usuario se registraron exitosamente."
        })
    
    return render(request, 'Director_General/pre_registro_personal.html')

