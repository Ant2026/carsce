from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from inicio_sesion.models import Usuario, Contacto, Nacimiento, Residencia, SeccionAcademica

def obtener_pre_inscrito(request):
    if request.method == "POST":
        id_nucleo = request.POST.get("nucleo")
        id_pnf = request.POST.get("pnf")

        if not id_nucleo or not id_pnf:
            return JsonResponse({
                "estado": "exito",
                "secciones": [],
                "estudiantes": []
            })

        # secciones = []
        # for seccion in SeccionAcademica.objects.select_related(
        #     "id_aula"
        # ).filter(
        #     id_nucleo_id=id_nucleo,
        #     id_pnf_id=id_pnf
        # ).order_by("seccion"):

        #     cantidad_estudiantes = SeccionEstudiante.objects.filter(id_seccion=seccion).count()

        #     if cantidad_estudiantes < 48:
        #         secciones.append({
        #             "id_seccion": seccion.id_seccion,
        #             "seccion": seccion.seccion,
        #             "aula": seccion.id_aula.nombre_aula,
        #             "turno": seccion.turno,
        #             "cantidad_estudiantes": cantidad_estudiantes
        #         })

        # estudiantes = EstatusEstudiante.objects.select_related(
        #     "id_asignacion",
        #     "id_asignacion__id_usuario",
        #     "id_asignacion__id_perfil",
        #     "id_asignacion__id_pnf",
        #     "id_asignacion__id_nucleo"
        # ).filter(
        #     estatus="Pre-Inscrito(a)",
        #     estado="Espera",
        #     id_asignacion__id_perfil_id=5,
        #     id_asignacion__id_nucleo_id=id_nucleo,
        #     id_asignacion__id_pnf_id=id_pnf
        # )

        # datos = []
        # for estudiante in estudiantes:
        #     usuario = estudiante.id_asignacion.id_usuario

        #     datos.append({
        #         "id_usuario": usuario.id_usuario,
        #         "nombres": usuario.nombres,
        #         "apellidos": usuario.apellidos,
        #         "cedula": usuario.cedula_identidad
        #     })

        # return JsonResponse({
        #     "estado": "exito",
        #     "secciones": secciones,
        #     "estudiantes": datos
        # })

    return JsonResponse({
        "estado": "error",
        "secciones": [],
        "estudiantes": []
    })

def obtener_datos_pre_inscrito(request):
    if request.method == "POST":
        cedula_estudiante = request.POST.get("cedula_estudiante")

        usuario = Usuario.objects.filter(cedula_identidad=cedula_estudiante).first()
        if not usuario:
            return JsonResponse({
                "estado": "fallo",
                "descripcion": "Estudiante no encontrado"
            })

        datos_usuario = Usuario.objects.filter(pk=usuario.pk).values().first()

        contacto = Contacto.objects.filter(id_usuario=usuario).values().first()
        
        residencia = Residencia.objects.filter(id_usuario=usuario).values().first()

        nacimiento = Nacimiento.objects.filter(id_usuario=usuario).values().first()

        # informacion_secundaria = InformacionSecundaria.objects.filter(id_usuario=usuario).values().first()

        # discapacidad = Discapacidad.objects.filter(id_usuario=usuario).values().first()

        # representantes = list(
        #     PadresEstudiante.objects.filter(id_usuario=usuario).values()
        # )

        # documentos = []

        # for doc in DocumentosEstudiante.objects.filter(id_usuario=usuario):
        #     if doc.archivo:

        #         ruta = str(doc.archivo).replace("\\", "/")

        #         if ruta.startswith("media/"):
        #             ruta = ruta[6:]

        #         documentos.append({
        #             "tipo_documento": doc.nombre_documento,
        #             "archivo": settings.MEDIA_URL + ruta
        #         })

        # return JsonResponse({
        #     "usuario": datos_usuario,
        #     "contacto": contacto,
        #     "residencia": residencia,
        #     "nacimiento": nacimiento,
        #     "informacion_secundaria": informacion_secundaria,
        #     "discapacidad": discapacidad,
        #     "representantes": representantes,
        #     "documentos": documentos
        # })

    return JsonResponse({
        "estado": "fallo",
        "descripcion": "Método no permitido"
    })

def inscripcion_estudiante(request):
    if request.method == "POST":
        cedula = request.POST.get("cedula")
        id_nucleo = request.POST.get("nucleo")
        id_pnf = request.POST.get("pnf")
        id_seccion = request.POST.get("seccion")
        accion = request.POST.get("accion")

        if accion == "aceptado" and not id_seccion:
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Debe seleccionar la sección."
            })

        usuario = Usuario.objects.filter(
            cedula_identidad=cedula
        ).first()

        if not usuario:
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "El estudiante no existe."
            })

        # estatus_estudiante = EstatusEstudiante.objects.select_related(
        #     "id_asignacion"
        # ).filter(
        #     id_asignacion__id_usuario=usuario,
        #     id_asignacion__id_nucleo_id=id_nucleo,
        #     id_asignacion__id_pnf_id=id_pnf,
        #     id_asignacion__id_perfil_id=5,
        #     estatus="Pre-Inscrito(a)",
        #     estado="Espera"
        # ).first()

        # if not estatus_estudiante:
        #     return JsonResponse({
        #         "titulo": "¡Advertencia!",
        #         "estado": "fallo",
        #         "icon": "warning",
        #         "descripcion": "No se encontró la preinscripción del estudiante."
        #     })

        # # RECHAZAR
        # if accion == "rechazado":

        #     estatus_estudiante.estado = "Rechazado"
        #     estatus_estudiante.save()

        #     return JsonResponse({
        #         "titulo": "¡Éxito!",
        #         "estado": "exito",
        #         "icon": "success",
        #         "descripcion": "La preinscripción fue rechazada."
        #     })

        # ACEPTAR
        seccion = SeccionAcademica.objects.filter(
            id_seccion=id_seccion
        ).first()

        if not seccion:
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "La sección seleccionada no existe."
            })

        # if SeccionEstudiante.objects.filter(
        #     id_usuario=usuario,
        #     fecha_final__isnull=True
        # ).exists():

        #     return JsonResponse({
        #         "titulo": "¡Advertencia!",
        #         "estado": "fallo",
        #         "icon": "warning",
        #         "descripcion": "El estudiante ya posee una sección activa."
        #     })

        # SeccionEstudiante.objects.create(
        #     id_seccion=seccion,
        #     id_usuario=usuario,
        #     fecha_inicio=timezone.now().date()
        # )

        # estatus_estudiante.estatus = "Inscrito(a)"
        # estatus_estudiante.estado = "Activo"
        # estatus_estudiante.save()

        return JsonResponse({
            "titulo": "¡Éxito!",
            "estado": "exito",
            "icon": "success",
            "descripcion": "El estudiante fue inscrito correctamente."
        })

    return render(request, "Director_General/inscripcion_estudiante.html")