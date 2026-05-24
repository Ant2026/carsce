from django.shortcuts import render, redirect
from .models import Usuario, UsuarioPerfil, Perfiles, Contacto
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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

                    return redirect("panel_usuario")
                else:
                    request.session['login_error'] = "Contraseña incorrecta"
                    return redirect("inicio_sesion")

            except Usuario.DoesNotExist:
                request.session['login_error'] = "Usuario no existe"
                return redirect("inicio_sesion")

        else:
            request.session['login_error'] = "Campos vacíos"
            return redirect("inicio_sesion")

    error = request.session.pop('login_error', None)
    return render(request, 'inicio_sesion.html', {'login_error': error})

def cerrar_sesion(request):
    request.session.flush() 
    return redirect("inicio_sesion")

def buscar_usuario(request):
    return render(request, 'buscar_usuario.html')

def panel_recuperar_credenciales(request):
    return render(request, 'panel_recuperar_credenciales.html')

def recuperar_contrasenia(request):
    return render(request, 'recuperar_contrasenia.html')

def recuperar_usuario(request):
    return render(request, 'recuperar_usuario.html')


def panel_registro(request):
    return render(request, 'panel_registro.html')

def confirmar_registro_personal(request):
    return render(request, 'confirmar_registro_personal.html')


def panel_usuario(request):
    return render(request, 'panel_usuario.html')

def inscripcion_estudiante(request):
    return render(request, 'inscripcion_estudiante.html')

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

            verificar_cedula = Usuario.objects.filter(
                cedula_identidad=cedula_identidad
            ).exists()

            verificar_usuario = Usuario.objects.filter(
                nombre_usuario=usuario
            ).first()

            verificar_correo = Contacto.objects.filter(
                correo_electronico=correo_electronico
            ).exists()

            if verificar_cedula:

                return JsonResponse({
                    "estado": "fallo",
                    "descripcion": "Ya existe una cédula registrada"
                })

            if verificar_correo:

                return JsonResponse({
                    "estado": "fallo",
                    "descripcion": "Ya existe un correo registrado"
                })

            if verificar_usuario:

                return JsonResponse({
                    "estado": "fallo",
                    "descripcion": "Ya existe el usuario registrado"
                })

            ultimo_usuario = Usuario.objects.order_by("-id_usuario").first()

            nuevo_id_usuario = ultimo_usuario.id_usuario + 1 if ultimo_usuario else 1 

            nuevo_usuario = Usuario.objects.create(
                id_usuario=nuevo_id_usuario,
                nombres=nombres,
                apellidos=apellidos,
                cedula_identidad=cedula_identidad,
                nombre_usuario=usuario,
                clave=make_password(password)
            )

            ultimo_contacto = Contacto.objects.order_by("-id_contacto").first()

            nuevo_id_contacto = ultimo_contacto.id_contacto + 1 if ultimo_contacto else 1 

            Contacto.objects.create(
                id_contacto=nuevo_id_contacto,
                telefono_personal=telefono,
                correo_electronico=correo_electronico,
                id_usuario=nuevo_usuario
            )

            return JsonResponse({
                "estado": "exito",
                "descripcion": "Se registró correctamente"
            })

        return JsonResponse({
            "estado": "fallo",
            "descripcion": "Complete todos los campos"
        })

    return render(request, "pre_inscripción.html")