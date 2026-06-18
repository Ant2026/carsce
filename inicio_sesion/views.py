from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction

from .models import Usuario, Perfiles, Nucleos, Pnf, Contacto, VerificacionCodigo, PNFNucleo,  GacetaOficial, UsuarioAsignacion, Nacimiento, Residencia, DatosPreofesion, Discapacidad, InformacionSecundaria, DocumentosEstudiante, PadresEstudiante, EstatusEstudiante

import secrets, string, json, uuid
from math import ceil
from datetime import timedelta

# Create your views here.
def foro(request):

    if request.method == "POST":
        nucleo = request.POST.get("nucleos_seleccionado")

        if not nucleo:
            return JsonResponse({
                "icon": "warning",
                "descripcion": "Debe seleccionar un núcleo."
            })

        request.session["nucleo_seleccionado"] = nucleo

        return JsonResponse({
            "icon": "success",
            "descripcion": "Núcleo registrado correctamente."
        })

    return render(
        request,
        "Foro/foro.html",
        {
            "mostrar_dialogo": not request.session.get("nucleo_seleccionado"),
            "nucleo_seleccionado": request.session.get("nucleo_seleccionado")
        }
    )

def inicio_sesion(request):
    if request.method == "POST":
        nombre_usuario = request.POST.get("usuario")
        contrasenia = request.POST.get("contrasenia")

        if nombre_usuario and contrasenia:
            usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)

            if usuario:
                if check_password(contrasenia, usuario.clave):
                    nombre_completo = usuario.nombres + " " + usuario.apellidos

                    perfiles = Perfiles.objects.filter(usuarioasignacion__id_usuario=usuario)

                    lista_perfiles = list(perfiles.values_list('perfil', flat=True))

                    request.session['cedula_usuario'] = usuario.cedula_identidad
                    request.session['usuario_nombre'] = nombre_completo
                    request.session['perfiles'] = lista_perfiles

                    existe = Nacimiento.objects.filter(id_usuario=usuario).exists()

                    if existe:
                        url = "/panel_usuario/"
                    else:
                        if "Estudiante" in lista_perfiles:
                            url = "/completar_registro_estudiante/"
                        else:
                            url = "/completar_registro_personal/"

                    return JsonResponse({
                        "success": True,
                        "url": url
                    })
                else:
                    return JsonResponse({
                        "success": False,
                        "icon": "error",
                        "descripcion": "Contraseña incorrecta"
                    })
            else:
                return JsonResponse({
                    "success": False,
                    "icon": "error",
                    "descripcion": "El usuario no se encuentra registrado"
                })
        else:
            return JsonResponse({
                "success": False,
                "icon": "warning",
                "descripcion": "Debe completar todos los campos"
            })
    return render(request, 'inicio_sesion.html')

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
        
    return render(request, 'buscar_usuario.html')

def comprobar_usuario(request):
    if not request.session.get("flujo_verificacion"):
        return redirect("buscar_usuario")

    usuario = Usuario.objects.filter(cedula_identidad=request.session.get("CI_usuario")).first()

    if not usuario:
        return redirect("buscar_usuario")

    contacto = Contacto.objects.filter(id_usuario_id=usuario.id_usuario).first()

    verificacion = VerificacionCodigo.objects.filter(
                                            cedula_identidad=usuario.cedula_identidad,
                                            token=request.session.get("token_recuperacion")).first()

    if not verificacion:
        enviar_codigo_verificacion(
            usuario.nombres,
            usuario.apellidos,
            contacto.correo_electronico,
            usuario.cedula_identidad,
            request.session["token_recuperacion"])
        
        verificacion = VerificacionCodigo.objects.filter(cedula_identidad=usuario.cedula_identidad).first()

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        codigo_ingresado = request.POST.get("codigo")

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
            request.session["token_recuperacion"])

        datos = json.loads(respuesta.content)
        request.session["correo_verificado"] = True
        
        if datos.get("estado") == "exito":    
            verificacion.intentos = 0
            verificacion.bloqueado_hasta = None
            verificacion.activo = 0
            verificacion.save()

        return respuesta

    fecha_expiracion_ts = int(verificacion.fecha_expiracion.timestamp())

    return render(request, "comprobar_usuario.html", {
        "fecha_expiracion": fecha_expiracion_ts
    })

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
    verificacion = VerificacionCodigo.objects.filter(cedula_identidad=cedula_identidad,
                                                     token=token).first()

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
    else:
        verificacion = VerificacionCodigo.objects.create(
            cedula_identidad=cedula_identidad,
            codigo=codigo_generado,
            creado=timezone.now(),
            intentos=0,
            activo=1,
            fecha_expiracion=fecha_expiracion,
            bloqueado_hasta=None,
            descripcion=f"Código de verificación para recuperación de credenciales al usuario {nombres_usuario} {apellidos_usuario}"
        )

    send_mail(
        subject="Código de verificación",
        message=f"Tu código es: {codigo_generado}",
        from_email="ejemplo@gmail.com",
        recipient_list=[correo_electronico],
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

    send_mail(
        subject="Código de verificación",
        message=f"Tu código es: {codigo_generado}",
        from_email="ejemplo@gmail.com",
        recipient_list=[correo_electronico],
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

        usuario.clave = password
        usuario.save()

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

    return render(request, "recuperar_contrasenia.html")

def recuperar_usuario(request):
    if not request.session.get("flujo_verificacion"):
        return redirect("buscar_usuario")
    
    if not request.session.get("correo_verificado"):
        return redirect("comprobar_usuario")

    token = request.session.get("token_recuperacion")

    verificacion = VerificacionCodigo.objects.filter(token=token, activo=0).first()
    if not verificacion:
        return redirect("buscar_usuario")

    usuario = Usuario.objects.filter(cedula_identidad=request.session.get("CI_usuario")).first()

    if not usuario: 
        return redirect("buscar_usuario")

    contacto = Contacto.objects.filter(id_usuario_id=usuario.id_usuario).first()

    correo = contacto.correo_electronico

    verificacion = VerificacionCodigo.objects.filter(cedula_identidad=request.session["CI_usuario"]).first()

    if verificacion:
        verificacion.token = ""
        verificacion.save()

    del request.session["correo_verificado"]
    del request.session["CI_usuario"]
    del request.session["token_recuperacion"]

    send_mail(
        subject="Recuperación de usuario",
        message=f"Su nombre de usuario es: {usuario.nombre_usuario}",
        from_email="ejemplo@gmail.com",
        recipient_list=[correo],
    )

    return render(request, 'recuperar_usuario.html', {
        "usuario_enviado": True
    })

# Esto son los modulos para registrar credenciales por parte del personal y
# pre-inscripción para los estudiantes

def panel_registro(request):
    return render(request, 'panel_registro.html')

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

            # Verificar si ya tiene credenciales
            if usuario.nombre_usuario and usuario.clave:
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

    return render(request, "confirmar_registro_personal.html")

def guardar_credenciales_personal(request):
    if request.method == "POST":

        cedula_identidad = request.session.get('cedula_personal')

        nombre_usuario = request.POST.get("nombre_usuario")
        password = request.POST.get("password_usuario")
        print(nombre_usuario)
        print(password)
        if nombre_usuario and password:
            usuario = Usuario.objects.get(cedula_identidad=cedula_identidad)

            usuario.nombre_usuario = nombre_usuario
            usuario.clave = make_password(password)
            usuario.save()
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

def pre_inscripcion(request):
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
            verificar_usuario = Usuario.objects.filter(nombre_usuario=usuario).first()
            verificar_correo = Contacto.objects.filter(correo_electronico=correo_electronico).exists()

            if verificar_cedula:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe una cédula registrada"
                })

            if verificar_correo:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe un correo registrado"
                })

            if verificar_usuario:
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe el usuario registrado"
                })
            
            nuevo_usuario = Usuario.objects.create(
                            nombres=nombres,
                            apellidos=apellidos,
                            cedula_identidad=cedula_identidad,
                            nombre_usuario=usuario,
                            clave=make_password(password))

            Contacto.objects.create(
                telefono_personal=telefono,
                correo_electronico=correo_electronico,
                id_usuario=nuevo_usuario)

            perfil = Perfiles.objects.get(pk=5)

            UsuarioAsignacion.objects.create(
                id_usuario=nuevo_usuario,
                id_perfil=perfil
            )

            return JsonResponse({
                "icon": "success",
                "descripcion": "Se registró correctamente"
            })

        return JsonResponse({
            "icon": "warning",
            "descripcion": "Complete todos los campos"
        })

    return render(request, "pre_inscripcion.html")

# Esto son los modulos para realizar el pre registro por parte del Director General

def panel_usuario(request):
    return render(request, 'panel_usuario.html')

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

            perfil = Perfiles.objects.get(
                pk=perfil_id
            )

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

            return JsonResponse({
                "nucleos": resultado
            })

        except Exception as e:
            return JsonResponse({
                "error": str(e)
            }, status=500)

def pnfs_nucleos(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nucleo_id = data.get("id_nucleo")

            if not nucleo_id:
                return JsonResponse({"error": "Datos incompletos"}, status=400)

            pnfs_ocupados = UsuarioAsignacion.objects.filter(
                id_perfil__perfil="Coordinador de PNF",
                id_nucleo_id=nucleo_id
            ).values_list("id_pnf_id", flat=True)

            pnfs = PNFNucleo.objects.filter(id_nucleo=nucleo_id).exclude(id_pnf_id__in=pnfs_ocupados).select_related("id_pnf")

            resultado = [ {
                    "id_pnf": item.id_pnf.id_pnf,
                    "pnf": item.id_pnf.pnf
                }
                for item in pnfs
            ]

            return JsonResponse({"pnfs": resultado})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)

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

        print("Perfiles:", perfiles_asignados)

        print("Núcleos Control:", nucleos_control)
        print("Núcleos Coordinador:", nucleos_coordinador)
        print("Núcleos Docente:", nucleos_docente)

        print("PNF Coordinador:", pnfs_coordinador)
        print("PNF Docente:", pnfs_docente)

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

# Formulario Completo del Personal

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

            if ci_representante_principal == request.session.get("cedula_usuario"):
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "La cedula de identidad del Representante es identica de la cedula de identidad del estudiante, por favor ingrese la cedula correspondiente del representante."
                })

            if Contacto.objects.filter(
                correo_alternativo=correo_alternativo
            ).exclude(id_usuario=usuario).exists():
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "Este correo ya está registrado en otro usuario"
                })
                            
            if PadresEstudiante.objects.filter(
                cedula_identidad=ci_representante_principal
            ).exclude(id_usuario=usuario).exists():
                return JsonResponse({
                    "titulo": "¡Advertencia!",
                    "estado": "fallo",
                    "icon": "warning",
                    "descripcion": "La cédula del representante ya está registrada"
                })

            if PadresEstudiante.objects.filter(
                cedula_identidad=ci_otrorepresentante
            ).exclude(id_usuario=usuario).exists():
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

            usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()
            usuario.genero = genero
            usuario.estado_civil = estado_civil
            usuario.save()

            contacto = Contacto.objects.filter(id_usuario=usuario).first()
            contacto.telefono_suplete = telefono_sucundario
            contacto.correo_alternativo = correo_alternativo
            contacto.save()

            PadresEstudiante.objects.create(nombres=nombres_representante, apellidos=apellidos_representante, cedula_identidad=ci_representante_principal, telefono=tlf_representante_principal, parentesco=parestencorepresentante, id_usuario=usuario)

            if nombres_otrorepresentante and apellidos_otrorepresentante and nacionalidad_otrorepresentante and ci_otrorepresentante and prefijo_num3 and telefono_otrorepresentante and parestencootrorepresentante:
                
                ci_otrorepresentante = nacionalidad_otrorepresentante + "-" + ci_otrorepresentante
                tlf_representante_principal = prefijo_num3 + telefono_otrorepresentante
                
                PadresEstudiante.objects.create(nombres=nombres_otrorepresentante, apellidos=apellidos_otrorepresentante, cedula_identidad=ci_otrorepresentante, telefono=telefono_otrorepresentante, parentesco=parestencootrorepresentante, id_usuario=usuario)

            Nacimiento.objects.create(pais=pais_nacimiento, estado=estado_nacimiento, municipio=municipio_nacimiento, parroquia=parroquia_nacimiento, direccion_nacimiento=direccion_nacimiento, fecha_nacimiento=fecha_nacimiento, id_usuario=usuario)

            Residencia.objects.create(condicion_residencia=condicion_residencia, municipio=municipio_residencia, parroquia=parroquia_residencia, direccion_residencia=direccion_domicilio, id_usuario=usuario)

            InformacionSecundaria.objects.create(tipo_institucion=tipos_secundaria, nombre_institucion=nombre_secundaria, fecha_grado=fecha_graduacion, codigo_sni_opsu=codigo_opsu, id_usuario=usuario)

            Discapacidad.objects.create(codigo_carnet_discapacidad=carnet_dispacidad, nro_registro_medico=registro_medico, tipo_discapacidad=tipo_discapacidad, grado_discapacidad=grado_discapacidad, causa_discapacidad=causa_discapacidad, id_usuario=usuario)

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
    nucleo_seleccionado = request.session.get("nucleo_seleccionado")
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

def registrar_pnfs_cursar(request):
    if request.method == "POST":
        pnfs_seleccionado = request.POST.getlist("pnfs")
        nucleo_seleccionado = request.session.get("nucleo_seleccionado")
        cedula_identidad = request.session.get("cedula_usuario")

        if pnfs_seleccionado:
            usuario = Usuario.objects.filter(cedula_identidad=cedula_identidad).first()
            nucleo = Nucleos.objects.filter(municipio=nucleo_seleccionado).first()

            asignacion_base = UsuarioAsignacion.objects.filter(id_usuario=usuario).first()
            primer_pnf = Pnf.objects.filter(id_pnf=pnfs_seleccionado[0]).first()

            asignacion_base.id_nucleo = nucleo
            asignacion_base.id_pnf = primer_pnf
            asignacion_base.save()

            for pnf_id in pnfs_seleccionado[1:]:
                pnf = Pnf.objects.filter(id_pnf=pnf_id).first()

                UsuarioAsignacion.objects.create(
                    id_usuario=usuario,
                    id_perfil=usuario.id_perfil,
                    id_nucleo=nucleo,
                    id_pnf=pnf
                )
            
            return JsonResponse({
                "estado": "success"
            })

        return JsonResponse({
            "titulo": "¡Advertencia!",
            "estado": "fallo",
            "icon": "warning",
            "descripcion": "Se ha detectado uno o algunos campos vacios, por favor llene todos los campos."
        })
    
    return render(request, 'registro_pnf_estudiante.html')

def registro_documento(request):
    if request.method == "POST":
        usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()

        if not usuario:
            return JsonResponse({
                "icon": "error",
                "descripcion": "Usuario no encontrado"
            })

        documentos = {
            "Cédula de Identidad": request.FILES.get("CI_estudiante"),
            "Título de Bachiller": request.FILES.get("TBachiller_estudiante"),
            "Sabana de Notas": request.FILES.get("SNotas_estudiante"),
            "OPSU": request.FILES.get("OPSU_estudiante"),
        }

        for nombre, archivo in documentos.items():
            if archivo:
                DocumentosEstudiante.objects.update_or_create(
                    id_usuario=usuario,
                    nombre_documento=nombre,
                    defaults={
                        "archivo": archivo
                    }
                )

        return JsonResponse({
            "estado": "success",
            "titulo": "Éxito",
            "descripcion": "Documentos registrados correctamente",
            "icon": "success"
        })

    return render(request, "registro_documento.html")

# Formulario Completo de los Estudiantes

def obtener_pre_inscripto(request):
    usuario = Usuario.objects.filter(
        cedula_identidad=request.session.get("cedula_usuario")
    ).first()

    if not usuario:
        return JsonResponse({
            "titulo": "¡Error!",
            "estado": "fallo",
            "icon": "error",
            "descripcion": "Usuario no encontrado."
        })

    asignacion = UsuarioAsignacion.objects.select_related(
        'id_pnf',
        'id_nucleo'
    ).filter(
        id_usuario=usuario
    ).first()

    if asignacion:
        estudiante_pre_inscrito = UsuarioAsignacion.objects.filter(
            id_perfil_id=5,
            id_pnf=asignacion.id_pnf,
            id_nucleo=asignacion.id_nucleo
        ).first()

        if estudiante_pre_inscrito:
            usuario_pre_inscrito = Usuario.objects.filter(
                pk=estudiante_pre_inscrito.id_usuario_id
            ).first()

            if usuario_pre_inscrito:
                return JsonResponse({
                    "nombres": usuario_pre_inscrito.nombres,
                    "apellidos": usuario_pre_inscrito.apellidos,
                    "cedula": usuario_pre_inscrito.cedula_identidad,
                    "estado": "exito"
                })

            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "No existe un usuario con perfil de estudiante preinscrito para el núcleo y PNF seleccionados."
            })

    return JsonResponse({
        "titulo": "¡Advertencia!",
        "estado": "fallo",
        "icon": "warning",
        "descripcion": "No hay estudiantes preinscritos registrados en este núcleo y PNF."
    })

def inscripcion_estudiante(request):
    if request.method == "POST":

        id_usuario = request.POST.get("id_usuario")

        usuario = Usuario.objects.filter(
            id_usuario=id_usuario
        ).first()

        if not usuario:
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "El estudiante no existe."
            })

        if EstatusEstudiante.objects.filter(id_usuario=usuario).exists():
            return JsonResponse({
                "titulo": "¡Advertencia!",
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "El estudiante ya se encuentra inscrito."
            })

        EstatusEstudiante.objects.create(
            estatus="Regular",
            estado="Activo",
            ingreso="Nuevo Ingreso",
            descripcion_ingreso="Preinscrito",
            trayecto="Trayecto Inicial",
            fecha_ingreso=timezone.now().date(),
            id_usuario=usuario
        )

        return JsonResponse({
            "titulo": "¡Éxito!",
            "estado": "exito",
            "icon": "success",
            "descripcion": "El estudiante fue inscrito correctamente."
        })
    
    return render(request, "inscripcion_estudiante.html")

"""FORO"""

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