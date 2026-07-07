from django.urls import path
from inicio_sesion import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.foro, name="foro"),
    path('inicio_sesion/', views.inicio_sesion, name="inicio_sesion"),
    
    path('buscar_usuario/', views.buscar_usuario, name="buscar_usuario"),
    path('comprobar_usuario/', views.comprobar_usuario, name="comprobar_usuario"),
    path('reenviar_codigo_btn/', views.reenviar_codigo_btn, name="reenviar_codigo_btn"),
    path('panel_recuperar_credenciales/', views.panel_recuperar_credenciales, name="panel_recuperar_credenciales"),
    path('recuperar_contrasenia/', views.recuperar_contrasenia, name="recuperar_contrasenia"),
    path('recuperar_usuario/', views.recuperar_usuario, name="recuperar_usuario"),

    path('panel_registro/', views.panel_registro, name="panel_registro"),
    path('panel_estudiantes/', views.panel_estudiantes, name="panel_estudiantes"),
    path('confirmar_registro_personal/', views.confirmar_registro_personal, name="confirmar_registro_personal"),
    path('guardar_credenciales_personal/', views.guardar_credenciales_personal, name="guardar_credenciales_personal"),
    path('buscar_personal_registrado/', views.buscar_personal_registrado, name="buscar_personal_registrado"),
    path('credenciales_estudiante/', views.credenciales_estudiante, name="credenciales_estudiante"),
    path('pre_inscripcion/', views.pre_inscripcion, name="pre_inscripcion"),

    path('pre_registro_personal/', views.pre_registro_personal, name="pre_registro_personal"),
    path('validar_nucleos/', views.validar_nucleos, name="validar_nucleos"),
    path('pnfs_nucleos/', views.pnfs_nucleos, name="pnfs_nucleos"),
    path('datos_registro/', views.datos_registro, name="datos_registro"),

    path('completar_registro_personal/', views.completar_registro_personal, name="completar_registro_personal"),
    path('completar_registro_estudiante/', views.completar_registro_estudiante, name="completar_registro_estudiante"),
    path('completar_registro_pe/', views.completar_registro_pe, name="completar_registro_pe"),
    path('datos_registrado/', views.datos_registrado, name="datos_registrado"),
    path('mostrar_pnfs_cursar/', views.mostrar_pnfs_cursar, name="mostrar_pnfs_cursar"),
    
    path('panel_usuario/', views.panel_usuario, name="panel_usuario"),
    path('cerrar_sesion/', views.cerrar_sesion, name="cerrar_sesion"),

    # 
    path('nucleos_coordinador_pnfs/', views.nucleos_coordinador_pnfs, name="nucleos_coordinador_pnfs"),
    path('pnfs_coordinador_pnfs/', views.pnfs_coordinador_pnfs, name="pnfs_coordinador_pnfs"),
    path('obtener_pre_inscrito/', views.obtener_pre_inscrito, name="obtener_pre_inscrito"),
    path('obtener_datos_pre_inscrito/', views.obtener_datos_pre_inscrito, name="obtener_datos_pre_inscrito"),
    path('inscripcion_estudiante/', views.inscripcion_estudiante, name="inscripcion_estudiante"),
    
    #
    path('pnfs_registrada/', views.pnfs_registrada, name="pnfs_registrada"),
    path('datos_pnf/', views.datos_pnf, name="datos_pnf"),
    path('guardar_actuailizacion_pnf/', views.guardar_actuailizacion_pnf, name="guardar_actuailizacion_pnf"),
    path('modulo_pnf/', views.modulo_pnf, name="modulo_pnf"),
    
    path('nucleos_registrados/', views.nucleos_registrados, name="nucleos_registrados"),
    path('datos_nucleo/', views.datos_nucleo, name="datos_nucleo"),
    path('guardar_actualizacion_nucleo/', views.guardar_actualizacion_nucleo, name="guardar_actualizacion_nucleo"),
    path('modulo_nucleo/', views.modulo_nucleo, name="modulo_nucleo"),
    
    path('secciones_registradas/', views.secciones_registradas, name="secciones_registradas"),
    path('datos_seccion/', views.datos_seccion, name="datos_seccion"),
    path('guardar_actualizacion_seccion/', views.guardar_actualizacion_seccion, name="guardar_actualizacion_seccion"),
    path('modulo_seccion/', views.modulo_seccion, name="modulo_seccion"),
    
    path('materias_registradas/', views.materias_registradas, name="materias_registradas"),
    path('datos_materia/', views.datos_materia, name="datos_materia"),
    path('guardar_actualizacion_materia/', views.guardar_actualizacion_materia, name="guardar_actualizacion_materia"),
    path('modulo_materia/', views.modulo_materia, name="modulo_materia"),

    path('periodos_academicos/', views.periodos_academicos, name="periodos_academicos"),
    path('calendarios_registrados/', views.calendarios_registrados, name="calendarios_registrados"),
    path('datos_calendario/', views.datos_calendario, name="datos_calendario"),
    path('guardar_actualizar_calendario/', views.guardar_actualizar_calendario, name="guardar_actualizar_calendario"),
    path('modelo_calendario_academico/', views.modelo_calendario_academico, name="modelo_calendario_academico"),

    path('datos_usuario/', views.datos_usuario, name="datos_usuario"),
    path('correos_usuario/', views.correos_usuario, name="correos_usuario"),
    path('enviar_codigo_actualizar_correo/', views.enviar_codigo_actualizar_correo, name="enviar_codigo_actualizar_correo"),
    path('autenticacion_actualizar_correo/', views.autenticacion_actualizar_correo, name="autenticacion_actualizar_correo"),
    path('actualizar_datosusuario/', views.actualizar_datosusuario, name="actualizar_datosusuario"),
    
    path('modulo_horario_academico/', views.modulo_horario_academico, name="modulo_horario_academico"),
    
    path('pnfs_pertenece_nucleo/', views.pnfs_pertenece_nucleo, name="pnfs_pertenece_nucleo"),
    path('docentes_registrados/', views.docentes_registrados, name="docentes_registrados"),
    path('materias_registradas/', views.materias_registradas, name="materias_registradas"),
    path('modulo_asignar_materia_docente/', views.modulo_asignar_materia_docente, name="modulo_asignar_materia_docente"),
    
    path('autoridades_registradas/', views.autoridades_registradas, name="autoridades_registradas"),
    path('datos_autoridad/', views.datos_autoridad, name="datos_autoridad"),
    path('actualizar_datos_autoridad/', views.actualizar_datos_autoridad, name="actualizar_datos_autoridad"),
    path('modulo_autoridades/', views.modulo_autoridades, name="modulo_autoridades"),
    
    path('buscar_datos_usuario/', views.buscar_datos_usuario, name="buscar_datos_usuario"),
    path('modulo_actualizar_usuarios/', views.modulo_actualizar_usuarios, name="modulo_actualizar_usuarios"),

    path('registro_estudiantil/', views.registro_estudiantil, name="registro_estudiantil"),

    #FORO
    path('Historia/', views.Historia, name="Historia"),
    path('mision_vision/', views.mision_vision, name="mision_vision"),
    path('pst/', views.pst, name="pst"),
    path('psc/', views.psc, name="psc"),
    path('trayectoria/', views.trayectoria, name="trayectoria"),
    path('carreras_impartidas/', views.carreras_impartidas, name="carreras_impartidas"),
    path('Planificacion_Docente/', views.Planificacion_Docente, name="Planificacion_Docente")
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )