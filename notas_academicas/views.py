from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Prefetch
from decimal import Decimal, ROUND_DOWN
from django.utils import timezone

from inicio_sesion.models import MateriaAsignada, PeriodoNotasMateria, Pnf, PNFNucleo, Estudiante, EstatusEstudiante, CalendarioCargarNotas, Nucleos, PeriodoCargarNotas, Materia, Docente, DocenteAsignadoMateria

from .models import PlanActividadAcademica, DetallePlanActividades, HistorialDetalleNota, HistorialModificacionNotas, DetallePlanEvaluacion, PromedioFinal, Calificaciones, DetalleCalificacionesUnidad

# Registrar Plan de Actividades

def nucl_asig_doc(request):
    cedula = request.session.get("cedula_usuario")

    nucleos = Nucleos.objects.filter(docente__usuario__cedula_identidad=cedula).distinct()

    datos = [
        {
            "id_nucleo": nucleo.id_nucleo,
            "municipio": nucleo.municipio,
            "direccion": nucleo.direccion,
        }
        for nucleo in nucleos
    ]

    return JsonResponse({
        "estado": "exito",
        "datos": datos
    })

def pnfs_asig_doc(request):
    cedula = request.session.get("cedula_usuario")
    nucleo_asignado = request.POST.get("nucleo_asignado")

    docentes = Docente.objects.filter(usuario__cedula_identidad=cedula, nucleo_id=nucleo_asignado).values_list("pnf_id", flat=True).distinct()

    pnfs = Pnf.objects.filter(id_pnf__in=docentes, pnfnucleo__id_nucleo=nucleo_asignado).distinct()

    datos = [
        {
            "id_pnf": pnf.id_pnf,
            "pnf": pnf.pnf,
            "codigo": pnf.codigo,
            "periodo_academico": pnf.periodo_academico,
        }
        for pnf in pnfs
    ]

    return JsonResponse({
        "estado": "exito",
        "datos": datos
    })

def mat_asig_doc(request):
    id_nucleo = request.POST.get("id_nucleo")
    id_pnf = request.POST.get("id_pnf")
    cedula = request.session.get("cedula_usuario")

    docente = Docente.objects.get(usuario__cedula_identidad=cedula, nucleo_id=id_nucleo, pnf_id=id_pnf)

    planes = (
        PlanActividadAcademica.objects
        .filter(
            pnf_id=id_pnf,
            nucleo_id=id_nucleo,
            activo=True
        )
        .prefetch_related("detalles")
    )

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
        .prefetch_related(
            Prefetch(
                "materia_asignada__planactividadacademica_set",
                queryset=planes,
                to_attr="planes_actividad"
            )
        )
    )

    materias = []
    for asignacion in asignaciones:
        materia_asignada = asignacion.materia_asignada

        planes_materia = getattr(materia_asignada, "planes_actividad", [])

        if planes_materia:
            plan = planes_materia[0]

            if plan.estado_aceptacion == "ACEPTADA": # Ya fue aceptado
                continue

            if len(plan.detalles.all()) >= 6: # Ya tiene las 6 unidades
                continue

        materia = materia_asignada.materia
        seccion = materia_asignada.seccion

        materias.append({
            "id_materia_asignada": materia_asignada.id_materia_asignada,
            "id_materia": materia.id_materia,
            "nombre": materia.nombre,
            "codigo": materia.codigo,
            "trayecto": materia.trayecto,
            "seccion": str(seccion),
            "rol": asignacion.rol,
        })

    return JsonResponse({
        "estado": "exito",
        "datos": materias
    })

def perd_acad_reg(request):
    id_asignacion = request.POST.get("id_asignacion")

    try:
        materia_asignada = MateriaAsignada.objects.select_related("materia").get(id_materia_asignada=id_asignacion)
    except MateriaAsignada.DoesNotExist:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Error",
            "descripcion": "La materia asignada no existe."
        })

    periodos = PeriodoNotasMateria.objects.filter(
        materia=materia_asignada.materia
    ).select_related(
        "periodo"
    ).values(
        "periodo__id_periodo_academico",
        "periodo__nombre"
    ).order_by(
        "periodo__id_periodo_academico"
    )

    resultado = [
        {
            "id_periodo": periodo["periodo__id_periodo_academico"],
            "nombre": periodo["periodo__nombre"]
        }
        for periodo in periodos
    ]

    return JsonResponse({
        "estado": "exito",
        "periodos": resultado
    })

def cant_und_reg(request):
    id_asignacion = request.POST.get("id_asignacion")

    plan = (
        PlanActividadAcademica.objects
        .filter(
            materia_asignacion_id=id_asignacion,
            activo=True
        )
        .first()
    )

    if not plan:
        return JsonResponse({
            "estado": "ok",
            "existe_plan": False,
            "cantidad": 0,
            "puede_enviar": False
        })

    cantidad = plan.detalles.count()

    return JsonResponse({
        "estado": "ok",
        "existe_plan": True,
        "id_plan": plan.id_plan,
        "cantidad": cantidad,
        "puede_enviar": 4 <= cantidad <= 6
    })

def reg_pl_act(request):
    if request.method == "POST":
        materia_asignacion = request.POST.get("asignacion_materia")
        periodo_academico = request.POST.get("periodo_academico")
        titulo_unidad = request.POST.get("titulo_unidad")
        contenido_unidad = request.POST.get("contenido_unidad")

        cantidad_evaluaciones = int(request.POST.get("cantidad_evaluaciones", 0))

        controles = [
            (materia_asignacion, "Materia Asignada", "Por favor, selecciona una materia."),
            (periodo_academico, "Periodo Académico", "Por favor, selecciona una periodo académico."),
            (titulo_unidad, "Titulo de la Unidad", "Por favor, ingresa el titulo de la unidad."),
            (contenido_unidad, "Contenido de la Unidad", "Por favor, ingresa el contenido de la unidad."),
            (cantidad_evaluaciones, "Cantidad Evaluaciones", "Por favor, ingresa la cantidad de evaluaciones."),
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })

        evaluaciones = []
        for i in range(1, cantidad_evaluaciones + 1):
            metodo_evaluacion = request.POST.get(f"metodo_evaluacion_{i}", "").strip()
            fecha_evaluacion = request.POST.get(f"fecha_evaluacion_{i}", "").strip()

            if not metodo_evaluacion:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": "Método de Evaluación",
                    "descripcion": f"El método de evaluación {i} no puede estar vacío."
                })

            if not fecha_evaluacion:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": "Fecha de Evaluación",
                    "descripcion": f"La fecha de evaluación {i} no puede estar vacía."
                })

            evaluaciones.append({
                "metodo_evaluacion": metodo_evaluacion,
                "fecha_evaluacion": fecha_evaluacion
            })

        docente = Docente.objects.get(usuario__cedula_identidad=request.session.get("cedula_usuario"))

        try:
            asignacion = MateriaAsignada.objects.get(pk=materia_asignacion)
        except MateriaAsignada.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "La materia asignada no se encuentra registrado."
            })
        
        try:
            periodo = PeriodoCargarNotas.objects.get(pk=periodo_academico)
        except PeriodoCargarNotas.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "El periodo acadèmico no se encuentra registrado."
            })

        estado = "BORRADOR"
        try:
            with transaction.atomic():
                plan_actividad, creado = PlanActividadAcademica.objects.get_or_create(
                    pnf=docente.pnf,
                    nucleo=docente.nucleo,
                    materia_asignacion=asignacion,
                    periodo_academico=periodo,
                    activo=True,
                    estado_aceptacion=estado
                )
    
                detalleactividades = DetallePlanActividades.objects.create(
                    plan_academico=plan_actividad,
                    titulo_unidad=titulo_unidad,
                    contenido_unidad=contenido_unidad,
                    ponderacion=Decimal("0.00")
                )

                # Cantidad total de unidades registradas
                unidades = DetallePlanActividades.objects.filter(plan_academico=plan_actividad)

                cantidad_unidades = unidades.count()

                # Calcular ponderación
                ponderacion = (
                    Decimal("100.00") / Decimal(cantidad_unidades)
                ).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_DOWN
                )

                # Actualizar todas las unidades
                unidades.update(
                    ponderacion=ponderacion
                )
    
                for evaluacion in evaluaciones:
                    DetallePlanEvaluacion.objects.create(
                        detalle_plan=detalleactividades,
                        metodo_evaluacion=evaluacion["metodo_evaluacion"],
                        fecha_evaluacion=evaluacion["fecha_evaluacion"]
                    )

                return JsonResponse({
                    "estado": "exito",
                    "icon": "success",
                    "title": "Exito",
                    "descripcion": "Se reguistro exitosamente los datos del plan de actividades."
                })
            
        except Exception as e:
            print("ERROR:", e)

            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Ocurrio un error al momento de registrar el plan de actividades."
            })

    return render(request, "registrar_plan_actividad.html")  

# Visualizar Plan de Actividades

def vis_plan_est(request):
    return render(request, "visualizar_plan_academico.html")

def pl_reg(request):
    docente = Docente.objects.get(
        usuario__cedula_identidad=request.session.get("cedula_usuario")
    )

    # Materias que pertenecen a este docente
    materias_docente = DocenteAsignadoMateria.objects.filter(
        docente=docente,
        activo=True
    ).values_list(
        "materia_asignada_id",
        flat=True
    )

    # Planes únicamente de las materias asignadas a este docente
    planes = PlanActividadAcademica.objects.filter(
        materia_asignacion_id__in=materias_docente,
        nucleo=docente.nucleo,
        pnf=docente.pnf,
        activo=True
    ).select_related(
        "materia_asignacion__materia"
    )

    datos = []

    for plan in planes:
        datos.append({
            "id_plan": plan.id_plan,
            "materia": plan.materia_asignacion.materia.nombre,
            "observacion": plan.observacion,
            "estado_aceptacion": plan.estado_aceptacion,
            "estado_aceptacion_display": plan.get_estado_aceptacion_display(),
            "cantidad_unidades": plan.detalles.count(),
        })

    return JsonResponse({"datos": datos})

def datos_pl_reg(request):
    if request.method == "POST":
        id_plan = request.POST.get("id_plan")

        plan = PlanActividadAcademica.objects.select_related(
            "pnf",
            "nucleo",
            "materia_asignacion__materia",
            "periodo_academico",
        ).prefetch_related(
            "detalles__evaluaciones"
        ).get(
            id_plan=id_plan,
            activo=True
        )

        datos = {
            "id_plan": plan.id_plan,

            # Plan
            "pnf": plan.pnf.pnf,
            "nucleo": plan.nucleo.municipio,
            "materia": plan.materia_asignacion.materia.nombre,
            "periodo_academico": plan.periodo_academico.nombre,

            "fecha_creacion": plan.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
            "fecha_actualizacion": plan.fecha_actualizacion.strftime("%d/%m/%Y %H:%M"),

            "estado_aceptacion": plan.estado_aceptacion,
            "estado_aceptacion_display": plan.get_estado_aceptacion_display(),

            # Unidades
            "detalles": []
        }

        for detalle in plan.detalles.all():
            datos["detalles"].append({
                "id_detalle": detalle.id_detalle,
                "titulo_unidad": detalle.titulo_unidad,
                "ponderacion": str(detalle.ponderacion),
                "contenido_unidad": detalle.contenido_unidad,

                # Evaluaciones
                "evaluaciones": [
                    {
                        "id_evaluacion": evaluacion.id_evaluacion,
                        "metodo_evaluacion": evaluacion.metodo_evaluacion,
                        "fecha_evaluacion": evaluacion.fecha_evaluacion.strftime("%Y-%m-%d"),
                    }
                    for evaluacion in detalle.evaluaciones.all()
                ]
            })

        return JsonResponse({ "datos": datos })

def env_pla(request):
    if request.method == "POST":
        id_plan = request.POST.get("id_plan")

        try:
            with transaction.atomic():
                plan_actividad = PlanActividadAcademica.objects.get(id_plan=id_plan)
                plan_actividad.estado_aceptacion = "ENVIADO"
                plan_actividad.save()

                return JsonResponse({
                    "estado": "exito",
                    "icon": "success",
                    "title": "Éxito",
                    "descripcion": "Se registró exitosamente el envío del plan de actividades."
                })

        except Exception as e:
            print("ERROR:", e)

            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Ocurrió un error al momento de enviar el plan de actividades."
            })

def act_pl_reg(request):
    if request.method == "POST":
        id_plan = request.POST.get("id_plan")

        try:
            plan = PlanActividadAcademica.objects.get(id_plan=id_plan)
        except PlanActividadAcademica.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "No se encuentra registrado el Plan de Actividades Académicas."
            })

        try:
            with transaction.atomic():
                evaluaciones_eliminar = request.POST.getlist("eliminar_evaluacion[]")
                if evaluaciones_eliminar:
                    DetallePlanEvaluacion.objects.filter(
                        id_evaluacion__in=evaluaciones_eliminar,
                        detalle_plan__plan_academico=plan
                    ).delete()


                for clave, valor in request.POST.items():
                    if not clave.startswith("id_detalle_"):
                        continue

                    i = clave.replace(
                        "id_detalle_",
                        ""
                    )

                    id_detalle = valor
                    titulo_unidad = request.POST.get(
                        f"titulo_unidad_{i}"
                    )

                    contenido_unidad = request.POST.get(
                        f"contenido_unidad_{i}"
                    )


                    if not titulo_unidad or not titulo_unidad.strip():
                        return JsonResponse({
                            "estado": "fallo",
                            "icon": "error",
                            "title": "Título de unidad requerido",
                            "descripcion": "Debe registrar el título de la unidad."
                        })

                    if not contenido_unidad or not contenido_unidad.strip():
                        return JsonResponse({
                            "estado": "fallo",
                            "icon": "error",
                            "title": "Contenido de unidad requerido",
                            "descripcion": "Debe registrar el contenido correspondiente a la unidad."
                        })

                    try:
                        detalle = DetallePlanActividades.objects.get(
                            id_detalle=id_detalle,
                            plan_academico=plan
                        )
                    except DetallePlanActividades.DoesNotExist:
                        return JsonResponse({
                            "estado": "fallo",
                            "icon": "error",
                            "title": "Unidad no encontrada",
                            "descripcion": "La unidad de actividad académica que intenta modificar no se encuentra registrada en este plan."
                        })
                    
                    detalle.titulo_unidad = titulo_unidad.strip()
                    detalle.contenido_unidad = contenido_unidad.strip()
                    detalle.save(
                        update_fields=[
                            "titulo_unidad",
                            "contenido_unidad"
                        ]
                    )

                    prefijo = f"metodo_evaluacion_{i}_"

                    for clave_evaluacion in request.POST.keys():

                        if not clave_evaluacion.startswith(prefijo):
                            continue


                        j = clave_evaluacion.replace(
                            prefijo,
                            ""
                        )


                        id_evaluacion = request.POST.get(
                            f"id_evaluacion_{i}_{j}"
                        )


                        metodo_evaluacion = request.POST.get(
                            f"metodo_evaluacion_{i}_{j}"
                        )


                        fecha_evaluacion = request.POST.get(
                            f"fecha_evaluacion_{i}_{j}"
                        )


                        if not metodo_evaluacion or not metodo_evaluacion.strip():

                            return JsonResponse({
                                "estado": "fallo",
                                "icon": "error",
                                "title": "Error",
                                "descripcion": (
                                    f"El método de evaluación "
                                    f"{int(j) + 1} es obligatorio."
                                )
                            })


                        if not fecha_evaluacion or not fecha_evaluacion.strip():

                            return JsonResponse({
                                "estado": "fallo",
                                "icon": "error",
                                "title": "Error",
                                "descripcion": (
                                    f"La fecha de evaluación "
                                    f"{int(j) + 1} es obligatoria."
                                )
                            })


                        # ==========================================
                        # EVALUACIÓN EXISTENTE
                        # ==========================================

                        if id_evaluacion:

                            if id_evaluacion in evaluaciones_eliminar:
                                continue


                            try:

                                evaluacion = DetallePlanEvaluacion.objects.get(
                                    id_evaluacion=id_evaluacion,
                                    detalle_plan=detalle
                                )

                            except DetallePlanEvaluacion.DoesNotExist:

                                return JsonResponse({
                                    "estado": "fallo",
                                    "icon": "error",
                                    "title": "Error",
                                    "descripcion": (
                                        "No se encuentra registrada "
                                        "la evaluación."
                                    )
                                })


                            evaluacion.metodo_evaluacion = (
                                metodo_evaluacion.strip()
                            )

                            evaluacion.fecha_evaluacion = (
                                fecha_evaluacion
                            )


                            evaluacion.save(
                                update_fields=[
                                    "metodo_evaluacion",
                                    "fecha_evaluacion"
                                ]
                            )


                        # ==========================================
                        # EVALUACIÓN NUEVA
                        # ==========================================

                        else:

                            DetallePlanEvaluacion.objects.create(
                                detalle_plan=detalle,
                                metodo_evaluacion=(
                                    metodo_evaluacion.strip()
                                ),
                                fecha_evaluacion=fecha_evaluacion
                            )
                plan.save()

            return JsonResponse({
                "estado": "exito",
                "icon": "success",
                "title": "Actualizado",
                "descripcion": (
                    "El Plan de Actividades Académicas "
                    "fue actualizado correctamente."
                )
            })

        except Exception as error:
            print("ERROR ACTUALIZANDO PLAN:", error)

            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": (
                    "Ocurrió un error al actualizar "
                    "el Plan de Actividades Académicas."
                )
            })

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
                "datos": [],
                "descripcion": "La materia no tiene un período de carga habilitado actualmente."
            })

        # ---------------------------------------------------------
        # PERÍODOS YA REGISTRADOS ESTE AÑO
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # BUSCAR EL PERÍODO PENDIENTE
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # RESPUESTA
        # ---------------------------------------------------------

        return JsonResponse({
            "estado": "exito",
            "datos": datos
        })

def cant_det_pla(request):
    if request.method == "POST":
        nucleo = request.POST.get("id_nucleo")
        pnf = request.POST.get("id_pnf")
        materia_asignada = request.POST.get("id_materia_asignada")

        cantidad_actividades = DetallePlanActividades.objects.filter(
            plan_academico__materia_asignacion_id=materia_asignada,
            plan_academico__pnf_id=pnf,
            plan_academico__nucleo_id=nucleo,
            plan_academico__activo=True
        ).count()

        return JsonResponse({
            "estado": "exito",
            "cantidad_actividades": cantidad_actividades
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

        cantidad_evaluaciones = request.POST.get("cantidad_evaluaciones")

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

        try:
            periodo = PeriodoNotasMateria.objects.get(
                id=periodo_academico
            )
        except PeriodoNotasMateria.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Ocurrió un error en el modelo intermedio (Periodo Notas Materia)."
            })

        try:
            materia_asignacion = MateriaAsignada.objects.get(
                id_materia_asignada=materia_asignada
            )
        except MateriaAsignada.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Ocurrió un error en el modelo intermedio (Materia Asignación)."
            })

        plan = PlanActividadAcademica.objects.filter(
            materia_asignacion=materia_asignacion,
            pnf_id=pnf_asignado,
            nucleo_id=nucleo_asignado,
            activo=True,
            estado_aceptacion="ACEPTADA"
        ).first()

        if not plan:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Plan académico",
                "descripcion": "No se encuentra registrado un plan de actividad académica aceptado para la materia."
            })

        unidades = list(plan.detalles.all().order_by("id_detalle"))
        if not unidades:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Unidades académicas",
                "descripcion": "El plan de actividad académica no tiene unidades registradas."
            })

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
            notas_estudiante = calificaciones.get(
                id_estudiante,
                {}
            )

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

        fechas = (
            Calificaciones.objects
            .filter(materia_asignada_id=materia_asignada)
            .values_list("fecha_promedio", flat=True)
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

# Visualizar Notas Académicas

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

@transaction.atomic
def mod_not_acad(request):
    if request.method == "POST":
        nucleo_asignado = request.POST.get("nucleo_asignado")
        pnf_asignado = request.POST.get("pnf_asignado")
        materia_asignada = request.POST.get("materia_asignada")
        periodo_academico = request.POST.get("id_periodo_academico")
        nombre_periodo_academico = request.POST.get("periodo_academico")
        trayecto_academico = request.POST.get("trayecto_academico")

        cedula = request.session.get("cedula_usuario")

        calificaciones = {}
        asistencias = {}
        promedios = {}
        for nombre_campo, valor in request.POST.items():
            # CALIFICACIONES
            if nombre_campo.startswith("calificacion_"):
                partes = nombre_campo.split("_")
                id_estudiante = partes[1]
                numero_unidad = partes[2]
                calificaciones.setdefault(id_estudiante, {})
                calificaciones[id_estudiante][numero_unidad] = valor

            # ASISTENCIA
            elif nombre_campo.startswith("asistencia_"):
                id_estudiante = nombre_campo.split("_")[1]
                asistencias[id_estudiante] = valor

            # PROMEDIO
            elif nombre_campo.startswith("promedio_"):
                id_estudiante = nombre_campo.split("_")[1]
                promedios[id_estudiante] = valor

            for nombre_campo, valor in request.POST.items():
                valor = valor.strip()

                # CALIFICACIONES
                if nombre_campo.startswith("calificacion_"):
                    partes = nombre_campo.split("_")
                    id_estudiante = partes[1]
                    numero_unidad = partes[2]

                    if not valor:
                        return JsonResponse({
                            "estado": "error",
                            "icon": "warning",
                            "title": "Campos vacíos",
                            "descripcion": (
                                f"La calificación de la unidad {numero_unidad} "
                                f"del estudiante {id_estudiante} está vacía."
                            )
                        })

                    calificaciones.setdefault(id_estudiante, {})
                    calificaciones[id_estudiante][numero_unidad] = valor

                # ASISTENCIA
                elif nombre_campo.startswith("asistencia_"):
                    id_estudiante = nombre_campo.split("_")[1]
                    if not valor:
                        return JsonResponse({
                            "estado": "error",
                            "icon": "warning",
                            "title": "Campo vacío",
                            "descripcion": (
                                f"La asistencia del estudiante "
                                f"{id_estudiante} está vacía."
                            )
                        })

                    asistencias[id_estudiante] = valor

                # PROMEDIO
                elif nombre_campo.startswith("promedio_"):
                    id_estudiante = nombre_campo.split("_")[1]
                    if not valor:
                        return JsonResponse({
                            "estado": "error",
                            "icon": "warning",
                            "title": "Campo vacío",
                            "descripcion": (
                                f"El promedio del estudiante "
                                f"{id_estudiante} está vacío."
                            )
                        })

                    promedios[id_estudiante] = valor

        # PERIODO
        try:
            periodo = PeriodoNotasMateria.objects.get(id=periodo_academico)
        except PeriodoNotasMateria.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Ocurrió un error en el modelo intermedio (Periodo Notas Materia)."
            })

        # MATERIA ASIGNADA
        try:
            materia_asignacion = MateriaAsignada.objects.get(id_materia_asignada=materia_asignada)
        except MateriaAsignada.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Ocurrió un error en el modelo intermedio (Materia Asignación)."
            })

        # PLAN DE ACTIVIDAD ACADÉMICA
        plan = PlanActividadAcademica.objects.filter(
            materia_asignacion=materia_asignacion,
            pnf_id=pnf_asignado,
            nucleo_id=nucleo_asignado,
            activo=True,
            estado_aceptacion="ACEPTADA"
        ).first()

        if not plan:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Plan académico",
                "descripcion": "No se encuentra registrado un plan de actividad académica aceptado para la materia."
            })

        # UNIDADES DEL PLAN
        unidades = list(plan.detalles.all().order_by("id_detalle"))
        if not unidades:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Unidades académicas",
                "descripcion": "El plan de actividad académica no tiene unidades registradas."
            })
        
        # VALIDAR QUE EXISTAN ESTUDIANTES
        ids_estudiantes = set(calificaciones.keys())
        if not ids_estudiantes:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Sin calificaciones",
                "descripcion": "No se encontraron calificaciones para actualizar."
            })

        # ACTUALIZAR NOTAS DE LAS UNIDADES
        for id_estudiante in ids_estudiantes:

            # VALIDAR ESTUDIANTE
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
                    "descripcion": (
                        f"No se encontró el estudiante "
                        f"{id_estudiante}."
                    )
                })

            # BUSCAR CALIFICACIÓN EXISTENTE
            try:
                calificacion = Calificaciones.objects.get(
                    periodo_materia=periodo,
                    materia_asignada=materia_asignacion,
                    estudiante=estudiante,
                    trayecto=trayecto_academico
                )
            except Calificaciones.DoesNotExist:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Calificación no encontrada",
                    "descripcion": (
                        f"No existe un registro de calificaciones "
                        f"para el estudiante {id_estudiante}."
                    )
                })
            except Calificaciones.MultipleObjectsReturned:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Error",
                    "descripcion": (
                        f"Existen múltiples registros de calificaciones "
                        f"para el estudiante {id_estudiante}."
                    )
                })

            # ACTUALIZAR CONDICIÓN
            valor_promedio = promedios.get(id_estudiante, "0")

            try:
                promedio = Decimal(
                    str(valor_promedio).replace(",", ".")
                )
            except (ValueError, TypeError):
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "Promedio inválido",
                    "descripcion": (
                        f"El promedio del estudiante "
                        f"{id_estudiante} no es válido."
                    )
                })

            try:
                asistencia = int(
                    asistencias.get(id_estudiante, 0)
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

            # DETERMINAR CONDICIÓN
            nombre_materia = (
                materia_asignacion.materia.nombre
                .strip()
                .lower()
            )

            if asistencia >= 75:
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

            # MODIFICAR ÚNICAMENTE CONDICIÓN
            calificacion.condicion = condicion
            calificacion.save(update_fields=["condicion"])

            # NOTAS DE LAS UNIDADES
            notas_estudiante = calificaciones.get(
                id_estudiante,
                {}
            )

            for numero_unidad, nota in notas_estudiante.items():
                if nota == "":
                    continue

                # VALIDAR NÚMERO DE UNIDAD
                try:
                    numero_unidad = int(numero_unidad)
                except (ValueError, TypeError):
                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "error",
                        "title": "Unidad inválida",
                        "descripcion": (
                            f"La unidad recibida para el estudiante "
                            f"{id_estudiante} no es válida."
                        )
                    })

                # VALIDAR QUE EXISTA EN EL PLAN
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

                # CONVERTIR NOTA
                try:
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

                # OBTENER UNIDAD DEL PLAN
                unidad = unidades[numero_unidad - 1]

                # BUSCAR DETALLE EXISTENTE
                try:
                    detalle_calificacion = (
                        DetalleCalificacionesUnidad.objects.get(
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
                            f"No existe el detalle de calificación "
                            f"de la unidad {numero_unidad} para "
                            f"el estudiante {id_estudiante}."
                        )
                    })

                # ACTUALIZAR NOTA DE LA UNIDAD
                detalle_calificacion.nota_unidad = nota_unidad
                detalle_calificacion.save(
                    update_fields=["nota_unidad"]
                )

            # RECALCULAR PROMEDIO
            detalles_unidades = (
                DetalleCalificacionesUnidad.objects.filter(
                    calificacion=calificacion
                )
            )

            notas_validas = [
                detalle.nota_unidad
                for detalle in detalles_unidades
                if detalle.nota_unidad is not None
            ]

            if not notas_validas:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": "Sin notas",
                    "descripcion": (
                        f"No existen notas registradas para "
                        f"el estudiante {id_estudiante}."
                    )
                })

            # CALCULAR NUEVO PROMEDIO
            promedio = (
                sum(notas_validas, Decimal("0"))
                / Decimal(len(notas_validas))
            ).quantize(
                Decimal("0.01")
            )

            # GUARDAR PROMEDIO
            calificacion.promedio_tramo = promedio
            calificacion.save(
                update_fields=["promedio_tramo"]
            )

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Exito",
            "descripcion": "Se registraron las notas académicas exitosamente."
        }) 

    return render(request, "modificar_notas_academicas.html")

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
                ingreso="Inscrito(a)"
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

        if (estatus_estudiante.estado.upper() != "Activo" or estatus_estudiante.ingreso.upper() != "Inscrito(a)"):
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
                "estado": "fallo",
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
                materia_asignada__seccion__nucleo_id=id_nucleo
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