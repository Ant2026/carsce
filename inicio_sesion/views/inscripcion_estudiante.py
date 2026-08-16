from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from inicio_sesion.models import Usuario, Contacto, Nacimiento, Residencia, SeccionAcademica, SeccionEstudiante, Bitacora, CoordinadorPNF, EstatusEstudiante, DocumentosEstudiante, ContactoAuxiliar, Discapacidad, InformacionSecundaria, Estudiante
def obt_pre_inscrt(request):

    coordinador = CoordinadorPNF.objects.select_related(
        "nucleo",
        "pnf"
    ).get(
        usuario__cedula_identidad=request.session.get("cedula_usuario")
    )

    estudiantes = Estudiante.objects.filter(
        nucleo=coordinador.nucleo,
        pnf=coordinador.pnf,
        estatusestudiante__estado="Espera",
        estatusestudiante__estatus="Espera"
    ).select_related(
        "usuario"
    ).distinct()

    resultado = []

    for estudiante in estudiantes:

        estatus = estudiante.estatusestudiante_set.filter(
            estado="Espera",
            estatus="Espera"
        ).order_by(
            "-fecha_ingreso"
        ).first()

        if estatus:

            resultado.append({
                "id_estudiante": estudiante.id_estudiante,
                "cedula_identidad": estudiante.usuario.cedula_identidad,
                "nombres": estudiante.usuario.nombres,
                "apellidos": estudiante.usuario.apellidos,
                "genero": estudiante.usuario.genero,

                "estatus": estatus.estatus,
                "estado": estatus.estado,
                "ingreso": estatus.ingreso,
                "descripcion_ingreso": estatus.descripcion_ingreso,
                "trayecto": estatus.trayecto,
                "fecha_ingreso": estatus.fecha_ingreso.strftime("%Y-%m-%d"),
            })

    secciones = SeccionAcademica.objects.values(
        "id_seccion",
        "nombre",
        "turno"
    ).order_by("nombre")

    return JsonResponse({
        "estudiantes": resultado,
        "secciones": list(secciones)
    })
    
def obt_data_est(request):
    if request.method == "POST":
        usuario = Usuario.objects.filter(cedula_identidad=request.POST.get("cedula_estudiante")).first()

        datos_usuario = Usuario.objects.filter(pk=usuario.pk).values().first()

        contacto = Contacto.objects.filter(id_usuario=usuario).values().first()
        
        residencia = Residencia.objects.filter(id_usuario=usuario).values().first()

        nacimiento = Nacimiento.objects.filter(id_usuario=usuario).values().first()

        informacion_secundaria = InformacionSecundaria.objects.filter(id_usuario=usuario).values().first()

        discapacidad = Discapacidad.objects.filter(id_usuario=usuario).values().first()

        representantes = ContactoAuxiliar.objects.filter(id_usuario=usuario).values()

        documentos = []

        for doc in DocumentosEstudiante.objects.filter(id_usuario=usuario):
            if doc.archivo:

                ruta = str(doc.archivo).replace("\\", "/")

                if ruta.startswith("media/"):
                    ruta = ruta[6:]

                documentos.append({
                    "tipo_documento": doc.nombre_documento,
                    "archivo": settings.MEDIA_URL + ruta
                })

        return JsonResponse({
            "usuario": datos_usuario,
            "contacto": contacto,
            "residencia": residencia,
            "nacimiento": nacimiento,
            "informacion_secundaria": informacion_secundaria,
            "discapacidad": discapacidad,
            "representantes": representantes,
            "documentos": documentos
        })

    return JsonResponse({
        "estado": "fallo",
        "descripcion": "Método no permitido"
    })

def inscr_est(request):
    if request.method == "POST":
        cedula = request.POST.get("cedula")
        id_seccion = request.POST.get("seccion")
        accion = request.POST.get("accion")

        # OBTENER COORDINADOR
        coordinador = CoordinadorPNF.objects.select_related(
            "nucleo",
            "pnf"
        ).filter(
            usuario__cedula_identidad=request.session.get("cedula_usuario")
        ).first()

        if not coordinador:
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "No se encontró el coordinador."
            })

        # VALIDAR SECCIÓN CUANDO SE ACEPTA
        if accion == "aceptado" and not id_seccion:
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Debe seleccionar la sección."
            })

        # BUSCAR USUARIO
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

        # BUSCAR ESTUDIANTE DEL NÚCLEO Y PNF DEL COORDINADOR
        estudiante = Estudiante.objects.filter(
            usuario=usuario,
            nucleo=coordinador.nucleo,
            pnf=coordinador.pnf
        ).first()

        if not estudiante:
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "El estudiante no pertenece al PNF o núcleo del coordinador."
            })

        # BUSCAR ESTATUS DE PREINSCRIPCIÓN
        estatus_estudiante = EstatusEstudiante.objects.filter(
            estudiante=estudiante,
            estatus="Espera",
            estado="Espera"
        ).order_by(
            "-fecha_ingreso"
        ).first()

        if not estatus_estudiante:
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "No se encontró la preinscripción del estudiante."
            })

        # ==========================================
        # RECHAZAR
        # ==========================================

        if accion == "rechazado":
            estatus_estudiante.estado = "Rechazado"
            estatus_estudiante.save(
                update_fields=["estado"]
            )

            return JsonResponse({
                "titulo": "¡Éxito!",
                "estado": "exito",
                "icon": "success",
                "descripcion": "La preinscripción fue rechazada."
            })

        # ==========================================
        # ACEPTAR
        # ==========================================

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

        # VALIDAR QUE EL ESTUDIANTE NO TENGA
        # OTRA SECCIÓN ACTIVA
        if SeccionEstudiante.objects.filter(
            estudiante=estudiante,
            fecha_final__isnull=True
        ).exists():

            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "El estudiante ya posee una sección activa."
            })

        # REGISTRAR SECCIÓN
        SeccionEstudiante.objects.create(
            seccion=seccion,
            estudiante=estudiante,
            fecha_inicio=timezone.now().date()
        )

        # ACTUALIZAR ESTATUS
        estatus_estudiante.estatus = "Inscrito(a)"
        estatus_estudiante.estado = "Activo"
        estatus_estudiante.save(
            update_fields=["estatus", "estado"]
        )

        return JsonResponse({
            "titulo": "¡Éxito!",
            "estado": "exito",
            "icon": "success",
            "descripcion": "El estudiante fue inscrito correctamente."
        })

    return render(request, "Coordinador_PNF/inscripcion/inscripcion_estudiante.html")



