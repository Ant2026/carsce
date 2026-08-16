from django.shortcuts import render
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse

from inicio_sesion.models import Usuario, Contacto, Cuenta, Estudiante

def panel_registro(request):
    return render(request, 'Sesion/panel_registro.html')

def val_usuario(request):
    if request.method == "POST":
        nombre_usuario = request.POST.get("nombre_usuario")

        existe = Cuenta.objects.filter(usuario=nombre_usuario).exists()
        if existe:
            return JsonResponse({ "existe": True })

        return JsonResponse({ "existe": False })

def val_password(request):
    if request.method == "POST":
        password = request.POST.get("password")

        existe = any(
            check_password(password, cuenta.clave)
            for cuenta in Cuenta.objects.only("clave")
        )

        return JsonResponse({ "existe": existe })

def registro_est(request):
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

        for valor, titulo, mensaje in campos:
            if not valor:
                return JsonResponse({
                    "estado": "fallo",
                    "title": titulo,
                    "descripcion": mensaje,
                    "icon": "warning"
                })

        correo_electronico = nombre_correo + dominio
        cedula_identidad = nacionalidad + "-" + num_cedula
        telefono = prefijo + num_telefono
        
        nuevo_usuario = Usuario.objects.create(nombres=nombres, apellidos=apellidos,cedula_identidad=cedula_identidad)

        Contacto.objects.create(telefono_personal=telefono, correo_electronico=correo_electronico, id_usuario=nuevo_usuario)

        Cuenta.objects.create(usuario=usuario, clave=make_password(password), tipo_cuenta='EST', id_usuario=nuevo_usuario)

        Estudiante.objects.create(usuario=nuevo_usuario)

        return JsonResponse({
            "estado": "exito",
            "title": "Exito",
            "icon": "success",
            "descripcion": "Los datos del estudiante se registraron exitosamente."
        })

    return render(request, "Sesion/registro_estudiantil.html")

def confirmar_reg(request):
    if request.method == "POST":
        nacionalidad = request.POST.get("nacionalidad")
        cedula = request.POST.get("usuario_ci")

        if not nacionalidad:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Campo Nacionalidad",
                "descripcion": "Por favor, seleccione la nacionalidad."
            })
        
        if not cedula:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Campo Cédula de Identidad",
                "descripcion": "Por favor, ingrese los número para la cedula de identidad."
            })

        cedula_identidad = f"{nacionalidad}-{cedula}"
        
        usuario = Usuario.objects.filter(cedula_identidad=cedula_identidad).first()
        if not usuario:
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Usuario no registrado",
                "descripcion": "El usuario no se encuentra registrado."
            })

        if Estudiante.objects.filter(usuario=usuario).exists():
            return JsonResponse({
                "estado": "fallo",
                "icon": "error",
                "title": "Usuario es Estudiante",
                "descripcion": "No puede registrar credenciales para un usuario que es estudiante."
            })

        if Cuenta.objects.filter(id_usuario=usuario, tipo_cuenta='ADMIN').exists():
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Cuenta con Credenciales",
                "descripcion": "El usuario ya posee credenciales registradas."
            })
        
        request.session["cedula_personal"] = cedula_identidad

        return JsonResponse({ "estado": "exito" })

    return render(request, "Sesion/confirmar_registro_personal.html")

def guardar_cred(request):
    if request.method == "POST":

        nombre_usuario = request.POST.get("nombre_usuario")
        contrasenia = request.POST.get("password_usuario")

        if not nombre_usuario:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Campo Nombre de Usuario",
                "descripcion": "Por favor, ingresa el nombre de usuario."
            })
        
        if not contrasenia:
            return JsonResponse({
                "estado": "fallo",
                "icon": "warning",
                "title": "Campo Contraseña",
                "descripcion": "Por favor, ingresa su contraseña."
            })

        usuario = Usuario.objects.get(cedula_identidad=request.session.get('cedula_personal'))

        Cuenta.objects.create(usuario=nombre_usuario, clave=make_password(contrasenia), tipo_cuenta='ADMIN', id_usuario=usuario)

        del request.session["cedula_personal"]

        return JsonResponse({
            "estado": "exito",
            "icon": "success",
            "title": "Registro Exitoso",
            "descripcion": "Se registraron exitosamente las credenciales."
        })

    return render(request, 'Sesion/confirmar_registro_personal.html')
