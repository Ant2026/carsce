from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime

from django.shortcuts import get_object_or_404

from inicio_sesion.models import HorarioAcademica, DetalleHorario, CarpetaAcademica, DocumentoHorario, DocumentoCompartido, Bitacora, CoordinadorPNF, Usuario, MateriaAsignada, SeccionAcademica, PeriodoCargarNotas

from django.conf import settings
from pathlib import Path
import re

from django.contrib.staticfiles import finders
from reportlab.platypus import Image

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

def trayecto_hor(request):
    coordinador = CoordinadorPNF.objects.get(usuario__cedula_identidad=request.session.get("cedula_usuario"))
    pnf = coordinador.pnf

    if pnf.pnf == "PNF en Mediciona Veterinaria":
        trayectos = [
            "Inicial",
            "Trayecto I",
            "Trayecto II",
            "Trayecto III",
            "Trayecto IV",
            "Trayecto V",
        ]
    else:
        trayectos = [
            "Inicial",
            "Trayecto I",
            "Trayecto II",
            "Trayecto III",
            "Trayecto IV",
        ]

    return JsonResponse({
        "estado": "exito",
        "trayectos": trayectos
    })

def periodo_academico_hor(request):

    coordinador = CoordinadorPNF.objects.get(
        usuario__cedula_identidad=request.session.get("cedula_usuario")
    )

    pnf = coordinador.pnf

    trayecto_seleccionado = request.POST.get("trayecto")

    if pnf.pnf == "PNF en Medicina Veterinaria":

        if trayecto_seleccionado == "Inicial":
            nombres_periodos = [
                "Inicial Semestre",
            ]

        else:
            nombres_periodos = [
                "Semestre I",
                "Semestre II",
            ]

    else:

        if trayecto_seleccionado == "Inicial":
            nombres_periodos = [
                "Inicial Trimestre",
            ]

        else:
            nombres_periodos = [
                "Tramo I",
                "Tramo II",
                "Tramo III",
            ]

    periodos_academicos = []

    for nombre in nombres_periodos:

        periodo = PeriodoCargarNotas.objects.filter(
            nombre=nombre
        ).first()

        if periodo:
            periodos_academicos.append({
                "id": periodo.id_periodo_academico,
                "nombre": periodo.nombre
            })

    return JsonResponse({
        "estado": "exito",
        "periodos_academicos": periodos_academicos
    })

def asig_mat_reg(request):
    trayecto = request.POST.get("trayecto")
    seccion = request.POST.get("seccion")

    materias_asignadas = (
        MateriaAsignada.objects
        .filter(
            materia__trayecto=trayecto,
            seccion_id=seccion,
            activo=True
        )
        .select_related(
            "materia",
            "seccion"
        )
        .prefetch_related(
            "docentes__docente__usuario"
        )
    )

    resultado = []
    for asignacion in materias_asignadas:
        docentes = []
        for asignacion_docente in asignacion.docentes.filter(
            activo=True
        ).select_related("docente__usuario"):
            docentes.append({
                "id_docente": asignacion_docente.docente.id_docente,
                "nombre": str(asignacion_docente.docente.usuario),
                "rol": asignacion_docente.rol
            })

        resultado.append({
            "id_materia_asignada": asignacion.id_materia_asignada,

            "materia": {
                "id_materia": asignacion.materia.id_materia,
                "nombre": asignacion.materia.nombre,
                "codigo": asignacion.materia.codigo,
            },

            "docentes": docentes
        })

    return JsonResponse({
        "estado": "exito",
        "materias": resultado
    })

def reg_hor(request):
    if request.method == "POST":
        # Datos del encabezado
        trayecto = request.POST.get("trayecto")
        periodo_academico = request.POST.get("periodo_academico")
        aula = request.POST.get("aula")
        seccion = request.POST.get("seccion")
        
        # Datos de la tabla
        cantidad_filas = request.POST.get("filas")

        controles = [
            (trayecto, "Trayecto Académico", "Por favor, debe seleccionar el trayecto académico."),
            (periodo_academico, "Periodo Académico", "Por favor, debe seleccionar el periodo académico."),
            (aula, "Aula Académica", "Por favor, debe seleccionar el aula académica."),
            (seccion, "Sección Académica", "Por favor, debe seleccionar la sección académica."),
            (cantidad_filas, "Cantidad de Filas", "Por favor, debe ingresar la cantidad de filas para el horario académico."),
        ]

        for value, field_name, error_message in controles:
            if not value:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "title": field_name,
                    "descripcion": error_message
                })

        cantidad_filas = int(cantidad_filas)

        horario = []

        for fila in range(cantidad_filas):

            hora_inicio = request.POST.get(
                f"hora_inicio_{fila}"
            )

            hora_final = request.POST.get(
                f"hora_final_{fila}"
            )

            materias = {
                "lunes": request.POST.get(f"materia_{fila}_0"),
                "martes": request.POST.get(f"materia_{fila}_1"),
                "miercoles": request.POST.get(f"materia_{fila}_2"),
                "jueves": request.POST.get(f"materia_{fila}_3"),
                "viernes": request.POST.get(f"materia_{fila}_4"),
            }

            # Validar hora de inicio
            if not hora_inicio:
                return JsonResponse({
                    "estado": "fallo",
                    "title": f"Hora de inicio - Fila {fila + 1}",
                    "descripcion": "Debe ingresar la hora de inicio.",
                    "icon": "warning"
                })

            # Validar hora final
            if not hora_final:
                return JsonResponse({
                    "estado": "fallo",
                    "title": f"Hora final - Fila {fila + 1}",
                    "descripcion": "Debe ingresar la hora final.",
                    "icon": "warning"
                })

            # Validar que la hora final sea posterior
            if hora_final <= hora_inicio:
                return JsonResponse({
                    "estado": "fallo",
                    "title": f"Hora inválida - Fila {fila + 1}",
                    "descripcion": "La hora final debe ser posterior a la hora de inicio.",
                    "icon": "warning"
                })

            # Validar al menos una materia
            if not any(materias.values()):
                return JsonResponse({
                    "estado": "fallo",
                    "title": f"Materia - Fila {fila + 1}",
                    "descripcion": "Debe seleccionar al menos una materia en esta fila.",
                    "icon": "warning"
                })

            datos_fila = {
                "hora_inicio": hora_inicio,
                "hora_final": hora_final,
                **materias
            }

            horario.append(datos_fila)

        coordinador = CoordinadorPNF.objects.get(usuario__cedula_identidad=request.session.get("cedula_usuario"))

        periodo = PeriodoCargarNotas.objects.get(id_periodo_academico=periodo_academico)

        encabezado = HorarioAcademica.objects.create(
            id_nucleo=coordinador.nucleo,
            id_pnf=coordinador.pnf,
            id_periodo_academico=periodo,
            id_aula_id=aula,
            id_seccion_id=seccion,
            trayecto=trayecto,
            activo=True
        )

        for fila in range(cantidad_filas): 
            hora_inicio = request.POST.get(f"hora_inicio_{fila}") 
            hora_final = request.POST.get(f"hora_final_{fila}") 

            # DÍAS DE LA SEMANA 
            dias = { 
                0: "Lunes", 
                1: "Martes", 
                2: "Miércoles", 
                3: "Jueves", 
                4: "Viernes", 
            }

            for dia_numero, dia_nombre in dias.items(): 
                materia_id = request.POST.get( f"materia_{fila}_{dia_numero}" ) 

                # Si no hay materia seleccionada ese día, no se crea el detalle  
                if not materia_id: 
                    continue 

                materia_asignada = MateriaAsignada.objects.get(id_materia_asignada=materia_id) 

                DetalleHorario.objects.create( 
                    horario=encabezado, 
                    materia_asignada=materia_asignada, 
                    dia=dia_nombre,
                    hora_inicio=hora_inicio, 
                    hora_fin=hora_final 
                )

        # Ruta donde se almacenara el horario
        def limpiar_nombre(nombre):
            return re.sub(r'[<>:"/\\|?*]', '', str(nombre)).strip()


        municipio = limpiar_nombre(coordinador.nucleo.municipio)
        nombre_pnf = limpiar_nombre(coordinador.pnf.pnf)
        nombre_trayecto = limpiar_nombre(trayecto)

        carpeta_horarios = (
            Path(settings.MEDIA_ROOT)
            / "Horarios Academicos"
            / municipio
            / nombre_pnf
            / nombre_trayecto
        )

        carpeta_horarios.mkdir(
            parents=True,
            exist_ok=True
        )

        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        nombre_archivo = (f"Horario_{trayecto}_{periodo.nombre}_{seccion}_{fecha_hora}.pdf")

        nombre_archivo = limpiar_nombre(nombre_archivo)

        ruta_pdf = carpeta_horarios / nombre_archivo

        # Carpeta raíz
        carpeta_raiz, _ = CarpetaAcademica.objects.get_or_create(
            nombre="Horarios Academicos",
            carpeta_padre=None,
            activa=True
        )

        # Municipio
        carpeta_municipio, _ = CarpetaAcademica.objects.get_or_create(
            nombre=coordinador.nucleo.municipio,
            carpeta_padre=carpeta_raiz,
            activa=True
        )

        # PNF
        carpeta_pnf, _ = CarpetaAcademica.objects.get_or_create(
            nombre=coordinador.pnf.pnf,
            carpeta_padre=carpeta_municipio,
            activa=True
        )

        # Trayecto
        carpeta_trayecto, _ = CarpetaAcademica.objects.get_or_create(
            nombre=trayecto,
            carpeta_padre=carpeta_pnf,
            activa=True
        )

        # Controlador del archivo PDF
        documento = SimpleDocTemplate(
            str(ruta_pdf),
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        elementos = []

        # Encabezado del documento
        estilos = getSampleStyleSheet()

        # Estilo para el texto institucional
        estilo_institucional = ParagraphStyle(
           "Institucional",
            parent=estilos["Normal"],
            alignment=TA_CENTER,
            fontSize=11,
            leading=14,
            spaceAfter=4
        )

        estilo_informacion = ParagraphStyle(
            "Informacion",
            parent=estilos["Normal"],
            alignment=TA_LEFT,
            fontSize=11,
            leading=15,
            spaceAfter=8
        )

        # Logo
        ruta_logo = finders.find("Imagenes/Logo_UPT.png")

        logo = Image(
            ruta_logo,
            width=70,
            height=70
        )

        # Título institucional
        encabezado_institucional = [
            Paragraph(
                "MINISTERIO DEL PODER POPULAR PARA LA EDUCACIÓN UNIVERSITARIA",
                estilo_institucional
            ),
            Paragraph(
                "UNIVERSIDAD POLITÉCNICA TERRITORIAL DEL ESTADO BARINAS JOSÉ FÉLIX RIBAS",
                estilo_institucional
            ),
        ]

        tabla_encabezado = Table(
            [[
                logo,
                encabezado_institucional
            ]],
            colWidths=[85, 647]
        )

        tabla_encabezado.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            # Logo
            ("ALIGN", (0, 0), (0, 0), "LEFT"),

            # Título hacia la izquierda
            ("ALIGN", (1, 0), (1, 0), "LEFT"),

            # Eliminar espacios
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

        elementos.append(tabla_encabezado)
        elementos.append(Spacer(1, 12))


        # Información del horario
        encabezado_pnf = [
            Paragraph(
                f"<b>PNF:</b> {coordinador.pnf}",
                estilo_informacion
            ),
            Paragraph(
                f"<b>TRAYECTO:</b> {trayecto}",
                estilo_informacion
            ),
            Paragraph(
                f"<b>PERÍODO ACADÉMICO:</b> {periodo.nombre}",
                estilo_informacion
            ),
        ]

        elementos.extend(encabezado_pnf)

        estilo_celda = ParagraphStyle(
            "CeldaHorario",
            parent=estilos["Normal"],
            alignment=TA_CENTER,
            fontSize=8,
            leading=10
        )

        # Encabezado horario académico
        datos_horario = [
            [
                "Hora Inicio",
                "Hora Final",
                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
                "Viernes"
            ]
        ]

        # Cuerpo del horario
        for fila in horario:
            datos_fila_pdf = [
                fila["hora_inicio"],
                fila["hora_final"],
                "",
                "",
                "",
                "",
                ""
            ]
            dias = {
                "lunes": 2,
                "martes": 3,
                "miercoles": 4,
                "jueves": 5,
                "viernes": 6,
            }

            for campo, posicion in dias.items():
                materia_id = fila[campo]
                if not materia_id:
                    continue
                materia_asignada = (
                    MateriaAsignada.objects
                    .select_related("materia")
                    .prefetch_related("docentes__docente__usuario")
                    .get(
                        id_materia_asignada=materia_id
                    )
                )

                materia = materia_asignada.materia

                docente_activo = materia_asignada.docentes.filter(
                    activo=True
                ).first()

                if docente_activo:
                    docente = docente_activo.docente

                    nombre_docente = (
                        f"{docente.usuario.nombres} "
                        f"{docente.usuario.apellidos}"
                    )

                datos_fila_pdf[posicion] = Paragraph(
                    f"<b>{materia.codigo}</b><br/>"
                    f"{materia.nombre}<br/>"
                    f"{nombre_docente}",
                    estilo_celda
                )
            datos_horario.append(datos_fila_pdf)

        # Contrador de la tabla
        tabla_horario = Table(
            datos_horario,
            colWidths=[60, 60, 105, 105, 105, 105, 105] # La distancia horizontal de cada celda
        )

        # Estilos para la tabla
        tabla_horario.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            # Todo el contenido centrado
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))

        elementos.append(tabla_horario)

        # Crea el documento
        documento.build(elementos) 

        ruta_relativa = ruta_pdf.relative_to(settings.MEDIA_ROOT)

        DocumentoHorario.objects.create(
            horario=encabezado,
            carpeta=carpeta_trayecto,
            archivo=str(ruta_relativa),
            nombre_archivo=nombre_archivo,
            activo=True
        )

        Bitacora.objects.create(
            nombre_usuario=request.session.get("usuario_nombre"),
            fecha_hora=timezone.now(),
            accion=(
                f"Se registró el horario académico del "
                f"PNF {coordinador.pnf.pnf}, "
                f"Trayecto {trayecto}, "
                f"Período {periodo.nombre}, "
                f"Sección {seccion}."
            )
        )

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Exito",
            "descripcion": "El horario académico se registro exitosamente."
        })

    return render(request, "Coordinador_PNF/horario/registrar_horario.html")

def hor_reg(request):
    return render(request, "Coordinador_PNF/horario/visualizar_horario.html")

