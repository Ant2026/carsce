from django.shortcuts import render, redirect
from .models import Usuario, UsuarioPerfil, Perfiles, Contacto
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse

# Create your views here.

def foro(request):
    return render(request, 'foro.html')

def inicio_sesion(request):

    if request.method == "POST":
        nombre_usuario = request.POST.get("usuario")
        contrasenia = request.POST.get("contrasenia")

        if nombre_usuario and contrasenia:

            usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)

            if check_password(contrasenia, usuario.clave):
                nombre_completo = usuario.nombres + " " + usuario.apellidos

                perfiles = Perfiles.objects.filter(usuarioperfil__id_usuario=usuario)

                lista_perfiles = list(perfiles.values_list('perfil', flat=True))

                request.session['usuario_nombre'] = nombre_completo
                request.session['perfiles'] = lista_perfiles

                return redirect("panel_usuario")
            else:
                return JsonResponse({
                            "icon": "error",
                            "descripcion": "Ya existe un correo registrado"
                        }) 
        else:
            return JsonResponse({
                        "icon": "warning",
                        "descripcion": "Ya existe un correo registrado"
                    })

    error = request.session.pop('login_error', None)
    return render(request, 'inicio_sesion.html', {'login_error': error})

def cerrar_sesion(request):
    request.session.flush() 
    return redirect("inicio_sesion")

def buscar_usuario(request):

    if request.method == "POST":

        nacionalidad = request.POST.get("nacionalidad")
        num_cedula = request.POST.get("ci")

        if nacionalidad and num_cedula:

            cedula_identidad = nacionalidad + num_cedula

            existe = Usuario.objects.filter(
                cedula_identidad=cedula_identidad
            ).exists()

            if existe:

                request.session['usuario_existe'] = True

                return JsonResponse({
                    "estado": "exito",
                    "icon": "success",
                    "descripcion": "Usuario encontrado"
                })

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
                "icon": "success",
                "descripcion": "Se registró correctamente"
            })

        return JsonResponse({
            "icon": "warning",
            "descripcion": "Complete todos los campos"
        })

    return render(request, "pre_inscripción.html")