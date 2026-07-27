from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction

from inicio_sesion.models import Usuario, Perfiles, Nucleos, Contacto, PNFNucleo, UsuarioAsignacion

import json

# Verificado
def datos_registro(request):
    # Obtiene todos los perfiles excepto el perfil estudiante y director general
    perfiles = Perfiles.objects.exclude(perfil__in=["Estudiante", "Director General"])

    # Obtiene todos los nucleos registrados
    nucleos = Nucleos.objects.all()

    # Envia las dos lista con los perfiles filtrados y todos los nucleos
    return JsonResponse({
        "perfiles": list(
            perfiles.values(
                "id_pefil",
                "perfil"
            )
        ),
        "nucleos": list(
            nucleos.values(
                "id_nucleo",
                "municipio"
            )
        )
    })

# Verificado
def validar_nucleos(request):
    if request.method == "POST": # Recibe la petición POST desde el frontend
        data = json.loads(request.body) # Convierte los datos obtenidos en un diccionario

        perfil_id = data.get("id_perfil") # Obtiene solo el id del perfil

        perfil = Perfiles.objects.get(pk=perfil_id) # Lo busca en la base de datos

        # Obtiene todos los nucleos registrados
        nucleos = Nucleos.objects.all()

        # Solo va a validar el perfil de Encargado de control de estudio
        if perfil.perfil == "Encargado de Control de Estudio":

            # Obtiene todos los núcleos asignados
            # Con el parametro flat cambia la lista de id que viene en tuplas a listas
            nucleos_ocupados = UsuarioAsignacion.objects.filter(
                id_perfil__perfil="Encargado de Control de Estudio"
            ).values_list(
                "id_nucleo_id",
                flat=True
            )

            # Excluye los registrados, porque el operador _in espera una secuencia de valores
            nucleos = nucleos.exclude(
                id_nucleo__in=nucleos_ocupados
            )

        # Envia a la vista la lista de los nucleos que aun no han sido asignado
        resultado = list(
            nucleos.values(
                "id_nucleo",
                "municipio"
            )
        )

        # Envia las listas filtradas
        return JsonResponse({"nucleos": resultado})

# Verificado
def pnfs_nucleos(request):
    if request.method == "POST": # Solo acepta peticiones POST
        data = json.loads(request.body) # Convierte la petición en un diccionario

        nucleo_id = data.get("id_nucleo") # Obtiene el núcleo seleccionado 
        perfil_id = data.get("id_perfil") # Obtiene el perfil seleccionado

        perfil = Perfiles.objects.get(pk=perfil_id) # Busca el perfil a validar

        # Busca los pnfs perteneciente al nucleo seleccionado, a través de la tabla intermedia
        pnfs = PNFNucleo.objects.filter(
            id_nucleo_id=nucleo_id
        ).select_related("id_pnf") # Aprovecha la petición para buscar los datos de los pnfs

        # Solo para Coordinador de PNF se excluyen los PNF ya asignados
        if perfil.perfil == "Coordinador de PNF":

            # Busca los pnfs ya registrados, especificando el perfil del Coordinador
            # Utiliza el operador flat para convertir la lista de tuplas a una lista
            # Con valores continuo
            pnfs_ocupados = UsuarioAsignacion.objects.filter(
                id_perfil=perfil,
                id_nucleo_id=nucleo_id
            ).values_list(
                "id_pnf_id",
                flat=True
            )

            # Aquí excluye los registrados
            pnfs = pnfs.exclude(id_pnf_id__in=pnfs_ocupados)

        # Convierte los datos a una lista de diccionario
        resultado = []
        for item in pnfs:
            resultado.append({
                "id_pnf": item.id_pnf.id_pnf,
                "pnf": item.id_pnf.pnf
            })

        # Obtiene los pnfs filtados
        return JsonResponse({ "pnfs": resultado })

# Verificado
def pre_registro_personal(request):
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
            
        perfiles = Perfiles.objects.filter(pk__in=perfiles_asignados)

        for perfil in perfiles:
            if perfil.perfil == "Encargado de Control de Estudio":
                if not nucleos_control:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "Vacío",
                        "descripcion": "Debe seleccionar al menos un núcleo para el perfil Encargado de Control de Estudio.",
                        "icon": "warning"
                    })

            elif perfil.perfil == "Coordinador de PNF":
                if not nucleos_coordinador:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "Vacío",
                        "descripcion": "Debe seleccionar al menos un núcleo para el perfil Coordinador de PNF.",
                        "icon": "warning"
                    })

                if not pnfs_coordinador:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": "Vacío",
                        "descripcion": "Debe seleccionar al menos un PNF para el perfil Coordinador de PNF.",
                        "icon": "warning"
                    })

            elif perfil.perfil == "Docente":
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

            for perfil_id in perfiles_asignados:
                perfil = Perfiles.objects.get(pk=perfil_id)

                if perfil.perfil == "Encargado de Control de Estudio":
                    for nucleo_id in nucleos_control:
                        UsuarioAsignacion.objects.create(id_usuario=usuario, id_perfil=perfil, id_nucleo_id=nucleo_id)

                elif perfil.perfil == "Coordinador de PNF":
                    for nucleo_id in nucleos_coordinador:
                        for pnf_id in pnfs_coordinador:
                            existe = PNFNucleo.objects.filter(
                                id_nucleo_id=nucleo_id,
                                id_pnf_id=pnf_id
                            ).exists()

                            if existe:
                                UsuarioAsignacion.objects.create(id_usuario=usuario, id_perfil=perfil, id_nucleo_id=nucleo_id, id_pnf_id=pnf_id)

                elif perfil.perfil == "Docente":
                    for nucleo_id in nucleos_docente:
                        for pnf_id in pnfs_docente:
                            existe = PNFNucleo.objects.filter(
                                id_nucleo_id=nucleo_id,
                                id_pnf_id=pnf_id
                            ).exists()

                            if existe:
                                UsuarioAsignacion.objects.create(
                                    id_usuario=usuario,
                                    id_perfil=perfil,
                                    id_nucleo_id=nucleo_id,
                                    id_pnf_id=pnf_id
                                )
        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Exito",
            "descripcion": "Se registró exitosamente."
        })
    
    return render(request, 'Director_General/pre_registro_personal.html')

