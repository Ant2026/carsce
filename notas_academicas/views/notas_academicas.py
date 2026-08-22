from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Prefetch
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from django.utils import timezone
from django.db.models import Exists, OuterRef

from inicio_sesion.models import MateriaAsignada, PeriodoNotasMateria, Usuario, Pnf, PNFNucleo, Estudiante, EstatusEstudiante, CalendarioCargarNotas, Nucleos, PeriodoCargarNotas, Materia, Docente, DocenteAsignadoMateria

from notas_academicas.models import PlanActividadAcademica, DetallePlanActividades, HistorialTrayectoEstudiante, HistorialDetalleNota, HistorialModificacionNotas, DetallePlanEvaluacion, PromedioFinal, Calificaciones, DetalleCalificacionesUnidad

# Registrar Notas Académicas

def mat_not_acad(request):
    id_nucleo = request.POST.get("id_nucleo")
    id_pnf = request.POST.get("id_pnf")
    cedula = request.session.get("cedula_usuario")

    try:
        docente = Docente.objects.get(
            usuario__cedula_identidad=cedula,
            nucleo_id=id_nucleo,
            pnf_id=id_pnf
        )
    except Docente.DoesNotExist:
        return JsonResponse({
            "estado": "fallo",
            "datos": [],
            "descripcion": "No se encontró el docente."
        })

    hoy = timezone.localdate()

    # PERÍODOS CUYA FECHA DE CARGA ESTÁ ABIERTA ACTUALMENTE
    calendarios = (
        CalendarioCargarNotas.objects
        .filter(
            activo=True,
            fecha_inicio__lte=hoy,
            fecha_final__gte=hoy
        )
        .select_related("periodo")
    )

    if not calendarios.exists():
        return JsonResponse({
            "estado": "exito",
            "datos": [],
            "descripcion": "Actualmente no hay un período habilitado para cargar notas."
        })

    periodos_activos = {
        calendario.periodo.id_periodo_academico
        for calendario in calendarios
    }

    # MATERIAS ASIGNADAS AL DOCENTE
    asignaciones = (
        DocenteAsignadoMateria.objects
        .filter(
            docente=docente,
            activo=True,
            materia_asignada__activo=True
        )
        .select_related(
            "materia_asignada__materia",
            "materia_asignada__seccion"
        )
    )

    materias = []

    for asignacion in asignaciones:

        materia_asignada = asignacion.materia_asignada
        materia = materia_asignada.materia
        seccion = materia_asignada.seccion

        # PERÍODOS QUE TIENE CONFIGURADOS LA MATERIA
        periodos_materia = (
            PeriodoNotasMateria.objects
            .filter(
                materia=materia,
                periodo_id__in=periodos_activos
            )
            .select_related("periodo")
        )

        if not periodos_materia.exists():
            continue

        # CALIFICACIONES YA REGISTRADAS
        periodos_registrados = set(
            Calificaciones.objects
            .filter(
                materia_asignada=materia_asignada
            )
            .values_list(
                "periodo_materia__periodo_id",
                flat=True
            )
        )

        periodo_pendiente = None
        for periodo_materia in periodos_materia:
            periodo = periodo_materia.periodo
            id_periodo = periodo.id_periodo_academico

            # Ya fue cargado
            if id_periodo in periodos_registrados:
                continue

            periodo_pendiente = periodo
            break

        # SI TODOS LOS PERÍODOS YA FUERON CARGADOS
        if periodo_pendiente is None:
            continue

        materias.append({
            "id_materia_asignada": materia_asignada.id_materia_asignada,
            "id_materia": materia.id_materia,
            "nombre": materia.nombre,
            "codigo": materia.codigo,
            "trayecto": materia.trayecto,
            "seccion": str(seccion),
            "rol": asignacion.rol,

            "periodo": {
                "id": periodo_pendiente.id_periodo_academico,
                "nombre": periodo_pendiente.nombre
            }
        })

    return JsonResponse({
        "estado": "exito",
        "datos": materias
    })

def per_not_acad(request):
    if request.method == "POST":
        pnf = request.POST.get("id_pnf")
        materia_asignacion = request.POST.get("id_materia_asignada")

        try:
            materia_asignada = (
                MateriaAsignada.objects
                .select_related("materia")
                .get(
                    id_materia_asignada=materia_asignacion,
                    activo=True,
                    materia__id_pnf=pnf
                )
            )

        except MateriaAsignada.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "La materia asignada no se encuentra registrada."
            })

        # FECHA ACTUAL
        hoy = timezone.localdate()
        anio_actual = hoy.year

        # CALENDARIO DE CARGA ACTIVO EN LA FECHA ACTUAL
        calendarios = (
            CalendarioCargarNotas.objects
            .filter(
                activo=True,
                fecha_inicio__lte=hoy,
                fecha_final__gte=hoy
            )
            .select_related("periodo")
        )

        if not calendarios.exists():
            return JsonResponse({
                "estado": "exito",
                "title": "Exito",
                "icon": "success",
                "datos": [],
                "descripcion": "Actualmente no hay un período habilitado para cargar notas."
            })

        periodos_activos = {
            calendario.periodo_id
            for calendario in calendarios
        }

        # PERÍODOS QUE CORRESPONDEN A LA MATERIA
        periodos_materia = (
            PeriodoNotasMateria.objects
            .filter(
                materia=materia_asignada.materia,
                periodo_id__in=periodos_activos
            )
            .select_related("periodo")
        )

        if not periodos_materia.exists():
            return JsonResponse({
                "estado": "exito",
                "title": "Error",
                "icon": "error",
                "descripcion": "La materia no tiene un período de carga habilitado actualmente.",
                "datos": []
            })
        
        periodos_registrados = set(
            Calificaciones.objects
            .filter(
                materia_asignada=materia_asignada,
                fecha_promedio__year=anio_actual
            )
            .values_list(
                "periodo_materia__periodo_id",
                flat=True
            )
        )

        datos = []
        for periodo_materia in periodos_materia:
            periodo = periodo_materia.periodo

            # Ya fue registrado este período durante el año actual
            if periodo.id_periodo_academico in periodos_registrados:
                continue

            datos.append({
                "id_periodo_materia": periodo_materia.id,
                "id_periodo": periodo.id_periodo_academico,
                "nombre": periodo.nombre
            })

        return JsonResponse({
            "estado": "exito",
            "datos": datos
        })

def cant_det_pla(request):
    if request.method == "POST":
        nucleo = request.POST.get("id_nucleo")
        pnf = request.POST.get("id_pnf")
        materia_asignada = request.POST.get("id_materia_asignada")
        id_periodo_materia = request.POST.get("id_periodo_academico")

        if not all([
            nucleo,
            pnf,
            materia_asignada,
            id_periodo_materia
        ]):
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "Faltan datos para realizar la consulta."
            })

        try:
            periodo_materia = PeriodoNotasMateria.objects.select_related("periodo").get(id=id_periodo_materia)
        except PeriodoNotasMateria.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "El período seleccionado no existe."
            })

        # BUSCAR EL PLAN EXACTAMENTE DEL PERÍODO SELECCIONADO
        plan = PlanActividadAcademica.objects.filter(
            materia_asignacion_id=materia_asignada,
            pnf_id=pnf,
            nucleo_id=nucleo,
            periodo_academico_id=periodo_materia.periodo_id,
            activo=True,
            estado_aceptacion="ACEPTADA"
        ).first()

        # ==========================================================
        # SI NO EXISTE PLAN
        # ==========================================================

        if not plan:
            return JsonResponse({
                "estado": "exito",
                "cantidad_actividades": 0
            })

        # ==========================================================
        # CONTAR UNIDADES DEL PLAN
        # ==========================================================

        cantidad_unidades = (
            DetallePlanActividades.objects
            .filter(plan_academico_id=plan.id_plan)
            .values("titulo_unidad")
            .distinct()
            .count()
        )

        return JsonResponse({
            "estado": "exito",
            "cantidad_actividades": cantidad_unidades
        })

    return JsonResponse({
        "estado": "fallo",
        "title": "Error",
        "icon": "error",
        "descripcion": "Método de solicitud no permitido."
    })

def est_not_acad(request):
    if request.method == "POST":
        nucleo = request.POST.get("id_nucleo")
        pnf = request.POST.get("id_pnf")
        materia_asignacion = request.POST.get("id_materia_asignada")

        try:
            materia_asignada = MateriaAsignada.objects.select_related(
                "materia"
            ).get(
                id_materia_asignada=materia_asignacion
            )

            estudiantes = Estudiante.objects.filter(
                nucleo_id=nucleo,
                pnf_id=pnf,
                estatusestudiante__trayecto=materia_asignada.materia.trayecto,
                estatusestudiante__estatus="Inscrito(a)",
                estatusestudiante__estado="Activo"
            ).select_related(
                "usuario"
            ).distinct()

            datos = []
            for estudiante in estudiantes:
                datos.append({
                    "id_estudiante": estudiante.id_estudiante,
                    "nombres": estudiante.usuario.nombres,
                    "apellidos": estudiante.usuario.apellidos,
                    "nombre_completo": f"{estudiante.usuario.apellidos} {estudiante.usuario.nombres}",
                    "cedula": estudiante.usuario.cedula_identidad,
                })

            return JsonResponse({
                "estado": "exito",
                "estudiantes": datos
            })

        except MateriaAsignada.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "La materia asignada no existe."
            })

def reg_nota_acad(request):
    if request.method == "POST":
        nucleo_asignado = request.POST.get("nucleo_asignado")
        pnf_asignado = request.POST.get("pnf_asignado")
        materia_asignada = request.POST.get("materia_asignada")
        periodo_academico = request.POST.get("periodo_academico")
        trayecto_academico = request.POST.get("trayecto_academico")

        cantidad_evaluaciones = request.POST.get("cantidad_evaluaciones")
        
        calificaciones = {}
        asistencias = {}
        promedios = {}

        controles = [
            (nucleo_asignado, "Núcleo", "Debe selecciona el núcleo."),
            (pnf_asignado, "P.N.F", "Debe selecciona el P.N.F."),
            (materia_asignada, "Materia", "Debe seleccionar la materia."),
            (periodo_academico, "Periodo Académico", "Debe seleccionar el periodo académico."),
        ]

        for control, titulo, descripcion in controles:
            if not control:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": titulo,
                    "descripcion": descripcion
                })

        if not cantidad_evaluaciones:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Cantidad de evaluaciones",
                "descripcion": "Debe indicar la cantidad de evaluaciones."
            })

        try:
            cantidad_evaluaciones = int(cantidad_evaluaciones)
        except (TypeError, ValueError):
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Cantidad de evaluaciones",
                "descripcion": "La cantidad de evaluaciones no es válida."
            })

        if cantidad_evaluaciones < 1:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Cantidad de evaluaciones",
                "descripcion": "La cantidad de evaluaciones debe ser mayor que cero."
            })

        ids_estudiantes = set()
        for nombre_campo, valor in request.POST.items():
            if nombre_campo.startswith("calificacion_"):
                partes = nombre_campo.split("_")
                if len(partes) != 3:
                    continue

                id_estudiante = partes[1]
                numero_unidad = partes[2]

                ids_estudiantes.add(id_estudiante)

                calificaciones.setdefault(id_estudiante, {})
                calificaciones[id_estudiante][numero_unidad] = valor

            elif nombre_campo.startswith("asistencia_"):
                partes = nombre_campo.split("_")
                if len(partes) != 2:
                    continue

                id_estudiante = partes[1]

                ids_estudiantes.add(id_estudiante)
                asistencias[id_estudiante] = valor

            elif nombre_campo.startswith("promedio_"):
                partes = nombre_campo.split("_")
                if len(partes) != 2:
                    continue

                id_estudiante = partes[1]

                ids_estudiantes.add(id_estudiante)
                promedios[id_estudiante] = valor

        # OBTENER PERÍODO ACADÉMICO
        try:
            periodo = PeriodoNotasMateria.objects.select_related("periodo").get(id=periodo_academico)
        except PeriodoNotasMateria.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Ocurrió un error en el modelo intermedio (Periodo Notas Materia)."
            })

        # OBTENER MATERIA ASIGNADA
        try:
            materia_asignacion = MateriaAsignada.objects.get(id_materia_asignada=materia_asignada)
        except MateriaAsignada.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Ocurrió un error en el modelo intermedio (Materia Asignación)."
            })

        # BUSCAR EL PLAN DEL PERÍODO ACADÉMICO SELECCIONADO
        plan = PlanActividadAcademica.objects.filter(
            materia_asignacion=materia_asignacion,
            pnf_id=pnf_asignado,
            nucleo_id=nucleo_asignado,
            periodo_academico_id=periodo.periodo_id,

            activo=True,
            estado_aceptacion="ACEPTADA"
        ).first()
        if not plan:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Plan académico",
                "descripcion": (
                    "No se encuentra registrado un plan de actividad "
                    "académica aceptado para la materia y el período "
                    "académico seleccionado."
                )
            })

        # OBTENER LAS UNIDADES DEL PLAN
        unidades = list(plan.detalles.all().order_by("id_detalle"))
        if not unidades:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Unidades académicas",
                "descripcion": (
                    "El plan de actividad académica seleccionado "
                    "no tiene unidades registradas."
                )
            })

        # LA CANTIDAD REAL DE COLUMNAS ES LA CANTIDAD DE UNIDADES
        cantidad_evaluaciones = len(unidades)

        # ESTUDIANTES
        for id_estudiante in ids_estudiantes:
            try:
                estudiante = Estudiante.objects.get(
                    id_estudiante=id_estudiante,
                    nucleo_id=nucleo_asignado,
                    pnf_id=pnf_asignado
                )
            except Estudiante.DoesNotExist:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Estudiante",
                    "descripcion": f"No se encontró el estudiante {id_estudiante}."
                })

            # PROMEDIO
            valor_promedio = promedios.get(id_estudiante,  "0")
            if valor_promedio == "":
                valor_promedio = "0"

            try:
                promedio = Decimal(valor_promedio.replace(",", "."))
            except (ValueError, TypeError):
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Promedio inválido",
                    "descripcion": f"El promedio del estudiante {id_estudiante} no es válido."
                })

            # ASISTENCIA
            try:
                asistencia = int(asistencias.get(id_estudiante, 0))
            except (ValueError, TypeError):
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Asistencia inválida",
                    "descripcion": f"La asistencia del estudiante {id_estudiante} no es válida."
                })

            if asistencia < 0 or asistencia > 100:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Asistencia inválida",
                    "descripcion": f"La asistencia del estudiante {id_estudiante} debe estar entre 0 y 100."
                })

            # CONDICIÓN
            nombre_materia = (
                materia_asignacion.materia.nombre
                .strip()
                .lower()
            )

            if asistencia >= Decimal("75"):
                if "proyecto socio tecnológico" in nombre_materia:
                    if promedio >= Decimal("16"):
                        condicion = "APROBADO"
                    else:
                        condicion = "REPROBADO"
                else:
                    if promedio >= Decimal("12"):
                        condicion = "APROBADO"
                    else:
                        condicion = "REPARACIÓN"
            else:
                condicion = "REPROBADO"

            # CABECERA DE CALIFICACIÓN
            calificacion = Calificaciones.objects.create(
                periodo_materia=periodo,
                materia_asignada=materia_asignacion,
                estudiante=estudiante,
                promedio_tramo=promedio,
                asistencia=asistencia,
                condicion=condicion,
                trayecto=trayecto_academico,
                fecha_promedio=timezone.localdate()
            )

            # NOTAS DE LAS UNIDADES
            notas_estudiante = calificaciones.get(id_estudiante, {})
            for numero_unidad, nota in notas_estudiante.items():
                if nota == "":
                    continue
                try:
                    numero_unidad = int(numero_unidad)
                except (ValueError, TypeError):
                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "error",
                        "title": "Unidad inválida",
                        "descripcion": f"La unidad recibida para el estudiante {id_estudiante} no es válida."
                    })

                if numero_unidad < 1 or numero_unidad > len(unidades):
                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "error",
                        "title": "Unidad inválida",
                        "descripcion": (
                            f"La unidad {numero_unidad} "
                            f"no existe en el plan académico."
                        )
                    })

                try:
                    nota_unidad = Decimal(nota.replace(",", "."))
                except (ValueError, TypeError):
                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "error",
                        "title": "Nota inválida",
                        "descripcion": (
                            f"La nota de la unidad {numero_unidad} "
                            f"del estudiante {id_estudiante} no es válida."
                        )
                    })

                unidad = unidades[numero_unidad - 1]
                DetalleCalificacionesUnidad.objects.create(
                    calificacion=calificacion,
                    unidad=unidad,
                    nota_unidad=nota_unidad
                )

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Exito",
            "descripcion": "Se registraron las notas académicas exitosamente."
        }) 

    return render(request, "registrar_notas_academicas.html")

# Visualizar Notas Académicas

def vis_not_acad(request):
    return render (request, "visualizar_notas_academicas.html")

def mat_reg_not(request):
    if request.method == "POST":
        cedula = request.session.get("cedula_usuario")
        pnf = request.POST.get("id_pnf")

        materias = (
            Calificaciones.objects
            .filter(
                materia_asignada__isnull=False,
                materia_asignada__materia__id_pnf_id=pnf,
                materia_asignada__docentes__docente__usuario__cedula_identidad=cedula,
            )
            .select_related(
                "materia_asignada__materia"
            )
            .values(
                "materia_asignada_id",
                "materia_asignada__materia__nombre",
                "materia_asignada__materia__trayecto",
            )
            .distinct()
            .order_by(
                "materia_asignada__materia__nombre"
            )
        )

        return JsonResponse({
            "estado": "exito",
            "materias": [
                {
                    "id_materia_asignada": materia["materia_asignada_id"],
                    "nombre_materia": materia[
                        "materia_asignada__materia__nombre"
                    ],
                    "trayecto_materia": materia[
                        "materia_asignada__materia__trayecto"
                    ]
                }
                for materia in materias
            ]
        })

def perd_reg_not(request):
    if request.method == "POST":
        cedula = request.session.get("cedula_usuario")
        pnf = request.POST.get("id_pnf")
        materia_asignada = request.POST.get("id_materia_asignada")

        periodos = (
            Calificaciones.objects
            .filter(
                materia_asignada_id=materia_asignada,
                materia_asignada__materia__id_pnf_id=pnf,
                materia_asignada__docentes__docente__usuario__cedula_identidad=cedula,
            )
            .select_related(
                "periodo_materia__periodo"
            )
            .values(
                "periodo_materia__periodo__id_periodo_academico",
                "periodo_materia__periodo__nombre"
            )
            .distinct()
            .order_by(
                "periodo_materia__periodo__nombre"
            )
        )

        return JsonResponse({
            "estado": "exito",
            "periodos": [
                {
                    "id_periodo_academico": periodo[
                        "periodo_materia__periodo__id_periodo_academico"
                    ],
                    "nombre_periodo": periodo[
                        "periodo_materia__periodo__nombre"
                    ]
                }
                for periodo in periodos
            ]
        })

def fech_reg_not(request):
    if request.method == "POST":
        materia_asignada = request.POST.get("id_materia_asignada")
        periodo_academico = request.POST.get("id_periodo_academico")

        if not materia_asignada or not periodo_academico:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Datos incompletos",
                "descripcion": (
                    "Debe seleccionar la materia y el período académico."
                )
            })

        fechas = (
            Calificaciones.objects
            .filter(
                materia_asignada_id=materia_asignada,
                periodo_materia__periodo_id=periodo_academico
            )
            .values_list(
                "fecha_promedio",
                flat=True
            )
            .distinct()
            .order_by("-fecha_promedio")
        )

        return JsonResponse({
            "estado": "exito",
            "fechas": [
                fecha.strftime("%Y-%m-%d")
                for fecha in fechas
            ]
        })

def calf_reg_not(request):
    if request.method == "POST":
        cedula = request.session.get("cedula_usuario")
        nucleo = request.POST.get("id_nucleo")
        pnf = request.POST.get("id_pnf")
        materia_asignada = request.POST.get("id_materia_asignada")
        periodo_academico = request.POST.get("id_periodo_academico")
        fecha_calificacion = request.POST.get("fecha_calificacion")

        calificaciones = (
            Calificaciones.objects
            .filter(
                materia_asignada_id=materia_asignada,
                materia_asignada__materia__id_pnf_id=pnf,
                materia_asignada__docentes__docente__usuario__cedula_identidad=cedula,
                periodo_materia__periodo_id=periodo_academico,
                fecha_promedio=fecha_calificacion,
            )
            .select_related(
                "estudiante__usuario",
                "periodo_materia__periodo",
            )
            .prefetch_related(
                "detalles_unidad__unidad"
            )
            .order_by(
                "estudiante__usuario__apellidos",
                "estudiante__usuario__nombres",
                "estudiante__usuario__cedula_identidad",
            )
        )

        datos = []
        for calificacion in calificaciones:
            estudiante = calificacion.estudiante
            usuario = estudiante.usuario

            datos.append({
                "id_calificaciones": calificacion.id_calificaciones,
                "id_estudiante": estudiante.id_estudiante,
                "nombre_estudiante": (
                    f"{usuario.nombres} {usuario.apellidos}"
                ),
                "cedula_identidad": usuario.cedula_identidad,
                "promedio": str(calificacion.promedio_tramo),
                "asistencia": calificacion.asistencia,
                "condicion": calificacion.condicion,
                "trayecto": calificacion.trayecto,
                "unidades": [
                    {
                        "id_unidad": detalle.unidad_id,
                        "nombre_unidad": detalle.unidad.titulo_unidad,
                        "nota_unidad": str(detalle.nota_unidad),
                        "fecha_calificacion": (
                            detalle.fecha_calificacion.strftime("%Y-%m-%d")
                        ),
                    }
                    for detalle in calificacion.detalles_unidad.all()
                ]
            })

        return JsonResponse({
            "estado": "exito",
            "calificaciones": datos
        })

# Modificar Notas Académicas

def mod_mat_not(request):
    if request.method == "POST":
        cedula = request.session.get("cedula_usuario")
        pnf = request.POST.get("id_pnf")

        hoy = timezone.localdate()
        materias = (
            Calificaciones.objects
            .filter(
                materia_asignada__isnull=False,
                materia_asignada__materia__id_pnf_id=pnf, # PNF
                materia_asignada__docentes__docente__usuario__cedula_identidad=cedula, # Docente que tiene asignada la materia
                # Calendario de carga de notas vigente
                materia_asignada__materia__periodonotasmateria__periodo__calendariocargarnotas__activo=True,
                materia_asignada__materia__periodonotasmateria__periodo__calendariocargarnotas__fecha_inicio__lte=hoy,
                materia_asignada__materia__periodonotasmateria__periodo__calendariocargarnotas__fecha_final__gte=hoy,
            )
            .select_related(
                "materia_asignada__materia"
            )
            .values(
                "materia_asignada_id",
                "materia_asignada__materia__nombre",
                "materia_asignada__materia__trayecto",
            )
            .distinct()
            .order_by(
                "materia_asignada__materia__nombre"
            )
        )

        return JsonResponse({
            "estado": "exito",
            "materias": [
                {
                    "id_materia_asignada": materia["materia_asignada_id"],
                    "nombre_materia": materia[
                        "materia_asignada__materia__nombre"
                    ],
                    "trayecto_materia": materia[
                        "materia_asignada__materia__trayecto"
                    ]
                }
                for materia in materias
            ]
        })

def mod_per_not(request):
    if request.method == "POST":

        cedula = request.session.get("cedula_usuario")
        pnf = request.POST.get("id_pnf")
        materia_asignada = request.POST.get("id_materia_asignada")

        hoy = timezone.localdate()

        periodo = (
            Calificaciones.objects
            .filter(
                materia_asignada_id=materia_asignada,
                materia_asignada__materia__id_pnf_id=pnf,
                materia_asignada__docentes__docente__usuario__cedula_identidad=cedula,

                # CALENDARIO ACADÉMICO VIGENTE
                periodo_materia__periodo__calendariocargarnotas__activo=True,
                periodo_materia__periodo__calendariocargarnotas__fecha_inicio__lte=hoy,
                periodo_materia__periodo__calendariocargarnotas__fecha_final__gte=hoy,
            )
            .select_related(
                "periodo_materia__periodo"
            )
            .values(
                "periodo_materia__periodo__id_periodo_academico",
                "periodo_materia__periodo__nombre"
            )
            .first()
        )

        if not periodo:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Periodo Académico",
                "descripcion": (
                    "No existe un período académico vigente "
                    "para modificar las notas."
                )
            })

        return JsonResponse({
            "estado": "exito",
            "id_periodo_academico": periodo[
                "periodo_materia__periodo__id_periodo_academico"
            ],
            "nombre_periodo": periodo[
                "periodo_materia__periodo__nombre"
            ]
        })

def mod_calf_not(request):
    if request.method == "POST":

        cedula = request.session.get("cedula_usuario")
        pnf = request.POST.get("id_pnf")
        materia_asignada = request.POST.get("id_materia_asignada")
        periodo_academico = request.POST.get("id_periodo_academico")

        calificaciones = (
            Calificaciones.objects
            .filter(
                materia_asignada_id=materia_asignada,
                materia_asignada__materia__id_pnf_id=pnf,
                materia_asignada__docentes__docente__usuario__cedula_identidad=cedula,
                periodo_materia__periodo_id=periodo_academico,
            )
            .select_related(
                "estudiante__usuario",
                "periodo_materia__periodo",
                "materia_asignada__materia",
            )
            .prefetch_related(
                "detalles_unidad__unidad"
            )
            .order_by(
                "estudiante__usuario__apellidos",
                "estudiante__usuario__nombres",
                "estudiante__usuario__cedula_identidad",
            )
        )

        if not calificaciones.exists():
            return JsonResponse({
                "estado": "error",
                "mensaje": "No existen calificaciones registradas para este período."
            })

        # Como todas las calificaciones pertenecen al mismo período
        # y a la misma carga, tomamos la fecha de la primera.
        primera_calificacion = calificaciones.first()

        periodo = primera_calificacion.periodo_materia.periodo
        materia = primera_calificacion.materia_asignada.materia

        datos = []

        for calificacion in calificaciones:
            estudiante = calificacion.estudiante
            usuario = estudiante.usuario

            datos.append({
                "id_calificaciones": calificacion.id_calificaciones,
                "id_estudiante": estudiante.id_estudiante,
                "nombre_estudiante": (
                    f"{usuario.nombres} {usuario.apellidos}"
                ),
                "cedula_identidad": usuario.cedula_identidad,
                "promedio": str(calificacion.promedio_tramo),
                "asistencia": calificacion.asistencia,
                "condicion": calificacion.condicion,
                "trayecto": calificacion.trayecto,

                "unidades": [
                    {
                        "id_unidad": detalle.unidad_id,
                        "nombre_unidad": detalle.unidad.titulo_unidad,
                        "nota_unidad": str(detalle.nota_unidad),
                        "fecha_calificacion": (
                            detalle.fecha_calificacion.strftime("%Y-%m-%d")
                            if detalle.fecha_calificacion
                            else None
                        ),
                    }
                    for detalle in calificacion.detalles_unidad.all()
                ]
            })

        return JsonResponse({
            "estado": "exito",

            "periodo": {
                "id_periodo_academico": periodo.id_periodo_academico,
                "nombre": periodo.nombre,
            },

            "materia": {
                "id_materia_asignada": materia_asignada,
                "id_materia": materia.id_materia,
                "nombre": materia.nombre,
                "trayecto": materia.trayecto,
            },

            # Fecha en que se registraron las notas
            "fecha_calificacion": (
                primera_calificacion.fecha_promedio.strftime("%Y-%m-%d")
                if primera_calificacion.fecha_promedio
                else None
            ),

            "calificaciones": datos
        })

def mod_calf_not(request):
    if request.method == "POST":

        cedula = request.session.get("cedula_usuario")
        pnf = request.POST.get("id_pnf")
        materia_asignada = request.POST.get("id_materia_asignada")
        periodo_academico = request.POST.get("id_periodo_academico")

        calificaciones = (
            Calificaciones.objects
            .filter(
                materia_asignada_id=materia_asignada,
                materia_asignada__materia__id_pnf_id=pnf,
                materia_asignada__docentes__docente__usuario__cedula_identidad=cedula,
                periodo_materia__periodo_id=periodo_academico,
            )
            .select_related(
                "estudiante__usuario",
                "periodo_materia__periodo",
                "materia_asignada__materia",
            )
            .prefetch_related(
                "detalles_unidad__unidad"
            )
            .order_by(
                "estudiante__usuario__apellidos",
                "estudiante__usuario__nombres",
                "estudiante__usuario__cedula_identidad",
            )
        )

        if not calificaciones.exists():
            return JsonResponse({
                "estado": "error",
                "mensaje": "No existen calificaciones registradas para este período."
            })

        # Como todas las calificaciones pertenecen al mismo período
        # y a la misma carga, tomamos la fecha de la primera.
        primera_calificacion = calificaciones.first()

        periodo = primera_calificacion.periodo_materia.periodo
        materia = primera_calificacion.materia_asignada.materia

        datos = []

        for calificacion in calificaciones:
            estudiante = calificacion.estudiante
            usuario = estudiante.usuario

            datos.append({
                "id_calificaciones": calificacion.id_calificaciones,
                "id_estudiante": estudiante.id_estudiante,
                "nombre_estudiante": (
                    f"{usuario.nombres} {usuario.apellidos}"
                ),
                "cedula_identidad": usuario.cedula_identidad,
                "promedio": str(calificacion.promedio_tramo),
                "asistencia": calificacion.asistencia,
                "condicion": calificacion.condicion,
                "trayecto": calificacion.trayecto,

                "unidades": [
                    {
                        "id_unidad": detalle.unidad_id,
                        "nombre_unidad": detalle.unidad.titulo_unidad,
                        "nota_unidad": str(detalle.nota_unidad),
                        "fecha_calificacion": (
                            detalle.fecha_calificacion.strftime("%Y-%m-%d")
                            if detalle.fecha_calificacion
                            else None
                        ),
                    }
                    for detalle in calificacion.detalles_unidad.all()
                ]
            })

        return JsonResponse({
            "estado": "exito",

            "periodo": {
                "id_periodo_academico": periodo.id_periodo_academico,
                "nombre": periodo.nombre,
            },

            "materia": {
                "id_materia_asignada": materia_asignada,
                "id_materia": materia.id_materia,
                "nombre": materia.nombre,
                "trayecto": materia.trayecto,
            },

            # Fecha en que se registraron las notas
            "fecha_calificacion": (
                primera_calificacion.fecha_promedio.strftime("%Y-%m-%d")
                if primera_calificacion.fecha_promedio
                else None
            ),

            "calificaciones": datos
        })

@transaction.atomic
def mod_not_acad(request):
    if request.method != "POST":
        return render(request, "modificar_notas_academicas.html")
    
    nucleo = request.POST.get("nucleo_asignado")
    pnf = request.POST.get("pnf_asignado")
    materia_id = request.POST.get("materia_asignada")
    periodo_id = request.POST.get("id_periodo_academico")
    trayecto = request.POST.get("trayecto_academico")
    motivo = request.POST.get(
        "motivo",
        "Modificación de notas académicas."
    ).strip()

    cedula = request.session.get("cedula_usuario")
    if not cedula:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Sesión",
            "descripcion": "No se encontró la cédula del usuario en la sesión."
        })

    usuario = Usuario.objects.filter(cedula_identidad=cedula).first()
    if not usuario:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Usuario",
            "descripcion": "No se encontró el usuario asociado a la cédula de la sesión."
        })

    # VALIDAR DATOS PRINCIPALES
    for valor, titulo, descripcion in [
        (
            nucleo,
            "Núcleo",
            "Debe seleccionar el núcleo."
        ),
        (
            pnf,
            "P.N.F",
            "Debe seleccionar el P.N.F."
        ),
        (
            materia_id,
            "Materia",
            "Debe seleccionar la materia."
        ),
        (
            periodo_id,
            "Período Académico",
            "Debe seleccionar el período académico."
        ),
        (
            trayecto,
            "Trayecto",
            "Debe seleccionar el trayecto."
        ),]:
        if not valor:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": titulo,
                "descripcion": descripcion
            })

    # RECOPILAR DATOS DEL FORMULARIO
    calificaciones = {}
    asistencias = {}
    for nombre, valor in request.POST.items():
        if not ( nombre.startswith("calificacion_") or nombre.startswith("asistencia_")):
            continue

        valor = valor.strip()
        partes = nombre.split("_")

        # CALIFICACIÓN
        if nombre.startswith("calificacion_"):
            if len(partes) != 3:
                continue

            id_estudiante = partes[1]
            numero_unidad = partes[2]
            if not valor:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": "Campo vacío",
                    "descripcion": (
                        f"La calificación de la unidad "
                        f"{numero_unidad} del estudiante "
                        f"{id_estudiante} está vacía."
                    )
                })

            calificaciones.setdefault(
                id_estudiante,
                {}
            )[numero_unidad] = valor

        # ASISTENCIA
        elif nombre.startswith("asistencia_"):
            if len(partes) != 2:
                continue

            id_estudiante = partes[1]

            if not valor:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": "Campo vacío",
                    "descripcion": (
                        f"La asistencia del estudiante "
                        f"{id_estudiante} está vacía."
                    )
                })

            asistencias[id_estudiante] = valor

    # VALIDAR CALIFICACIONES
    if not calificaciones:
        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "title": "Sin calificaciones",
            "descripcion": (
                "No se encontraron calificaciones "
                "para actualizar."
            )
        })

    # MATERIA ASIGNADA
    try:
        materia_asignacion = (
            MateriaAsignada.objects
            .select_related("materia")
            .get(
                id_materia_asignada=materia_id
            )
        )
    except MateriaAsignada.DoesNotExist:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Materia",
            "descripcion": (
                "No se encontró la materia asignada."
            )
        })

    # PERÍODO NOTAS MATERIA
    try:
        periodo = (
            PeriodoNotasMateria.objects
            .select_related("periodo")
            .get(
                materia=materia_asignacion.materia,
                periodo_id=periodo_id
            )
        )
    except PeriodoNotasMateria.DoesNotExist:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Período",
            "descripcion": (
                "No existe un período de notas para "
                "la materia y período seleccionado."
            )
        })

    # PLAN ACADÉMICO
    plan = (
        PlanActividadAcademica.objects
        .filter(
            materia_asignacion=materia_asignacion,
            pnf_id=pnf,
            nucleo_id=nucleo,
            periodo_academico_id=periodo.periodo_id,
            activo=True,
            estado_aceptacion="ACEPTADA"
        )
        .first()
    )
    if not plan:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Plan académico",
            "descripcion": (
                "No se encuentra un plan de actividad "
                "académica aceptado para la materia "
                "y período seleccionado."
            )
        })

    # UNIDADES
    unidades = list(
        plan.detalles
        .all()
        .order_by("id_detalle")
    )
    if not unidades:
        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "title": "Unidades académicas",
            "descripcion": (
                "El plan de actividad académica "
                "no tiene unidades registradas."
            )
        })

    # REGLA DE APROBACIÓN
    nombre_materia = (
        materia_asignacion.materia.nombre
        .strip()
        .lower()
    )

    es_proyecto = (
        "proyecto socio tecnológico"
        in nombre_materia
    )

    nota_aprobacion = (
        Decimal("16")
        if es_proyecto
        else Decimal("12")
    )

    # DOCENTE ASIGNADO
    docente_asignado = (
        DocenteAsignadoMateria.objects
        .filter(
            materia_asignada=materia_asignacion,
            activo=True
        )
        .first()
    )
    if not docente_asignado:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Docente",
            "descripcion": (
                "No existe un docente asignado activo "
                "para la materia seleccionada."
            )
        })

    # ==========================================================
    # LISTA DE CAMBIOS PARA EL HISTORIAL
    # ==========================================================

    cambios_historial = []

    # ==========================================================
    # PROCESAR ESTUDIANTES
    # ==========================================================

    for id_estudiante, notas in calificaciones.items():

        # ------------------------------------------------------
        # ESTUDIANTE
        # ------------------------------------------------------

        estudiante = (
            Estudiante.objects
            .filter(
                id_estudiante=id_estudiante,
                nucleo_id=nucleo,
                pnf_id=pnf
            )
            .first()
        )

        if not estudiante:

            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Estudiante",
                "descripcion": (
                    f"No se encontró el estudiante "
                    f"{id_estudiante}."
                )
            })

        # ------------------------------------------------------
        # CALIFICACIÓN EXISTENTE
        # ------------------------------------------------------

        try:

            calificacion = (
                Calificaciones.objects
                .get(
                    periodo_materia=periodo,
                    materia_asignada=materia_asignacion,
                    estudiante=estudiante,
                    trayecto=trayecto
                )
            )

        except Calificaciones.DoesNotExist:

            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Calificación no encontrada",
                "descripcion": (
                    f"No existe una calificación para "
                    f"el estudiante {id_estudiante}."
                )
            })

        except Calificaciones.MultipleObjectsReturned:

            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Registros duplicados",
                "descripcion": (
                    f"Existen múltiples calificaciones "
                    f"para el estudiante {id_estudiante}."
                )
            })

        # ------------------------------------------------------
        # RESPALDAR VALORES ANTERIORES
        # ------------------------------------------------------

        asistencia_anterior = calificacion.asistencia
        promedio_anterior = calificacion.promedio_tramo

        # ------------------------------------------------------
        # ASISTENCIA NUEVA
        # ------------------------------------------------------

        try:

            asistencia = int(
                asistencias.get(
                    id_estudiante,
                    asistencia_anterior
                )
            )

        except (ValueError, TypeError):

            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Asistencia inválida",
                "descripcion": (
                    f"La asistencia del estudiante "
                    f"{id_estudiante} no es válida."
                )
            })

        if not 0 <= asistencia <= 100:

            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Asistencia inválida",
                "descripcion": (
                    f"La asistencia del estudiante "
                    f"{id_estudiante} debe estar "
                    f"entre 0 y 100."
                )
            })

        # ------------------------------------------------------
        # NOTAS DE LAS UNIDADES
        # ------------------------------------------------------

        cambios_estudiante = []

        for numero_unidad, nota in notas.items():

            try:

                numero_unidad = int(
                    numero_unidad
                )

                nota_unidad = Decimal(
                    str(nota).replace(",", ".")
                )

            except (ValueError, TypeError):

                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Nota inválida",
                    "descripcion": (
                        f"La nota de la unidad "
                        f"{numero_unidad} del estudiante "
                        f"{id_estudiante} no es válida."
                    )
                })

            # --------------------------------------------------
            # VALIDAR UNIDAD
            # --------------------------------------------------

            if not 1 <= numero_unidad <= len(unidades):

                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Unidad inválida",
                    "descripcion": (
                        f"La unidad {numero_unidad} "
                        f"no existe en el plan académico."
                    )
                })

            unidad = unidades[
                numero_unidad - 1
            ]

            # --------------------------------------------------
            # DETALLE EXISTENTE
            # --------------------------------------------------

            try:

                detalle = (
                    DetalleCalificacionesUnidad.objects
                    .get(
                        calificacion=calificacion,
                        unidad=unidad
                    )
                )

            except DetalleCalificacionesUnidad.DoesNotExist:

                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Detalle no encontrado",
                    "descripcion": (
                        f"No existe el detalle de la unidad "
                        f"{numero_unidad} para el estudiante "
                        f"{id_estudiante}."
                    )
                })

            # --------------------------------------------------
            # NOTA ANTERIOR
            # --------------------------------------------------

            nota_anterior = detalle.nota_unidad

            # --------------------------------------------------
            # GUARDAR CAMBIO
            # --------------------------------------------------

            if nota_anterior != nota_unidad:

                cambios_estudiante.append({
                    "numero_unidad": numero_unidad,
                    "nota_anterior": nota_anterior,
                    "nota_nueva": nota_unidad,
                })

                detalle.nota_unidad = nota_unidad

                detalle.save(
                    update_fields=[
                        "nota_unidad"
                    ]
                )

        # ======================================================
        # RECALCULAR PROMEDIO
        # ======================================================

        notas_validas = list(
            DetalleCalificacionesUnidad.objects
            .filter(
                calificacion=calificacion,
                nota_unidad__isnull=False
            )
            .values_list(
                "nota_unidad",
                flat=True
            )
        )

        if not notas_validas:

            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Sin notas",
                "descripcion": (
                    f"No existen notas registradas "
                    f"para el estudiante "
                    f"{id_estudiante}."
                )
            })

        promedio = (
            sum(
                notas_validas,
                Decimal("0")
            )
            / Decimal(len(notas_validas))
        ).quantize(
            Decimal("0.01")
        )

        # ======================================================
        # DETERMINAR CONDICIÓN
        # ======================================================

        if asistencia < 75:

            condicion = "REPROBADO"

        elif promedio >= nota_aprobacion:

            condicion = "APROBADO"

        elif es_proyecto:

            condicion = "REPROBADO"

        else:

            condicion = "REPARACIÓN"

        # ======================================================
        # DETECTAR CAMBIO DE ASISTENCIA / PROMEDIO
        # ======================================================

        cambio_asistencia = (
            asistencia_anterior != asistencia
        )

        cambio_promedio = (
            promedio_anterior != promedio
        )

        # ======================================================
        # GUARDAR CALIFICACIÓN
        # ======================================================

        if (
            cambio_asistencia
            or cambio_promedio
            or cambios_estudiante
        ):

            calificacion.asistencia = asistencia
            calificacion.promedio_tramo = promedio
            calificacion.condicion = condicion

            calificacion.save(
                update_fields=[
                    "asistencia",
                    "promedio_tramo",
                    "condicion"
                ]
            )

        # ======================================================
        # AGREGAR AL HISTORIAL
        # ======================================================

        if (
            cambio_asistencia
            or cambio_promedio
            or cambios_estudiante
        ):

            cambios_historial.append({
                "estudiante": estudiante,
                "cambios_unidades": cambios_estudiante,
                "asistencia_anterior": asistencia_anterior,
                "asistencia_nueva": asistencia,
                "promedio_anterior": promedio_anterior,
                "promedio_nuevo": promedio,
            })

    # ==========================================================
    # CREAR HISTORIAL
    # ==========================================================

    if cambios_historial:

        historial = HistorialModificacionNotas.objects.create(
            docente_asignado=docente_asignado,
            periodo_academico=periodo.periodo,
            trayecto=trayecto,
            usuario_modifica=usuario,
            motivo=motivo or (
                "Modificación de notas académicas."
            )
        )

        # ======================================================
        # DETALLES DEL HISTORIAL
        # ======================================================

        for cambio in cambios_historial:

            estudiante = cambio["estudiante"]

            cambios_unidades = (
                cambio["cambios_unidades"]
            )

            # ----------------------------------------------
            # Si hubo modificaciones de unidades
            # ----------------------------------------------

            if cambios_unidades:

                for unidad in cambios_unidades:

                    HistorialDetalleNota.objects.create(
                        historial=historial,
                        estudiante=estudiante,
                        numero_unidad=unidad[
                            "numero_unidad"
                        ],
                        nota_anterior=unidad[
                            "nota_anterior"
                        ],
                        nota_nueva=unidad[
                            "nota_nueva"
                        ],
                        asistencia_anterior=cambio[
                            "asistencia_anterior"
                        ],
                        asistencia_nueva=cambio[
                            "asistencia_nueva"
                        ],
                        promedio_anterior=cambio[
                            "promedio_anterior"
                        ],
                        promedio_nuevo=cambio[
                            "promedio_nuevo"
                        ]
                    )

            # ----------------------------------------------
            # Si solamente cambió asistencia
            # ----------------------------------------------

            elif (
                cambio["asistencia_anterior"]
                != cambio["asistencia_nueva"]
                or
                cambio["promedio_anterior"]
                != cambio["promedio_nuevo"]
            ):

                HistorialDetalleNota.objects.create(
                    historial=historial,
                    estudiante=estudiante,
                    numero_unidad=0,
                    nota_anterior=Decimal("0"),
                    nota_nueva=Decimal("0"),
                    asistencia_anterior=cambio[
                        "asistencia_anterior"
                    ],
                    asistencia_nueva=cambio[
                        "asistencia_nueva"
                    ],
                    promedio_anterior=cambio[
                        "promedio_anterior"
                    ],
                    promedio_nuevo=cambio[
                        "promedio_nuevo"
                    ]
                )

    # ==========================================================
    # RESPUESTA
    # ==========================================================

    if cambios_historial:

        descripcion = (
            "Se actualizaron las notas y "
            "se generó el respaldo de la modificación."
        )

    else:

        descripcion = (
            "No se detectaron cambios en las notas."
        )

    return JsonResponse({
        "estado": "exito",
        "icon": "success",
        "title": "Éxito",
        "descripcion": descripcion
    })

# Visualizar Notas Académicas Estudiante

def nucleos_est_asig(request):
    cedula = request.session.get("cedula_usuario")

    nucleos = (
        Estudiante.objects
        .filter(
            usuario__cedula_identidad=cedula
        )
        .values(
            "nucleo__id_nucleo",
            "nucleo__municipio",
            "nucleo__direccion"
        )
        .distinct()
    )

    return JsonResponse({
        "nucleos": [
            {
                "id_nucleo": nucleo["nucleo__id_nucleo"],
                "municipio": nucleo["nucleo__municipio"],
                "direccion": nucleo["nucleo__direccion"],
            }
            for nucleo in nucleos
        ]
    })

def pnfs_est_asig(request):
    if request.method == "POST":
        id_nucleo = request.POST.get("id_nucleo")

        pnfs = (
            PNFNucleo.objects
            .filter(
                id_nucleo_id=id_nucleo
            )
            .values(
                "id_pnf__id_pnf",
                "id_pnf__pnf",
                "id_pnf__codigo",
                "id_pnf__periodo_academico"
            )
            .distinct()
        )

        return JsonResponse({
            "pnfs": [
                {
                    "id_pnf": pnf["id_pnf__id_pnf"],
                    "pnf": pnf["id_pnf__pnf"],
                    "codigo": pnf["id_pnf__codigo"],
                    "periodo_academico": pnf["id_pnf__periodo_academico"]
                }
                for pnf in pnfs
            ]
        })

def mate_tray_est(request):
    if request.method == "POST":
        cedula = request.session.get("cedula_usuario")
        id_nucleo = request.POST.get("id_nucleo")
        id_pnf = request.POST.get("id_pnf")

        # BUSCAR AL ESTUDIANTE
        estudiante = (
            Estudiante.objects
            .filter(
                usuario__cedula_identidad=cedula,
                nucleo_id=id_nucleo,
                pnf_id=id_pnf
            )
            .first()
        )

        if not estudiante:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "El estudiante no está asignado a ese núcleo y PNF"
            })

        # BUSCAR EL ESTATUS/TRAYECTO DEL ESTUDIANTE
        estatus_estudiante = (
            EstatusEstudiante.objects
            .filter(
                estudiante=estudiante,
                estado="Activo",
                estatus="Inscrito(a)"
            )
            .order_by("-fecha_ingreso")
            .first()
        )

        if not estatus_estudiante:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "El estudiante no se encuentra activo o inscrito en el P.N.F"
            })

        trayecto = estatus_estudiante.trayecto

        # BUSCAR LAS MATERIAS DEL PNF Y TRAYECTO
        materias = (
            Materia.objects
            .filter(
                id_pnf_id=id_pnf,
                trayecto=trayecto
            )
            .values(
                "id_materia",
                "nombre",
                "codigo",
                "trayecto",
                "recuperacion",
                "htea",
                "htei"
            )
            .order_by("nombre")
        )

        return JsonResponse({
            "estado": "exito",
            "trayecto": trayecto,
            "materias": list(materias)
        })

def plan_act_est(request):
    if request.method == "POST":
        cedula = request.session.get("cedula_usuario")
        id_nucleo = request.POST.get("id_nucleo")
        id_pnf = request.POST.get("id_pnf")
        id_materia = request.POST.get("id_materia")

        if not id_nucleo or not id_pnf or not id_materia:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Debe indicar el núcleo, PNF y materia"
            })

        # BUSCAR ESTUDIANTE
        estudiante = (
            Estudiante.objects
            .filter(
                usuario__cedula_identidad=cedula,
                nucleo_id=id_nucleo,
                pnf_id=id_pnf
            )
            .first()
        )

        if not estudiante:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "El estudiante no está registrado en el núcleo y P.N.F seleccionado"
            })

        # VERIFICAR ESTATUS DEL ESTUDIANTE
        estatus_estudiante = (
            EstatusEstudiante.objects
            .filter(estudiante=estudiante)
            .order_by("-fecha_ingreso")
            .first()
        )

        if not estatus_estudiante:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "El estudiante no fue aceptado por el P.N.F"
            })

        if (estatus_estudiante.estado != "Activo" or estatus_estudiante.estatus != "Inscrito(a)"):
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "El estudiante no se encuentra activo o inscrito en el P.N.F"
            })

        # BUSCAR PLAN DE ACTIVIDADES
        planes = (
            PlanActividadAcademica.objects
            .filter(
                pnf_id=id_pnf,
                nucleo_id=id_nucleo,
                materia_asignacion__materia_id=id_materia,
                activo=True,
                estado_aceptacion="ACEPTADA"
            )
            .prefetch_related(
                "detalles__evaluaciones"
            )
            .order_by("fecha_creacion")
        )

        if not planes.exists():
            return JsonResponse({
                "estado": "no_exite",
                "icon": "error",
                "title": "Sin plan de evaluación",
                "descripcion": "No existe un plan de evaluación aceptado para esta materia"
            })

        # CONSTRUIR LAS UNIDADES
        unidades = []
        for plan in planes:
            for detalle in plan.detalles.all():
                evaluaciones = []
                for evaluacion in detalle.evaluaciones.all():
                    evaluaciones.append({
                        "id_evaluacion": evaluacion.id_evaluacion,
                        "metodo_evaluacion": evaluacion.metodo_evaluacion,
                        "fecha_evaluacion": evaluacion.fecha_evaluacion
                    })

                unidades.append({
                    "id_detalle": detalle.id_detalle,
                    "titulo_unidad": detalle.titulo_unidad,
                    "ponderacion": detalle.ponderacion,
                    "contenido_unidad": detalle.contenido_unidad,
                    "evaluaciones": evaluaciones
                })

        return JsonResponse({
            "estado": "exito",
            "trayecto": estatus_estudiante.trayecto,
            "unidades": unidades
        })

def eval_reg_est(request):
    if request.method == "POST":
        cedula = request.session.get("cedula_usuario")
        id_nucleo = request.POST.get("id_nucleo")
        id_pnf = request.POST.get("id_pnf")
        id_materia = request.POST.get("id_materia")

        if not cedula:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "No se encontró la cédula del estudiante"
            })

        if not id_nucleo or not id_pnf or not id_materia:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Debe indicar el núcleo, PNF y materia"
            })

        # BUSCAR ESTUDIANTE
        estudiante = (
            Estudiante.objects
            .filter(
                usuario__cedula_identidad=cedula,
                nucleo_id=id_nucleo,
                pnf_id=id_pnf
            )
            .first()
        )
        if not estudiante:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "El estudiante no está registrado en el núcleo y P.N.F seleccionado"
            })

        # BUSCAR CALIFICACIONES
        calificacion = (
            Calificaciones.objects
            .filter(
                estudiante=estudiante,
                materia_asignada__materia_id=id_materia,
            )
            .prefetch_related(
                "detalles_unidad__unidad"
            )
            .first()
        )

        # TODAVÍA NO TIENE CALIFICACIONES
        if not calificacion:
            return JsonResponse({
                "estado": "exito",
                "registradas": False,
                "evaluaciones": []
            })

        # OBTENER DETALLES DE LAS UNIDADES
        detalles = calificacion.detalles_unidad.all()

        evaluaciones = []
        for detalle in detalles:
            evaluaciones.append({
                "id_detalle": detalle.id_detalle_calificaciones_unidad,
                "id_unidad": detalle.unidad.id_detalle,
                "titulo_unidad": detalle.unidad.titulo_unidad,
                "nota_unidad": detalle.nota_unidad,
                "fecha_calificacion": detalle.fecha_calificacion
            })

        return JsonResponse({
            "estado": "exito",
            "registradas": True,
            "promedio_tramo": calificacion.promedio_tramo,
            "asistencia": calificacion.asistencia,
            "condicion": calificacion.condicion,
            "trayecto": calificacion.trayecto,
            "evaluaciones": evaluaciones
        })

def info_acad_est(request):
    return render(request, "info_academica_estudiante.html")


@transaction.atomic
def calc_prom_est(request):

    PERIODOS_INICIALES = {
        "Inicial Trimestre",
        "Inicial Semestre",
    }

    PERIODOS_TRAMOS = {
        "Tramo I",
        "Tramo II",
        "Tramo III",
    }

    PERIODOS_SEMESTRES = {
        "Semestre I",
        "Semestre II",
    }

    NOTA_MINIMA_NORMAL = Decimal("12")
    NOTA_MINIMA_PROYECTO = Decimal("16")
    ASISTENCIA_MINIMA = 75

    # OBTENER CALIFICACIONES
    calificaciones = (
        Calificaciones.objects
        .select_related(
            "estudiante",
            "materia_asignada__materia",
            "periodo_materia__periodo",
        )
        .all()
    )

    # AGRUPAR
    grupos = {}
    for calificacion in calificaciones:
        if not calificacion.materia_asignada:
            continue
        if not calificacion.periodo_materia:
            continue

        materia = calificacion.materia_asignada.materia

        clave = (
            calificacion.estudiante_id,
            materia.id_materia,
            calificacion.trayecto,
        )

        if clave not in grupos:
            grupos[clave] = {
                "estudiante": calificacion.estudiante,
                "materia": materia,
                "trayecto": calificacion.trayecto,
                "calificaciones": [],
            }

        grupos[clave]["calificaciones"].append(
            calificacion
        )

    cantidad_guardada = 0

    # PROCESAR CADA MATERIA
    for grupo in grupos.values():

        estudiante = grupo["estudiante"]
        materia = grupo["materia"]
        trayecto = grupo["trayecto"]

        calificaciones_materia = grupo["calificaciones"]

        inicial = []
        tramos = []
        semestres = []

        # IDENTIFICAR TIPO DE MATERIA
        nombre_materia = (
            materia.nombre or ""
        ).strip().lower()

        es_proyecto = (
            "proyecto socio tecnologico" in nombre_materia
            or "proyecto socio-tecnologico" in nombre_materia
            or "proyecto sociotecnologico" in nombre_materia
        )

        es_electiva = (
            str(materia.recuperacion).strip().upper() == "NO"
        )

        # SEPARAR PERÍODOS
        for calificacion in calificaciones_materia:
            periodo = (
                calificacion
                .periodo_materia
                .periodo
                .nombre
            )

            if periodo in PERIODOS_INICIALES:
                inicial.append(calificacion)
            elif periodo in PERIODOS_TRAMOS:
                tramos.append(calificacion)
            elif periodo in PERIODOS_SEMESTRES:
                semestres.append(calificacion)

        # CALIFICACIONES QUE SE UTILIZARÁN
        calificaciones_validas = []

        # INICIAL
        if inicial:
            calificaciones_validas = inicial

        # TRAMOS
        elif tramos:
            periodos = {
                c.periodo_materia.periodo.nombre
                for c in tramos
            }

            # PROYECTO Puede tener uno o dos tramos
            if es_proyecto:
                calificaciones_validas = tramos

            # ELECTIVA Se utilizan los períodos registrados
            elif es_electiva:
                calificaciones_validas = tramos

            # MATERIA NORMAL Debe completar los tres tramos
            else:
                if not {
                    "Tramo I",
                    "Tramo II",
                    "Tramo III",
                }.issubset(periodos):

                    continue

                calificaciones_validas = tramos

        # SEMESTRES
        elif semestres:
            periodos = {
                c.periodo_materia.periodo.nombre
                for c in semestres
            }

            # ELECTIVA
            if es_electiva:
                calificaciones_validas = semestres

            # MATERIA NORMAL
            else:
                if not {
                    "Semestre I",
                    "Semestre II",
                }.issubset(periodos):

                    continue

                calificaciones_validas = semestres

        # NO HAY CALIFICACIONES SUFICIENTES
        if not calificaciones_validas:
            continue

        # CALCULAR PROMEDIO
        suma_notas = sum(
            (
                c.promedio_tramo
                for c in calificaciones_validas
            ),
            Decimal("0")
        )
        promedio_final = (
            suma_notas /
            Decimal(len(calificaciones_validas))
        )
        promedio_final = promedio_final.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        # CALCULAR ASISTENCIA
        suma_asistencia = sum(
            c.asistencia
            for c in calificaciones_validas
        )
        asistencia = (
            Decimal(suma_asistencia)
            / Decimal(len(calificaciones_validas))
        )
        asistencia = int(
            asistencia.quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP
            )
        )

        # NOTA MÍNIMA
        if es_proyecto:
            nota_minima = NOTA_MINIMA_PROYECTO
        else:
            nota_minima = NOTA_MINIMA_NORMAL

        # VALIDACIONES
        aprobado_nota = (
            promedio_final >= nota_minima
        )
        aprobado_asistencia = (
            asistencia >= ASISTENCIA_MINIMA
        )
        aprobada = (
            aprobado_nota
            and aprobado_asistencia
        )

        # ESTADO
        estado = (
            "APROBADO"
            if aprobada
            else "REPROBADO"
        )
        # GUARDAR PROMEDIO FINAL
        PromedioFinal.objects.update_or_create(
            estudiante=estudiante,
            materia=materia,
            trayecto=trayecto,
            defaults={
                "promedio_final": promedio_final,
                "estado": estado,
                "fecha_promedio": timezone.localdate(),
            }
        )

        cantidad_guardada += 1

    return JsonResponse({
        "estado": "exito",
        "title": "Éxito",
        "icon": "success",
        "descripcion": (
            f"Se calcularon {cantidad_guardada} "
            "promedios finales."
        ),
        "cantidad": cantidad_guardada,
    })

@transaction.atomic
def act_tray_est(request):

    promedios = (
        PromedioFinal.objects
        .select_related(
            "estudiante",
            "materia",
        )
        .all()
    )

    # ==========================================================
    # AGRUPAR POR ESTUDIANTE + TRAYECTO
    # ==========================================================

    grupos = {}

    for promedio in promedios:

        clave = (
            promedio.estudiante_id,
            promedio.trayecto,
        )

        if clave not in grupos:

            grupos[clave] = {
                "estudiante":
                    promedio.estudiante,

                "trayecto":
                    promedio.trayecto,

                "materias":
                    [],
            }

        grupos[clave]["materias"].append(
            promedio
        )

    actualizados = 0
    egresados = 0
    repiten = 0

    # ==========================================================
    # EVALUAR CADA ESTUDIANTE
    # ==========================================================

    for grupo in grupos.values():

        estudiante = grupo["estudiante"]

        trayecto_actual = (
            grupo["trayecto"]
        )

        materias = grupo["materias"]

        if not materias:
            continue

        # ======================================================
        # CONTADORES
        # ======================================================

        reprobadas_nota = 0

        reprobadas_asistencia = 0

        proyecto_reprobado = False

        # ======================================================
        # ANALIZAR MATERIAS
        # ======================================================

        for promedio in materias:

            materia = promedio.materia

            nombre_materia = (
                materia.nombre or ""
            ).strip().lower()

            # ==================================================
            # IDENTIFICAR PROYECTO
            # ==================================================

            es_proyecto = (
                "proyecto socio tecnologico"
                in nombre_materia
                or
                "proyecto socio-tecnologico"
                in nombre_materia
                or
                "proyecto sociotecnologico"
                in nombre_materia
            )

            # ==================================================
            # NOTA MÍNIMA
            # ==================================================

            if es_proyecto:

                nota_minima = Decimal("16")

            else:

                nota_minima = Decimal("12")

            # ==================================================
            # VALIDAR NOTA
            # ==================================================

            if (
                promedio.promedio_final
                < nota_minima
            ):

                reprobadas_nota += 1

                # ----------------------------------------------
                # PROYECTO REPROBADO
                # ----------------------------------------------

                if es_proyecto:

                    proyecto_reprobado = True

            # ==================================================
            # VALIDAR ASISTENCIA
            # ==================================================

            if promedio.asistencia < 75:

                reprobadas_asistencia += 1

        # ======================================================
        # REGLA PARA REPETIR
        # ======================================================

        no_avanza = False

        # ======================================================
        # PROYECTO SOCIO TECNOLÓGICO REPROBADO
        # ======================================================

        if proyecto_reprobado:

            no_avanza = True

        # ======================================================
        # 3 O MÁS MATERIAS REPROBADAS POR NOTA
        # ======================================================

        elif reprobadas_nota >= 3:

            no_avanza = True

        # ======================================================
        # MÁS DE 3 MATERIAS CON ASISTENCIA INSUFICIENTE
        # ======================================================

        elif reprobadas_asistencia > 3:

            no_avanza = True

        # ======================================================
        # SI REPITE
        # ======================================================

        if no_avanza:

            repiten += 1

            continue

        # ======================================================
        # OBTENER ESTATUS
        # ======================================================

        estatus_estudiante = (
            EstatusEstudiante.objects
            .filter(
                estudiante=estudiante
            )
            .order_by(
                "-id_estatus_estudiante"
            )
            .first()
        )

        if not estatus_estudiante:
            continue

        # ======================================================
        # TRAYECTO IV → EGRESO
        # ======================================================

        if trayecto_actual == "Trayecto IV":

            estatus_estudiante.estatus = (
                "Egreso"
            )

            estatus_estudiante.save(
                update_fields=[
                    "estatus"
                ]
            )

            egresados += 1

            continue

        # ======================================================
        # DETERMINAR SIGUIENTE TRAYECTO
        # ======================================================

        siguiente_trayecto = None

        if trayecto_actual == "Inicial":

            siguiente_trayecto = (
                "Trayecto I"
            )

        elif trayecto_actual == "Trayecto I":

            siguiente_trayecto = (
                "Trayecto II"
            )

        elif trayecto_actual == "Trayecto II":

            siguiente_trayecto = (
                "Trayecto III"
            )

        elif trayecto_actual == "Trayecto III":

            siguiente_trayecto = (
                "Trayecto IV"
            )

        # ======================================================
        # ACTUALIZAR TRAYECTO
        # ======================================================

        if siguiente_trayecto:

            estatus_estudiante.trayecto = (
                siguiente_trayecto
            )

            estatus_estudiante.save(
                update_fields=[
                    "trayecto"
                ]
            )

            actualizados += 1

    # ==========================================================
    # RESPUESTA
    # ==========================================================

    return JsonResponse({

        "estado":
            "exito",

        "title":
            "Éxito",

        "icon":
            "success",

        "descripcion":
            (
                f"Se actualizaron "
                f"{actualizados} trayectos, "
                
                f"y {egresados} pasan a egreso."
            ),

        "cantidad":
            actualizados,

        "repite":
            repiten,

        "egresados":
            egresados,
    })