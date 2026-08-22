from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone

from inicio_sesion.models import Usuario, Pnf, Materia, ControlEstudio, DirectorGeneral, Estudiante, MateriaAsignada, DocenteAsignadoMateria, CoordinadorPNF, Docente, Bitacora, Materia, SeccionAcademica
    
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

def per_reg_asig(request):
    # DIRECTOR GENERAL DE LA SESIÓN
    director = DirectorGeneral.objects.filter(
        usuario__cedula_identidad=request.session.get("cedula_usuario")
    ).select_related(
        "usuario",
        "nucleo"
    ).first()

    if not director:
        return JsonResponse({
            "personal": [],
            "error": "Director General no encontrado"
        }, status=404)

    nucleo = director.nucleo

    # FILTROS OPCIONALES
    pnf_filtro = request.POST.get("pnf", "").strip()
    perfil_filtro = request.POST.get("perfil", "").strip()

    datos = []

    # DOCENTES
    if not perfil_filtro or perfil_filtro == "Docente":
        docentes = Docente.objects.filter(
            nucleo=nucleo
        ).select_related(
            "usuario",
            "pnf"
        )

        for docente in docentes:

            if Estudiante.objects.filter(
                usuario=docente.usuario,
                nucleo=nucleo
            ).exists():
                continue

            if docente.pnf:
                pnf_asignado = docente.pnf.pnf
                id_pnf = str(docente.pnf.id_pnf)
            else:
                pnf_asignado = "NO CUENTA CON P.N.F"
                id_pnf = ""

            # Filtro por PNF
            if pnf_filtro and id_pnf != pnf_filtro:
                continue

            datos.append({
                "id_usuario": docente.usuario.id_usuario,
                "nombres": docente.usuario.nombres,
                "apellidos": docente.usuario.apellidos,
                "cedula": docente.usuario.cedula_identidad,
                "rol": "Docente",
                "pnf": pnf_asignado,
            })

    # COORDINADORES PNF
    if not perfil_filtro or perfil_filtro == "Coordinador de PNF":
        coordinadores = CoordinadorPNF.objects.filter(
            nucleo=nucleo
        ).select_related(
            "usuario",
            "pnf"
        )

        for coordinador in coordinadores:
            if Estudiante.objects.filter(
                usuario=coordinador.usuario,
                nucleo=nucleo
            ).exists():
                continue

            if coordinador.pnf:
                pnf_asignado = coordinador.pnf.pnf
                id_pnf = str(coordinador.pnf.id_pnf)
            else:
                pnf_asignado = "NO CUENTA CON P.N.F"
                id_pnf = ""

            # Filtro por PNF
            if pnf_filtro and id_pnf != pnf_filtro:
                continue

            datos.append({
                "id_usuario": coordinador.usuario.id_usuario,
                "nombres": coordinador.usuario.nombres,
                "apellidos": coordinador.usuario.apellidos,
                "cedula": coordinador.usuario.cedula_identidad,
                "rol": "Coordinador PNF",
                "pnf": pnf_asignado,
            })

    # CONTROL DE ESTUDIO
    if not perfil_filtro or perfil_filtro == "Encargado de Control de Estudio":
        controles = ControlEstudio.objects.filter(
            nucleo=nucleo
        ).select_related("usuario")

        if not pnf_filtro:
            for control in controles:
                if Estudiante.objects.filter(
                    usuario=control.usuario,
                    nucleo=nucleo
                ).exists():
                    continue

                datos.append({
                    "id_usuario": control.usuario.id_usuario,
                    "nombres": control.usuario.nombres,
                    "apellidos": control.usuario.apellidos,
                    "cedula": control.usuario.cedula_identidad,
                    "rol": "Control de Estudio",
                    "pnf": "NO CUENTA CON P.N.F",
                })

    return JsonResponse({ "personal": datos })

def vis_per_asig(request):
    return render(request, "Director_General/visualizar_personal_registrado.html")

def bus_per_asig(request):

    if request.method == "POST":

        nacionalidad = request.POST.get("nacionalidad_registrar")
        cedula = request.POST.get("cedula_registrar")

        # ==========================================
        # VALIDAR NACIONALIDAD
        # ==========================================

        if not nacionalidad:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Vacio",
                "descripcion": "Por favor, selecciona la nacionalidad."
            })

        # ==========================================
        # VALIDAR CÉDULA
        # ==========================================

        if not cedula:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Vacio",
                "descripcion": "Por favor, ingrese los números de su cedula de identidad."
            })

        cedula_identidad = nacionalidad + "-" + cedula

        # ==========================================
        # BUSCAR USUARIO
        # ==========================================

        usuario = Usuario.objects.filter(
            cedula_identidad=cedula_identidad
        ).first()

        if not usuario:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "No encontrado",
                "descripcion": "No existe un usuario registrado con esa cédula."
            })

        # ==========================================
        # BUSCAR DIRECTOR GENERAL
        # ==========================================

        director = DirectorGeneral.objects.filter(
            usuario__cedula_identidad=request.session.get("cedula_usuario")
        ).select_related(
            "nucleo"
        ).first()

        if not director:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "No se encontró el Director General."
            })

        # Núcleo donde se está realizando la actualización
        nucleo = director.nucleo

        # ==========================================
        # DATOS DEL USUARIO
        # ==========================================

        datos_usuario = {
            "id_usuario": usuario.id_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "cedula": usuario.cedula_identidad,
        }

        perfiles = []

        # Guardaremos solamente los tipos de perfil
        # que ya tiene el usuario.
        perfiles_asignados = set()

        # ==========================================
        # DOCENTE
        # ==========================================

        docentes = Docente.objects.filter(
            usuario=usuario
        ).select_related(
            "nucleo",
            "pnf"
        )

        for docente in docentes:

            perfiles_asignados.add("docente")

            perfiles.append({
                "rol": "Docente",
                "tipo": "docente",
                "id_perfil": docente.id_docente,
                "activo": docente.activo,
                "estado": "ACTIVO" if docente.activo else "INHABILITADO",
                "nucleo": docente.nucleo.municipio,
                "id_pnf": docente.pnf.id_pnf if docente.pnf else None,
                "pnf": docente.pnf.pnf if docente.pnf else "NO CUENTA CON P.N.F",
            })

        # ==========================================
        # COORDINADOR PNF
        # ==========================================

        coordinadores = CoordinadorPNF.objects.filter(
            usuario=usuario
        ).select_related(
            "nucleo",
            "pnf"
        )

        for coordinador in coordinadores:

            perfiles_asignados.add("coordinador_pnf")

            perfiles.append({
                "rol": "Coordinador de PNF",
                "tipo": "coordinador_pnf",
                "id_perfil": coordinador.id_coordinador,
                "activo": coordinador.activo,
                "estado": "ACTIVO" if coordinador.activo else "INHABILITADO",
                "nucleo": coordinador.nucleo.municipio,
                "id_pnf": coordinador.pnf.id_pnf if coordinador.pnf else None,
                "pnf": coordinador.pnf.pnf if coordinador.pnf else "NO CUENTA CON P.N.F",
            })

        # ==========================================
        # CONTROL DE ESTUDIO
        # ==========================================

        controles = ControlEstudio.objects.filter(
            usuario=usuario
        ).select_related(
            "nucleo"
        )

        for control in controles:

            perfiles_asignados.add("control_estudio")

            perfiles.append({
                "rol": "Encargado de Control de Estudio",
                "tipo": "control_estudio",
                "id_perfil": control.id_control,
                "activo": control.activo,
                "estado": "ACTIVO" if control.activo else "INHABILITADO",
                "nucleo": control.nucleo.municipio,
                "id_pnf": None,
                "pnf": "NO CUENTA CON P.N.F",
            })

        # ==========================================
        # PERFILES DISPONIBLES
        # ==========================================

        todos_los_perfiles = [
            {
                "tipo": "docente",
                "rol": "Docente"
            },
            {
                "tipo": "coordinador_pnf",
                "rol": "Coordinador de PNF"
            },
            {
                "tipo": "control_estudio",
                "rol": "Encargado de Control de Estudio"
            }
        ]

        perfiles_disponibles = [
            perfil
            for perfil in todos_los_perfiles
            if perfil["tipo"] not in perfiles_asignados
        ]

        # ==========================================
        # PNF QUE YA TIENEN COORDINADOR ACTIVO
        # ==========================================

        pnfs_coordinador_ocupados = set(
            CoordinadorPNF.objects.filter(
                nucleo=nucleo,
                activo=True
            ).values_list(
                "pnf_id",
                flat=True
            )
        )

        # ==========================================
        # PNF DISPONIBLES PARA COORDINADOR
        # ==========================================

        pnfs_disponibles_coordinador = Pnf.objects.filter(
            pnfnucleo__id_nucleo=nucleo
        ).exclude(
            id_pnf__in=pnfs_coordinador_ocupados
        ).values(
            "id_pnf",
            "pnf",
            "codigo"
        )

        # ==========================================
        # PNF DEL NÚCLEO
        # ==========================================

        pnfs_nucleo = Pnf.objects.filter(
            pnfnucleo__id_nucleo=nucleo
        ).values(
            "id_pnf",
            "pnf",
            "codigo"
        )


        # ==========================================
        # PNF QUE EL USUARIO YA TIENE COMO DOCENTE
        # ==========================================

        pnfs_docente_asignados = set(
            Docente.objects.filter(
                usuario=usuario,
                nucleo=nucleo
            ).values_list(
                "pnf_id",
                flat=True
            )
        )


        # ==========================================
        # PNF DISPONIBLES PARA DOCENTE
        # ==========================================

        pnfs_disponibles_docente = [
            pnf
            for pnf in pnfs_nucleo
            if pnf["id_pnf"] not in pnfs_docente_asignados
        ]


        # ==========================================
        # PNF QUE YA TIENEN COORDINADOR ACTIVO
        # ==========================================

        pnfs_coordinador_ocupados = set(
            CoordinadorPNF.objects.filter(
                nucleo=nucleo,
                activo=True
            ).exclude(
                usuario=usuario
            ).values_list(
                "pnf_id",
                flat=True
            )
        )



        # ==========================================
        # PNF QUE EL USUARIO YA TIENE COMO DOCENTE
        # ==========================================

        pnfs_docente_asignados = set(
            Docente.objects.filter(
                usuario=usuario,
                nucleo=nucleo
            ).values_list(
                "pnf_id",
                flat=True
            )
        )


        # ==========================================
        # PNF DISPONIBLES PARA DOCENTE
        # ==========================================

        pnfs_disponibles_docente = [
            pnf
            for pnf in pnfs_nucleo
            if pnf["id_pnf"] not in pnfs_docente_asignados
        ]


        # ==========================================
        # PNF QUE YA TIENEN COORDINADOR ACTIVO
        # ==========================================

        pnfs_coordinador_ocupados = set(
            CoordinadorPNF.objects.filter(
                nucleo=nucleo,
                activo=True
            ).exclude(
                usuario=usuario
            ).values_list(
                "pnf_id",
                flat=True
            )
        )


        # ==========================================
        # PNF DISPONIBLES PARA COORDINADOR
        # ==========================================

        pnfs_disponibles_coordinador = [
            pnf
            for pnf in pnfs_nucleo
            if pnf["id_pnf"] not in pnfs_coordinador_ocupados
        ]

        return JsonResponse({
            "estado": "exito",
            "usuario": datos_usuario,
            "perfiles": perfiles,
            "perfiles_disponibles": perfiles_disponibles,

            "pnfs_disponibles_docente": pnfs_disponibles_docente,

            "pnfs_disponibles_coordinador": pnfs_disponibles_coordinador
        })

def act_per_asig(request):
    if request.method == "POST":
        cedula_usuario = request.POST.get("cedula_usuario")
        # PNF seleccionados para Docente
        pnfs_docente = request.POST.getlist("pnfs_docente")
        # PNF seleccionados para Coordinador PNF
        pnfs_coordinador = request.POST.getlist("pnfs_coordinador")
        # Control de Estudio
        control_estudio = request.POST.get("control_estudio")

        # DIRECTOR GENERAL
        director = DirectorGeneral.objects.filter(
            usuario__cedula_identidad=request.session.get("cedula_usuario")
        ).select_related("nucleo").first()

        nucleo = director.nucleo

        # BUSCAR USUARIO
        usuario = Usuario.objects.filter(
            cedula_identidad=cedula_usuario
        ).first()

        if not usuario:
            return JsonResponse({
                "estado": "fallo",
                "title": "Usuario no encontrado",
                "descripcion": "No existe un usuario registrado con esa cédula.",
                "icon": "warning"
            })

        try:

            with transaction.atomic():

                # ==========================================
                # DOCENTE
                # ==========================================

                for id_pnf in pnfs_docente:

                    pnf = Pnf.objects.filter(
                        id_pnf=id_pnf
                    ).first()

                    if not pnf:
                        continue

                    docente, creado = Docente.objects.get_or_create(
                        usuario=usuario,
                        nucleo=nucleo,
                        pnf=pnf,
                        defaults={
                            "activo": True
                        }
                    )

                    # Si ya existe pero está inhabilitado,
                    # se vuelve a activar.
                    if not creado and not docente.activo:

                        docente.activo = True

                        docente.save(
                            update_fields=["activo"]
                        )

                # ==========================================
                # COORDINADOR PNF
                # ==========================================

                for id_pnf in pnfs_coordinador:

                    pnf = Pnf.objects.filter(
                        id_pnf=id_pnf
                    ).first()

                    if not pnf:
                        continue

                    coordinador, creado = CoordinadorPNF.objects.get_or_create(
                        usuario=usuario,
                        nucleo=nucleo,
                        pnf=pnf,
                        defaults={
                            "activo": True
                        }
                    )

                    if not creado and not coordinador.activo:

                        coordinador.activo = True

                        coordinador.save(
                            update_fields=["activo"]
                        )

                # ==========================================
                # CONTROL DE ESTUDIO
                # ==========================================

                if control_estudio == "1":

                    control, creado = ControlEstudio.objects.get_or_create(
                        usuario=usuario,
                        nucleo=nucleo,
                        defaults={
                            "activo": True
                        }
                    )

                    if not creado and not control.activo:

                        control.activo = True

                        control.save(
                            update_fields=["activo"]
                        )

            return JsonResponse({
                "estado": "exito",
                "title": "Perfiles actualizados",
                "descripcion": "Los perfiles fueron actualizados correctamente.",
                "icon": "success"
            })

        except Exception as error:

            print("ERROR:", error)

            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "descripcion": "Ocurrió un error al actualizar los perfiles.",
                "icon": "error"
            })

    return render(request, "Director_General/actualizar_personal_registrado.html")

