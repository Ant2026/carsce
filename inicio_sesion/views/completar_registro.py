from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse

from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import Q

from inicio_sesion.models import Usuario, Nucleos, Pnf, Contacto, PNFNucleo,  Nacimiento, Residencia, Estudiante, Docente, CoordinadorPNF, ControlEstudio, DirectorGeneral, ContactoAuxiliar, Discapacidad, EstatusEstudiante, DocumentosEstudiante, InformacionSecundaria, DatosPreofesion 

import os
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def datos_usr_admin(request):
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
            "genero": datos_basicos.genero,
            "estado_civil": datos_basicos.estado_civil
        },
        "contacto": {
            "telefono_personal": contacto.telefono_personal if contacto else "",
            "correo_electronico": contacto.correo_electronico if contacto else "",
        }
    })

def validar_ci_auxiliar(request):
    if request.method == "POST":
        nacionalidad = request.POST.get("nacionalidad")
        cedula = request.POST.get("cedula")

        existe = ContactoAuxiliar.objects.filter(cedula_identidad=f"{nacionalidad}-{cedula}").exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def validar_cod_opsu(request):
    if request.method == "POST":
        codigo_opsu = request.POST.get("codigo")

        existe = InformacionSecundaria.objects.filter(codigo_sni_opsu=codigo_opsu).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def validar_ci_usr(request):
    if request.method == "POST":
        nacionalidad = request.POST.get("nacionalidad")
        cedula = request.POST.get("cedula")

        existe = Usuario.objects.filter(cedula_identidad=f"{nacionalidad}-{cedula}").exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def validar_email(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        dominio = request.POST.get("dominio")

        email = f"{correo}{dominio}"

        existe = Contacto.objects.filter(
            Q(correo_electronico=email) |
            Q(correo_alternativo=email)
        ).exists()

        return JsonResponse({"existe": existe})

def pnfs_cursar(request):
    nucleo_seleccionado = request.POST.get("nucleo")
    print(nucleo_seleccionado)
    nucleo = Nucleos.objects.filter(municipio=nucleo_seleccionado).first()
    print(nucleo)
    if not nucleo:
        return JsonResponse({"pnfs": []})

    pnfs = PNFNucleo.objects.select_related("id_pnf").filter(id_nucleo=nucleo)

    datos = []
    for pnf_nucleo in pnfs:
        datos.append({
            "id": pnf_nucleo.id_pnf.id_pnf,
            "nombre": pnf_nucleo.id_pnf.pnf
        })

    return JsonResponse({
        "pnfs": datos
    })

def comp_registro(request):
    if request.method == "POST":
        genero = request.POST.get("genero")
        estado_civil = request.POST.get("estado_civil")
            
        prefijo_telefono_principal = request.POST.get("prefijo_telefono_principal")
        num_telefono_principal = request.POST.get("num_telefono_principal")
        prefijo_telefono_secundaria = request.POST.get("prefijo_telefono_secundaria")
        num_telefono_secundaria = request.POST.get("num_telefono_secundaria")

        if not prefijo_telefono_secundaria and num_telefono_secundaria:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacío",
                "descripcion": "Debe seleccionar el prefijo telefónico o dejar vacío el número telefónico.",
                "icon": "warning"
            })
                            
        if prefijo_telefono_secundaria and not num_telefono_secundaria:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacío",
                "descripcion": "Debe ingresar el número telefónico o seleccionar la opción TLF.",
                "icon": "warning"
            })

        telefono_secundario = (
            prefijo_telefono_secundaria + num_telefono_secundaria
            if prefijo_telefono_secundaria and num_telefono_secundaria
            else "N/A"
        )
                    
        correo_principal = request.POST.get("correo_principal")
        dominio_correo_principal = request.POST.get("dominio_correo_principal")
        correo_secundaria = request.POST.get("correo_secundaria")
        dominio_correo_secundaria = request.POST.get("dominio_correo_secundaria")
        
        pais_nacimiento = request.POST.get("pais_nacimiento")
        
        direccion_nacimiento = request.POST.get("direccion_nacimiento")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")

        condicion_residencia = request.POST.get("condicion_residencia")
        municipio_residencia = request.POST.get("municipio_residencia")
        parroquia_residencia = request.POST.get("parroquia_residencia")
        direccion_domicilio = request.POST.get("direccion_domicilio")

        profesion_pregrado = request.POST.get("profesion_pregrado")
        universidad_pregrado = request.POST.get("universidad_pregrado")
        pais_profesion = request.POST.get("pais_profesion")
        
        tipos_secundaria = request.POST.get("tipos_secundaria")
        nombre_secundaria = request.POST.get("nombre_secundaria")
        fecha_graduacion = request.POST.get("fecha_graduacion")
        codigo_opsu = request.POST.get("codigo_opsu")

        nacionalidad_auxiliar = request.POST.get("nacionalidad_auxiliar")
        ci_auxiliar = request.POST.get("ci_auxiliar")
        prefijo_auxiliar = request.POST.get("prefijo_auxiliar")
        telefono_auxiliar = request.POST.get("telefono_auxiliar")

        # Contacto Auxiliar
        if request.POST.get("nombres_auxiliar"):
            nombres_auxiliar = request.POST.get("nombres_auxiliar")
        else:
            nombres_auxiliar = "N/A"
        
        if request.POST.get("apellidos_auxiliar"):
            apellidos_auxiliar = request.POST.get("apellidos_auxiliar")
        else:
            apellidos_auxiliar = "N/A"
        
        if not nacionalidad_auxiliar and ci_auxiliar:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacío",
                "descripcion": "Debe seleccionar la nacionalidad y sino vacia el campo para los numeros de cedulas.",
                "icon": "warning"
            })
                            
        if nacionalidad_auxiliar and not ci_auxiliar:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacío",
                "descripcion": "Debe ingresar los numeros de cedulas o seleccionar la opción N.",
                "icon": "warning"
            })

        cedula_auxiliar = (
            nacionalidad_auxiliar + "-" + ci_auxiliar
            if nacionalidad_auxiliar and ci_auxiliar
            else ""
        )

        if not prefijo_auxiliar and num_telefono_secundaria:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacío",
                "descripcion": "Debe seleccionar el prefijo telefónico o dejar vacío el número telefónico.",
                "icon": "warning"
            })
                            
        if prefijo_auxiliar and not telefono_auxiliar:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacío",
                "descripcion": "Debe ingresar el número telefónico o seleccionar la opción TLF.",
                "icon": "warning"
            })

        telefono_auxiliar = (
            prefijo_auxiliar + telefono_auxiliar
            if prefijo_auxiliar and telefono_auxiliar
            else "N/A"
        )
        
        if request.POST.get("parestenco_auxiliar"):
            parestenco_auxiliar = request.POST.get("parestenco_auxiliar")
        else:
            parestenco_auxiliar = "N/A"

        # Campos discapacidad
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

        campos_generales = [
            (genero, "Género", "Por favor, seleccione una de las opciones presentes."),
            (estado_civil, "Estado Civil", "Por favor, seleccione una de las opciones presentadas."),
            (prefijo_telefono_principal, "Prefijo Telefonico", "Por favor, selecciona uno de los prefijos telefonico."),
            (num_telefono_principal, "Números Telefonico", "Por favor, ingrese el numero telefonico."),
            (correo_secundaria, "Correo Alternativo", "Por favor, ingrese el correo electrónico alternativo."),
            (dominio_correo_secundaria, "Dominio Correo Principal", "Por favor, seleccione una de las opciones."),
            (pais_nacimiento, "País de Nacimiento", "Por favor, seleccione una de las opciones."),
            (direccion_nacimiento, "Dirección de Nacimiento", "Por favor, ingrese la dirección de nacimiento."),
            (fecha_nacimiento, "Fecha de Nacimiento", "Por favor, ingrese la fecha de nacimiento."),
            (condicion_residencia, "Condición de Residencia", "Por favor, seleccione una de las opciones."),
            (municipio_residencia, "Municipio de Residencia", "Por favor, seleccione una de las opciones."),
            (parroquia_residencia, "Parroquia de Residencia", "Por favor, seleccione una de las opciones."),
            (direccion_domicilio, "Dirección de Residencia", "Por favor, ingrese la dirección de domicilio."),
        ]

        for valor, titulo, mensaje in campos_generales:
            if not valor:
                return JsonResponse({
                    "estado": "fallo",
                    "title": titulo,
                    "descripcion": mensaje,
                    "icon": "warning"
                })
    
        if request.POST.get("estado_nacimiento"):
            estado_nacimiento = request.POST.get("estado_nacimiento")
        elif request.POST.get("estado_novzla"):
            estado_nacimiento = request.POST.get("estado_novzla")     
        else:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacío",
                "descripcion": "Por favor, selecciona o ingrese el estado de nacimiento.",
                "icon": "warning"
            })
        
        if request.POST.get("municipio_nacimiento"):
            municipio_nacimiento = request.POST.get("municipio_nacimiento")
        elif request.POST.get("municipio_novzla"):
            municipio_nacimiento = request.POST.get("municipio_novzla")
        else:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacío",
                "descripcion": "Por favor, selecciona o ingrese el municipio de nacimiento.",
                "icon": "warning"
            })
        
        if request.POST.get("parroquia_nacimiento"):
            parroquia_nacimiento = request.POST.get("parroquia_nacimiento")
        elif request.POST.get("parroquia_novzla"):
            parroquia_nacimiento = request.POST.get("parroquia_novzla")
        else:
            return JsonResponse({
                "estado": "fallo",
                "title": "Vacío",
                "descripcion": "Por favor, selecciona o ingrese la parroquia de nacimiento.",
                "icon": "warning"
            })

        telefono_principal = prefijo_telefono_principal+num_telefono_principal
        
        correo_electronico1 = correo_principal + dominio_correo_principal
        
        correo_electronico2 = correo_secundaria + dominio_correo_secundaria

        if correo_electronico1 == correo_electronico2:
            return JsonResponse({
                "estado": "fallo",
                "title": "Error",
                "descripcion": "Por favor, ingrese correos electronicos diferentes.",
                "icon": "error"
            })

        usuario = Usuario.objects.get(cedula_identidad=request.session.get("cedula_usuario"))

        roles = []
        if Estudiante.objects.filter(usuario=usuario).exists():
            roles.append("Estudiante")

        if Docente.objects.filter(usuario=usuario).exists():
            roles.append("Docente")

        if CoordinadorPNF.objects.filter(usuario=usuario).exists():
            roles.append("Coordinador PNF")

        if ControlEstudio.objects.filter(usuario=usuario).exists():
            roles.append("Control de Estudio")

        if DirectorGeneral.objects.filter(usuario=usuario).exists():
            roles.append("Director General")

        
        if "Estudiante" not in roles:
            campos_administrativo = [
                (profesion_pregrado, "Profesión de Egreso", "Por favor, ingrese la profesión de egreso de pregrado."),
                (universidad_pregrado, "Universidad de Egreso", "Por favor, ingrese la universidad de egreso de pregrado."),
                (pais_profesion, "País de Egreso Posgrado", "Por favor, seleccione una de las opciones presentes."),
            ]
    
            for valor, titulo, mensaje in campos_administrativo:
                if not valor:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": titulo,
                        "descripcion": mensaje,
                        "icon": "warning"
                    })

            usuario.genero = genero
            usuario.estado_civil = estado_civil
            usuario.save()
    
            contacto, _ = Contacto.objects.get_or_create(id_usuario=usuario)
            
            contacto.telefono_personal = telefono_principal
    
            if telefono_secundario: 
                contacto.telefono_suplete = telefono_secundario
                
            contacto.correo_electronico = correo_electronico1
            contacto.correo_alternativo = correo_electronico2
            contacto.save()
    
            Residencia.objects.create(condicion_residencia=condicion_residencia, municipio=municipio_residencia, parroquia=parroquia_residencia, direccion_residencia=direccion_domicilio, id_usuario=usuario)
    
            Nacimiento.objects.create(pais=pais_nacimiento, estado=estado_nacimiento, municipio=municipio_nacimiento, parroquia=parroquia_nacimiento, direccion_nacimiento=direccion_nacimiento, fecha_nacimiento=fecha_nacimiento, id_usuario=usuario)
    
            DatosPreofesion.objects.create(profesion_pregrado=profesion_pregrado, universidad_egreso_pregrado=universidad_pregrado, pais_profesion_pregrado=pais_profesion, id_usuario=usuario)

            request.session['registro_completado'] = True

            return JsonResponse({
                "estado": "exito",
                "title": "Exito",
                "descripcion": "Los datos del usuario se registraron exitosamente.",
                "icon": "success",
                "url": reverse("panel_usuario")
            })
        else:
            campos_estudiantil = [
                (tipos_secundaria, "Tipo de Institución", "Por favor, seleccione una de las opciones presentes."),
                (nombre_secundaria, "Nombre del Liceo", "Por favor, ingrese la institución de bachillerato."),
                (codigo_opsu, "Código OPSU", "Por favor, ingrese el código de la opsu."),
            ]
    
            for valor, titulo, mensaje in campos_estudiantil:
                if not valor:
                    return JsonResponse({
                        "estado": "fallo",
                        "title": titulo,
                        "descripcion": mensaje,
                        "icon": "warning"
                    })

            nucleos = {
                "Barinas": request.POST.getlist("pnf_Barinas"),
                "Barinitas": request.POST.getlist("pnf_Barinitas"),
                "Socopo": request.POST.getlist("pnf_Socopo"),
                "Pedraza": request.POST.getlist("pnf_Pedraza"),
            }

            if not any(nucleos.values()):
                return JsonResponse({
                    "estado": "fallo",
                    "title": "PNF requerido",
                    "descripcion": "Debe seleccionar al menos un PNF para continuar.",
                    "icon": "warning"
                })

            documentos = {
                "Cédula de Identidad": request.FILES.get("CI_estudiante"),
                "Título de Bachiller": request.FILES.get("TBachiller_estudiante"),
                "Sabana de Notas": request.FILES.get("SNotas_estudiante"),
                "OPSU": request.FILES.get("OPSU_estudiante"),
            }

            if not all(documentos.values()):
                return JsonResponse({
                    "estado": "fallo",
                    "title": "Documentos incompletos",
                    "descripcion": "Debe cargar todos los documentos requeridos para continuar.",
                    "icon": "warning"
                })
            
            usuario.genero = genero
            usuario.estado_civil = estado_civil
            usuario.save()
    
            contacto = Contacto.objects.get(id_usuario=usuario)
            
            contacto.telefono_personal = telefono_principal
    
            if telefono_secundario: 
                contacto.telefono_suplete = telefono_secundario
                
            contacto.correo_electronico = correo_electronico1
            contacto.correo_alternativo = correo_electronico2
            contacto.save()
    
            Residencia.objects.create(condicion_residencia=condicion_residencia, municipio=municipio_residencia, parroquia=parroquia_residencia, direccion_residencia=direccion_domicilio, id_usuario=usuario)
    
            Nacimiento.objects.create(pais=pais_nacimiento, estado=estado_nacimiento, municipio=municipio_nacimiento, parroquia=parroquia_nacimiento, direccion_nacimiento=direccion_nacimiento, fecha_nacimiento=fecha_nacimiento, id_usuario=usuario)
                
            estudiante = Estudiante.objects.get(usuario=usuario)

            ContactoAuxiliar.objects.create(nombres=nombres_auxiliar, apellidos=apellidos_auxiliar, cedula_identidad=cedula_auxiliar, telefono=telefono_auxiliar, parentesco=parestenco_auxiliar, estudiante=estudiante)

            Discapacidad.objects.create(codigo_carnet_discapacidad=carnet_dispacidad, nro_registro_medico=registro_medico, tipo_discapacidad=tipo_discapacidad, grado_discapacidad=grado_discapacidad, causa_discapacidad=causa_discapacidad, estudiante=estudiante)

            InformacionSecundaria.objects.create(tipo_institucion=tipos_secundaria, nombre_institucion=nombre_secundaria, fecha_grado=fecha_graduacion, codigo_sni_opsu=codigo_opsu, estudiante=estudiante)

            primer_registro = True

            for nombre_nucleo, lista_pnfs in nucleos.items():
                if not lista_pnfs:
                    continue

                nucleo = Nucleos.objects.filter(municipio=nombre_nucleo).first()
                if not nucleo:
                    continue

                for id_pnf in lista_pnfs:
                    pnf_nucleo = PNFNucleo.objects.filter(
                        id_nucleo=nucleo,
                        id_pnf_id=id_pnf
                    ).select_related("id_pnf").first()
                    if not pnf_nucleo:
                        continue

                    if primer_registro:
                        estudiante.nucleo = nucleo
                        estudiante.pnf = pnf_nucleo.id_pnf
                        estudiante.save()

                        primer_registro = False
                    else:
                        estudiante = Estudiante.objects.create(
                            usuario=usuario,
                            nucleo=nucleo,
                            pnf=pnf_nucleo.id_pnf
                        )

                    EstatusEstudiante.objects.create(
                        estudiante=estudiante,
                        estatus="Espera",
                        estado="Espera",
                        ingreso="Bachiller",
                        descripcion_ingreso="En espera de la aceptación.",
                        trayecto="Inicial",
                        fecha_ingreso=timezone.now().date()
                    )

            nombre_estudiante = f"{usuario.nombres}_{usuario.apellidos}".replace(" ", "_")

            base_path = os.path.join(settings.BASE_DIR, "media", "documentosEstudiante", nombre_estudiante)
            
            os.makedirs(base_path, exist_ok=True)

            fs = FileSystemStorage(location=base_path)

            for nombre, archivo in documentos.items():
                if archivo:
                    extension = os.path.splitext(archivo.name)[1]
                    nuevo_nombre = f"{nombre}{extension}"
                    filename = fs.save(nuevo_nombre, archivo)

                    file_path = os.path.join("media", "documentosEstudiante", nombre_estudiante, filename)
                    DocumentosEstudiante.objects.update_or_create(
                        estudiante=estudiante, 
                        nombre_documento=nombre,
                        defaults={
                            "archivo": file_path
                        }
                    )
            
            request.session['registro_completado'] = True

            return JsonResponse({
                "estado": "exito",
                "title": "Exito",
                "descripcion": "Los datos del estudiante se registraron exitosamente.",
                "icon": "success",
                "url": reverse("panel_usuario")
            })

    return render(request, "Actualizaciones/completar_registro.html")




