from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

from inicio_sesion.models import PeriodoCargarNotas, CalendarioCargarNotas, Bitacora

# periodos_academicos
def periodos_lista(request):
    periodos = list(
        PeriodoCargarNotas.objects.values(
            "id_periodo_academico",
            "nombre"
        )
    )

    return JsonResponse({
        "estado": "exito",
        "periodos": periodos
    })

# calendarios_registrados
def calendarios_lista(request):
    calendarios = list(
        CalendarioCargarNotas.objects.values(
            "id_fecha_carga_nota",
            "periodo__id_periodo_academico",
            "periodo__nombre",
            "fecha_inicio",
            "fecha_final"
        )
    )

    return JsonResponse({
        "estado": "exito",
        "calendarios": calendarios
    })

#  datos_calendario
def calendario_datos(request):
    if request.method == "POST":
        id_calendario = request.POST.get("id_calendario")

        try:
            cal = CalendarioCargarNotas.objects.select_related("periodo").get(id_fecha_academica=id_calendario)
        except CalendarioCargarNotas.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "No se encuentra registrado el calendario académico."
            })

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
    
    return render(request, "Director_General/calendario_notas/visualizar_calendario.html")

# guardar_actualizar_calendario
def calendario_guardar(request):
    if request.method == "POST":
        id_calendario = request.POST.get("fechaseleccionado")
        periodo = request.POST.get("actualizar_fecha_academica")
        inicio = request.POST.get("nueva_fecha")

        controles = [
            (periodo, "Periodo Académico", "Por favor, selecciona el periodo académico."),
            (inicio, "Fecha de Inicio del Tramo", "Por favor, ingrese la fecha inicial."),
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "falla",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })
        try:
            calendario_original = CalendarioCargarNotas.objects.get(id_fecha_academica=id_calendario)
        except CalendarioCargarNotas.DoesNotExist:
            return JsonResponse({
                "estado": "falla",
                "icon": "error",
                "title": "Error",
                "descripcion": "Calendario no encontrado."
            })

        fecha_inicio = datetime.strptime(inicio, "%Y-%m-%d").date()
        fecha_final = fecha_inicio + timedelta(days=3)
        
        calendario_original.periodo_id = periodo
        calendario_original.fecha_inicio = fecha_inicio
        calendario_original.fecha_final = fecha_final
        calendario_original.save()

        Bitacora.objects.create(
            nombre_usuario=request.session.get("usuario_nombre"),
            fecha_hora=timezone.now(),
            accion=f"Se actualizo el calendario académico."
        ) 
        
        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Exito",
            "descripcion": "Se actualizo la fecha exitosamente."
        })

# registrar calendario
def reg_calendario(request):
    if request.method == "POST":
        fechainicialtrimestral = request.POST.get("fechainicialtrimestral")
        fechainicialsemestral = request.POST.get("fechainicialsemestral")
        fechareparacion = request.POST.get("fechareparacion")
        fechatramoI = request.POST.get("fechatramoI")
        fechatramoII = request.POST.get("fechatramoII")
        fechatramoIII = request.POST.get("fechatramoIII")
        fechasemestreI = request.POST.get("fechasemestreI")
        fechasemestreII = request.POST.get("fechasemestreII")

        controles = [
            (fechainicialtrimestral, "Fecha de Inicial Trimestre", "Por favor, selecciona la fecha del tramo inicial."),
            (fechainicialsemestral, "Fecha de Inicial Semestre", "Por favor, selecciona la fecha del tramo inicial."),
            (fechareparacion, "Fecha de Reparación", "Por favor, selecciona la fecha del tramo Reparación."),
            (fechatramoI, "Fecha del Tramo I", "Por favor, selecciona la fecha del tramo Tramo I."),
            (fechatramoII, "Fecha del Tramo II", "Por favor, selecciona la fecha del tramo Tramo II."),
            (fechatramoIII, "Fecha del Tramo III", "Por favor, selecciona la fecha del tramo Tramo III."),
            (fechasemestreI, "Fecha del Semestre I", "Por favor, selecciona la fecha del tramo Semestre I."),
            (fechasemestreII, "Fecha del Semestre II", "Por favor, selecciona la fecha del tramo Semestre II."),
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })

        anio = datetime.strptime(fechainicialtrimestral, "%Y-%m-%d").year

        if CalendarioCargarNotas.objects.filter(fecha_inicio__year=anio).exists():
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Duplicado",
                "descripcion": f"El calendario del año {anio} ya existe."
            })

        mapa = [
            ("Inicial Trimestre", fechainicialtrimestral),
            ("Inicial Semestre", fechainicialsemestral),
            ("Reparación", fechareparacion),
            ("Tramo I", fechatramoI),
            ("Tramo II", fechatramoII),
            ("Tramo III", fechatramoIII),
            ("Semestre I", fechasemestreI),
            ("Semestre II", fechasemestreII),
        ]

        with transaction.atomic():
            CalendarioCargarNotas.objects.filter(activo=True).update(activo=False)

            nuevo_calendarios = []
            for nombre_periodo, fecha in mapa:
                fecha_inicio = datetime.strptime(fecha, "%Y-%m-%d").date()
                fecha_final = fecha_inicio + timedelta(days=3)

                periodo = PeriodoCargarNotas.objects.get(nombre=nombre_periodo)

                calendario = CalendarioCargarNotas.objects.create(
                    periodo=periodo,
                    fecha_inicio=fecha_inicio,
                    fecha_final=fecha_final,
                    activo=True
                )

                nuevo_calendarios.append((calendario, periodo))

            Bitacora.objects.create(
                nombre_usuario=request.session.get("usuario_nombre"),
                fecha_hora=timezone.now(),
                accion="Registró el calendario académico."
            )
            return JsonResponse({
                "estado": "exito",
                "icon": "success",
                "title": "Exito",
                "descripcion": "El calendario académico se registro exitosamente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Error",
            "descripcion": "Ocurrio un error al momento de registrar el calendario académico."
        })

    return render(request, "Director_General/calendario_notas/registrar_calendario.html")

