from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone

from inicio_sesion.models import Materia, MateriaAsignada, DocenteAsignadoMateria, CoordinadorPNF, Docente, Bitacora, Materia, SeccionAcademica
    
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

def busc_mat(request):
    if request.method == "POST":
        materia = request.POST.get("nombre_materia", "").strip()

        resultados = Materia.objects.filter(nombre__icontains=materia)

        if not resultados.exists():
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "No se encontraron materias."
            })

        materias = []
        for resultado in resultados:
            materias.append({
                "id": resultado.id_materia,
                "nombre": resultado.nombre,
                "codigo": resultado.codigo,
                "trayecto": resultado.trayecto,
                "recuperacion": resultado.recuperacion,
                "htea": resultado.htea,
                "htei": resultado.htei,
                "thte": resultado.thte,
                "uc": resultado.uc,
                "pnf": resultado.id_pnf.pnf
            })

        return JsonResponse({
            "estado": "exito",
            "materias": materias
        })

def mats_reg(request):
    try:
        coordinador = CoordinadorPNF.objects.get(
            usuario__cedula_identidad=request.session.get("cedula_usuario")
        )
    except CoordinadorPNF.DoesNotExist:
        return JsonResponse({
            "estado": "fallo",
            "title": "Error",
            "icon": "error",
            "descripcion": "No cuenta con el rol de Coordinador de PNF.",
            "materias": []
        })

    materias = []

    for materia in Materia.objects.filter(id_pnf=coordinador.pnf).order_by(
        "trayecto",
        "nombre"
    ):

        materia_asignada = MateriaAsignada.objects.filter(
            materia=materia
        ).first()

        estado = "VERDE"

        if materia_asignada:

            roles = DocenteAsignadoMateria.objects.filter(
                materia_asignada=materia_asignada,
                activo=True
            ).values_list("rol", flat=True)

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

def asig_mat_doc(request):
    if request.method == "POST":
        docente = request.POST.get("docente")
        rol_docente = request.POST.get("rol_docente")
        seccion = request.POST.get("seccion")
        materias = request.POST.getlist("materias[]")

        controles = [
            (docente, "Docente", "Debe seleccionar un docente."), 
            (rol_docente, "Rol del Docente", "Debe seleccionar el rol del docente."), 
            (seccion, "Sección Académico", "Debe seleccionar la sección académica."), 
            (materias, "Materia Académico", "Debe seleccionar al meno una materia."), 
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
            docente = Docente.objects.get(pk=docente)
        except Docente.DoesNotExist:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "icon": "error",
                "descripcion": "No se encontró el perfil de docente."
            })

        with transaction.atomic():
            for id_materia in materias:
                try:
                    materia = Materia.objects.get(pk=id_materia)
                except Materia.DoesNotExist:
                    continue

                asignacion, creada = MateriaAsignada.objects.get_or_create(materia=materia, seccion_id=seccion)

                # Validar que no exista otro docente con el mismo rol
                if DocenteAsignadoMateria.objects.filter(
                    materia_asignada=asignacion,
                    rol=rol_docente,
                    activo=True
                ).exists():
                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "warning",
                        "title": "Asignación existente",
                        "descripcion": (
                            f"La materia '{materia.nombre}' ya tiene asignado un "
                            f"{'docente principal' if rol_docente == 'PRINCIPAL' else 'docente secundario'}."
                        )
                    })
                
                DocenteAsignadoMateria.objects.create(
                    materia_asignada=asignacion,
                    docente=docente,
                    rol=rol_docente,
                    activo=True
                )

                Bitacora.objects.create(
                    nombre_usuario=request.session.get("usuario_nombre"),
                    fecha_hora=timezone.now(),
                    accion=(
                        f"Asignó la materia '{materia.nombre}' al docente "
                        f"{docente.usuario.nombres} {docente.usuario.apellidos} "
                        f"como {'Docente Principal' if rol_docente == 'PRINCIPAL' else 'Docente Secundario'}."
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
    return render(request, "Coordinador_PNF/asignacion_materia/visualizar_asignaciones.html")


