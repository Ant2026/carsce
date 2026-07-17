from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse, FileResponse
from django.core.mail import send_mail, EmailMessage
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from datetime import datetime, timedelta
from django.forms.models import model_to_dict
from django.template.loader import render_to_string

from .models import Usuario, Perfiles, Nucleos, Pnf, Contacto, SeccionEstudiante, VerificacionCodigo, PNFNucleo,  GacetaOficial, UsuarioAsignacion, Nacimiento, Residencia, DatosPreofesion, Discapacidad, InformacionSecundaria, DocumentosEstudiante, PadresEstudiante, EstatusEstudiante, SeccionAcademica, CredencialesUsuario, Materia, PeriodoAcademico, CalendarioAcademico, PeriodoMateria, CalendarioMateria, MateriaAsignada, Autoridades, TrayectoAcademico, AulaAcademica, HorarioAcademica

from collections import defaultdict
import secrets, string, json, uuid, os
from math import ceil
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, letter, legal, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT

ROMANOS = [
    "I", "II", "III", "IV", "V",
    "VI", "VII", "VIII", "IX", "X"
]

# Create your views here.

def inicio_sesion(request):
    if request.method == "POST":
        try:
            nombre_usuario = request.POST.get("usuario")
            contrasenia = request.POST.get("contrasenia")

            if not nombre_usuario or not contrasenia:
                return JsonResponse({
                    "success": False,
                    "icon": "warning",
                    "descripcion": "Debe completar todos los campos"
                })

            credenciales = CredencialesUsuario.objects.select_related(
                'id_asignacion__id_usuario',
                'id_asignacion__id_perfil'
            ).filter(nombre_usuario=nombre_usuario).first()

            if not credenciales:
                return JsonResponse({
                    "success": False,
                    "icon": "error",
                    "descripcion": "El usuario no se encuentra registrado."
                })

            if not check_password(contrasenia, credenciales.clave):
                return JsonResponse({
                    "success": False,
                    "icon": "error",
                    "descripcion": "Contraseña incorrecta"
                })

            usuario = credenciales.id_asignacion.id_usuario
            perfil = credenciales.id_asignacion.id_perfil

            request.session['cedula_usuario'] = usuario.cedula_identidad
            request.session['usuario_nombre'] = f"{usuario.nombres} {usuario.apellidos}"
            request.session['perfil'] = perfil.perfil

            registro_basico = Nacimiento.objects.filter(id_usuario=usuario).exists()

            registro_estudiante = InformacionSecundaria.objects.filter(id_usuario=usuario).exists()

            request.session['registro_completado'] = (
                registro_basico or registro_estudiante
            )

            if not registro_basico:
                if perfil.perfil == "Estudiante":
                    url = "/../completar_registro_estudiante/"
                else:
                    url = "/completar_registro_personal/"

            elif perfil.perfil == "Estudiante" and not registro_estudiante:
                url = "/../completar_registro_pe/"
            else:
                url = "/../panel_usuario/"

            return JsonResponse({
                "success": True,
                "url": url
            })
        
        except Exception as e:
            return JsonResponse({
                "success": False,
                "icon": "error",
                "descripcion": "Error interno del servidor",
                "detalle": str(e)
            })

    return render(request, 'Sesion/inicio_sesion.html')

def cerrar_sesion(request):
    request.session.flush() 
    return redirect("inicio_sesion")

# Esto son los modulos para recuperar o cambiar de credenciales con sus procesos de autenticación
# Los modulos no tiene ninguna relación con el perfil ni mucho meno núcleo y pnf
def buscar_usuario(request):
    if request.method == "POST":
        nacionalidad = request.POST.get("nacionalidad")
        num_cedula = request.POST.get("ci")

        if nacionalidad and num_cedula:
            cedula_identidad = nacionalidad + "-" + num_cedula

            existe = Usuario.objects.filter(cedula_identidad=cedula_identidad).exists()

            if existe:
                
                request.session['CI_usuario'] = cedula_identidad
                request.session['flujo_verificacion'] = True
                
                token = str(uuid.uuid4())
                request.session['token_recuperacion'] = token

                return JsonResponse({"estado": "exito"})
            else:
                return JsonResponse({
                            "estado": "fallo",
                            "icon": "error",
                            "descripcion": "No se encuentra registrado"
                        })
        return JsonResponse({
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "Debe completar los campos"
                })
        
    return render(request, 'Sesion/buscar_usuario.html')

# Asegúrate de importar tus modelos y funciones (Usuario, Contacto, VerificacionCodigo, etc.)

# Asegúrate de importar tus modelos y funciones (Usuario, Contacto, VerificacionCodigo, etc.)

def comprobar_usuario(request):
    # 1. Validaciones de flujo de sesión obligatorias
    if not request.session.get("flujo_verificacion"):
        return redirect("buscar_usuario")

    usuario = Usuario.objects.filter(cedula_identidad=request.session.get("CI_usuario")).first()
    if not usuario:
        return redirect("buscar_usuario")

    contacto = Contacto.objects.filter(id_usuario_id=usuario.id_usuario).first()
    token_sesion = request.session.get("token_recuperacion")

    # 2. Intentar buscar si ya existe un código activo para este token
    verificacion = VerificacionCodigo.objects.filter(
        cedula_identidad=usuario.cedula_identidad, 
        token=token_sesion
    ).first()

    # Si no existe, se genera y envía por primera vez
    if not verificacion:
        enviar_codigo_verificacion(
            usuario.nombres,
            usuario.apellidos,
            contacto.correo_electronico,
            usuario.cedula_identidad,
            token_sesion
        )
        # Volvemos a consultar para obtener el registro recién creado
        verificacion = VerificacionCodigo.objects.filter(
            cedula_identidad=usuario.cedula_identidad, 
            token=token_sesion
        ).first()

    # 3. MANEJO DE LA PETICIÓN ASÍNCRONA (POST) -> Sacado del bloque anterior
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        codigo_ingresado = request.POST.get("codigo")

        if not codigo_ingresado:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Debe ingresar el código de verificación",
                "accion": "input_vacio"
            })

        # Verificar si el código ya expiró
        if verificacion and verificacion.fecha_expiracion < timezone.now():
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "El código ha expirado, debe solicitar el código a través del botón de reenviar código",
                "accion": "expirado"
            })

        # Validamos el código usando tu función externa
        respuesta = validar_codigo(
            codigo_ingresado,
            usuario.cedula_identidad,
            token_sesion
        )

        # Procesamos la respuesta para limpiar intentos si fue exitoso
        datos = json.loads(respuesta.content)
        if datos.get("estado") == "exito":    
            request.session["correo_verificado"] = True
            if verificacion:
                verificacion.intentos = 0
                verificacion.bloqueado_hasta = None
                verificacion.activo = 0
                verificacion.save()

        return respuesta

    # 4. MANEJO DE LA PETICIÓN INICIAL (GET)
    # Pasamos el timestamp de expiración a la plantilla
    fecha_expiracion_ts = int(verificacion.fecha_expiracion.timestamp()) if verificacion else 0

    return render(request, "Sesion/comprobar_usuario.html", {"fecha_expiracion": fecha_expiracion_ts})

def validar_codigo(codigo, cedula_identidad,token):
    verificacion = VerificacionCodigo.objects.filter(
                cedula_identidad=cedula_identidad,
                token=token,
                activo=1).first()

    if not verificacion:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "descripcion": "No existe un código de verificación"
        })
    
    if (verificacion.bloqueado_hasta and timezone.now() >= verificacion.bloqueado_hasta):
        verificacion.intentos = 0
        verificacion.bloqueado_hasta = None
        verificacion.save()

    if (verificacion.bloqueado_hasta and timezone.now() < verificacion.bloqueado_hasta):
        tiempo_restante = verificacion.bloqueado_hasta - timezone.now()
        minutos_restantes = ceil(tiempo_restante.total_seconds() / 60)

        return JsonResponse({
            "estado": "bloqueado",
            "icon": "error",
            "descripcion": f"Demasiados intentos. Intente nuevamente en {minutos_restantes} minuto(s)"
        })

    if timezone.now() > verificacion.fecha_expiracion:
        return JsonResponse({
            "estado": "expirado",
            "icon": "warning",
            "descripcion": "El código expiró. Solicite uno nuevo."
        })

    if verificacion.codigo == codigo:
        verificacion.intentos = 0
        verificacion.bloqueado_hasta = None
        verificacion.activo = 0
        verificacion.save()

        return JsonResponse({
            "estado": "exito"
        })

    verificacion.intentos += 1

    if verificacion.intentos >= 3:
        verificacion.bloqueado_hasta = timezone.now() + timedelta(minutes=5)
        verificacion.save()

        return JsonResponse({
            "estado": "bloqueado",
            "icon": "error",
            "descripcion": "Ha superado el número máximo de intentos. Intente nuevamente en 5 minutos."
        })

    verificacion.save()

    return JsonResponse({
        "estado": "fallo",
        "icon": "error",
        "descripcion": f"Código incorrecto. Intentos: {verificacion.intentos}/3"
    })

def reenviar_codigo_btn(request):
    if not request.session.get("flujo_verificacion"):
        return JsonResponse({
            "estado": "error",
            "icon": "error",
            "descripcion": "Sesión inválida"
        })

    usuario = Usuario.objects.filter(cedula_identidad=request.session.get("CI_usuario")).first()

    if not usuario:
        return JsonResponse({
            "estado": "error",
            "icon": "error",
            "descripcion": "Usuario no encontrado"
        })

    contacto = Contacto.objects.filter(id_usuario_id=usuario.id_usuario).first()

    verificacion = VerificacionCodigo.objects.filter(cedula_identidad=usuario.cedula_identidad,
                                                    token=request.session.get("token_recuperacion")).first()

    if (verificacion and verificacion.bloqueado_hasta and timezone.now() < verificacion.bloqueado_hasta):
        tiempo_restante = (verificacion.bloqueado_hasta - timezone.now())
        minutos_restantes = ceil(tiempo_restante.total_seconds() / 60)

        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "descripcion": f"Demasiados intentos. Intente nuevamente en {minutos_restantes} minuto(s)"
        })

    return reenviar_codigo(
            usuario.nombres,
            usuario.apellidos,
            contacto.correo_electronico,
            usuario.cedula_identidad,
            request.session.get("token_recuperacion"))

def reenviar_codigo(nombres_usuario, apellidos_usuario, correo_electronico, cedula_identidad, token):
    numero_intento = 0
    
    verificacion = VerificacionCodigo.objects.filter(
        cedula_identidad=cedula_identidad,
        token=token
    ).first()

    # Bloqueo activo
    if verificacion and verificacion.bloqueado_hasta and timezone.now() < verificacion.bloqueado_hasta:

        tiempo_restante = verificacion.bloqueado_hasta - timezone.now()
        minutos_restantes = max(1, int(tiempo_restante.total_seconds() / 60))

        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "descripcion": f"Demasiados intentos. Intente nuevamente en {minutos_restantes} minuto(s)"
        })

    codigo_generado = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(6)
    )

    fecha_expiracion = timezone.now() + timedelta(minutes=5)

    if verificacion:
        verificacion.codigo = codigo_generado
        verificacion.fecha_expiracion = fecha_expiracion
        verificacion.activo = 1
        verificacion.save()

        numero_intento = verificacion.intentos
    else:
        verificacion = VerificacionCodigo.objects.create(
            cedula_identidad=cedula_identidad,
            token=token,
            codigo=codigo_generado,
            creado=timezone.now(),
            intentos=0,
            activo=1,
            fecha_expiracion=fecha_expiracion,
            bloqueado_hasta=None,
            descripcion=f"Código de verificación para recuperación de credenciales al usuario {nombres_usuario} {apellidos_usuario}"
        )

    html = render_to_string(
        "Email/reenviar_codigo.html",
        {
            "nombres": nombres_usuario,
            "apellidos": apellidos_usuario,
            "codigo": codigo_generado,
            "numero_intento": numero_intento,
        }
    )
    send_mail(
        subject="Nuevo código de autenticación - UPT José Félix Ribas",
        message=f"Su nuevo código de autenticación es: {codigo_generado}",
        from_email="ejemplo@gmail.com",
        recipient_list=[correo_electronico],
        html_message=html,
    )

    return JsonResponse({
        "estado": "codigo_enviado",
        "icon": "info",
        "descripcion": "Se ha enviado un nuevo código de verificación"
    })

def enviar_codigo_verificacion(nombres_usuario, apellidos_usuario, correo_electronico, cedula_identidad, token):
    codigo_generado = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    fecha_expiracion = timezone.now() + timedelta(minutes=15)

    VerificacionCodigo.objects.create(
        cedula_identidad=cedula_identidad,
        token=token,
        codigo=codigo_generado,
        creado=timezone.now(),
        intentos=0,
        activo=1,
        fecha_expiracion=fecha_expiracion,
        descripcion=f"Código de verificación para recuperación de credenciales al usuario {nombres_usuario} {apellidos_usuario}"
    )

    # Renderizar la plantilla HTML
    html = render_to_string(
        "Email/enviar_codigo.html",
        {
            "nombres": nombres_usuario,
            "apellidos": apellidos_usuario,
            "codigo": codigo_generado,
        }
    )

    # Enviar correo
    send_mail(
        subject="Código de Autenticación - UPT José Félix Ribas",
        message=f"Su código de autenticación es: {codigo_generado}",  # Texto plano de respaldo
        from_email="ejemplo@gmail.com",
        recipient_list=[correo_electronico],
        html_message=html,
    )

    return JsonResponse({
        "estado": "codigo_enviado",
        "icon": "info",
        "descripcion": "Se ha enviado un código de verificación a su correo electrónico"
    })

def panel_recuperar_credenciales(request):
    if not request.session.get("flujo_verificacion"):
        return redirect("buscar_usuario")
    
    if not request.session['correo_verificado']:
        return redirect("comprobar_usuario")
    
    token = request.session.get("token_recuperacion")

    verificacion = VerificacionCodigo.objects.filter(token=token, activo=0).first()

    if not verificacion:
        return redirect("buscar_usuario")
    
    return render(request, 'panel_recuperar_credenciales.html')

def recuperar_contrasenia(request):
    if not request.session.get("flujo_verificacion"):
        return redirect("buscar_usuario")
    
    if not request.session.get("correo_verificado"):
        return redirect("comprobar_usuario")
    
    token = request.session.get("token_recuperacion")
    verificacion = VerificacionCodigo.objects.filter(token=token, activo=0).first()

    if not verificacion:
        return redirect("buscar_usuario")

    if request.method == "POST":
        password = request.POST.get("nueva_contrasenia")
        confirmar_password = request.POST.get("confirmar_contrasenia")

        if not password or not confirmar_password:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "Debe completar todos los campos"
            })

        if password != confirmar_password:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "Las contraseñas no coinciden"
            })

        usuario = Usuario.objects.filter(cedula_identidad=request.session.get("CI_usuario")).first()
        if not usuario:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "Usuario no encontrado"
            })

        asignacion = UsuarioAsignacion.objects.filter(id_usuario=usuario).first()
        if not asignacion:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "El usuario no tiene una asignación registrada"
            })

        credenciales = CredencialesUsuario.objects.filter(id_asignacion=asignacion).first()
        if not credenciales:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "No existen credenciales registradas"
            })

        credenciales.clave = password
        credenciales.save()

        verificacion = VerificacionCodigo.objects.filter(cedula_identidad=request.session["CI_usuario"]).first()

        if verificacion:
            verificacion.token = ""
            verificacion.save()

        del request.session["correo_verificado"]
        del request.session["CI_usuario"]
        del request.session["token_recuperacion"]

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "descripcion": "Contraseña actualizada correctamente"
        })

    return render(request, "Sesion/recuperar_contrasenia.html")

from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

def recuperar_usuario(request):
    ci_usuario = request.session.get("CI_usuario")

    if not ci_usuario:
        return redirect("inicio_sesion")

    try:
        usuario = Usuario.objects.get(
            cedula_identidad=ci_usuario
        )

        contacto = Contacto.objects.filter(
            id_usuario=usuario
        ).first()

        if not contacto or not contacto.correo_electronico:
            return render(
                request,
                "Sesion/recuperar_usuario.html",
                {
                    "error": "El usuario no posee un correo electrónico registrado."
                }
            )

        credenciales = (
            CredencialesUsuario.objects
            .filter(id_asignacion__id_usuario=usuario)
            .select_related("id_asignacion")
            .first()
        )

        if not credenciales:
            return render(
                request,
                "Sesion/recuperar_usuario.html",
                {
                    "error": "No existen credenciales asociadas a este usuario."
                }
            )

        correo = contacto.correo_electronico

    except ObjectDoesNotExist:
        return render(
            request,
            "Sesion/recuperar_usuario.html",
            {
                "error": "Los datos suministrados no son válidos."
            }
        )

    VerificacionCodigo.objects.filter(
        cedula_identidad=ci_usuario
    ).update(token="")

    request.session.pop("correo_verificado", None)
    request.session.pop("CI_usuario", None)
    request.session.pop("token_recuperacion", None)

    html = render_to_string(
        "Email/recuperar_usuario.html",
        {
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "nombre_usuario": credenciales.nombre_usuario,
        }
    )

    try:
        send_mail(
            subject="Recuperación de usuario - UPT José Félix Ribas",
            message=f"Su nombre de usuario es: {credenciales.nombre_usuario}",
            from_email="ejemplo@gmail.com",
            recipient_list=[correo],
            html_message=html,
            fail_silently=False,
        )

    except Exception:
        return render(
            request,
            "Sesion/recuperar_usuario.html",
            {
                "error": "No fue posible enviar el correo electrónico."
            }
        )

    return render(
        request,
        "Sesion/recuperar_usuario.html",
        {
            "usuario_enviado": True
        }
    )

# Esto son los modulos para registrar credenciales por parte del personal y
# pre-inscripción para los estudiantes

def panel_estudiantes(request):
    return render(request, 'panel_estudiantes.html')

def panel_registro(request):
    return render(request, 'Sesion/panel_registro.html')

def registro_estudiantil(request):
    if request.method == "POST":
        nombres = request.POST.get("nombres")
        apellidos = request.POST.get("apellidos")
        nacionalidad = request.POST.get("nacionalidad")
        num_cedula = request.POST.get("cedula_identidad")
        nombre_correo = request.POST.get("correo_electronico")
        dominio = request.POST.get("dominio")
        prefijo = request.POST.get("prefijo")
        num_telefono = request.POST.get("telefono")
        usuario = request.POST.get("usuario")
        password = request.POST.get("password")

        if nombres and apellidos and nacionalidad and num_cedula and nombre_correo and dominio and prefijo and num_telefono and usuario and password:
            correo_electronico = nombre_correo + dominio
            cedula_identidad = nacionalidad + "-" + num_cedula
            telefono = prefijo + num_telefono

            verificar_cedula = Usuario.objects.filter(cedula_identidad=cedula_identidad).exists()
            verificar_usuario = CredencialesUsuario.objects.filter(nombre_usuario=usuario).first()
            verificar_correo = Contacto.objects.filter(correo_electronico=correo_electronico).exists()

            if verificar_cedula:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe una cédula registrada."
                })

            if verificar_correo:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe un correo registrado."
                })

            if verificar_usuario:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe el usuario registrado."
                })
            
            nuevo_usuario = Usuario.objects.create(
                            nombres=nombres,
                            apellidos=apellidos,
                            cedula_identidad=cedula_identidad
                        )

            Contacto.objects.create(
                telefono_personal=telefono,
                correo_electronico=correo_electronico,
                id_usuario=nuevo_usuario)

            perfil = Perfiles.objects.get(pk=5)

            nuevo_asignacion = UsuarioAsignacion.objects.create(
                id_usuario=nuevo_usuario,
                id_perfil=perfil
            )

            CredencialesUsuario.objects.create(
                            nombre_usuario=usuario,
                            clave=make_password(password),
                            id_asignacion=nuevo_asignacion)

            return JsonResponse({
                "icon": "success",
                "descripcion": "Se registró correctamente."
            })

        return JsonResponse({
            "icon": "warning",
            "descripcion": "Complete todos los campos."
        })

    return render(request, "Sesion/registro_estudiantil.html")

def confirmar_registro_personal(request):
    if request.method == "POST":
        nacionalidad = request.POST.get("nacionalidad")
        num_cedula_identidad = request.POST.get("usuario_ci")

        if nacionalidad and num_cedula_identidad:
            cedula_identidad = f"{nacionalidad}-{num_cedula_identidad}"

            usuario = Usuario.objects.filter(cedula_identidad=cedula_identidad).first()

            if not usuario:
                return JsonResponse({
                    "existe": "error",
                    "icon": "error",
                    "descripcion": "El usuario no se encuentra registrado"
                })

            perfil_estudiante = Perfiles.objects.get(pk=5)

            asignacion = UsuarioAsignacion.objects.filter(id_usuario=usuario).exclude(id_perfil=perfil_estudiante).first()

            if asignacion:
                credenciales = CredencialesUsuario.objects.filter(id_asignacion=asignacion).first()

                if credenciales:
                    return JsonResponse({
                        "existe": "error",
                        "icon": "warning",
                        "descripcion": "El usuario ya posee credenciales registradas"
                    })
            request.session["cedula_personal"] = cedula_identidad

            return JsonResponse({
                "existe": "success"
            })

        return JsonResponse({
            "existe": "error",
            "icon": "warning",
            "descripcion": "Complete todos los campos"
        })

    return render(request, "Sesion/confirmar_registro_personal.html")

def guardar_credenciales_personal(request):
    if request.method == "POST":
        cedula_identidad = request.session.get('cedula_personal')

        nombre_usuario = request.POST.get("nombre_usuario")
        password = request.POST.get("password_usuario")

        if nombre_usuario and password:
            usuario = Usuario.objects.get(cedula_identidad=cedula_identidad)

            asignacion = UsuarioAsignacion.objects.exclude(id_perfil_id=5).filter(id_usuario=usuario).first()

            if not asignacion:
                return JsonResponse({
                    "existe": "error",
                    "icon": "warning",
                    "descripcion": "El usuario solo posee el perfil de estudiante"
                })

            CredencialesUsuario.objects.create(
                nombre_usuario=nombre_usuario,
                clave=password,
                id_asignacion=asignacion)

            del request.session["cedula_personal"]

            return JsonResponse({
                "existe": "success",
                "icon": "success",
                "descripcion": "Se registraron exitosamente las credenciales"
            })
        else:
            return JsonResponse({
                "existe": "error",
                "icon": "warning",
                "descripcion": "Complete todos los campos"
            })

    return render(request, 'confirmar_registro_personal.html')

def buscar_personal_registrado(request):
    if request.method == "POST":
        nacionalidad = request.POST.get('nacionalidad')
        cedula = request.POST.get('cedula')

        if nacionalidad and cedula:
            cedula_identidad = nacionalidad + "-" + cedula
            
            if Usuario.objects.filter(cedula_identidad=cedula_identidad).exists():
                request.session['cedula_usuario'] = cedula_identidad
                
                usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()
                perfil = Perfiles.objects.get(pk=5)

                existe = UsuarioAsignacion.objects.filter(id_usuario=usuario, id_perfil=perfil).exists()
                if existe:
                    return JsonResponse({
                        "estado": "existe",
                        "icon": "error",
                        "descripcion": "Ya se encuentra el usuario registrado como estudiante."
                    })
                
                return JsonResponse({
                    "estado": "success",
                })
            else:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "El usuario no se encuentra registrado"
                })
        else:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "El campo se encuentra vacio."
            })

def credenciales_estudiante(request):
    if request.method == "POST":
        nombre_usuario = request.POST.get('nombreusuario')
        contrasenia = request.POST.get('passwordusuario')

        if nombre_usuario and contrasenia:
            existe = CredencialesUsuario.objects.filter(nombre_usuario=nombre_usuario).exists()
            if existe:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "Ya se encuentra un nombre de usuario similar"
                })
            
            credenciales = CredencialesUsuario.objects.all()
            for credencial in credenciales:
                if check_password(contrasenia, credencial.clave):
                    return JsonResponse({
                        "estado": "fallo",
                        "icon": "error",
                        "descripcion": "Ya existe una contraseña igual."
                    })
                
            usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()
            perfil = Perfiles.objects.get(pk=5)
                        
            asignacion = UsuarioAsignacion.objects.create(
                id_usuario=usuario,
                id_perfil=perfil)

            CredencialesUsuario.objects.create(
                nombre_usuario=nombre_usuario,
                clave=contrasenia,
                id_asignacion=asignacion)

            return JsonResponse({
                "estado": "success",
                "icon": "success",
                "descripcion": "Se registraron las credenciales exitosamente"
            })
        else:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "El campo se encuentra vacio."
            })

    return render(request, "credenciales_estudiante.html")

# MODULO 

def panel_usuario(request):
    return render(request, 'Logueado/panel_usuario.html')

# PRE REGISTRO PERSONAL

def datos_registro(request):
    perfiles = Perfiles.objects.exclude(perfil="Estudiante")

    cantidad_directores = UsuarioAsignacion.objects.filter(id_perfil__perfil="Director General").count()

    if cantidad_directores >= 2:
        perfiles = perfiles.exclude(perfil="Director General")

    nucleos = Nucleos.objects.all()

    return JsonResponse({
        "perfiles": list(
            perfiles.values(
                "id_pefil",
                "perfil"
            )
        ),
        "nucleos": list(
            nucleos.values(
                "id_nucleo",
                "municipio"
            )
        )
    })

def validar_nucleos(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            perfil_id = data.get("id_perfil")
            perfil = Perfiles.objects.get(pk=perfil_id)
            nucleos = Nucleos.objects.all()

            if perfil.perfil == "Encargado de Control de Estudio":
                nucleos_ocupados = UsuarioAsignacion.objects.filter(
                    id_perfil__perfil="Encargado de Control de Estudio"
                ).values_list(
                    "id_nucleo_id",
                    flat=True
                )
                nucleos = nucleos.exclude(
                    id_nucleo__in=nucleos_ocupados
                )

            resultado = list(
                nucleos.values(
                    "id_nucleo",
                    "municipio"
                )
            )

            return JsonResponse({"nucleos": resultado})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def pnfs_nucleos(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            nucleo_id = data.get("id_nucleo")
            perfil_id = data.get("id_perfil")

            if not nucleo_id or not perfil_id:
                return JsonResponse(
                    {"error": "Datos incompletos"},
                    status=400
                )

            perfil = Perfiles.objects.get(pk=perfil_id)

            pnfs = PNFNucleo.objects.filter(
                id_nucleo_id=nucleo_id
            ).select_related("id_pnf")

            # Solo para Coordinador de PNF se excluyen los PNF ya asignados
            if perfil.perfil == "Coordinador de PNF":

                pnfs_ocupados = UsuarioAsignacion.objects.filter(
                    id_perfil=perfil,
                    id_nucleo_id=nucleo_id
                ).values_list(
                    "id_pnf_id",
                    flat=True
                )

                pnfs = pnfs.exclude(
                    id_pnf_id__in=pnfs_ocupados
                )

            resultado = [
                {
                    "id_pnf": item.id_pnf.id_pnf,
                    "pnf": item.id_pnf.pnf
                }
                for item in pnfs
            ]

            return JsonResponse({
                "pnfs": resultado
            })

        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=500
            )

    return JsonResponse(
        {"error": "Método no permitido"},
        status=405
    )

def pre_registro_personal(request):
    if request.method == "POST":
        nombres = request.POST.get("nombres")
        apellidos = request.POST.get("apellidos")
        nacionalidad = request.POST.get("nacionalidad")
        num_cedula = request.POST.get("cedula_identidad")
        nombre_correo = request.POST.get("correo_electronico")
        dominio = request.POST.get("dominio")
        prefijo = request.POST.get("prefijo")
        num_telefono = request.POST.get("telefono")

        gaceta_oficial = request.POST.get("gaceta_oficial")
        fecha_gaceta = request.POST.get("fecha_gaceta")

        perfiles_asignados = request.POST.getlist("perfil")

        nucleos_control = request.POST.getlist("nucleo_encargado_control_estudios")
        nucleos_coordinador = request.POST.getlist("nucleo_coordinador_pnf")
        nucleos_docente = request.POST.getlist("nucleo_docente")

        pnfs_coordinador = request.POST.getlist("pnf_coordinador_pnf")
        pnfs_docente = request.POST.getlist("pnf_docente")

        if nombres and apellidos and nacionalidad and num_cedula and nombre_correo and dominio and prefijo and num_telefono:
            
            cedula_identidad = f"{nacionalidad}-{num_cedula}"
            correo_principal = f"{nombre_correo}{dominio}"
            telefono_principal = f"{prefijo}{num_telefono}"
            
            if Usuario.objects.filter(cedula_identidad=cedula_identidad).exists():
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe un usuario con esta cédula"
                })

            try:
                with transaction.atomic():
                    usuario = Usuario.objects.create(nombres=nombres, apellidos=apellidos, cedula_identidad=cedula_identidad)
                    Contacto.objects.create(correo_electronico=correo_principal, telefono_personal=telefono_principal, id_usuario=usuario)
                
                    if gaceta_oficial and fecha_gaceta:
                        GacetaOficial.objects.create(gaceta_oficial=gaceta_oficial, fecha_gaceta_oficial=fecha_gaceta, id_usuario=usuario)
                    
                    for perfil_id in perfiles_asignados:
                        perfil = Perfiles.objects.get(pk=perfil_id)

                        if perfil.perfil == "Director General":
                            UsuarioAsignacion.objects.create(
                                id_usuario=usuario,
                                id_perfil=perfil
                            )

                        # CONTROL DE ESTUDIO
                        if perfil.perfil == "Encargado de Control de Estudio":
                            for nucleo_id in nucleos_control:

                                UsuarioAsignacion.objects.create(
                                    id_usuario=usuario,
                                    id_perfil=perfil,
                                    id_nucleo_id=nucleo_id)

                        # COORDINADOR PNF
                        elif perfil.perfil == "Coordinador de PNF":
                            for nucleo_id in nucleos_coordinador:
                                for pnf_id in pnfs_coordinador:
                                    existe = PNFNucleo.objects.filter(id_nucleo_id=nucleo_id, id_pnf_id=pnf_id).exists()

                                    if existe:
                                        UsuarioAsignacion.objects.create(
                                            id_usuario=usuario,
                                            id_perfil=perfil,
                                            id_nucleo_id=nucleo_id,
                                            id_pnf_id=pnf_id)
                                        
                        # DOCENTE
                        elif perfil.perfil == "Docente":
                            for nucleo_id in nucleos_docente:
                                for pnf_id in pnfs_docente:
                                    existe = PNFNucleo.objects.filter(id_nucleo_id=nucleo_id, id_pnf_id=pnf_id).exists()

                                    if existe:
                                        UsuarioAsignacion.objects.create(
                                            id_usuario=usuario,
                                            id_perfil=perfil,
                                            id_nucleo_id=nucleo_id,
                                            id_pnf_id=pnf_id)

                    return JsonResponse({
                        "icon": "success",
                        "descripcion": "Se registró correctamente"
                    })

            except Exception as e:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": f"Error al registrar los datos: {str(e)}"
                })
        else:
            return JsonResponse({
                "icon": "warning",
                "descripcion": "Se encuentran vacíos los campos obligatorios"
            })
        
    return render(request, 'pre_registro_personal.html')

# FORMULARIOS USUARIOS

def datos_registrado(request):
    if not request.session.get("usuario_nombre"):
        return JsonResponse({"error": "no_session"}, status=401)

    ci_usuario = request.session.get("cedula_usuario")

    datos_basicos = Usuario.objects.filter(cedula_identidad=ci_usuario).first()
    if not datos_basicos:
        return JsonResponse({"error": "usuario_no_encontrado"})

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

def completar_registro_personal(request):
    if request.method == "POST":
        genero = request.POST.get("genero")
        estado_civil = request.POST.get("estado_civil")
        
        num_telefono = request.POST.get("num_telefono_secundaria")
        prefijo_telefono = request.POST.get("prefijo_telefono_secundaria")
        correo_secundaria = request.POST.get("correo_secundaria")
        dominio_correo_secundaria = request.POST.get("dominio_correo_secundaria")
        
        pais_nacimiento = request.POST.get("pais_nacimiento_personal")
        
        if prefijo_telefono and num_telefono:
            telefono_sucundario = prefijo_telefono+num_telefono
        else:
            telefono_sucundario = "N/A"

        if request.POST.get("estado_nacimiento_personal"):
            estado_nacimiento = request.POST.get("estado_nacimiento_personal")
        else:
            estado_nacimiento = request.POST.get("estado_novzla_personal")
        
        if request.POST.get("municipio_nacimiento_personal"):
            municipio_nacimiento = request.POST.get("municipio_nacimiento_personal")
        else:
            municipio_nacimiento = request.POST.get("municipio_novzla_personal")
        
        if request.POST.get("parroquia_nacimiento_personal"):
            parroquia_nacimiento = request.POST.get("parroquia_nacimiento_personal")
        else:
            parroquia_nacimiento = request.POST.get("parroquia_novzla_personal")

        direccion_nacimiento = request.POST.get("direccion_nacimiento_personal")
        fecha_nacimiento = request.POST.get("fecha_nacimiento_personal")

        condicion_residencia = request.POST.get("condicion_residencia_personal")
        municipio_residencia = request.POST.get("municipio_residencia_personal")
        parroquia_residencia = request.POST.get("parroquia_residencia_personal")
        direccion_domicilio = request.POST.get("direccion_domicilio_personal")

        profesion_pregrado = request.POST.get("profesion_pregrado_personal")
        universidad_pregrado = request.POST.get("universidad_pregrado_personal")
        pais_profesion = request.POST.get("pais_profesion_personal")

        if genero and estado_civil and correo_secundaria and dominio_correo_secundaria and pais_nacimiento and estado_nacimiento and municipio_nacimiento and parroquia_nacimiento and direccion_nacimiento and fecha_nacimiento and condicion_residencia and municipio_residencia and parroquia_residencia and direccion_domicilio and profesion_pregrado and universidad_pregrado and pais_profesion:

            correo_alternativo = correo_secundaria + dominio_correo_secundaria

            usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()

            existe = Contacto.objects.filter(correo_alternativo=correo_alternativo).exclude(id_usuario=usuario).exists()
            if existe:
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "Ya existe ese correo alternativo en otro usuario"
                })

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
                "estado": "success"
            })

        return JsonResponse({
            "titulo": "¡Advertencia!",
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se ha detectado uno o algunos campos vacios, por favor llene todos los campos."
        })

    return render(request, "completar_registro_personal.html")

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
        else:
            estado_nacimiento = request.POST.get("estado_novzla_estudiante")
        
        if request.POST.get("municipio_nacimiento_estudiante"):
            municipio_nacimiento = request.POST.get("municipio_nacimiento_estudiante")
        else:
            municipio_nacimiento = request.POST.get("municipio_novzla_estudiante")
        
        if request.POST.get("parroquia_nacimiento_estudiante"):
            parroquia_nacimiento = request.POST.get("parroquia_nacimiento_estudiante")
        else:
            parroquia_nacimiento = request.POST.get("parroquia_novzla_estudiante")

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
        
        if num_telefono and prefijo_telefono:
            telefono_sucundario = prefijo_telefono + "-" + num_telefono
        else:
            telefono_sucundario = "N/A"

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

        if genero and estado_civil and correo_secundaria and dominio_correo_secundaria and pais_nacimiento and estado_nacimiento and municipio_nacimiento and parroquia_nacimiento and direccion_nacimiento and fecha_nacimiento and condicion_residencia and municipio_residencia and parroquia_residencia and direccion_domicilio and tipos_secundaria and nombre_secundaria and fecha_graduacion and codigo_opsu and carnet_dispacidad and registro_medico and tipo_discapacidad and grado_discapacidad and causa_discapacidad and nombres_representante and apellidos_representante and nacionalidad_representante and ci_representante and prefijo_num2 and telefono_representante and parestencorepresentante:
            correo_alternativo = correo_secundaria + dominio_correo_secundaria

            ci_representante_principal = nacionalidad_representante + "-" + ci_representante
            tlf_representante_principal = prefijo_num2 + telefono_representante

            if nombres_otrorepresentante and apellidos_otrorepresentante and nacionalidad_otrorepresentante and ci_otrorepresentante and prefijo_num3 and telefono_otrorepresentante and parestencootrorepresentante:
                
                ci_otro_representante = nacionalidad_otrorepresentante + "-" + ci_otrorepresentante
                tlf_representante_principal = prefijo_num3 + telefono_otrorepresentante

                if ci_otro_representante == ci_representante_principal:
                    return JsonResponse({
                        "titulo": "¡Advertencia!",
                        "estado": "fallo",
                        "icon": "warning",
                        "descripcion": "La cedula de identidad del Representante es identica a la cedula de identidad del primer representante, por favor ingrese la cedula correspondiente del representante."
                    })
                
                if ci_otro_representante == request.session.get("cedula_usuario"):
                    return JsonResponse({
                        "titulo": "¡Advertencia!",
                        "estado": "fallo",
                        "icon": "warning",
                        "descripcion": "La cedula de identidad del Representante es identica a la cedula de identidad del estudiante, por favor ingrese la cedula correspondiente del representante."
                    })
                
                PadresEstudiante.objects.create(nombres=nombres_otrorepresentante, apellidos=apellidos_otrorepresentante, cedula_identidad=ci_otrorepresentante, telefono=telefono_otrorepresentante, parentesco=parestencootrorepresentante, id_usuario=usuario)

            usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()
            if not usuario:
                return JsonResponse({
                    "estado": "fallo",
                    "titulo": "¡Advertencia!",
                    "icon": "warning",
                    "descripcion": "Usuario no encontrado"
                })
            
            if ci_representante_principal == request.session.get("cedula_usuario"):
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "La cedula de identidad del Representante es identica de la cedula de identidad del estudiante, por favor ingrese la cedula correspondiente del representante."
                })

            if Contacto.objects.filter(correo_alternativo=correo_alternativo).exclude(id_usuario=usuario).exists():
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "Este correo ya está registrado en otro usuario"
                })
                            
            if PadresEstudiante.objects.filter(cedula_identidad=ci_otrorepresentante).exclude(id_usuario=usuario).exists():
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "La cédula del segundo representante ya está registrada"
                })

            usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()
            usuario.genero = genero
            usuario.estado_civil = estado_civil
            usuario.save()

            contacto = Contacto.objects.filter(id_usuario=usuario).first()
            contacto.telefono_suplete = telefono_sucundario
            contacto.correo_alternativo = correo_alternativo
            contacto.save()

            PadresEstudiante.objects.create(nombres=nombres_representante, apellidos=apellidos_representante, cedula_identidad=ci_representante_principal, telefono=tlf_representante_principal, parentesco=parestencorepresentante, id_usuario=usuario)

            Nacimiento.objects.create(pais=pais_nacimiento, estado=estado_nacimiento, municipio=municipio_nacimiento, parroquia=parroquia_nacimiento, direccion_nacimiento=direccion_nacimiento, fecha_nacimiento=fecha_nacimiento, id_usuario=usuario)

            Residencia.objects.create(condicion_residencia=condicion_residencia, municipio=municipio_residencia, parroquia=parroquia_residencia, direccion_residencia=direccion_domicilio, id_usuario=usuario)

            InformacionSecundaria.objects.create(tipo_institucion=tipos_secundaria, nombre_institucion=nombre_secundaria, fecha_grado=fecha_graduacion, codigo_sni_opsu=codigo_opsu, id_usuario=usuario)

            Discapacidad.objects.create(codigo_carnet_discapacidad=carnet_dispacidad, nro_registro_medico=registro_medico, tipo_discapacidad=tipo_discapacidad, grado_discapacidad=grado_discapacidad, causa_discapacidad=causa_discapacidad, id_usuario=usuario)

            nucleos = {
                "Barinas": request.POST.getlist("pnf_Barinas"),
                "Barinitas": request.POST.getlist("pnf_Barinitas"),
                "Sopoco": request.POST.getlist("pnf_Sopoco"),
                "Pedraza": request.POST.getlist("pnf_Pedraza"),
            }

            asignacion_base = UsuarioAsignacion.objects.filter(id_usuario=usuario,id_perfil_id=5).first()
            trayecto_inicial = TrayectoAcademico.objects.get(trayecto="Inicial")
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

                        EstatusEstudiante.objects.create(
                            estatus="Pre-Inscrito(a)",
                            estado="Espera",
                            ingreso="Bachiller",
                            descripcion_ingreso="No ha presentado Inicial",
                            id_trayecto=trayecto_inicial,
                            fecha_ingreso=timezone.now().date(),
                            id_asignacion=asignacion_base)

                        primera_asignacion = False
                    else:
                        nueva_asignacion = UsuarioAsignacion.objects.create(
                            id_usuario=usuario,
                            id_perfil_id=5,  
                            id_nucleo=nucleo,
                            id_pnf=pnf)

                        EstatusEstudiante.objects.create(
                            estatus="Pre-Inscrito(a)",
                            estado="Espera",
                            ingreso="Bachiller",
                            descripcion_ingreso="No ha presentado Inicial",
                            id_trayecto=trayecto_inicial,
                            fecha_ingreso=timezone.now().date(),
                            id_asignacion=nueva_asignacion)
                
            nombre_estudiante = f"{usuario.nombres}_{usuario.apellidos}".replace(" ", "_")

            base_path = os.path.join(
                settings.BASE_DIR,
                "media",
                "documentosEstudiante",
                nombre_estudiante)
            
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

                    DocumentosEstudiante.objects.update_or_create(
                        id_usuario=usuario,
                        nombre_documento=nombre,
                        defaults={
                            "archivo": file_path
                        }
                    )
                    
            ruta_pdf = generar_documento_inscripcion(
                estudiante=usuario,
                contacto=contacto
            )

            # Crear contenido HTML del correo utilizando la plantilla
            html_email = render_to_string(
                "Email/comprobante_inscripcion.html",
                {
                    "nombres": usuario.nombres,
                    "apellidos": usuario.apellidos,
                    "fecha": timezone.now().strftime("%d/%m/%Y %H:%M:%S"),
                }
            )

            # Crear correo electrónico
            correo = EmailMessage(
                subject="Comprobante de Preinscripción - UPT José Félix Ribas",
                body=html_email,
                from_email="uptjfr2025@gmail.com",
                to=[contacto.correo_electronico]
            )

            # Indicar que el contenido del correo es HTML
            correo.content_subtype = "html"

            # Adjuntar comprobante PDF
            correo.attach_file(
                ruta_pdf
            )

            # Enviar correo
            correo.send()
                        
            request.session['registro_completado'] = True
            
            return JsonResponse({
                "estado": "success"
            })

        return JsonResponse({
            "titulo": "¡Advertencia!",
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se ha detectado uno o algunos campos vacios, por favor llene todos los campos."
        })

    return render(request, "completar_registro_estudiante.html")

def mostrar_pnfs_cursar(request):
    nucleo_seleccionado = request.POST.get("nucleo")

    nucleo = Nucleos.objects.filter(municipio=nucleo_seleccionado).first()
    if not nucleo:
        return JsonResponse({"pnfs": []})

    pnfs = PNFNucleo.objects.select_related("id_pnf").filter(id_nucleo=nucleo)
    
    datos = []
    for pnf_nucleo in pnfs:
        datos.append({
            "id": pnf_nucleo.id_pnf.id_pnf,
            "nombre": pnf_nucleo.id_pnf.pnf,
            "codigo": pnf_nucleo.id_pnf.codigo
        })

    return JsonResponse({
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
        
        if tipos_secundaria and nombre_secundaria and fecha_graduacion and codigo_opsu and carnet_dispacidad and registro_medico and tipo_discapacidad and grado_discapacidad and causa_discapacidad and nombres_representante and apellidos_representante and nacionalidad_representante and ci_representante and prefijo_num2 and telefono_representante and parestencorepresentante:

            ci_representante_principal = nacionalidad_representante + "-" + ci_representante
            tlf_representante_principal = prefijo_num2 + telefono_representante

            usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()

            if ci_representante_principal == request.session.get("cedula_usuario"):
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "La cedula de identidad del Representante es identica de la cedula de identidad del estudiante, por favor ingrese la cedula correspondiente del representante."
                })
            
            if PadresEstudiante.objects.filter(cedula_identidad=ci_representante_principal).exclude(id_usuario=usuario).exists():
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "La cédula del representante ya está registrada"
                })

            if PadresEstudiante.objects.filter(cedula_identidad=ci_otrorepresentante).exclude(id_usuario=usuario).exists():
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "La cédula del segundo representante ya está registrada"
                })

            if ci_otrorepresentante == ci_representante_principal:
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "La cedula de identidad del Representante es identica a la cedula de identidad del primer representante, por favor ingrese la cedula correspondiente del representante."
                })
                
            if ci_otrorepresentante == request.session.get("cedula_usuario"):
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "La cedula de identidad del Representante es identica a la cedula de identidad del estudiante, por favor ingrese la cedula correspondiente del representante."
                })

            PadresEstudiante.objects.create(nombres=nombres_representante, apellidos=apellidos_representante, cedula_identidad=ci_representante_principal, telefono=tlf_representante_principal, parentesco=parestencorepresentante, id_usuario=usuario)

            if nombres_otrorepresentante and apellidos_otrorepresentante and nacionalidad_otrorepresentante and ci_otrorepresentante and prefijo_num3 and telefono_otrorepresentante and parestencootrorepresentante:
                
                ci_otrorepresentante = nacionalidad_otrorepresentante + "-" + ci_otrorepresentante
                tlf_representante_principal = prefijo_num3 + telefono_otrorepresentante
                
                PadresEstudiante.objects.create(nombres=nombres_otrorepresentante, apellidos=apellidos_otrorepresentante, cedula_identidad=ci_otrorepresentante, telefono=telefono_otrorepresentante, parentesco=parestencootrorepresentante, id_usuario=usuario)

            InformacionSecundaria.objects.create(tipo_institucion=tipos_secundaria, nombre_institucion=nombre_secundaria, fecha_grado=fecha_graduacion, codigo_sni_opsu=codigo_opsu, id_usuario=usuario)

            Discapacidad.objects.create(codigo_carnet_discapacidad=carnet_dispacidad, nro_registro_medico=registro_medico, tipo_discapacidad=tipo_discapacidad, grado_discapacidad=grado_discapacidad, causa_discapacidad=causa_discapacidad, id_usuario=usuario)

            nucleos = {
                "Barinas": request.POST.getlist("pnf_Barinas"),
                "Barinitas": request.POST.getlist("pnf_Barinitas"),
                "Sopoco": request.POST.getlist("pnf_Sopoco"),
                "Pedraza": request.POST.getlist("pnf_Pedraza"),
            }

            asignacion_base = UsuarioAsignacion.objects.filter(id_usuario=usuario,id_perfil_id=5).first()
            trayecto_inicial = TrayectoAcademico.objects.get(trayecto="Inicial")
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

                        EstatusEstudiante.objects.create(
                            estatus="Pre-Inscrito(a)",
                            estado="Espera",
                            ingreso="Bachiller",
                            descripcion_ingreso="No ha presentado Inicial",
                            id_trayecto=trayecto_inicial,
                            fecha_ingreso=timezone.now().date(),
                            id_asignacion=asignacion_base)

                        primera_asignacion = False
                    else:
                        nueva_asignacion = UsuarioAsignacion.objects.create(
                            id_usuario=usuario,
                            id_perfil_id=5,  
                            id_nucleo=nucleo,
                            id_pnf=pnf)

                        EstatusEstudiante.objects.create(
                            estatus="Pre-Inscrito(a)",
                            estado="Espera",
                            ingreso="Bachiller",
                            descripcion_ingreso="No ha presentado Inicial",
                            id_trayecto=trayecto_inicial,
                            fecha_ingreso=timezone.now().date(),
                            id_asignacion=nueva_asignacion)
                
            nombre_estudiante = f"{usuario.nombres}_{usuario.apellidos}".replace(" ", "_")

            base_path = os.path.join(
                settings.BASE_DIR,
                "media",
                "documentosEstudiante",
                nombre_estudiante)
            
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

                    DocumentosEstudiante.objects.update_or_create(
                        id_usuario=usuario,
                        nombre_documento=nombre,
                        defaults={
                            "archivo": file_path
                        })

            contacto = Contacto.objects.filter(id_usuario=usuario).first()
                    
            ruta_pdf = generar_documento_inscripcion(
                estudiante=usuario,
                contacto=contacto
            )

            # Crear contenido HTML del correo utilizando la plantilla
            html_email = render_to_string(
                "Email/comprobante_inscripcion.html",
                {
                    "nombres": usuario.nombres,
                    "apellidos": usuario.apellidos,
                    "fecha": timezone.now().strftime("%d/%m/%Y %H:%M:%S"),
                }
            )

            # Crear correo electrónico
            correo = EmailMessage(
                subject="Comprobante de Preinscripción - UPT José Félix Ribas",
                body=html_email,
                from_email="uptjfr2025@gmail.com",
                to=[contacto.correo_electronico]
            )

            # Indicar que el contenido del correo es HTML
            correo.content_subtype = "html"

            # Adjuntar comprobante PDF
            correo.attach_file(
                ruta_pdf
            )

            # Enviar correo
            correo.send()

            request.session['registro_completado'] = True

            return JsonResponse({
                "estado": "success"
            })
        
        return JsonResponse({
            "titulo": "¡Advertencia!",
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se ha detectado uno o algunos campos vacios, por favor llene todos los campos."
        })

    return render(request, "completar_registro_pe.html")

def generar_documento_inscripcion(estudiante, contacto):
    # Crear la ruta donde se almacenarán los comprobantes PDF
    carpeta = os.path.join(
        settings.MEDIA_ROOT,
        "comprobantes",
        "preinscripciones"
    )

    # Crear las carpetas si no existen
    os.makedirs(carpeta, exist_ok=True)

    # Nombre del archivo PDF utilizando la cédula del estudiante
    nombre_archivo = (
        f"comprobante_preinscripcion_{estudiante.cedula_identidad}.pdf"
    )

    # Ruta completa donde se guardará el documento
    ruta_archivo = os.path.join(
        carpeta,
        nombre_archivo
    )

    # Configuración del documento PDF:
    # - Define ubicación del archivo
    # - Tamaño de página A4
    # - Márgenes del documento
    documento = SimpleDocTemplate(
        ruta_archivo,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Cargar estilos predeterminados de ReportLab
    estilos = getSampleStyleSheet()

    # Crear estilos personalizados usando Times New Roman (Times-Roman)
    estilo_titulo = ParagraphStyle(
        "TituloPersonalizado",
        parent=estilos["Title"],
        fontName="Times-Roman",
        fontSize=26,
        leading=32,
        alignment=TA_CENTER
    )

    estilo_datos = ParagraphStyle(
        "DatosPersonalizados",
        parent=estilos["Normal"],
        fontName="Times-Roman",
        fontSize=18,
        leading=25,
        alignment=TA_LEFT
    )

    estilo_final = ParagraphStyle(
        "TextoFinal",
        parent=estilos["Normal"],
        fontName="Times-Roman",
        fontSize=16,
        leading=22,
        alignment=TA_LEFT
    )

    # Lista donde se almacenarán todos los elementos del PDF
    contenido = []

    # Crear el título del documento
    titulo = Paragraph(
        "Comprobante de Preinscripción",
        estilo_titulo
    )

    # Agregar título al documento
    contenido.append(titulo)

    # Agregar espacio debajo del título
    contenido.append(
        Spacer(1, 20)
    )

    # Obtener la fecha y hora actual de generación del documento
    fecha_actual = timezone.now()

    # Información que aparecerá en el comprobante
    datos = [
        f"<b>Universidad:</b> UPT José Félix Ribas",
        f"<b>Proceso:</b> Preinscripción Académica",
        f"<b>Estudiante:</b> {estudiante.nombres} {estudiante.apellidos}",
        f"<b>Cédula:</b> {estudiante.cedula_identidad}",
        f"<b>Correo:</b> {contacto.correo_electronico}",
        f"<b>Fecha de emisión:</b> {fecha_actual.strftime('%d/%m/%Y %H:%M:%S')}",
    ]

    # Recorrer cada dato y agregarlo al PDF
    for dato in datos:
        # Agregar texto con formato
        contenido.append(
            Paragraph(
                dato,
                estilo_datos
            )
        )

        # Separación entre cada línea
        contenido.append(
            Spacer(1, 10)
        )

    # Espacio antes del mensaje final
    contenido.append(
        Spacer(1, 20)
    )

    # Mensaje de confirmación del comprobante
    contenido.append(
        Paragraph(
            "Este documento confirma que el estudiante realizó correctamente el proceso de preinscripción.",
            estilo_final
        )
    )

    # Generar físicamente el archivo PDF
    documento.build(contenido)

    # Retornar la ubicación del archivo creado
    return ruta_archivo

# INSCRIPCIÓN ESTUDIANTE DIRECTOR GENERAL

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

        secciones = []
        for seccion in SeccionAcademica.objects.select_related(
            "id_aula"
        ).filter(
            id_nucleo_id=id_nucleo,
            id_pnf_id=id_pnf
        ).order_by("seccion"):

            cantidad_estudiantes = SeccionEstudiante.objects.filter(id_seccion=seccion).count()

            if cantidad_estudiantes < 48:
                secciones.append({
                    "id_seccion": seccion.id_seccion,
                    "seccion": seccion.seccion,
                    "aula": seccion.id_aula.nombre_aula,
                    "turno": seccion.turno,
                    "cantidad_estudiantes": cantidad_estudiantes
                })

        estudiantes = EstatusEstudiante.objects.select_related(
            "id_asignacion",
            "id_asignacion__id_usuario",
            "id_asignacion__id_perfil",
            "id_asignacion__id_pnf",
            "id_asignacion__id_nucleo"
        ).filter(
            estatus="Pre-Inscrito(a)",
            estado="Espera",
            id_asignacion__id_perfil_id=5,
            id_asignacion__id_nucleo_id=id_nucleo,
            id_asignacion__id_pnf_id=id_pnf
        )

        datos = []
        for estudiante in estudiantes:
            usuario = estudiante.id_asignacion.id_usuario

            datos.append({
                "id_usuario": usuario.id_usuario,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "cedula": usuario.cedula_identidad
            })

        return JsonResponse({
            "estado": "exito",
            "secciones": secciones,
            "estudiantes": datos
        })

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

        informacion_secundaria = InformacionSecundaria.objects.filter(id_usuario=usuario).values().first()

        discapacidad = Discapacidad.objects.filter(id_usuario=usuario).values().first()

        representantes = list(
            PadresEstudiante.objects.filter(id_usuario=usuario).values()
        )

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

        estatus_estudiante = EstatusEstudiante.objects.select_related(
            "id_asignacion"
        ).filter(
            id_asignacion__id_usuario=usuario,
            id_asignacion__id_nucleo_id=id_nucleo,
            id_asignacion__id_pnf_id=id_pnf,
            id_asignacion__id_perfil_id=5,
            estatus="Pre-Inscrito(a)",
            estado="Espera"
        ).first()

        if not estatus_estudiante:
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "No se encontró la preinscripción del estudiante."
            })

        # RECHAZAR
        if accion == "rechazado":

            estatus_estudiante.estado = "Rechazado"
            estatus_estudiante.save()

            return JsonResponse({
                "titulo": "¡Éxito!",
                "estado": "exito",
                "icon": "success",
                "descripcion": "La preinscripción fue rechazada."
            })

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

        if SeccionEstudiante.objects.filter(
            id_usuario=usuario,
            fecha_final__isnull=True
        ).exists():

            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "El estudiante ya posee una sección activa."
            })

        SeccionEstudiante.objects.create(
            id_seccion=seccion,
            id_usuario=usuario,
            fecha_inicio=timezone.now().date()
        )

        estatus_estudiante.estatus = "Inscrito(a)"
        estatus_estudiante.estado = "Activo"
        estatus_estudiante.save()

        return JsonResponse({
            "titulo": "¡Éxito!",
            "estado": "exito",
            "icon": "success",
            "descripcion": "El estudiante fue inscrito correctamente."
        })

    return render(request, "inscripcion_estudiante.html")

# CRUD PNF

def pnfs_registrada(request):

    data = PNFNucleo.objects.select_related("id_pnf", "id_nucleo")

    resultado = defaultdict(lambda: {
        "id_pnf": None,
        "pnf": "",
        "codigo": "",
        "nucleos": []
    })

    for item in data:
        pnf_id = item.id_pnf.id_pnf

        resultado[pnf_id]["id_pnf"] = pnf_id
        resultado[pnf_id]["pnf"] = item.id_pnf.pnf
        resultado[pnf_id]["codigo"] = item.id_pnf.codigo

        resultado[pnf_id]["nucleos"].append({
            "id_nucleo": item.id_nucleo.id_nucleo,
            "municipio": item.id_nucleo.municipio
        })

    return JsonResponse({
        "estado": "exito",
        "pnfs": list(resultado.values())
    })

def datos_pnf(request):
    if request.method == "POST":
        pnf = request.POST.get("pnf")

        pnfs = Pnf.objects.get(id_pnf=pnf)

        nucleos_asignados = []
        relaciones = PNFNucleo.objects.filter(id_pnf=pnfs)
        for relacion in relaciones:
            nucleos_asignados.append({
                "id": relacion.id_nucleo.id_nucleo,
                "municipio": relacion.id_nucleo.municipio
            })

        todos_nucleos = []
        for nucleo in Nucleos.objects.all():
            todos_nucleos.append({
                "id": nucleo.id_nucleo,
                "municipio": nucleo.municipio
            })

        return JsonResponse({
            "pnf": {
                "id": pnfs.id_pnf,
                "nombre": pnfs.pnf,
                "codigo": pnfs.codigo,
                "periodo_academico": pnfs.periodo_academico
            },
            "nucleos": nucleos_asignados,
            "todos_nucleos": todos_nucleos
        })

def guardar_actuailizacion_pnf(request):
    if request.method == "POST":
        id_pnf = request.POST.get("pnfseleccionado")
        nombre_pnf = request.POST.get("nombrepnf", "").strip()
        codigo_pnf = request.POST.get("codigopnf", "").strip()
        periodoacademico_pnf = request.POST.get("periodoacademico", "").strip()
        nucleos = request.POST.getlist("nucleo")

        if not id_pnf or not nombre_pnf or not codigo_pnf or not nucleos or not periodoacademico_pnf:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Se encuentra vacío al menos un campo."
            })

        try:
            with transaction.atomic():

                pnf = Pnf.objects.get(id_pnf=id_pnf)                
                pnf.pnf = nombre_pnf
                pnf.codigo = codigo_pnf
                pnf.periodo_academico = periodoacademico_pnf
                pnf.save()

                PNFNucleo.objects.filter(id_pnf=pnf).delete()

                for id_nucleo in nucleos:
                    nucleo = Nucleos.objects.get(id_nucleo=id_nucleo)
                    PNFNucleo.objects.create(
                        id_pnf=pnf,
                        id_nucleo=nucleo
                    )

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "PNF actualizado correctamente."
            })

        except Exception as e:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": str(e)
            })

    return JsonResponse({
        "estado": "fallo",
        "icon": "warning",
        "descripcion": "Método no permitido."
    })

def modulo_pnf(request):
    if request.method == "POST":
        nombre_pnf = request.POST.get("nombrepnf")
        codigo_pnf = request.POST.get("codigopnf")
        periodoacademico_pnf = request.POST.get("periodoacademico")
        nucleos = request.POST.getlist("nucleos")

        if nombre_pnf and codigo_pnf and nucleos:
            existe = Pnf.objects.filter(codigo__iexact=codigo_pnf).exists()
            if existe:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Debe ingresar otro código."
                })

            existe = Pnf.objects.filter(pnf__iexact=nombre_pnf).exists()
            if existe:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe un Programa Nacional de Formación con ese nombre."
                })

            pnf_registrado = Pnf.objects.create(pnf=nombre_pnf, codigo=codigo_pnf, periodo_academico=periodoacademico_pnf)
            for nucleo_id in nucleos:
                PNFNucleo.objects.create(id_pnf=pnf_registrado, id_nucleo_id=nucleo_id)

            return JsonResponse({
                "icon": "success",
                "descripcion": "PNF se registro exitosamente."
            })

        return JsonResponse({
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })

    return render(request, "pnfs.html")

# CRUD NÚCLEO

def nucleos_registrados(request):
    nucleos = list(Nucleos.objects.values(
        "id_nucleo",
        "municipio",
        "direccion"
    ))

    return JsonResponse({
        "estado": "exito",
        "nucleos": nucleos
    })

def datos_nucleo(request):
    if request.method == "POST":
        id_nucleo = request.POST.get("nucleo")

        nucleo = Nucleos.objects.filter(id_nucleo=id_nucleo).first()

        if not nucleo:
            return JsonResponse({
                "estado": "error",
                "mensaje": "Núcleo no encontrado"
            })

        return JsonResponse({
            "estado": "ok",
            "nucleo": {
                "id": nucleo.id_nucleo,
                "municipio": nucleo.municipio,
                "direccion": nucleo.direccion
            }
        })

def guardar_actualizacion_nucleo(request):
    if request.method == "POST":
        id_nucleo = request.POST.get("nucleoseleccionado")
        municipio = request.POST.get("municipio")
        direccion = request.POST.get("direccionnucleo")

        if not id_nucleo or not municipio or not direccion:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Se encuentra vacío al menos un campo."
            })

        try:
            with transaction.atomic():

                nucleo = Nucleos.objects.get(id_nucleo=id_nucleo)                
                nucleo.municipio = municipio
                nucleo.direccion = direccion
                nucleo.save()

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "PNF actualizado correctamente."
            })

        except Exception as e:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": str(e)
            })

    return JsonResponse({
        "estado": "fallo",
        "icon": "warning",
        "descripcion": "Método no permitido."
    })

def modulo_nucleo(request):
    if request.method == "POST":
        municipio = request.POST.get("municipio")
        direccion = request.POST.get("direccion")
        
        if municipio and direccion:

            Nucleos.objects.create(municipio=municipio, direccion=direccion)

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Núcleo se registro exitosamente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })
    
    return render(request, "nucleos.html")

# CRUD SECCIÓN ACADÉMICA

def secciones_registradas(request):
    secciones = list(
        SeccionAcademica.objects.values(
            "id_seccion",
            "seccion",
            "turno",
            "id_nucleo__municipio",
            "id_pnf__pnf",
            "id_trayecto__trayecto",
            "id_aula__nombre_aula",
            "id_aula__nombre_edificio",
            "id_aula__piso_edificio"
        )
    )

    return JsonResponse({
        "estado": "exito",
        "secciones": secciones
    })

def datos_seccion(request):
    if request.method == "POST":
        id_seccion = request.POST.get("seccion")

        seccion = SeccionAcademica.objects.filter(id_seccion=id_seccion).first()

        if not seccion:
            return JsonResponse({
                "estado": "error",
                "mensaje": "Sección no encontrada"
            })

        return JsonResponse({
            "estado": "ok",
            "seccion": {
                "id_seccion": seccion.id_seccion,
                "seccion": seccion.seccion,
                "turno": seccion.turno,
                "nucleo": {
                    "id": seccion.id_nucleo.id_nucleo,
                    "nombre": seccion.id_nucleo.municipio
                },
                "pnf": {
                    "id": seccion.id_pnf.id_pnf,
                    "nombre": seccion.id_pnf.pnf
                },
                "trayecto": {
                    "id": seccion.id_trayecto.id_trayecto,
                    "nombre": seccion.id_trayecto.trayecto
                },
                "aula": {
                    "id": seccion.id_aula.id_aula,
                    "nombre": seccion.id_aula.nombre_aula
                }
            }
        })
    
def guardar_actualizacion_seccion(request):
    if request.method == "POST":
        id_seccion = request.POST.get("seccion")
        nucleo = request.POST.get("actualizar_nucleo")
        pnf = request.POST.get("actualizar_pnf")
        trayecto = request.POST.get("actualizar_trayecto")
        aula = request.POST.get("actualizar_aula")
        turno = request.POST.get("actualizar_turno")
        nuevo_seccion = request.POST.get("actualizar_seccion")

        if not id_seccion or not nucleo or not pnf or not trayecto or not aula or not turno or not nuevo_seccion:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Se encuentra vacío al menos un campo."
            })

        try:
            with transaction.atomic():
                id_nucleo = Nucleos.objects.get(id_nucleo=nucleo)
                id_pnf = Pnf.objects.get(id_pnf=pnf)
                id_trayecto = TrayectoAcademico.objects.get(id_trayecto=trayecto)
                id_aula = AulaAcademica.objects.get(id_aula=aula)
                seccion = SeccionAcademica.objects.get(id_seccion=id_seccion)

                seccion.id_nucleo = id_nucleo
                seccion.id_pnf = id_pnf
                seccion.id_trayecto = id_trayecto
                seccion.id_aula = id_aula
                seccion.turno = turno
                seccion.seccion = nuevo_seccion

                seccion.save()

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Sección actualizado correctamente."
            })

        except Exception as e:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": str(e)
            })

    return JsonResponse({
        "estado": "fallo",
        "icon": "warning",
        "descripcion": "Método no permitido."
    })

def modulo_seccion(request):
    if request.method == "POST":
        nucleo = request.POST.get("registro_nucleo")
        pnf = request.POST.get("registro_pnf")
        trayecto = request.POST.get("registro_trayecto")
        aula = request.POST.get("registro_aula")
        turno = request.POST.get("registro_turno")
        seccion = request.POST.get("registro_seccion")
        
        if nucleo and pnf and trayecto and aula and turno and seccion:
            id_nucleo = Nucleos.objects.get(id_nucleo=nucleo)
            id_pnf = Pnf.objects.get(id_pnf=pnf)
            id_trayecto = TrayectoAcademico.objects.get(id_trayecto=trayecto)
            id_aula = AulaAcademica.objects.get(id_aula=aula)
        
            SeccionAcademica.objects.create(id_nucleo=id_nucleo, id_pnf=id_pnf, id_trayecto=id_trayecto, id_aula=id_aula, turno=turno, seccion=seccion)

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Sección se registro exitosamente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })
    
    return render(request, "secciones.html")

# CRUD MATERIA

def materias_almacenada(request):
   if request.method == "POST":
        pnf = request.POST.get("pnf")
        trayecto = request.POST.get("trayecto")

        materias_query = Materia.objects.select_related(
            "id_trayecto",
            "id_pnf"
        )
        
        if pnf and pnf != "ninguno":
            materias_query = materias_query.filter(id_pnf=pnf)

        if trayecto and trayecto != "ninguno":
            materias_query = materias_query.filter(
                id_trayecto=trayecto
            )

        materias = list(
            materias_query.values(
                "id_materia",
                "nombre",
                "codigo",
                "tipo_materia",
                "recuperacion",
                "id_pnf",
                "id_trayecto"
            )
        )

        # Agregar nombre del trayecto
        for materia in materias:
            trayecto_obj = TrayectoAcademico.objects.filter(
                id_trayecto=materia["id_trayecto"]
            ).first()

            materia["trayecto"] = (
                trayecto_obj.trayecto 
                if trayecto_obj 
                else ""
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
                "id_trayecto"
            ).get(id_materia=id_materia)

            return JsonResponse({
                "estado": "ok",
                "materia": {
                    "id_materia": materia.id_materia,
                    "nombre": materia.nombre,
                    "codigo": materia.codigo,
                    "tipo_materia": materia.tipo_materia,
                    "recuperacion": materia.recuperacion
                },
                "trayecto": {
                    "id_trayecto": materia.id_trayecto.id_trayecto,
                    "trayecto": materia.id_trayecto.trayecto
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

            trayecto = TrayectoAcademico.objects.get(id_trayecto=trayecto_materia)

            materia = Materia.objects.get(id_materia=id_materia)
            materia.nombre = nombre
            materia.codigo = codigo
            materia.tipo_materia = periodo_materia
            materia.id_trayecto = trayecto
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
        
        trayecto_obj = TrayectoAcademico.objects.get(id_trayecto=trayecto)

        materia = Materia.objects.create(
            nombre=nombre,
            codigo=codigo,
            tipo_materia=periodo_materia,
            id_trayecto=trayecto_obj,
            recuperacion=reparacion,
            id_pnf=pnf_obj
        )

        mapa_periodo_bd = {
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

    return render(request, "materias.html")

# CRUD CALENDARIO ACADÉMICO

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

        if not all([fechainicial, fechareparacion, fechatramoI, fechatramoII,
                    fechatramoIII, fechasemestreI, fechasemestreII]):

            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Campos vacíos."
            })

        anio = datetime.strptime(fechainicial, "%Y-%m-%d").year

        if CalendarioAcademico.objects.filter(fecha_inicio__year=anio).exists():
            return JsonResponse({
                "estado": "error",
                "icon": "warning",
                "descripcion": f"El calendario del año {anio} ya existe."
            })

        mapa = [
            ("INICIAL", fechainicial),
            ("REPARACION", fechareparacion),
            ("TRAMO I", fechatramoI),
            ("TRAMO II", fechatramoII),
            ("TRAMO III", fechatramoIII),
            ("SEMESTRE I", fechasemestreI),
            ("SEMESTRE II", fechasemestreII),
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

# ACTUALIZAR DATOS USUARIO

def datos_usuario(request):
    cedula_identidad = request.session.get("cedula_usuario")
    
    perfil = request.POST.get("perfil")

    usuario = Usuario.objects.get(cedula_identidad=cedula_identidad)
    datos = {
        "usuario": model_to_dict(usuario),
        "contacto": model_to_dict(usuario.contacto),
        "residencia": model_to_dict(usuario.residencia),
    }

    if perfil == "Estudiante":
        discapacidad = getattr(usuario, "discapacidad", None)
        datos["discapacidad"] = (
            model_to_dict(discapacidad)
            if discapacidad
            else None
        )
    return JsonResponse(datos)

def correos_usuario(request):
    cedula_identidad = request.session.get("cedula_usuario")

    token = str(uuid.uuid4())
    request.session['token_recuperacion'] = token

    if not cedula_identidad:
        return JsonResponse({
            "status": "error",
            "mensaje": "No hay una sesión activa."
        }, status=401)

    try:
        usuario = Usuario.objects.get(cedula_identidad=cedula_identidad)

        contacto = Contacto.objects.get(id_usuario=usuario)

        return JsonResponse({
            "status": "ok",
            "correo_principal": contacto.correo_electronico,
            "correo_alternativo": contacto.correo_alternativo,
        })

    except Usuario.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "mensaje": "Usuario no encontrado."
        }, status=404)

    except Contacto.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "mensaje": "El usuario no posee información de contacto."
        }, status=404)

def enviar_codigo_actualizar_correo(request):
    if request.method == "POST":
        cedula = request.session.get("cedula_usuario")
        correo_seleccionado = request.POST.get("correo_verificacion")

        usuario = Usuario.objects.get(cedula_identidad=cedula)
        contacto = Contacto.objects.get(id_usuario=usuario)

        if correo_seleccionado == "principal":
            correo_electronico = contacto.correo_electronico
        else:
            correo_electronico = contacto.correo_alternativo

        return enviar_codigo_verificacion(
            usuario.nombres,
            usuario.apellidos,
            correo_electronico,
            usuario.cedula_identidad,
            request.session["token_recuperacion"]
        )

def autenticacion_actualizar_correo(request):
    if request.method == "POST":
        cedula = request.session.get("cedula_usuario")
        codigo_ingresado = request.POST.get("codigocorreo")

        usuario = Usuario.objects.get(cedula_identidad=cedula)
        
        verificacion = VerificacionCodigo.objects.filter(cedula_identidad=usuario.cedula_identidad,token=request.session.get("token_recuperacion")).first()

        if not codigo_ingresado:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Debe ingresar el código de verificación",
                "accion": "input_vacio"
            })

        if verificacion and verificacion.fecha_expiracion < timezone.now():
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "El código ha expirado, debe solicitar el código a través del botón de reenviar código",
                "accion": "expirado"
            })

        respuesta = validar_codigo(
            codigo_ingresado,
            usuario.cedula_identidad,
            request.session["token_recuperacion"]
        )

        datos = json.loads(respuesta.content)
        request.session["correo_verificado"] = True
        
        if datos.get("estado") == "exito":    
            verificacion.intentos = 0
            verificacion.bloqueado_hasta = None
            verificacion.activo = 0
            verificacion.save()

        return respuesta

def actualizar_datosusuario(request):
    if request.method == "POST":
        cedula_identidad = request.session.get("cedula_usuario")
        perfil = request.session.get("perfil")

        telefono_principal = request.POST.get("num_telefono_principal")
        prefijo_principal = request.POST.get("prefijo_telefono_principal")

        telefono_secundaria = request.POST.get("num_telefono_secundaria")
        prefijo_secundaria = request.POST.get("prefijo_telefono_secundaria")

        correo_principal = request.POST.get("correo_principal")
        dominio_principal = request.POST.get("dominio_correo_principal")

        correo_secundaria = request.POST.get("correo_secundaria")
        dominio_secundaria = request.POST.get("dominio_correo_secundaria")

        condicion_residencia = request.POST.get("condicionresidencia")
        municipio_residencia = request.POST.get("municipioresidencia")
        parroquia_residencia = request.POST.get("parroquiaresidencia")
        direccion_domicilio = request.POST.get("direcciondomicilio")

        carnet_discapacidad = request.POST.get("carnet_dispacidad")
        registro_medico = request.POST.get("registro_medico")
        tipos_discapacidad = request.POST.get("tipos_discapacidad")
        grado_discapacidad = request.POST.get("grado_discapacidad")
        causa_discapacidad = request.POST.get("causa_discapacidad")

        if telefono_principal and prefijo_principal and correo_principal and dominio_principal and correo_secundaria and dominio_secundaria and condicion_residencia and municipio_residencia and parroquia_residencia and direccion_domicilio:
            try:
                if telefono_secundaria == "" and prefijo_secundaria == "":
                    telefono_num2 = "N/A"
                else:
                    telefono_num2 = prefijo_secundaria + telefono_secundaria
                
                telefono_num1 = prefijo_principal + telefono_principal

                correo_num1 = correo_principal + dominio_principal
                correo_num2 = correo_secundaria + dominio_secundaria

                usuario = Usuario.objects.get(cedula_identidad=cedula_identidad)

                contacto = usuario.contacto
                contacto.telefono_personal = telefono_num1
                contacto.telefono_suplete = telefono_num2
                contacto.correo_electronico = correo_num1
                contacto.correo_alternativo = correo_num2
                contacto.save()

                residencia = usuario.residencia
                residencia.condicion_residencia = condicion_residencia
                residencia.municipio = municipio_residencia
                residencia.parroquia = parroquia_residencia
                residencia.direccion_residencia = direccion_domicilio
                residencia.save()

                if perfil == "Estudiante":
                    discapacidad = Discapacidad.objects.get_or_create(id_usuario=usuario)

                    discapacidad.codigo_carnet_discapacidad = carnet_discapacidad
                    discapacidad.nro_registro_medico = registro_medico
                    discapacidad.tipo_discapacidad = tipos_discapacidad
                    discapacidad.grado_discapacidad = grado_discapacidad
                    discapacidad.causa_discapacidad = causa_discapacidad
                    discapacidad.save()

                return JsonResponse({
                    "estado": "ok",
                    "icon": "success",
                    "descripcion": "Los datos se actualizaron existosamente."
                })

            except Usuario.DoesNotExist:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "Ocurrio un problema al momento de actualizar los datos."
                })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío, por favor rellene los campos."
        })
    
    return render(request, "actualizar_datosusuario.html")

# ASIGNAR MATERIA A DOCENTE

def pnfs_pertenece_nucleo(request):
    if request.method == "POST":
        nucleo = request.POST.get("nucleo")

        pnfs = PNFNucleo.objects.filter(
            id_nucleo=nucleo
        ).values(
            "id_pnf__id_pnf",
            "id_pnf__pnf",
            "id_pnf__periodo_academico"
        )

        lista = []

        for pnf in pnfs:
            lista.append({
                "id_pnf": pnf["id_pnf__id_pnf"],
                "pnf": pnf["id_pnf__pnf"],
                "periodo_academico": pnf["id_pnf__periodo_academico"],
            })

        return JsonResponse({"pnfs": lista})
    
def docentes_registrados(request):
    if request.method == "POST":
        nucleo = request.POST.get("nucleo")
        pnf = request.POST.get("pnf")

        if not nucleo or not pnf:
            return JsonResponse({
                "estado": "error",
                "usuarios": []
            })

        docentes = (
            UsuarioAsignacion.objects
            .select_related("id_usuario")
            .filter(
                id_perfil__perfil="Docente",
                id_nucleo_id=nucleo,
                id_pnf_id=pnf
            )
        )

        usuarios = [
            {
                "id_asignacion": docente.id_asignacion,
                "id_usuario": docente.id_usuario.id_usuario,
                "nombres": docente.id_usuario.nombres,
                "apellidos": docente.id_usuario.apellidos,
            }
            for docente in docentes
        ]

        return JsonResponse({
            "estado": "exito",
            "usuarios": usuarios
        })

    return JsonResponse({
        "estado": "error",
        "usuarios": []
    })

def materias_registradas(request):
    if request.method == "POST":
        pnf = request.POST.get("pnf")

        if not pnf:
            return JsonResponse({
                "estado": "error",
                "materias": []
            })

        materias = (
            Materia.objects
            .filter(id_pnf_id=pnf)
            .values(
                "id_materia",
                "nombre",
                "codigo",
                "tipo_materia",
                "recuperacion",
                "id_trayecto__trayecto"
            )
            .order_by(
                "id_trayecto__trayecto",
                "nombre"
            )
        )

        return JsonResponse({
            "estado": "exito",
            "materias": list(materias)
        })

    return JsonResponse({
        "estado": "error",
        "materias": []
    })

def modulo_asignar_materia_docente(request):
    if request.method == "POST":
        id_asignacion = request.POST.get("docentes")
        materias = request.POST.getlist("materias")

        if not id_asignacion or not materias:
            return JsonResponse({
                "estado": "error",
                "descripcion": "Debe seleccionar un docente y al menos una materia.",
                "icon": "warning"
            })

        asignacion = UsuarioAsignacion.objects.get(id_asignacion=id_asignacion)

        with transaction.atomic():
            for id_materia in materias:
                MateriaAsignada.objects.get_or_create(id_asignacion=asignacion, id_materia_id=id_materia)

        return JsonResponse({
            "estado": "success",
            "descripcion": "Las materias fueron asignadas correctamente al docente.",
            "icon": "success"
        })

    return render(request, "asignar_materia.html")

#  AUTORIDADES

def autoridades_registradas(request):

    autoridades = Autoridades.objects.all().values(
        "id_autoridad",
        "nombres",
        "apellidos",
        "cedula_identidad",
        "cargo",
        "resolucion"
    )

    return JsonResponse(list(autoridades), safe=False)

def datos_autoridad(request):
    if request.method == "POST":
        id_autoridad = request.POST.get("id")

        autoridad = Autoridades.objects.filter(id_autoridad=id_autoridad).first()

        if not autoridad:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "La autoridad no existe."
            })

        return JsonResponse({
            "id_autoridad": autoridad.id_autoridad,
            "nombres": autoridad.nombres,
            "apellidos": autoridad.apellidos,
            "cedula": autoridad.cedula_identidad,
            "genero": autoridad.genero,
            "cargo": autoridad.cargo,
            "resolucion": autoridad.resolucion
        })

def actualizar_datos_autoridad(request):
    if request.method == "POST":
        id_autoridad = request.POST.get("usuarioseleccionado")
        nombres = request.POST.get("nombres_actualizarautoridades")
        apellidos = request.POST.get("apellidos_actualizarautoridades")
        nacionalidad = request.POST.get("nacionalidad_actualizarautoridades")
        cedula = request.POST.get("cedula_actualizarautoridades")
        genero = request.POST.get("genero_actualizarautoridades")
        cargo = request.POST.get("cargo_actualizarautoridades")
        resolucion = request.POST.get("resolucion_actualizarautoridades")

        if nombres and apellidos and nacionalidad and cedula and genero and cargo and resolucion:
            
            cedula_identidad = nacionalidad + "-" + cedula

            autoridad = Autoridades.objects.filter(id_autoridad=id_autoridad).first()

            if not autoridad:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "La autoridad no existe."
                })
            
            autoridad.nombres = nombres
            autoridad.apellidos = apellidos
            autoridad.cedula_identidad = cedula_identidad
            autoridad.genero = genero
            autoridad.cargo = cargo
            autoridad.resolucion = resolucion
            autoridad.save()

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Se actualizo exitosamente los datos de la autoridad."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })

def modulo_autoridades(request):    
    if request.method == "POST":
        nombres = request.POST.get("nombres_registrarautoridades")
        apellidos = request.POST.get("apellidos_registrarautoridades")
        nacionalidad = request.POST.get("nacionalidad_actualizarautoridades")
        cedula = request.POST.get("cedula_registrarautoridades")
        genero = request.POST.get("genero_registrarautoridades")
        cargo = request.POST.get("cargo_registrarautoridades")
        resolucion = request.POST.get("resolucion_registrarautoridadess")

        if nombres and apellidos and nacionalidad and cedula and genero and cargo and resolucion:

            cedula_autoridad = nacionalidad + "-" + cedula

            if Autoridades.objects.filter(cedula_identidad__iexact=cedula_autoridad).exists():
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "Ya se encuentra registrado dicho usuario."
                })
            
            if Autoridades.objects.filter(resolucion__iexact=resolucion).exists():
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "Ya se encuentra registrado una resolución."
                })
            
            Autoridades.objects.create(nombres=nombres, apellidos=apellidos, cedula_identidad=cedula_autoridad, genero=genero, cargo=cargo, resolucion=resolucion)

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Las materias fueron asignadas correctamente al docente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })

    return render(request, "autoridades.html")

# ACTUALIZAR DATOS DE USUARIOS (ENCARGADO DE CONTROL DE ESTUDIO, DOCENTES, ESTUDIANTES Y COORDINADORES PNF)

def buscar_datos_usuario(request):
    if request.method == "POST":

        nacionalidad = request.POST.get("nacionalidad_busqueda")
        cedula = request.POST.get("cedula_busqueda")

        cedulausuario = f"{nacionalidad}-{cedula}"

        usuario = (
            Usuario.objects
            .select_related(
                "contacto",
                "residencia",
                "nacimiento",
                "profesional",
                "discapacidad",
                "secundaria"
            )
            .prefetch_related("padresEstudiante")
            .filter(cedula_identidad=cedulausuario)
            .first()
        )

        if not usuario:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "Usuario no encontrado"
            })

        asignacion = (
            UsuarioAsignacion.objects
            .select_related("id_perfil")
            .filter(id_usuario=usuario)
            .first()
        )

        perfil = asignacion.id_perfil.perfil if asignacion else None

        contacto = getattr(usuario, "contacto", None)
        residencia = getattr(usuario, "residencia", None)
        nacimiento = getattr(usuario, "nacimiento", None)

        respuesta = {
            "estado": "correcto",
            "perfil": perfil,
            "usuario": model_to_dict(usuario),
            "contacto": model_to_dict(contacto) if contacto else None,
            "residencia": model_to_dict(residencia) if residencia else None,
            "nacimiento": model_to_dict(nacimiento) if nacimiento else None,
        }

        if perfil == "Estudiante":

            discapacidad = getattr(usuario, "discapacidad", None)
            secundaria = getattr(usuario, "secundaria", None)

            respuesta["discapacidad"] = (
                model_to_dict(discapacidad)
                if discapacidad else None
            )

            respuesta["secundaria"] = (
                model_to_dict(secundaria)
                if secundaria else None
            )

            respuesta["padres"] = [
                model_to_dict(padre)
                for padre in usuario.padresEstudiante.all()
            ]

        else:

            profesional = getattr(usuario, "profesional", None)

            respuesta["profesion"] = (
                model_to_dict(profesional)
                if profesional else None
            )

        return JsonResponse(respuesta)

    return JsonResponse({
        "estado": "fallo",
        "descripcion": "Método no permitido"
    })

def modulo_actualizar_usuarios(request):
    if request.method == "POST":
        usuario_id = request.POST.get("id_usuario")

        nombres_actualizar = request.POST.get("nombres_actualizar")
        apellidos_actualizar = request.POST.get("apellidos_actualizar")
        genero_actualizar = request.POST.get("genero_actualizar")
        nacionalidad_actualizar = request.POST.get("nacionalidad_actualizar")
        cedula_actualizar = request.POST.get("cedula_actualizar")
        estado_civil_actualizar = request.POST.get("estado_civil_actualizar")
        
        prefijo_principal = request.POST.get("prefijo_principal")
        telefono_principal = request.POST.get("telefono_principal")
        prefijo_secundaria = request.POST.get("prefijo_secundaria")
        telefono_secundaria = request.POST.get("telefono_secundaria")
        nombre_correo_principal = request.POST.get("nombre_correo_principal")
        dominio_correo_principal = request.POST.get("dominio_correo_principal")
        nombre_correo_secundaria = request.POST.get("nombre_correo_secundaria")
        dominio_correo_secundaria = request.POST.get("dominio_correo_secundaria")
        
        paisnacimiento = request.POST.get("paisnacimiento")
        estadonacimiento = request.POST.get("estadonacimiento")
        estado_novzla_personal = request.POST.get("estado_novzla_personal")
        municipionacimiento = request.POST.get("municipionacimiento")
        municipio_novzla_personal = request.POST.get("municipio_novzla_personal")
        parroquianacimiento = request.POST.get("parroquianacimiento")
        parroquia_novzla_personal = request.POST.get("parroquia_novzla_personal")
        direccionnacimiento = request.POST.get("direccionnacimiento")
        fechanacimiento = request.POST.get("fechanacimiento")
        
        condicionresidencia = request.POST.get("condicionresidencia")
        municipioresidencia = request.POST.get("municipioresidencia")
        parroquiaresidencia = request.POST.get("parroquiaresidencia")
        direcciondomicilio = request.POST.get("direcciondomicilio")
        
        profesion = request.POST.get("profesion")
        universidad = request.POST.get("universidad")
        paisprofesion = request.POST.get("paisprofesion")
        
        tipos_secundaria = request.POST.get("tipossecundaria")
        nombre_liceo = request.POST.get("nombreliceo")
        fecha_graduacion = request.POST.get("fecha_graduacion")
        codigo_opsu = request.POST.get("codigo_opsu")
        
        nombres_representante = request.POST.get("nombresrepresentante")
        apellidos_representante = request.POST.get("apellidosrepresentante")
        nacionalidad_representante = request.POST.get("nacionalidadrepresentante")
        ci_representante = request.POST.get("ci_representante")
        prefijo_num_representante = request.POST.get("prefijo_num_representante")
        telefono_representante = request.POST.get("telefono_representante")
        parestenco = request.POST.get("parestenco")
        
        nombres_otro_representante = request.POST.get("nombresotrorepresentante")
        apellidos_otro_representante = request.POST.get("apellidosotrorepresentante")
        nacionalidad_otro_representante = request.POST.get("nacionalidad_otrorepresentante")
        ci_otro_representante = request.POST.get("ci_otrorepresentante")
        prefijo_num_otro_representante = request.POST.get("prefijo_num_otrorepresentante")
        telefono_otro_representante = request.POST.get("telefono_otrorepresentante")
        parestenco_otro_representante = request.POST.get("parestencootrorepresentante")
        
        carnet_dispacidad = request.POST.get("carnet_dispacidad")
        registro_medico = request.POST.get("registro_medico")
        tipos_discapacidad = request.POST.get("tipos_discapacidad")
        grado_discapacidad = request.POST.get("grado_discapacidad")
        causa_discapacidad = request.POST.get("causa_discapacidad")

        if nombres_actualizar and apellidos_actualizar and genero_actualizar and nacionalidad_actualizar and cedula_actualizar and estado_civil_actualizar and prefijo_principal and telefono_principal and nombre_correo_principal and dominio_correo_principal and nombre_correo_secundaria and dominio_correo_secundaria and condicionresidencia and municipioresidencia and parroquiaresidencia and direcciondomicilio:

            cedula_identidad = nacionalidad_actualizar+"-"+cedula_actualizar
            telefono_personal = prefijo_principal+telefono_principal
            
            if prefijo_secundaria and telefono_secundaria:
                telefono_secundario = prefijo_secundaria+telefono_secundaria
            else:
                telefono_secundario = "N/A"

            correo_electronico = nombre_correo_principal+dominio_correo_principal
            correo_alternativo = nombre_correo_secundaria+dominio_correo_secundaria

            if paisnacimiento == "Venezuela":
                estado = estadonacimiento
                municipio = municipionacimiento
                parroquia = parroquianacimiento
            else:
                estado = estado_novzla_personal
                municipio = municipio_novzla_personal
                parroquia = parroquia_novzla_personal

            usuario = get_object_or_404(Usuario, pk=usuario_id)
            
            asignacion = (
                UsuarioAsignacion.objects
                .select_related("id_perfil")
                .filter(id_usuario=usuario)
                .first()
            )

            if not asignacion:
                return JsonResponse({
                    "estado": "fallo",
                    "descripcion": "El usuario no tiene un perfil asignado."
                })

            perfil = asignacion.id_perfil.perfil

            with transaction.atomic():

                # Usuario
                usuario.nombres = nombres_actualizar
                usuario.apellidos = apellidos_actualizar
                usuario.genero = genero_actualizar
                usuario.cedula_identidad = cedula_identidad
                usuario.estado_civil = estado_civil_actualizar
                usuario.save()

                # Contacto
                contacto = usuario.contacto
                contacto.telefono_personal = telefono_personal
                contacto.telefono_suplete = telefono_secundario
                contacto.correo_electronico = correo_electronico
                contacto.correo_alternativo = correo_alternativo
                contacto.save()

                # Nacimiento
                nacimiento = usuario.nacimiento
                nacimiento.pais = paisnacimiento
                nacimiento.estado = estado
                nacimiento.municipio = municipio
                nacimiento.parroquia = parroquia
                nacimiento.direccion_nacimiento = direccionnacimiento
                nacimiento.fecha_nacimiento = fechanacimiento
                nacimiento.save()

                # Residencia
                residencia = usuario.residencia
                residencia.condicion_residencia = condicionresidencia
                residencia.municipio = municipioresidencia
                residencia.parroquia = parroquiaresidencia
                residencia.direccion_residencia = direcciondomicilio
                residencia.save()

                if perfil == "Estudiante":
                    if not tipos_secundaria or not nombre_liceo or not fecha_graduacion  or not codigo_opsu  or not nombres_representante or not apellidos_representante or not nacionalidad_representante or not ci_representante or not prefijo_num_representante or not telefono_representante or not parestenco:
                        return JsonResponse({
                            "estado": "fallo",
                            "icon": "warning",
                            "descripcion": "Los campos del estudiante esta vacio."
                        })
                    
                    # Información secundaria
                    secundaria = usuario.secundaria
                    secundaria.tipo_institucion = tipos_secundaria
                    secundaria.nombre_institucion = nombre_liceo
                    secundaria.fecha_grado = fecha_graduacion
                    secundaria.codigo_sni_opsu = codigo_opsu
                    secundaria.save()

                    if carnet_dispacidad and registro_medico and tipos_discapacidad and grado_discapacidad and causa_discapacidad:
                        carnet = carnet_dispacidad
                        registromedico = registro_medico
                        tipodiscapacidad = tipos_discapacidad
                        gradodiscapacidad = grado_discapacidad
                        causasdiscapacidad = causa_discapacidad
                    else:
                        carnet = "N/A"
                        registromedico = "N/A"
                        tipodiscapacidad = "N/A"
                        gradodiscapacidad = "N/A"
                        causasdiscapacidad = "N/A"

                    # Discapacidad
                    discapacidad = usuario.discapacidad
                    discapacidad.codigo_carnet_discapacidad = carnet
                    discapacidad.nro_registro_medico = registromedico
                    discapacidad.tipo_discapacidad = tipodiscapacidad
                    discapacidad.grado_discapacidad = gradodiscapacidad
                    discapacidad.causa_discapacidad = causasdiscapacidad
                    discapacidad.save()

                    # Representantes
                    representantes = usuario.padresEstudiante.all()

                    if representantes.exists():
                        representante = representantes.first()
                        representante.nombres = nombres_representante
                        representante.apellidos = apellidos_representante
                        representante.cedula_identidad = (
                            f"{nacionalidad_representante}-{ci_representante}"
                        )
                        representante.telefono = (
                            f"{prefijo_num_representante}{telefono_representante}"
                        )
                        representante.parentesco = parestenco
                        representante.save()

                    if representantes.count() > 1:
                        otro = representantes[1]
                        otro.nombres = nombres_otro_representante
                        otro.apellidos = apellidos_otro_representante
                        otro.cedula_identidad = (
                            f"{nacionalidad_otro_representante}-{ci_otro_representante}"
                        )
                        otro.telefono = (
                            f"{prefijo_num_otro_representante}{telefono_otro_representante}"
                        )
                        otro.parentesco = parestenco_otro_representante
                        otro.save()
                else:
                    if not profesion or not universidad or not paisprofesion:
                        return JsonResponse({
                            "estado": "fallo",
                            "icon": "warning",
                            "descripcion": "Los campos del usuario está vacio."
                        })
                    
                    profesional = usuario.profesional
                    profesional.profesion_pregrado = profesion
                    profesional.universidad_egreso_pregrado = universidad
                    profesional.pais_profesion_pregrado = paisprofesion
                    profesional.save()

            return JsonResponse({
                "estado": "success",
                "descripcion": "Las materias fueron asignadas correctamente al docente.",
                "icon": "success"
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío, por favor rellene los campos."
        })
    
    return render(request, "actualizar_datos_usuarios.html")

# MODULO TRAYECTO

def siguiente_trayecto(request):
    cantidad = TrayectoAcademico.objects.count()

    if cantidad == 0:
        return JsonResponse({
            "trayecto": "Inicial"
        })

    if cantidad - 1 >= len(ROMANOS):
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "descripcion": "Se alcanzó el número máximo de trayectos permitidos."
        })

    return JsonResponse({
        "trayecto": f"TRAYECTO {ROMANOS[cantidad - 1]}"
    })

def trayectos_registrados(request):
    trayectos = TrayectoAcademico.objects.all().order_by("id_trayecto")

    datos = []

    for trayecto in trayectos:
        datos.append({
            "id_trayecto": trayecto.id_trayecto,
            "trayecto": trayecto.trayecto,
        })

    return JsonResponse({
        "trayectos": datos
    })

def modulo_trayecto(request):
    if request.method == "POST":
        trayecto = request.POST.get("trayecto")

        if not trayecto:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Debe indicar el trayecto."
            })

        if TrayectoAcademico.objects.filter(trayecto=trayecto).exists():
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "El trayecto ya se encuentra registrado."
            })

        TrayectoAcademico.objects.create(trayecto=trayecto)

        return JsonResponse({
            "success": True,
            "icon": "success",
            "descripcion": "Trayecto registrado correctamente."
        })

    return render(request, "trayecto.html")

# MODULO AULAS ACADÉMICAS

def aulas_registrados(request):
    if request.method == "POST":
        id_nucleo = request.POST.get("id_nucleo")

        aulas = AulaAcademica.objects.filter(
            id_nucleo=id_nucleo
        ).values(
            "id_aula",
            "nombre_aula",
            "nombre_edificio",
            "piso_edificio"
        )

        return JsonResponse({
            "success": True,
            "aulas": list(aulas)
        })

def aulas_almacenadas(request):
    aulas_queryset = AulaAcademica.objects.all().select_related("id_nucleo").values(
        "id_aula",
        "nombre_aula",
        "nombre_edificio",
        "piso_edificio",
        "id_nucleo__municipio"
    )

    aulas_agrupadas = defaultdict(list)
    for aula in aulas_queryset:
        municipio = aula["id_nucleo__municipio"] or "Sin Municipio"
        aulas_agrupadas[municipio].append({
            "id_aula": aula["id_aula"],
            "nombre_aula": aula["nombre_aula"],
            "nombre_edificio": aula["nombre_edificio"],
            "piso_edificio": aula["piso_edificio"],
            "id_nucleo": municipio 
        })

    return JsonResponse(dict(aulas_agrupadas), safe=True)


def datos_aula(request):
    if request.method == "POST":
        id_aula = request.POST.get("id_aula")

        aula = AulaAcademica.objects.select_related("id_nucleo").get(id_aula=id_aula)

        return JsonResponse({
            "estado": "ok",
            "id_aula": aula.id_aula,
            "nombre_aula": aula.nombre_aula,
            "nombre_edificio": aula.nombre_edificio,
            "piso_edificio": aula.piso_edificio,
            "id_nucleo": aula.id_nucleo.id_nucleo,
            "municipio": aula.id_nucleo.municipio
        })
    
def actualizar_aula_academica(request):
    if request.method == "POST":
        aula_seleccionado = request.POST.get("aulaseleccionar")
        nombre_aula = request.POST.get("actualizar_aula")
        edificio = request.POST.get("actualizar_edificio")
        piso = request.POST.get("actualizar_piso")
        id_nucleo = request.POST.get("actualizar_nucleo")

        if nombre_aula and edificio and piso and id_nucleo:

            nucleo = Nucleos.objects.get(id_nucleo=id_nucleo)
            aula = AulaAcademica.objects.get(id_aula=aula_seleccionado)

            aula.nombre_aula = nombre_aula
            aula.nombre_edificio = edificio
            aula.piso_edificio = piso
            aula.id_nucleo = nucleo

            aula.save()

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "El aula se actualizó exitosamente."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })
    
def modulo_aula_academica(request):
    if request.method == "POST":
        aula = request.POST.get("registrar_aula")
        edificio = request.POST.get("registrar_edificio")
        piso = request.POST.get("registrar_piso")
        id_nucleo = request.POST.get("registrar_nucleo")

        if aula and edificio and piso and id_nucleo:
            existe = AulaAcademica.objects.filter(nombre_aula__iexact=aula).exists()
            if existe:
                return JsonResponse({
                    "estado": "fallo",
                    "icon": "error",
                    "descripcion": "Ya existe una aula registrada con el mismo nombre."
                })
            
            nucleo = Nucleos.objects.get(id_nucleo=id_nucleo)

            AulaAcademica.objects.create(nombre_aula=aula, nombre_edificio=edificio, piso_edificio=piso, id_nucleo=nucleo)
            
            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Se registro exitosamente el aula académica."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })

    return render(request, "aulas_academicas.html")

# HORARIO ACADÉMICO

def buscar_materias_docente(request):
    if request.method == "POST":
        nucleo = request.POST.get("nucleos")
        pnf = request.POST.get("pnfs")
        trayecto = request.POST.get("trayecto")

        materias = (
            MateriaAsignada.objects
            .select_related(
                "id_materia",
                "id_asignacion__id_usuario"
            )
            .filter(
                id_materia__id_pnf_id=pnf,
                id_materia__id_trayecto_id=trayecto,
                id_asignacion__id_nucleo_id=nucleo
            )
        )

        datos = []
        for materia in materias:
            docente = materia.id_asignacion.id_usuario

            datos.append({
                "id_materia": materia.id_materia.id_materia,
                "materia": materia.id_materia.nombre,
                "docente": f"{docente.nombres} {docente.apellidos}",
            })

        return JsonResponse({
            "success": True,
            "materias": datos
        })

def modulo_horario_academico(request):
    if request.method == "POST":
        nucleo = request.POST.get("nucleos")
        pnf = request.POST.get("pnfs")
        trayecto = request.POST.get("trayecto")
        periodo = request.POST.get("periodo")
        aula = request.POST.get("aulas")
        turno = request.POST.get("turno")

        if nucleo and pnf and trayecto and periodo and aula and turno:
            
            idnucleo = Nucleos.objects.get(id_nucleo=nucleo)
            idpnf = Pnf.objects.get(id_pnf=pnf)
            idtrayecto = TrayectoAcademico.objects.get(id_trayecto=trayecto)
            idperiodo = PeriodoAcademico.objects.get(id_periodo_academico=periodo)
            idaula = AulaAcademica.objects.get(id_aula=aula)

            HorarioAcademica.objects.create(id_nucleo=idnucleo, id_pnf=idpnf, id_trayecto=idtrayecto, id_periodo_academico=idperiodo, id_aula=idaula, turno_academico=turno, activo=1)

            return JsonResponse({
                "estado": "ok",
                "icon": "success",
                "descripcion": "Se registro exitosamente el aula académica."
            })

        return JsonResponse({
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se encuentra vacío al menos un campo."
        })
    
    return render(request, "horario_academico.html")

def limpiar_nombre(nombre):
    nombre = nombre.strip()
    return re.sub(r'[\\/:*?"<>|]', "_", nombre)

def generar_horario_pdf(request):
    if request.method != "POST":
        return JsonResponse({
            "estado": "error",
            "descripcion": "Método no permitido."
        })
    try:
        json_data = json.loads(request.body)

        nucleo = json_data.get("nucleos")
        pnf = json_data.get("pnfs")
        trayecto = json_data.get("trayecto")
        periodo = json_data.get("periodo")
        aula = json_data.get("aulas")
        turno = json_data.get("turno")
        horario = json_data.get("horario", [])

        if not all([ nucleo, pnf, trayecto, periodo, aula, turno]):
            return JsonResponse({
                "estado": "error",
                "descripcion": "Faltan datos para generar el horario."
            })

        idnucleo = get_object_or_404(Nucleos, id_nucleo=nucleo)

        idpnf = get_object_or_404(Pnf, id_pnf=pnf)

        idtrayecto = get_object_or_404(TrayectoAcademico, id_trayecto=trayecto)

        idperiodo = get_object_or_404(PeriodoAcademico, id_periodo_academico=periodo)

        idaula = get_object_or_404(AulaAcademica, id_aula=aula)

        ruta = (
            Path(settings.MEDIA_ROOT)
            / "Horarios Academicos"
            / limpiar_nombre(idnucleo.municipio)
            / limpiar_nombre(idpnf.pnf)
            / limpiar_nombre(idtrayecto.trayecto)
        )

        ruta.mkdir(
            parents=True,
            exist_ok=True
        )

        fecha = datetime.now().strftime("%d-%m-%Y")
        nombre_pdf = limpiar_nombre(
            f"{fecha} - "
            f"{idperiodo.nombre} - "
            f"{idtrayecto.trayecto} - "
            f"{idpnf.pnf}.pdf"
        )

        archivo_pdf = ruta / nombre_pdf
        estilos = getSampleStyleSheet()

        titulo = ParagraphStyle(
            "Titulo",
            parent=estilos["Heading1"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=18,
            spaceAfter=10
        )

        subtitulo = ParagraphStyle(
            "Subtitulo",
            parent=estilos["Heading2"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=13,
            spaceAfter=15
        )

        informacion = ParagraphStyle(
            "Informacion",
            parent=estilos["BodyText"],
            alignment=TA_LEFT,
            fontName="Helvetica",
            fontSize=10,
            leading=18
        )

        doc = SimpleDocTemplate(
            str(archivo_pdf),
            pagesize=landscape(letter),
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm
        )

        elementos = []
        elementos.append(
            Paragraph(
                "UNIVERSIDAD POLITÉCNICA TERRITORIAL DEL ESTADO BARINAS JOSÉ FÉLIX RIBAS",
                titulo
            )
        )

        elementos.append(
            Paragraph(
                "HORARIO ACADÉMICO",
                subtitulo
            )
        )

        elementos.append(
            Spacer(1, 0.4 * cm)
        )

        texto = f"""
            <b>Núcleo:</b> {idnucleo.municipio}<br/>
            <b>Programa Nacional de Formación:</b> {idpnf.pnf}<br/>
            <b>Trayecto:</b> {idtrayecto.trayecto}<br/>
            <b>Periodo Académico:</b> {idperiodo.nombre}<br/>
            <b>Aula:</b> {idaula.nombre_aula}<br/>
            <b>Edificio:</b> {idaula.nombre_edificio}<br/>
            <b>Piso:</b> {idaula.piso_edificio}<br/>
            <b>Turno:</b> {turno}<br/>
            <b>Fecha de emisión:</b> {fecha}
        """
        elementos.append(
            Paragraph(
                texto,
                informacion
            )
        )

        elementos.append(
            Spacer(1, 0.7 * cm)
        )

        datos_tabla = [
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

        for fila in horario:
            lunes = obtener_materia_docente(
                fila.get("lunes")
            )
            martes = obtener_materia_docente(
                fila.get("martes")
            )
            miercoles = obtener_materia_docente(
                fila.get("miercoles")
            )
            jueves = obtener_materia_docente(
                fila.get("jueves")
            )
            viernes = obtener_materia_docente(
                fila.get("viernes")
            )

            # AHORA ESTÁ DENTRO DEL BUCLE FOR
            datos_tabla.append([
                fila.get("hora_inicio", ""),
                fila.get("hora_final", ""),
                Paragraph(
                    lunes.replace("\n", "<br/>"),
                    informacion
                ),
                Paragraph(
                    martes.replace("\n", "<br/>"),
                    informacion
                ),
                Paragraph(
                    miercoles.replace("\n", "<br/>"),
                    informacion
                ),
                Paragraph(
                    jueves.replace("\n", "<br/>"),
                    informacion
                ),
                Paragraph(
                    viernes.replace("\n", "<br/>"),
                    informacion
                )
            ])

        # Definir anchos aproximados en centímetros (el total disponible es ~25.9 cm)
        anchos_columnas = [2.0 * cm, 2.0 * cm, 4.3 * cm, 4.3 * cm, 4.3 * cm, 4.3 * cm, 4.3 * cm]

        tabla = Table(
            datos_tabla,
            colWidths=anchos_columnas,
            repeatRows=1
        )
        tabla.setStyle(
            TableStyle([(
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    colors.HexColor("#0D6EFD")
                ),
                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,0),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0,0),
                    (-1,-1),
                    9
                ),

                (
                    "ALIGN",
                    (0,0),
                    (-1,-1),
                    "CENTER"
                ),

                (
                    "VALIGN",
                    (0,0),
                    (-1,-1),
                    "MIDDLE"
                ),

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.black
                ),
                (
                    "ROWBACKGROUNDS",
                    (0,1),
                    (-1,-1),
                    [
                        colors.white,
                        colors.HexColor("#F5F5F5")
                    ]
                )
            ])
        )

        elementos.append(tabla)
        doc.build(elementos)

        archivo = open(
            archivo_pdf,
            "rb"
        )

        return FileResponse(
            archivo,
            as_attachment=True,
            filename=nombre_pdf
        )

    except Exception as e:
        return JsonResponse({
            "estado": "error",
            "descripcion": str(e)
        })

def obtener_materia_docente(id_materia):
    if not id_materia:
        return ""

    asignacion = (
        MateriaAsignada.objects
        .filter(id_materia=id_materia)
        .select_related(
            "id_materia",
            "id_asignacion__id_usuario"
        )
        .first()
    )

    if asignacion:
        materia = asignacion.id_materia.nombre

        docente = (asignacion.id_asignacion.id_usuario.nombres
            + " "
            + asignacion.id_asignacion.id_usuario.apellidos
        )

        return (
            f"{materia}\n"
            f"{docente}"
        )

    return ""
    
"""FORO"""
def foro(request):
    return render(request, 'Foro/foro.html')

def Historia(request):
    return render(request, 'Foro/Historia.html')

def mision_vision(request):
    return render(request, 'Foro/mision_vision.html')

def psc(request):
    return render(request, 'Foro/psc.html')

def pst(request):
    return render(request, 'Foro/pst.html')

def trayectoria(request):
    return render(request, 'Foro/trayectoria.html')

def carreras_impartidas(request):
    return render(request, 'Foro/carreras_impartidas.html')

def Planificacion_Docente(request):
    return render(request, 'Foro/Planificacion_Docente.html')

def barra_lateral(request):
    return render(request, 'Estructura/Barra_Lateral.html')