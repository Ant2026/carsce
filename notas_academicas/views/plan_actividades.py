from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Prefetch
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from django.utils import timezone
from django.db.models import Exists, OuterRef

from inicio_sesion.models import MateriaAsignada, PeriodoNotasMateria, Usuario, Pnf, PNFNucleo, Estudiante, EstatusEstudiante, CalendarioCargarNotas, Nucleos, PeriodoCargarNotas, Materia, Docente, DocenteAsignadoMateria

from notas_academicas.models import PlanActividadAcademica, DetallePlanActividades, HistorialTrayectoEstudiante, HistorialDetalleNota, HistorialModificacionNotas, DetallePlanEvaluacion, PromedioFinal, Calificaciones, DetalleCalificacionesUnidad

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

    docente = Docente.objects.get(
        usuario__cedula_identidad=cedula,
        nucleo_id=id_nucleo,
        pnf_id=id_pnf
    )

    # ==========================================================
    # PLANES ACADÉMICOS DEL NÚCLEO Y PNF
    # ==========================================================

    planes = (
        PlanActividadAcademica.objects
        .filter(
            pnf_id=id_pnf,
            nucleo_id=id_nucleo,
            activo=True
        )
        .prefetch_related("detalles")
    )

    # ==========================================================
    # ASIGNACIONES DEL DOCENTE
    # ==========================================================

    asignaciones = (
        DocenteAsignadoMateria.objects
        .filter(
            docente=docente,
            activo=True,
            materia_asignada__activo=True
        )
        .select_related(
            "materia_asignada__materia"
        )
        .prefetch_related(
            Prefetch(
                "materia_asignada__materia__periodonotasmateria_set",
                queryset=PeriodoNotasMateria.objects.select_related(
                    "periodo"
                ),
                to_attr="periodos_notas"
            ),
            Prefetch(
                "materia_asignada__planactividadacademica_set",
                queryset=planes,
                to_attr="planes_actividad"
            )
        )
    )

    materias = []

    # ==========================================================
    # RECORRER MATERIAS
    # ==========================================================

    for asignacion in asignaciones:

        materia_asignada = asignacion.materia_asignada
        materia = materia_asignada.materia

        periodos_materia = getattr(
            materia,
            "periodos_notas",
            []
        )

        planes_materia = getattr(
            materia_asignada,
            "planes_actividad",
            []
        )

        # ======================================================
        # REVISAR CADA PERÍODO DE LA MATERIA
        # ======================================================

        for periodo_materia in periodos_materia:

            periodo = periodo_materia.periodo

            # --------------------------------------------------
            # BUSCAR EL PLAN DE ESTE PERÍODO
            # --------------------------------------------------

            plan_periodo = next(
                (
                    plan
                    for plan in planes_materia
                    if plan.periodo_academico_id ==
                       periodo.id_periodo_academico
                ),
                None
            )

            # --------------------------------------------------
            # NO EXISTE PLAN PARA ESTE PERÍODO
            # --------------------------------------------------

            if plan_periodo is None:

                materias.append({
                    "id_materia_asignada":
                        materia_asignada.id_materia_asignada,

                    "id_materia":
                        materia.id_materia,

                    "nombre":
                        materia.nombre,

                    "codigo":
                        materia.codigo,

                    "trayecto":
                        materia.trayecto,

                    "periodo":
                        periodo.nombre,

                    "id_periodo":
                        periodo.id_periodo_academico,

                    "rol":
                        asignacion.rol,
                })

                continue

            # --------------------------------------------------
            # EL PLAN YA FUE ACEPTADO
            # --------------------------------------------------

            if plan_periodo.estado_aceptacion == "ACEPTADA":
                continue

            # --------------------------------------------------
            # EL PLAN YA TIENE LAS 6 UNIDADES
            # --------------------------------------------------

            if plan_periodo.detalles.count() >= 6:
                continue

            # --------------------------------------------------
            # PLAN EN BORRADOR / ENVIADO / DENEGADO
            # --------------------------------------------------

            materias.append({
                "id_materia_asignada":
                    materia_asignada.id_materia_asignada,

                "id_materia":
                    materia.id_materia,

                "nombre":
                    materia.nombre,

                "codigo":
                    materia.codigo,

                "trayecto":
                    materia.trayecto,

                "periodo":
                    periodo.nombre,

                "id_periodo":
                    periodo.id_periodo_academico,

                "rol":
                    asignacion.rol,
            })

    return JsonResponse({
        "estado": "exito",
        "datos": materias
    })

def perd_acad_reg(request):
    id_asignacion = request.POST.get("id_asignacion")

    try:
        materia_asignada = (
            MateriaAsignada.objects
            .select_related("materia")
            .get(id_materia_asignada=id_asignacion)
        )

    except MateriaAsignada.DoesNotExist:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Error",
            "descripcion": "La materia asignada no existe."
        })

    # ==========================================================
    # PLAN ACEPTADO PARA EL PERÍODO
    # ==========================================================

    plan_aceptado = PlanActividadAcademica.objects.filter(
        materia_asignacion=materia_asignada,
        periodo_academico=OuterRef("periodo"),
        activo=True,
        estado_aceptacion="ACEPTADA"
    )

    # ==========================================================
    # PERÍODOS DE LA MATERIA
    # ==========================================================

    periodos = (
        PeriodoNotasMateria.objects
        .filter(
            materia=materia_asignada.materia
        )
        .select_related("periodo")
        .annotate(
            plan_aceptado=Exists(plan_aceptado)
        )
        .filter(
            plan_aceptado=False
        )
        .values(
            "periodo__id_periodo_academico",
            "periodo__nombre"
        )
        .order_by(
            "periodo__id_periodo_academico"
        )
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
    id_periodo_academico = request.POST.get("id_periodo_academico")

    if not id_asignacion or not id_periodo_academico:
        return JsonResponse({
            "estado": "fallo",
            "existe_plan": False,
            "cantidad": 0,
            "puede_enviar": False,
            "descripcion": "Debe indicar la materia y el período académico."
        })

    plan = (
        PlanActividadAcademica.objects
        .filter(
            materia_asignacion_id=id_asignacion,
            periodo_academico_id=id_periodo_academico,
            activo=True
        )
        .prefetch_related("detalles")
        .first()
    )

    # ==========================================================
    # NO EXISTE PLAN PARA ESTE PERÍODO
    # ==========================================================

    if not plan:
        return JsonResponse({
            "estado": "exito",
            "existe_plan": False,
            "cantidad": 0,
            "puede_enviar": False
        })

    # ==========================================================
    # CANTIDAD DE UNIDADES DEL PLAN
    # ==========================================================

    cantidad = plan.detalles.count()

    # ==========================================================
    # VALIDAR SI PUEDE ENVIARSE
    # ==========================================================

    puede_enviar = (
        4 <= cantidad <= 6
        and plan.estado_aceptacion in [
            "BORRADOR",
            "DENEGADA"
        ]
    )

    return JsonResponse({
        "estado": "exito",
        "existe_plan": True,
        "id_plan": plan.id_plan,
        "id_periodo_academico": plan.periodo_academico_id,
        "periodo": plan.periodo_academico.nombre,
        "cantidad": cantidad,
        "estado_aceptacion": plan.estado_aceptacion,
        "puede_enviar": puede_enviar
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
