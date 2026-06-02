from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone

from .models import Usuario, Perfiles, Nucleos, Pnf, Contacto, VerificacionCodigo, PNFNucleo, GacetaOficial, UsuarioPerfil, PerfilesPnf, UsuarioNucleo

import secrets, string
from math import ceil
from datetime import timedelta
import json

# Create your views here.

def foro(request):
    return render(request, 'foro.html')

def inicio_sesion(request):

    if request.method == "POST":
        nombre_usuario = request.POST.get("usuario")
        contrasenia = request.POST.get("contrasenia")

        if nombre_usuario and contrasenia:

            try:
                usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)

                if check_password(contrasenia, usuario.clave):
                    nombre_completo = usuario.nombres + " " + usuario.apellidos

                    perfiles = Perfiles.objects.filter(usuarioperfil__id_usuario=usuario)

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

            except Usuario.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "icon": "error",
                    "descripcion": "El usuario no existe"
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
    if not request.session.get('flujo_verificacion'):
        return redirect("buscar_usuario")

    usuario = Usuario.objects.filter(cedula_identidad=request.session.get("CI_usuario")).first()
    contacto = Contacto.objects.filter(id_usuario_id=usuario.id_usuario).first()
    verificacion = VerificacionCodigo.objects.filter(cedula_identidad=request.session.get("CI_usuario")).first()

    if not verificacion:
        enviar_codigo_verificacion(
            usuario.nombres,
            usuario.apellidos,
            contacto.correo_electronico,
            usuario.cedula_identidad)

    if request.method == "POST":
        codigo_ingresado = request.POST.get("codigo")

        if not codigo_ingresado:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Debe ingresar el código de verificación"
            })

        respuesta = validar_codigo(
                        codigo_ingresado,
                        usuario.cedula_identidad,
                        usuario.nombres,
                        usuario.apellidos,
                        contacto.correo_electronico
                    )

        datos = json.loads(respuesta.content)

        if datos.get("estado") == "exito":
            request.session["correo_verificado"] = True

        return respuesta
    
    return render(request, "comprobar_usuario.html")

def validar_codigo(codigo, cedula_identidad, nombres, apellidos, correo_electronico):

    verificacion = VerificacionCodigo.objects.filter(
        cedula_identidad=cedula_identidad
    ).first()

    if not verificacion:
        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "descripcion": "No existe un código de verificación"
        })

    if (verificacion.bloqueado_hasta and timezone.now() < verificacion.bloqueado_hasta):
        tiempo_restante = verificacion.bloqueado_hasta - timezone.now()
        minutos_restantes = ceil(tiempo_restante.total_seconds() / 60)

        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "descripcion": f"Demasiados intentos. Intente nuevamente en {minutos_restantes} minuto(s)"
        })

    if timezone.now() > verificacion.fecha_expiracion:
        reenviar_codigo(nombres, apellidos, correo_electronico, cedula_identidad)

        return JsonResponse({
            "estado": "expirado",
            "icon": "warning",
            "descripcion": "El código expiró. Se envió uno nuevo a su correo"
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

    contacto = Contacto.objects.filter(
        id_usuario_id=usuario.id_usuario
    ).first()

    verificacion = VerificacionCodigo.objects.filter(
        cedula_identidad=usuario.cedula_identidad
    ).first()

    if (
        verificacion and
        verificacion.bloqueado_hasta and
        timezone.now() < verificacion.bloqueado_hasta
    ):

        tiempo_restante = (
            verificacion.bloqueado_hasta - timezone.now()
        )

        minutos_restantes = ceil(
            tiempo_restante.total_seconds() / 60
        )

        return JsonResponse({
            "estado": "fallo",
            "icon": "error",
            "descripcion": f"Demasiados intentos. Intente nuevamente en {minutos_restantes} minuto(s)"
        })

    return reenviar_codigo(
        usuario.nombres,
        usuario.apellidos,
        contacto.correo_electronico,
        usuario.cedula_identidad
    )

def reenviar_codigo(nombres_usuario, apellidos_usuario, correo_electronico, cedula_identidad):

    verificacion = VerificacionCodigo.objects.filter(
        cedula_identidad=cedula_identidad
    ).first()

    # Bloqueo activo
    if (
        verificacion and
        verificacion.bloqueado_hasta and
        timezone.now() < verificacion.bloqueado_hasta
    ):
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

    fecha_expiracion = timezone.now() + timedelta(minutes=15)

    if verificacion:

        verificacion.codigo = codigo_generado
        verificacion.fecha_expiracion = fecha_expiracion
        verificacion.activo = 1
        verificacion.intentos += 1

        if verificacion.intentos >= 3:
            verificacion.intentos = 0
            verificacion.bloqueado_hasta = None

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

def enviar_codigo_verificacion(nombres_usuario, apellidos_usuario, correo_electronico, cedula_identidad):
    
    codigo_generado = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    fecha_expiracion = timezone.now() + timedelta(minutes=15)

    VerificacionCodigo.objects.create(
        cedula_identidad=cedula_identidad,
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
    if not request.session['correo_verificado']:
        return redirect("buscar_usuario")
    
    return render(request, 'panel_recuperar_credenciales.html')

def recuperar_contrasenia(request):

    if not request.session.get("correo_verificado"):
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

        usuario = Usuario.objects.filter(
            cedula_identidad=request.session.get("CI_usuario")
        ).first()

        if not usuario:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "Usuario no encontrado"
            })

        usuario.clave = password
        usuario.save()

        request.session.pop("correo_verificado", None)

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "descripcion": "Contraseña actualizada correctamente"
        })

    return render(request, "recuperar_contrasenia.html")

def recuperar_usuario(request):

    if not request.session.get('correo_verificado'):
        return redirect("buscar_usuario")

    usuario = Usuario.objects.filter(
        cedula_identidad=request.session.get("CI_usuario")
    ).first()

    if not usuario:
        return redirect("buscar_usuario")

    contacto = Contacto.objects.filter(
        id_usuario_id=usuario.id_usuario
    ).first()

    correo = contacto.correo_electronico

    send_mail(
        subject="Recuperación de usuario",
        message=f"Su nombre de usuario es: {usuario.nombre_usuario}",
        from_email="ejemplo@gmail.com",
        recipient_list=[correo],
    )

    request.session.pop("correo_verificado", None)
    request.session.pop("CI_usuario", None)

    return render(request, 'recuperar_usuario.html', {
        "usuario_enviado": True
    })

# Esto son los modulos para registrar credenciales por parte del personal y
# pre-inscripción para los estudiantes

def panel_registro(request):
    return render(request, 'panel_registro.html')

def confirmar_registro_personal(request):
    return render(request, 'confirmar_registro_personal.html')

def pre_inscripción(request):
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
            cedula_identidad = nacionalidad + num_cedula
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
                clave=make_password(password)
            )

            Contacto.objects.create(
                telefono_personal=telefono,
                correo_electronico=correo_electronico,
                id_usuario=nuevo_usuario
            )

            return JsonResponse({
                "icon": "success",
                "descripcion": "Se registró correctamente"
            })

        return JsonResponse({
            "icon": "warning",
            "descripcion": "Complete todos los campos"
        })

    return render(request, "pre_inscripción.html")

# Esto son los modulos del panel de usuarios

def panel_usuario(request):
    return render(request, 'panel_usuario.html')

def datos_registro(request):
    nucleos = list(Nucleos.objects.values("id_nucleo", "municipio"))
    perfiles = list(Perfiles.objects.values("id_pefil", "perfil"))

    return JsonResponse({
                "nucleos": nucleos,
                "perfiles": perfiles
            })

def pnfs_nucleos(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            nucleo_id = data.get("id_nucleo")

            if not nucleo_id:
                return JsonResponse({"error": "Datos incompletos"}, status=400)

            pnfs = PNFNucleo.objects.filter(
                id_nucleo=nucleo_id
            ).select_related("id_pnf")

            resultado = [
                {
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

        perfil = request.POST.get("perfiles")
        nucleo = request.POST.get("nucleos")
        pnf = request.POST.get("pnf")

        if nombres and apellidos and nacionalidad and num_cedula and nombre_correo and dominio and prefijo and num_telefono:
            
            cedula_identidad = nacionalidad+"-"+num_cedula
            correo_principal = nombre_correo+dominio
            telefono_principal = prefijo+num_telefono
            
            if Usuario.objects.filter(cedula_identidad=cedula_identidad).exists():
                return JsonResponse({
                    "icon": "error",
                    "descripcion": "Ya existe un usuario con esta cédula"
                })

            usuario = Usuario.objects.create(nombres=nombres, apellidos=apellidos, cedula_identidad=cedula_identidad)
            Contacto.objects.create(correo_electronico=correo_principal, telefono_personal=telefono_principal, id_usuario=usuario)
            
            if gaceta_oficial and fecha_gaceta:
                GacetaOficial.objects.create(numero_gaceta=gaceta_oficial, fecha_gaceta=fecha_gaceta, id_usuario=usuario.id_usuario)
            
            UsuarioPerfil.objects.create(id_usuario=usuario, id_perfil=perfil)

            if nucleo:
                UsuarioNucleo.objects.create(id_usuario=usuario.id_usuario, id_nucleo=nucleo)
            if pnf:
                if pnf:
                    perfilpnf = UsuarioPerfil.objects.filter(id_usuario=usuario).first()

                    if perfilpnf is None:
                        return JsonResponse({
                            "icon": "error",
                            "descripcion": "Debe seleccionar un perfil antes de asignar un PNF"
                        })

                    PerfilesPnf.objects.create(
                        id_perfil_asignado=perfilpnf.id_perfil_asignado,
                        id_pnf_id=pnf
                    )

            return JsonResponse({
                    "icon": "success",
                    "descripcion": "Se registró correctamente"
                })
        else:
            return JsonResponse({
                    "icon": "warning",
                    "descripcion": "Se encuentra vacio los campos"
                })
        
    return render(request, 'pre_registro_personal.html')

def inscripcion_estudiante(request):
    return render(request, 'inscripcion_estudiante.html')

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