from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone

from inicio_sesion.models import Usuario, Bitacora, Pnf, Materia, PeriodoCargarNotas, PeriodoNotasMateria, DirectorGeneral, ControlEstudio

def mat_lista(request):
    if request.method == "POST":
        cedula_usuario = request.session.get("cedula_usuario")
        nucleo = None

        # Buscar si es Director General
        director = DirectorGeneral.objects.filter(
            usuario__cedula_identidad=cedula_usuario
        ).select_related(
            "nucleo"
        ).first()

        if director:
            nucleo = director.nucleo

        # Si no es Director, buscar Control de Estudio
        if not nucleo:
            control = ControlEstudio.objects.filter(
                usuario__cedula_identidad=cedula_usuario
            ).select_related(
                "nucleo"
            ).first()

            if control:
                nucleo = control.nucleo

        if not nucleo:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "mensaje": "El usuario no tiene núcleo asignado."
            })

        # Obtener PNF asignados al núcleo
        pnfs_usuario = Pnf.objects.filter(pnfnucleo__id_nucleo_id=nucleo.id_nucleo).distinct()

        pnf = request.POST.get("pnf")

        # Materias de esos PNF
        materias_query = Materia.objects.select_related("id_pnf").filter(id_pnf__in=pnfs_usuario)

        # Filtrar por PNF seleccionado
        if pnf and pnf != "ninguno":
            materias_query = materias_query.filter(id_pnf=pnf)

        materias = list(
            materias_query.values(
                "id_materia",
                "nombre",
                "codigo",
                "recuperacion",
                "id_pnf",
                "trayecto"
            )
        )

        pnfs = list(
            pnfs_usuario.values(
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

    return render(request, "Director_General/materia/visualizar_materia.html")

def mat_datos(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo")

        try:
            materia = Materia.objects.select_related(
                "id_pnf",
            ).get(codigo=codigo)
        except Materia.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "La materia no se encuentra registrado."
            })
        
        return JsonResponse({
            "estado": "ok",
            "materia": {
                "id_materia": materia.id_materia,
                "nombre": materia.nombre,
                "recuperacion": materia.recuperacion,
                "trayecto": materia.trayecto
            },
            "pnf": {
                "id_pnf": materia.id_pnf.id_pnf,
                "pnf": materia.id_pnf.pnf,
                "codigo": materia.id_pnf.codigo
            }
        })

def mat_guardar(request):
    if request.method == "POST":
        id_materia = request.POST.get("materiaseleccionado")
        nombre = request.POST.get("nombresmaterias")
        reparacion_materia = request.POST.get("reparacionmateria")
        pnf_materia = request.POST.get("pnfmateria")

        controles = [
            (nombre, "Nombre de la Materia", "Por favor, debe ingresar el nombre de la materia."),
            (reparacion_materia, "Reparación de la Materia", "Por favor, seleccione si la materia hay la posibilidad de haber o no reparación."),
            (pnf_materia, "PNF de la Materia", "Por favor, seleccione el pnf que pertenecera la materia."),
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })

        with transaction.atomic():
            try:
                materia = Materia.objects.get(id_materia=id_materia)
            except Materia.DoesNotExist:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "title": "No Existe",
                    "descripcion": "La materia no se encuentra registrada."
                })

            materia.nombre = nombre
            materia.recuperacion = reparacion_materia
            materia.id_pnf_id = pnf_materia
            materia.save()

            Bitacora.objects.create(
                nombre_usuario=request.session.get("usuario_nombre"),
                fecha_hora=timezone.now(),
                accion=f"Actualizó la materia '{materia.nombre}'."
            )

            return JsonResponse({
                "estado": "exito",
                "icon": "success",
                "title": "Éxito",
                "descripcion": "La materia se actualizó exitosamente."
            })

    return render(request, "Director_General/materia/actualizar_materia.html")

def nombre_materia(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")

        existe = Materia.objects.filter(nombre__iexact=nombre).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def codigo_materia(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo")

        existe = Materia.objects.filter(codigo__iexact=codigo).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def reg_mat(request):
    if request.method == "POST":
        nombre = request.POST.get("nombresmaterias")
        codigo = request.POST.get("codigosmaterias")
        periodo_materia = request.POST.get("periodomateria")
        trayecto = request.POST.get("trayectomateria")
        reparacion = request.POST.get("reparacionmateria")
        pnf = request.POST.get("pnfmateria")

        controles = [
            (nombre, "Nombre de la Materia", "Por favor, debe ingresar el nombre de la materia."),
            (codigo, "Código de la Materia", "Por favor, debe ingresar el código de la Materia."),
            (periodo_materia, "Periodo Académico", "Por favor, debe seleccionar el periodo académico."),
            (trayecto, "Trayecto Académico", "Por favor, debe seleccionar el taryecto académico."),
            (reparacion, "Reparación", "Por favor, debe seleccionar la posibilidad de reparación."),
            (pnf, "P.N.F", "Por favor, debe seleccionar el PNF.")
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })

        pnf_obj = Pnf.objects.get(id_pnf=pnf)

        mapa_periodo_bd = {
            "INICIAL_TRIMESTRE": ["Inicial Trimestre"],
            "INICIAL_SEMESTRE": ["Inicial Semestre"],
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
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Error",
                "descripcion": "Periodo inválido."
            })

        periodos = PeriodoCargarNotas.objects.filter(nombre__in=valores)
        if not periodos.exists():
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "No existen periodos académicos."
            })

        with transaction.atomic():
            materia = Materia.objects.create(
                nombre=nombre,
                codigo=codigo,
                trayecto=trayecto,
                recuperacion=reparacion,
                id_pnf=pnf_obj
            )

            periodo_materias = []

            for periodo in periodos:
                pm = PeriodoNotasMateria.objects.create(
                    materia=materia,
                    periodo=periodo
                )
                periodo_materias.append(pm)

            Bitacora.objects.create(
                nombre_usuario=request.session.get("usuario_nombre"),
                fecha_hora=timezone.now(),
                accion=f"Registró la materia '{materia.nombre}' ({materia.codigo}) en el PNF '{pnf_obj.pnf}'."
            )

            return JsonResponse({
                "estado": "exito",
                "icon": "success",
                "title": "Éxito",
                "descripcion": "Materia registrada correctamente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "title": "Error",
            "descripcion": "Hubo un error al registrar los datos del PNF."
        })

    return render(request, "Director_General/materia/registrar_materias.html")

