from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.forms.models import model_to_dict
from inicio_sesion.models import Usuario, Contacto, VerificacionCodigo
import json, uuid

from .recuperar_credenciales import *

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

def actualizar_datos_usuario(request):
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

                # if perfil == "Estudiante":
                #     discapacidad = Discapacidad.objects.get_or_create(id_usuario=usuario)

                #     discapacidad.codigo_carnet_discapacidad = carnet_discapacidad
                #     discapacidad.nro_registro_medico = registro_medico
                #     discapacidad.tipo_discapacidad = tipos_discapacidad
                #     discapacidad.grado_discapacidad = grado_discapacidad
                #     discapacidad.causa_discapacidad = causa_discapacidad
                #     discapacidad.save()

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
    
    return render(request, "Actualizaciones/actualizar_registro_usuario.html")
