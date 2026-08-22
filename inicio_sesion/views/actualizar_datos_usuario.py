# from django.shortcuts import render
# from django.http import JsonResponse
# from django.db import transaction
# from django.utils import timezone
# from inicio_sesion.models import Usuario, Contacto, Residencia, Discapacidad, VerificacionCodigo
# import json, uuid

# from .recuperar_credenciales import *

# def dat_usr(request):
#     usuario = Usuario.objects.get(cedula_identidad=request.session.get("cedula_usuario"))

#     contacto = Contacto.objects.get(id_usuario=usuario)

#     residencia = Residencia.objects.get(id_usuario=usuario)

#     if request.session.get("rol") == "Estudiante":
#         discapacidad = Discapacidad.objects.get(id_usuario=usuario)

#     datos = {
#         "id_usuario": usuario.id_usuario,
#         "nombres": usuario.nombres,
#         "apellidos": usuario.apellidos,
#         "genero": usuario.genero,
#         "cedula_identidad": usuario.cedula_identidad,
#         "estado_civil": usuario.estado_civil,

#         "telefono_personal": contacto.telefono_personal,
#         "telefono_suplete": contacto.telefono_suplete,
#         "correo_electronico": contacto.correo_electronico,
#         "correo_alternativo": contacto.correo_alternativo,

#         "condicion_residencia": residencia.condicion_residencia,
#         "municipio": residencia.municipio,
#         "parroquia": residencia.parroquia,
#         "direccion_residencia": residencia.direccion_residencia,
#     }

#     if request.session.get("rol") == "Estudiante":
#         datos["discapacidad"] = (
#             {
#                 "carnet_discapacidad": discapacidad.codigo_carnet_discapacidad,
#                 "nro_registro_medico": discapacidad.nro_registro_medico,
#                 "tipo_discapacidad": discapacidad.tipo_discapacidad,
#                 "grado_discapacidad": discapacidad.grado_discapacidad,
#                 "causa_discapacidad": discapacidad.causa_discapacidad,
#             }
#             if discapacidad
#             else None
#         )

#     return JsonResponse(datos)

# def corr_usr(request):
#     token = str(uuid.uuid4())
#     request.session['token_recuperacion'] = token

#     usuario = Usuario.objects.get(cedula_identidad=request.session.get("cedula_usuario"))

#     contacto = Contacto.objects.get(id_usuario=usuario)

#     return JsonResponse({
#         "correo_principal": contacto.correo_electronico,
#         "correo_alternativo": contacto.correo_alternativo,
#     })
    
# def env_cod_act_corr(request):
#     if request.method == "POST":
#         cedula = request.session.get("cedula_usuario")
#         correo_seleccionado = request.POST.get("correo_verificacion")

#         usuario = Usuario.objects.get(cedula_identidad=cedula)

#         contacto = Contacto.objects.get(id_usuario=usuario)

#         if correo_seleccionado == "principal":
#             correo_electronico = contacto.correo_electronico
#         else:
#             correo_electronico = contacto.correo_alternativo

#         return env_cod_ver(
#             usuario.nombres,
#             usuario.apellidos,
#             correo_electronico,
#             usuario.cedula_identidad,
#             request.session["token_recuperacion"]
#         )

# def aut_act_corr(request):
#     if request.method == "POST":
#         codigo_ingresado = request.POST.get("codigocorreo")

#         usuario = Usuario.objects.get(cedula_identidad=request.session.get("cedula_usuario"))
        
#         verificacion = VerificacionCodigo.objects.filter(cedula_identidad=usuario.cedula_identidad,token=request.session.get("token_recuperacion")).first()

#         if not codigo_ingresado:
#             return JsonResponse({
#                 "estado": "fallo",
#                 "icon": "warning",
#                 "descripcion": "Debe ingresar el código de verificación",
#                 "accion": "input_vacio"
#             })

#         if verificacion and verificacion.fecha_expiracion < timezone.now():
#             return JsonResponse({
#                 "estado": "fallo",
#                 "icon": "error",
#                 "descripcion": "El código ha expirado, debe solicitar el código a través del botón de reenviar código",
#                 "accion": "expirado"
#             })

#         respuesta = val_cod(
#             codigo_ingresado,
#             usuario.cedula_identidad,
#             request.session["token_recuperacion"]
#         )

#         datos = json.loads(respuesta.content)
#         request.session["correo_verificado"] = True
        
#         if datos.get("estado") == "exito":    
#             verificacion.intentos = 0
#             verificacion.bloqueado_hasta = None
#             verificacion.activo = 0
#             verificacion.save()

#         return respuesta

# def act_dat_usr(request):
#     if request.method == "POST":
#         telefono_principal = request.POST.get("telefono_principal")
#         prefijo_principal = request.POST.get("prefijo_principal")

#         telefono_secundaria = request.POST.get("telefono_secundario")
#         prefijo_secundaria = request.POST.get("prefijo_secundario")

#         correo_principal = request.POST.get("correo_principal")
#         dominio_principal = request.POST.get("dominio_principal")

#         correo_secundaria = request.POST.get("correo_secundario")
#         dominio_secundaria = request.POST.get("dominio_secundario")

#         condicion_residencia = request.POST.get("condicionresidencia")
#         municipio_residencia = request.POST.get("municipioresidencia")
#         parroquia_residencia = request.POST.get("parroquiaresidencia")
#         direccion_domicilio = request.POST.get("direcciondomicilio")

#         if request.POST.get("carnet_dispacidad"):
#             carnet_discapacidad = request.POST.get("carnet_dispacidad")
#         else:
#             carnet_discapacidad = "N/A"

#         if request.POST.get("registro_medico"):
#             registro_medico = request.POST.get("registro_medico")
#         else:
#             registro_medico = "N/A"

#         if request.POST.get("tipos_discapacidad"):
#             tipos_discapacidad = request.POST.get("tipos_discapacidad")
#         else:
#             tipos_discapacidad = "N/A"

#         if request.POST.get("grado_discapacidad"):
#             grado_discapacidad = request.POST.get("grado_discapacidad")
#         else:
#             grado_discapacidad = "N/A"

#         if request.POST.get("causa_discapacidad"):
#             causa_discapacidad = request.POST.get("causa_discapacidad")
#         else:
#             causa_discapacidad = "N/A"

#         controles = [
#             (telefono_principal, "Número de Teléfono Principal", "Por favor, ingrese el número de teléfono principal."),
#             (prefijo_principal, "Prefijo del Teléfono Principal", "Por favor, seleccione el prefijo del teléfono principal."),
#             (correo_principal, "Correo Electrónico Principal", "Por favor, ingrese el correo principal."),
#             (dominio_principal, "Dominio del Correo Electrónico Principal", "Por favor, seleccione el dominio del correo electrónico principal."),
#             (correo_secundaria, "Correo Electrónico Secundario", "Por favor, ingrese el correo secundario."),
#             (dominio_secundaria, "Dominio del Correo Electrónico Secundario", "Por favor, seleccione el dominio del correo electrónico secundario."),
#             (condicion_residencia, "Condición de Residencia", "Por favor, seleccione la condición de residencia."),
#             (municipio_residencia, "Municipio de Residencia", "Por favor, seleccione el municipio donde reside."),
#             (parroquia_residencia, "Parroquia de Residencia", "Por favor, seleccione el parroquia donde reside."),
#             (direccion_domicilio, "Dirección de Domicilio", "Por favor, ingrese la dirección de domicilio."),
#         ]  

#         for valor, titulo, descripcion in controles:
#             if not valor:
#                 return JsonResponse({
#                     "estado": "fallo",
#                     "title": titulo,
#                     "icon": "warning",
#                     "descripcion": descripcion,
#                 })

#         if telefono_secundaria == "" and prefijo_secundaria == "":
#             telefono_num2 = "N/A"
#         else:
#             telefono_num2 = prefijo_secundaria + telefono_secundaria
        
#         telefono_num1 = prefijo_principal + telefono_principal

#         correo_num1 = correo_principal + dominio_principal

#         correo_num2 = correo_secundaria + dominio_secundaria

#         with transaction.atomic():
#             usuario = Usuario.objects.get(cedula_identidad=request.session.get("cedula_usuario"))

#             contacto = Contacto.objects.get(id_usuario=usuario)
#             contacto.telefono_personal = telefono_num1
#             contacto.telefono_suplete = telefono_num2
#             contacto.correo_electronico = correo_num1
#             contacto.correo_alternativo = correo_num2
#             contacto.save()

#             residencia = Residencia.objects.get(id_usuario=usuario)
#             residencia.condicion_residencia = condicion_residencia
#             residencia.municipio = municipio_residencia
#             residencia.parroquia = parroquia_residencia
#             residencia.direccion_residencia = direccion_domicilio
#             residencia.save()

#             if request.session.get("rol") == "Estudiante":
#                 discapacidad = Discapacidad.objects.get(id_usuario=usuario)
#                 discapacidad.codigo_carnet_discapacidad = carnet_discapacidad
#                 discapacidad.nro_registro_medico = registro_medico
#                 discapacidad.tipo_discapacidad = tipos_discapacidad
#                 discapacidad.grado_discapacidad = grado_discapacidad
#                 discapacidad.causa_discapacidad = causa_discapacidad
#                 discapacidad.save()

#             return JsonResponse({
#                 "estado": "exito",
#                 "icon": "success",
#                 "title": "Exito",
#                 "descripcion": "Los datos se actualizaron existosamente."
#             })
        
#         return JsonResponse({
#             "estado": "fallo",
#             "icon": "error",
#             "title": "Error",
#             "descripcion": "Ocurrio un error al momento de actualizar los datos."
#         })

#     return render(request, "Actualizaciones/actualizar_registro_usuario.html")


