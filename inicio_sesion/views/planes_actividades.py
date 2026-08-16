from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone

from inicio_sesion.models import CoordinadorPNF
from notas_academicas.models import PlanActividadAcademica, DetallePlanActividades, DetallePlanEvaluacion

def pnf_asig_coord(request):
    coordinadores = CoordinadorPNF.objects.filter(usuario__cedula_identidad=request.session.get("cedula_usuario")
    ).select_related("pnf")

    pnfs = []
    for coordinador in coordinadores:
        pnfs.append({
            "id_pnf": coordinador.pnf.id_pnf,
            "pnf": coordinador.pnf.pnf,
        })

    return JsonResponse({ "pnfs": pnfs })

def pl_reg_coord_pnf(request):
    if request.method == "POST":
        id_pnf = request.POST.get("pnf_asignado")
        if not id_pnf:
            return JsonResponse({
                "datos": []
            })
    
        cedula = request.session.get("cedula_usuario")
    
        coordinador = CoordinadorPNF.objects.filter(usuario__cedula_identidad=cedula, pnf_id=id_pnf
        ).select_related("pnf", "nucleo").first()
    
        planes = PlanActividadAcademica.objects.filter(pnf=coordinador.pnf, nucleo=coordinador.nucleo,
            estado_aceptacion="ENVIADO"
        ).select_related(
            "pnf", "nucleo", "materia_asignacion__materia", "periodo_academico"
        ).order_by("-fecha_creacion")
    
        datos = []
        for plan in planes:
            datos.append({
                "id_plan": plan.id_plan,
                "pnf": plan.pnf.pnf,
                "nucleo": plan.nucleo.municipio,
                "materia": plan.materia_asignacion.materia.nombre,
                "periodo_academico": str(plan.periodo_academico),
                "cantidad_unidades": plan.detalles.count(),
                "fecha_creacion": plan.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
                "fecha_actualizacion": plan.fecha_actualizacion.strftime("%d/%m/%Y %H:%M"),
            })
    
        return JsonResponse({ "datos": datos })

def datos_pl_reg_coord_pnf(request):
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

        # Docente activo de la materia
        docente_asignado = plan.materia_asignacion.docentes.filter(
            activo=True
        ).select_related("docente").first()

        datos = {
            "id_plan": plan.id_plan,

            # Plan
            "pnf": plan.pnf.pnf,
            "nucleo": plan.nucleo.municipio,
            "materia": plan.materia_asignacion.materia.nombre,
            "periodo_academico": plan.periodo_academico.nombre,

            # Docente
            "docente": (
                f"{docente_asignado.docente.usuario.nombres} "
                f"{docente_asignado.docente.usuario.apellidos}"
                if docente_asignado
                else None
            ),

            "cedula_docente": (
                docente_asignado.docente.usuario.cedula_identidad
                if docente_asignado
                else None
            ),

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

        return JsonResponse({"datos": datos})

def vis_pl_env(request):
    return render(request, "Coordinador_PNF/planes_actividades/visualizar_planes_actvidades.html")

def camb_est_pl(request):
    if request.method == "POST":

        id_plan = request.POST.get("id_plan")
        estado = request.POST.get("estado")
        observacion = request.POST.get("observacion")

        try:
            plan = PlanActividadAcademica.objects.get(
                id_plan=id_plan
            )

        except PlanActividadAcademica.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Plan de Actividades",
                "descripcion": "No se encuentra registrado el plan de actividades."
            })

        try:

            plan.estado_aceptacion = estado
            plan.observacion = observacion
            plan.save()

            return JsonResponse({
                "estado": "exito",
                "icon": "success",
                "title": "Plan de Actividades",
                "descripcion": (
                    f"El plan ha sido marcado como {estado.lower()}."
                )
            })

        except Exception:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Plan de Actividades",
                "descripcion": (
                    "Ocurrió un error al momento de actualizar "
                    "el estado del plan de actividades."
                )
            })

        