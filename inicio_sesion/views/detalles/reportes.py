# views.py
from django.shortcuts import render, get_object_or_404
from ...models import Cuenta, DirectorGeneral, Docente, Estudiante, CoordinadorPNF

def perfil_usuario_view(request):
    # Ejemplo: obteniendo la cuenta actual
    cuenta = Cuenta.objects.get(id_cuenta=request.session.get('id_cuenta'))
    usuario = cuenta.id_usuario

    # Option A: Obtener la cadena legible del rol
    rol_actual = cuenta.obtener_rol_principal()

    # Option B: Comprobar el rol mediante orm directo
    es_director = DirectorGeneral.objects.filter(usuario=usuario).exists()
    es_docente = Docente.objects.filter(usuario=usuario).exists()

    context = {
        'nombre_completo': f"{usuario.nombres} {usuario.apellidos}",
        'rol': rol_actual,
        'es_director': es_director
    }
    return render(request, 'perfil.html', context)

# views.py

def obtener_contexto_academico(cuenta_instancia):
    usuario = cuenta_instancia.id_usuario

    # Buscar si es Director General
    director = DirectorGeneral.objects.filter(usuario=usuario).first()
    if director:
        return {
            "rol": "DirectorGeneral",
            "objeto": director,
            "nucleo": director.nucleo
        }

    # Buscar si es Coordinador de PNF
    coordinador = CoordinadorPNF.objects.filter(usuario=usuario).first()
    if coordinador:
        return {
            "rol": "CoordinadorPNF",
            "objeto": coordinador,
            "nucleo": coordinador.nucleo,
            "pnf": coordinador.pnf
        }

    # Buscar si es Estudiante
    estudiante = Estudiante.objects.filter(usuario=usuario).first()
    if estudiante:
        return {
            "rol": "Estudiante",
            "objeto": estudiante,
            "nucleo": estudiante.nucleo,
            "pnf": estudiante.pnf
        }

    return None