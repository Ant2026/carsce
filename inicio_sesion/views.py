from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction

from .models import Usuario, Perfiles, Nucleos, Pnf, Contacto, VerificacionCodigo, PNFNucleo, GacetaOficial, UsuarioAsignacion

import secrets, string
from math import ceil
from datetime import timedelta
import json
import uuid

# Create your views here.
def foro(request):
    return render(request, 'Foro/foro.html')

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

                    request.session['usuario_nombre'] = nombre_completo
                    request.session['perfiles'] = lista_perfiles

                    return JsonResponse({
                        "success": True,
                        "redirect_url": reverse("panel_usuario")
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
def completar_registro_personal(request):
    return render(request, "completar_registro_personal.html")


# Formulario Completo de los Estudiantes

def inscripcion_estudiante(request):
    return render(request, 'inscripcion_estudiante.html')

def panel_registro(request):
    return render(request, 'panel_registro.html')

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