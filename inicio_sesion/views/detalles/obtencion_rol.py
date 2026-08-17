from django.conf import settings
from django.db.models import Count  # <-- Importamos Count
from inicio_sesion.models import (
    Cuenta, 
    DirectorGeneral, 
    ControlEstudio, 
    CoordinadorPNF, 
    Docente, 
    Estudiante,
    Nucleos  # <-- Importamos Nucleos
)

def datos_usuario_global(request):
    id_cuenta = request.session.get('id_cuenta')
    if not id_cuenta:
        return {}

    try:
        cuenta = Cuenta.objects.select_related('id_usuario').get(id_cuenta=id_cuenta)
        u = cuenta.id_usuario

        # 1. Búsqueda de Objetos (Agregamos .select_related('nucleo') a DirectorGeneral)
        estudiante_obj = Estudiante.objects.filter(usuario=u).select_related('nucleo').first()
        docente_obj = Docente.objects.filter(usuario=u).select_related('nucleo').first()
        coordinador_obj = CoordinadorPNF.objects.filter(usuario=u).select_related('nucleo').first()
        control_obj = ControlEstudio.objects.filter(usuario=u).select_related('nucleo').first()
        director_obj = DirectorGeneral.objects.filter(usuario=u).select_related('nucleo').first()

        # Determinar Rol Principal (en texto)
        rol_nombre = "Usuario"
        if director_obj:
            rol_nombre = "Director General"
        elif control_obj:
            rol_nombre = "Control de Estudio"
        elif coordinador_obj:
            rol_nombre = "Coordinador PNF"
        elif docente_obj:
            rol_nombre = "Docente"
        elif estudiante_obj:
            rol_nombre = "Estudiante"

        # Determinar el Núcleo del Usuario Conectado
        nucleo_usuario = None
        if director_obj and director_obj.nucleo:
            nucleo_usuario = director_obj.nucleo.municipio 
        elif estudiante_obj and estudiante_obj.nucleo:
            nucleo_usuario = estudiante_obj.nucleo.municipio
        elif docente_obj and docente_obj.nucleo:
            nucleo_usuario = docente_obj.nucleo.municipio
        elif coordinador_obj and coordinador_obj.nucleo:
            nucleo_usuario = coordinador_obj.nucleo.municipio
        elif control_obj and control_obj.nucleo:
            nucleo_usuario = control_obj.nucleo.municipio
        else:
            nucleo_usuario = "Sede Central / Sin Núcleo"

        # -------------------------------------------------------------
        # 2. Conteos y Estadísticas Globales
        # -------------------------------------------------------------
        total_estudiantes = Estudiante.objects.count()
        
        # Estudiantes que ya tienen completados sus registros de PNF y Núcleo
        total_inscritos = Estudiante.objects.filter(
            nucleo__isnull=False, 
            pnf__isnull=False
        ).count()

        # Conteo total del personal administrativo y docente
        conteo_docentes = Docente.objects.count()
        conteo_coordinadores = CoordinadorPNF.objects.count()
        conteo_control = ControlEstudio.objects.count()
        conteo_directores = DirectorGeneral.objects.count()

        total_personal = conteo_docentes + conteo_coordinadores + conteo_control + conteo_directores

        # NUEVO: Conteo de estudiantes agrupados por cada Núcleo
        estudiantes_por_nucleo = Nucleos.objects.annotate(
            total=Count(
                'estudiante__usuario',
                distinct=True
            )
        ).order_by('id_nucleo')

        # -------------------------------------------------------------
        # 3. Retorno de Variables Globales para las Plantillas
        # -------------------------------------------------------------
        return {
            'usuario_actual': u,
            'cuenta_actual': cuenta,
            'rol_principal': rol_nombre,
            'nucleo_usuario': nucleo_usuario,
            
            # Conteos
            'total_estudiantes': total_estudiantes,
            'total_inscritos': total_inscritos,
            'total_personal': total_personal,
            'estudiantes_por_nucleo': estudiantes_por_nucleo,  # <-- Agregado al contexto
            
            # Verificación de Roles en Booleanos
            'es_director': director_obj is not None,
            'es_control_estudio': control_obj is not None,
            'es_coordinador': coordinador_obj is not None,
            'es_docente': docente_obj is not None,
            'es_estudiante': estudiante_obj is not None,
        }

    except Cuenta.DoesNotExist:
        return {}