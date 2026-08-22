# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.http import JsonResponse
# from django.contrib.auth.hashers import make_password
# from django.core.mail import send_mail
# from django.utils import timezone
# from datetime import timedelta
# from django.template.loader import render_to_string
# from django.contrib import messages

# from inicio_sesion.models import Usuario, Contacto, VerificacionCodigo, Cuenta

# import secrets, string, json, uuid
# from math import ceil

# # Verificado

# def bus_usr(request):
#     if request.method == "POST":
#         nacionalidad = request.POST.get("nacionalidad")
#         num_cedula = request.POST.get("cedula")

#         if not nacionalidad:
#             return JsonResponse({
#                 "estado": "fallo",
#                 "title": "Vacio",
#                 "icon": "warning",
#                 "descripcion": "Por favor, selecciona la nacionalidad."
#             })
        
#         if not num_cedula:
#             return JsonResponse({
#                 "estado": "fallo",
#                 "title": "Vacio",
#                 "icon": "warning",
#                 "descripcion": "Por favor, ingresa sus número para la cedula de identidad."
#             })

#         cedula_identidad = nacionalidad + "-" + num_cedula
        
#         try:
#             Usuario.objects.filter(cedula_identidad=cedula_identidad)
#         except Usuario.DoesNotExist:
#             return JsonResponse({
#                 "estado": "fallo",
#                 "title": "Error",
#                 "icon": "error",
#                 "descripcion": "El usuario no se encuentra registrado."
#             })
        
#         request.session['cedula_usuario'] = cedula_identidad

#         request.session['flujo_verificacion'] = True
        
#         request.session['token_recuperacion'] = str(uuid.uuid4())

#         return JsonResponse({"estado": "exito"})
        
#     return render(request, 'Sesion/buscar_usuario.html')

# def exist_cod(request):
#     usuario = Usuario.objects.get(cedula_identidad=request.session.get("cedula_usuario"))

#     token_sesion = request.session.get("token_recuperacion")

#     verificacion = VerificacionCodigo.objects.filter(
#         cedula_identidad=usuario.cedula_identidad,
#         token=token_sesion
#     ).first()

#     # No existe un código activo
#     if not verificacion:
#         return JsonResponse({
#             "estado": "no_exite",
#             "icon": "error",
#             "title": "Error",
#             "descripcion": "No existe un código de verificación vigente, selecciona uno de los correos registrados."
#         })

#     # El código expiró
#     if verificacion.fecha_expiracion <= timezone.now():
#         return JsonResponse({
#             "estado": "expirado",
#             "icon": "warning",
#             "title": "Expiro Código",
#             "descripcion": "El código ha expirado, debera presionar el botón reenviar código."
#         })

#     # El código sigue vigente
#     return JsonResponse({
#         "estado": "vigente",
#         "fecha_expiracion": int(verificacion.fecha_expiracion.timestamp())
#     })

# def corr_reg(request):
#     # Obtener el id del usuario
#     usuario = Usuario.objects.get(cedula_identidad=request.session.get("cedula_usuario"))

#     contacto = Contacto.objects.get(id_usuario=usuario)

#     correos = {}
#     if contacto.correo_electronico:
#         correos["correo_principal"] = contacto.correo_electronico

#     if contacto.correo_alternativo:
#         correos["correo_secundario"] = contacto.correo_alternativo

#     return JsonResponse({ "correos": correos })

# # Verificado
# def comp_usr(request):
#     return render(request, "Sesion/comprobar_usuario.html")

# def env_cod_usr(request):

#     if request.method != "POST":
#         return JsonResponse({
#             "estado": "fallo",
#             "title": "Error",
#             "icon": "error",
#             "descripcion": "Método no permitido"
#         }, status=405)


#     correo_seleccionado = request.POST.get("correo_verificacion")

#     if not correo_seleccionado:
#         return JsonResponse({
#             "estado": "fallo",
#             "title": "Error",
#             "icon": "error",
#             "descripcion": "Debe seleccionar un correo electrónico"
#         })


#     usuario = Usuario.objects.filter(
#         cedula_identidad=request.session.get("cedula_usuario")
#     ).first()


#     if not usuario:
#         return JsonResponse({
#             "estado": "fallo",
#             "title": "Error",
#             "icon": "error",
#             "descripcion": "Usuario no encontrado"
#         })


#     resultado = env_cod_ver(
#         usuario.nombres,
#         usuario.apellidos,
#         correo_seleccionado,
#         usuario.cedula_identidad,
#         request.session.get("token_recuperacion")
#     )

#     return resultado

# # Verificado
# def comp_cod_usr(request):
#     if request.method == "POST": # Se obtiene el código registrado por el usuario
#         codigo_ingresado = request.POST.get("codigo") # Verifica si no se encuentra vacio

#         if not codigo_ingresado:
#             return JsonResponse({
#                 "estado": "fallo",
#                 "title": "Error",
#                 "icon": "warning",
#                 "descripcion": "Debe ingresar el código de verificación",
#                 "accion": "vacio"
#             })

#         # Obtener el id del usuario
#         usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()

#         # Crear un token de seguridad
#         token_sesion = request.session.get("token_recuperacion")
        
#         verificacion = VerificacionCodigo.objects.filter(
#             cedula_identidad=usuario.cedula_identidad, 
#             token=token_sesion
#         ).first()

#         # Aquí se comprueba si el código perdio su vigencia
#         if verificacion and verificacion.fecha_expiracion < timezone.now():
#             return JsonResponse({
#                 "estado": "fallo",
#                 "title": "Error",
#                 "icon": "error",
#                 "descripcion": "El código ha expirado, debe solicitar el código a través del botón de reenviar código",
#                 "accion": "expirado"
#             })

#         # Se obtiene la respuesta del servidor si esta o no correcto el código
#         respuesta = val_cod(
#             codigo_ingresado,
#             usuario.cedula_identidad,
#             token_sesion
#         )

#         # Convierte la repuesta de un json HTTP a un objecto (Direccionario) que se pueda entender
#         datos = json.loads(respuesta.content)

#         # Si es exitosa se reinicia los campos para un futuro uso
#         if datos.get("estado") == "exito":    
#             # Se asigna el valor verdadero como bandera que se verifico el código
#             request.session["correo_verificado"] = True

#             if verificacion:
#                 verificacion.intentos = 0
#                 verificacion.bloqueado_hasta = None
#                 verificacion.activo = 0
#                 verificacion.save()

#         # Envia la respuesta a la vista
#         return respuesta

# # Verificado
# def val_cod(codigo, cedula_identidad, token):
#     # Se busca el código creado de acuerdo a los valores
#     verificacion = VerificacionCodigo.objects.filter(cedula_identidad=cedula_identidad, token=token, activo=1).first()
#     if not verificacion:
#         return JsonResponse({
#             "estado": "fallo",
#             "title": "Error",
#             "icon": "error",
#             "descripcion": "No existe un código de verificación"
#         })

#     # Aquí se elimina el bloqueo para el usuario
#     if (verificacion.bloqueado_hasta and timezone.now() >= verificacion.bloqueado_hasta):
#         verificacion.intentos = 0
#         verificacion.bloqueado_hasta = None
#         verificacion.save()

#     # Aquí se calcula el tiempo que le falta al usuario para desbloquearse
#     if (verificacion.bloqueado_hasta and timezone.now() < verificacion.bloqueado_hasta):
#         tiempo_restante = verificacion.bloqueado_hasta - timezone.now()
#         minutos_restantes = ceil(tiempo_restante.total_seconds() / 60)
#         return JsonResponse({
#             "estado": "bloqueado",
#             "title": "Bloqueado",
#             "icon": "error",
#             "descripcion": f"Demasiados intentos. Intente nuevamente en {minutos_restantes} minuto(s)"
#         })

#     # Se verifica que el código no se halla pasado del tiempo de vigencia
#     if timezone.now() > verificacion.fecha_expiracion:
#         return JsonResponse({
#             "estado": "expirado",
#             "title": "Expirado",
#             "icon": "warning",
#             "descripcion": "El código expiró. Solicite uno nuevamente con el botón de reenviar código."
#         })

#     # Si el código coincide con el ingresado por el usuario, se reinicie todos los campos
#     if verificacion.codigo == codigo:
#         verificacion.intentos = 0
#         verificacion.bloqueado_hasta = None
#         verificacion.activo = 0
#         verificacion.save()

#         return JsonResponse({
#             "estado": "exito",
#             "title": "Exito",
#             "icon": "success",
#             "descripcion": "Código corretamente."
#         })

#     # Aquí se suma un intento si ocurrio un error
#     verificacion.intentos += 1
#     # Se verifica si los intentos superan al limite establecido
#     if verificacion.intentos >= 3:
#         verificacion.bloqueado_hasta = timezone.now() + timedelta(minutes=5)
#         verificacion.save()
#         return JsonResponse({
#             "estado": "bloqueado",
#             "title": "Bloqueado",
#             "icon": "error",
#             "descripcion": "Ha superado el número máximo de intentos. Intente nuevamente en 5 minutos."
#         })

#     # Guarda los intentos fallidos
#     verificacion.save()

#     return JsonResponse({
#         "estado": "fallo",
#         "title": "Error",
#         "icon": "error",
#         "descripcion": f"Código incorrecto. Intentos: {verificacion.intentos}/3"
#     })

# # Verificado
# def reenv_cod_btn(request):
#     if request.method == "POST": # Se obtiene el código registrado por el usuario
#         codigo_seleccionado = request.POST.get("correo_verificacion") # Verifica si no se encuentra vacio

#         # Aquí se valida si realizaron las validaciones por la cedula y el correo electronico 
#         if not request.session.get("flujo_verificacion"):
#             return JsonResponse({
#                 "estado": "reenviar",
#                 "icon": "error",
#                 "title": "Error",
#                 "descripcion": "Debe de pasar en la validación para comprobar si esta registrado.",
#                 "url": reverse("bus_usr")
#             })

#         # Se buscan todos los datos necesarios
#         usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()

#         verificacion = VerificacionCodigo.objects.filter(cedula_identidad=usuario.cedula_identidad, token=request.session.get("token_recuperacion")).first()

#         # Aquí se calcula el tiempo que debe esperar el usuario
#         if (verificacion and verificacion.bloqueado_hasta and timezone.now() < verificacion.bloqueado_hasta):
#             tiempo_restante = (verificacion.bloqueado_hasta - timezone.now())
#             minutos_restantes = ceil(tiempo_restante.total_seconds() / 60)
#             return JsonResponse({
#                 "estado": "fallo",
#                 "icon": "error",
#                 "title": "Error",
#                 "descripcion": f"Demasiados intentos. Intente nuevamente en {minutos_restantes} minuto(s)"
#             })

#         # Se reenvia el código nuevamente
#         resultado = reenv_cod(
#             usuario.nombres,
#             usuario.apellidos,
#             codigo_seleccionado,
#             usuario.cedula_identidad,
#             request.session.get("token_recuperacion")
#         )

#         return resultado

# # Verificado
# def reenv_cod(nombres_usuario, apellidos_usuario, correo_electronico, cedula_identidad, token):
#     # Se obtiene los datos registrados
#     verificacion = VerificacionCodigo.objects.filter(cedula_identidad=cedula_identidad, token=token).first()

#     numero_intento = 0

#     # Se calcula el tiempo que debe esperar el usuario bloqueado
#     if verificacion and verificacion.bloqueado_hasta and timezone.now() < verificacion.bloqueado_hasta:
#         tiempo_restante = verificacion.bloqueado_hasta - timezone.now()
#         minutos_restantes = max(1, int(tiempo_restante.total_seconds() / 60))
#         return JsonResponse({
#             "estado": "fallo",
#             "title": "Bloqueado",
#             "icon": "error",
#             "descripcion": f"Demasiados intentos. Intente nuevamente en {minutos_restantes} minuto(s)"
#         })

#     # Se genera el código a enviar a correo electronico
#     codigo_generado = ''.join(
#         secrets.choice(string.ascii_uppercase + string.digits)
#         for _ in range(6)
#     )

#     # Se establece el tiempo vigencia
#     fecha_expiracion = timezone.now() + timedelta(minutes=5)

#     # Se actualiza si se encuentra registrado los datos a verificar
#     if verificacion:
#         verificacion.codigo = codigo_generado
#         verificacion.fecha_expiracion = fecha_expiracion
#         verificacion.activo = 1
#         verificacion.save()

#         numero_intento = verificacion.intentos
#     else:
#         verificacion = VerificacionCodigo.objects.create(
#             cedula_identidad=cedula_identidad,
#             token=token,
#             codigo=codigo_generado,
#             creado=timezone.now(),
#             intentos=0,
#             activo=1,
#             fecha_expiracion=fecha_expiracion,
#             bloqueado_hasta=None,
#             descripcion=f"Código de verificación para recuperación de credenciales al usuario {nombres_usuario} {apellidos_usuario}"
#         )

#     # Plantilla utilizado para el envío de código al correo electronico
#     html = render_to_string(
#         "Email/reenviar_codigo.html",
#         {
#             "nombres": nombres_usuario,
#             "apellidos": apellidos_usuario,
#             "codigo": codigo_generado,
#             "numero_intento": numero_intento,
#         }
#     )

#     # Envio al correo electronico
#     send_mail(
#         subject="Nuevo código de autenticación - UPT José Félix Ribas",
#         message=f"Su nuevo código de autenticación es: {codigo_generado}",
#         from_email="ejemplo@gmail.com",
#         recipient_list=[correo_electronico],
#         html_message=html,
#     )

#     # Notificación
#     return JsonResponse({
#         "estado": "exito",
#         "title": "Código",
#         "icon": "info",
#         "descripcion": "Se ha enviado un nuevo código de verificación",
#         "fecha_expiracion": fecha_expiracion.isoformat()
#     })

# # Verificado
# def env_cod_ver(nombres_usuario, apellidos_usuario, correo_electronico, cedula_identidad, token):
#     # Generar el código que se enviara al correo electronico
#     codigo_generado = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
#     fecha_expiracion = timezone.now() + timedelta(minutes=5)

#     # Se registran los datos 
#     VerificacionCodigo.objects.create(
#         cedula_identidad=cedula_identidad,
#         token=token,
#         codigo=codigo_generado,
#         creado=timezone.now(),
#         intentos=0,
#         activo=1,
#         fecha_expiracion=fecha_expiracion,
#         descripcion=f"Código de verificación para recuperación de credenciales al usuario {nombres_usuario} {apellidos_usuario}"
#     )
#     # Plantilla que se utilizara al correo electronica
#     html = render_to_string(
#         "Email/enviar_codigo.html",
#         {
#             "nombres": nombres_usuario,
#             "apellidos": apellidos_usuario,
#             "codigo": codigo_generado,
#         }
#     )
#     # Enviar correo
#     send_mail(
#         subject="Código de Autenticación - UPT José Félix Ribas",
#         message=f"Su código de autenticación es: {codigo_generado}",  # Texto plano de respaldo
#         from_email="ejemplo@gmail.com",
#         recipient_list=[correo_electronico],
#         html_message=html,
#     )

#     return JsonResponse({
#         "estado": "codigo_enviado",
#         "title": "Enviado",
#         "icon": "info",
#         "descripcion": "Se ha enviado un código de verificación a su correo electrónico",
#         "fecha_expiracion": fecha_expiracion.isoformat()
#     })

# # Verificado
# def panel_rec_cred(request):
#     # Se verififca si paso por las todas las validaciones
#     if not request.session.get("flujo_verificacion"):
#         return redirect("buscar_usuario")
    
#     if not request.session['correo_verificado']:
#         return redirect("buscar_usuario")

#     #Obtener el token creado
#     token = request.session.get("token_recuperacion")

#     # Comprobar si el codigo esta verificado o no
#     verificacion = VerificacionCodigo.objects.filter(token=token, activo=0).first()
#     if not verificacion:
#         return redirect("bus_usr")
    
#     return render(request, 'Sesion/panel_recuperar_credenciales.html')

# # Verificado
# def rec_cont(request):
#     if not request.session.get("flujo_verificacion"):
#         return redirect("bus_usr")
    
#     if not request.session.get("correo_verificado"):
#         return redirect("comp_usr")
    
#     token = request.session.get("token_recuperacion")

#     verificacion = VerificacionCodigo.objects.filter(token=token, activo=0).first()
#     if not verificacion:
#         return redirect("bus_usr")

#     if request.method == "POST":
#         password = request.POST.get("nueva_contrasenia")
#         confirmar_password = request.POST.get("confirmar_contrasenia")

#         # Se envia los mensajes de advertencia
#         if not password:
#             return JsonResponse({
#                 "estado": "fallo",
#                 "title": "Vacio",
#                 "icon": "warning",
#                 "descripcion": "Por favor, ingresa la nueva contraseña."
#             })
        
#         if not confirmar_password:
#             return JsonResponse({
#                 "estado": "fallo",
#                 "title": "Vacio",
#                 "icon": "warning",
#                 "descripcion": "Por favor, ingresa la confirmación de la nueva contraseña."
#             })

#         if password != confirmar_password:
#             return JsonResponse({
#                 "estado": "fallo",
#                 "title": "Error",
#                 "icon": "error",
#                 "descripcion": "No coincide las contraseñas."
#             })

#         usuario = Usuario.objects.filter(cedula_identidad=request.session.get("cedula_usuario")).first()
        
#         credenciales = Cuenta.objects.filter(id_usuario=usuario).first()
#         if not credenciales:
#             return JsonResponse({
#                 "estado": "fallo",
#                 "title": "Error",
#                 "icon": "error",
#                 "descripcion": "No existen credenciales registradas."
#             })

#         # Se guardaron la nuevas contraseña
#         credenciales.clave = make_password(password)
#         credenciales.save()

#         # Se reinicia los campos
#         verificacion = VerificacionCodigo.objects.filter(cedula_identidad=request.session["cedula_usuario"]).first()
#         if verificacion:
#             verificacion.token = ""
#             verificacion.save()

#         # Se elimina las variables de sesión
#         del request.session["correo_verificado"]
#         del request.session["cedula_usuario"]
#         del request.session["token_recuperacion"]

#         return JsonResponse({
#             "estado": "exito",
#             "title": "Exito",
#             "icon": "success",
#             "descripcion": "Contraseña actualizada correctamente."
#         })

#     return render(request, "Sesion/recuperar_contrasenia.html")

# # Verificado
# def rec_usr(request):
#     # Verificar que el flujo de recuperación sea válido
#     if not request.session.get("flujo_verificacion"):
#         return redirect("bus_usr")

#     if not request.session.get("correo_verificado"):
#         return redirect("comp_usr")

#     try:
#         usuario_reg = Usuario.objects.get(cedula_identidad=request.session.get("cedula_usuario"))
#     except Usuario.DoesNotExist:
#         messages.error(
#             request,
#             "Ocurrió un error al momento de buscar los datos del usuario."
#         )
#         return redirect("bus_usr")

#     contacto = Contacto.objects.filter(id_usuario=usuario_reg).first()
#     if not contacto or not contacto.correo_electronico:
#         messages.error(
#             request,
#             "Ocurrió un error al momento de obtener el correo electrónico registrado."
#         )
#         return redirect("bus_usr")

#     credenciales = Cuenta.objects.filter(id_usuario=usuario_reg).first()
#     if not credenciales:
#         messages.error(
#             request,
#             "Ocurrió un error al momento de obtener las credenciales del usuario."
#         )
#         return redirect("bus_usr")

#     # Generar plantilla del correo
#     html = render_to_string(
#         "Email/recuperar_usuario.html",
#         {
#             "nombres": usuario_reg.nombres,
#             "apellidos": usuario_reg.apellidos,
#             "nombre_usuario": credenciales.usuario,
#         },
#     )

#     try:
#         send_mail(
#             subject="Recuperación de usuario - UPT José Félix Ribas",
#             message=f"Su nombre de usuario es: {credenciales.usuario}",
#             from_email="ejemplo@gmail.com",
#             recipient_list=[contacto.correo_electronico],
#             html_message=html,
#             fail_silently=False,
#         )
#     except Exception:
#         messages.error(
#             request,
#             "Ocurrió un error al enviar el correo electrónico."
#         )
#         return redirect("buscar_usuario")

#     # Eliminar variables de sesión
#     request.session.pop("correo_verificado", None)
#     request.session.pop("cedula_usuario", None)
#     request.session.pop("token_recuperacion", None)
#     request.session.pop("flujo_verificacion", None)

#     return render(request, "Sesion/recuperar_usuario.html")



