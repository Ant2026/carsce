from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction

from inicio_sesion.models import Usuario, Contacto, PNFNucleo, DirectorGeneral, Docente, CoordinadorPNF, ControlEstudio

import json

PERFILES = {
    "1": "Coordinador PNF",
    "2": "Control de Estudio",
    "3": "Docente"
}

def datos_perfiles(request):
    director = DirectorGeneral.objects.select_related("nucleo").get(usuario__cedula_identidad=request.session.get("cedula_usuario"))

    nucleo_director = director.nucleo

    perfiles = [
        {
            "id_perfil": 1,
            "perfil": "Coordinador PNF"
        },
        {
            "id_perfil": 3,
            "perfil": "Docente"
        }
    ]

    # Verificar si el núcleo ya tiene Control de Estudio
    existe_control = ControlEstudio.objects.filter(
        nucleo=nucleo_director
    ).exists()
    if not existe_control:
        perfiles.insert(
            1,
            {
                "id_perfil": 2,
                "perfil": "Control de Estudio"
            }
        )

    return JsonResponse({
        "perfiles": perfiles
    })

def pnfs_disp(request):
    if request.method == "POST":
        data = json.loads(request.body)

        perfil_id = int(data.get("id_perfil"))

        director = DirectorGeneral.objects.select_related(
            "nucleo"
        ).get(
            usuario__cedula_identidad=request.session.get("cedula_usuario")
        )

        nucleo = director.nucleo

        pnfs = PNFNucleo.objects.filter(
            id_nucleo=nucleo
        ).select_related("id_pnf")

        # Coordinador PNF (id_perfil = 1)
        if perfil_id == 1:

            pnfs_ocupados = CoordinadorPNF.objects.filter(
                nucleo=nucleo
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

        pnfs_coordinador = request.POST.getlist("pnf_coordinador_pnf")
        pnfs_docente = request.POST.getlist("pnf_docente")

        # Obtener núcleo del Director General
        director = DirectorGeneral.objects.select_related(
            "usuario",
            "nucleo"
        ).get(
            usuario__cedula_identidad=request.session.get("cedula_usuario")
        )

        nucleo_director = director.nucleo

        campos = [
            (nombres, "Nombres", "Por favor, ingresar los nombres del usuario."),
            (apellidos, "Apellidos", "Por favor, ingresar los apellidos del usuario."),
            (nacionalidad, "Nacionalidad", "Por favor, selecciona la nacionalidad."),
            (num_cedula, "Cédula", "Por favor, ingresa la cédula."),
            (nombre_correo, "Correo", "Por favor, ingresa el correo."),
            (dominio, "Dominio", "Por favor, selecciona el dominio."),
            (prefijo, "Prefijo", "Por favor, selecciona el prefijo."),
            (num_telefono, "Teléfono", "Por favor, ingresa el teléfono."),
        ]

        for valor, campo, mensaje in campos:
            if not valor:
                return JsonResponse({
                    "estado": "fallo",
                    "title": campo,
                    "descripcion": mensaje,
                    "icon": "warning"
                })

        perfiles_asignados = [
            perfil for perfil in request.POST.getlist("perfil")
            if perfil.strip()
        ]

        pnfs_coordinador = [
            pnf for pnf in request.POST.getlist("pnf_coordinador_pnf")
            if pnf.strip()
        ]

        pnfs_docente = [
            pnf for pnf in request.POST.getlist("pnf_docente")
            if pnf.strip()
        ]

        # Validar que exista al menos un perfil
        if not perfiles_asignados:
            return JsonResponse({
                "estado": "fallo",
                "title": "Perfil vacío",
                "descripcion": "Debe seleccionar al menos un perfil para el usuario.",
                "icon": "warning"
            })


        # Validar los PNF según el perfil seleccionado
        for perfil_id in perfiles_asignados:

            perfil = PERFILES.get(perfil_id)

            if perfil == "Coordinador PNF":

                if not pnfs_coordinador:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "PNF vacío",
                        "descripcion": "Debe seleccionar al menos un PNF para el perfil Coordinador PNF.",
                        "icon": "warning"
                    })

            elif perfil == "Docente":

                if not pnfs_docente:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "PNF vacío",
                        "descripcion": "Debe seleccionar al menos un PNF para el perfil Docente.",
                        "icon": "warning"
                    })
                        

        cedula_identidad = f"{nacionalidad}-{num_cedula}"
        correo_principal = f"{nombre_correo}{dominio}"
        telefono_principal = f"{prefijo}{num_telefono}"

        with transaction.atomic():
            usuario = Usuario.objects.create(
                nombres=nombres,
                apellidos=apellidos,
                cedula_identidad=cedula_identidad
            )

            Contacto.objects.create(
                correo_electronico=correo_principal,
                telefono_personal=telefono_principal,
                id_usuario=usuario
            )

            for perfil_id in perfiles_asignados:
                perfil = PERFILES.get(perfil_id)

                # Control de Estudio
                if perfil == "Control de Estudio":
                    ControlEstudio.objects.create(
                        usuario=usuario,
                        nucleo=nucleo_director
                    )

                # Coordinador PNF
                elif perfil == "Coordinador PNF":
                    for pnf_id in pnfs_coordinador:
                        if PNFNucleo.objects.filter(
                            id_nucleo=nucleo_director,
                            id_pnf_id=pnf_id
                        ).exists():

                            CoordinadorPNF.objects.create(
                                usuario=usuario,
                                nucleo=nucleo_director,
                                pnf_id=pnf_id
                            )

                # Docente
                elif perfil == "Docente":
                    for pnf_id in pnfs_docente:
                        if PNFNucleo.objects.filter(
                            id_nucleo=nucleo_director,
                            id_pnf_id=pnf_id
                        ).exists():
                            Docente.objects.create(
                                usuario=usuario,
                                nucleo=nucleo_director,
                                pnf_id=pnf_id
                            )

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Éxito",
            "descripcion": "Los datos del usuario se registraron exitosamente."
        })

    return render(request, "Director_General/pre_registro_personal.html")

