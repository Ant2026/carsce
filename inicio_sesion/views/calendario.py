from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db import transaction

from inicio_sesion.models import PeriodoAcademico, CalendarioAcademico, PeriodoMateria, CalendarioMateria

def periodos_academicos(request):
    periodos = list(
        PeriodoAcademico.objects.values(
            "id_periodo_academico",
            "nombre"
        )
    )

    return JsonResponse({
        "estado": "exito",
        "periodos": periodos
    })

def calendarios_registrados(request):
    calendarios = list(
        CalendarioAcademico.objects.values(
            "id_fecha_academica",
            "periodo_id",
            "periodo__nombre",
            "fecha_inicio",
            "fecha_final"
        )
    )

    return JsonResponse({
        "estado": "exito",
        "calendarios": calendarios
    })

def datos_calendario(request):
    if request.method == "POST":
        id_calendario = request.POST.get("id_calendario")

        try:
            cal = CalendarioAcademico.objects.select_related("periodo").get(
                id_fecha_academica=id_calendario
            )

            return JsonResponse({
                "estado": "exito",
                "calendario": {
                    "id": cal.id_fecha_academica,
                    "periodo_id": cal.periodo.id_periodo_academico,
                    "periodo": cal.periodo.nombre,
                    "inicio": cal.fecha_inicio,
                    "final": cal.fecha_final
                }
            })

        except CalendarioAcademico.DoesNotExist:
            return JsonResponse({
                "estado": "error",
                "icon": "error",
                "descripcion": "No se encuentra registrado el calendario académico."
            })

def guardar_actualizar_calendario(request):
    if request.method == "POST":

        id_calendario = request.POST.get("fechaseleccionado")
        periodo = request.POST.get("actualizar_fecha_academica")
        inicio = request.POST.get("nueva_fecha")

        if not all([id_calendario, periodo, inicio]):
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Campos vacíos."
            })

        try:
            fecha_inicio = datetime.strptime(inicio, "%Y-%m-%d").date()
            fecha_final = fecha_inicio + timedelta(days=3)

            calendario_original = CalendarioAcademico.objects.get(id_fecha_academica=id_calendario)
            calendario_original.periodo_id = periodo
            calendario_original.fecha_inicio = fecha_inicio
            calendario_original.fecha_final = fecha_final
            calendario_original.save()

            relaciones = CalendarioMateria.objects.filter(calendario=calendario_original)

            for rel in relaciones:
                CalendarioMateria.objects.get_or_create(
                    calendario=calendario_original,
                    periodo_materia=rel.periodo_materia
                )

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Calendario actualizado correctamente."
            })

        except CalendarioAcademico.DoesNotExist:
            return JsonResponse({
                "estado": "error",
                "icon": "error",
                "descripcion": "Calendario no encontrado."
            })

    return JsonResponse({
        "estado": "fallo",
        "icon": "warning",
        "descripcion": "Método no permitido."
    })
    
def modelo_calendario_academico(request):
    if request.method == "POST":
        fechainicial = request.POST.get("fechainicial")
        fechareparacion = request.POST.get("fechareparacion")
        fechatramoI = request.POST.get("fechatramoI")
        fechatramoII = request.POST.get("fechatramoII")
        fechatramoIII = request.POST.get("fechatramoIII")
        fechasemestreI = request.POST.get("fechasemestreI")
        fechasemestreII = request.POST.get("fechasemestreII")

        anio = datetime.strptime(fechainicial, "%Y-%m-%d").year

        if CalendarioAcademico.objects.filter(fecha_inicio__year=anio).exists():
            return JsonResponse({
                "estado": "error",
                "icon": "warning",
                "descripcion": f"El calendario del año {anio} ya existe."
            })

        mapa = [
            ("Inicial", fechainicial),
            ("Reparación", fechareparacion),
            ("Tramo I", fechatramoI),
            ("Tramo II", fechatramoII),
            ("Tramo III", fechatramoIII),
            ("Semestre I", fechasemestreI),
            ("Semestre II", fechasemestreII),
        ]

        with transaction.atomic():
            CalendarioAcademico.objects.filter(activo=True).update(activo=False)

            nuevo_calendarios = []
            for nombre_periodo, fecha in mapa:

                fecha_inicio = datetime.strptime(fecha, "%Y-%m-%d").date()
                fecha_final = fecha_inicio + timedelta(days=3)
                periodo = PeriodoAcademico.objects.get(nombre=nombre_periodo)

                calendario = CalendarioAcademico.objects.create(
                    periodo=periodo,
                    fecha_inicio=fecha_inicio,
                    fecha_final=fecha_final,
                    activo=True
                )

                nuevo_calendarios.append((calendario, periodo))

            for calendario, periodo in nuevo_calendarios:
                periodos_materia = PeriodoMateria.objects.filter(periodo=periodo)

                if periodos_materia.exists():
                    for pm in periodos_materia:
                        CalendarioMateria.objects.get_or_create(
                            calendario=calendario,
                            periodo_materia=pm
                        )

        return JsonResponse({
            "estado": "ok",
            "icon": "success",
            "descripcion": "Calendario académico actualizado correctamente."
        })

    return render(request, "calendario_academico.html")