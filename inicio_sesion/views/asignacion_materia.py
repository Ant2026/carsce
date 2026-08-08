from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone

from inicio_sesion.models import Usuario, Materia, MateriaAsignada, DocenteAsignadoMateria, CoordinadorPNF, Docente, Bitacora, Materia, SeccionAcademica
    
def docs_reg(request):
    try:
        coordinador = CoordinadorPNF.objects.get(usuario__cedula_identidad=request.session.get("cedula_usuario"))
    except CoordinadorPNF.DoesNotExist:
        return JsonResponse({
            "estado": "fallo",
            "title": "Error",
            "icon": "error",
            "descripcion": "No cuenta con el rol de Coordinador de PNF.",
            "usuarios": []
        })

    docentes = Docente.objects.filter(nucleo=coordinador.nucleo,pnf=coordinador.pnf).select_related("usuario")

    usuarios = [
        {
            "id_usuario": docente.usuario.id_usuario,
            "nombre": str(docente.usuario)
        }
        for docente in docentes
    ]

    return JsonResponse({
        "estado": "exito",
        "usuarios": usuarios
    })

def mats_reg(request):
    seccion_id = request.POST.get("seccion")

    try:
        coordinador = CoordinadorPNF.objects.get(usuario__cedula_identidad=request.session.get("cedula_usuario"))
    except CoordinadorPNF.DoesNotExist:
        return JsonResponse({
            "estado": "fallo",
            "title": "Error",
            "icon": "error",
            "descripcion": "No cuenta con el rol de Coordinador de PNF.",
            "materias": []
        })

    materias = []

    for materia in Materia.objects.filter(
        id_pnf=coordinador.pnf
    ).order_by(
        "trayecto",
        "nombre"
    ):

        estado = "VERDE"

        # Solo calcular el estado cuando exista una sección
        if seccion_id:

            materia_asignada = MateriaAsignada.objects.filter(
                materia=materia,
                seccion_id=seccion_id,
                activo=True
            ).first()

            if materia_asignada:

                roles = DocenteAsignadoMateria.objects.filter(
                    materia_asignada=materia_asignada
                ).values_list(
                    "rol",
                    flat=True
                )

                tiene_principal = "PRINCIPAL" in roles
                tiene_secundario = "SECUNDARIO" in roles

                if tiene_principal and tiene_secundario:
                    estado = "ROJO"

                elif tiene_principal:
                    estado = "AMARILLO"

        materias.append({
            "id_materia": materia.id_materia,
            "nombre": materia.nombre,
            "codigo": materia.codigo,
            "trayecto": materia.trayecto,
            "recuperacion": materia.recuperacion,
            "htea": materia.htea,
            "htei": materia.htei,
            "estado": estado
        })

    return JsonResponse({
        "estado": "exito",
        "materias": materias
    })

def mat_asig(request):
    materias = MateriaAsignada.objects.filter(activo=True).select_related("materia", "seccion")

    if request.method == "POST":
        trayecto = request.POST.get("trayecto", "").strip()
        nombre_materia = request.POST.get("materia", "").strip()

        if trayecto:
            materias = materias.filter(materia__trayecto=trayecto)

        if nombre_materia:
            materias = materias.filter(materia__nombre__icontains=nombre_materia)

    datos = []
    for asignacion in materias:
        materia = asignacion.materia

        datos.append({
            "id_materia_asignada": asignacion.id_materia_asignada,
            "id_materia": materia.id_materia,
            "nombre": materia.nombre,
            "codigo": materia.codigo,
            "trayecto": materia.trayecto,
            "seccion": asignacion.seccion.nombre,
            "htea": materia.htea,
            "htei": materia.htei,
            "thte": materia.thte,
            "uc": materia.uc,
        })

    return JsonResponse({
        "materias": datos
    })

def busc_mat(request):
    id_asignacion = request.POST.get("id_asignacion")

    if not id_asignacion:
        return JsonResponse({
            "estado": "fallo",
            "title": "Error",
            "icon": "error",
            "descripcion": "No se recibió el ID de la asignación."
        })

    try:
        asignacion = (
            MateriaAsignada.objects
            .select_related(
                "materia",
                "materia__id_pnf",
                "seccion"
            )
            .prefetch_related(
                "docentes__docente__usuario"
            )
            .get(
                id_materia_asignada=id_asignacion,
                activo=True
            )
        )
    except MateriaAsignada.DoesNotExist:
        return JsonResponse({
            "estado": "fallo",
            "title": "Error",
            "icon": "error",
            "descripcion": "No se encontró la materia asignada."
        })

    materia = asignacion.materia
    
    docentes = [] # Docentes asignados
    for asignacion_docente in asignacion.docentes.all():
        docente = asignacion_docente.docente
        usuario = docente.usuario

        docentes.append({"id_asignacion_docente": asignacion_docente.pk,
            "id_docente": docente.id_docente,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "nombre_completo":  f"{usuario.nombres} {usuario.apellidos}",
            "cedula": usuario.cedula_identidad,
            "rol": asignacion_docente.rol,
            "activo": asignacion_docente.activo,
            "fecha_asignacion": asignacion_docente.fecha_asignacion,
            "fecha_suspension": asignacion_docente.fecha_suspension,
        })

    datos = {
        # MateriaAsignada
        "id_materia_asignada": asignacion.id_materia_asignada,
        "activo": asignacion.activo,
        "fecha_asignacion": asignacion.fecha_asignacion,
        "fecha_suspension": asignacion.fecha_suspension,

        # Materia
        "id_materia": materia.id_materia,
        "nombre": materia.nombre,
        "codigo": materia.codigo,
        "trayecto": materia.trayecto,
        "recuperacion": materia.recuperacion,
        "htea": materia.htea,
        "htei": materia.htei,
        "thte": materia.thte,
        "uc": materia.uc,

        # PNF
        "pnf": materia.id_pnf.pnf,
        "id_pnf": materia.id_pnf.id_pnf,

        # Sección
        "id_seccion": asignacion.seccion.pk,
        "seccion": asignacion.seccion.nombre,

        # Docentes
        "docentes": docentes
    }

    return JsonResponse({
        "estado": "exito",
        "materia": datos
    })

def asig_mat_doc(request):
    if request.method == "POST":
        docente_id = request.POST.get("docente")
        rol_docente = request.POST.get("rol_docente")
        seccion_id = request.POST.get("seccion")
        materias_ids = request.POST.getlist("materias[]")

        controles = [
            (docente_id, "Docente", "Debe seleccionar un docente."),
            (rol_docente, "Rol del Docente", "Debe seleccionar el rol del docente."),
            (seccion_id, "Sección Académica", "Debe seleccionar la sección académica."),
            (materias_ids, "Materias Académicas", "Debe seleccionar al menos una materia."),
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
            usuario = Usuario.objects.get(pk=docente_id)
        except Usuario.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "El usuario no se encuentra registrado."
            })

        try:
            docente = Docente.objects.get(usuario=usuario)
        except Docente.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "No se encontró el perfil de docente."
            })

        try:
            seccion = SeccionAcademica.objects.get(pk=seccion_id)
        except SeccionAcademica.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "No se encontró la sección académica."
            })

        if rol_docente not in ["PRINCIPAL", "SECUNDARIO"]:
            return JsonResponse({
                "estado": "fallo",
                "title": "Rol inválido",
                "icon": "warning",
                "descripcion": "El rol del docente seleccionado no es válido."
            })

        materias = list(
            Materia.objects.filter(
                pk__in=materias_ids
            )
        )

        if len(materias) != len(set(materias_ids)):
            return JsonResponse({
                "estado": "fallo",
                "title": "Materia inválida",
                "icon": "warning",
                "descripcion": "Una o más materias seleccionadas no existen."
            })

        with transaction.atomic():

            for materia in materias:

                # ---------------------------------------------------------
                # BUSCAR LA MATERIA ASIGNADA A LA SECCIÓN
                # ---------------------------------------------------------

                asignacion = (
                    MateriaAsignada.objects
                    .filter(
                        materia=materia,
                        seccion=seccion,
                        activo=True
                    )
                    .first()
                )


                # ---------------------------------------------------------
                # SI NO EXISTE, CREAR LA ASIGNACIÓN
                # ---------------------------------------------------------

                if not asignacion:

                    asignacion = MateriaAsignada.objects.create(
                        materia=materia,
                        seccion=seccion,
                        activo=True
                    )


                # ---------------------------------------------------------
                # VALIDAR SI EL MISMO DOCENTE YA ESTÁ ASIGNADO
                # ---------------------------------------------------------

                docente_existente = (
                    DocenteAsignadoMateria.objects
                    .filter(
                        materia_asignada=asignacion,
                        docente=docente,
                        activo=True
                    )
                    .first()
                )


                if docente_existente:

                    nombre_rol_existente = (
                        "Docente Principal"
                        if docente_existente.rol == "PRINCIPAL"
                        else "Docente Secundario"
                    )

                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "warning",
                        "title": "Docente ya asignado",
                        "descripcion": (
                            f"El docente "
                            f"'{docente.usuario.nombres} "
                            f"{docente.usuario.apellidos}' "
                            f"ya está asignado a la materia "
                            f"'{materia.nombre}' "
                            f"como {nombre_rol_existente}."
                        )
                    })


                # ---------------------------------------------------------
                # VALIDAR SI YA EXISTE EL ROL
                # ---------------------------------------------------------

                docente_rol_existente = (
                    DocenteAsignadoMateria.objects
                    .filter(
                        materia_asignada=asignacion,
                        rol=rol_docente,
                        activo=True
                    )
                    .first()
                )


                if docente_rol_existente:

                    nombre_rol = (
                        "Docente Principal"
                        if rol_docente == "PRINCIPAL"
                        else "Docente Secundario"
                    )

                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "warning",
                        "title": "Rol ya asignado",
                        "descripcion": (
                            f"La materia '{materia.nombre}' "
                            f"ya tiene un {nombre_rol.lower()} "
                            f"asignado en la sección "
                            f"'{seccion.nombre}'."
                        )
                    })


                # ---------------------------------------------------------
                # CREAR ASIGNACIÓN DEL DOCENTE
                # ---------------------------------------------------------

                activo_docente = (
                    rol_docente == "PRINCIPAL"
                )


                DocenteAsignadoMateria.objects.create(
                    materia_asignada=asignacion,
                    docente=docente,
                    rol=rol_docente,
                    activo=activo_docente
                )


                # ---------------------------------------------------------
                # BITÁCORA
                # ---------------------------------------------------------

                Bitacora.objects.create(
                    nombre_usuario=request.session.get(
                        "usuario_nombre"
                    ),
                    fecha_hora=timezone.now(),
                    accion=(
                        f"Asignó la materia '{materia.nombre}' "
                        f"al docente "
                        f"{docente.usuario.nombres} "
                        f"{docente.usuario.apellidos} "
                        f"como "
                        f"{'Docente Principal' if rol_docente == 'PRINCIPAL' else 'Docente Secundario'}."
                    )
                )
        return JsonResponse({
            "estado": "exito",
            "title": "Éxito",
            "icon": "success",
            "descripcion": "Se asignaron las materias correctamente."
        })

    return render(request, "Coordinador_PNF/asignacion_materia/registrar_asignaciones.html")

def act_asig(request):
    if request.method == "POST":
        materia_asignada_id = request.POST.get("materia_asignada")
        estado_principal = request.POST.get("estado_principal")
        estado_secundario = request.POST.get("estado_secundario")
        estado_materia = request.POST.get("estado_materia")

        # VALIDAR ASIGNACIÓN
        if not materia_asignada_id:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Asignación",
                "descripcion": (
                    "No se especificó la asignación "
                    "de la materia."
                )
            })

        # VALIDAR ESTADO PRINCIPAL
        if estado_principal not in ["ACTIVO", "INACTIVO"]:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Docente principal",
                "descripcion": (
                    "El estado del docente principal "
                    "no es válido."
                )
            })

        # VALIDAR ESTADO DE LA MATERIA
        if estado_materia not in ["ACTIVA", "SUSPENDIDA"]:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Materia",
                "descripcion": (
                    "El estado de la materia "
                    "no es válido."
                )
            })

        # BUSCAR ASIGNACIÓN
        try:
            materia_asignada = (MateriaAsignada.objects.select_related("materia","seccion").get(pk=materia_asignada_id))
        except MateriaAsignada.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Asignación no encontrada",
                "descripcion": (
                    "No se encontró la asignación "
                    "de la materia."
                )
            })

        # OBTENER DOCENTES
        docentes = materia_asignada.docentes.all()

        principal = (docentes.filter(rol="PRINCIPAL").first())

        secundario = (docentes.filter(rol="SECUNDARIO").first())

        # VALIDAR PRINCIPAL
        if not principal:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Docente principal",
                "descripcion": (
                    "La asignación no tiene "
                    "un docente principal."
                )
            })

        # SI EXISTE DOCENTE SECUNDARIO
        if secundario:
            # VALIDAR ESTADO DEL SECUNDARIO
            if estado_secundario not in ["ACTIVO", "INACTIVO"]:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": "Docente secundario",
                    "descripcion": (
                        "El estado del docente secundario "
                        "no es válido."
                    )
                })

            # MATERIA ACTIVA
            if estado_materia == "ACTIVA":
                # Principal y secundario deben ser opuestos.
                if estado_principal == estado_secundario:
                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "warning",
                        "title": "Estado de los docentes",
                        "descripcion": (
                            "El docente principal y el docente "
                            "secundario deben tener estados opuestos."
                        )
                    })

        # SI NO EXISTE DOCENTE SECUNDARIO
        else:
            # MATERIA ACTIVA
            if (estado_materia == "ACTIVA" and estado_principal == "INACTIVO"):
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": "Docente secundario",
                    "descripcion": (
                        "No se puede desactivar al docente "
                        "principal porque la materia no tiene "
                        "un docente secundario asignado."
                    )
                })

        # ACTUALIZAR
        with transaction.atomic():
            # ESTADO DE LA MATERIA
            if estado_materia == "SUSPENDIDA":
                materia_asignada.activo = False
                materia_asignada.fecha_suspension = (timezone.now())
            else:
                materia_asignada.activo = True
                materia_asignada.fecha_suspension = None

            materia_asignada.save(update_fields=["activo", "fecha_suspension"])

            # ACTUALIZAR PRINCIPAL
            principal.activo = (
                estado_principal == "ACTIVO"
                and estado_materia == "ACTIVA"
            )

            if principal.activo:
                principal.fecha_suspension = None
            else:
                principal.fecha_suspension = (timezone.now())

            principal.save(update_fields=["activo", "fecha_suspension"])

            # ACTUALIZAR SECUNDARIO
            if secundario:
                secundario.activo = (estado_secundario == "ACTIVO" and estado_materia == "ACTIVA")

                if secundario.activo:
                    secundario.fecha_suspension = None
                else:
                    secundario.fecha_suspension = (timezone.now())

                secundario.save(update_fields=["activo", "fecha_suspension"])

            # BITÁCORA
            Bitacora.objects.create(
                nombre_usuario=request.session.get("usuario_nombre"),
                fecha_hora=timezone.now(),
                accion=(
                    f"Actualizó la asignación de la materia "
                    f"'{materia_asignada.materia.nombre}' "
                    f"de la sección "
                    f"'{materia_asignada.seccion.nombre}'."
                )
            )

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Éxito",
            "descripcion": (
                "La asignación se actualizó correctamente."
            )
        })

    return render(request, "Coordinador_PNF/asignacion_materia/visualizar_asignaciones.html")

def mats_desact(request):
    materias = (MateriaAsignada.objects.filter(activo=False).select_related("materia", "seccion").prefetch_related("docentes__docente__usuario"))

    if request.method == "POST":
        trayecto = request.POST.get("trayecto", "").strip()
        nombre_materia = request.POST.get("materia", "").strip()

        if trayecto:
            materias = materias.filter(materia__trayecto=trayecto)

        if nombre_materia:
            materias = materias.filter(materia__nombre__icontains=nombre_materia)


    datos = []
    for asignacion in materias:
        materia = asignacion.materia
        
        docente_principal = (asignacion.docentes.filter(rol="PRINCIPAL").first())

        # DOCENTE SECUNDARIO
        docente_secundario = (asignacion.docentes.filter(rol="SECUNDARIO").first())

        # DATOS DE LA ASIGNACIÓN
        datos.append({
            # MATERIA ASIGNADA
            "id_materia_asignada": asignacion.id_materia_asignada,
            "activo": asignacion.activo,
            "fecha_asignacion": asignacion.fecha_asignacion,
            "fecha_suspension": asignacion.fecha_suspension,

            # MATERIA
            "id_materia": materia.id_materia,
            "nombre": materia.nombre,
            "codigo": materia.codigo,
            "trayecto": materia.trayecto,
            "htea": materia.htea,
            "htei": materia.htei,
            "thte": materia.thte,
            "uc": materia.uc,
            
            # SECCIÓN
            "id_seccion": asignacion.seccion.id_seccion,
            "seccion": asignacion.seccion.nombre,
            
            # DOCENTE PRINCIPAL
            "docente_principal": ({
                    "id_asignacion_docente": docente_principal.id,
                    "id_docente": docente_principal.docente.id_docente,
                    "nombres": docente_principal.docente.usuario.nombres,
                    "apellidos": docente_principal.docente.usuario.apellidos,
                    "nombre_completo":(
                            docente_principal.docente.usuario.nombres
                            + " "
                            + docente_principal.docente.usuario.apellidos
                        ),
                    "cedula": docente_principal.docente.usuario.cedula_identidad,
                    "rol": docente_principal.rol,
                    "activo": docente_principal.activo,
                    "fecha_asignacion": docente_principal.fecha_asignacion,
                    "fecha_suspension": docente_principal.fecha_suspension,
                }
                if docente_principal
                else None
            ),

            # DOCENTE SECUNDARIO / SUPLENTE
            "docente_secundario": ({
                    "id_asignacion_docente": docente_secundario.id,
                    "id_docente": docente_secundario.docente.id_docente,
                    "nombres": docente_secundario.docente.usuario.nombres,
                    "apellidos": docente_secundario.docente.usuario.apellidos,
                    "nombre_completo":(
                            docente_secundario.docente.usuario.nombres
                            + " "
                            + docente_secundario.docente.usuario.apellidos
                        ),
                    "cedula": docente_secundario.docente.usuario.cedula_identidad,
                    "rol": docente_secundario.rol,
                    "activo": docente_secundario.activo,
                    "fecha_asignacion": docente_secundario.fecha_asignacion,
                    "fecha_suspension": docente_secundario.fecha_suspension,
                }
                if docente_secundario
                else None
            ),
        })

    return JsonResponse({
        "materias": datos
    })

def asig_desact(request):
    if request.method == "POST":
        materia_asignada_id = request.POST.get("materia_asignada")
        if not materia_asignada_id:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Asignación",
                "descripcion": (
                    "No se especificó la asignación "
                    "que se desea reactivar."
                )
            })

        # BUSCAR ASIGNACIÓN SUSPENDIDA
        try:
            materia_asignada = (
                MateriaAsignada.objects.select_related(
                "materia",
                "seccion"
            ).get(
                id_materia_asignada=materia_asignada_id,
                activo=False
            ))
        except MateriaAsignada.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Asignación no encontrada",
                "descripcion": (
                    "No se encontró una asignación "
                    "suspendida con el ID indicado."
                )
            })

        # COMPROBAR SI YA EXISTE OTRA ASIGNACIÓN ACTIVA
        asignacion_existente = (
            MateriaAsignada.objects
            .filter(
                materia=materia_asignada.materia,
                seccion=materia_asignada.seccion,
                activo=True
            )
            .exclude(
                pk=materia_asignada.pk
            )
            .first()
        )
        if asignacion_existente:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Materia ya asignada",
                "descripcion": (
                    f"La materia "
                    f"'{materia_asignada.materia.nombre}' "
                    f"ya se encuentra activa en la sección "
                    f"'{materia_asignada.seccion.nombre}'. "
                    f"No se puede reactivar esta asignación."
                )
            })
        # REACTIVAR
        with transaction.atomic():
            # REACTIVAR MATERIA
            materia_asignada.activo = True
            materia_asignada.fecha_suspension = None

            materia_asignada.save(update_fields=["activo", "fecha_suspension"])

            # OBTENER DOCENTES
            docentes = (
                materia_asignada.docentes
                .select_related(
                    "docente__usuario"
                )
                .all()
            )

            principal = docentes.filter(rol="PRINCIPAL").first()
            secundario = docentes.filter(rol="SECUNDARIO").first()
            
            # REACTIVAR PRINCIPAL
            if principal:
                principal.activo = True
                principal.fecha_suspension = None
                principal.save(update_fields=["activo", "fecha_suspension"])

            # SUPLENTE INACTIVO
            if secundario:
                secundario.activo = False
                secundario.fecha_suspension = timezone.now()
                secundario.save(update_fields=["activo", "fecha_suspension"])

            # BITÁCORA
            Bitacora.objects.create(
                nombre_usuario=request.session.get(
                    "usuario_nombre"
                ),
                fecha_hora=timezone.now(),
                accion=(
                    f"Reactivó la materia "
                    f"'{materia_asignada.materia.nombre}' "
                    f"de la sección "
                    f"'{materia_asignada.seccion.nombre}'."
                )
            )

        # RESPUESTA
        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Asignación reactivada",
            "descripcion": (
                f"La materia "
                f"'{materia_asignada.materia.nombre}' "
                f"fue reactivada correctamente."
            )
        })

    return render(request, "Coordinador_PNF/asignacion_materia/reactivar_asignaciones.html")
