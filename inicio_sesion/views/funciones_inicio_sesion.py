from django.shortcuts import render
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.db.models import Q

from inicio_sesion.models import Usuario, Contacto, Cuenta

def panel_estudiantes(request):
    return render(request, 'Sesion/panel_estudiantes.html')

def panel_registro(request):
    return render(request, 'Sesion/panel_registro.html')

def verificar_cedula_identidad(request):
    if request.method == "POST":
        nacionalidad = request.POST.get("nacionalidad")
        cedula = request.POST.get("cedula")

        cedula_identidad = f"{nacionalidad}-{cedula}"

        existe = Usuario.objects.filter(cedula_identidad=cedula_identidad).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def verificar_correo_electronico(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        dominio = request.POST.get("dominio")

        correo_completo = f"{correo}{dominio}"

        existe = Contacto.objects.filter(Q(correo_electronico=correo_completo) | Q(correo_alternativo=correo_completo)).exists()

        return JsonResponse({
            "existe": existe
        })

def verificar_nombre_usuario(request):
    if request.method == "POST":
        nombre_usuario = request.POST.get("nombre_usuario")

        existe = Cuenta.objects.filter(usuario=nombre_usuario).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def verificar_password(request):
    if request.method == "POST":
        password = request.POST.get("password")

        existe = any(
            check_password(password, cuenta.clave)
            for cuenta in Cuenta.objects.only("clave")
        )

        return JsonResponse({
            "existe": existe
        })

# Verificar
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

        campos = [
            (nombres, "Nombres", "Por favor, ingrese sus nombres."),
            (apellidos, "Apellidos", "Por favor, ingrese sus apellidos."),
            (nacionalidad, "Nacionalidad", "Por favor, seleccione su nacionalidad."),
            (num_cedula, "Números de la Cedula de Identidad", "Por favor, ingrese sus números de la cedula de identidad."),
            (nombre_correo, "Nombre del Correo Electrónico", "Por favor, ingrese el nombre del correo electrónico."),
            (dominio, "Dominio del Correo", "Por favor, seleccione el dominio del correo electrónico."),
            (prefijo, "Prefijo Telefonico", "Por favor, seleccione el prefijo telefonico."),
            (num_telefono, "Números Telefonico", "Por favor, ingrese sus números de telefono."),
            (usuario, "Nombre de Usuario", "Por favor, ingrese su nombre de usuario."),
            (password, "Contraseña", "Por favor, ingrese su contraseña."),
        ]

        for valor, campo, mensaje in campos:
            if not valor:
                return JsonResponse({
                    "title": campo,
                    "descripcion": mensaje,
                    "icon": "warning"
                })

        correo_electronico = nombre_correo + dominio
        cedula_identidad = nacionalidad + "-" + num_cedula
        telefono = prefijo + num_telefono
        
        nuevo_usuario = Usuario.objects.create(nombres=nombres, apellidos=apellidos,cedula_identidad=cedula_identidad)

        Contacto.objects.create(telefono_personal=telefono, correo_electronico=correo_electronico, id_usuario=nuevo_usuario)

        # perfil = Perfiles.objects.get(perfil="Estudiante")
        # if perfil is None:
        #     return JsonResponse({
        #         "title": "Exito",
        #         "title": "Error",
        #         "icon": "error",
        #         "descripcion": "No existe el perfil Estudiante."
        #     })

        # CredencialesUsuario.objects.create(nombre_usuario=usuario, clave=make_password(password), id_asignacion=nuevo_asignacion)

        return JsonResponse({
            "title": "Exito",
            "icon": "success",
            "descripcion": "Se registró correctamente."
        })

    return render(request, "Sesion/registro_estudiantil.html")

# Verificado 
def confirmar_registro_personal(request):
    if request.method == "POST":
        nacionalidad = request.POST.get("nacionalidad")
        cedula = request.POST.get("usuario_ci")

        if not nacionalidad:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Por favor, seleccione la nacionalidad."
            })
        
        if not cedula:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Por favor, ingrese los número para la cedula de identidad."
            })

        cedula_identidad = f"{nacionalidad}-{cedula}"
        
        usuario = Usuario.objects.filter(cedula_identidad=cedula_identidad).first()
        if not usuario:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "El usuario no se encuentra registrado."
            })

        # perfil_estudiante = Perfiles.objects.get(perfil="Estudiante")



        # credenciales = CredencialesUsuario.objects.filter(id_asignacion=asignacion).first()
        # if credenciales:
        #     return JsonResponse({
        #         "estado": "fallo",
        #         "icon": "warning",
        #         "descripcion": "El usuario ya posee credenciales registradas."
        #     })
        
        request.session["cedula_personal"] = cedula_identidad

        return JsonResponse({
            "estado": "exito"
        })

    return render(request, "Sesion/confirmar_registro_personal.html")

# Verificado 
def guardar_credenciales_personal(request):
    if request.method == "POST":

        nombre_usuario = request.POST.get("nombre_usuario")
        password = request.POST.get("password_usuario")

        if not nombre_usuario:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Por favor, ingresa el nombre de usuario."
            })
        
        if not password:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Por favor, ingresa su contraseña."
            })

        # if CredencialesUsuario.objects.filter(nombre_usuario=nombre_usuario).exists():
        #     return JsonResponse({
        #         "estado": "fallo",
        #         "icon": "error",
        #         "descripcion": "Ya se encuentra un nombre de usuario similar."
        #     })

        # credenciales = CredencialesUsuario.objects.all()
        # for credencial in credenciales:
        #     if check_password(password, credencial.clave):
        #         return JsonResponse({
        #             "estado": "fallo",
        #             "icon": "error",
        #             "descripcion": "Ya existe una contraseña igual."
        #         })

        usuario = Usuario.objects.get(cedula_identidad=request.session.get('cedula_personal'))


        # CredencialesUsuario.objects.create(nombre_usuario=nombre_usuario, clave=make_password(password), id_asignacion=asignacion)

        del request.session["cedula_personal"]

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "descripcion": "Se registraron exitosamente las credenciales."
        })

    return render(request, 'Sesion/confirmar_registro_personal.html')

# Verificado
def buscar_personal_registrado(request):
    if request.method == "POST":
        nacionalidad = request.POST.get('nacionalidad')
        cedula = request.POST.get('cedula')

        if not nacionalidad:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Por favor, seleccionado la nacionalidad."
            })

        if not cedula:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Por favor, ingresa los números de la cedula de identidad."
            })

        cedula_identidad = f"{nacionalidad}-{cedula}"
                    
        if not Usuario.objects.filter(cedula_identidad=cedula_identidad).exists():
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "descripcion": "El usuario no se encuentra registrado."
            })
    
        usuario = Usuario.objects.filter(cedula_identidad=cedula_identidad).first()

        # perfil_estudiante = Perfiles.objects.get(pk=5)


        request.session['cedula_usuario'] = cedula_identidad

        return JsonResponse({
            "estado": "exito",
        })

# Verificado
def credenciales_estudiante(request):
    if request.method == "POST":
        nombre_usuario = request.POST.get('nombreusuario')
        password = request.POST.get('passwordusuario')

        if not nombre_usuario:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Por favor, ingresa su nombre de usuario."
            })
        
        if not password:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "descripcion": "Por favor, ingresa su contraseña."
            })

        # if CredencialesUsuario.objects.filter(nombre_usuario=nombre_usuario).exists():
        #     return JsonResponse({
        #         "estado": "fallo",
        #         "icon": "error",
        #         "descripcion": "Ya se encuentra un nombre de usuario similar."
        #     })
        
        # credenciales = CredencialesUsuario.objects.all()
        # for credencial in credenciales:
        #     if check_password(password, credencial.clave):
        #         return JsonResponse({
        #             "estado": "fallo",
        #             "icon": "error",
        #             "descripcion": "Ya existe una contraseña igual."
        #         })
            
        usuario = Usuario.objects.get(cedula_identidad=request.session.get("cedula_usuario")).first()

        # perfil_estudiante = Perfiles.objects.get(pk=5)
      
        # CredencialesUsuario.objects.create(nombre_usuario=nombre_usuario, clave=password, id_asignacion=asignacion)

        del request.session["cedula_personal"]

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "descripcion": "Se registraron las credenciales exitosamente."
        })

    return render(request, "Sesion/credenciales_estudiante.html")
