from django.shortcuts import render
from django.http import JsonResponse

from inicio_sesion.models import  Pnf, Materia, PeriodoAcademico, CalendarioAcademico, PeriodoMateria, CalendarioMateria

def materias_almacenada(request):
   if request.method == "POST":
        pnf = request.POST.get("pnf")

        materias_query = Materia.objects.select_related(
            "id_pnf"
        )
        
        if pnf and pnf != "ninguno":
            materias_query = materias_query.filter(id_pnf=pnf)


        materias = list(
            materias_query.values(
                "id_materia",
                "nombre",
                "codigo",
                "tipo_materia",
                "recuperacion",
                "id_pnf",
                "trayecto"
            )
        )

        pnfs = list(
            Pnf.objects.values(
                "id_pnf",
                "pnf",
                "codigo"
            )
        )

        return JsonResponse({
            "estado": "exito",
            "materias": materias,
            "pnfs": pnfs
        })

def datos_materia(request):
    if request.method == "POST":
        id_materia = request.POST.get("id_materia")

        try:
            materia = Materia.objects.select_related(
                "id_pnf",
            ).get(id_materia=id_materia)

            return JsonResponse({
                "estado": "ok",
                "materia": {
                    "id_materia": materia.id_materia,
                    "nombre": materia.nombre,
                    "codigo": materia.codigo,
                    "tipo_materia": materia.tipo_materia,
                    "recuperacion": materia.recuperacion,
                    "trayecto": materia.trayecto
                },
                "pnf": {
                    "id_pnf": materia.id_pnf.id_pnf,
                    "pnf": materia.id_pnf.pnf,
                    "codigo": materia.id_pnf.codigo
                }
            })

        except Materia.DoesNotExist:
            return JsonResponse({
                "estado": "error",
                "mensaje": "Materia no encontrada"
            })

def guardar_actualizacion_materia(request):
    if request.method == "POST":
        id_materia = request.POST.get("materiaseleccionado")
        nombre = request.POST.get("nombresmaterias")
        codigo = request.POST.get("codigosmaterias")
        periodo_materia = request.POST.get("periodomateria")
        trayecto_materia = request.POST.get("trayectomateria")
        reparacion_materia = request.POST.get("reparacionmateria")
        pnf_materia = request.POST.get("pnfmateria")

        if not all([id_materia, nombre, codigo, periodo_materia, trayecto_materia, reparacion_materia, pnf_materia]):
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Campos vacíos."
            })

        try:
            materia = Materia.objects.get(id_materia=id_materia)
            materia.nombre = nombre
            materia.codigo = codigo
            materia.tipo_materia = periodo_materia
            materia.trayecto = trayecto_materia
            materia.recuperacion = reparacion_materia
            materia.id_pnf_id = pnf_materia
            materia.save()

            PeriodoMateria.objects.filter(materia=materia).delete()

            mapa_periodos = {
                "INICIAL": ["INICIAL"],
                "REPARACION": ["REPARACIÓN"],

                "TRIMESTRE": ["TRAMO I", "TRAMO II", "TRAMO III"],
                "TRAMO_I": ["TRAMO I"],
                "TRAMO_II": ["TRAMO II"],
                "TRAMO_III": ["TRAMO III"],
                "TRAMO_I_II": ["TRAMO I", "TRAMO II"],
                "TRAMO_II_III": ["TRAMO II", "TRAMO III"],
                "TRAMO_I_III": ["TRAMO I", "TRAMO III"],

                "SEMESTRE": ["SEMESTRE I", "SEMESTRE II"],
                "SEMESTRE_I": ["SEMESTRE I"],
                "SEMESTRE_II": ["SEMESTRE II"],
            }

            valores = mapa_periodos.get(periodo_materia)

            if not valores:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "Periodo inválido."
                })

            nuevos_pm = []

            for nombre_periodo in valores:
                periodo = PeriodoAcademico.objects.get(nombre=nombre_periodo)

                pm = PeriodoMateria.objects.create(
                    materia=materia,
                    periodo=periodo
                )

                nuevos_pm.append(pm)

            calendario = CalendarioAcademico.objects.filter(
                activo=True
            ).order_by("-fecha_inicio").first()

            if calendario:

                CalendarioMateria.objects.filter(
                    periodo_materia__materia=materia,
                    calendario=calendario
                ).delete()

                for pm in nuevos_pm:
                    CalendarioMateria.objects.create(
                        calendario=calendario,
                        periodo_materia=pm
                    )

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "La materia se actualizó correctamente."
            })

        except Materia.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "Materia no encontrada."
            })
        
def modulo_materia(request):
    if request.method == "POST":

        nombre = request.POST.get("nombresmaterias")
        codigo = request.POST.get("codigosmaterias")
        periodo_materia = request.POST.get("periodomateria")
        trayecto = request.POST.get("trayectomateria")
        reparacion = request.POST.get("reparacionmateria")
        pnf = request.POST.get("pnfmateria")

        if not all([nombre, codigo, periodo_materia, trayecto, reparacion, pnf]):
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Campos vacíos."
            })

        if Materia.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "Nombre duplicado."
            })

        if Materia.objects.filter(codigo__iexact=codigo).exists():
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "Código duplicado."
            })
        
        pnf_obj = Pnf.objects.get(id_pnf=pnf)
        

        materia = Materia.objects.create(
            nombre=nombre,
            codigo=codigo,
            tipo_materia=periodo_materia,
            trayecto=trayecto,
            recuperacion=reparacion,
            id_pnf=pnf_obj
        )

        mapa_periodo_bd = {
            "INICIAL": ["Inicial"],
            "REPARACION": ["Reparación"],
            "TRIMESTRE": ["Tramo I", "Tramo II", "Tramo III"],
            "TRAMO_I": ["Tramo I"],
            "TRAMO_II": ["Tramo II"],
            "TRAMO_III": ["Tramo III"],
            "TRAMO_I_II": ["Tramo I", "Tramo II"],
            "TRAMO_II_III": ["Tramo II", "Tramo III"],
            "TRAMO_I_III": ["Tramo I", "Tramo III"],
            "SEMESTRE": ["Semestre I", "Semestre II"],
            "SEMESTRE I": ["Semestre I"],
            "SEMESTRE II": ["Semestre II"],
        }

        valores = mapa_periodo_bd.get(periodo_materia)
        if not valores:
            materia.delete()
            return JsonResponse({
                "estado": "fallo", 
                "icon": "error", 
                "descripcion": "Periodo inválido."
            })

        periodos = PeriodoAcademico.objects.filter(nombre__in=valores)
        if not periodos.exists():
            materia.delete()
            return JsonResponse({
                "estado": "fallo", 
                "icon": "error", 
                "descripcion": "No existen periodos."
            })

        calendario = CalendarioAcademico.objects.filter(activo=True).order_by("-fecha_inicio").first()

        if not calendario:
            materia.delete()
            return JsonResponse({
                "estado": "fallo", 
                "icon": "error", 
                "descripcion": 
                "No hay calendario activo."
            })

        existe = CalendarioMateria.objects.filter(calendario=calendario, periodo_materia__materia=materia).exists()

        if existe:
            materia.delete()
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "Materia ya registrada en el calendario activo."
            })

        periodo_materias = []
        for periodo in periodos:
            pm, _ = PeriodoMateria.objects.get_or_create(
                materia=materia,
                periodo=periodo
            )
            periodo_materias.append(pm)

        if periodo_materia in ["INICIAL", "REPARACION"]:
            pm = periodo_materias[0]
            CalendarioMateria.objects.create(
                calendario=calendario,
                periodo_materia=pm
            )

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Materia inicial registrada correctamente."
            })

        for pm in periodo_materias:
            CalendarioMateria.objects.get_or_create(
                calendario=calendario,
                periodo_materia=pm
            )

        return JsonResponse({
            "estado": "ok",
            "icon": "success",
            "descripcion": "Materia registrada correctamente."
        })

    return render(request, "Director_General/materias.html")