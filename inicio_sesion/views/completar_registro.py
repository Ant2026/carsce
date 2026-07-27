from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string

from inicio_sesion.models import Usuario, Nucleos, Pnf, Contacto, PNFNucleo, UsuarioAsignacion, Nacimiento, Residencia, DatosPreofesion, Discapacidad, InformacionSecundaria, DocumentosEstudiante, PadresEstudiante, EstatusEstudiante, Perfiles

import os
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def datos_registrado(request):
    if not request.session.get("usuario_nombre"):
        return JsonResponse({
            "estado": "no_exite",
            "icon": "error",
            "title": "No Existe",
            "descripcion": "Estimado(a), no ha realizado el proceso autenticación.",
            "url": reverse("inicio_sesion")
        })

    ci_usuario = request.session.get("cedula_usuario")

    datos_basicos = Usuario.objects.filter(cedula_identidad=ci_usuario).first()
    if not datos_basicos:
        return JsonResponse({
            "estado": "no_exite",
            "icon": "error",
            "title": "No Existe",
            "descripcion": "Estimado(a), no se encuentra registrado.",
            "url": reverse("inicio_sesion")
        })

    contacto = Contacto.objects.filter(id_usuario=datos_basicos).first()

    return JsonResponse({
        "usuario": {
            "nombres": datos_basicos.nombres,
            "apellidos": datos_basicos.apellidos,
            "cedula_identidad": datos_basicos.cedula_identidad,
        },
        "contacto": {
            "telefono_personal": contacto.telefono_personal if contacto else "",
            "correo_electronico": contacto.correo_electronico if contacto else "",
        }
    })

def verificar_cedula_representante(request):
    if request.method == "POST":
        nacionalidad = request.POST.get("nacionalidad")
        cedula = request.POST.get("cedula")

        cedula_identidad = f"{nacionalidad}-{cedula}"

        existe = PadresEstudiante.objects.filter(cedula_identidad=cedula_identidad).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def verificar_codigo_opsu(request):
    if request.method == "POST":
        codigo_opsu = request.POST.get("codigo_opsu")

        existe = InformacionSecundaria.objects.filter(codigo_sni_opsu=codigo_opsu).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def completar_registro_personal(request):
    if request.method == "POST":
        genero = request.POST.get("genero")
        estado_civil = request.POST.get("estado_civil")
        
        prefijo_telefono = request.POST.get("prefijo_telefono_secundaria")
        num_telefono = request.POST.get("num_telefono_secundaria")
        
        correo_secundaria = request.POST.get("correo_secundaria")
        dominio_correo_secundaria = request.POST.get("dominio_correo_secundaria")
        
        pais_nacimiento = request.POST.get("pais_nacimiento_personal")
        direccion_nacimiento = request.POST.get("direccion_nacimiento_personal")
        fecha_nacimiento = request.POST.get("fecha_nacimiento_personal")

        condicion_residencia = request.POST.get("condicion_residencia_personal")
        municipio_residencia = request.POST.get("municipio_residencia_personal")
        parroquia_residencia = request.POST.get("parroquia_residencia_personal")
        direccion_domicilio = request.POST.get("direccion_domicilio_personal")

        profesion_pregrado = request.POST.get("profesion_pregrado_personal")
        universidad_pregrado = request.POST.get("universidad_pregrado_personal")
        pais_profesion = request.POST.get("pais_profesion_personal")

        campos = [
            (genero, "Genero", "Por favor, selecciona el genero."),
            (estado_civil, "estado Civil", "Por favor, selecciona el estado civil."),
            (correo_secundaria, "Nombre del Correo Secundario", "Por favor, ingrese el nombre del correo secundario."),
            (dominio_correo_secundaria, "Dominio del Correo Secundario", "Por favor, selecciona el dominio del correo secundario."),
            (pais_nacimiento, "País de Nacimiento", "Por favor, selecciona el país de nacimiento."),
            (direccion_nacimiento, "Dirección de Nacimiento", "Por favor, ingresa la dirección de nacimiento."),
            (fecha_nacimiento, "Fecha de Nacimiento", "Por favor, ingresa la fecha de nacimiento."),
            (condicion_residencia, "Condición de Residencia", "Por favor, selecciona la condición de residencia."),
            (municipio_residencia, "Municipio de Residencia", "Por favor, selecciona el municipio de residencia."),
            (parroquia_residencia, "Parroquia de Residencia", "Por favor, selecciona la parroquia de residencia."),
            (direccion_domicilio, "Dirección de Residencia", "Por favor, ingresa la dirección de residencia."),
            (profesion_pregrado, "Profesión Posgrado", "Por favor, ingresa la profesión."),
            (universidad_pregrado, "Universidad Posgrado", "Por favor, ingresa la universidad."),
            (pais_profesion, "País Posgrado", "Por favor, selecciona el país de posgrado."),
        ]

        for valor, campo, mensaje in campos:
            if not valor:
                return JsonResponse({
                    "title": campo,
                    "descripcion": mensaje,
                    "icon": "warning"
                })

        if prefijo_telefono and not num_telefono:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Debe de ingresar los número telefonicos, sino vuelve a seleccionar TLF.",
                "icon": "warning"
            })
        
        if not prefijo_telefono and num_telefono:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Debe seleccionar el prefijo telefonico, sino vuelve a seleccionar TLF.",
                "icon": "warning"
            })
        
        telefono_sucundario = (prefijo_telefono + num_telefono if prefijo_telefono and num_telefono else "N/A")

        if request.POST.get("estado_nacimiento_personal"):
            estado_nacimiento = request.POST.get("estado_nacimiento_personal")
        elif request.POST.get("estado_novzla_personal"):
            estado_nacimiento = request.POST.get("estado_novzla_personal")     
        else:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Por favor, selecciona o ingrese el estado de nacimiento.",
                "icon": "warning"
            })
        
        if request.POST.get("municipio_nacimiento_personal"):
            municipio_nacimiento = request.POST.get("municipio_nacimiento_personal")
        elif request.POST.get("municipio_novzla_personal"):
            municipio_nacimiento = request.POST.get("municipio_novzla_personal")
        else:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Por favor, selecciona o ingrese el municipio de nacimiento.",
                "icon": "warning"
            })
        
        if request.POST.get("parroquia_nacimiento_personal"):
            parroquia_nacimiento = request.POST.get("parroquia_nacimiento_personal")
        elif request.POST.get("parroquia_novzla_personal"):
            parroquia_nacimiento = request.POST.get("parroquia_novzla_personal")
        else:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Por favor, selecciona o ingrese la parroquia de nacimiento.",
                "icon": "warning"
            })
        
        correo_alternativo = correo_secundaria + dominio_correo_secundaria

        usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()
        usuario.genero = genero
        usuario.estado_civil = estado_civil
        usuario.save()

        contacto = Contacto.objects.filter(id_usuario=usuario).first()
        contacto.telefono_suplete = telefono_sucundario
        contacto.correo_alternativo = correo_alternativo
        contacto.save()

        Nacimiento.objects.create(pais=pais_nacimiento, estado=estado_nacimiento, municipio=municipio_nacimiento, parroquia=parroquia_nacimiento, direccion_nacimiento=direccion_nacimiento, fecha_nacimiento=fecha_nacimiento, id_usuario=usuario)

        Residencia.objects.create(condicion_residencia=condicion_residencia, municipio=municipio_residencia, parroquia=parroquia_residencia, direccion_residencia=direccion_domicilio, id_usuario=usuario)

        DatosPreofesion.objects.create(profesion_pregrado=profesion_pregrado, universidad_egreso_pregrado=universidad_pregrado, pais_profesion_pregrado=pais_profesion, id_usuario=usuario)
        
        request.session['registro_completado'] = True

        return JsonResponse({
            "estado": "exito",
            "title": "Exito",
            "descripcion": "Se registro exitosamente",
            "icon": "success",
            "url": reverse("panel_usuario")
        })
    
    return render(request, "Actualizaciones/completar_registro_personal.html")

def completar_registro_estudiante(request):
    if request.method == "POST":
        genero = request.POST.get("genero")
        estado_civil = request.POST.get("estado_civil")
        
        nombres_representante = request.POST.get("nombres_representante")
        apellidos_representante = request.POST.get("apellidos_representante")
        nacionalidad_representante = request.POST.get("nacionalidad_representante")
        ci_representante = request.POST.get("ci_representante")
        prefijo_num2 = request.POST.get("prefijo_num2")
        telefono_representante = request.POST.get("telefono_representante")
        parestencorepresentante = request.POST.get("parestencorepresentante")
        
        nombres_otrorepresentante = request.POST.get("nombres_otrorepresentante")
        apellidos_otrorepresentante = request.POST.get("apellidos_otrorepresentante")
        nacionalidad_otrorepresentante = request.POST.get("nacionalidad_otrorepresentante")
        ci_otrorepresentante = request.POST.get("ci_otrorepresentante")
        prefijo_num3 = request.POST.get("prefijo_num3")
        telefono_otrorepresentante = request.POST.get("telefono_otrorepresentante")
        parestencootrorepresentante = request.POST.get("parestencootrorepresentante")
        
        num_telefono = request.POST.get("num_telefono_secundaria")
        prefijo_telefono = request.POST.get("prefijo_telefono_secundaria")
        correo_secundaria = request.POST.get("correo_secundaria")
        dominio_correo_secundaria = request.POST.get("dominio_correo_secundaria")
        
        pais_nacimiento = request.POST.get("pais_nacimiento_estudiante")

        if request.POST.get("estado_nacimiento_estudiante"):
            estado_nacimiento = request.POST.get("estado_nacimiento_estudiante")
        elif request.POST.get("estado_novzla_estudiante"):
            estado_nacimiento = request.POST.get("estado_novzla_estudiante")
        else:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Por favor, selecciona o ingrese el estado de nacimiento.",
                "icon": "warning"
            })

        if request.POST.get("municipio_nacimiento_estudiante"):
            municipio_nacimiento = request.POST.get("municipio_nacimiento_estudiante")
        elif request.POST.get("municipio_novzla_estudiante"):
            municipio_nacimiento = request.POST.get("municipio_novzla_estudiante")
        else:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Por favor, selecciona o ingrese el municipio de nacimiento.",
                "icon": "warning"
            })

        if request.POST.get("parroquia_nacimiento_estudiante"):
            parroquia_nacimiento = request.POST.get("parroquia_nacimiento_estudiante")
        elif request.POST.get("parroquia_novzla_estudiante"):
            parroquia_nacimiento = request.POST.get("parroquia_novzla_estudiante")
        else:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Por favor, selecciona o ingrese el parroquia de nacimiento.",
                "icon": "warning"
            })
     
        direccion_nacimiento = request.POST.get("direccion_nacimiento_estudiante")
        fecha_nacimiento = request.POST.get("fecha_nacimiento_estudiante")

        condicion_residencia = request.POST.get("condicion_residencia_estudiante")
        municipio_residencia = request.POST.get("municipio_residencia_estudiante")
        parroquia_residencia = request.POST.get("parroquia_residencia_estudiante")
        direccion_domicilio = request.POST.get("direccion_domicilio_estudiante")

        tipos_secundaria = request.POST.get("tipos_secundaria")
        nombre_secundaria = request.POST.get("nombre_secundaria")
        fecha_graduacion = request.POST.get("fecha_graduacion")
        codigo_opsu = request.POST.get("codigo_opsu")

        if prefijo_telefono and not num_telefono:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Debe de ingresar los número telefonicos, sino vuelve a seleccionar TLF.",
                "icon": "warning"
            })
        
        if not prefijo_telefono and num_telefono:
            return JsonResponse({
                "title": "Vacío",
                "descripcion": "Debe seleccionar el prefijo telefonico, sino vuelve a seleccionar TLF.",
                "icon": "warning"
            })

        if request.POST.get("carnet_dispacidad"):
            carnet_dispacidad = request.POST.get("carnet_dispacidad")
        else:
            carnet_dispacidad = "N/A"
        
        if request.POST.get("registro_medico"):
            registro_medico = request.POST.get("registro_medico")
        else:
            registro_medico = "N/A"

        if request.POST.get("tipo_discapacidad"):
            tipo_discapacidad = request.POST.get("tipo_discapacidad")
        else:
            tipo_discapacidad = "N/A"
        
        if request.POST.get("grado_discapacidad"):
            grado_discapacidad = request.POST.get("grado_discapacidad")
        else:
            grado_discapacidad = "N/A"
        
        if request.POST.get("causa_discapacidad"):
            causa_discapacidad = request.POST.get("causa_discapacidad")
        else:
            causa_discapacidad = "N/A"

        campos = [
            (genero, "Genero", "Por favor, selecciona el genero."),
            (estado_civil, "estado Civil", "Por favor, selecciona el estado civil."),

            (correo_secundaria, "Nombre del Correo Secundario", "Por favor, ingrese el nombre del correo secundario."),
            (dominio_correo_secundaria, "Dominio del Correo Secundario", "Por favor, selecciona el dominio del correo secundario."),

            (pais_nacimiento, "País de Nacimiento", "Por favor, selecciona el país de nacimiento."),
            (direccion_nacimiento, "Dirección de Nacimiento", "Por favor, ingresa la dirección de nacimiento."),
            (fecha_nacimiento, "Fecha de Nacimiento", "Por favor, ingresa la fecha de nacimiento."),

            (condicion_residencia, "Condición de Residencia", "Por favor, selecciona la condición de residencia."),
            (municipio_residencia, "Municipio de Residencia", "Por favor, selecciona el municipio de residencia."),
            (parroquia_residencia, "Parroquia de Residencia", "Por favor, selecciona la parroquia de residencia."),
            (direccion_domicilio, "Dirección de Residencia", "Por favor, ingresa la dirección de residencia."),

            (tipos_secundaria, "Tipo de Secundaria", "Por favor, seleccione el tipo de institución."),
            (nombre_secundaria, "Nombre de la Secundaria", "Por favor, ingrese el nombre de la institución."),
            (fecha_graduacion, "Fecha de Graduación", "Por favor, ingrese la fecha de graduación."),
            (codigo_opsu, "Código OPSU", "Por favor, ingrese el código de la opsu."),

            (nombres_representante, "Nombre del Representante", "Por favor, ingrese el nombre del representante."),
            (apellidos_representante, "Apellido del Representante", "Por favor, ingrese el apellido del representante."),
            (nacionalidad_representante, "Nacionalidad del Representante", "Por favor, seleccione la nacionalidad del representante."),
            (ci_representante, "Cedula de Identidad del Representante", "Por favor, ingrese los números de la cedula de identidad del representante."),
            (prefijo_num2, "Prefijo de Telefonico del Representante", "Por favor, seleccione el prefijo telefonico del representante."),
            (telefono_representante, "Números Telefonico del Representante", "Por favor, ingrese los números telefonico del representante."),
            (parestencorepresentante, "Parentesco del Representante", "Por favor, seleccione el parentesco del representante."),
        ]

        for valor, campo, mensaje in campos:
            if not valor:
                return JsonResponse({
                    "title": campo,
                    "descripcion": mensaje,
                    "icon": "warning"
                })
            
        campos_otro_representante = [
            (nombres_otrorepresentante, "Nombres", "Debe ingresar los nombres del otro representante."),
            (apellidos_otrorepresentante, "Apellidos", "Debe ingresar los apellidos del otro representante."),
            (nacionalidad_otrorepresentante, "Nacionalidad", "Debe seleccionar la nacionalidad del otro representante."),
            (ci_otrorepresentante, "Cédula", "Debe ingresar la cédula del otro representante."),
            (prefijo_num3, "Prefijo telefónico", "Debe seleccionar el prefijo telefónico."),
            (telefono_otrorepresentante, "Teléfono", "Debe ingresar el número telefónico."),
            (parestencootrorepresentante, "Parentesco", "Debe seleccionar el parentesco.")
        ]

        if any(valor for valor, _, _ in campos_otro_representante):

            for valor, titulo, mensaje in campos_otro_representante:
                if not valor:
                    return JsonResponse({
                        "title": titulo,
                        "descripcion": mensaje,
                        "icon": "warning"
                    })
                
        telefono = (prefijo_telefono + num_telefono if prefijo_telefono and num_telefono else "N/A")
        correo_electronico = correo_secundaria+dominio_correo_secundaria
        ci_representante_principal = nacionalidad_representante + "-" + ci_representante
        tlf_representante_principal = prefijo_num2+telefono_representante
    
        usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()
        usuario.genero = genero
        usuario.estado_civil = estado_civil
        usuario.save()

        contacto = Contacto.objects.filter(id_usuario=usuario).first()
        contacto.telefono_suplete = telefono
        contacto.correo_alternativo = correo_electronico
        contacto.save()

        PadresEstudiante.objects.create(nombres=nombres_representante, apellidos=apellidos_representante, cedula_identidad=ci_representante_principal, telefono=tlf_representante_principal, parentesco=parestencorepresentante, id_usuario=usuario)

        Nacimiento.objects.create(pais=pais_nacimiento, estado=estado_nacimiento, municipio=municipio_nacimiento, parroquia=parroquia_nacimiento, direccion_nacimiento=direccion_nacimiento, fecha_nacimiento=fecha_nacimiento, id_usuario=usuario)

        Residencia.objects.create(condicion_residencia=condicion_residencia, municipio=municipio_residencia, parroquia=parroquia_residencia, direccion_residencia=direccion_domicilio, id_usuario=usuario)

        InformacionSecundaria.objects.create(tipo_institucion=tipos_secundaria, nombre_institucion=nombre_secundaria, fecha_grado=fecha_graduacion, codigo_sni_opsu=codigo_opsu, id_usuario=usuario)

        Discapacidad.objects.create(codigo_carnet_discapacidad=carnet_dispacidad, nro_registro_medico=registro_medico, tipo_discapacidad=tipo_discapacidad, grado_discapacidad=grado_discapacidad, causa_discapacidad=causa_discapacidad, id_usuario=usuario)

        if nombres_otrorepresentante and apellidos_otrorepresentante and nacionalidad_otrorepresentante and ci_otrorepresentante and prefijo_num3 and telefono_otrorepresentante and parestencootrorepresentante:
            ci_representante_secundario = nacionalidad_otrorepresentante + "-" + ci_otrorepresentante
            telefono_representante_secundario = prefijo_num3 + telefono_otrorepresentante

            PadresEstudiante.objects.create(nombres=nombres_otrorepresentante, apellidos=apellidos_otrorepresentante, cedula_identidad=ci_representante_secundario, telefono=telefono_representante_secundario, parentesco=parestencootrorepresentante, id_usuario=usuario)

        nucleos = {
            "Barinas": request.POST.getlist("pnf_Barinas"),
            "Barinitas": request.POST.getlist("pnf_Barinitas"),
            "Sopoco": request.POST.getlist("pnf_Sopoco"),
            "Pedraza": request.POST.getlist("pnf_Pedraza"),
        }

        asignacion_base = UsuarioAsignacion.objects.filter(id_usuario=usuario, id_perfil_id=5).first()

        primera_asignacion = True
        for nombre_nucleo, lista_pnfs in nucleos.items():
            if not lista_pnfs:
                continue

            nucleo = Nucleos.objects.filter(municipio=nombre_nucleo).first()

            for pnf_id in lista_pnfs:
                pnf = Pnf.objects.filter(id_pnf=pnf_id).first()

                if primera_asignacion and asignacion_base:
                    asignacion_base.id_nucleo = nucleo
                    asignacion_base.id_pnf = pnf
                    asignacion_base.save()
                    asignacion = asignacion_base
                    primera_asignacion = False
                else:
                    perfil_estudiante = Perfiles.objects.get(perfil="Estudiante")

                    asignacion = UsuarioAsignacion.objects.create(
                        id_usuario=usuario,
                        id_perfil=perfil_estudiante,
                        id_nucleo=nucleo,
                        id_pnf=pnf
                    )
                    
                EstatusEstudiante.objects.create(
                    estatus="Pre-Inscrito(a)",
                    estado="Espera",
                    ingreso="Bachiller",
                    trayecto="Inicial",
                    descripcion_ingreso="No ha presentado Inicial",
                    fecha_ingreso=timezone.now().date(),
                    id_asignacion=asignacion
                )

        nombre_estudiante = f"{usuario.nombres}_{usuario.apellidos}".replace(" ", "_")

        base_path = os.path.join(settings.BASE_DIR, "media", "documentosEstudiante", nombre_estudiante)
        
        os.makedirs(base_path, exist_ok=True)

        fs = FileSystemStorage(location=base_path)

        documentos = {
            "Cédula de Identidad": request.FILES.get("CI_estudiante"),
            "Título de Bachiller": request.FILES.get("TBachiller_estudiante"),
            "Sabana de Notas": request.FILES.get("SNotas_estudiante"),
            "OPSU": request.FILES.get("OPSU_estudiante"),
        }

        for nombre, archivo in documentos.items():
            if archivo:
                extension = os.path.splitext(archivo.name)[1]
                nuevo_nombre = f"{nombre}{extension}"
                filename = fs.save(nuevo_nombre, archivo)

                file_path = os.path.join("media", "documentosEstudiante", nombre_estudiante, filename)
                DocumentosEstudiante.objects.update_or_create(id_usuario=usuario, nombre_documento=nombre,
                    defaults={
                        "archivo": file_path
                    }
                )

        ruta_pdf = generar_documento_inscripcion(estudiante=usuario)
        
        html_email = render_to_string(
            "Email/comprobante_inscripcion.html",
            {
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "fecha": timezone.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )

        correo = EmailMessage(
            subject="Comprobante de Preinscripción - UPT José Félix Ribas",
            body=html_email,
            from_email="uptjfr2025@gmail.com",
            to=[contacto.correo_electronico]
        )

        correo.content_subtype = "html"
        correo.attach_file(ruta_pdf)
        correo.send()
        
        request.session['registro_completado'] = True
        
        return JsonResponse({
            "estado": "exito",
            "title": "Exito",
            "descripcion": "Se registraron exitosamente",
            "icon": "success"
        })
        
    return render(request, "Actualizaciones/completar_registro_estudiante.html")

def mostrar_pnfs_cursar(request):
    nucleo_seleccionado = request.POST.get("nucleo")

    nucleo = Nucleos.objects.filter(municipio=nucleo_seleccionado).first()
    if not nucleo:
        return JsonResponse({
            "estado": "fallo",
            "title": "Error",
            "icon": "error",
            "descripcion": "No hay pnfs asignado al presente núcleo.",
            "pnfs": []
        })

    pnfs = PNFNucleo.objects.select_related("id_pnf").filter(id_nucleo=nucleo)
    
    datos = []
    for pnf_nucleo in pnfs:
        datos.append({
            "id": pnf_nucleo.id_pnf.id_pnf,
            "nombre": pnf_nucleo.id_pnf.pnf,
            "codigo": pnf_nucleo.id_pnf.codigo
        })

    return JsonResponse({ 
        "estado": "exito",
        "pnfs": datos 
    })

def completar_registro_pe(request):
    if request.method == "POST":
        nombres_representante = request.POST.get("nombres_representante")
        apellidos_representante = request.POST.get("apellidos_representante")
        nacionalidad_representante = request.POST.get("nacionalidad_representante")
        ci_representante = request.POST.get("ci_representante")
        prefijo_num2 = request.POST.get("prefijo_num2")
        telefono_representante = request.POST.get("telefono_representante")
        parestencorepresentante = request.POST.get("parestencorepresentante")
        
        nombres_otrorepresentante = request.POST.get("nombres_otrorepresentante")
        apellidos_otrorepresentante = request.POST.get("apellidos_otrorepresentante")
        nacionalidad_otrorepresentante = request.POST.get("nacionalidad_otrorepresentante")
        ci_otrorepresentante = request.POST.get("ci_otrorepresentante")
        prefijo_num3 = request.POST.get("prefijo_num3")
        telefono_otrorepresentante = request.POST.get("telefono_otrorepresentante")
        parestencootrorepresentante = request.POST.get("parestencootrorepresentante")

        tipos_secundaria = request.POST.get("tipos_secundaria")
        nombre_secundaria = request.POST.get("nombre_secundaria")
        fecha_graduacion = request.POST.get("fecha_graduacion")
        codigo_opsu = request.POST.get("codigo_opsu")

        if request.POST.get("carnet_dispacidad"):
            carnet_dispacidad = request.POST.get("carnet_dispacidad")
        else:
            carnet_dispacidad = "N/A"
        
        if request.POST.get("registro_medico"):
            registro_medico = request.POST.get("registro_medico")
        else:
            registro_medico = "N/A"

        if request.POST.get("tipo_discapacidad"):
            tipo_discapacidad = request.POST.get("tipo_discapacidad")
        else:
            tipo_discapacidad = "N/A"
        
        if request.POST.get("grado_discapacidad"):
            grado_discapacidad = request.POST.get("grado_discapacidad")
        else:
            grado_discapacidad = "N/A"
        
        if request.POST.get("causa_discapacidad"):
            causa_discapacidad = request.POST.get("causa_discapacidad")
        else:
            causa_discapacidad = "N/A"

        campos = [
            (tipos_secundaria, "Tipo de Secundaria", "Por favor, seleccione el tipo de institución."),
            (nombre_secundaria, "Nombre de la Secundaria", "Por favor, ingrese el nombre de la institución."),
            (fecha_graduacion, "Fecha de Graduación", "Por favor, ingrese la fecha de graduación."),
            (codigo_opsu, "Código OPSU", "Por favor, ingrese el código de la opsu."),

            (nombres_representante, "Nombre del Representante", "Por favor, ingrese el nombre del representante."),
            (apellidos_representante, "Apellido del Representante", "Por favor, ingrese el apellido del representante."),
            (nacionalidad_representante, "Nacionalidad del Representante", "Por favor, seleccione la nacionalidad del representante."),
            (ci_representante, "Cedula de Identidad del Representante", "Por favor, ingrese los números de la cedula de identidad del representante."),
            (prefijo_num2, "Prefijo de Telefonico del Representante", "Por favor, seleccione el prefijo telefonico del representante."),
            (telefono_representante, "Números Telefonico del Representante", "Por favor, ingrese los números telefonico del representante."),
            (parestencorepresentante, "Parentesco del Representante", "Por favor, seleccione el parentesco del representante."),
        ]

        for valor, campo, mensaje in campos:
            if not valor:
                return JsonResponse({
                    "title": campo,
                    "descripcion": mensaje,
                    "icon": "warning"
                })

        campos_otro_representante = [
            (nombres_otrorepresentante, "Nombres", "Debe ingresar los nombres del otro representante."),
            (apellidos_otrorepresentante, "Apellidos", "Debe ingresar los apellidos del otro representante."),
            (nacionalidad_otrorepresentante, "Nacionalidad", "Debe seleccionar la nacionalidad del otro representante."),
            (ci_otrorepresentante, "Cédula", "Debe ingresar la cédula del otro representante."),
            (prefijo_num3, "Prefijo telefónico", "Debe seleccionar el prefijo telefónico."),
            (telefono_otrorepresentante, "Teléfono", "Debe ingresar el número telefónico."),
            (parestencootrorepresentante, "Parentesco", "Debe seleccionar el parentesco.")
        ]

        if any(valor for valor, _, _ in campos_otro_representante):
            for valor, titulo, mensaje in campos_otro_representante:
                if not valor:
                    return JsonResponse({
                        "title": titulo,
                        "descripcion": mensaje,
                        "icon": "warning"
                    })

        ci_representante_principal = nacionalidad_representante + "-" + ci_representante
        tlf_representante_principal = prefijo_num2 + telefono_representante

        usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()

        PadresEstudiante.objects.create(nombres=nombres_representante, apellidos=apellidos_representante, cedula_identidad=ci_representante_principal, telefono=tlf_representante_principal, parentesco=parestencorepresentante, id_usuario=usuario)

        InformacionSecundaria.objects.create(tipo_institucion=tipos_secundaria, nombre_institucion=nombre_secundaria, fecha_grado=fecha_graduacion, codigo_sni_opsu=codigo_opsu, id_usuario=usuario)

        Discapacidad.objects.create(codigo_carnet_discapacidad=carnet_dispacidad, nro_registro_medico=registro_medico, tipo_discapacidad=tipo_discapacidad, grado_discapacidad=grado_discapacidad, causa_discapacidad=causa_discapacidad, id_usuario=usuario)

        if nombres_otrorepresentante and apellidos_otrorepresentante and nacionalidad_otrorepresentante and ci_otrorepresentante and prefijo_num3 and telefono_otrorepresentante and parestencootrorepresentante:         
            ci_otrorepresentante = nacionalidad_otrorepresentante + "-" + ci_otrorepresentante
            tlf_representante_principal = prefijo_num3 + telefono_otrorepresentante
            
            PadresEstudiante.objects.create(nombres=nombres_otrorepresentante, apellidos=apellidos_otrorepresentante, cedula_identidad=ci_otrorepresentante, telefono=telefono_otrorepresentante, parentesco=parestencootrorepresentante, id_usuario=usuario)

        nucleos = {
            "Barinas": request.POST.getlist("pnf_Barinas"),
            "Barinitas": request.POST.getlist("pnf_Barinitas"),
            "Sopoco": request.POST.getlist("pnf_Sopoco"),
            "Pedraza": request.POST.getlist("pnf_Pedraza"),
        }

        asignacion_base = UsuarioAsignacion.objects.filter(id_usuario=usuario, id_perfil_id=5).first()

        primera_asignacion = True
        for nombre_nucleo, lista_pnfs in nucleos.items():
            if not lista_pnfs:
                continue

            nucleo = Nucleos.objects.filter(municipio=nombre_nucleo).first()

            for pnf_id in lista_pnfs:
                pnf = Pnf.objects.filter(id_pnf=pnf_id).first()

                if primera_asignacion and asignacion_base:
                    asignacion_base.id_nucleo = nucleo
                    asignacion_base.id_pnf = pnf
                    asignacion_base.save()
                    asignacion = asignacion_base
                    primera_asignacion = False
                else:
                    perfil_estudiante = Perfiles.objects.get(perfil="Estudiante")

                    asignacion = UsuarioAsignacion.objects.create(
                        id_usuario=usuario,
                        id_perfil=perfil_estudiante,
                        id_nucleo=nucleo,
                        id_pnf=pnf
                    )
                    
                EstatusEstudiante.objects.create(
                    estatus="Pre-Inscrito(a)",
                    estado="Espera",
                    ingreso="Bachiller",
                    trayecto="Inicial",
                    descripcion_ingreso="No ha presentado Inicial",
                    fecha_ingreso=timezone.now().date(),
                    id_asignacion=asignacion
                )
            
        nombre_estudiante = f"{usuario.nombres}_{usuario.apellidos}".replace(" ", "_")

        base_path = os.path.join(settings.BASE_DIR, "media", "documentosEstudiante", nombre_estudiante)
        
        os.makedirs(base_path, exist_ok=True)

        fs = FileSystemStorage(location=base_path)

        documentos = {
            "Cédula de Identidad": request.FILES.get("CI_estudiante"),
            "Título de Bachiller": request.FILES.get("TBachiller_estudiante"),
            "Sabana de Notas": request.FILES.get("SNotas_estudiante"),
            "OPSU": request.FILES.get("OPSU_estudiante"),
        }

        for nombre, archivo in documentos.items():
            if archivo:
                extension = os.path.splitext(archivo.name)[1]
                nuevo_nombre = f"{nombre}{extension}"
                filename = fs.save(nuevo_nombre, archivo)

                file_path = os.path.join(
                    "media",
                    "documentosEstudiante",
                    nombre_estudiante,
                    filename)

                DocumentosEstudiante.objects.update_or_create(id_usuario=usuario, nombre_documento=nombre,
                    defaults={
                        "archivo": file_path
                    })

        contacto = Contacto.objects.filter(id_usuario=usuario).first()
                
        ruta_pdf = generar_documento_inscripcion(estudiante=usuario)

        html_email = render_to_string(
            "Email/comprobante_inscripcion.html",
            {
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "fecha": timezone.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )

        correo = EmailMessage(
            subject="Comprobante de Preinscripción - UPT José Félix Ribas",
            body=html_email,
            from_email="uptjfr2025@gmail.com",
            to=[contacto.correo_electronico]
        )

        correo.content_subtype = "html"
        correo.attach_file(ruta_pdf)
        correo.send()

        request.session['registro_completado'] = True

        return JsonResponse({
            "estado": "exito",
            "title": "Exito",
            "descripcion": "Se registraron exitosamente",
            "icon": "success"
        })

    return render(request, "Actualizaciones/completar_registro_pe.html")

def generar_documento_inscripcion(estudiante):
    carpeta = os.path.join(settings.MEDIA_ROOT, "comprobantes", "preinscripciones")

    os.makedirs(carpeta, exist_ok=True)

    nombre_archivo = (f"comprobante_preinscripcion_{estudiante.cedula_identidad}.pdf")

    ruta_archivo = os.path.join(carpeta,nombre_archivo)

    documento = SimpleDocTemplate(
        ruta_archivo,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloPersonalizado",
        parent=estilos["Title"],
        fontName="Times-Roman",
        fontSize=18,
        leading=32,
        alignment=TA_CENTER
    )

    estilo_datos = ParagraphStyle(
        "DatosPersonalizados",
        parent=estilos["Normal"],
        fontName="Times-Roman",
        fontSize=14,
        leading=25,
        alignment=TA_LEFT
    )

    estilo_final = ParagraphStyle(
        "TextoFinal",
        parent=estilos["Normal"],
        fontName="Times-Roman",
        fontSize=14,
        leading=22,
        alignment=TA_LEFT
    )

    logo_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "Imagenes",
        "Logo_UPT.png"
    )

    logo = Image(logo_path, width=2.3*cm, height=2.3*cm)

    titulo = Paragraph(
        "<b>COMPROBANTE DE PREINSCRIPCIÓN</b>",
        estilo_titulo
    )

    cabecera = Table(
        [[logo, titulo]],
        colWidths=[3*cm, 13*cm]
    )

    cabecera.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "CENTER"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))

    contenido = []

    contenido.append(cabecera)
    contenido.append(Spacer(1,20))

    fecha_actual = timezone.now()

    asignaciones = UsuarioAsignacion.objects.filter(
        id_usuario=estudiante,
        id_perfil_id=5
    ).select_related("id_nucleo", "id_pnf")
    detalle_pnf = []

    for asignacion in asignaciones:
        estatus = EstatusEstudiante.objects.filter(
            id_asignacion=asignacion
        ).first()

        detalle_pnf.append(
            f"el Programa Nacional de Formación (PNF) "
            f"{asignacion.id_pnf.nombre_pnf}, correspondiente al núcleo "
            f"{asignacion.id_nucleo.municipio}, con estatus "
            f"'{estatus.estatus}' y estado '{estatus.estado}'"
        )

    parrafo_pnf = "; ".join(detalle_pnf) + "."

    datos = [
        (
            f"La Universidad Politécnica Territorial del Estado Barinas "
            f'"José Félix Ribas" certifica que el(la) ciudadano(a) '
            f"{estudiante.nombres} {estudiante.apellidos}, titular de la cédula "
            f"de identidad N.º {estudiante.cedula_identidad}, realizó "
            f"satisfactoriamente el proceso de preinscripción académica a través "
            f"de la Plataforma Digital para la Gestión de CARSCE."
        ),

        (
            f"Como resultado del proceso, el estudiante quedó registrado en "
            f"{parrafo_pnf}"
        ),

        (
            f"El presente comprobante fue emitido el "
            f"{fecha_actual.strftime('%d/%m/%Y')} a las "
            f"{fecha_actual.strftime('%H:%M:%S')} y constituye una constancia "
            f"electrónica del registro efectuado en el sistema institucional de "
            f"la Universidad Politécnica Territorial del Estado Barinas "
            f'"José Félix Ribas".'
        )
    ]

    for dato in datos:
        contenido.append(Paragraph(dato, estilo_datos))
        contenido.append(Spacer(1, 10))

    contenido.append(Spacer(1, 20))
    contenido.append(
        Paragraph(
            "Este documento confirma que el estudiante realizó correctamente el proceso de preinscripción.",
            estilo_final
        )
    )

    documento.build(contenido)

    return ruta_archivo